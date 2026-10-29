
from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from .config import FusionConfig
from .models import Alignment, GraphClock, GraphNode, LocalGraph

ALIGNED = "ALIGNED"
UNALIGNED = "UNALIGNED"


def impulse_similarity(first: GraphNode, second: GraphNode) -> float:
    a = float(first.attributes["peak_impulse"])
    b = float(second.attributes["peak_impulse"])
    return 1.0 - abs(a - b) / max(a, b, 1e-9)


def impulse_z(a: float, b: float, cfg: FusionConfig) -> float:
    sigma = cfg.impulse_relative_std * math.hypot(a, b)
    return abs(a - b) / max(sigma, 1e-9)


def _impulse_pass(a: float, b: float, cfg: FusionConfig, has_geometry: bool) -> bool:
    if a <= 0 or b <= 0 or not math.isfinite(a + b):
        return False
    if has_geometry and cfg.impulse_relative_std > 0:
        return impulse_z(a, b, cfg) <= cfg.impulse_sigma_gate
    return abs(a - b) / max(a, b) <= cfg.impulse_tolerance + 1e-9


class _Clocks:

    def __init__(self, owners: Sequence[str]) -> None:
        self.parent = {owner: owner for owner in owners}
        self.shift = {owner: 0.0 for owner in owners}
        self.event = {owner: None for owner in owners}

    def root(self, owner: str) -> Tuple[str, float]:
        shift = 0.0
        while self.parent[owner] != owner:
            shift += self.shift[owner]
            owner = self.parent[owner]
        return owner, shift

    def link(self, first: str, t_first: float, second: str, t_second: float) -> None:
        (root_a, shift_a), (root_b, shift_b) = self.root(first), self.root(second)
        self.parent[root_b] = root_a
        self.shift[root_b] = (t_first + shift_a) - (t_second + shift_b)

    def residual(self, first: str, t_first: float, second: str, t_second: float) -> float:
        (_, shift_a), (_, shift_b) = self.root(first), self.root(second)
        return (t_first + shift_a) - (t_second + shift_b)

    def linked(self, first: str, second: str) -> bool:
        return self.root(first)[0] == self.root(second)[0]


ContactCheck = Callable[[str, float, str, float], Optional[Tuple[float, float]]]


def _forced_pairs(candidates, consistent, cfg, clocks, used) -> set:
    import copy
    edges = [c for c in candidates if c[1] not in used and c[2] not in used
             and _apart(consistent, c[3], c[4].t_local, c[5], c[6].t_local)[0] is None]
    visits, best, common = 0, -1, set()

    def walk(remaining, state, chosen):
        nonlocal visits, best, common
        visits += 1
        if visits > 10000:
            raise OverflowError
        if not remaining:
            n = len(chosen)
            if n > best:
                best, common = n, set(chosen)
            elif n == best:
                common.intersection_update(chosen)
            return
        report = remaining[0][1]
        walk([c for c in remaining if report not in (c[1], c[2])], state, chosen)
        for c in remaining:
            if report not in (c[1], c[2]):
                continue
            _, ia, ib, a, na, b, nb = c
            if state.linked(a, b) and abs(state.residual(a, na.t_local, b, nb.t_local)) > cfg.clock_tolerance_s + 1e-9:
                continue
            nxt = copy.deepcopy(state)
            if not nxt.linked(a, b):
                nxt.link(a, na.t_local, b, nb.t_local)
            walk([other for other in remaining if not ({ia, ib} & {other[1], other[2]})], nxt, chosen + [(ia, ib)])
    try:
        walk(edges, clocks, [])
    except OverflowError:
        return set()
    return common


