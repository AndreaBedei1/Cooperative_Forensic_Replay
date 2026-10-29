
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .alignment import align_graphs
from .anonymous import RoadUserFusion, align_by_observations, fuse_road_users
from .common_frame import (RECORDER_POSES_FILE, PoseSource, RecordedPoseSource, contact_check, footprint_gap,
                           is_recorded_stream,
                           recorder_pose_record)
from .config import ReconstructionConfig, load_config
from .fusion import associate_tracks, fuse_graphs, global_temporal_relations, global_trace
from .identity import radar_contact_evidence
from .local import LocalReconstruction, reconstruct_vehicle
from .models import Alignment, Association, GlobalGraph
from .render import (global_graph_dot, global_graph_markdown, local_graph_dot, local_graph_markdown,
                     render_svg, report_markdown, write_json, write_jsonl, write_text)


@dataclass
class RunReconstruction:
    run_dir: Path
    output_dir: Path
    locals: List[LocalReconstruction]
    alignment: Alignment
    associations: List[Association]
    graph: GlobalGraph
    trace: List[Dict[str, Any]]
    road_users: Optional[RoadUserFusion] = None

PoseFactory = Callable[[Path, float], PoseSource]


def measured_ego_records(vehicle_dir: Path, pose_factory: Optional[PoseFactory]) -> Optional[List[Dict[str, Any]]]:
    if pose_factory is None:
        return None
    vehicle_dir = Path(vehicle_dir)
    with (vehicle_dir / "ego.jsonl").open(encoding="utf-8") as handle:
        records = sorted((json.loads(line) for line in handle if line.strip()), key=lambda r: float(r["timestamp"]))
    origin = float(records[0]["timestamp"])
    source = pose_factory(vehicle_dir, origin)
    if type(source) is RecordedPoseSource:
        return None
    out = []
    for record in records:
        pose = source.pose_at(float(record["timestamp"]) - origin)
        row = dict(record, x=pose.x, y=pose.y, yaw_deg=math.degrees(pose.yaw))
        row["velocity"] = dict(record.get("velocity") or {}, x=pose.vx, y=pose.vy)
        out.append(row)
    return out


def run_title(run_dir: Path) -> str:
    return "{0}/{1}".format(run_dir.parent.name, run_dir.name)


def read_incident_context(run_dir: Path) -> Dict[str, Any]:
    path = Path(run_dir) / "incident_context.json"
    if not path.exists():
        return {}
    context = json.loads(path.read_text(encoding="utf-8"))
    limit = context.get("speed_limit_kmh")
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, (int, float)) or limit <= 0):
        raise ValueError("incident_context.json: speed_limit_kmh must be a positive number")
    road_map = context.get("map")
    if road_map is not None and (not isinstance(road_map, str) or not road_map.strip()):
        raise ValueError("incident_context.json: map must be the name of a road map")
    return context


def incident_map(run_dir: Path) -> Optional[str]:
    return read_incident_context(run_dir).get("map")


def _on_trace_grid(t_local: float, trace_hz: float) -> bool:
    return abs(t_local * trace_hz - round(t_local * trace_hz)) < 1e-3


def write_local_outputs(directory: Path, local: LocalReconstruction, trace_hz: float) -> None:
    write_jsonl(directory / "local_trace.jsonl", (frame.to_dict() for frame in local.trace))
    track_rows = []
    for track in local.tracks:
        for sample in track.samples:
            if _on_trace_grid(sample.t_local, trace_hz):
                track_rows.append(sample.to_dict(track.track_id))
    write_jsonl(directory / "local_tracks.jsonl", track_rows)
    write_json(directory / "local_graph.json", local.graph.to_dict())
    write_text(directory / "local_graph.md", local_graph_markdown(local.graph))
    write_text(directory / "local_graph.dot", local_graph_dot(local.graph))
    render_svg(directory / "local_graph.dot")


def body_separation(poses: Dict[str, PoseSource], footprints: Dict[str, Any], alignment: Alignment
                    ) -> Callable[[Tuple[str, ...], float, float], Optional[float]]:
    def separation(pair: Tuple[str, ...], t1: float, t2: float) -> Optional[float]:
        if len(pair) != 2 or any(name not in poses for name in pair):
            return None
        clocks = [alignment.graphs.get(name) for name in pair]
        if any(clock is None or clock.status != "ALIGNED" or clock.offset_to_global is None for clock in clocks):
            return None
        a, b = pair
        sigma = math.hypot(getattr(poses[a], "position_std_m", 0.0), getattr(poses[b], "position_std_m", 0.0))
        steps = max(1, int(math.ceil((t2 - t1) / 0.05)))
        worst = 0.0
        for k in range(steps + 1):
            t = t1 + (t2 - t1) * k / steps
            worst = max(worst, footprint_gap(poses[a].pose_at(t - clocks[0].offset_to_global), footprints.get(a),
                                             poses[b].pose_at(t - clocks[1].offset_to_global), footprints.get(b)))
        return max(0.0, worst - 3.0 * sigma)
    return separation


