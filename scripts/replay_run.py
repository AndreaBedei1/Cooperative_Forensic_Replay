#!/usr/bin/env python3
"""Interactive slow-motion replay of a recorded run in CARLA (visualization only).

    python scripts/replay_run.py traces/S01/run_0_crash [--speed 0.25]

Every rendered frame, the recorded ego.jsonl pose of each vehicle is
interpolated at the playback time and applied directly to a physics-less CARLA
actor.  No scenario controller runs and CARLA simulates no vehicle physics, so
every playback speed shows exactly the recorded trajectories.  Reconstructed
events (local graphs, global collisions, track associations) and each
recorder's perceived state (``local_trace.jsonl``: its tracks with CLOSING,
CRITICAL_TTC, CUT_IN, ..., lost tracks, known signs) are only read and
displayed, never derived here; nothing is written anywhere.

The viewer shows what the reconstruction knows, not the simulator's ground
truth: only the recorders (vehicles with their own ego.jsonl) are replayed as
vehicles, and the map is recognised from their recorded positions and the
public OpenDRIVE files (``--map`` overrides it).  The clock is the
reconstruction's global time; a recorder it could not align is not replayed.
Every anonymous road user of the fusion (U1, U2, ...: a road user that recorded
nothing) is drawn once, in grey: a wireframe box of its fitted footprint at the
fused position and heading with an arrow along its motion, solid while measured,
dashed while predicted, labelled only U1; scientific dimensions, uncertainty,
method and sources remain in the reconstruction files. Member tracks are radar dots. A
track associated with a recorder is a radar dot and a line from its observer (one line per
observer and recorder), never a second body and never a second label: the recorder's own badge
names it.  Each recorder's panel lists its recent semantic events first, then its confirmed
important states per global road user (never UNKNOWN states, never raw track lists), at most a
few lines (``... +N more``).  A track that is neither (none after
the fusion) is drawn as before: a ghost box of the nominal size in its
observer's colour.

Controls: SPACE play/pause, R restart, LEFT/RIGHT seek 0.5 s (with SHIFT
0.05 s), N/P next/previous reconstructed event, 1-4 speed 0.25/0.5/1/2x,
C camera: overview, then a follow camera on every recorder vehicle in turn, then free (TAB next
recorder), T tracks, G ghost boxes or dots, H help, ESC exit.  In the free camera: W/A/S/D/Q/E move (SHIFT faster); drag with the
mouse to look or orbit, wheel to zoom.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import queue
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from cdf.common.config import load_run_config  # noqa: E402
from cdf.reconstruction.pipeline import incident_map  # noqa: E402
from cdf.replay.model import (ASSOCIATED, BOX_EDGES, GLOBAL_CLOCK, HEADING_HELD, HEADING_UNKNOWN, MAP_MIN_FIT,  # noqa: E402
                              SPEEDS, EntityPath, EntityState, FreeCamera, PlaybackClock, Pose, ReplayRun, TrackPath,
                              TrackPoint, Vector, box_corners, choose_map, follow_camera, overview_camera, project,
                              project_segment, rotate)
from cdf.replay.topdown import export_keyframes, lanes_from_map  # noqa: E402
from cdf.replay.presentation import (ALERT, ANONYMOUS, EGO, EVENT, HELP_LINES, MAX_EVENT_LINES,  # noqa: E402
                                     MAX_STATE_LINES, MORE, ROAD_USER, event_line, event_window, next_camera,
                                     recorder_panel, subject_label, wrap_text)
from cdf.simulation.carla_client import (find_carla_root, import_carla, map_basename,  # noqa: E402
                                         session_from_config)

LOGGER = logging.getLogger("replay")
ROLE_PREFIX = "replay_"
PALETTE = [(230, 57, 70), (52, 120, 246), (46, 184, 92), (245, 158, 11), (168, 85, 247),
           (20, 184, 166), (236, 72, 153), (140, 140, 140)]
ROAD_USER_RGB = (225, 225, 225)  # an anonymous road user belongs to no observer
CAMERA_MODES = ("overview", "follow", "free")
SEEK_S, FINE_SEEK_S = 0.5, 0.05
EVENT_WINDOW_S = 1.0  # replay seconds an event stays next to its vehicle
COMPACT_STATE_LINES, COMPACT_EVENT_LINES = 3, 3  # the panels of the recorders not selected
ALL_EVENTS = 10 ** 6  # the selected recorder's panel: its whole history, scrolled
SECTION_RGB = (150, 200, 255)
COLLISION_RGB = (255, 95, 95)  # a recorder's COLLISION events in its panel
# A link line with the clearance: every track a recorder holds one of these about, plus its nearest IN_EGO_PATH
# track (the car it follows); farther cars in its path get no line.
INTERACTION_STATES = ("CRITICAL_TTC", "CUT_IN_FROM_LEFT", "CUT_IN_FROM_RIGHT")
COLLISION_WINDOW_S = 1.5
PANEL_MAX_WIDTH = 360  # pixels: the recorder panels stay a narrow column at the right edge
FOCUS_PANEL_WIDTH = 420  # pixels (at most a third of the window): the selected recorder's panel in focus mode
LABEL_CLEARANCE_M = 0.6  # label anchor above the roof
TRACK_DOT_HEIGHT_M = 0.8  # radar dots above the road (tracks are planar)
OPENDRIVE_DIR = Path("CarlaUE4") / "Content" / "Carla" / "Maps" / "OpenDrive"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay a recorded run in CARLA (visualization only)")
    parser.add_argument("run_dir", help="run directory, e.g. traces/S01/run_0_crash")
    parser.add_argument("--speed", type=float, default=0.5, help="playback speed (default 0.5x)")
    parser.add_argument("--start", type=float, default=0.0, help="start at this replay time [s]")
    parser.add_argument("--paused", action="store_true", help="start paused")
    parser.add_argument("--camera", choices=CAMERA_MODES, default="overview")
    parser.add_argument("--follow", default=None, help="recorder selected for the follow camera")
    parser.add_argument("--focus", action="store_true",
                        help="start with the selected recorder's panel focused (F toggles)")
    parser.add_argument("--hide-tracks", action="store_true",
                        help="start with the radar-track overlay hidden (toggle with T)")
    parser.add_argument("--show-tracks", action="store_true", help=argparse.SUPPRESS)  # markers are on by default
    parser.add_argument("--track-dots", action="store_true",
                        help="start with anonymous tracks as dots instead of ghost boxes (toggle with G)")
    parser.add_argument("--res", default="1280x720", help="window size WxH")
    parser.add_argument("--fov", type=float, default=90.0)
    parser.add_argument("--fps", type=float, default=30.0, help="render rate (CARLA ticks per wall second)")
    parser.add_argument("--map", default=None,
                        help="CARLA map; default: recognised from the recorders' recorded positions")
    parser.add_argument("--no-autostart", action="store_true", help="do not start a local CARLA process")
    parser.add_argument("--port", type=int, default=None,
                        help="CARLA RPC port (default: simulation.port of configs/default.yaml)")
    parser.add_argument("--keep-server", action="store_true", help="leave a CARLA server this viewer started running")
    parser.add_argument("--sync-lead", type=int, default=None, metavar="PORT",
                        help="send the instant shown, play state and speed to a viewer following on local UDP PORT")
    parser.add_argument("--sync-follow", type=int, default=None, metavar="PORT",
                        help="follow the instant, play state and speed of the viewer leading on local UDP PORT")
    parser.add_argument("--exit-after", type=float, default=None, help=argparse.SUPPRESS)  # smoke tests
    # Self-test of the real viewer: presses C six times through pygame's own event queue, saves the rendered
    # window after each press and the camera sequence and CARLA vehicle actors to DIR, then exits.
    parser.add_argument("--selftest", default=None, metavar="DIR", help=argparse.SUPPRESS)
    parser.add_argument("--export", default=None, metavar="DIR",
                        help="headless: draw top-down frames into DIR instead of opening the viewer (no CARLA "
                             "server; driving lanes from the public OpenDRIVE files when the carla module is there)")
    parser.add_argument("--at", action="append", type=float, default=[], metavar="T",
                        help="with --export: a displayed time to draw (t_global when aligned); repeatable; "
                             "default: the reconstruction's keyframes")
    parser.add_argument("--format", default="png", choices=("png", "svg", "pdf"), help="with --export: image format")
    args = parser.parse_args(argv)
    width, _, height = args.res.lower().partition("x")
    args.res = (int(width), int(height))
    if args.speed <= 0:
        parser.error("--speed must be positive")
    return args


def opendrive_sources(carla_root: Optional[Path]) -> Dict[str, str]:
    """Map name -> OpenDRIVE text of the maps shipped with a local CARLA installation (public files)."""
    if carla_root is None:
        return {}
    return {path.stem: path.read_text(encoding="utf-8", errors="replace")
            for path in sorted((Path(carla_root) / OPENDRIVE_DIR).glob("*.xodr"))}


_PARSED_MAPS: Dict[Tuple[int, str, str], Any] = {}


def parsed_map(carla: Any, name: str, text: str) -> Any:
    """A client-side carla.Map of an OpenDRIVE text, parsed once per process."""
    key = (id(carla), name, hashlib.sha1(text.encode("utf-8")).hexdigest())
    if key not in _PARSED_MAPS:
        _PARSED_MAPS[key] = carla.Map(name, text)
    return _PARSED_MAPS[key]


def lane_share(lane_map: Any, samples: Sequence[Vector]) -> float:
    """Share of the positions inside a driving lane of ``lane_map`` (a carla.Map)."""
    carla = import_carla()
    inside = sum(1 for x, y, z in samples
                 if lane_map.get_waypoint(carla.Location(x=x, y=y, z=z), project_to_road=False,
                                          lane_type=carla.LaneType.Driving) is not None)
    return inside / float(len(samples)) if samples else 0.0


def resolve_map(run: ReplayRun, carla_root: Optional[Path], current: Optional[str],
                current_map: Any = None) -> Optional[str]:
    """The map the recorders drove on, from their own recorded positions only.

    Every OpenDRIVE map of the local CARLA installation is parsed client-side
    and scored by the share of recorded ego positions inside its driving lanes
    (``choose_map``).  Without a local installation only the server's current
    map (``current_map``) can be checked.  No scenario configuration, run
    metadata or ground truth is read.
    """
    carla = import_carla()
    samples = run.map_samples()
    sources = opendrive_sources(carla_root)
    if not sources:
        if current_map is None:
            return None
        share = lane_share(current_map, samples)
        LOGGER.warning("no local OpenDRIVE files: only the server's map %s was checked (%.0f%% of the recorded "
                       "positions in its driving lanes)", current, 100.0 * share)
        return current if share >= MAP_MIN_FIT else None
    fits: Dict[str, float] = {}
    networks: Dict[str, str] = {}
    scored: Dict[str, float] = {}
    for name, text in sources.items():
        network = hashlib.sha1(text.encode("utf-8")).hexdigest()  # Town05 and Town05_Opt share one
        if network not in scored:
            scored[network] = lane_share(parsed_map(carla, name, text), samples)
        fits[name], networks[name] = scored[network], network
    ranked = sorted(fits.items(), key=lambda item: (-item[1], item[0]))
    LOGGER.info("recorded positions in the driving lanes of: %s",
                ", ".join("{0} {1:.0%}".format(name, fit) for name, fit in ranked[:4]))
    return choose_map(fits, networks, current)


class ReplayApp:
    """CARLA actors, a camera and the pygame window for one replay."""

    def __init__(self, run: ReplayRun, map_name: str, client: Any, world: Any, args: argparse.Namespace):
        self.carla = import_carla()
        self.run, self.map_name, self.client, self.world, self.args = run, map_name, client, world, args
        self.width, self.height = args.res
        self.ids = [p.participant_id for p in run.participants]  # the recorders: TAB cycles these only
        self.colors = {pid: PALETTE[i % len(PALETTE)] for i, pid in enumerate(self.ids)}
        self.clock = PlaybackClock(run.duration, speed=args.speed, start=args.start, playing=not args.paused)
        # Side by side (cdf.replay.sync): the instant, play state, speed, camera and quit cross between the two
        # viewers, whichever window the user acts in.
        from cdf.replay.sync import SyncPeer, follow_ports, lead_ports
        self.leading = bool(getattr(args, "sync_lead", None))
        ports = lead_ports(args.sync_lead) if self.leading else (
            follow_ports(args.sync_follow) if getattr(args, "sync_follow", None) else None)
        self.peer = SyncPeer(*ports) if ports else None
        self.commands = 0  # follower: its latest clock command; leader: the latest one it applied
        self.command_sent = 0.0  # follower: wall time of its latest clock command
        self.synced = False
        # The camera of two viewers side by side moves over the vehicles both replay: the recorders.
        recorders = getattr(run, "recorders", None) or self.ids
        self.view_ids = [pid for pid in self.ids if pid in recorders] if self.peer is not None else list(self.ids)
        self.events = run.display_events()
        self.selected = args.follow if args.follow in self.ids else self.ids[0]
        self.event_scroll = 0  # the selected recorder's events: index of the newest one shown
        self.focus = bool(getattr(args, "focus", False))  # F: the selected panel takes the column, others headers
        self.camera_mode = args.camera
        self.heading = run.participants[0].trajectory.pose_at(run.start).yaw
        self.elevation = 30.0
        self.zoom = 1.0
        self.follow_orbit, self.follow_distance = 0.0, 9.0
        self.free: Optional[FreeCamera] = None
        self.show_tracks = not args.hide_tracks
        self.show_ghosts = not args.track_dots
        self.show_help = True
        self.running = True
        self.dragging = False
        self.actors: Dict[str, Any] = {}
        self.indicator_bits: Dict[str, int] = {}  # the turn indicator bits last sent per replayed recorder
        self.roof: Dict[str, float] = {}
        self.camera: Any = None
        self.camera_pose: Optional[Pose] = None
        self.images: "queue.Queue[Any]" = queue.Queue()
        self.last_image: Any = None
        self.original_settings: Any = None
        self.map: Any = None
        self.screen: Any = None
        self.overlay: Any = None
        self.pygame: Any = None
        self.occupied: List[Any] = []  # per frame: screen rectangles a track label must not cover
        self.associated_lines: set = set()  # per frame: (observer, recorder) pairs already joined by a line

    # -- setup / teardown -------------------------------------------------------

    def setup(self) -> None:
        import pygame

        self.pygame = pygame
        self._destroy_leftovers()
        self.map = self.world.get_map()  # client-side; only for the height of drawn track markers
        self.original_settings = self.world.get_settings()
        settings = self.world.get_settings()
        settings.synchronous_mode = True  # every frame: place actors, then render exactly that state
        settings.fixed_delta_seconds = 1.0 / float(self.args.fps)
        settings.no_rendering_mode = False
        self.world.apply_settings(settings)
        self._spawn_vehicles()
        self._spawn_camera()
        pygame.init()
        pygame.display.set_caption(("GROUND TRUTH - " if self.run.clock == "t_contact" else "RECONSTRUCTION - ")
                                   + self.run.name)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # translucent ghost footprints
        pygame.key.set_repeat(300, 80)
        mono = "consolas,dejavusansmono,couriernew,monospace"
        self.font = pygame.font.SysFont(mono, 15)
        self.font_small = pygame.font.SysFont(mono, 13)
        self.font_bold = pygame.font.SysFont(mono, 15, bold=True)
        self.font_id = pygame.font.SysFont("arial,dejavusans", 26, bold=True)
        self.font_banner = pygame.font.SysFont("arial,dejavusans", 34, bold=True)

    def _destroy_leftovers(self) -> None:
        stale = [a for a in self.world.get_actors() if a.attributes.get("role_name", "").startswith(ROLE_PREFIX)]
        if stale:
            LOGGER.info("destroying %d replay actor(s) left by an earlier viewer", len(stale))
            self.client.apply_batch_sync([self.carla.command.DestroyActor(a.id) for a in stale], False)

    def _blueprint(self, name: str) -> Any:
        library = self.world.get_blueprint_library()
        try:
            return library.find(name)
        except (IndexError, RuntimeError):
            LOGGER.warning("blueprint %s not available; using vehicle.tesla.model3", name)
            return library.find("vehicle.tesla.model3")

    def _spawn_vehicles(self) -> None:
        carla = self.carla
        for index, participant in enumerate(self.run.participants):
            pid = participant.participant_id
            bp = self._blueprint(participant.blueprint)
            bp.set_attribute("role_name", ROLE_PREFIX + pid)
            if bp.has_attribute("color"):
                try:
                    bp.set_attribute("color", "{0},{1},{2}".format(*self.colors[pid]))
                except RuntimeError:
                    pass
            pose = participant.trajectory.pose_at(self.run.start)
            # Spawn well above the first pose (nothing to collide with), then
            # switch physics off and place it by transform only.
            spawn = carla.Transform(carla.Location(x=pose.x, y=pose.y, z=pose.z + 200.0 + 10.0 * index),
                                    carla.Rotation(yaw=pose.yaw))
            actor = self.world.try_spawn_actor(bp, spawn)
            if actor is None:
                raise RuntimeError("could not spawn a replay actor for " + pid)
            actor.set_simulate_physics(False)
            self.actors[pid] = actor
            box = actor.bounding_box
            self.roof[pid] = float(box.location.z + box.extent.z)
            LOGGER.info("%s: %s (%s blueprint)", pid, participant.blueprint, participant.blueprint_source)

    def _spawn_camera(self) -> None:
        bp = self.world.get_blueprint_library().find("sensor.camera.rgb")
        bp.set_attribute("image_size_x", str(self.width))
        bp.set_attribute("image_size_y", str(self.height))
        bp.set_attribute("fov", str(self.args.fov))
        bp.set_attribute("sensor_tick", "0.0")
        if bp.has_attribute("role_name"):
            bp.set_attribute("role_name", ROLE_PREFIX + "camera")
        pose = self._camera_pose(self._poses(self.clock.time))
        if self.camera_mode == "free":
            self.free = FreeCamera(pose)
        self.camera = self.world.spawn_actor(bp, self._transform(pose))
        self.camera.listen(self.images.put)

    def close(self) -> None:
        """Destroy every replay actor, restore the world settings, close pygame."""
        carla = self.carla
        if self.peer is not None:
            self.peer.close()
        if self.camera is not None:
            try:
                self.camera.stop()
            except RuntimeError as exc:
                LOGGER.warning("could not stop the replay camera: %s", exc)
        actors = list(self.actors.values()) + ([self.camera] if self.camera is not None else [])
        try:
            if actors:
                self.client.apply_batch_sync([carla.command.DestroyActor(a.id) for a in actors], False)
            if self.world.get_settings().synchronous_mode:
                self.world.tick()  # a destroy only takes effect on the next synchronous tick
        except RuntimeError as exc:
            LOGGER.warning("could not destroy the replay actors: %s", exc)
        if self.original_settings is not None:
            try:
                self.world.apply_settings(self.original_settings)
            except RuntimeError as exc:
                LOGGER.warning("could not restore the world settings: %s", exc)
        try:
            left = [a.id for a in self.world.get_actors() if a.attributes.get("role_name", "").startswith(ROLE_PREFIX)]
            if left:
                LOGGER.warning("replay actor(s) %s still in the world", left)
            else:
                LOGGER.info("replay actors destroyed")
        except RuntimeError:
            pass
        self.actors, self.camera = {}, None
        if self.pygame is not None:
            self.pygame.quit()

    # -- geometry -----------------------------------------------------------------

    def _transform(self, pose: Pose) -> Any:
        carla = self.carla
        return carla.Transform(carla.Location(x=pose.x, y=pose.y, z=pose.z),
                               carla.Rotation(pitch=pose.pitch, yaw=pose.yaw, roll=pose.roll))

    def _poses(self, t: float) -> Dict[str, Pose]:
        return {p.participant_id: p.trajectory.pose_at(self.run.start + t) for p in self.run.participants}

    def _camera_pose(self, poses: Dict[str, Pose]) -> Pose:
        if self.camera_mode == "follow":
            return follow_camera(poses[self.selected], orbit=self.follow_orbit, distance=self.follow_distance,
                                 height=0.4 * self.follow_distance)
        if self.camera_mode == "free" and self.free is not None:
            return self.free.pose
        points = [(p.x, p.y, p.z) for pid, p in poses.items() if pid in self.view_ids]
        return overview_camera(points, self.heading, zoom=self.zoom, elevation=self.elevation)

    def _project(self, point: Tuple[float, float, float]) -> Optional[Tuple[int, int]]:
        uv = project(point, self.camera_pose, self.args.fov, self.width, self.height)
        if uv is None or not (-200 < uv[0] < self.width + 200 and -200 < uv[1] < self.height + 200):
            return None
        return int(uv[0]), int(uv[1])

    # -- input ----------------------------------------------------------------------

    def handle(self, event: Any) -> None:
        pg = self.pygame
        if event.type == pg.QUIT:
            self._quit()
        elif event.type == pg.KEYDOWN:
            self._on_key(event.key, event.mod)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button in (1, 3):
            if event.button == 1 and self._timeline_hit(event.pos):
                self._seek_to_pixel(event.pos[0])
            else:
                self.dragging = True
        elif event.type == pg.MOUSEBUTTONUP and event.button in (1, 3):
            self.dragging = False
        elif event.type == pg.MOUSEMOTION and self.dragging:
            dx, dy = event.rel
            if self.camera_mode == "free" and self.free is not None:
                self.free.turn(0.2 * dx, -0.2 * dy)
            elif self.camera_mode == "follow":
                self.follow_orbit += 0.3 * dx
            else:
                self.heading += 0.3 * dx
                self.elevation = max(10.0, min(85.0, self.elevation + 0.2 * dy))
        elif event.type == pg.MOUSEWHEEL:
            if self.camera_mode == "free" and self.free is not None:
                self.free.move(2.0 * event.y, 0.0, 0.0)
            elif self.camera_mode == "follow":
                self.follow_distance = max(3.0, min(60.0, self.follow_distance * (0.9 ** event.y)))
            else:
                self.zoom = max(0.2, min(8.0, self.zoom * (0.9 ** event.y)))

    def _on_key(self, key: int, mod: int) -> None:
        pg = self.pygame
        speed_keys = {pg.K_1: 0, pg.K_2: 1, pg.K_3: 2, pg.K_4: 3, pg.K_KP1: 0, pg.K_KP2: 1, pg.K_KP3: 2, pg.K_KP4: 3}
        if key == pg.K_ESCAPE:
            self._quit()
        elif key == pg.K_SPACE:
            self.clock.toggle()
        elif key == pg.K_r:
            self.clock.restart()
        elif key in (pg.K_LEFT, pg.K_RIGHT):
            step = FINE_SEEK_S if mod & pg.KMOD_SHIFT else SEEK_S
            self.clock.seek(step if key == pg.K_RIGHT else -step)
        elif key in speed_keys:
            self.clock.set_speed(SPEEDS[speed_keys[key]])
        elif key == pg.K_c:
            # overview -> follow each recorder vehicle in turn -> free -> overview
            self.camera_mode, selected = next_camera(self.view_ids, self.camera_mode, self.selected)
            if selected is not None:
                self.selected = selected
            if self.camera_mode == "free" and self.camera_pose is not None:
                self.free = FreeCamera(self.camera_pose)
        elif key == pg.K_TAB:
            step = -1 if mod & pg.KMOD_SHIFT else 1
            # Side by side, the selection (and a follow camera) moves over the vehicles both viewers replay.
            cycle = self.view_ids if self.peer is not None else self.ids
            index = cycle.index(self.selected) if self.selected in cycle else -step
            self.selected = cycle[(index + step) % len(cycle)]
            self.event_scroll = 0  # the new recorder's newest events
        elif key in (pg.K_n, pg.K_p):
            target = (self.run.next_event_time if key == pg.K_n else self.run.previous_event_time)(self.clock.time)
            if target is not None:
                self.clock.seek_to(target)
                self.clock.pause()
        elif key in (pg.K_PAGEUP, pg.K_PAGEDOWN):
            self.event_scroll = max(0, self.event_scroll + (3 if key == pg.K_PAGEUP else -3))
        elif key == pg.K_t:
            self.show_tracks = not self.show_tracks
        elif key == pg.K_g:
            self.show_ghosts = not self.show_ghosts
        elif key == pg.K_h:
            self.show_help = not self.show_help
        elif key == pg.K_f:
            self.focus = not self.focus

    def _move_free_camera(self, wall_dt: float) -> None:
        if self.camera_mode != "free" or self.free is None:
            return
        pg = self.pygame
        keys = pg.key.get_pressed()
        rate = (30.0 if keys[pg.K_LSHIFT] or keys[pg.K_RSHIFT] else 10.0) * wall_dt
        forward = (keys[pg.K_w] - keys[pg.K_s]) * rate
        right = (keys[pg.K_d] - keys[pg.K_a]) * rate
        up = (keys[pg.K_e] - keys[pg.K_q]) * rate
        if forward or right or up:
            self.free.move(forward, right, up)

    # -- side by side ---------------------------------------------------------------

    def _quit(self) -> None:
        """ESC or the window closed: this viewer stops, and so does the other one side by side."""
        self.running = False
        if self.peer is not None:
            from cdf.replay.sync import encode_quit
            for _ in range(3):
                self.peer.send(encode_quit())

    def _clock_state(self) -> Tuple[float, bool, float]:
        return round(self.clock.time, 6), self.clock.playing, self.clock.speed

    def _view_state(self) -> Dict[str, Any]:
        free = None
        if self.camera_mode == "free" and self.free is not None:
            free = [round(value, 4) for value in (self.free.x, self.free.y, self.free.z, self.free.yaw, self.free.pitch)]
        return {"camera": self.camera_mode, "selected": self.selected if self.selected in self.view_ids else None,
                "heading": round(self.heading, 4), "elevation": round(self.elevation, 4), "zoom": round(self.zoom, 4),
                "orbit": round(self.follow_orbit, 4), "distance": round(self.follow_distance, 4), "free": free}

    def _apply_view(self, view: Dict[str, Any]) -> None:
        """The camera the user set in the other window."""
        before = (self.camera_mode, self.selected)
        if view.get("selected") in self.view_ids:
            self.selected = view["selected"]
        if view.get("camera") in ("overview", "follow", "free"):
            self.camera_mode = view["camera"]
        for key, attribute in (("heading", "heading"), ("elevation", "elevation"), ("zoom", "zoom"),
                               ("orbit", "follow_orbit"), ("distance", "follow_distance")):
            if view.get(key) is not None:
                setattr(self, attribute, float(view[key]))
        if self.camera_mode == "free":
            if view.get("free"):
                x, y, z, yaw, pitch = (float(value) for value in view["free"])
                self.free = FreeCamera(Pose(x, y, z, yaw, pitch, 0.0))
            elif self.free is None and self.camera_pose is not None:
                self.free = FreeCamera(self.camera_pose)
        if (self.camera_mode, self.selected) != before:
            LOGGER.info("camera set in the other window: %s", self.camera_mode
                        + (" " + self.selected if self.camera_mode == "follow" else ""))

    def _exchange(self, before: Tuple[Any, Any], now: float) -> bool:
        """Side by side: send what this window's user changed, take what the other window sent.  True when this
        frame's instant is the leader's (the follower then does not advance its own clock)."""
        from cdf.replay.sync import CLOCK, QUIT, VIEW, apply_sync, encode, encode_view
        clock_before, view_before = before
        view = self._view_state()
        if view != view_before:
            self.peer.send(encode_view(view))
        if not self.leading and self._clock_state() != clock_before:
            # Play, pause, seek or speed in the follower's window: a command for the leader.
            self.commands += 1
            self.command_sent = now
            self.peer.send(encode(self.run.recording_time(self.clock.time), self.clock.playing, self.clock.speed,
                                  self.commands))
        followed = False
        for message in self.peer.received():
            if message["type"] == QUIT:
                if self.running:  # the quit is sent three times
                    LOGGER.info("the other viewer was closed: closing this one too")
                self.running = False
            elif message["type"] == VIEW:
                self._apply_view(message)
            elif message["type"] == CLOCK and self.leading:
                apply_sync(self.clock, self.run, message)  # the follower's user acted
                self.commands = message["n"]
            elif message["type"] == CLOCK and (message["n"] >= self.commands or now - self.command_sent > 1.0):
                apply_sync(self.clock, self.run, message)
                followed = True
                if not self.synced:
                    self.synced = True
                    LOGGER.info("side by side with the leading viewer: recording clock %.3f s = %s %+.2f s",
                                message["t_recording"], "t_global" if self.run.clock == GLOBAL_CLOCK else "t",
                                self.run.display_time(self.clock.time))
        return followed

    # -- frame --------------------------------------------------------------------

    def run_loop(self) -> None:
        ticker = self.pygame.time.Clock()
        last = started = time.perf_counter()
        selftest = SelfTest(self, Path(self.args.selftest), started) if getattr(self.args, "selftest", None) else None
        while self.running:
            now = time.perf_counter()
            wall_dt, last = min(now - last, 0.25), now
            before = (self._clock_state(), self._view_state())  # what this window's user changes this frame
            for event in self.pygame.event.get():
                self.handle(event)
            self._move_free_camera(wall_dt)
            if not (self.peer is not None and self._exchange(before, now)):
                self.clock.advance(wall_dt)
            if self.peer is not None and self.leading:
                from cdf.replay.sync import encode
                self.peer.send(encode(self.run.recording_time(self.clock.time), self.clock.playing, self.clock.speed,
                                      self.commands))
            if not self.running:
                break
            self.render_frame()
            ticker.tick(self.args.fps)
            if selftest is not None:
                selftest.step(now)
            if self.args.exit_after is not None and now - started >= self.args.exit_after:
                self.running = False

    def render_frame(self) -> None:
        """Place every actor at the recorded pose for the current time, render, draw overlays."""
        carla = self.carla
        t = self.clock.time
        poses = self._poses(t)
        self.camera_pose = self._camera_pose(poses)
        commands = [carla.command.ApplyTransform(self.actors[pid].id, self._transform(pose)) for pid, pose in poses.items()]
        commands += self._indicator_commands(t)
        commands.append(carla.command.ApplyTransform(self.camera.id, self._transform(self.camera_pose)))
        self.client.apply_batch_sync(commands, False)
        self.world.get_spectator().set_transform(self._transform(self.camera_pose))
        frame = self.world.tick()
        image = self._image_for(frame)
        self._draw(image, poses, t)

    def _indicator_commands(self, t: float) -> List[Any]:
        """The recorders' turn indicators as their own light log recorded them (perceived INDICATOR_LEFT /
        INDICATOR_RIGHT): CARLA blinks the lights of a replayed vehicle whose blinker bit is set.  Unknown (a
        recording without the log) or off: no blinker.  Sent only when it changes."""
        carla = self.carla
        out = []
        for pid, actor in self.actors.items():
            perceived = (getattr(self.run, "perceived", None) or {}).get(pid)
            ego = ((perceived.state_at(t) if perceived is not None else None) or {}).get("ego") or {}
            bits = (int(carla.VehicleLightState.LeftBlinker) if ego.get("INDICATOR_LEFT") is True else 0) | (
                int(carla.VehicleLightState.RightBlinker) if ego.get("INDICATOR_RIGHT") is True else 0)
            if self.indicator_bits.get(pid) != bits:
                self.indicator_bits[pid] = bits
                out.append(carla.command.SetVehicleLightState(actor.id, carla.VehicleLightState(bits)))
        return out

    def _image_for(self, frame: int) -> Any:
        deadline = time.time() + 2.0
        while time.time() < deadline:
            try:
                image = self.images.get(timeout=max(0.0, deadline - time.time()))
            except queue.Empty:
                break
            if image.frame >= frame:
                self.last_image = image
                return image
        return self.last_image

    # -- drawing ------------------------------------------------------------------

    def _draw(self, image: Any, poses: Dict[str, Pose], t: float) -> None:
        pg, screen = self.pygame, self.screen
        if image is not None:
            import numpy as np

            array = np.frombuffer(image.raw_data, dtype=np.uint8).reshape((image.height, image.width, 4))
            screen.blit(pg.surfarray.make_surface(array[:, :, 2::-1].swapaxes(0, 1)), (0, 0))
        else:
            screen.fill((20, 20, 20))
        self.occupied = []  # screen rectangles a track label must not cover
        self.associated_lines = set()  # (observer, recorder) pairs already joined by a line this frame
        labels = self._draw_tracks(poses, t) if self.show_tracks else []
        badges = {pid: self._draw_badge(pid, pose) for pid, pose in poses.items()}
        # The recorder panels on a layer of their own: laid out now (their rectangles keep the labels off them),
        # put on top after the labels, so no label's leader line crosses a panel's text.
        layer = pg.Surface((self.width, self.height), pg.SRCALPHA)
        screen, self.screen = self.screen, layer
        try:
            self._draw_side_panels(t, badges)
        finally:
            self.screen = screen
        self._draw_hud(t)
        self._draw_collision_banner(t)  # in the free span between the HUD and the panel column
        self._draw_timeline(t)
        for label in labels:  # each in free space: off the panels, the badges and each other
            label()
        screen.blit(layer, (0, 0))
        pg.display.flip()

    def _panel(self, rect: Tuple[int, int, int, int], alpha: int = 170) -> None:
        panel = self.pygame.Surface((rect[2], rect[3]), self.pygame.SRCALPHA)
        panel.fill((0, 0, 0, alpha))
        self.screen.blit(panel, (rect[0], rect[1]))
        self.occupied.append(self.pygame.Rect(rect))

    def _draw_badge(self, pid: str, pose: Pose) -> Any:
        """The vehicle's letter just above its roof; returns the badge rectangle (None if not visible)."""
        pg = self.pygame
        anchor = self._project((pose.x, pose.y, pose.z + self.roof.get(pid, 1.5) + LABEL_CLEARANCE_M))
        if anchor is None:
            return None
        u, v = anchor
        color = self.colors[pid]
        text = self.font_id.render(pid, True, (255, 255, 255))
        box = pg.Rect(0, 0, text.get_width() + 16, text.get_height() + 4)
        box.midbottom = (u, v - 8)
        pg.draw.polygon(self.screen, color, [(u - 7, v - 9), (u + 7, v - 9), (u, v)])
        pg.draw.rect(self.screen, color, box, border_radius=6)
        pg.draw.rect(self.screen, (255, 255, 255), box, width=2, border_radius=6)
        self.screen.blit(text, (box.x + 8, box.y + 2))
        self.occupied.append(box.inflate(4, 14))
        return box

    def _vehicle_lines(self, pid: str, t: float, full: bool = True) -> List[Tuple[str, Tuple[int, int, int], Any]]:
        """The recorder's panel (``presentation.recorder_panel``): its CURRENT state (own states, active track
        states, anonymous tracks, road users) and, in a separate section, its most recent semantic events newest
        first, each with its age.  ``full`` (the selected recorder): up to MAX_STATE_LINES states and every
        event (the panel shows MAX_EVENT_LINES at a time, PgUp/PgDn scroll); else compact: COMPACT_STATE_LINES states (own state and alerts first) and the
        COMPACT_EVENT_LINES latest events.  No UNKNOWN or PREDICTED text."""
        style = {ALERT: ((255, 150, 90), self.font_small), ANONYMOUS: ((200, 200, 255), self.font_small),
                 ROAD_USER: ((220, 220, 220), self.font_small), EVENT: ((255, 214, 10), self.font_small),
                 EGO: ((255, 255, 255), self.font_small), MORE: ((170, 170, 170), self.font_small)}
        panel = recorder_panel(self.run, pid, t, ALL_EVENTS if full else COMPACT_EVENT_LINES,
                               MAX_STATE_LINES if full else COMPACT_STATE_LINES)
        lines = []
        for text, kind in panel.states:
            rgb, font = style.get(kind, ((255, 255, 255), self.font_small))
            lines.append((text, rgb, font))
        collisions = sum(1 for e in self.run.display_events()
                         if e.actor == pid and e.event_type == "COLLISION" and e.time <= t + 1e-6)
        lines.append(("recent events ({0} so far{1})".format(
            panel.events_total, ", {0} collision{1}".format(collisions, "s" if collisions > 1 else "") if collisions
            else ""), SECTION_RGB, self.font_bold))
        for text, kind in panel.events:
            rgb, font = style.get(kind, ((255, 255, 255), self.font_small))
            if kind == EVENT and text.split("  ", 1)[-1].startswith(("COLLISION", "RECONTACT")):
                rgb, font = COLLISION_RGB, self.font_bold  # the recorder's own collisions (and recontacts) stand out
            lines.append((text, rgb, font))
        return lines

    def _draw_side_panels(self, t: float, badges: Dict[str, Any]) -> None:
        """One details panel per vehicle in a right-hand column, linked to its badge.  Normal layout: the
        selected recorder's panel full, the others compact.  Focus (F): the others reduced to their headers and
        the selected one given the rest of the column down to the help lines and the timeline.  The selected
        panel keeps its states at the top and shows at most MAX_EVENT_LINES events newest first; when they do not
        fit PgUp/PgDn scroll through all of them (``presentation.event_window``: none lost, none cut).  Long
        lines wrap at the panel width."""
        pg = self.pygame
        focus = self.focus
        width_limit = min(FOCUS_PANEL_WIDTH, max(PANEL_MAX_WIDTH, self.width // 3)) if focus else PANEL_MAX_WIDTH
        text_width = width_limit - 18

        def rows(text: str, rgb: Tuple[int, int, int], font: Any) -> List[Any]:
            return [font.render(piece, True, rgb) for piece in wrap_text(text, lambda x: font.size(x)[0], text_width)]

        panels = []
        for pid in self.ids:
            speed = self.run.participant(pid).trajectory.speed_at(self.run.start + t)
            header = self.font_bold.render("{0}   {1:5.1f} m/s  {2:3.0f} km/h".format(pid, speed, speed * 3.6),
                                           True, (255, 255, 255))
            full = pid == self.selected
            fixed, events = [], []  # fixed: rows of the states and the section line; events: the rows of each event
            if full or not focus:
                in_events = False
                for text, rgb, font in self._vehicle_lines(pid, t, full):
                    if in_events:
                        events.append(rows(text, rgb, font))
                    else:
                        fixed.extend(rows(text, rgb, font))
                        in_events = font is self.font_bold and rgb == SECTION_RGB
            panels.append((pid, header, fixed, events, full))
        if focus:
            width = width_limit
        else:
            widest = max(max([h.get_width()] + [r.get_width() for r in fixed] + [r.get_width() for e in ev for r in e])
                         for _, h, fixed, ev, _ in panels)
            width = min(PANEL_MAX_WIDTH, max(240, widest + 18))
        x, y = self.width - width - 8, 8
        self.panel_left = x  # the collision banner stays left of the column
        bottom = self._bottom_bar_top() - 4  # keep clear of the help lines and the timeline

        def height_of(header: Any, body: Sequence[Any]) -> int:
            return header.get_height() + 6 + sum(b.get_height() for b in body) + (4 if body else 0)

        # The other panels first: the selected one gets the room they leave.
        reserved = sum(height_of(h, fixed + [r for e in ev for r in e]) + 6
                       for _, h, fixed, ev, full in panels if not full)
        line = max(1, self.font_small.get_linesize())
        for pid, header, fixed, events, full in panels:
            body = fixed + [r for e in events for r in e]
            if full:
                room = max(0, (bottom - y - reserved - header.get_height() - 12) // line)
                first, last, self.event_scroll = event_window([len(e) for e in events], room - len(fixed),
                                                              self.event_scroll, MAX_EVENT_LINES)
                body = fixed + [r for e in events[first:last] for r in e]
                if (first, last) != (0, len(events)):
                    body.append(self.font_small.render("PgUp older / PgDn newer: events {0}-{1} of {2}".format(
                        first + 1, last, len(events)), True, (170, 170, 170)))
            else:
                reserved -= height_of(header, body) + 6
            height = height_of(header, body)
            if y + height > bottom and body:  # too tall for what is left: clip the body, never the header
                keep = max(0, (bottom - y - header.get_height() - 10) // line - 1)
                body = body[:keep] + [self.font_small.render("...", True, (200, 200, 200))]
                height = height_of(header, body)
            if y + height > bottom:
                break
            color = self.colors[pid]
            self._panel((x, y, width, height), 185 if focus and full else 165)
            pg.draw.rect(self.screen, color, (x, y, width, header.get_height() + 6))
            self.screen.blit(header, (x + 8, y + 3))
            line_y = y + header.get_height() + 8
            for surface in body:
                self.screen.blit(surface, (x + 8, line_y))
                line_y += surface.get_height()
            badge = badges.get(pid)
            if badge is not None:
                anchor = (x, y + (header.get_height() + 6) // 2)
                pg.draw.line(self.screen, color, anchor, badge.midright, 2)
                pg.draw.circle(self.screen, color, anchor, 4)
            y += height + 6

    def _ground_z(self, x: float, y: float, near_z: float) -> float:
        """Road height under a 2-D track position, for drawing only (the tracks are planar)."""
        try:
            waypoint = self.map.get_waypoint(self.carla.Location(x=x, y=y, z=near_z), project_to_road=True)
            if waypoint is not None:
                return float(waypoint.transform.location.z)
        except RuntimeError:
            pass
        return near_z

    def _draw_tracks(self, poses: Dict[str, Pose], t: float) -> List[Any]:
        """What each recorder's radar knows at ``t``, in the recorder's colour, as the reconstruction wrote it.

        Each track is drawn from its own samples through its own observer's
        frame; tracks of different recorders are never merged, even when they
        overlap.  A track is shown only between its first and last sample (it
        disappears at its TRACK_LOST).  Returns the deferred label drawings.
        """
        ghosts, dots = [], []
        for index, recorder in enumerate(self.ids):
            observer = poses.get(recorder)
            if observer is None:
                continue
            for track in self.run.tracks.get(recorder, []):
                state = track.state_at(t)
                if state is None:
                    continue
                (ghosts if track.ghost and self.show_ghosts else dots).append((track, state, observer, index))
        size = self.run.geometry
        boxes, users = [], []
        entities = self.run.entities_at(t) if self.show_ghosts else []
        if ghosts or entities:
            self.overlay.fill((0, 0, 0, 0))
            for track, state, observer, index in ghosts:
                z = self._ground_z(state.centre[0], state.centre[1], observer.z)
                corners = box_corners(state.centre, state.yaw, size.length, size.width, z, size.height)
                footprint = [self._project(corner) for corner in corners[:4]]
                if all(point is not None for point in footprint):  # translucent, under every line
                    alpha = 70 if state.measured else 35
                    self.pygame.draw.polygon(self.overlay, self.colors[track.recorder] + (alpha,), footprint)
                boxes.append((track, state, corners, index))
            for entity, state in entities:
                near = next((poses[o] for o in state.observers if o in poses), next(iter(poses.values()), None))
                yaw = state.yaw if state.yaw is not None else (near.yaw if near is not None else 0.0)
                z = self._ground_z(state.centre[0], state.centre[1], near.z if near is not None else 0.0)
                corners = box_corners(state.centre, yaw, entity.length, entity.width, z, size.height)
                footprint = [self._project(corner) for corner in corners[:4]]
                if all(point is not None for point in footprint):
                    self.pygame.draw.polygon(self.overlay, ROAD_USER_RGB + (80 if state.measured else 40,), footprint)
                users.append((entity, state, corners, yaw))
            self.screen.blit(self.overlay, (0, 0))
        labels = [self._draw_ghost(track, state, corners, index) for track, state, corners, index in boxes]
        labels += [self._draw_road_user(entity, state, corners, yaw) for entity, state, corners, yaw in users]
        labels += [self._draw_track_dot(track, state, observer, index) for track, state, observer, index in dots]
        labels += self._draw_interaction_links(ghosts + dots, t)
        return [label for label in labels if label is not None]

    def _draw_interaction_links(self, tracks: Sequence[Tuple[Any, Any, Pose, int]], t: float) -> List[Any]:
        """The semantic link of an active interaction: a line from the observer to the track it holds
        CRITICAL_TTC or CUT_IN about, or to its nearest IN_EGO_PATH track, labelled with their body-to-body
        clearance (the track's near surface to the observer's own footprint, as the reconstruction measured
        it).  One label per observer and road user (the closest of its tracks).  Returns the deferred label
        drawings."""
        best: Dict[Tuple[str, str], Tuple[float, Any, Any, Pose]] = {}
        leader: Dict[str, Tuple[float, str, Any, Any, Pose]] = {}
        for track, state, observer, _ in tracks:
            if state.clearance is None:
                continue
            perceived = self.run.perceived.get(track.recorder)
            snapshot = perceived.state_at(t) if perceived is not None else None
            states = ((snapshot or {}).get("external") or {}).get(track.track_id) or {}
            subject = subject_label(self.run, track.recorder, track.track_id)
            if any(states.get(name) is True for name in INTERACTION_STATES):
                key = (track.recorder, subject)
                if key not in best or state.clearance < best[key][0]:
                    best[key] = (state.clearance, track, state, observer)
            if states.get("IN_EGO_PATH") is True:
                if track.recorder not in leader or state.clearance < leader[track.recorder][0]:
                    leader[track.recorder] = (state.clearance, subject, track, state, observer)
        for recorder, (clearance, subject, track, state, observer) in leader.items():
            if (recorder, subject) not in best:
                best[(recorder, subject)] = (clearance, track, state, observer)
        labels = []
        for (recorder, _), (clearance, track, state, observer) in sorted(best.items()):
            x, y = state.position
            point = (x, y, self._ground_z(x, y, observer.z) + TRACK_DOT_HEIGHT_M)
            start = (observer.x, observer.y, observer.z + 1.0)
            color = self.colors[recorder]
            self._line3d(start, point, color, 2)
            middle = self._project(((start[0] + point[0]) / 2.0, (start[1] + point[1]) / 2.0, (start[2] + point[2]) / 2.0))
            if middle is not None:
                labels.append(lambda uv=middle, text="{0:.1f} m".format(max(clearance, 0.0)), rgb=color:
                              self._distance_label(uv, text, rgb))
        return labels

    def _distance_label(self, uv: Tuple[int, int], text: str, color: Tuple[int, int, int]) -> None:
        """A compact clearance label on a link line, moved to free space."""
        surface = self.font_small.render(text, True, (255, 255, 255))
        rect = self._free_rect(self.pygame.Rect(uv[0] - surface.get_width() // 2 - 4, uv[1] - surface.get_height() // 2,
                                                surface.get_width() + 8, surface.get_height()))
        self._panel(tuple(rect), 190)
        self.pygame.draw.rect(self.screen, color, tuple(rect), 1)
        self.screen.blit(surface, (rect.left + 4, rect.top))
        self.occupied.append(rect.inflate(4, 4))

    def _draw_road_user(self, entity: EntityPath, state: EntityState, corners: List[Vector], yaw: float) -> Any:
        """An anonymous road user of the fusion: its fitted box, an arrow along its motion (none while its
        heading is unknown), solid while measured, dashed while only predicted, and its compact U label.
        Returns the deferred label drawing."""
        dashed = not state.measured
        for i, j in BOX_EDGES:
            self._line3d(corners[i], corners[j], ROAD_USER_RGB, 2, dashed)
        roof = corners[4][2]
        if state.heading != HEADING_UNKNOWN and state.yaw is not None:
            reach = entity.length / 2.0 + 1.5
            fx, fy = rotate(reach, 0.0, yaw)
            tip = (state.centre[0] + fx, state.centre[1] + fy, roof)
            self._line3d((state.centre[0], state.centre[1], roof), tip, ROAD_USER_RGB, 3, dashed)
            for side in (-1.0, 1.0):
                bx, by = rotate(-1.0, 0.6 * side, yaw)
                self._line3d(tip, (tip[0] + bx, tip[1] + by, roof), ROAD_USER_RGB, 3, dashed)
        anchor = self._project((state.centre[0], state.centre[1], roof + 0.3))
        if anchor is None:
            return None
        lines = [entity.entity_id]
        return lambda: self._label(anchor, lines, ROAD_USER_RGB, len(self.ids), above=True)

    def _track_lines(self, track: TrackPath, state: TrackPoint) -> List[str]:
        """The track's global subject name (a track no fusion named keeps its local id)."""
        return [subject_label(self.run, track.recorder, track.track_id)]

    def _draw_ghost(self, track: TrackPath, state: TrackPoint, corners: List[Vector], index: int) -> Any:
        """An anonymous track as a ghost: the reconstruction's nominal box where its CRITICAL_TTC model
        places the target, an arrow along the estimated motion (none while the heading is unknown),
        solid while measured, dashed while only predicted.  Returns the deferred label drawing."""
        color = self.colors[track.recorder]
        size = self.run.geometry
        dashed = not state.measured
        for i, j in BOX_EDGES:
            self._line3d(corners[i], corners[j], color, 2, dashed)
        roof = corners[4][2]
        if state.heading != HEADING_UNKNOWN:
            reach = size.length / 2.0 + 1.5
            fx, fy = rotate(reach, 0.0, state.yaw)
            tip = (state.centre[0] + fx, state.centre[1] + fy, roof)
            self._line3d((state.centre[0], state.centre[1], roof), tip, color, 3, dashed)
            for side in (-1.0, 1.0):
                bx, by = rotate(-1.0, 0.6 * side, state.yaw)
                self._line3d(tip, (tip[0] + bx, tip[1] + by, roof), color, 3, dashed)
        anchor = self._project((state.centre[0], state.centre[1], roof + 0.3))
        if anchor is None:
            return None
        lines = self._track_lines(track, state)
        return lambda: self._label(anchor, lines, color, index, above=True)

    def _draw_track_dot(self, track: TrackPath, state: TrackPoint, observer: Pose, index: int) -> Any:
        """A radar dot at the track estimate.  For a track associated with a recorder (that recorder's
        replayed vehicle: no second body), a line from the observer and ``A:track_002 → B``.
        Returns the deferred label drawing."""
        pg = self.pygame
        color = self.colors[track.recorder]
        x, y = state.position
        point = (x, y, self._ground_z(x, y, observer.z) + TRACK_DOT_HEIGHT_M)
        uv = self._project(point)
        if track.status == ASSOCIATED and (track.recorder, track.entity) not in self.associated_lines:
            # One line per observer and recorder: several tracks of one body are one subject.
            self.associated_lines.add((track.recorder, track.entity))
            self._line3d((observer.x, observer.y, observer.z + 1.0), point, color, 1)
        if uv is None:
            return None
        if state.measured:
            pg.draw.circle(self.screen, color, uv, 6)
            pg.draw.circle(self.screen, (255, 255, 255), uv, 6, width=2)
        else:
            pg.draw.circle(self.screen, color, uv, 6, width=2)  # hollow: predicted
        if not track.ghost:
            return None  # its global subject is already named: the U label or the recorder's own badge
        lines = self._track_lines(track, state)
        return lambda: self._label(uv, lines, color, index, above=False)

    def _free_rect(self, rect: Any) -> Any:
        """``rect`` or the nearest shift of it (rows up and down, or slid left of what it hits) that is
        inside the window and covers nothing in ``self.occupied``; ``rect`` itself when none is free."""
        window = self.pygame.Rect(0, 0, self.width, self.height)
        for rows in (0, -1, 1, -2, 2, -3, 3, -4, 4, -5, 5, -6, 6):
            moved = rect.move(0, rows * (rect.height + 3))
            candidates = [moved] + [moved.move(other.left - 4 - moved.right, 0)
                                    for other in self.occupied if moved.colliderect(other)]
            for candidate in candidates:
                if window.contains(candidate) and candidate.collidelist(self.occupied) < 0:
                    return candidate
        return rect

    def _label(self, anchor: Tuple[int, int], lines: List[str], color: Tuple[int, int, int], index: int,
               above: bool) -> None:
        """A small panel with a bar in the recorder's colour and a leader line to what it names: above
        a ghost box (one row per recorder, so the labels of overlapping ghosts of two recorders do not
        cover each other) or left of a dot (vehicle panels sit to the right), moved to free space."""
        pg = self.pygame
        surfaces = [self.font_small.render(text, True, (255, 255, 255)) for text in lines]
        width = max(surface.get_width() for surface in surfaces) + 13
        height = sum(surface.get_height() for surface in surfaces) + 2
        u, v = anchor
        if above:
            rect = pg.Rect(u - width // 2, v - height - 6 - index * (height + 4), width, height)
        else:
            row = index - (len(self.ids) - 1) / 2.0
            rect = pg.Rect(u - 14 - width, int(round(v - height / 2.0 + (height + 2) * row)), width, height)
        rect = self._free_rect(rect)
        end = (min(max(u, rect.left), rect.right), rect.bottom) if above \
            else (rect.right, min(max(v, rect.top), rect.bottom))
        pg.draw.line(self.screen, color, (u, v), end, 1)
        self._panel(tuple(rect), 165)
        pg.draw.rect(self.screen, color, (rect.left, rect.top, 4, rect.height))
        y = rect.top + 1
        for surface in surfaces:
            self.screen.blit(surface, (rect.left + 9, y))
            y += surface.get_height()

    def _line3d(self, a: Vector, b: Vector, color: Tuple[int, int, int], width: int = 2, dashed: bool = False) -> None:
        """A world segment, clipped at the camera's near plane and at the window."""
        segment = project_segment(a, b, self.camera_pose, self.args.fov, self.width, self.height)
        if segment is None:
            return
        clipped = self.pygame.Rect(-4, -4, self.width + 8, self.height + 8).clipline(segment[0], segment[1])
        if not clipped:
            return
        p0, p1 = clipped
        if not dashed:
            self.pygame.draw.line(self.screen, color, p0, p1, width)
            return
        length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        if length < 1.0:
            return
        ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
        start = 0.0
        while start < length:  # 9 px dashes, 7 px gaps
            end = min(start + 9.0, length)
            self.pygame.draw.line(self.screen, color, (p0[0] + ux * start, p0[1] + uy * start),
                                  (p0[0] + ux * end, p0[1] + uy * end), width)
            start += 16.0

    def _draw_collision_banner(self, t: float) -> None:
        """The collisions of the last COLLISION_WINDOW_S, every pair kept (repeated contacts too), centred in the
        free span between the HUD and the recorder panels and wrapped onto several lines when they do not fit
        (focus mode narrows the span); below the HUD when the span is too narrow."""
        marks = self.run.collisions_near(t, COLLISION_WINDOW_S)
        if not marks:
            return
        pairs = ["–".join(mark.participants) for mark in marks if mark.participants]
        hud = getattr(self, "hud_rect", (8, 8, 0, 0))
        left, right, top = hud[0] + hud[2] + 16, getattr(self, "panel_left", self.width - 8) - 16, 16
        if right - left < 220:  # no room beside the HUD: under it
            left, top = 8, hud[1] + hud[3] + 10
        lines = [line.strip() for line in wrap_text("  ".join(["COLLISION"] + pairs),
                                                    lambda text: self.font_banner.size(text)[0],
                                                    max(right - left - 28, self.font_banner.size("COLLISION")[0]), "")]
        lines = [line for line in lines if line]
        rendered = [self.font_banner.render(line, True, (255, 255, 255)) for line in lines]
        width = max(r.get_width() for r in rendered) + 28
        height = sum(r.get_height() for r in rendered) + 12
        box = self.pygame.Rect(0, 0, width, height)
        box.midtop = ((left + right) // 2, top - 6)
        box.left = max(min(box.left, right - width), min(left, self.width - width))
        self.pygame.draw.rect(self.screen, (200, 20, 30), box, border_radius=8)
        self.occupied.append(box)
        y = box.top + 6
        for surface in rendered:
            self.screen.blit(surface, surface.get_rect(midtop=(box.centerx, y)))
            y += surface.get_height()

    def _draw_hud(self, t: float) -> None:
        state = "END" if self.clock.at_end and not self.clock.playing else ("PLAYING" if self.clock.playing else "PAUSED")
        camera = self.camera_mode + (" " + self.selected if self.camera_mode == "follow" else "")
        tracks = ("tracks: ghost boxes + dots" if self.show_ghosts else "tracks: dots") if self.show_tracks \
            else "tracks hidden"
        lines = [(self.run.name + "  (" + self.map_name + ")", self.font_bold, (255, 255, 255)),
                 (("t_global {0:+6.2f} s   replay {1:5.2f} / {2:.2f} s" if self.run.clock == "t_global" else
                   "t_contact {0:+6.2f} s   scenario {1:5.2f} / {2:.2f} s" if self.run.clock == "t_contact" else
                   "Time  {1:6.2f} / {2:.2f} s (recorded source clock)").format(self.run.display_time(t), t,
                                                                               self.run.duration),
                  self.font, (255, 255, 255)),
                 (("GROUND TRUTH (CARLA): true trajectories and physical contacts" if self.run.clock == "t_contact"
                   else "RECONSTRUCTION: recorders at their sensor (GNSS/INS) pose, estimated road users"),
                  self.font_bold, (255, 200, 80) if self.run.clock == "t_contact" else (120, 200, 255)),
                 ("Speed {0:.2f}x   {1}".format(self.clock.speed, state), self.font,
                  (120, 230, 120) if state == "PLAYING" else (255, 170, 60)),
                 ("Camera {0}   selected {1}   {2}".format(camera, self.selected, tracks),
                  self.font_small, (200, 200, 200))]
        passed = [e for e in self.events if e.time <= t + 1e-6]
        upcoming = [e for e in self.events if e.time > t + 1e-6]
        if passed:
            e = passed[-1]
            lines.append(("last {0:+6.2f} {1}".format(self.run.display_time(e.time), event_line(self.run, e)),
                          self.font_small, (255, 214, 10)))
        if upcoming:
            e = upcoming[0]
            lines.append(("next {0:+6.2f} {1}".format(self.run.display_time(e.time), event_line(self.run, e)),
                          self.font_small, (200, 200, 200)))
        if not self.run.local_events and self.run.clock != "t_contact":
            lines.append(("NO RECONSTRUCTION: run scripts/reconstruct_run.py on this run (no boxes, no events)",
                          self.font_bold, (255, 90, 90)))
        rendered = [font.render(text, True, rgb) for text, font, rgb in lines]
        width = max(r.get_width() for r in rendered) + 16
        height = sum(r.get_height() for r in rendered) + 10
        self._panel((8, 8, width, height))
        self.hud_rect = (8, 8, width, height)
        y = 13
        for surface in rendered:
            self.screen.blit(surface, (16, y))
            y += surface.get_height()

    def _timeline_rect(self) -> Tuple[int, int, int, int]:
        return 12, self.height - 26, self.width - 24, 14

    def _timeline_hit(self, pos: Tuple[int, int]) -> bool:
        x, y, w, h = self._timeline_rect()
        return x <= pos[0] <= x + w and y - 8 <= pos[1] <= y + h + 8

    def _seek_to_pixel(self, px: int) -> None:
        x, _, w, _ = self._timeline_rect()
        self.clock.seek_to((px - x) / float(w) * self.run.duration)

    def _help_lines(self) -> List[str]:
        if not self.show_help:
            return []
        if self.peer is not None:
            return list(HELP_LINES) + ["side by side: play, seek, speed, N/P, camera and ESC act on both viewers"]
        return list(HELP_LINES)

    def _bottom_bar_top(self) -> int:
        """Top of the help lines and timeline at the bottom of the window."""
        return self._timeline_rect()[1] - 14 - 16 * len(self._help_lines())

    def _draw_timeline(self, t: float) -> None:
        pg = self.pygame
        x, y, w, h = self._timeline_rect()
        help_lines = self._help_lines()
        top = self._bottom_bar_top() + 4
        self._panel((0, top - 4, self.width, self.height - top + 4), 140)
        for index, text in enumerate(help_lines):
            self.screen.blit(self.font_small.render(text, True, (220, 220, 220)), (x, top + 16 * index))
        duration = max(self.run.duration, 1e-6)
        pg.draw.rect(self.screen, (70, 70, 70), (x, y, w, h), border_radius=4)
        pg.draw.rect(self.screen, (150, 150, 150), (x, y, int(w * t / duration), h), border_radius=4)
        for event in self.events:
            ex = x + int(w * event.time / duration)
            pg.draw.line(self.screen, self.colors.get(event.actor, (255, 255, 255)), (ex, y + 2), (ex, y + h - 2), 2)
        for mark in self.run.collisions:
            mx = x + int(w * mark.time / duration)
            pg.draw.line(self.screen, (230, 20, 30), (mx, y - 5), (mx, y + h + 5), 3)
        cx = x + int(w * t / duration)
        pg.draw.line(self.screen, (255, 255, 255), (cx, y - 7), (cx, y + h + 7), 2)


class SelfTest:
    """Hidden ``--selftest``: drives the real window through pygame's event queue (no desktop access needed)."""

    WARMUP_S, PERIOD_S, PRESSES = 6.0, 3.0, 6

    def __init__(self, app: "ReplayApp", directory: Path, started: float) -> None:
        self.app, self.directory, self.started = app, directory, started
        self.directory.mkdir(parents=True, exist_ok=True)
        self.saved, self.pressed, self.log, self.hud = 0, 0, [], []

    def _camera(self) -> str:
        return self.app.camera_mode + (" " + self.app.selected if self.app.camera_mode == "follow" else "")

    def step(self, now: float) -> None:
        pg, elapsed = self.app.pygame, now - self.started
        due = self.WARMUP_S + self.saved * self.PERIOD_S
        if elapsed >= due and self.saved == self.pressed:
            name = "{0:02d}_{1}.png".format(self.saved, self._camera().replace(" ", "_"))
            pg.image.save(self.app.screen, str(self.directory / name))
            self.log.append(self._camera())
            t = self.app.clock.time
            self.hud.append({"t": round(t, 2), "panels": {pid: [text for text, _, _ in self.app._vehicle_lines(pid, t)]
                                                          for pid in self.app.ids}})
            self.saved += 1
            if self.pressed >= self.PRESSES:
                actors = sorted((a.attributes.get("role_name", ""), a.type_id)
                                for a in self.app.world.get_actors().filter("vehicle.*"))
                (self.directory / "selftest.json").write_text(json.dumps(
                    {"run": self.app.run.name, "camera_sequence": self.log, "panels": self.hud,
                     "vehicle_actors": actors,
                     "recorders": self.app.ids}, indent=1), encoding="utf-8")
                self.app._quit()  # as ESC: side by side, the other viewer closes too
        elif elapsed >= due - self.PERIOD_S / 2.0 and self.pressed < self.saved and self.pressed < self.PRESSES:
            pg.event.post(pg.event.Event(pg.KEYDOWN, key=pg.K_c, mod=0))
            self.pressed += 1


_LANES: Dict[str, Any] = {}


def export_lanes(run: ReplayRun, map_name: Optional[str] = None) -> Tuple[Optional[str], Optional[List[Any]]]:
    """(map, driving lanes) for the headless export: the map recognised from the recorded positions and
    the public OpenDRIVE files (``resolve_map``), parsed client-side by the carla module or, without it, by
    ``cdf.replay.opendrive`` (pure Python); (None, None) without a local installation.  No server, scenario or run metadata is used."""
    try:
        carla = import_carla()
    except Exception:  # without the carla module: the same public OpenDRIVE geometry, sampled in pure Python
        from cdf.replay.opendrive import best_map, lanes_from_opendrive
        sources = opendrive_sources(find_carla_root(load_run_config().get("simulation.carla_root")))
        if map_name:
            if map_name not in sources:
                return map_name, None
            if map_name not in _LANES:
                _LANES[map_name] = lanes_from_opendrive(sources[map_name])
            return map_name, _LANES[map_name]
        return best_map(sources, [(x, y) for x, y, _ in run.map_samples()], MAP_MIN_FIT)
    root = find_carla_root(load_run_config().get("simulation.carla_root"))
    sources = opendrive_sources(root)
    name = map_name or resolve_map(run, root, None)
    if not name or name not in sources:
        return name, None
    if name not in _LANES:
        _LANES[name] = lanes_from_map(parsed_map(carla, name, sources[name]))
    return name, _LANES[name]


def export_run(run_dir: Path, directory: Path, at: Sequence[float] = (), image_format: str = "png",
               map_name: Optional[str] = None, run: Any = None) -> List[Dict[str, Any]]:
    """Headless export of one run: top-down frames at ``at`` (displayed times) or at its keyframes."""
    if run is None:
        run = ReplayRun.load(Path(run_dir))
        run.name = "RECONSTRUCTION  " + run.name
    name, lanes = export_lanes(run, map_name)
    LOGGER.info("%s: map %s, %s", run.name, name or "unknown", "lanes drawn" if lanes else "no lanes")
    times = None
    if at:
        offset = run.display_time(0.0)
        times = [("t = {0:+.2f} s".format(value), value - offset) for value in at]
    return export_keyframes(run, Path(directory), lanes=lanes, times=times, suffix="." + image_format)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    run_dir = Path(args.run_dir)
    if args.export:
        for frame in export_run(run_dir, Path(args.export), args.at, args.format, supplied_map(args)[0]):
            LOGGER.info("%s  %s", frame["file"], frame["label"])
        return 0
    run = ReplayRun.load(run_dir)
    return view(run, args)


def supplied_map(args: argparse.Namespace, run: Any = None) -> Tuple[Optional[str], str]:
    """(map to load, where it comes from): ``--map``; for the GROUND TRUTH viewer its own acquisition metadata;
    else the road map of the run's supplied incident context, read as the reconstruction reads it (known context,
    never the simulator server's state).  (None, ...) for a run whose context names no map."""
    if args.map:
        return args.map, "--map"
    truth_map = getattr(run, "map_name", None)
    if truth_map:
        return truth_map, "the ground-truth acquisition metadata"
    return incident_map(Path(args.run_dir)), "the supplied incident context"


def view(run: Any, args: argparse.Namespace) -> int:
    """Open the interactive viewer on a loaded run (a ReplayRun of the reconstruction, or another model with
    the same interface: scripts/view_ground_truth.py)."""
    run_dir = Path(args.run_dir)
    for note in run.notes:
        LOGGER.info("note: %s", note)
    if not run.local_events:
        LOGGER.warning("%s has no reconstruction (no %s): the replay shows the recorders only, no reconstructed "
                       "road users and no events; run scripts/reconstruct_run.py %s first", run.name,
                       run_dir / "reconstruction", run_dir)
    if run.clock == "t_contact":  # the GROUND TRUTH viewer: true vehicles and true contacts, nothing reconstructed
        LOGGER.info("%s: vehicles %s, %.2f s, %d ground-truth contact event(s)", run.name,
                    ", ".join(p.participant_id for p in run.participants), run.duration, len(run.all_events()))
    else:
        LOGGER.info("%s: recorders %s, %.2f s, %d reconstructed event(s), anonymous road users: %s%s", run.name,
                    ", ".join(p.participant_id for p in run.participants), run.duration, len(run.all_events()),
                    "; ".join("{0} = {1}".format(e.entity_id, e.sources) for e in run.entities) or "none",
                    "" if not run.ghost_tracks() else "; unfused tracks: " + ", ".join(t.name for t in run.ghost_tracks()))

    # configs/default.yaml: only the simulator connection (no scenario).
    cfg = load_run_config(overrides=[] if args.port is None else ["simulation.port={0}".format(args.port)])
    session = session_from_config(cfg, autostart=not args.no_autostart)
    app = None
    try:
        map_name, source = supplied_map(args, run)
        if not map_name:  # a run recorded before its incident context named the map
            server_map = session.client().get_world().get_map()
            map_name = resolve_map(run, find_carla_root(cfg.get("simulation.carla_root")),
                                   map_basename(server_map.name), server_map)
            source = "recognised from the recorded positions"
            if not map_name:
                LOGGER.error("cannot recognise the map of %s: its incident context names none and the recorded "
                             "positions fit no single map; pass --map", run_dir)
                return 2
        LOGGER.info("map %s (%s)", map_name, source)
        world = session.world_for_map(map_name)
        app = ReplayApp(run, map_name, session.client(), world, args)
        app.setup()
        app.run_loop()
    except KeyboardInterrupt:
        LOGGER.info("interrupted")
    finally:
        if app is not None:
            app.close()
        if not args.keep_server:
            session.close()  # stops only a server this viewer started
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
