
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .common_frame import (DEFAULT_BODY, CommonSample, CommonTrack, PoseSource, RecorderBody, WorldPose,
                           common_track, entry_distances, outline_distances)
from .config import ReconstructionConfig
from .tracking import _transition, kf_predict, kf_update
from .models import Alignment, Association, GraphClock

ASSOCIATED = "ASSOCIATED"
ANONYMOUS = "ANONYMOUS"
OBSERVED = "observed_trajectories"
REFERENCE = "reference_recorder"
CROSS, SPLIT, STITCH = "cross_observer", "same_observer", "stitch"


def chi2_2dof(probability: float) -> float:
    return -2.0 * math.log(1.0 - probability)



def _faces(heading: float) -> List[Tuple[np.ndarray, np.ndarray, int]]:
    f = np.array([math.cos(heading), math.sin(heading)])
    r = np.array([-math.sin(heading), math.cos(heading)])
    return [(f, r, 0), (-f, r, 0), (r, f, 1), (-r, f, 1)]


@dataclass
class FaceMeasurement:
    normal: np.ndarray
    tangent: np.ndarray
    half: int
    offset: float
    along: float
    extent: float
    count: int
    observer: str
    pose_var: float


def _initial_centre(sample: CommonSample, heading: Optional[float], halves: Tuple[float, float]) -> np.ndarray:
    line = sample.line_of_sight
    if heading is None:
        return sample.near + line * 0.5 * (halves[0] + halves[1])
    along = abs(line[0] * math.cos(heading) + line[1] * math.sin(heading))
    across = abs(-line[0] * math.sin(heading) + line[1] * math.cos(heading))
    depth = min(halves[0] / along if along > 1e-6 else math.inf, halves[1] / across if across > 1e-6 else math.inf)
    if not math.isfinite(depth):
        depth = 0.5 * (halves[0] + halves[1])
    return sample.near + line * depth


def face_measurements(sample: CommonSample, observer: str, heading: float, centre: np.ndarray,
                      halves: Tuple[float, float], min_returns: int = 3) -> List[FaceMeasurement]:
    faces = _faces(heading)
    if sample.returns is not None and sample.origins is not None and len(sample.returns) >= min_returns:
        points, origins = sample.returns, sample.origins
    else:
        points, origins = sample.near[None, :], sample.observer[None, :]
        min_returns = 1
    lines = points - origins
    lines = lines / np.maximum(np.hypot(lines[:, 0], lines[:, 1]), 1e-6)[:, None]
    best = np.full(len(points), -1)
    best_distance = np.full(len(points), np.inf)
    for index, (normal, _, half) in enumerate(faces):
        visible = (lines @ normal) < 0.0
        distance = np.abs((points - centre) @ normal - halves[half])
        better = visible & (distance < best_distance)
        best[better], best_distance[better] = index, distance[better]
    out = []
    for index, (normal, tangent, half) in enumerate(faces):
        chosen = best == index
        if int(chosen.sum()) >= min_returns:
            along = points[chosen] @ tangent
            extent = float(np.percentile(along, 95) - np.percentile(along, 5)) if len(along) >= 5 else 0.0
            out.append(FaceMeasurement(normal, tangent, half, float(np.median(points[chosen] @ normal)),
                                       float(np.median(along)), extent, int(chosen.sum()), observer,
                                       sample.pose_var))
    return out


@dataclass
class BoxFit:
    centre: np.ndarray
    halves: Tuple[float, float]
    covariance: np.ndarray
    chi2: float
    faces: int
    observers: int
    measurements: List[FaceMeasurement] = field(default_factory=list, repr=False)


