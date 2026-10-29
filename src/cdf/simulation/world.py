
from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..common.config import Config
from .carla_client import ensure_map, import_carla, map_basename

LOGGER = logging.getLogger(__name__)

__all__ = ["ScenarioWorld", "SpawnPlan", "resolve_spawn"]


@dataclass
class SpawnPlan:

    participant_id: str
    blueprint: str
    x: float
    y: float
    z: float
    yaw: float
    role: str = "participant"

    def as_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z, "yaw": self.yaw}


def resolve_spawn(
    carla_map: Any,
    anchor: Any,
    forward_m: float = 0.0,
    lateral_lane_offset: int = 0,
    z_offset: float = 0.3,
) -> Any:
    carla = import_carla()

    if hasattr(anchor, "transform") and hasattr(anchor, "lane_id"):
        wp = anchor
    else:
        location = anchor.location if hasattr(anchor, "location") else anchor
        wp = carla_map.get_waypoint(
            location, project_to_road=True, lane_type=carla.LaneType.Driving
        )
    if wp is None:
        raise ValueError("could not project the spawn anchor onto a driving lane")

    for _ in range(abs(int(lateral_lane_offset))):
        nxt = wp.get_right_lane() if lateral_lane_offset > 0 else wp.get_left_lane()
        if (
            nxt is None
            or nxt.lane_type != carla.LaneType.Driving
            or nxt.lane_id * wp.lane_id < 0
        ):
            raise ValueError(
                "no drivable same-direction lane {0} of the anchor".format(
                    "right" if lateral_lane_offset > 0 else "left"
                )
            )
        wp = nxt

    if abs(float(forward_m)) > 1e-6:
        candidates = wp.next(abs(float(forward_m))) if forward_m > 0 else wp.previous(abs(float(forward_m)))
        if not candidates:
            raise ValueError(
                "cannot advance {0} m along the lane from the anchor".format(forward_m)
            )
        wp = candidates[0]

    tf = wp.transform
    return carla.Transform(
        carla.Location(x=tf.location.x, y=tf.location.y, z=tf.location.z + float(z_offset)),
        carla.Rotation(pitch=0.0, yaw=tf.rotation.yaw, roll=0.0),
    )