def _apart(consistent: Optional[ContactCheck], first: str, t_first: float, second: str,
           t_second: float) -> Tuple[Optional[str], Optional[str]]:
    measured = None if consistent is None else consistent(first, t_first, second, t_second)
    if measured is None:
        return None, None
    gap, tolerance = measured
    if gap > tolerance:
        return ("the two bodies are {0:.1f} m apart at their reports (their pose streams; tolerance {1:.1f} m): "
                "two separate contacts".format(gap, tolerance), None)
    return None, "the two bodies touch at their reports ({0:.2f} m apart, tolerance {1:.1f} m)".format(gap, tolerance)


def match_collisions(graphs: Sequence[LocalGraph], cfg: FusionConfig,
                     consistent: Optional[ContactCheck] = None,
                     clock_check: Optional[Callable[[str, float, str, float], Optional[bool]]] = None
                     ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    reports = [(graph.owner, node) for graph in sorted(graphs, key=lambda item: item.owner)
               for node in graph.nodes if node.event_type == "COLLISION"]
    candidates = []
    for index, (first_owner, first) in enumerate(reports):
        for second_owner, second in reports[index + 1:]:
            if first_owner == second_owner:
                continue
            if clock_check is not None and clock_check(first_owner, first.t_local, second_owner, second.t_local) is False:
                continue
            similarity = impulse_similarity(first, second)
            geometry = None if consistent is None else consistent(first_owner, first.t_local, second_owner, second.t_local)
            if _impulse_pass(float(first.attributes['peak_impulse']), float(second.attributes['peak_impulse']),
                             cfg, geometry is not None):
                candidates.append((-similarity, first.node_id, second.node_id,
                                   first_owner, first, second_owner, second))
    candidates.sort(key=lambda item: item[:3])
    per_report: Dict[str, int] = {}
    for candidate in candidates:
        for node_id in (candidate[1], candidate[2]):
            per_report[node_id] = per_report.get(node_id, 0) + 1

    clocks = _Clocks([graph.owner for graph in graphs])
    used = set()
    matched, rejected = [], []
    for negative_similarity, first_id, second_id, first_owner, first, second_owner, second in candidates:
        if first_id in used or second_id in used:
            continue
        similarity = round(-negative_similarity, 4)
        peaks = {first_owner: first.attributes["peak_impulse"], second_owner: second.attributes["peak_impulse"]}
        apart, touching = _apart(consistent, first_owner, first.t_local, second_owner, second.t_local)
        if apart is not None:
            rejected.append({"nodes": {first_owner: first_id, second_owner: second_id},
                             "t_local": {first_owner: first.t_local, second_owner: second.t_local},
                             "peak_impulse": peaks, "impulse_similarity": similarity, "reason": apart})
            continue
        timing = None
        if clocks.linked(first_owner, second_owner):
            residual = clocks.residual(first_owner, first.t_local, second_owner, second.t_local)
            if abs(residual) > cfg.clock_tolerance_s + 1e-9:
                rejected.append({"nodes": {first_owner: first_id, second_owner: second_id},
                                 "t_local": {first_owner: first.t_local, second_owner: second.t_local},
                                 "peak_impulse": peaks, "impulse_similarity": similarity,
                                 "reason": "{0:+.3f} s from the clock offset between {1} and {2} that earlier "
                                           "matches fix (tolerance {3:.2f} s)".format(
                                               residual, first_owner, second_owner, cfg.clock_tolerance_s)})
                continue
            timing = "consistent with the clock offset between {0} and {1} that earlier matches fix " \
                     "({2:+.3f} s, tolerance {3:.2f} s)".format(first_owner, second_owner, residual,
                                                                cfg.clock_tolerance_s)
        else:
            rivals = []
            if consistent is not None:
                for rival in candidates:
                    _, rid_a, rid_b, ro_a, rn_a, ro_b, rn_b = rival
                    if (rid_a, rid_b) == (first_id, second_id) or rid_a in used or rid_b in used:
                        continue
                    if not ({rid_a, rid_b} & {first_id, second_id}):
                        continue
                    if _apart(consistent, ro_a, rn_a.t_local, ro_b, rn_b.t_local)[0] is not None:
                        continue
                    if clocks.linked(ro_a, ro_b) and abs(clocks.residual(ro_a, rn_a.t_local, ro_b, rn_b.t_local)) > cfg.clock_tolerance_s + 1e-9:
                        continue
                    rivals.append((rid_a, rid_b))
            if rivals and (first_id, second_id) not in _forced_pairs(candidates, consistent, cfg, clocks, used):
                rejected.append({'nodes': {first_owner: first_id, second_owner: second_id},
                                 't_local': {first_owner: first.t_local, second_owner: second.t_local},
                                 'peak_impulse': peaks, 'impulse_similarity': similarity,
                                 'reason': 'ambiguous geometry-compatible collision reports; no independent clock anchor'})
                continue
            clocks.link(first_owner, first.t_local, second_owner, second.t_local)
        used.update((first_id, second_id))
        evidence = ["{0} and {1} both recorded a collision".format(first_owner, second_owner),
                    "peak impulses {0} vs {1} N*s (similarity {2:.3f}, tolerance {3:.2f})".format(
                        peaks[first_owner], peaks[second_owner], similarity, cfg.impulse_tolerance)]
        alternatives = max(per_report[first_id], per_report[second_id]) - 1
        evidence.append("no competing report within tolerance" if alternatives == 0
                        else "{0} competing report(s) within tolerance; best match kept".format(alternatives))
        if touching is not None:
            evidence.append(touching)
        if timing is not None:
            evidence.append(timing)
        z = impulse_z(float(peaks[first_owner]), float(peaks[second_owner]), cfg)
        if touching is not None:
            evidence.append('independent relative impulse std {0:.3f}; combined z {1:.3f} (gate {2:.1f}); engineering assumption'.format(
                cfg.impulse_relative_std, z, cfg.impulse_sigma_gate))
        matched.append({"event_id": None, "graphs": [first_owner, second_owner],
                        "nodes": {first_owner: first_id, second_owner: second_id},
                        "t_local": {first_owner: first.t_local, second_owner: second.t_local},
                        "peak_impulse": peaks, "impulse_similarity": similarity,
                        "impulse_z": round(z, 4),
                        "confidence": similarity, "evidence": evidence})
    matched += _match_merged_bursts(reports, used, clocks, cfg, consistent)
    matched.sort(key=lambda event: (event["graphs"][0], event["t_local"][event["graphs"][0]]))
    for number, event in enumerate(matched, 1):
        event["event_id"] = "collision_{0:03d}".format(number)
    return matched, rejected


def _match_merged_bursts(reports, used, clocks: "_Clocks", cfg: FusionConfig,
                         consistent: Optional[ContactCheck] = None) -> List[Dict[str, Any]]:
    matched = []
    taken = set()
    for owner, node in reports:
        if node.node_id in used:
            continue
        peak = float(node.attributes["peak_impulse"])
        best = None
        for other_owner, other in reports:
            if other_owner == owner or not clocks.linked(owner, other_owner):
                continue
            for t_burst, burst_peak in other.attributes.get("merged_bursts", []):
                if (other.node_id, t_burst) in taken:
                    continue
                similarity = 1.0 - abs(peak - burst_peak) / max(peak, burst_peak, 1e-9)
                residual = clocks.residual(owner, node.t_local, other_owner, t_burst)
                geometry = None if consistent is None else consistent(owner, node.t_local, other_owner, t_burst)
                if _impulse_pass(peak, burst_peak, cfg, geometry is not None) and abs(residual) <= cfg.clock_tolerance_s + 1e-9:
                    if _apart(consistent, owner, node.t_local, other_owner, t_burst)[0] is not None:
                        continue
                    if best is None or similarity > best[0]:
                        best = (similarity, other_owner, other, t_burst, burst_peak, residual)
        if best is None:
            continue
        similarity, other_owner, other, t_burst, burst_peak, residual = best
        taken.add((other.node_id, t_burst))
        used.add(node.node_id)
        graphs = sorted([owner, other_owner])
        matched.append({"event_id": None, "graphs": graphs, "nodes": {owner: node.node_id, other_owner: other.node_id},
                        "t_local": {owner: node.t_local, other_owner: t_burst},
                        "peak_impulse": {owner: node.attributes["peak_impulse"], other_owner: burst_peak},
                        "impulse_similarity": round(similarity, 4), "confidence": round(similarity, 4),
                        "merged_burst_of": other_owner,
                        "evidence": ["{0} recorded a collision; {1} recorded the same impulse as a burst within its "
                                     "contact {2}, merged there by its own sensor".format(owner, other_owner,
                                                                                         other.node_id),
                                     "peak impulses {0} vs {1} N*s (similarity {2:.3f}, tolerance {3:.2f})".format(
                                         node.attributes["peak_impulse"], burst_peak, similarity, cfg.impulse_tolerance),
                                     "consistent with the clock offset between {0} and {1} that earlier matches fix "
                                     "({2:+.3f} s, tolerance {3:.2f} s)".format(owner, other_owner, residual,
                                                                                cfg.clock_tolerance_s)]})
    return matched


def _strength(event: Dict[str, Any]) -> float:
    return max(float(value) for value in event["peak_impulse"].values())


def align_graphs(graphs: Sequence[LocalGraph], cfg: FusionConfig,
                 consistent: Optional[ContactCheck] = None,
                 clock_check: Optional[Callable[[str, float, str, float], Optional[bool]]] = None) -> Alignment:
    matched, rejected = match_collisions(graphs, cfg, consistent, clock_check)
    clocks = {}
    for graph in graphs:
        has_collision = any(node.event_type == "COLLISION" for node in graph.nodes)
        reason = ("its collision report matched no other graph" if has_collision
                  else "it recorded no collision to anchor on")
        clocks[graph.owner] = GraphClock(graph=graph.owner, status=UNALIGNED, reason=reason)
    if not matched:
        return Alignment(reference_event=None, graphs=clocks, matched_events=[], rejected_matches=rejected)

    reference = matched[0]
    for event in matched[1:]:
        if _strength(event) > _strength(reference):
            reference = event
    for owner in reference["graphs"]:
        anchor = reference["t_local"][owner]
        clocks[owner] = GraphClock(graph=owner, status=ALIGNED, anchor_node=reference["nodes"][owner],
                                   anchor_t_local=anchor, offset_to_global=round(-anchor, 4),
                                   reason="reported the reference collision " + reference["event_id"],
                                   chain=[reference["event_id"]], method="matched_collisions")
    frontier = list(reference["graphs"])
    while frontier:
        reached = []
        for event in sorted(matched, key=lambda item: (-_strength(item), item["event_id"])):
            known = [owner for owner in event["graphs"] if owner in frontier]
            new = [owner for owner in event["graphs"] if clocks[owner].status != ALIGNED]
            if len(known) != 1 or len(new) != 1:
                continue
            via, owner = clocks[known[0]], new[0]
            t_global = via.to_global(event["t_local"][known[0]])
            anchor = event["t_local"][owner]
            clocks[owner] = GraphClock(
                graph=owner, status=ALIGNED, anchor_node=event["nodes"][owner], anchor_t_local=anchor,
                offset_to_global=round(t_global - anchor, 4), chain=via.chain + [event["event_id"]],
                reason="shares {0} with {1}, aligned through {2}".format(
                    event["event_id"], known[0], " -> ".join(via.chain + [event["event_id"]])),
                method="matched_collisions")
            reached.append(owner)
        frontier = reached
    for owner, clock in clocks.items():
        if clock.status == UNALIGNED and any(owner in event["graphs"] for event in matched):
            clock.reason = "its matched collisions link it to no graph aligned with the reference"
    return Alignment(reference_event=reference["event_id"], graphs=clocks, matched_events=matched,
                     rejected_matches=rejected)
