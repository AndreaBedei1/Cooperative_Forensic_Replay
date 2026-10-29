"""Execute one fixed scenario and write raw CARLA acquisitions."""

from __future__ import annotations

import json
import logging
import math
import platform
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..common.config import Config
from ..common.geometry import distance
from ..recording.ground_truth_logger import GroundTruthLogger
from .carla_client import import_carla
from .scenario_base import ScenarioSpec, build_route, make_controller, resolve_spawn_waypoint
from .triggers import Pose, fire_due_triggers
from .vehicle_agent import RawVehicleAgent
from .world import ScenarioWorld

LOGGER = logging.getLogger(__name__)
POST_IMPACT_RECORDING_S = 5.0


def _state(actor: Any, frame: int, timestamp: float) -> dict:
    tf = actor.get_transform(); v = actor.get_velocity(); a = actor.get_acceleration(); w = actor.get_angular_velocity()
    bbox = getattr(actor, "bounding_box", None)
    extent = getattr(bbox, "extent", None)
    return {"frame": int(frame), "timestamp": float(timestamp), "actor_id": int(actor.id), "type_id": str(actor.type_id),
            "transform": {"x": float(tf.location.x), "y": float(tf.location.y), "z": float(tf.location.z), "roll_deg": float(tf.rotation.roll), "pitch_deg": float(tf.rotation.pitch), "yaw_deg": float(tf.rotation.yaw)},
            "bbox_extent": {"x": float(extent.x), "y": float(extent.y), "z": float(extent.z)} if extent is not None else None,
            "velocity": {"x": float(v.x), "y": float(v.y), "z": float(v.z)}, "acceleration": {"x": float(a.x), "y": float(a.y), "z": float(a.z)},
            "angular_velocity": {"x": float(w.x), "y": float(w.y), "z": float(w.z)}}


def _position_spectator(world: Any, vehicles: List[Any], carla: Any) -> None:
    """Keep CARLA's spectator on a read-only overhead view of the run."""
    if not vehicles:
        return
    transforms = [vehicle.get_transform() for vehicle in vehicles]
    locations = [transform.location for transform in transforms]
    center_x = sum(float(location.x) for location in locations) / len(locations)
    center_y = sum(float(location.y) for location in locations) / len(locations)
    center_z = sum(float(location.z) for location in locations) / len(locations)
    span = max(
        max(float(location.x) for location in locations) - min(float(location.x) for location in locations),
        max(float(location.y) for location in locations) - min(float(location.y) for location in locations),
        1.0,
    )
    offset = min(12.0, max(6.0, span * 0.2))
    altitude = max(35.0, min(45.0, 35.0 + span * 0.15))
    camera_location = carla.Location(
        x=center_x + offset,
        y=center_y - offset,
        z=center_z + altitude,
    )
    look_x = center_x - float(camera_location.x)
    look_y = center_y - float(camera_location.y)
    look_z = center_z - float(camera_location.z)
    horizontal = math.hypot(look_x, look_y)
    spectator = world.get_spectator()
    spectator.set_transform(
        carla.Transform(
            camera_location,
            carla.Rotation(
                pitch=math.degrees(math.atan2(look_z, horizontal)),
                yaw=math.degrees(math.atan2(look_y, look_x)),
                roll=0.0,
            ),
        )
    )


def _pose(actor: Any) -> Pose:
    """True planar pose and box of an actor, for privileged triggers only."""
    tf = actor.get_transform()
    extent = actor.bounding_box.extent
    return Pose(x=float(tf.location.x), y=float(tf.location.y), yaw_deg=float(tf.rotation.yaw),
                half_length=float(extent.x), half_width=float(extent.y))


def _scheduled_end(spec: ScenarioSpec) -> float:
    """When every declared manoeuvre is over (an armed triggered action: if it fired
    at the end of its window).  A turn indicator is a light, not a manoeuvre: one left on
    beyond the run does not extend it.  Capture control only."""
    return max([action.latest_end() for participant in spec.participants for action in participant.actions
                if (action.enabled or action.trigger is None) and action.kind != "indicator"], default=0.0)


def write_incident_context(run_root: Path, context: Dict[str, Any], map_name: Optional[str] = None) -> None:
    """Copy the scenario's supplied incident context into the run.

    This is known context such as the legal speed limit at the incident
    location and the road map of that location (``map``: an investigation
    knows where the incident happened): neither perceived by a vehicle nor
    privileged ground truth.  It is the only scenario information the
    reconstruction may read.
    """
    if not context and not map_name:
        LOGGER.warning("scenario defines no incident context: no speed limit will be available")
        return
    limit = context.get("speed_limit_kmh")
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, (int, float)) or limit <= 0):
        raise ValueError("context.speed_limit_kmh must be a positive number")
    record = dict(context)
    if map_name:
        record["map"] = str(map_name)
    record["note"] = "supplied incident context from the scenario configuration; not perceived, not ground truth"
    (Path(run_root) / "incident_context.json").write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")