class ScenarioWorld:

    def __init__(
        self,
        client: Any,
        cfg: Config,
        map_name: str,
        seed: int = 0,
    ) -> None:
        self.client = client
        self.cfg = cfg
        self.map_name = map_basename(map_name)
        self.seed = int(seed)
        self.rng = random.Random(self.seed)

        self.world: Any = None
        self.map: Any = None
        self.traffic_manager: Any = None

        self._original_settings: Any = None
        self._tm_original_sync: Optional[bool] = None
        self._actors: List[Any] = []
        self._sensors: List[Any] = []
        self._frame: int = 0
        self._pending_commands: List[Any] = []
        self._entered = False


    def __enter__(self) -> "ScenarioWorld":
        import_carla()
        settle = float(self.cfg.get("simulation.map_switch_settle_s", 60.0))
        self.world = ensure_map(self.client, self.map_name, settle_timeout_s=settle)
        self.map = self.world.get_map()

        self._original_settings = self.world.get_settings()
        settings = self.world.get_settings()
        settings.synchronous_mode = bool(self.cfg.get("simulation.synchronous_mode", True))
        settings.fixed_delta_seconds = float(
            self.cfg.get("simulation.fixed_delta_seconds", 0.05)
        )
        settings.substepping = bool(self.cfg.get("simulation.substepping", True))
        settings.max_substep_delta_time = float(
            self.cfg.get("simulation.max_substep_delta_time", 0.01)
        )
        settings.max_substeps = int(self.cfg.get("simulation.max_substeps", 10))
        self.world.apply_settings(settings)

        if bool(self.cfg.get("simulation.traffic_manager_enabled", True)):
            try:
                tm_port = int(self.cfg.get("simulation.traffic_manager_port", 8100))
                self.traffic_manager = self.client.get_trafficmanager(tm_port)
                self._tm_original_sync = True
                self.traffic_manager.set_synchronous_mode(True)
                self.traffic_manager.set_random_device_seed(self.seed)
            except RuntimeError as exc:
                LOGGER.warning("traffic manager unavailable (%s); continuing without it", exc)
                self.traffic_manager = None
        else:
            LOGGER.info("Traffic Manager disabled for %s", self.map_name)

        self._entered = True
        for _ in range(int(self.cfg.get("simulation.sync_settle_ticks", 10))):
            self.tick()
        LOGGER.info(
            "scenario world ready: map=%s dt=%.3f seed=%d",
            self.map_name,
            settings.fixed_delta_seconds,
            self.seed,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.cleanup()

    def cleanup(self) -> None:
        for sensor in reversed(self._sensors):
            try:
                if sensor.is_listening:
                    sensor.stop()
            except RuntimeError as exc:
                LOGGER.warning("could not stop sensor %s: %s", sensor, exc)
        destroyed: List[int] = []
        for actor in reversed(self._sensors + self._actors):
            try:
                destroyed.append(int(actor.id))
                actor.destroy()
            except RuntimeError as exc:
                LOGGER.warning("could not destroy actor %s: %s", actor, exc)
        self._sensors = []
        self._actors = []

        if destroyed and self.world is not None:
            try:
                if self.world.get_settings().synchronous_mode:
                    self.world.tick()
                survivors = [
                    int(a.id)
                    for a in self.world.get_actors(destroyed)
                    if bool(getattr(a, "is_alive", True))
                ]
                if survivors:
                    LOGGER.warning(
                        "actor(s) %s survived cleanup and are still in the world",
                        survivors,
                    )
            except RuntimeError as exc:
                LOGGER.warning("could not confirm actor destruction: %s", exc)

        if self.traffic_manager is not None and self._tm_original_sync is not None:
            try:
                self.traffic_manager.set_synchronous_mode(False)
            except RuntimeError as exc:
                LOGGER.warning("could not reset traffic manager: %s", exc)

        if self.world is not None and self._original_settings is not None:
            try:
                self.world.apply_settings(self._original_settings)
            except RuntimeError as exc:
                LOGGER.warning("could not restore world settings: %s", exc)
        self._entered = False


    def blueprint(self, blueprint_id: str, attributes: Optional[Dict[str, Any]] = None) -> Any:
        library = self.world.get_blueprint_library()
        matches = library.filter(blueprint_id)
        if not matches:
            raise ValueError("no CARLA blueprint matches {0!r}".format(blueprint_id))
        bp = matches[0]
        for key, value in (attributes or {}).items():
            if not bp.has_attribute(key):
                raise ValueError(
                    "blueprint {0!r} has no attribute {1!r}".format(bp.id, key)
                )
            bp.set_attribute(key, str(value))
        if bp.has_attribute("color"):
            options = bp.get_attribute("color").recommended_values
            if options:
                bp.set_attribute("color", options[self.rng.randrange(len(options))])
        if bp.has_attribute("role_name"):
            bp.set_attribute("role_name", "cdf")
        return bp

    def spawn_vehicle(
        self,
        blueprint_id: str,
        transform: Any,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Any:
        bp = self.blueprint(blueprint_id, attributes)
        actor = self.world.try_spawn_actor(bp, transform)
        if actor is None:
            raise RuntimeError(
                "failed to spawn {0} at ({1:.2f}, {2:.2f}, {3:.2f}) yaw={4:.1f}: the "
                "position is blocked. Scenario spawn points must be separated and "
                "derived from lane waypoints.".format(
                    blueprint_id,
                    transform.location.x,
                    transform.location.y,
                    transform.location.z,
                    transform.rotation.yaw,
                )
            )
        self._actors.append(actor)
        return actor

    def spawn_prop(
        self,
        blueprint_id: str,
        transform: Any,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Any:
        bp = self.blueprint(blueprint_id, attributes)
        actor = self.world.try_spawn_actor(bp, transform)
        if actor is not None:
            self._actors.append(actor)
        return actor

    def spawn_sensor(
        self,
        blueprint_id: str,
        transform: Any,
        attach_to: Any,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Any:
        bp = self.blueprint(blueprint_id, attributes)
        sensor = self.world.spawn_actor(bp, transform, attach_to=attach_to)
        self._sensors.append(sensor)
        return sensor

    def register_actor(self, actor: Any) -> Any:
        self._actors.append(actor)
        return actor


    def send(self, command: Any) -> None:
        self._pending_commands.append(command)

    def tick(self) -> Any:
        if not self._entered:
            raise RuntimeError("ScenarioWorld.tick() called outside its context manager")
        if self._pending_commands:
            commands, self._pending_commands = self._pending_commands, []
            for response in self.client.apply_batch_sync(commands, False):
                if getattr(response, "error", None):
                    raise RuntimeError("CARLA rejected a vehicle command: " + str(response.error))
        self._frame = self.world.tick()
        return self.world.get_snapshot()

    def warmup(self, ticks: Optional[int] = None) -> None:
        n = int(self.cfg.get("simulation.warmup_ticks", 20)) if ticks is None else int(ticks)
        for _ in range(n):
            self.tick()

    @property
    def snapshot(self) -> Any:
        return self.world.get_snapshot()

    @property
    def elapsed_seconds(self) -> float:
        return float(self.world.get_snapshot().timestamp.elapsed_seconds)

    @property
    def frame(self) -> int:
        return int(self.world.get_snapshot().frame)

    @property
    def delta_seconds(self) -> float:
        return float(self.cfg.get("simulation.fixed_delta_seconds", 0.05))


    def all_vehicles(self) -> List[Any]:
        return list(self.world.get_actors().filter("vehicle.*"))

    def traffic_lights(self) -> List[Any]:
        return list(self.world.get_actors().filter("traffic.traffic_light"))

    def spawn_points(self) -> List[Any]:
        return list(self.map.get_spawn_points())

    def waypoint(self, location: Any) -> Any:
        carla = import_carla()
        return self.map.get_waypoint(
            location, project_to_road=True, lane_type=carla.LaneType.Driving
        )