def fuse_recorders(run_dir: Path, locals_: List[LocalReconstruction], cfg: ReconstructionConfig,
                   pose_factory: Optional[PoseFactory] = None
                   ) -> Tuple[Alignment, List[Association], RoadUserFusion, GlobalGraph]:
    pose_factory = pose_factory or RecordedPoseSource.from_vehicle_dir
    poses = {local.owner: pose_factory(Path(run_dir) / "vehicles" / local.owner, local.clock_origin)
             for local in locals_}
    geometry = contact_check(poses, {local.owner: local.footprint for local in locals_},
                             cfg.fusion.contact_consistency_m)
    radar = radar_contact_evidence(locals_, cfg)

    def approach_check(a: str, ta: float, b: str, tb: float) -> Optional[bool]:
        return False if radar(a, ta, b, tb) is False else None

    alignment = align_graphs([local.graph for local in locals_], cfg.fusion, geometry, approach_check)
    for event in alignment.matched_events:
        event['evidence'].append("pre-contact radar view of each recorder checked against the candidate partner's own speed: not contradicted")
    associations = associate_tracks(locals_, alignment, cfg.fusion, cfg.tracking.radial_speed_std_mps)
    align_by_observations(locals_, alignment, associations, poses, cfg)
    if alignment.observed:
        associations = associate_tracks(locals_, alignment, cfg.fusion, cfg.tracking.radial_speed_std_mps)
    road_users = fuse_road_users(locals_, alignment, associations, poses, cfg)
    separation = body_separation(road_users.poses or poses, {local.owner: local.footprint for local in locals_}, alignment)
    return alignment, associations, road_users, fuse_graphs(
        locals_, alignment, associations, cfg.fusion.touching_clearance_m, separation=separation,
        recontact_max_pause_s=cfg.fusion.recontact_max_pause_s,
        recontact_max_separation_m=cfg.fusion.recontact_max_separation_m)


def reconstruct_run(run_dir: Path, cfg: Optional[ReconstructionConfig] = None,
                    pose_factory: Optional[PoseFactory] = None) -> RunReconstruction:
    run_dir = Path(run_dir)
    cfg = cfg or load_config()
    output_dir = run_dir / "reconstruction"
    for stale in (output_dir / "evaluation" / "evaluation.json", output_dir / "evaluation" / "evaluation.md"):
        if stale.exists():
            stale.unlink()

    context = read_incident_context(run_dir)
    vehicle_dirs = sorted(path for path in (run_dir / "vehicles").iterdir() if path.is_dir())
    locals_ = [reconstruct_vehicle(path, cfg, context=context, ego_records=measured_ego_records(path, pose_factory))
               for path in vehicle_dirs]
    for local in locals_:
        write_local_outputs(output_dir / local.owner, local, cfg.trace_hz)

    alignment, associations, road_users, graph = fuse_recorders(run_dir, locals_, cfg, pose_factory)
    trace = global_trace(graph)
    relations = global_temporal_relations(locals_, alignment, associations)

    title = run_title(run_dir)
    global_dir = output_dir / "global"
    write_json(global_dir / "alignment.json", alignment.to_dict())
    write_json(global_dir / "associations.json", [item.to_dict() for item in associations])
    road_user_record = road_users.to_dict(cfg, alignment)
    write_json(global_dir / "anonymous_entities.json", road_user_record)
    poses_path = global_dir / RECORDER_POSES_FILE
    if poses_path.exists():
        poses_path.unlink()
    if any(not is_recorded_stream(source) for source in road_users.poses.values()):
        origins = {local.owner: local.clock_origin for local in locals_}
        times = {}
        for owner, origin in origins.items():
            with (run_dir / "vehicles" / owner / "ego.jsonl").open(encoding="utf-8") as handle:
                times[owner] = sorted(float(json.loads(line)["timestamp"]) - origin for line in handle if line.strip())
        write_json(poses_path, recorder_pose_record(road_users.poses, origins, times))
    write_jsonl(global_dir / "global_trace.jsonl", trace)
    write_json(global_dir / "global_graph.json", dict(graph.to_dict(), run=title, incident_context=context or None,
                                                     temporal_safety_relations=relations,
                                                     reconstruction_config=cfg.to_dict()))
    write_text(global_dir / "global_graph.md",
               global_graph_markdown(title, graph, alignment, associations, trace, context, relations))
    write_text(global_dir / "global_graph.dot", global_graph_dot(title, graph))
    render_svg(global_dir / "global_graph.dot")
    write_text(output_dir / "report.md",
               report_markdown(title, locals_, alignment, associations, graph, trace, cfg.to_dict(), context,
                               relations, road_user_record))
    return RunReconstruction(run_dir=run_dir, output_dir=output_dir, locals=locals_, alignment=alignment,
                             associations=associations, graph=graph, trace=trace, road_users=road_users)