def solve_box(measurements: Sequence[FaceMeasurement], cfg: ReconstructionConfig) -> BoxFit:
    fusion, semantics = cfg.fusion, cfg.semantics
    prior = (semantics.target_length_m / 2.0, semantics.target_width_m / 2.0)
    prior_std = (fusion.box_length_std_m / 2.0, fusion.box_width_std_m / 2.0)
    rows, values, sigmas = [], [], []
    for m in measurements:
        rows.append([m.normal[0], m.normal[1], 1.0 if m.half == 0 else 0.0, 1.0 if m.half == 1 else 0.0])
        values.append(m.offset)
        sigmas.append(math.sqrt(fusion.box_face_std_m ** 2 + m.pose_var))
        rows.append([m.tangent[0], m.tangent[1], 0.0, 0.0])
        values.append(m.along)
        sigmas.append(math.sqrt((prior[1 - m.half] / math.sqrt(3.0)) ** 2 + m.pose_var))
    rows += [[0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    values += [prior[0], prior[1]]
    sigmas += [prior_std[0], prior_std[1]]
    A, b, w = np.array(rows), np.array(values), 1.0 / np.array(sigmas)
    Aw = A * w[:, None]
    theta = np.linalg.lstsq(Aw, b * w, rcond=None)[0]
    residual = (A @ theta - b) * w
    covariance = np.linalg.pinv(Aw.T @ Aw)
    faces = {(round(float(m.normal[0]), 6), round(float(m.normal[1]), 6)) for m in measurements}
    return BoxFit(theta[:2], (float(theta[2]), float(theta[3])), covariance, float(residual @ residual),
                  len(faces), len({m.observer for m in measurements}), list(measurements))


def fit_box(observations: Sequence[Tuple[str, CommonSample]], heading: float, cfg: ReconstructionConfig,
            start: Optional[np.ndarray] = None, iterations: int = 3) -> BoxFit:
    prior = (cfg.semantics.target_length_m / 2.0, cfg.semantics.target_width_m / 2.0)
    centre = start if start is not None else np.mean(
        [_initial_centre(sample, heading, prior) for _, sample in observations], axis=0)
    halves = prior
    fit = None
    for _ in range(iterations):
        measurements = [m for observer, sample in observations
                        for m in face_measurements(sample, observer, heading, centre, halves)]
        if not measurements:
            break
        fit = solve_box(measurements, cfg)
        centre, halves = fit.centre, fit.halves
    if fit is None:
        raise ValueError("no face measurement")
    return fit



def covariance_intersection(estimates: Sequence[Tuple[np.ndarray, np.ndarray]]) -> Tuple[np.ndarray, np.ndarray]:
    mean, cov = np.asarray(estimates[0][0], float), np.asarray(estimates[0][1], float)
    for other_mean, other_cov in estimates[1:]:
        inv_a, inv_b = np.linalg.pinv(cov), np.linalg.pinv(np.asarray(other_cov, float))
        other = np.asarray(other_mean, float)

        def fused(omega: float, inv_a: np.ndarray = inv_a, inv_b: np.ndarray = inv_b,
                  mean: np.ndarray = mean, other: np.ndarray = other) -> Tuple[np.ndarray, np.ndarray]:
            fused_cov = np.linalg.pinv(omega * inv_a + (1.0 - omega) * inv_b)
            return fused_cov @ (omega * inv_a @ mean + (1.0 - omega) * inv_b @ other), fused_cov

        lo, hi = 0.0, 1.0
        golden = (math.sqrt(5.0) - 1.0) / 2.0
        for _ in range(40):
            a, b = hi - golden * (hi - lo), lo + golden * (hi - lo)
            if np.trace(fused(a)[1]) < np.trace(fused(b)[1]):
                hi = b
            else:
                lo = a
        mean, cov = fused((lo + hi) / 2.0)
    return mean, cov



@dataclass
class CommonView:

    tracks: List[CommonTrack]
    bodies: Dict[str, RecorderBody]


def build_common_view(locals_: Sequence[Any], alignment: Alignment, associations: Sequence[Association],
                      poses: Dict[str, PoseSource]) -> CommonView:
    status = {(a.local_graph, a.local_track): a for a in associations}
    tracks, bodies = [], {}
    for local in sorted(locals_, key=lambda item: item.owner):
        clock = alignment.graphs.get(local.owner)
        if clock is None or clock.status != "ALIGNED" or clock.offset_to_global is None:
            continue
        partners = {event["nodes"][local.owner]: tuple(sorted(g for g in event["graphs"] if g != local.owner))
                    for event in alignment.matched_events if local.owner in event["nodes"]}
        contacts = tuple(sorted((round(node.t_local + clock.offset_to_global, 4), partners.get(node.node_id, ()))
                                for node in local.graph.nodes if node.event_type == "COLLISION"))
        bodies[local.owner] = RecorderBody(local.owner, poses[local.owner], local.footprint, clock.offset_to_global,
                                           contacts)
        for track in local.tracks:
            item = status.get((local.owner, track.track_id))
            linked = item is not None and item.status == ASSOCIATED
            tracks.append(common_track(track, local.owner, local.ego, poses[local.owner], local.footprint,
                                       clock.offset_to_global, ASSOCIATED if linked else ANONYMOUS,
                                       item.global_entity if linked else None))
            tracks[-1].own_impact = contacts[0][0] if contacts else None
    return CommonView(tracks, bodies)


def _position_sigma(cfg: ReconstructionConfig, sample: CommonSample, body_source: Optional[PoseSource] = None) -> float:
    other = body_source.position_std_m ** 2 if body_source is not None else 0.0
    return math.sqrt(cfg.tracking.measurement_std_m ** 2 + sample.pose_var + other)


def _velocity_sigma(cfg: ReconstructionConfig, *stds: float) -> float:
    floor = cfg.tracking.radial_speed_std_mps
    return math.sqrt(sum(max(std, floor) ** 2 for std in stds))



def _moving(track: CommonTrack, cfg: ReconstructionConfig) -> List[CommonSample]:
    return [s for s in track.samples if s.measured and s.speed >= cfg.fusion.observed_alignment_min_speed_mps]


def _components(mask: np.ndarray) -> List[Tuple[int, int]]:
    runs, start = [], None
    for index, value in enumerate(mask):
        if value and start is None:
            start = index
        if not value and start is not None:
            runs.append((start, index - 1))
            start = None
    if start is not None:
        runs.append((start, len(mask) - 1))
    return runs


def align_by_observations(locals_: Sequence[Any], alignment: Alignment, associations: Sequence[Association],
                          poses: Dict[str, PoseSource], cfg: ReconstructionConfig) -> List[Dict[str, Any]]:
    fusion = cfg.fusion
    by_owner = {local.owner: local for local in locals_}
    decisions: List[Dict[str, Any]] = []
    if alignment.graphs and not any(clock.status == "ALIGNED" for clock in alignment.graphs.values()):
        reference = sorted(alignment.graphs)[0]
        alignment.graphs[reference] = GraphClock(
            graph=reference, status="ALIGNED", offset_to_global=0.0, method=REFERENCE,
            reason="no matched collision: its own clock defines t_global (t_global = its t_local)")
        decisions.append({"recorder": reference, "method": REFERENCE, "accepted": True, "offset_to_global": 0.0,
                          "reason": "no matched collision: the first recorder's clock is the global one"})
    pending = sorted(owner for owner, clock in alignment.graphs.items() if clock.status != "ALIGNED")
    progress = True
    while pending and progress:
        progress = False
        view = build_common_view(locals_, alignment, associations, poses)
        if not view.bodies:
            break
        for recorder in list(pending):
            local, source = by_owner[recorder], poses[recorder]
            comparisons = []
            for track in view.tracks:
                if track.status == ASSOCIATED:
                    continue
                samples = _moving(track, cfg)
                if len(samples) >= fusion.observed_alignment_min_samples:
                    comparisons.append((track.name, source, local.footprint, np.array([s.t_global for s in samples]),
                                        -1.0, 0.0, np.array([s.near for s in samples]),
                                        np.array([s.observer for s in samples]),
                                        np.array([_position_sigma(cfg, s, source) for s in samples])))
            for track in local.tracks:
                own = common_track(track, recorder, local.ego, source, local.footprint, 0.0)
                samples = _moving(own, cfg)
                if len(samples) < fusion.observed_alignment_min_samples:
                    continue
                for body in view.bodies.values():
                    comparisons.append(("{0} on {1}".format(own.name, body.recorder), body.poses, body.footprint,
                                        np.array([s.t_local for s in samples]), 1.0, body.offset_to_global,
                                        np.array([s.near for s in samples]), np.array([s.observer for s in samples]),
                                        np.array([_position_sigma(cfg, s, body.poses) for s in samples])))
            lows = [body.poses.start + body.offset_to_global - source.end for body in view.bodies.values()]
            highs = [body.poses.end + body.offset_to_global - source.start for body in view.bodies.values()]
            grid = np.arange(min(lows), max(highs) + 1e-9, fusion.observed_alignment_step_s)
            curves: Dict[str, List[Optional[np.ndarray]]] = {}
            for name, outline, footprint, times, sign, offset, near, observers, sigma in comparisons:
                need = max(fusion.observed_alignment_min_samples, 0.5 * len(times))
                row: List[Optional[np.ndarray]] = []
                for delta in grid:
                    distance, valid = entry_distances(outline, footprint, times + sign * delta - offset, near,
                                                      observers)
                    row.append((distance / sigma)[valid] if valid.sum() >= need else None)
                if any(values is not None and float(np.median(values)) <= 2.0 for values in row):
                    curves[name] = row
            decision: Dict[str, Any] = {"recorder": recorder, "method": OBSERVED, "accepted": False,
                                        "comparisons": len(comparisons), "pooled": sorted(curves)}
            scores = np.full(len(grid), np.inf)
            for k in range(len(grid)):
                pooled = [row[k] for row in curves.values() if row[k] is not None]
                if pooled and sum(len(values) for values in pooled) >= fusion.observed_alignment_min_samples:
                    scores[k] = float(np.median(np.concatenate(pooled)))
            if not np.isfinite(scores).any():
                decision["reason"] = "no observation of a moving target lies where its line of sight enters a body"
                decisions.append(decision)
                pending.remove(recorder)
                continue
            k, threshold, home, others = offset_decision(scores, fusion.observed_alignment_uniqueness_ratio)
            decision.update(offset_to_global=round(float(grid[k]), 4) + 0.0, median_distance_sigma=round(float(scores[k]), 3),
                            interval=[round(float(grid[home[0]]), 4) + 0.0, round(float(grid[home[1]]), 4) + 0.0],
                            other_intervals=len(others),
                            best_elsewhere_sigma=round(min(others), 3) if others else None,
                            candidates=len(grid))
            if scores[k] <= 2.0 and not others:
                decision["accepted"] = True
                alignment.graphs[recorder] = GraphClock(
                    graph=recorder, status="ALIGNED", offset_to_global=round(float(grid[k]), 4) + 0.0, method=OBSERVED,
                    reason="aligned through observed trajectories: the near surfaces of {0} lie where their lines of "
                           "sight enter the body (pooled median {1:.2f} sigma) at this offset; offsets within {2:.2f} "
                           "sigma span [{3:+.2f}, {4:+.2f}] s and nothing else fits".format(
                               ", ".join(sorted(curves)), scores[k], threshold, grid[home[0]], grid[home[1]]))
                progress = True
            else:
                decision["reason"] = ("median beyond 2 sigma" if scores[k] > 2.0 else
                                      "not unique: {0} other offset interval(s) fit (best {1:.2f} sigma): the observed "
                                      "target barely moves or moves along its own outline".format(len(others), min(others)))
            decisions.append(decision)
            pending.remove(recorder)
            if progress:
                break
    alignment.observed = decisions
    return [decision for decision in decisions if decision["method"] == OBSERVED]


def offset_decision(scores: np.ndarray, uniqueness_ratio: float) -> Tuple[int, float, Tuple[int, int], List[float]]:
    k = int(np.argmin(scores))
    threshold = max(uniqueness_ratio * float(scores[k]), 2.0)
    intervals = _components(scores <= threshold)
    home = next(run for run in intervals if run[0] <= k <= run[1])
    others = [float(np.min(scores[a:b + 1])) for a, b in intervals if (a, b) != home]
    return k, threshold, home, others



@dataclass
class RecorderLink:
    track: str
    recorder: str
    samples: int
    median_distance_m: float
    median_distance_sigma: float
    median_velocity_difference_mps: float
    fraction_within: float
    accepted: bool
    until: Optional[float] = None
    refused: Optional[str] = None
    reacquired: bool = False
    collision_anchored: bool = False


def _third_body_contact(observer: RecorderBody, target: RecorderBody) -> float:
    return min((t for t, partners in target.contacts if observer.recorder not in partners), default=math.inf)



@dataclass
class PairEvidence:
    a: str
    b: str
    kind: str
    compared: int
    passed: float
    median_box_chi2: Optional[float]
    median_velocity_chi2: Optional[float]
    centre_gap_m: Optional[float]
    gap_s: Optional[float] = None
    accepted: bool = False
    refused: Optional[str] = None
    lateral_chi2: Optional[float] = None

    @property
    def score(self) -> float:
        box = self.median_box_chi2 if self.median_box_chi2 is not None else math.inf
        return box + (self.median_velocity_chi2 or 0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {"a": self.a, "b": self.b, "kind": self.kind, "compared": self.compared, "passed": self.passed,
                "median_box_chi2": self.median_box_chi2, "median_velocity_chi2": self.median_velocity_chi2,
                "centre_gap_m": self.centre_gap_m, "gap_s": self.gap_s, "accepted": self.accepted,
                "refused": self.refused, "lateral_chi2": self.lateral_chi2}


def _heading(samples: Sequence[CommonSample], cfg: ReconstructionConfig) -> Optional[float]:
    floor = cfg.tracking.radial_speed_std_mps
    weights = [1.0 / max(s.vel_std, floor) ** 2 for s in samples]
    v = sum(w * s.velocity for w, s in zip(weights, samples)) / sum(weights)
    speed = float(np.hypot(*v))
    spread = math.sqrt(1.0 / sum(weights))
    return math.atan2(v[1], v[0]) if speed >= max(3.0 * spread, 1.0) else None


def _after_impact(track: CommonTrack, sample: CommonSample) -> bool:
    impact = getattr(track, "own_impact", None)
    return impact is not None and sample.t_global >= impact - 1e-6


def pair_evidence(a: CommonTrack, b: CommonTrack, cfg: ReconstructionConfig) -> Optional[PairEvidence]:
    fusion, semantics = cfg.fusion, cfg.semantics
    if a.identity_ambiguous or b.identity_ambiguous:
        return None
    gate = chi2_2dof(fusion.anonymous_gate_probability)
    if min(a.end, b.end) < max(a.start, b.start):
        return None
    diagonal = math.hypot(semantics.target_length_m + fusion.box_length_std_m * 3.0,
                          semantics.target_width_m + fusion.box_width_std_m * 3.0)
    box, velocity, gaps, passed = [], [], [], []
    for sa in a.samples:
        if not sa.measured:
            continue
        sb = b.state_at(sa.t_global)
        if sb is None or not sb.measured:
            continue
        heading = _heading([sa, sb], cfg)
        if heading is None:
            continue
        reach = diagonal + 6.0 * math.hypot(_position_sigma(cfg, sa), _position_sigma(cfg, sb))
        dv = sa.velocity - sb.velocity
        d_vel = float(dv @ dv) / _velocity_sigma(cfg, sa.vel_std, sb.vel_std) ** 2
        if _after_impact(a, sa) or _after_impact(b, sb):
            d_vel = 0.0
        if float(np.hypot(*(sa.near - sb.near))) > reach:
            box.append(math.inf)
            velocity.append(d_vel)
            passed.append(False)
            continue
        try:
            fa = fit_box([(a.recorder, sa)], heading, cfg)
            fb = fit_box([(b.recorder, sb)], heading, cfg)
            joint = fit_box([(a.recorder, sa), (b.recorder, sb)], heading, cfg, start=(fa.centre + fb.centre) / 2.0)
        except (ValueError, np.linalg.LinAlgError):
            continue
        d_box = max(joint.chi2 - fa.chi2 - fb.chi2, 0.0)
        box.append(d_box)
        velocity.append(d_vel)
        gaps.append(float(np.hypot(*(fa.centre - fb.centre))))
        passed.append(d_box <= gate and d_vel <= gate)
    if not box:
        return None
    median_box = float(np.median(box))
    evidence = PairEvidence(a.name, b.name, CROSS if a.recorder != b.recorder else SPLIT, len(box),
                            round(float(np.mean(passed)), 3),
                            round(median_box, 3) if math.isfinite(median_box) else None,
                            round(float(np.median(velocity)), 3), round(float(np.median(gaps)), 3) if gaps else None)
    evidence.accepted = (evidence.compared >= fusion.anonymous_min_shared_samples
                         and evidence.passed >= fusion.anonymous_pass_fraction)
    return evidence


def _centre_estimate(observer: str, sample: CommonSample, heading: Optional[float],
                     cfg: ReconstructionConfig) -> Tuple[np.ndarray, np.ndarray]:
    prior = (cfg.semantics.target_length_m / 2.0, cfg.semantics.target_width_m / 2.0)
    if heading is not None:
        try:
            fit = fit_box([(observer, sample)], heading, cfg)
            return fit.centre, fit.covariance[:2, :2]
        except (ValueError, np.linalg.LinAlgError):
            pass
    return _initial_centre(sample, None, prior), np.eye(2) * (prior[0] ** 2 + sample.pose_var)


def stitch_evidence(a: CommonTrack, b: CommonTrack, cfg: ReconstructionConfig) -> Optional[PairEvidence]:
    fusion = cfg.fusion
    if a.recorder != b.recorder:
        return None
    if (a.identity_ambiguous or b.identity_ambiguous
            or a.parent_track is not None or b.parent_track is not None):
        return None
    last = next((s for s in reversed(a.samples) if s.measured), None)
    first = next((s for s in b.samples if s.measured), None)
    if last is None or first is None:
        return None
    gap = first.t_global - last.t_global
    if b.start <= a.end or gap <= 0.0 or gap > fusion.stitch_max_gap_s + 1e-9:
        return None
    ca, pa = _centre_estimate(a.recorder, last, _heading([last], cfg), cfg)
    cb, pb = _centre_estimate(b.recorder, first, _heading([first], cfg), cfg)
    sigma_a = cfg.tracking.acceleration_std_mps2
    predicted = ca + last.velocity * gap
    covariance = pa + pb + np.eye(2) * ((sigma_a * gap ** 2 / 2.0) ** 2 + (last.vel_std * gap) ** 2)
    miss = cb - predicted
    d_pos = float(miss @ np.linalg.solve(covariance, miss))
    heading = _heading([last, first], cfg)
    lateral_chi2 = 0.0
    if heading is not None:
        normal = np.array([-math.sin(heading), math.cos(heading)])
        lateral_cov = pa + pb + np.eye(2) * (last.vel_std * gap) ** 2
        lateral_chi2 = float(normal @ miss) ** 2 / max(float(normal @ lateral_cov @ normal), 1e-9)
    dv = first.velocity - last.velocity
    d_vel = float(dv @ dv) / (_velocity_sigma(cfg, first.vel_std, last.vel_std) ** 2 + (sigma_a * gap) ** 2)
    gate = chi2_2dof(fusion.anonymous_gate_probability)
    ok = d_pos <= gate and d_vel <= gate and lateral_chi2 <= gate
    return PairEvidence(a.name, b.name, STITCH, 1, 1.0 if ok else 0.0, round(d_pos, 3), round(d_vel, 3),
                        round(float(np.hypot(*miss)), 3), round(gap, 3), accepted=ok,
                        lateral_chi2=round(lateral_chi2,3))


def _overlap(a: CommonTrack, b: CommonTrack) -> bool:
    return min(a.end, b.end) - max(a.start, b.start) > 1e-6


def _dominates(a: "RecorderLink", b: "RecorderLink") -> bool:
    return a.median_distance_sigma < b.median_distance_sigma and a.fraction_within >= b.fraction_within


def on_recorder_together(a: CommonTrack, b: CommonTrack, body: Optional[RecorderBody],
                         cfg: ReconstructionConfig) -> bool:
    if body is None:
        return False
    times, pa, pb, sa, sb = [], [], [], [], []
    for x in a.samples:
        if not x.measured or not body.covers(x.t_global):
            continue
        y = b.state_at(x.t_global)
        if y is None or not y.measured:
            continue
        times.append(x.t_global - body.offset_to_global)
        pa.append(x.point)
        pb.append(y.point)
        sa.append(_position_sigma(cfg, x, body.poses))
        sb.append(_position_sigma(cfg, y, body.poses))
    if len(times) < cfg.fusion.link_min_samples:
        return False
    da, _ = outline_distances(body.poses, body.footprint, times, np.array(pa), inside_zero=True)
    db, _ = outline_distances(body.poses, body.footprint, times, np.array(pb), inside_zero=True)
    sa, sb = np.array(sa), np.array(sb)
    passed = (da <= 3.0 * sa) & (db <= 3.0 * sb) & (3.0 * np.maximum(sa, sb) <= cfg.semantics.target_width_m)
    return float(np.mean(passed)) >= cfg.fusion.link_min_fraction


def exclusive_recorder_links(view: CommonView, links: Sequence["RecorderLink"], cfg: ReconstructionConfig,
                             same_body: Optional[Callable[[CommonTrack, CommonTrack, str], bool]] = None
                             ) -> Tuple[List["RecorderLink"], List[Dict[str, Any]]]:
    if same_body is None:
        def same_body(a: CommonTrack, b: CommonTrack, recorder: str) -> bool:
            item = pair_evidence(a, b, cfg)
            if item is not None and item.accepted and item.kind == SPLIT:
                return True
            return on_recorder_together(a, b, view.bodies.get(recorder), cfg)
    by_name = {t.name: t for t in view.tracks}
    claims: List[Tuple[str, str, Optional[RecorderLink]]] = [
        (t.name, t.entity, None) for t in view.tracks if t.status == ASSOCIATED and t.entity is not None]
    claims += [(link.track, link.recorder, link) for link in links]
    refused: Dict[str, Tuple[str, str]] = {}
    for i, (a, ra, la) in enumerate(claims):
        for b, rb, lb in claims[i + 1:]:
            if a == b or ra != rb or a.split(":", 1)[0] != b.split(":", 1)[0]:
                continue
            if la is None and lb is None:
                continue
            ta, tb = by_name.get(a), by_name.get(b)
            if ta is None or tb is None or not _overlap(ta, tb) or same_body(ta, tb, ra):
                continue
            if la is None:
                refused.setdefault(b, (ra, a))
            elif lb is None:
                refused.setdefault(a, (ra, b))
            elif _dominates(la, lb):
                refused.setdefault(b, (ra, a))
            elif _dominates(lb, la):
                refused.setdefault(a, (ra, b))
            else:
                refused.setdefault(a, (ra, b))
                refused.setdefault(b, (ra, a))
    kept = [link for link in links if link.track not in refused]
    refusals = [{"track": name, "recorder": recorder, "rival": rival,
                 "reason": "recorder link to {0} refused: {1} carries {0} at the same time and no same-body (split) "
                           "evidence shows the two tracks are one vehicle".format(recorder, rival)}
                for name, (recorder, rival) in sorted(refused.items())]
    return kept, refusals



def smooth_entity_states(states: List[Dict[str, Any]], cfg: ReconstructionConfig,
                         boundaries: Sequence[float] = ()) -> List[Dict[str, Any]]:
    if not states:
        return states
    tracking = cfg.tracking
    accel = tracking.acceleration_std_mps2
    times = [float(s["t_global"]) for s in states]
    measured = [bool(s.get("measured_by")) for s in states]
    breaks = {0}
    for k in range(1, len(states)):
        dt = times[k] - times[k - 1]
        cut = dt > tracking.max_track_gap_s + 1e-9 or any(times[k - 1] < b <= times[k] for b in boundaries)
        if not cut and measured[k] and measured[k - 1]:
            dv = math.hypot(states[k]["vx"] - states[k - 1]["vx"], states[k]["vy"] - states[k - 1]["vy"])
            spread = math.sqrt(states[k]["vel_std_mps"] ** 2 + states[k - 1]["vel_std_mps"] ** 2 + (accel * dt) ** 2)
            cut = dv > 3.0 * spread
        if cut:
            breaks.add(k)
    edges = sorted(breaks) + [len(states)]
    out = [dict(s) for s in states]
    H = np.eye(4)
    for a, b in zip(edges, edges[1:]):
        if not any(measured[a:b]):
            continue
        first = next(k for k in range(a, b) if measured[k])
        s0, back = states[first], times[a] - times[first]
        x = np.array([s0["x"] + s0["vx"] * back, s0["y"] + s0["vy"] * back, s0["vx"], s0["vy"]], dtype=float)
        P = np.eye(4) * 25.0
        filtered, predicted = [], []
        for k in range(a, b):
            if k > a:
                x, P = kf_predict(x, P, times[k] - times[k - 1], accel)
            predicted.append((x, P))
            if measured[k]:
                s = states[k]
                z = np.array([s["x"], s["y"], s["vx"], s["vy"]], dtype=float)
                R = np.diag([max(s["pos_std_m"], 0.05) ** 2] * 2 + [max(s["vel_std_mps"], 0.05) ** 2] * 2)
                x, P = kf_update(x, P, z, H, R)
            filtered.append((x, P))
        smoothed = list(filtered)
        for k in range(len(filtered) - 2, -1, -1):
            F = _transition(times[a + k + 1] - times[a + k])
            gain = filtered[k][1] @ F.T @ np.linalg.inv(predicted[k + 1][1])
            xs = filtered[k][0] + gain @ (smoothed[k + 1][0] - predicted[k + 1][0])
            Ps = filtered[k][1] + gain @ (smoothed[k + 1][1] - predicted[k + 1][1]) @ gain.T
            smoothed[k] = (xs, Ps)
        for k, (xs, Ps) in enumerate(smoothed):
            row = out[a + k]
            row.update({"x": round(float(xs[0]), 3), "y": round(float(xs[1]), 3),
                        "vx": round(float(xs[2]), 3), "vy": round(float(xs[3]), 3),
                        "pos_std_m": round(math.sqrt(max(float(np.max(np.linalg.eigvalsh(Ps[:2, :2]))), 0.0)), 3),
                        "vel_std_mps": round(math.sqrt(max(float(np.trace(Ps[2:, 2:])) / 2.0, 0.0)), 3),
                        "position": "smoothed"})
    return out


def entity_trajectory(group: Sequence[CommonTrack], cfg: ReconstructionConfig) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    fusion, semantics = cfg.fusion, cfg.semantics
    step = 1.0 / fusion.entity_output_rate_hz
    start, end = min(t.start for t in group), max(t.end for t in group)
    states: List[Dict[str, Any]] = []
    lengths, widths, length_bounds, width_bounds = [], [], [], []
    prior_std = (fusion.box_length_std_m / 2.0, fusion.box_width_std_m / 2.0)
    floor = cfg.tracking.radial_speed_std_mps
    heading_held: Optional[float] = None
    for k in range(int(math.ceil(start / step - 1e-6)), int(math.floor(end / step + 1e-6)) + 1):
        t = round(k * step, 4)
        observations = [(track.recorder, sample) for track in group
                        for sample in [track.state_at(t, tolerance=step / 2.0 + 1e-3)] if sample is not None]
        if not observations:
            continue
        velocity, velocity_cov = covariance_intersection(
            [(s.velocity, np.eye(2) * max(s.vel_std, floor) ** 2) for _, s in observations])
        vel_std = math.sqrt(max(float(np.trace(velocity_cov)) / 2.0, 0.0))
        moving = float(np.hypot(*velocity)) >= max(3.0 * vel_std, 1.0)
        heading = math.atan2(velocity[1], velocity[0]) if moving else heading_held
        heading_source = "velocity" if moving else ("held" if heading is not None else None)
        heading_held = heading
        measured = [(o, s) for o, s in observations if s.measured]
        method, centre, covariance, halves = "covariance_intersection", None, None, None
        if heading is not None and measured:
            try:
                fit = fit_box(measured, heading, cfg)
            except (ValueError, np.linalg.LinAlgError):
                fit = None
            if fit is not None and (fit.observers >= 2 or fit.faces >= 2):
                method, centre, covariance, halves = "box_fit", fit.centre, fit.covariance[:2, :2], fit.halves
                if math.sqrt(fit.covariance[2, 2]) < 0.6 * prior_std[0]:
                    lengths.append(2.0 * fit.halves[0])
                if math.sqrt(fit.covariance[3, 3]) < 0.6 * prior_std[1]:
                    widths.append(2.0 * fit.halves[1])
            if fit is not None:
                for m in fit.measurements:
                    if m.count >= 5:
                        (width_bounds if m.half == 0 else length_bounds).append(m.extent)
        if centre is None:
            centre, covariance = covariance_intersection([_centre_estimate(o, s, heading, cfg) for o, s in observations])
        states.append({"t_global": t, "x": round(float(centre[0]), 3), "y": round(float(centre[1]), 3),
                       "pos_std_m": round(math.sqrt(max(float(np.max(np.linalg.eigvalsh(covariance))), 0.0)), 3),
                       "vx": round(float(velocity[0]), 3), "vy": round(float(velocity[1]), 3),
                       "vel_std_mps": round(vel_std, 3),
                       "heading_deg": None if heading is None else round(math.degrees(heading), 2),
                       "heading_source": heading_source,
                       "length_m": None if halves is None else round(2.0 * halves[0], 3),
                       "width_m": None if halves is None else round(2.0 * halves[1], 3),
                       "method": method, "observers": sorted({o for o, _ in observations}),
                       "measured_by": sorted({o for o, s in measured})})

    def dimension(fitted: List[float], bounds: List[float], prior: float, prior_spread: float) -> Dict[str, Any]:
        bound = float(np.percentile(bounds, 90)) if len(bounds) >= 3 else None
        usable = bound is not None and bound <= prior + 3.0 * prior_spread
        value, source = (float(np.median(fitted)), "fitted") if fitted else (prior, "prior")
        if usable and bound > value:
            value, source = bound, "observed_extent"
        spread = float(np.std(fitted)) if len(fitted) > 1 and source == "fitted" else prior_spread
        return {"value_m": round(value, 3), "source": source, "std_m": round(spread, 3),
                "fitted_instants": len(fitted), "observed_extent_m": None if bound is None else round(bound, 3),
                "observed_extent_used": bool(usable and bound > value - 1e-9 and source == "observed_extent")}

    length = dimension(lengths, length_bounds, semantics.target_length_m, fusion.box_length_std_m)
    width = dimension(widths, width_bounds, semantics.target_width_m, fusion.box_width_std_m)
    impacts = sorted({t.own_impact for t in group if getattr(t, "own_impact", None) is not None})
    states = smooth_entity_states(states, cfg, impacts)
    return states, {"length_m": length["value_m"], "width_m": width["value_m"], "length": length, "width": width}



FUSION_PARAMETERS = ("observed_alignment_step_s", "observed_alignment_min_samples", "observed_alignment_min_speed_mps",
                     "observed_alignment_uniqueness_ratio", "link_min_samples",
                     "link_min_fraction", "anonymous_gate_probability", "anonymous_min_shared_samples",
                     "anonymous_pass_fraction", "stitch_max_gap_s", "box_face_std_m", "box_length_std_m",
                     "box_width_std_m", "entity_output_rate_hz")


class OffsetPoseSource(PoseSource):

    def __init__(self, base: PoseSource, dx: float, dy: float, position_std_m: float) -> None:
        self.base, self.dx, self.dy = base, float(dx), float(dy)
        self.name = getattr(base, "name", "recorded") + "+mutual"
        self.position_std_m = float(position_std_m)
        self.yaw_std_rad = getattr(base, "yaw_std_rad", 0.0)
        self.velocity_std_mps = getattr(base, "velocity_std_mps", 0.0)

    @property
    def start(self) -> float:
        return self.base.start

    @property
    def end(self) -> float:
        return self.base.end

    def pose_at(self, t_local: float) -> WorldPose:
        pose = self.base.pose_at(t_local)
        return WorldPose(pose.x + self.dx, pose.y + self.dy, pose.yaw, pose.vx, pose.vy)

    def poses_at(self, times: Sequence[float]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        x, y, yaw = self.base.poses_at(times)
        return x + self.dx, y + self.dy, yaw


MUTUAL_HEADING_BIN_RAD = math.radians(10.0)
MUTUAL_DECORRELATION_S = 1.0
MUTUAL_SCAN_TRUNCATION_M = 1.0
MUTUAL_SCAN_STEP_M = 0.5
MUTUAL_SCAN_MAX_HALF_WIDTH_M = 30.0
MUTUAL_SCAN_MAX_POINTS = 2000


def _body_faces(fp: Any) -> List[Tuple[np.ndarray, float, Tuple[float, float], str]]:
    return [(np.array([1.0, 0.0]), fp.x_max, (fp.y_min, fp.y_max), "front"),
            (np.array([-1.0, 0.0]), -fp.x_min, (fp.y_min, fp.y_max), "rear"),
            (np.array([0.0, 1.0]), fp.y_max, (fp.x_min, fp.x_max), "right"),
            (np.array([0.0, -1.0]), -fp.y_min, (fp.x_min, fp.x_max), "left")]


def _sample_returns(sample: CommonSample) -> Tuple[np.ndarray, np.ndarray]:
    if sample.returns is not None and sample.origins is not None and len(sample.returns):
        return sample.returns, sample.origins
    return sample.near[None, :], sample.observer[None, :]


def face_depths(body: RecorderBody, sample: CommonSample) -> List[Tuple[str, np.ndarray, float, int]]:
    pose, fp = body.pose_at_global(sample.t_global), body.footprint or DEFAULT_BODY
    points, origins = _sample_returns(sample)
    c, s = math.cos(pose.yaw), math.sin(pose.yaw)

    def local(world: np.ndarray) -> np.ndarray:
        dx, dy = world[:, 0] - pose.x, world[:, 1] - pose.y
        return np.column_stack([c * dx + s * dy, -s * dx + c * dy])

    lp, lo = local(points), local(origins)
    outside = ~((lo[:, 0] > fp.x_min) & (lo[:, 0] < fp.x_max) & (lo[:, 1] > fp.y_min) & (lo[:, 1] < fp.y_max))
    faces = _body_faces(fp)
    best, best_gap = np.full(len(lp), -1), np.full(len(lp), np.inf)
    for index, (normal, offset, (low, high), _) in enumerate(faces):
        along = lp[:, 1] if abs(normal[0]) > 0.5 else lp[:, 0]
        gap = np.hypot(lp @ normal - offset, np.maximum(0.0, np.maximum(low - along, along - high)))
        better = outside & (lo @ normal > offset) & (gap < best_gap)
        best[better], best_gap[better] = index, gap[better]
    out = []
    for index, (normal, offset, _, name) in enumerate(faces):
        chosen = best == index
        if chosen.any():
            world = np.array([c * normal[0] - s * normal[1], s * normal[0] + c * normal[1]])
            out.append((name, world, float(np.median(offset - lp[chosen] @ normal)), int(chosen.sum())))
    return out


def scan_relative_offset(body: RecorderBody, samples: Sequence[CommonSample], spread_m: float) -> np.ndarray:
    fp = body.footprint or DEFAULT_BODY
    parts = []
    for sample in samples:
        points, _ = _sample_returns(sample)
        pose = body.pose_at_global(sample.t_global)
        c, s = math.cos(pose.yaw), math.sin(pose.yaw)
        dx, dy = points[:, 0] - pose.x, points[:, 1] - pose.y
        parts.append(np.column_stack([c * dx + s * dy, -s * dx + c * dy, np.full(len(points), c),
                                      np.full(len(points), s)]))
    data = np.vstack(parts)
    if len(data) > MUTUAL_SCAN_MAX_POINTS:
        data = data[np.linspace(0, len(data) - 1, MUTUAL_SCAN_MAX_POINTS).astype(int)]
    lx, ly, cs, sn = (data[:, k][None, :] for k in range(4))

    def cost(candidates: np.ndarray) -> np.ndarray:
        out = np.empty(len(candidates))
        for first in range(0, len(candidates), 256):
            d = candidates[first:first + 256]
            px = lx + cs * d[:, :1] + sn * d[:, 1:]
            py = ly - sn * d[:, :1] + cs * d[:, 1:]
            gx, gy = np.maximum(fp.x_min - px, px - fp.x_max), np.maximum(fp.y_min - py, py - fp.y_max)
            gap = np.maximum(gx, gy)
            distance = np.where(gap > 0.0, np.hypot(np.maximum(gx, 0.0), np.maximum(gy, 0.0)), -gap)
            out[first:first + 256] = np.mean(np.minimum(distance, MUTUAL_SCAN_TRUNCATION_M) ** 2, axis=1)
        return out + 1e-4 * MUTUAL_SCAN_TRUNCATION_M ** 2 * np.sum(candidates ** 2, axis=1) / max(spread_m, 0.1) ** 2

    centre = np.zeros(2)
    half, step = min(3.0 * spread_m, MUTUAL_SCAN_MAX_HALF_WIDTH_M), MUTUAL_SCAN_STEP_M
    for _ in range(3):
        axis = np.arange(-half, half + 1e-9, step)
        grid = np.array([(centre[0] + a, centre[1] + b) for a in axis for b in axis])
        centre = grid[int(np.argmin(cost(grid)))]
        half, step = step, step / 5.0
    return centre


def mutual_offsets(locals_: Sequence[Any], alignment: Alignment, associations: Sequence[Association],
                   poses: Dict[str, PoseSource], cfg: ReconstructionConfig) -> Dict[str, Any]:
    sigma = {name: float(getattr(source, "position_std_m", 0.0)) for name, source in poses.items()}
    unknown = sorted(name for name, value in sigma.items() if value > 1e-6)
    if not unknown:
        return {"applied": False, "reason": "the pose sources declare no position error", "offsets_m": {}}
    index = {name: 2 * i for i, name in enumerate(unknown)}
    size = 2 * len(unknown)
    prior = np.diag(np.repeat([1.0 / sigma[name] ** 2 for name in unknown], 2))

    def part(vector: np.ndarray, name: str) -> np.ndarray:
        return vector[index[name]:index[name] + 2] if name in index else np.zeros(2)

    def identified(view: CommonView) -> Dict[Tuple[str, str], List[CommonSample]]:
        out: Dict[Tuple[str, str], List[CommonSample]] = {}
        for track in view.tracks:
            if track.status != ASSOCIATED or track.entity not in view.bodies or track.entity == track.recorder:
                continue
            if track.recorder not in index and track.entity not in index:
                continue
            body, observer = view.bodies[track.entity], view.bodies[track.recorder]
            cut = min([t for t, _ in body.contacts] + [t for t, partners in observer.contacts if body.recorder in partners]
                      + [math.inf])
            samples = [s for s in track.samples if s.measured and body.covers(s.t_global) and s.t_global < cut]
            if len(samples) >= cfg.fusion.link_min_samples:
                out.setdefault((track.recorder, track.entity), []).extend(samples)
        return out

    def row_for(observer: str, target: str, vector: np.ndarray) -> np.ndarray:
        row = np.zeros(size)
        if target in index:
            row[index[target]:index[target] + 2] += vector
        if observer in index:
            row[index[observer]:index[observer] + 2] -= vector
        return row

    view = build_common_view(locals_, alignment, associations, poses)
    pairs = identified(view)
    if not pairs:
        return {"applied": False, "reason": "no track identified with another recorder", "offsets_m": {}}
    rows, values, scans = [], [], []
    for (observer, target), samples in sorted(pairs.items()):
        spread = math.hypot(sigma[observer], sigma[target])
        offset = scan_relative_offset(view.bodies[target], samples, spread)
        scans.append({"observer": observer, "recorder": target, "samples": len(samples),
                      "offset_m": [round(float(offset[0]), 3), round(float(offset[1]), 3)]})
        for axis in (0, 1):
            unit = np.zeros(2)
            unit[axis] = 1.0
            rows.append(row_for(observer, target, unit))
            values.append(float(offset[axis]))
    A, e = np.array(rows), np.array(values)
    scanned = np.linalg.solve(A.T @ A / MUTUAL_SCAN_STEP_M ** 2 + prior, A.T @ e / MUTUAL_SCAN_STEP_M ** 2)

    guess, estimate = scanned, np.zeros(size)
    equations: List[Dict[str, Any]] = []
    covariance, reduced, iterations = np.linalg.inv(prior), None, 0
    for _ in range(max(1, cfg.fusion.mutual_refinement_iterations)):
        iterations += 1
        moved = {name: OffsetPoseSource(source, *(-part(guess, name)), sigma[name]) for name, source in poses.items()}
        view = build_common_view(locals_, alignment, associations, moved)
        groups: Dict[Tuple[str, str, str, int], List[Tuple[float, np.ndarray, float]]] = {}
        for (observer, target), samples in identified(view).items():
            shift = part(guess, target) - part(guess, observer)
            for sample in samples:
                for face, normal, depth, _ in face_depths(view.bodies[target], sample):
                    heading = math.atan2(normal[1], normal[0]) + math.pi
                    groups.setdefault((observer, target, face, int(heading // MUTUAL_HEADING_BIN_RAD)), []).append(
                        (sample.t_global, normal, depth + float(normal @ shift)))
        if not groups:
            return {"applied": False, "reason": "no face of a recorder observed", "offsets_m": {}}
        bins: Dict[Tuple[str, str, str], int] = {}
        for observer, target, face, _ in groups:
            bins[(observer, target, face)] = bins.get((observer, target, face), 0) + 1
        rows, values, weights, equations = [], [], [], []
        for (observer, target, face, _), items in sorted(groups.items()):
            depths = np.array([item[2] for item in items])
            normal = np.mean([item[1] for item in items], axis=0)
            normal = normal / max(float(np.hypot(*normal)), 1e-9)
            median = float(np.median(depths))
            spread = 1.4826 * float(np.median(np.abs(depths - median)))
            seconds = len({int(math.floor(item[0] / MUTUAL_DECORRELATION_S)) for item in items})
            variance = bins[(observer, target, face)] * cfg.fusion.box_face_std_m ** 2 + spread ** 2 / seconds
            rows.append(row_for(observer, target, normal))
            values.append(median)
            weights.append(1.0 / variance)
            equations.append({"observer": observer, "recorder": target, "face": face, "samples": len(items),
                              "seconds": seconds, "normal_deg": round(math.degrees(math.atan2(normal[1], normal[0])), 1),
                              "median_depth_m": round(median, 3), "std_m": round(math.sqrt(variance), 3)})
        A, e, w = np.array(rows), np.array(values), np.array(weights)
        covariance = np.linalg.inv(A.T @ (A * w[:, None]) + prior)
        estimate = covariance @ (A.T @ (w * e))
        residual = e - A @ estimate
        dof = max(1, len(e) - int(np.linalg.matrix_rank(A)))
        reduced = float(np.sum(w * residual ** 2)) / dof
        share = np.eye(size) - covariance @ prior
        following = scanned + share @ (estimate - scanned)
        if float(np.max(np.abs(following - guess))) < 1e-3:
            break
        guess = following
    if reduced is not None and reduced > 1.0:
        covariance = covariance * reduced
    offsets, declared, posterior = {}, {}, {}
    for name in sorted(poses):
        offsets[name] = [round(float(-v), 3) + 0.0 for v in part(estimate, name)]
        if name not in index:
            declared[name] = round(sigma[name], 3)
            continue
        block = covariance[index[name]:index[name] + 2, index[name]:index[name] + 2]
        eigen, vectors = np.linalg.eigh(block)
        posterior[name] = {"std_major_m": round(math.sqrt(max(eigen[1], 0.0)), 3),
                           "std_minor_m": round(math.sqrt(max(eigen[0], 0.0)), 3),
                           "minor_axis_deg": round(math.degrees(math.atan2(vectors[1, 0], vectors[0, 0])) % 180.0, 1)}
        declared[name] = round(min(sigma[name], math.sqrt(max(eigen[1], 0.0))), 3)
    return {"applied": True, "method": "point-to-face maximum a posteriori from a scan-matched start, the "
                                       "declared accuracies as priors",
            "offsets_m": offsets, "declared_position_std_m": declared, "posterior": posterior,
            "unknowns": unknown, "covariance_m2": [[round(float(v), 5) for v in row] for row in covariance],
            "reduced_chi2": None if reduced is None else round(reduced, 3), "scans": scans,
            "equations": equations, "iterations": iterations}


@dataclass
class RoadUserFusion:

    links: List[RecorderLink]
    evidence: List[PairEvidence]
    entities: List[Dict[str, Any]]
    pose_sources: Dict[str, str]
    names: Dict[Tuple[str, str], str] = field(default_factory=dict)
    refinement: Optional[Dict[str, Any]] = None
    poses: Dict[str, PoseSource] = field(default_factory=dict)

    def to_dict(self, cfg: ReconstructionConfig, alignment: Alignment) -> Dict[str, Any]:
        return {"definition": "road users in the common frame of the recorders' own pose streams; a road user "
                              "that recorded nothing is an anonymous entity U1, U2, ... and is never named after "
                              "a participant; t_global as in alignment.json; positions in the map frame of the "
                              "pose streams (m), headings in degrees",
                "pose_sources": dict(sorted(self.pose_sources.items())),
                "parameters": dict({key: getattr(cfg.fusion, key) for key in FUSION_PARAMETERS},
                                   measurement_std_m=cfg.tracking.measurement_std_m,
                                   radial_speed_std_mps=cfg.tracking.radial_speed_std_mps,
                                   acceleration_std_mps2=cfg.tracking.acceleration_std_mps2),
                "observed_alignment": list(alignment.observed),
                "mutual_refinement": self.refinement,
                "recorder_links": [dict(link.__dict__) for link in self.links],
                "association_evidence": [dict(e.to_dict(), score=round(e.score, 3) if math.isfinite(e.score) else None)
                                         for e in self.evidence],
                "entities": self.entities,
                **({"cannot_links": self.cannot_links} if getattr(self, "cannot_links", None) is not None else {}),
                **({"retrospective": self.retrospective} if getattr(self, "retrospective", None) is not None else {})}


def fuse_road_users(locals_: Sequence[Any], alignment: Alignment, associations: List[Association],
                    poses: Dict[str, PoseSource], cfg: ReconstructionConfig) -> RoadUserFusion:
    from .identity import fuse_corrected
    refinement = None
    if cfg.fusion.mutual_refinement or any(getattr(s, "position_std_m", 0.0) > 0.0 for s in poses.values()):
        import copy as _copy

        def corrected(record: Dict[str, Any]) -> Dict[str, PoseSource]:
            if not record.get("applied"):
                return poses
            return {name: OffsetPoseSource(source, *record["offsets_m"][name], record["declared_position_std_m"][name])
                    for name, source in poses.items()}
        first = mutual_offsets(locals_, alignment, associations, poses, cfg)
        trial = _copy.deepcopy(list(associations))
        fuse_corrected(locals_, alignment, trial, corrected(first), cfg)
        refinement = mutual_offsets(locals_, alignment, trial, poses, cfg)
        refinement["first_stage"] = {key: first.get(key) for key in ("applied", "offsets_m", "declared_position_std_m",
                                                                      "posterior", "reason") if key in first}
        poses = corrected(refinement)
    result = fuse_corrected(locals_, alignment, associations, poses, cfg, refinement)
    result.refinement = refinement
    result.poses = dict(poses)
    return result


def collision_continuity_links(view: CommonView, associations: Sequence[Association],
                               alignment: Alignment, links: Sequence[RecorderLink],
                               cfg: ReconstructionConfig) -> List[RecorderLink]:
    known = {t.name: t.entity for t in view.tracks if t.status == ASSOCIATED}
    known.update({link.track: link.recorder for link in links})
    decisions = {a.local_graph + ':' + a.local_track: a for a in associations}
    out = []
    for track in view.tracks:
        if track.name in known or track.parent_track is None:
            continue
        item = decisions[track.name]
        clock = alignment.graphs[track.recorder]
        if clock.status != 'ALIGNED' or clock.offset_to_global is None:
            continue
        event = next((e for e in alignment.matched_events if e['event_id'] == item.collision_event
                      and track.recorder in e['graphs'] and item.candidate in e['graphs']), None)
        if event is None or track.end-track.start > 2*cfg.fusion.contact_window_s:
            continue
        contact = event['t_local'][track.recorder] + clock.offset_to_global
        if not track.start <= contact <= track.end:
            continue
        siblings = [t for t in view.tracks if t.recorder == track.recorder and t.parent_track == track.parent_track]
        before = [t for t in siblings if 0 < track.start-t.end <= cfg.tracking.max_track_gap_s and known.get(t.name)==item.candidate]
        after = [t for t in siblings if 0 < t.start-track.end <= cfg.tracking.max_track_gap_s and known.get(t.name)==item.candidate]
        if not before or not after:
            continue
        body = view.bodies[item.candidate]
        samples = [s for s in track.samples if s.measured and body.covers(s.t_global)]
        if len(samples) < cfg.fusion.link_min_samples:
            continue
        distances = np.array([body.distance(s.t_global, s.point) for s in samples])
        sigmas = np.array([_position_sigma(cfg, s, body.poses) for s in samples])
        within = distances <= 3*sigmas
        width = cfg.fusion.link_min_samples
        if not all(np.mean(within[i:i+width]) >= cfg.fusion.link_min_fraction for i in range(len(samples)-width+1)):
            continue
        at = min(samples, key=lambda s: abs(s.t_global-contact))
        observer = view.bodies[track.recorder]
        if abs(at.t_global-contact) > cfg.tracking.max_track_gap_s or observer.distance(contact, at.near) > cfg.fusion.touching_clearance_m:
            continue
        rivals = [t for t in view.tracks if t.recorder==track.recorder and t.parent_track!=track.parent_track
                  and t.start <= contact <= t.end]
        if any(observer.distance(contact,min(t.samples,key=lambda s:abs(s.t_global-contact)).near)
               < cfg.fusion.rival_clearance_m for t in rivals):
            continue
        if any(sum(rival.distance(s.t_global,s.point)<=3*_position_sigma(cfg,s,rival.poses)
                   for s in samples if rival.covers(s.t_global)) >= width*cfg.fusion.link_min_fraction
               for name,rival in view.bodies.items() if name not in (track.recorder,item.candidate)):
            continue
        speed_gap = [np.linalg.norm(s.velocity-np.array([body.pose_at_global(s.t_global).vx,
                                                        body.pose_at_global(s.t_global).vy])) for s in samples]
        out.append(RecorderLink(track.name,item.candidate,len(samples),round(float(np.median(distances)),3),
                   round(float(np.median(distances/sigmas)),3),round(float(np.median(speed_gap)),3),
                   round(float(np.mean(within)),3),True,
                   collision_anchored=True))
    return out
