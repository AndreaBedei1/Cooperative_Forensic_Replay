
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

import numpy as np

from .compact_observations import CompactObservationWriter
from ..perception.traffic_signs import SignDetector, SignTracker


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _without_privileged_ids(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _without_privileged_ids(v) for k, v in value.items()
                if k not in {"actor_id", "other_actor_id", "other_type_id"}}
    if isinstance(value, list):
        return [_without_privileged_ids(item) for item in value]
    return value


class _Jsonl:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.handle = path.open("w", encoding="utf-8")

    def write(self, record: Dict[str, Any]) -> None:
        self.handle.write(_json(record) + "\n")

    def close(self) -> None:
        self.handle.close()


class VehicleLogger:

    def __init__(self, root: Path, participant_id: str, metadata: Dict[str, Any]) -> None:
        self.root = Path(root) / "vehicles" / str(participant_id)
        self.root.mkdir(parents=True, exist_ok=True)
        self.state = _Jsonl(self.root / "ego.jsonl")
        self.controls = _Jsonl(self.root / "controls.jsonl")
        self.lights = _Jsonl(self.root / "lights.jsonl")
        self.collisions = _Jsonl(self.root / "collisions.jsonl")
        self.traffic_signs = _Jsonl(self.root / "traffic_signs.jsonl")
        (self.root / "camera").mkdir(parents=True, exist_ok=True)
        (self.root / "metadata.json").write_text(_json(_without_privileged_ids(metadata)), encoding="utf-8")
        self._radar_writers: Dict[str, CompactObservationWriter] = {}
        radar_entries = list(metadata.get("radar", []) or [])
        radar_root = self.root / "radar"
        for radar in radar_entries:
            sensor_id = str(radar.get("sensor_id", "front"))
            if sensor_id in self._radar_writers:
                raise ValueError("radar sensor IDs must be unique: {0}".format(sensor_id))
            location = radar_root if len(radar_entries) == 1 else radar_root / sensor_id
            self._radar_writers[sensor_id] = CompactObservationWriter(
                location / "observations.npz",
                {
                    "source": "radar",
                    "sensor_id": sensor_id,
                    "schema_version": 1,
                    "columns": ["depth_m", "azimuth_rad", "altitude_rad", "radial_velocity_mps"],
                    "sensor_transform": dict(radar.get("sensor_transform") or {
                        "x": float(radar.get("mount_x", 0.0)), "y": float(radar.get("mount_y", 0.0)),
                        "z": float(radar.get("mount_z", 0.0)), "yaw_deg": float(radar.get("mount_yaw_deg", 0.0)),
                        "pitch_deg": float(radar.get("mount_pitch_deg", 0.0))}),
                    "mount": {"anchor": radar.get("anchor"), "gap_m": radar.get("gap_m")},
                    "sensor_tick_s": float(radar.get("sensor_tick_s", 0.05)),
                    "horizontal_fov_deg": float(radar.get("horizontal_fov_deg", 150.0)),
                    "vertical_fov_deg": float(radar.get("vertical_fov_deg", 20.0)),
                    "range_m": float(radar.get("range_m", 90.0)),
                    "points_per_second": int(radar.get("points_per_second", 0)),
                    "frame": "azimuth and altitude in this radar's own frame; returns beyond range_m (radial) "
                             "dropped",
                    "radial_velocity_status": "measured",
                    "radial_velocity_sign": "positive_away_from_sensor",
                    "radial_velocity_definition": "carla_range_rate",
                },
            )
        self._camera_metadata = {
            "source": "rgb",
            "sensor_id": (metadata.get("camera") or {}).get("sensor_id"),
            "schema_version": 1,
            "width": (metadata.get("camera") or {}).get("width"),
            "height": (metadata.get("camera") or {}).get("height"),
            "fov_deg": (metadata.get("camera") or {}).get("fov_deg"),
            "sensor_tick_s": (metadata.get("camera") or {}).get("sensor_tick_s"),
            "processing": "transient_bgra_to_rgb",
            "images_persisted": False,
        }
        (self.root / "camera" / "metadata.json").write_text(_json(self._camera_metadata), encoding="utf-8")
        sign_cfg = dict(metadata.get("traffic_signs") or {})
        sign_cfg.setdefault("camera_fov_deg", (metadata.get("camera") or {}).get("fov_deg", 110.0))
        self._sign_detector = SignDetector(sign_cfg)
        self._sign_tracker = SignTracker(sign_cfg)
        self._camera_width = int((metadata.get("camera") or {}).get("width") or 0)
        self._depth_writer = None
        if metadata.get("depth_camera") is not None:
            depth = metadata.get("depth_camera") or {}
            depth_spec = metadata.get("depth_observations") or {}
            depth_velocity = metadata.get("depth_radial_velocity") or {}
            self._depth_writer = CompactObservationWriter(
                self.root / "depth" / "observations.npz",
                {
                    "source": "depth",
                    "sensor_id": depth.get("sensor_id"),
                    "schema_version": 1,
                    "columns": ["depth_m", "azimuth_rad", "altitude_rad", "radial_velocity_mps"],
                    "sensor_transform": {
                        "x": depth.get("mount_x"), "y": depth.get("mount_y"), "z": depth.get("mount_z"),
                        "yaw_deg": depth.get("mount_yaw_deg"), "pitch_deg": depth.get("mount_pitch_deg"),
                        "roll_deg": depth.get("mount_roll_deg"),
                    },
                    "sensor_tick_s": depth.get("sensor_tick_s"),
                    "horizontal_fov_deg": depth.get("fov_deg"),
                    "vertical_observation_fov_deg": depth_spec.get("vertical_fov_deg"),
                    "observation_horizontal_fov_deg": depth_spec.get("horizontal_fov_deg"),
                    "max_range_m": depth_spec.get("max_range_m"),
                    "azimuth_bin_deg": depth_spec.get("azimuth_bin_deg"),
                    "altitude_bin_deg": depth_spec.get("altitude_bin_deg"),
                    "radial_velocity_status": "temporally_estimated" if depth_velocity.get("enabled", True) else "disabled",
                    "radial_velocity_method": "temporal_geometric_association_v1",
                    "radial_velocity_sign": "positive_towards_sensor",
                    "radial_velocity_definition": "closing_speed",
                    "uses_ground_truth": False,
                    "uses_radar_for_estimation": False,
                    "association": depth_velocity,
                },
            )
        self._camera_stats: Dict[str, Any] = {}
        self._depth_stats: Dict[str, Any] = {}
        self._radar_stats: Dict[str, Mapping[str, Any]] = {}
        self._closed = False

    def log_state(self, record: Dict[str, Any]) -> None: self.state.write(_without_privileged_ids(record))
    def log_control(self, record: Dict[str, Any]) -> None: self.controls.write(_without_privileged_ids(record))

    def log_lights(self, record: Dict[str, Any]) -> None: self.lights.write(_without_privileged_ids(record))
    def log_collision(self, record: Dict[str, Any]) -> None:
        self.collisions.write(_without_privileged_ids(record))
    def log_radar(self, record: Dict[str, Any]) -> None:
        sensor_id = str(record.get("sensor_id", "front"))
        writer = self._radar_writers.get(sensor_id)
        if writer is None:
            raise KeyError("unknown radar sensor ID: {0}".format(sensor_id))
        writer.append(record["frame"], record["timestamp"], record.get("detections", []))
    def log_camera(self, record: Dict[str, Any], data: bytes) -> None:
        width, height = int(record["width"]), int(record["height"])
        bgra = np.frombuffer(data, dtype=np.uint8).reshape((height, width, 4))
        rgb = bgra[..., [2, 1, 0]]
        frame = int(record["frame"]); timestamp = float(record["timestamp"])
        found = self._sign_detector.detect(rgb, frame=frame, t=timestamp)
        self._sign_tracker.update(found)
        self._camera_width = width
        del rgb, bgra

    def log_depth_observations(self, record: Dict[str, Any]) -> None:
        if self._depth_writer is None:
            raise RuntimeError("depth observations supplied without an enabled depth camera")
        self._depth_writer.append(record["frame"], record["timestamp"], record.get("detections", []))

    def set_camera_stats(self, stats: Mapping[str, Any]) -> None:
        self._camera_stats = dict(stats)

    def set_depth_stats(self, stats: Mapping[str, Any]) -> None:
        self._depth_stats = dict(stats)

    def set_radar_stats(self, sensor_id: str, stats: Mapping[str, Any]) -> None:
        self._radar_stats[str(sensor_id)] = dict(stats)

    def close(self) -> None:
        if self._closed:
            return
        for track in self._sign_tracker.tracks(confirmed_only=True):
            relevance = track.relevance(self._camera_width)
            self.traffic_signs.write({
                "sign_track_id": track.track_id,
                "sensor_id": self._camera_metadata.get("sensor_id"),
                "class": track.sign_class,
                "frame_first": track.detections[0].frame,
                "timestamp_first": round(track.t_first, 4),
                "frame_confirmed": track.detections[self._sign_tracker.min_detections - 1].frame,
                "timestamp_confirmed": round(track.detections[self._sign_tracker.min_detections - 1].t, 4),
                "frame_last": track.detections[-1].frame,
                "timestamp_last": round(track.t_last, 4),
                "n_detections": len(track.detections),
                "best_confidence": round(track.best.confidence, 4),
                "best_bbox": list(track.best.bbox),
                "relevant_to_ego_path": relevance["relevant_to_ego_path"],
                "centredness": relevance["centredness"],
                "growing": relevance["growing"],
                "min_bearing_deg": relevance["min_bearing_deg"],
            })
        self._camera_stats.update({
            "candidate_sign_detections": self._sign_tracker.n_detections,
            "candidate_stop_detections": sum(len(t.detections) for t in self._sign_tracker.tracks(False) if t.sign_class == "STOP"),
            "candidate_yield_detections": sum(len(t.detections) for t in self._sign_tracker.tracks(False) if t.sign_class == "YIELD"),
            "confirmed_sign_tracks": len(self._sign_tracker.tracks(True)),
            "rejected_short_tracks": self._sign_tracker.rejected_short_tracks,
            "confirmed_stop_tracks": sum(t.sign_class == "STOP" for t in self._sign_tracker.tracks(True)),
            "confirmed_yield_tracks": sum(t.sign_class == "YIELD" for t in self._sign_tracker.tracks(True)),
            "rgb_images_persisted": False,
        })
        for stream in (self.state, self.controls, self.lights, self.collisions, self.traffic_signs):
            stream.close()
        if self._depth_writer is not None:
            self._depth_writer.close(self._depth_stats)
        for sensor_id, writer in self._radar_writers.items():
            writer.close(self._radar_stats.get(sensor_id, {}))
        self._camera_metadata.update(self._camera_stats)
        (self.root / "camera" / "metadata.json").write_text(_json(self._camera_metadata), encoding="utf-8")
        self._closed = True