def run_scenario(client: Any, cfg: Config, spec: ScenarioSpec, seed: int, output_root: str = "traces") -> Path:
    """Run one scenario variant and return its trace directory."""
    carla = import_carla()
    run_name = f"run_{int(seed)}" if spec.variant == "default" else f"run_{int(seed)}_{spec.variant}"
    run_root = Path(output_root) / spec.scenario_id / run_name
    run_root.mkdir(parents=True, exist_ok=True)
    write_incident_context(run_root, spec.context, spec.map_name)
    # Privileged: every physical participant, recorder or not.
    gt = GroundTruthLogger(run_root, {"scenario_id": spec.scenario_id, "variant": spec.variant, "seed": int(seed),
                                      "map": spec.map_name,
                                      "participants": [{"participant_id": p.participant_id, "record": bool(p.record)}
                                                       for p in spec.participants]})
    agents: List[RawVehicleAgent] = []
    simulation_start_timestamp = None
    simulation_end_timestamp = None
    fixed_delta_seconds = None
    try:
        with ScenarioWorld(client, cfg, spec.map_name, seed=seed) as sworld:
            # A moving vehicle is launched (below) over launch_ticks ticks before the recording
            # starts; it is spawned that far back along its lane, so that the recording starts with
            # it at its scenario spawn point.
            launch_ticks = int(cfg.get("simulation.launch_ticks", 12))
            launch_s = launch_ticks * float(cfg.get("simulation.fixed_delta_seconds", 0.05))
            placements = []
            for pspec in spec.participants:
                wp = resolve_spawn_waypoint(sworld.map, sworld.spawn_points(), pspec.spawn)
                start = wp
                back = float(pspec.initial_speed) * launch_s
                if back > 0.01:
                    previous = wp.previous(back)
                    if not previous:
                        raise ValueError("no lane {0:.1f} m behind the spawn point of {1} for its launch".format(
                            back, pspec.participant_id))
                    start = previous[0]
                placements.append((pspec, start, build_route(sworld.map, wp, pspec.route)))
            for i, (_, wp, _) in enumerate(placements):
                for _, prior, _ in placements[:i]:
                    if distance(wp.transform.location.x, wp.transform.location.y, prior.transform.location.x, prior.transform.location.y) < float(cfg.get("simulation.min_spawn_gap_m", 5.0)):
                        raise ValueError("scenario spawn points are too close")
            for pspec, wp, route in placements:
                tf = wp.transform
                transform = carla.Transform(carla.Location(x=tf.location.x, y=tf.location.y, z=tf.location.z + float(cfg.get("simulation.spawn_z_offset", 0.3))), carla.Rotation(pitch=0, yaw=tf.rotation.yaw, roll=0))
                agent = RawVehicleAgent(sworld, cfg, pspec, make_controller(pspec, route), transform, run_root)
                agents.append(agent)
            sworld.warmup()
            # Launch: the scripted initial velocity is held for launch_ticks ticks in each vehicle's
            # cruising gear, at a nominal cruising throttle, steered along its route; its speed
            # controller then starts from that throttle.  The recording starts in a steady cruise
            # instead of CARLA's start-up transient (neutral -> first gear at speed: 10-20 m/s^2 of
            # engine braking under full throttle; with fewer than ~10 ticks the drivetrain has not
            # caught up with the imposed speed and the car loses up to 1 m/s once released).
            launch_throttle = float(cfg.get("simulation.launch_throttle", 0.5))
            moving = [agent for agent in agents if float(agent.spec.initial_speed)]
            for k in range(launch_ticks):
                for agent in moving:
                    agent.hold_initial_velocity(float(agent.spec.initial_speed), launch_throttle,
                                                t=-(launch_ticks - k) * sworld.delta_seconds,
                                                dt=sworld.delta_seconds)
                sworld.tick()
            for agent in moving:
                agent.controller.preload_cruise(launch_throttle)
            # CARLA's elapsed clock is not reset when the requested map is
            # already loaded. The scripted timeline begins after physics has
            # settled and the configured initial velocity has taken effect,
            # exactly as the scenario definitions expect.
            simulation_start = sworld.elapsed_seconds
            dt = sworld.delta_seconds
            simulation_start_timestamp = float(simulation_start)
            fixed_delta_seconds = float(dt)
            _position_spectator(sworld.world, [agent.vehicle for agent in agents], carla)
            for agent in agents:
                agent.set_sensor_start_frame(sworld.frame + 1)
            limit = min(float(spec.max_duration_s), float(cfg.get("simulation.max_duration_s", spec.max_duration_s)))
            scheduled_end = _scheduled_end(spec)
            armed = [(agent.spec.participant_id, action) for agent in agents for action in agent.controller.actions
                     if action.armed]
            last_collision_t = None
            wall_clock_start = time.monotonic()
            while sworld.elapsed_seconds - simulation_start <= limit + 1e-9:
                snapshot = sworld.tick(); frame = int(snapshot.frame); timestamp = float(snapshot.timestamp.elapsed_seconds)
                simulation_end_timestamp = timestamp
                scenario_timestamp = timestamp - simulation_start
                _position_spectator(sworld.world, [agent.vehicle for agent in agents], carla)
                if armed:
                    # Privileged scenario construction: true poses of the actors in this run.
                    poses = {agent.spec.participant_id: _pose(agent.vehicle) for agent in agents}
                    for record in fire_due_triggers(scenario_timestamp, poses, armed):
                        gt.trigger(dict(record, frame=frame, timestamp=timestamp))
                        LOGGER.info("trigger fired: %s %s at %.2f s", record["participant_id"],
                                    record["action_id"], scenario_timestamp)
                    armed = [(owner, action) for owner, action in armed if action.armed]
                    scheduled_end = _scheduled_end(spec)
                for agent in agents:
                    agent.receive_sensors(frame)
                controls = {
                    agent.spec.participant_id: agent.step(
                        scenario_timestamp, frame, dt, recorded_timestamp=timestamp
                    )
                    for agent in agents
                }
                for agent in agents:
                    gt.state({"participant_id": agent.spec.participant_id, **_state(agent.vehicle, frame, timestamp)})
                    gt.control({"participant_id": agent.spec.participant_id, **controls[agent.spec.participant_id]})
                    for collision in agent.ground_truth_collisions():
                        gt.collision({"participant_id": agent.spec.participant_id, **collision})
                        last_collision_t = scenario_timestamp
                # The reference runner ended a non-contact recording once every
                # declared manoeuvre had completed.  When a contact occurs, it
                # instead retains a fixed post-impact window, anchored to the
                # latest physical collision so a chain's secondary impact is
                # never truncated.  This is execution/capture control only;
                # it does not inspect expected outcomes or alter vehicle inputs.
                if scheduled_end > 0.0:
                    if last_collision_t is None and scenario_timestamp >= scheduled_end:
                        break
                    if (last_collision_t is not None
                            and scenario_timestamp >= scheduled_end
                            and scenario_timestamp >= last_collision_t + POST_IMPACT_RECORDING_S):
                        break
                # Real-time pacing lets a person watch; in synchronous mode it changes no sample, so a
                # batch of runs (scripts/run_sweep.py) may switch it off.
                if bool(cfg.get("simulation.real_time_pacing", True)):
                    remaining_wall_time = wall_clock_start + scenario_timestamp - time.monotonic()
                    if remaining_wall_time > 0.0:
                        time.sleep(remaining_wall_time)
            for agent in agents:
                agent.flush_sensor_queues()
    finally:
        late_impacts = sum(int(getattr(agent, "late_impact_notifications", 0)) for agent in agents)
        for agent in agents: agent.close()
        gt.close()
    # Recorders only: a participant with record: false is not revealed by the run's metadata.
    metadata = {"scenario_id": spec.scenario_id, "variant": spec.variant, "seed": int(seed), "participants": spec.recorder_ids, "python": sys.version, "platform": platform.platform(), "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if simulation_start_timestamp is not None:
        metadata["simulation_start_timestamp"] = simulation_start_timestamp
    if fixed_delta_seconds is not None:
        metadata["fixed_delta_seconds"] = fixed_delta_seconds
    # Collision callbacks that arrived after the tick the controller had to react on (vehicle_agent):
    # 0: no impact notification arrived after its reaction tick.  Not counted: a callback of an earlier frame
    # arriving after the controller already reacted to a later one (out-of-order delivery, not observed).
    metadata["late_impact_notifications"] = late_impacts
    if simulation_end_timestamp is not None and simulation_start_timestamp is not None:
        metadata["simulation_end_timestamp"] = simulation_end_timestamp
        metadata["recorded_duration_s"] = simulation_end_timestamp - simulation_start_timestamp
    (run_root / "metadata.json").write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    return run_root
