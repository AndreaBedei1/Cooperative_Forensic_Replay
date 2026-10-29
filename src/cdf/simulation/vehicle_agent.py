
from __future__ import annotations

from collections import deque
from concurrent.futures import ThreadPoolExecutor
import math
import time
from typing import Any

from ..common.config import Config, configs_dir, load_yaml
from ..recording.vehicle_logger import VehicleLogger
from .carla_client import import_carla
from .controllers import ScriptedController, VehicleState
from .sensors import (CameraSensor, CollisionSensor, RadarSensor,
                      camera_spec_from_config, depth_camera_spec_from_config,
                      depth_radial_velocity_config_from_config,
                      depth_observation_spec_from_config,
                      depth_observations_from_bgra, radar_specs_from_config)
from ..recording.depth_velocity import DepthRadialVelocityEstimator



def cruise_gear(physics_control: Any, speed: float, margin: float = 0.85) -> int:
    gears = list(physics_control.forward_gears)
    wheel_rpm = float(speed) / (float(physics_control.wheels[0].radius) / 100.0) * 60.0 / (2.0 * math.pi)
    for index, gear in enumerate(gears, start=1):
        engine_rpm = wheel_rpm * float(gear.ratio) * float(physics_control.final_ratio)
        if engine_rpm <= margin * float(gear.up_ratio) * float(physics_control.max_rpm):
            return index
    return max(len(gears), 1)


def ego_footprint(vehicle: Any) -> dict:
    box = vehicle.bounding_box
    cx, cy, cz = float(box.location.x), float(box.location.y), float(box.location.z)
    ex, ey, ez = float(box.extent.x), float(box.extent.y), float(box.extent.z)
    return {"length_m": round(2 * ex, 4), "width_m": round(2 * ey, 4), "height_m": round(2 * ez, 4),
            "x_min_m": round(cx - ex, 4), "x_max_m": round(cx + ex, 4),
            "y_min_m": round(cy - ey, 4), "y_max_m": round(cy + ey, 4),
            "roof_z_m": round(cz + ez, 4),
            "source": "the vehicle's own bounding box (vehicle frame: x forward, y right, z up, origin at the "
                      "vehicle origin on the ground)"}


class RawVehicleAgent:
    def __init__(self, scenario_world: Any, cfg: Config, spec: Any, controller: ScriptedController,
                 spawn_transform: Any, output_root: Any) -> None:
        self.world = scenario_world; self.cfg = cfg; self.spec = spec; self.controller = controller
        self.impact_reaction_ticks = int(cfg.get("simulation.impact_reaction_ticks", 1))
        self._first_impact_frame = None
        self.late_impact_notifications = 0
        self._received_frame = None
        self.vehicle = scenario_world.spawn_vehicle(spec.blueprint, spawn_transform)
        self.record = bool(getattr(spec, "record", True))
        if not self.record:
            self.radar, self.camera, self.depth_camera = [], None, None
            self._depth_executor, self._depth_futures = None, deque()
            self.collision_sensor = CollisionSensor(scenario_world, self.vehicle)
            self.logger = None
            return
        sensor_cfg = cfg
        if spec.sensor_profile:
            profile_path = configs_dir() / "sensors" / (str(spec.sensor_profile) + ".yaml")
            profile = load_yaml(profile_path)
            sensor_cfg = cfg.with_overrides({"radar": profile.get("radar", {}), "sensors": {"profile": str(spec.sensor_profile)}})
        self.radar = [RadarSensor(scenario_world, self.vehicle, rs) for rs in radar_specs_from_config(sensor_cfg)]
        camera_spec = camera_spec_from_config(cfg, spec.blueprint)
        depth_camera_spec = depth_camera_spec_from_config(cfg)
        self.depth_observation_spec = depth_observation_spec_from_config(cfg)
        self._depth_executor = ThreadPoolExecutor(max_workers=1) if depth_camera_spec else None
        self._depth_futures = deque()
        self.camera = CameraSensor(scenario_world, self.vehicle, camera_spec) if camera_spec else None
        self.depth_camera = (CameraSensor(scenario_world, self.vehicle, depth_camera_spec,
                                          max_queue=512, report_frame_gaps=True)
                             if depth_camera_spec else None)
        self.depth_velocity_config = depth_radial_velocity_config_from_config(cfg)
        self._depth_estimator = (DepthRadialVelocityEstimator(self.depth_velocity_config)
                                 if depth_camera_spec else None)
        self.collision_sensor = CollisionSensor(scenario_world, self.vehicle)
        self.logger = VehicleLogger(output_root, spec.participant_id, {
            "participant_id": spec.participant_id, "blueprint": spec.blueprint,
            "sensor_profile": str(spec.sensor_profile or cfg.get("sensors.profile", "")),
            "radar": [r.metadata() for r in self.radar],
            "ego_footprint": ego_footprint(self.vehicle),
            "pose_sensor": {"stream": "ego.jsonl", "model": "synthetic GNSS/INS", "profile": "G0",
                            "added_error": "none", "rate_hz": round(1.0 / float(cfg.get("simulation.fixed_delta_seconds", 0.05)), 3),
                            "fields": ["timestamp", "x", "y", "z", "roll_deg", "pitch_deg", "yaw_deg", "velocity",
                                       "acceleration", "angular_velocity"],
                            "note": "an ideal receiver: zero error is a reference condition, not a real receiver"},
            "camera": camera_spec.__dict__ if camera_spec else None,
            "depth_camera": depth_camera_spec.__dict__ if depth_camera_spec else None,
            "depth_observations": self.depth_observation_spec.__dict__,
            "traffic_signs": cfg.get("traffic_signs", {}) or {},
            "depth_radial_velocity": self.depth_velocity_config.as_metadata(),
            "vehicle_transform": {"x": spawn_transform.location.x, "y": spawn_transform.location.y, "z": spawn_transform.location.z, "yaw_deg": spawn_transform.rotation.yaw},
        })

    def state_record(self, t: float, frame: int) -> dict:
        tf = self.vehicle.get_transform(); v = self.vehicle.get_velocity(); a = self.vehicle.get_acceleration(); ang = self.vehicle.get_angular_velocity()
        return {"frame": int(frame), "timestamp": float(t), "x": float(tf.location.x), "y": float(tf.location.y), "z": float(tf.location.z),
                "roll_deg": float(tf.rotation.roll), "pitch_deg": float(tf.rotation.pitch), "yaw_deg": float(tf.rotation.yaw),
                "velocity": {"x": float(v.x), "y": float(v.y), "z": float(v.z)}, "acceleration": {"x": float(a.x), "y": float(a.y), "z": float(a.z)},
                "angular_velocity": {"x": float(ang.x), "y": float(ang.y), "z": float(ang.z)}}

    def hold_initial_velocity(self, speed: float, throttle: float, t: float = 0.0, dt: float = 0.05) -> None:
        carla = import_carla()
        if not hasattr(self, "_launch_gear"):
            self._launch_gear = cruise_gear(self.vehicle.get_physics_control(), speed)
        tf, v = self.vehicle.get_transform(), self.vehicle.get_velocity()
        steer = self.controller.step(VehicleState(t=float(t), x=tf.location.x, y=tf.location.y, yaw=tf.rotation.yaw,
                                                  speed=speed, vx=v.x, vy=v.y), dt).clamped().steer
        self.world.send(carla.command.ApplyVehicleControl(self.vehicle.id, carla.VehicleControl(
            throttle=float(throttle), steer=float(steer), manual_gear_shift=True, gear=int(self._launch_gear))))
        yaw = math.radians(tf.rotation.yaw)
        self.world.send(carla.command.ApplyTargetVelocity(
            self.vehicle.id, carla.Vector3D(x=math.cos(yaw) * speed, y=math.sin(yaw) * speed, z=0)))

    def set_sensor_start_frame(self, frame: int) -> None:
        if self.camera is not None:
            self.camera.set_minimum_frame(frame)
        if self.depth_camera is not None:
            self.depth_camera.set_minimum_frame(frame)

    def _submit_depth(self, item: dict) -> None:
        data = item.pop("data")
        item["source"] = "depth"
        future = self._depth_executor.submit(
            depth_observations_from_bgra,
            data, item["width"], item["height"], item["fov_deg"],
            self.depth_observation_spec,
        )
        self._depth_futures.append((item, future))

    def _drain_depth_futures(self, wait: bool = False) -> None:
        ready = []
        while self._depth_futures:
            item, future = self._depth_futures[0]
            if not wait and not future.done():
                break
            item["detections"] = future.result()
            self._depth_futures.popleft()
            ready.append(item)
        ready.sort(key=lambda record: (float(record["timestamp"]), int(record["frame"])))
        for item in ready:
            item["detections"] = self._depth_estimator.process(
                int(item["frame"]), float(item["timestamp"]), item["detections"]
            )
            self.logger.log_depth_observations(item)

    def step(self, t: float, frame: int, dt: float, recorded_timestamp: float = None) -> dict:
        timestamp = float(t) if recorded_timestamp is None else float(recorded_timestamp)
        self.receive_sensors(frame)
        self._receive_impacts(frame)
        record = self.state_record(timestamp, frame)
        speed = (record["velocity"]["x"] ** 2 + record["velocity"]["y"] ** 2 + record["velocity"]["z"] ** 2) ** 0.5
        state = VehicleState(t=t, x=record["x"], y=record["y"], yaw=record["yaw_deg"], speed=speed,
                             vx=record["velocity"]["x"], vy=record["velocity"]["y"])
        command = self.controller.step(state, dt)
        clamped = command.clamped()
        carla = import_carla()
        control = carla.VehicleControl(throttle=clamped.throttle, brake=clamped.brake, steer=clamped.steer,
                                       hand_brake=clamped.hand_brake, reverse=clamped.reverse)
        if clamped.neutral:
            control.manual_gear_shift, control.gear = True, 0
        self.world.send(carla.command.ApplyVehicleControl(self.vehicle.id, control))
        left, right = int(carla.VehicleLightState.LeftBlinker), int(carla.VehicleLightState.RightBlinker)
        self._update_indicator(t, left, right)
        if self.logger is not None:
            self.logger.log_state(record)
            self.logger.log_control({"frame": int(frame), "timestamp": timestamp, "throttle": command.throttle,
                                     "brake": command.brake, "steer": command.steer,
                                     "hand_brake": command.hand_brake, "reverse": command.reverse})
            light = int(self.vehicle.get_light_state())
            self.logger.log_lights({"frame": int(frame), "timestamp": timestamp, "light_state": light,
                                    "left_blinker": bool(light & left), "right_blinker": bool(light & right)})
        if self.camera is not None:
            for item in self.camera.drain_available():
                data = item.pop("data")
                item["source"] = "rgb"
                self.logger.log_camera(item, data)
        if self.depth_camera is not None:
            for item in self.depth_camera.drain_available():
                self._submit_depth(item)
            self._drain_depth_futures()
        return {"frame": int(frame), "timestamp": timestamp, "throttle": command.throttle, "brake": command.brake,
                "steer": command.steer, "hand_brake": command.hand_brake, "reverse": command.reverse}

    def receive_sensors(self, frame: int) -> None:
        if self._received_frame == int(frame):
            return
        self._received_frame = int(frame)
        for radar in self.radar:
            item = radar.poll(frame)
            if item is not None: self.logger.log_radar(item)

    def _receive_impacts(self, frame: int) -> None:
        for collision in self.collision_sensor.drain_vehicle():
            if self.logger is not None:
                self.logger.log_collision(collision)
            if self._first_impact_frame is None or int(collision["frame"]) < self._first_impact_frame:
                if not self.controller.impacted and int(collision["frame"]) + self.impact_reaction_ticks < int(frame):
                    self.late_impact_notifications += 1
                self._first_impact_frame = int(collision["frame"])
        if (self._first_impact_frame is not None and not self.controller.impacted
                and int(frame) >= self._first_impact_frame + self.impact_reaction_ticks):
            self.controller.notify_impact()

    def _update_indicator(self, t: float, left: int, right: int) -> None:
        side = self.controller.indicator(t)
        if side == getattr(self, "_indicator_side", 0):
            return
        carla = import_carla()
        value = int(self.vehicle.get_light_state()) & ~(left | right)
        value |= left if side < 0 else right if side > 0 else 0
        self.world.send(carla.command.SetVehicleLightState(self.vehicle.id, carla.VehicleLightState(value)))
        self._indicator_side = side

    def flush_sensor_queues(self, timeout_s: float = 2.0) -> None:
        if self.logger is None:
            return
        deadline = time.monotonic() + float(timeout_s)
        while time.monotonic() < deadline:
            drained = False
            if self.camera is not None:
                items = self.camera.drain_available()
                drained = drained or bool(items)
                for item in items:
                    data = item.pop("data")
                    item["source"] = "rgb"
                    self.logger.log_camera(item, data)
            if self.depth_camera is not None:
                items = self.depth_camera.drain_available()
                drained = drained or bool(items)
                for item in items:
                    self._submit_depth(item)
                self._drain_depth_futures()
            time.sleep(0.005)
        self._drain_depth_futures(wait=True)

    def ground_truth_collisions(self):
        return self.collision_sensor.drain_ground_truth()

    def close(self) -> None:
        if self._depth_executor is not None:
            self._depth_executor.shutdown(wait=True)
        if self.logger is None:
            return
        if self.camera is not None:
            self.logger.set_camera_stats(self.camera.stats)
        if self.depth_camera is not None:
            depth_stats = dict(self.depth_camera.stats)
            depth_stats["radial_velocity"] = self._depth_estimator.stats.as_dict()
            self.logger.set_depth_stats(depth_stats)
        for radar in self.radar:
            self.logger.set_radar_stats(radar.spec.sensor_id, radar.stats)
        self.logger.close()
