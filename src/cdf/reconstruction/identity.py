"""Identity association with the uncertainty each comparison has, and retrospective resolution (no ground
truth).  ``fuse_corrected`` names every anonymous track: another recorder, an anonymous road user (U1, U2, ...)
or UNRESOLVED.

* The radar measurement noise in the common frame grows with range: the declared polar accuracy
  (``fusion.radar_range_std_m``, ``fusion.radar_azimuth_std_deg``) propagated by the Jacobian of
  (range, azimuth) -> (x, y), Sigma_xy = J diag(sigma_r^2, sigma_az^2) J^T (lateral sigma = range x
  sigma_az), on top of the extended-body scatter ``tracking.measurement_std_m``.
* The pose error is a RELATIVE quantity: two tracks of one recorder share its pose error, which cancels in
  their difference except for the heading error turned over their separation; two recorders differ by
  their relative pose error (the mutual refinement's joint posterior when the recorders observe each
  other, else the sum of their declared variances: their correlation is unknown and not assumed).
* A pose error is a slowly varying bias: repeated instants do not average it out, so a positional link
  is identity evidence only when the relative bias can tell two bodies one car width apart
  (3 sigma_bias <= ``semantics.target_width_m``); otherwise the pair stays UNRESOLVED -- a larger
  uncertainty lowers the confidence, it never makes a merge easier.
* Recorder links (``link_to_recorders_corrected``) are conservative: one recorder per observer and instant
  unless same-body evidence (a split of one body, or both tracks on the recorder's own outline) joins the
  two tracks (``anonymous.exclusive_recorder_links``).
* CANNOT_LINK: two simultaneous tracks of one recorder whose returns cannot be one body (the one-box test
  beyond its gate on at least ``fusion.link_min_samples`` instants); the clustering refuses every merge that
  would put a cannot-link pair into one entity, also through a chain of links.
* One-to-one: a link with a rival (a second simultaneous candidate of the same other observer) is kept
  only when its median chi-square is better by at least 2 ln K (``fusion.assignment_likelihood_ratio`` K),
  else both stay UNRESOLVED.
* Operative relevance: cross-recorder identity evidence only where at least one of the two observations
  lies inside its observer's relevance envelope (``relevance_range``).
* A stitch of one observer's two tracks across a gap is a hypothesis against a new road user
  (``stitch_density``); it is resolved only at ``fusion.retrospective_min_posterior``.
* Retrospective resolution (``retrospective_links``): an unresolved entity that ends before an entity seen
  by several observers starts is tested against it by carrying the later entity's first state BACKWARD
  through the gap with the tracker's own motion model (constant velocity, white acceleration
  ``tracking.acceleration_std_mps2``, one prediction per radar sweep), against every other candidate and a
  new-target hypothesis (``fusion.retrospective_new_target_density``); it is resolved only with a posterior
  of at least ``fusion.retrospective_min_posterior``, no cannot-link and no simultaneous track of one
  observer.  Only the identity of existing observations changes: no sample, event or timestamp moves; the
  decision records the time its evidence starts (``identity_resolved_from``) and its posterior.
* Collision evidence (``radar_contact_evidence``): each recorder's own radar view of who arrived at its
  body, tested in the direction the radar observes (``_normal_component_consistent``).
"""

from __future__ import annotations

import math
from dataclasses import replace
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

import numpy as np

from .anonymous import (ANONYMOUS, ASSOCIATED, CROSS, SPLIT, STITCH, PairEvidence, RecorderLink, RoadUserFusion,
                        _heading, _overlap, _third_body_contact, _velocity_sigma, chi2_2dof, collision_continuity_links,
                        covariance_intersection, entity_trajectory, fit_box, pair_evidence, stitch_evidence,
                        build_common_view, _centre_estimate, exclusive_recorder_links)
from .common_frame import CommonSample, CommonTrack, PoseSource, outline_distances
from .config import ReconstructionConfig
from .tracking import kf_predict


# --------------------------------------------------------------------------
# Measurement and pose uncertainty
# --------------------------------------------------------------------------

def radar_covariance(range_m: float, bearing: float, cfg: ReconstructionConfig) -> np.ndarray:
    """Common-frame covariance of one radar position measurement from its declared polar accuracy:
    J diag(sigma_r^2, sigma_az^2) J^T with J the Jacobian of (r, phi) -> (r cos phi, r sin phi)."""
    sigma_r, sigma_az = cfg.fusion.radar_range_std_m, math.radians(cfg.fusion.radar_azimuth_std_deg)
    c, s = math.cos(bearing), math.sin(bearing)
    jacobian = np.array([[c, -range_m * s], [s, range_m * c]])
    return jacobian @ np.diag([sigma_r ** 2, sigma_az ** 2]) @ jacobian.T


def measurement_variance(sample: CommonSample, cfg: ReconstructionConfig) -> float:
    """Per-axis variance of a sample's position measurement: extended-body scatter plus the radar's polar
    noise at the sample's range (the mean of the two principal variances)."""
    line = sample.near - sample.observer
    polar = radar_covariance(float(np.hypot(*line)), math.atan2(line[1], line[0]), cfg)
    return cfg.tracking.measurement_std_m ** 2 + float(np.trace(polar)) / 2.0


class RelativePose:
    """Relative pose uncertainty between recorders (per axis, m^2), from the mutual refinement's joint
    posterior when it ran, else from the declared accuracies (their sum: no correlation is assumed)."""

    def __init__(self, poses: Dict[str, PoseSource], refinement: Optional[Dict[str, Any]] = None) -> None:
        self.declared = {name: float(getattr(source, "position_std_m", 0.0)) for name, source in poses.items()}
        self.yaw = {name: float(getattr(source, "yaw_std_rad", 0.0)) for name, source in poses.items()}
        self.joint: Optional[np.ndarray] = None
        self.index: Dict[str, int] = {}
        if refinement and refinement.get("applied") and refinement.get("covariance_m2"):
            self.joint = np.array(refinement["covariance_m2"], dtype=float)
            self.index = {name: 2 * i for i, name in enumerate(refinement.get("unknowns", []))}

    def block(self, a: str, b: str) -> np.ndarray:
        if self.joint is None or a not in self.index or b not in self.index:
            return np.zeros((2, 2))
        i, j = self.index[a], self.index[b]
        return self.joint[i:i + 2, j:j + 2]

    def variance(self, a: str, b: str) -> float:
        """Per-axis variance of the relative position error of recorders a and b (largest principal value)."""
        if a == b:
            return 0.0
        if self.joint is not None and (a in self.index or b in self.index):
            relative = self.block(a, a) + self.block(b, b) - self.block(a, b) - self.block(b, a)
            if a not in self.index:
                relative = relative + np.eye(2) * self.declared.get(a, 0.0) ** 2
            if b not in self.index:
                relative = relative + np.eye(2) * self.declared.get(b, 0.0) ** 2
            return float(max(np.linalg.eigvalsh(relative)[-1], 0.0))
        return self.declared.get(a, 0.0) ** 2 + self.declared.get(b, 0.0) ** 2


def _ranges(track: CommonTrack) -> float:
    values = [float(np.hypot(*(s.near - s.observer))) for s in track.samples if s.measured]
    return float(np.median(values)) if values else 0.0


def bias_sigma(a: CommonTrack, b: CommonTrack, rel: RelativePose) -> float:
    """The relative pose bias between two tracks (m): position bias of their recorders plus each one's
    heading error turned over the range of its observation (one recorder: over their separation)."""
    if a.recorder == b.recorder:
        return rel.yaw.get(a.recorder, 0.0) * _separation(a, b)
    return math.sqrt(rel.variance(a.recorder, b.recorder) + (rel.yaw.get(a.recorder, 0.0) * _ranges(a)) ** 2
                     + (rel.yaw.get(b.recorder, 0.0) * _ranges(b)) ** 2)


def _separation(a: CommonTrack, b: CommonTrack) -> float:
    gaps = []
    for sa in a.samples:
        if not sa.measured:
            continue
        sb = b.state_at(sa.t_global)
        if sb is not None:
            gaps.append(float(np.hypot(*(sa.point - sb.point))))
    return float(np.median(gaps)) if gaps else 0.0


def corrected(track: CommonTrack, pose_share: float, cfg: ReconstructionConfig, yaw_std: float = 0.0) -> CommonTrack:
    """The track with the variance each sample carries in one comparison: its measurement variance beyond the
    extended-body scatter (the box fit already holds ``box_face_std_m``), its share of the relative pose
    variance and its own heading error turned over its range."""
    def one(s: CommonSample) -> CommonSample:
        polar = measurement_variance(s, cfg) - cfg.tracking.measurement_std_m ** 2
        reach = float(np.hypot(*(s.near - s.observer)))
        return replace(s, pose_var=pose_share + polar + (yaw_std * reach) ** 2)
    return replace(track, samples=[one(s) for s in track.samples])


def discriminable(sigma: float, cfg: ReconstructionConfig) -> bool:
    """Can a positional comparison with this relative bias tell two bodies one car width apart (3 sigma)?"""
    return 3.0 * sigma <= cfg.semantics.target_width_m


# --------------------------------------------------------------------------
# Recorder links with relative uncertainty
# --------------------------------------------------------------------------

def partner_cannot_single_out(track: Any, observer: str, recorder: str, bodies: Mapping[str, Any]) -> bool:
    """Whether ``observer``'s track of ``recorder`` X cannot single X out for ``track``: the observer collided with X,
    and after their first contact the track lies on the observer's own body more often than on X's (both bodies
    from their own pose streams).  From that contact on, the observer's track of X and a track of the observer
    itself are one box; S06: C's track slides from B onto A at the A-B collision and stays on A."""
    own, partner = bodies.get(observer), bodies.get(recorder)
    if own is None or partner is None:
        return False
    contact = min((t for t, partners in own.contacts if recorder in partners), default=math.inf)
    after = [s for s in track.samples if s.measured and s.t_global >= contact
             and own.covers(s.t_global) and partner.covers(s.t_global)]
    on_own = sum(own.outline_distance(s.t_global, s.near) < partner.outline_distance(s.t_global, s.near)
                 for s in after)
    return bool(after) and on_own > len(after) / 2.0


def inherited_links(view: Any, links: Sequence[RecorderLink], cfg: ReconstructionConfig,
                    rel: RelativePose) -> List[RecorderLink]:
    """Recorder identities passed on through another observer's view.  An anonymous track that is the same
    body as a track another observer has identified as recorder X (the one-box and velocity test of
    ``pair_corrected``; a brief overlap must pass at every shared instant) inherits X, provided it is the same
    body as no track identified as any other recorder.  Its own returns may not single X out (X touching a
    third body: both outlines within its uncertainty); the other observer's track of X does.  The usual
    exclusivity per observer and instant applies afterwards (``exclusive_recorder_links``).  An observer's track of
    X passes nothing on to a track that lies on that observer's own body after their contact
    (``partner_cannot_single_out``)."""
    named = {t.name: t.entity for t in view.tracks if t.status == ASSOCIATED and t.entity}
    named.update({link.track: link.recorder for link in links})
    by_name = {t.name: t for t in view.tracks}
    out = []
    for track in view.tracks:
        if track.name in named or track.identity_ambiguous:
            continue
        found: Dict[str, Tuple[PairEvidence, str]] = {}
        for other_name, recorder in named.items():
            other = by_name.get(other_name)
            if other is None or other.recorder == track.recorder or recorder == track.recorder:
                continue
            if partner_cannot_single_out(track, other.recorder, recorder, view.bodies):
                continue
            evidence = pair_corrected(track, other, cfg, rel)
            if evidence is not None and not evidence.accepted and short_overlap(evidence, cfg):
                evidence = pair_corrected(track, other, strict_short(track, other, cfg), rel) or evidence
            if evidence is not None and evidence.accepted:
                best = found.get(recorder)
                if best is None or evidence.compared > best[0].compared:
                    found[recorder] = (evidence, other_name)
        if len(found) != 1:
            continue  # nothing, or the same body as two different recorders: unresolved
        recorder, (evidence, through) = next(iter(found.items()))
        link = RecorderLink(track.name, recorder, evidence.compared, round(evidence.centre_gap_m or 0.0, 3),
                            round(math.sqrt(max(evidence.median_box_chi2 or 0.0, 0.0)), 3),
                            round(math.sqrt(max(evidence.median_velocity_chi2 or 0.0, 0.0)), 3),
                            round(evidence.passed, 3), True)
        link.inherited_from = through  # type: ignore[attr-defined]
        out.append(link)
    return out


def link_to_recorders_corrected(view: Any, cfg: ReconstructionConfig, rel: RelativePose) -> Tuple[List[RecorderLink], List[Dict[str, Any]]]:
    """Per anonymous track, the recorder whose own footprint its returns lie on, at that recorder's own
    velocity: over at least ``link_min_samples`` samples before the recorder's first contact with a third
    body (``anonymous._third_body_contact``), median distance and velocity difference within 2 sigma of the
    pair's relative uncertainty and ``link_min_fraction`` of the samples within 3 sigma; refused when the
    relative pose bias cannot tell two bodies apart, when the track lies off the recorder after that contact,
    or when a second recorder explains it almost as well (``assignment_likelihood_ratio``).  Returns
    (links, refusals)."""
    fusion = cfg.fusion
    links, refusals = [], []
    for track in view.tracks:
        if track.status == ASSOCIATED or track.identity_ambiguous:
            continue
        observer = view.bodies[track.recorder]
        if (track.parent_track is not None
                and any(track.start >= _third_body_contact(observer, body)
                        for name, body in view.bodies.items() if name != track.recorder)):
            continue
        candidates = []
        for name, body in view.bodies.items():
            if name == track.recorder:
                continue
            cut = _third_body_contact(observer, body)
            covered = [s for s in track.samples if s.measured and body.covers(s.t_global)]
            samples = [s for s in covered if s.t_global < cut]
            # A short fragment (fewer samples than the minimum, at least SHORT_FRAGMENT_MIN_SAMPLES) is tested
            # too, but every one of its samples must pass.
            short = SHORT_FRAGMENT_MIN_SAMPLES <= len(samples) < fusion.link_min_samples
            if len(samples) < fusion.link_min_samples and not short:
                continue
            reach = float(np.median([np.hypot(*(s.near - s.observer)) for s in samples]))
            bias2 = rel.variance(track.recorder, name) + (rel.yaw.get(track.recorder, 0.0) * reach) ** 2
            distance, _ = outline_distances(body.poses, body.footprint,
                                            np.array([s.t_global for s in samples]) - body.offset_to_global,
                                            np.array([s.point for s in samples]), inside_zero=True)
            sigma = np.array([math.sqrt(measurement_variance(s, cfg) + bias2) for s in samples])
            speed_gap, speed_sigma = [], []
            for s in samples:
                # The velocity along the observer's line of sight (Doppler); the tangential component, which the
                # radar does not measure, is not tested.
                pose = body.pose_at_global(s.t_global)
                line = s.near - s.observer
                unit = line / max(float(np.hypot(*line)), 1e-6)
                speed_gap.append(abs(float((s.velocity - np.array([pose.vx, pose.vy])) @ unit)))
                speed_sigma.append(_velocity_sigma(cfg, s.vel_std, body.poses.velocity_std_mps))
            speed_gap, speed_sigma = np.array(speed_gap), np.array(speed_sigma)
            within = float(np.mean((distance <= 3.0 * sigma) & (speed_gap <= 3.0 * speed_sigma)))
            accepted = (float(np.median(distance / sigma)) <= 2.0 and float(np.median(speed_gap / speed_sigma)) <= 2.0
                        and within >= (1.0 if short else fusion.link_min_fraction))
            link = RecorderLink(track.name, name, len(samples), round(float(np.median(distance)), 3),
                                round(float(np.median(distance / sigma)), 3), round(float(np.median(speed_gap)), 3),
                                round(within, 3), accepted, None if math.isinf(cut) else round(cut, 4))
            if accepted and not discriminable(math.sqrt(bias2), cfg):
                link.accepted = False
                link.refused = ("UNRESOLVED: relative pose bias {0:.2f} m cannot tell two bodies {1:.1f} m apart"
                                .format(math.sqrt(bias2), cfg.semantics.target_width_m))
                refusals.append({"track": track.name, "recorder": name, "reason": link.refused})
            after = [s for s in covered if s.t_global >= cut]
            if link.accepted and len(after) >= fusion.link_min_samples:
                rest, _ = outline_distances(body.poses, body.footprint,
                                            np.array([s.t_global for s in after]) - body.offset_to_global,
                                            np.array([s.point for s in after]), inside_zero=True)
                rest_sigma = np.array([math.sqrt(measurement_variance(s, cfg) + bias2) for s in after])
                if float(np.median(rest / rest_sigma)) > 3.0:
                    link.accepted = False
                    link.refused = "after {0}'s contact with a third body the track lies off {0}".format(name)
            candidates.append(link)
        accepted = sorted((c for c in candidates if c.accepted), key=lambda c: c.median_distance_sigma)
        if len(accepted) > 1:
            # Two recorders explain the track: it is named only when the best is clearly better.
            gap = accepted[1].median_distance_sigma ** 2 - accepted[0].median_distance_sigma ** 2
            if gap < 2.0 * math.log(cfg.fusion.assignment_likelihood_ratio):
                refusals.append({"track": track.name, "recorder": accepted[0].recorder,
                                 "reason": "UNRESOLVED: also on {0}'s footprint".format(accepted[1].recorder)})
                continue
        links += accepted[:1]
    return links, refusals


# --------------------------------------------------------------------------
# Pairs of anonymous tracks
# --------------------------------------------------------------------------

def split_instants(a: CommonTrack, b: CommonTrack, cfg: ReconstructionConfig, rel: RelativePose) -> Tuple[int, int]:
    """(instants compared, instants where one body is ruled out) for two simultaneous tracks of one recorder,
    with their relative uncertainty (the recorder's pose error cancels)."""
    gate = chi2_2dof(cfg.fusion.anonymous_gate_probability)
    share = 0.5 * bias_sigma(a, b, rel) ** 2
    ca, cb = corrected(a, share, cfg), corrected(b, share, cfg)
    compared = distinct = 0
    for sa in ca.samples:
        if not sa.measured:
            continue
        sb = cb.state_at(sa.t_global)
        if sb is None or not sb.measured:
            continue
        heading = _heading([sa, sb], cfg)
        if heading is None:
            continue
        try:
            fa, fb = fit_box([(a.recorder, sa)], heading, cfg), fit_box([(b.recorder, sb)], heading, cfg)
            joint = fit_box([(a.recorder, sa), (b.recorder, sb)], heading, cfg, start=(fa.centre + fb.centre) / 2.0)
        except (ValueError, np.linalg.LinAlgError):
            continue
        compared += 1
        distinct += int(max(joint.chi2 - fa.chi2 - fb.chi2, 0.0) > gate)
    return compared, distinct


def pair_corrected(a: CommonTrack, b: CommonTrack, cfg: ReconstructionConfig, rel: RelativePose) -> Optional[PairEvidence]:
    """``anonymous.pair_evidence`` on the comparison's own uncertainty; a CROSS pair whose relative pose bias
    cannot separate two bodies stays unresolved."""
    sigma = bias_sigma(a, b, rel)
    if a.recorder == b.recorder:
        share = 0.5 * sigma ** 2
        evidence = pair_evidence(corrected(a, share, cfg), corrected(b, share, cfg), cfg)
    else:
        share = 0.5 * rel.variance(a.recorder, b.recorder)
        evidence = pair_evidence(corrected(a, share, cfg, rel.yaw.get(a.recorder, 0.0)),
                                 corrected(b, share, cfg, rel.yaw.get(b.recorder, 0.0)), cfg)
    if (evidence is not None and not evidence.accepted and evidence.kind == CROSS
            and evidence.compared >= LONG_OVERLAP_FACTOR * cfg.fusion.anonymous_min_shared_samples
            and evidence.passed >= 0.5 and evidence.median_box_chi2 is not None):
        # A long simultaneous observation by two observers: the majority decides (the median instant passes
        # both gates); occasional failures as the visible faces change are expected over a long window.
        gate = chi2_2dof(cfg.fusion.anonymous_gate_probability)
        evidence.accepted = evidence.median_box_chi2 <= gate and evidence.median_velocity_chi2 <= gate
    if evidence is not None and evidence.accepted and evidence.kind == CROSS and not discriminable(sigma, cfg):
        evidence.accepted = False
        evidence.refused = ("UNRESOLVED: relative pose bias {0:.2f} m cannot tell two bodies {1:.1f} m apart"
                            .format(sigma, cfg.semantics.target_width_m))
    return evidence


def stitch_corrected(a: CommonTrack, b: CommonTrack, cfg: ReconstructionConfig) -> Optional[PairEvidence]:
    """``anonymous.stitch_evidence`` with the measurement variance only: across a short gap one recorder's
    pose error is the same slowly varying bias on both sides."""
    return stitch_evidence(corrected(a, 0.0, cfg), corrected(b, 0.0, cfg), cfg)


def refuse_ambiguous_corrected(evidence: Sequence[PairEvidence], tracks: Dict[str, CommonTrack],
                               cfg: ReconstructionConfig) -> None:
    """One-to-one: of rival links (one track, two simultaneous candidates of another observer that are not one
    body) the best is kept only when better by 2 ln K in median chi-square; else every rival is refused.
    A stitch with two successors or predecessors is refused (as in main).  Sets ``posterior`` on each
    accepted link: its share among its candidates and a not-this-road-user hypothesis at the gate."""
    gate = chi2_2dof(cfg.fusion.anonymous_gate_probability)
    margin = 2.0 * math.log(cfg.fusion.assignment_likelihood_ratio)
    accepted = [e for e in evidence if e.accepted]
    one_body = {frozenset((e.a, e.b)) for e in accepted if e.kind == SPLIT}
    refusals: Dict[int, str] = {}
    rivals_of: Dict[int, List[PairEvidence]] = {id(e): [] for e in accepted}
    for e in accepted:
        for other in accepted:
            if other is e:
                continue
            if e.kind == STITCH or other.kind == STITCH:
                if e.kind == STITCH and other.kind == STITCH:
                    if other.a == e.a:
                        refusals[id(e)] = "{0} has two possible successors ({1}, {2})".format(e.a, e.b, other.b)
                    elif other.b == e.b:
                        refusals[id(e)] = "{0} has two possible predecessors ({1}, {2})".format(e.b, e.a, other.a)
                continue
            for mine, partner in ((e.a, e.b), (e.b, e.a)):
                if mine not in (other.a, other.b):
                    continue
                rival = other.b if other.a == mine else other.a
                if (rival != partner and tracks[rival].recorder == tracks[partner].recorder
                        and tracks[rival].recorder != tracks[mine].recorder
                        and _overlap(tracks[rival], tracks[partner])
                        and frozenset((rival, partner)) not in one_body):
                    rivals_of[id(e)].append(other)
                    if other.score - e.score < margin:
                        refusals[id(e)] = ("UNRESOLVED: {0} fits two simultaneous tracks of {1} ({2}, {3}) within "
                                           "a likelihood ratio of {4:g}".format(mine, tracks[partner].recorder, partner,
                                                                                rival, cfg.fusion.assignment_likelihood_ratio))
    for e in accepted:
        terms = [math.exp(-0.5 * max(r.score - e.score, 0.0)) for r in rivals_of[id(e)] if math.isfinite(r.score)]
        null = math.exp(-0.5 * max(gate - e.score, 0.0)) if math.isfinite(e.score) else 1.0
        e.posterior = round(1.0 / (1.0 + sum(terms) + null), 4)  # type: ignore[attr-defined]
        if id(e) in refusals:
            e.accepted, e.refused = False, refusals[id(e)]


def cannot_links(tracks: Sequence[CommonTrack], cfg: ReconstructionConfig, rel: RelativePose) -> Dict[frozenset, Dict[str, Any]]:
    """Pairs of simultaneous tracks of one recorder whose returns cannot be one body on enough instants."""
    out = {}
    for i, a in enumerate(tracks):
        for b in tracks[i + 1:]:
            if a.recorder != b.recorder or not _overlap(a, b):
                continue
            compared, distinct = split_instants(a, b, cfg, rel)
            if distinct >= cfg.fusion.link_min_samples:
                out[frozenset((a.name, b.name))] = {"a": a.name, "b": b.name, "compared": compared,
                                                    "distinct": distinct,
                                                    "evidence": "one recorder measured both at once, not one body"}
    return out


def cluster_corrected(tracks: Sequence[CommonTrack], evidence: Sequence[PairEvidence],
                      cannot: Dict[frozenset, Dict[str, Any]]) -> Tuple[List[List[CommonTrack]], List[PairEvidence]]:
    """Accepted links joined best first; a merge is refused when it would put a cannot-link pair, or two
    simultaneous tracks of one recorder not shown to be one body, into one entity."""
    parent = {track.name: track.name for track in tracks}
    one_body = {frozenset((e.a, e.b)) for e in evidence if e.accepted and e.kind == SPLIT}

    def root(name: str) -> str:
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    def conflict(x: CommonTrack, y: CommonTrack) -> bool:
        pair = frozenset((x.name, y.name))
        if pair in cannot:
            return True
        return x.recorder == y.recorder and _overlap(x, y) and pair not in one_body

    members = {track.name: [track] for track in tracks}
    used = []
    for item in sorted((e for e in evidence if e.accepted), key=lambda e: (e.score, e.a, e.b)):
        ra, rb = root(item.a), root(item.b)
        if ra == rb:
            continue
        if any(conflict(x, y) for x in members[ra] for y in members[rb]):
            item.refused = "CANNOT_LINK: would join tracks a recorder measured as two bodies (or two simultaneous tracks of one recorder)"
            item.accepted = False
            continue
        parent[rb] = ra
        members[ra] += members.pop(rb)
        used.append(item)
    groups = [sorted(group, key=lambda t: (t.start, t.name)) for name, group in members.items() if root(name) == name]
    return sorted(groups, key=lambda group: (group[0].start, group[0].name)), used


# --------------------------------------------------------------------------
# Retrospective identity resolution
# --------------------------------------------------------------------------

def chi2_4dof(probability: float) -> float:
    """Quantile of the chi-square distribution with 4 degrees of freedom: exp(-x/2)(1 + x/2) = 1 - p."""
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if math.exp(-mid / 2.0) * (1.0 + mid / 2.0) > 1.0 - probability:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0



def _state(group: Sequence[CommonTrack], t: float, cfg: ReconstructionConfig, rel: RelativePose) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]]:
    """(centre, its covariance, velocity, its covariance, observers) of a group at one of its measured instants,
    from each observer's centre estimate on its corrected samples (measurement uncertainty only), combined by
    covariance intersection."""
    floor = cfg.tracking.radial_speed_std_mps
    estimates, velocities, observers = [], [], []
    for track in group:
        s = track.at(t, tolerance=0.026)
        if s is None or not s.measured:
            continue
        s = corrected(CommonTrack(track.recorder, track.track_id, [s]), 0.0, cfg).samples[0]
        centre, cov = _centre_estimate(track.recorder, s, _heading([s], cfg), cfg)
        estimates.append((centre, cov))
        velocities.append((s.velocity, np.eye(2) * max(s.vel_std, floor) ** 2))
        observers.append(track.recorder)
    if not estimates:
        return None
    centre, cov = covariance_intersection(estimates)
    velocity, vcov = covariance_intersection(velocities)
    return centre, cov, velocity, vcov, observers


def _measured_times(group: Sequence[CommonTrack]) -> List[float]:
    return sorted({s.t_global for t in group for s in t.samples if s.measured})


def backward_test(old: Sequence[CommonTrack], new: Sequence[CommonTrack], cfg: ReconstructionConfig,
                  rel: RelativePose) -> Optional[Dict[str, Any]]:
    """Carry the later group's first state back to the earlier group's last measured instant with the tracker's
    motion model (one constant-velocity prediction per radar sweep, white acceleration
    ``tracking.acceleration_std_mps2``; the model is time-reversible) and compare: 4-dof chi-square of centre and
    velocity, and the Gaussian likelihood density of the miss (1/m^2 per (m/s)^2)."""
    old_times, new_times = _measured_times(old), _measured_times(new)
    if not old_times or not new_times:
        return None
    t_old, t_new = old_times[-1], new_times[0]
    gap = t_new - t_old
    if gap <= 0.0:
        return None
    a = _state(old, t_old, cfg, rel)
    b = _state(new, t_new, cfg, rel)
    if a is None or b is None:
        return None
    centre_a, cov_a, vel_a, vcov_a, obs_a = a
    centre_b, cov_b, vel_b, vcov_b, obs_b = b
    # Backward: the reversed constant-velocity model from t_new to t_old.
    x = np.array([centre_b[0], centre_b[1], -vel_b[0], -vel_b[1]])
    P = np.zeros((4, 4))
    P[:2, :2], P[2:, 2:] = cov_b, vcov_b
    step = 0.05
    remaining = gap
    while remaining > 1e-9:
        dt = min(step, remaining)
        x, P = kf_predict(x, P, dt, cfg.tracking.acceleration_std_mps2)
        remaining -= dt
    predicted = np.array([x[0], x[1], -x[2], -x[3]])
    observed = np.array([centre_a[0], centre_a[1], vel_a[0], vel_a[1]])
    flip = np.diag([1.0, 1.0, -1.0, -1.0])
    S = flip @ P @ flip
    S[:2, :2] += cov_a
    S[2:, 2:] += vcov_a
    # Different observers: their relative pose bias enters the position (largest pair).
    pose = max((rel.variance(p, q) for p in set(obs_a) for q in set(obs_b)), default=0.0)
    S[:2, :2] += np.eye(2) * pose
    miss = observed - predicted
    chi2 = float(miss @ np.linalg.solve(S, miss))
    density = math.exp(-0.5 * chi2) / ((2.0 * math.pi) ** 2 * math.sqrt(max(np.linalg.det(S), 1e-300)))
    return {"gap_s": round(gap, 3), "chi2": round(chi2, 3), "density": density, "t_old": t_old, "t_new": t_new,
            "position_sigma_m": round(math.sqrt(max(np.linalg.eigvalsh(S[:2, :2])[-1], 0.0)), 3),
            "velocity_sigma_mps": round(math.sqrt(max(np.linalg.eigvalsh(S[2:, 2:])[-1], 0.0)), 3)}


def retrospective_links(groups: List[List[CommonTrack]], cannot: Dict[frozenset, Dict[str, Any]],
                        cfg: ReconstructionConfig, rel: RelativePose,
                        links: Optional[Sequence[PairEvidence]] = None) -> Tuple[List[List[CommonTrack]], List[Dict[str, Any]]]:
    """Join an earlier entity to a later strongly identified one when the backward test singles it out, and the
    earlier one ended with no other observed road user within confusion distance (``confusable_neighbours``)."""
    fusion = cfg.fusion
    gate = chi2_4dof(fusion.anonymous_gate_probability)
    null = fusion.retrospective_new_target_density
    horizon = cfg.semantics.prediction_horizon_s

    full_links = None if links is None else [e for e in links if e.accepted and e.kind == CROSS
                                             and e.compared >= fusion.anonymous_min_shared_samples]

    def strong(group: Sequence[CommonTrack]) -> bool:
        # Seen by several observers, joined by a cross-observer link compared on at least the shared-instant
        # minimum (``links``: the joining evidence; without it, any two observers): a brief overlap may join two
        # fragments but does not anchor a backward resolution.
        if full_links is None:
            return len({t.recorder for t in group}) >= 2
        names = {t.name for t in group}
        return any(e.a in names and e.b in names for e in full_links)

    def compatible(x: Sequence[CommonTrack], y: Sequence[CommonTrack]) -> bool:
        for p in x:
            for q in y:
                if frozenset((p.name, q.name)) in cannot:
                    return False
                if p.recorder == q.recorder and _overlap(p, q):
                    return False
        return True

    decisions: List[Dict[str, Any]] = []
    merged = True
    while merged:
        merged = False
        ends = [(i, max(_measured_times(g) or [math.inf])) for i, g in enumerate(groups)]
        starts = [(j, min(_measured_times(g) or [-math.inf])) for j, g in enumerate(groups)]
        proposals = []
        for i, end in ends:
            old = groups[i]
            candidates = []
            for j, start in starts:
                if j == i or not strong(groups[j]) or not (0.0 < start - end <= horizon):
                    continue
                if not compatible(old, groups[j]):
                    continue
                test = backward_test(old, groups[j], cfg, rel)
                if test is None or test["chi2"] > gate:
                    continue
                candidates.append((j, test))
            if not candidates:
                continue
            ratios = [(j, test, test["density"] / null) for j, test in candidates]
            total = 1.0 + sum(r for _, _, r in ratios)
            j, test, ratio = max(ratios, key=lambda item: item[2])
            # The later entity may also continue ANOTHER earlier one: every earlier entity that passes the backward
            # test into it competes too (one-to-one, as two possible predecessors of a stitch).
            start_j = dict(starts)[j]
            rivals, rival_records = [], []
            for k, end_k in ends:
                if k in (i, j) or not (0.0 < start_j - end_k <= horizon) or not compatible(groups[k], groups[j]):
                    continue
                other = backward_test(groups[k], groups[j], cfg, rel)
                if other is not None and other["chi2"] <= gate:
                    rivals.append(other["density"] / null)
                    rival_records.append({"earlier": [t.name for t in groups[k]], "chi2": other["chi2"],
                                          "ratio": round(other["density"] / null, 3)})
            posterior = min(ratio / total, ratio / (1.0 + ratio + sum(rivals)))
            everyone = [t for g in groups for t in g]
            crowd = confusable_neighbours(old, end, everyone, cfg, rel, [t.name for t in groups[j]])
            record = {"earlier": [t.name for t in old], "later": [t.name for t in groups[j]],
                      "posterior": round(posterior, 4), "candidates": len(candidates), "ratio": round(ratio, 3),
                      "rival_predecessors": len(rivals), "rivals": rival_records, **{k: test[k] for k in
                      ("gap_s", "chi2", "position_sigma_m", "velocity_sigma_mps", "t_old", "t_new")}}
            if crowd:
                record["resolved"] = False
                record["reason"] = ("UNRESOLVED: when it was last measured, {0} was within two car widths of it"
                                    .format(", ".join(crowd)))
                decisions.append(record)
            elif posterior >= fusion.retrospective_min_posterior:
                proposals.append((posterior, i, j, record))
            else:
                record["resolved"] = False
                record["reason"] = "UNRESOLVED: posterior {0:.3f} below {1:g}".format(posterior, fusion.retrospective_min_posterior)
                decisions.append(record)
        for posterior, i, j, record in sorted(proposals, key=lambda item: -item[0]):
            record["resolved"] = True
            decisions.append(record)
            groups[j] = sorted(groups[j] + groups[i], key=lambda t: (t.start, t.name))
            groups.pop(i)
            merged = True
            break  # recompute with the joined entity
    unique, seen = [], set()
    for d in decisions:
        key = (tuple(d["earlier"]), tuple(d["later"]), d.get("resolved"))
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return sorted(groups, key=lambda group: (group[0].start, group[0].name)), unique


# --------------------------------------------------------------------------
# The whole step
# --------------------------------------------------------------------------

def fuse_corrected(locals_: Sequence[Any], alignment: Any, associations: List[Any], poses: Dict[str, PoseSource],
                   cfg: ReconstructionConfig, refinement: Optional[Dict[str, Any]] = None) -> RoadUserFusion:
    """Recorder links, anonymous road users and their fused trajectories (module docstring)."""
    rel = RelativePose(poses, refinement)
    view = build_common_view(locals_, alignment, associations, poses)
    links, link_refusals = link_to_recorders_corrected(view, cfg, rel)
    links += collision_continuity_links(view, associations, alignment, links, cfg)
    links += inherited_links(view, links, cfg, rel)
    links, exclusive = exclusive_recorder_links(view, links, cfg)
    link_refusals = list(link_refusals) + [{"track": r["track"], "reason": r["reason"]} for r in exclusive]
    by_key = {(a.local_graph, a.local_track): a for a in associations}
    for link in links:
        recorder, track_id = link.track.split(":", 1)
        item = by_key[(recorder, track_id)]
        item.status, item.global_entity, item.candidate = ASSOCIATED, link.recorder, link.recorder
        item.confidence = link.fraction_within
        item.blocking = []
        if getattr(link, "inherited_from", None):
            item.collision_event = None
            item.evidence = list(item.evidence) + [
                "same body as {0} (identified as {1}): one box and one velocity on {2} shared instants, {3:.0%} "
                "within the gates; the same body as no track of another recorder".format(
                    link.inherited_from, link.recorder, link.samples, link.fraction_within)]
        elif not link.collision_anchored:
            item.collision_event = None
            item.evidence = list(item.evidence) + [
                "common frame: its returns lie on {0}'s own footprint (median {1:.2f} m, {2:.2f} sigma of the relative "
                "uncertainty, over {3} samples; {4:.0%} within 3 sigma) at {0}'s own velocity".format(
                    link.recorder, link.median_distance_m, link.median_distance_sigma, link.samples, link.fraction_within)]
        else:
            item.evidence = list(item.evidence) + ["short impact segment identity anchored by the matched collision"]
        item.source_graphs = sorted(set(item.source_graphs) | {recorder, link.recorder})
    for refusal in link_refusals:
        recorder, track_id = refusal["track"].split(":", 1)
        by_key[(recorder, track_id)].evidence.append(refusal["reason"] + " (recorder link refused)")
    linked = {link.track for link in links}
    anonymous = [t for t in view.tracks if t.status != ASSOCIATED and t.name not in linked]
    by_name = {t.name: t for t in anonymous}
    evidence: List[PairEvidence] = []
    relevant = {t.name: relevant_samples(t, view.bodies, cfg) for t in anonymous}
    resolved_at: Dict[frozenset, float] = {}
    for i, a in enumerate(anonymous):
        for b in anonymous[i + 1:]:
            if a.recorder != b.recorder:
                # Operative relevance: cross-recorder identity evidence only where at least one of the two
                # observations lies inside its observer's relevance envelope (TRUSTED_FOR_FUSION).
                ra, rb = relevant_view(a, relevant[a.name], relevant[b.name], b), relevant_view(b, relevant[b.name], relevant[a.name], a)
                item = pair_corrected(ra, rb, cfg, rel)
                when = resolution_time(ra, rb, cfg)
                if item is None or not item.accepted:
                    # Superposition: two observers seeing one body at the same instants, also where neither needs
                    # it (a car driving away from a stopped wreck): the same one-box and velocity test on every
                    # instant both observe, with the same thresholds.  Its noise grows with range, so a far pair
                    # passes only when the bodies coincide within that noise.
                    full = pair_corrected(a, b, cfg, rel)
                    short = full is not None and short_overlap(full, cfg)
                    if short:
                        # The two observations overlap too briefly to ever reach the shared-instant minimum (a road
                        # user glimpsed while another observer keeps it): every shared instant must pass.
                        full = pair_corrected(a, b, strict_short(a, b, cfg), rel) or full
                    if full is not None and full.accepted:
                        item = full
                        when = resolution_time(a, b, strict_short(a, b, cfg) if short else cfg)
                    elif item is None:
                        item = full
                if when is not None:
                    resolved_at[frozenset((a.name, b.name))] = when
            elif _overlap(a, b):
                item = pair_corrected(a, b, cfg, rel)
            else:
                first, second = (a, b) if (a.start, a.name) <= (b.start, b.name) else (b, a)
                item = stitch_corrected(first, second, cfg)
                if item is not None and item.accepted:
                    # A stitch is a hypothesis against a new road user AND against every other observed road user
                    # that could have reached that place (``rival_density``: in dense traffic the re-acquired track
                    # is as likely another known car): the density of the miss under the tracker's own motion
                    # model across the gap over the sum of the alternatives; resolved only at the minimum
                    # posterior.  A long gap, a large miss or a rival nearby makes it UNRESOLVED, never easier.
                    density = stitch_density(first, second, cfg)
                    rivals, rival_names = rival_density(first, second, view.tracks, cfg, rel)
                    posterior = density / max(density + cfg.fusion.retrospective_new_target_density + rivals, 1e-300)
                    item.posterior = round(posterior, 4)  # type: ignore[attr-defined]
                    end = max((s.t_global for s in first.samples if s.measured), default=first.end)
                    crowd = confusable_neighbours([first], end, view.tracks, cfg, rel, [second.name])
                    if crowd:
                        item.accepted = False
                        item.refused = ("UNRESOLVED: when {0} was last measured, {1} was within two car widths of it: "
                                        "across the {2:.2f} s gap nothing tells which came back".format(
                                            first.name, ", ".join(crowd), item.gap_s or 0.0))
                    elif posterior < cfg.fusion.retrospective_min_posterior:
                        item.accepted = False
                        against = "a new road user" + (" or {0}".format(", ".join(rival_names)) if rival_names else "")
                        item.refused = ("UNRESOLVED: across the {0:.2f} s gap the re-acquisition is not singled out "
                                        "against {1} (posterior {2:.3f})".format(item.gap_s or 0.0, against, posterior))
            if item is not None:
                evidence.append(item)
    refuse_ambiguous_corrected(evidence, by_name, cfg)
    cannot = cannot_links(anonymous, cfg, rel)
    groups, used = cluster_corrected(anonymous, evidence, cannot)
    groups, retro = retrospective_links(groups, cannot, cfg, rel, used)
    resolved_late = {}
    for d in retro:
        if d.get("resolved"):
            for name in d["earlier"]:
                resolved_late[name] = d
    entities, names = [], {}
    for number, group in enumerate(groups, 1):
        entity_id = "U{0}".format(number)
        members = {t.name for t in group}
        states, footprint = entity_trajectory(group, cfg)
        joins = [e for e in used if e.a in members and e.b in members]
        posteriors = [getattr(e, "posterior", None) for e in joins]
        posteriors += [d["posterior"] for d in retro if d.get("resolved") and set(d["earlier"]) <= members]
        confidence = round(min(p for p in posteriors if p is not None), 4) if any(p is not None for p in posteriors) else None
        names.update({(t.recorder, t.track_id): entity_id for t in group})
        entities.append({"id": entity_id, "anonymous": True,
                         "identity_ambiguous": any(t.identity_ambiguous for t in group),
                         "source_tracks": [t.name for t in group],
                         "source_track_segments": [{"track": t.name, "observer": t.recorder,
                                                    "t_global": [round(t.start, 3), round(t.end, 3)]} for t in group],
                         "observers": sorted({t.recorder for t in group}),
                         "time_span": [round(min(t.start for t in group), 3), round(max(t.end for t in group), 3)],
                         "association": {"links": [dict(e.to_dict(), score=round(e.score, 3),
                                                        posterior=getattr(e, "posterior", None)) for e in joins],
                                         "retrospective": [d for d in retro if d.get("resolved") and set(d["earlier"]) <= members],
                                         "confidence": confidence},
                         "fusion_method": "+".join(sorted({s["method"] for s in states})), "footprint": footprint,
                         "relevance": entity_relevance(group, view.bodies, cfg),
                         "timeline": entity_timeline(group, joins, retro, resolved_at, view, locals_, cfg),
                         "trajectory": states})
        for track in group:
            item = by_key[(track.recorder, track.track_id)]
            item.global_entity = entity_id
            item.identity_confidence = confidence if len(group) > 1 else None
            late = resolved_late.get(track.name)
            if late is not None:
                item.retrospective = True
                item.identity_resolved_from = late["t_new"]
                item.identity_confidence = late["posterior"]
                item.evidence = list(item.evidence) + [
                    "retrospective: identity resolved from later evidence at {0:+.2f} s (entity seen by several "
                    "observers), carried back {1:.2f} s with the motion model; posterior {2:.3f} against {3} candidate(s) "
                    "and a new road user; observation times unchanged".format(late["t_new"], late["gap_s"],
                                                                                late["posterior"], late["candidates"])]
            if late is None and len(group) > 1:
                times = [resolved_at[frozenset((e.a, e.b))] for e in joins
                         if track.name in (e.a, e.b) and frozenset((e.a, e.b)) in resolved_at]
                if times and min(times) > track.start + 1e-6:
                    # Its identity follows from evidence that starts after its first observation: resolved later,
                    # the observation itself unchanged.
                    item.retrospective = True
                    item.identity_resolved_from = round(min(times), 4)
            item.evidence = list(item.evidence) + [
                "anonymous road user {0}: {1}".format(entity_id, ", ".join(t.name for t in group))]
    result = RoadUserFusion(links, evidence, entities, {owner: source.name for owner, source in poses.items()}, names)
    result.cannot_links = list(cannot.values())  # type: ignore[attr-defined]
    result.retrospective = retro  # type: ignore[attr-defined]
    return result


# --------------------------------------------------------------------------
# Collision association: pose-free radar evidence ("I see who hit me")
# --------------------------------------------------------------------------

def radar_contact_evidence(locals_: Sequence[Any], cfg: ReconstructionConfig):
    """A check for ``alignment.match_collisions``: does the reporting recorder's own radar
    show the candidate partner arriving at its body?  For a candidate pairing (O's report at t_O, P's report at
    t_P), per side: O's non-ambiguous tracks touching O's footprint at the report (a measured sample within
    ``fusion.contact_window_s`` before it, clearance <= ``fusion.touching_clearance_m``) that ARRIVED during the
    last ``fusion.approach_window_s`` (clearance at its start beyond the touching clearance + 3 sigma of the
    measurement: a body already in contact, an earlier partner, says nothing about who arrived now) and were
    still closing in the last 0.2 s.  Their motion is compared with P's OWN recorded speed at the mapped
    instants (t - t_O + t_P: the clock offset the candidate implies) in the direction O's radar observes
    (``_normal_component_consistent``).  Everything is in O's own frame and P's own speed: no pose stream,
    no GNSS.  Returns per candidate True
    (some side supports it, none contradicts), False (a side has touching approaching tracks and none
    moves like P: contradicted) or None (no radar sees the contact)."""
    by_owner = {local.owner: local for local in locals_}
    fusion = cfg.fusion

    def side(observer: str, t_o: float, partner: str, t_p: float) -> Optional[bool]:
        local, other = by_owner[observer], by_owner[partner]
        touching = []
        for track in local.tracks:
            if track.identity_ambiguous:
                continue
            window = [s for s in track.samples if s.measured and t_o - fusion.approach_window_s - 1e-6 <= s.t_local <= t_o + 1e-6]
            if len(window) < 2:
                continue
            near = [s for s in window if t_o - fusion.contact_window_s - 1e-6 <= s.t_local and s.clearance_m <= fusion.touching_clearance_m]
            # Arriving: outside the contact zone (beyond the touching clearance by 3 sigma of the measurement)
            # when the window starts, touching at the report.  A body already in contact (an earlier partner
            # stuck to the recorder) says nothing about who arrived now.
            arriving = window[0].clearance_m > fusion.touching_clearance_m + 3.0 * cfg.tracking.measurement_std_m
            if not near or not arriving:
                continue
            # The body that hit the recorder was still closing in the last 0.2 s before the report (4 radar
            # sweeps): one passing alongside, whose clearance no longer shrinks, did not arrive now.
            last = [x for x in window if x.t_local >= t_o - 0.2 - 1e-6]
            if len(last) < 2 or last[-1].clearance_m >= last[0].clearance_m:
                continue
            verdict = _normal_component_consistent(local, other, window, t_o, t_p, cfg)
            if verdict is not None:
                touching.append(verdict)
        if not touching:
            return None
        return any(touching)

    def check(a: str, ta: float, b: str, tb: float) -> Optional[bool]:
        sides = [side(a, ta, b, tb), side(b, tb, a, ta)]
        if any(value is False for value in sides):
            return False
        return True if any(value is True for value in sides) else None
    return check


# --------------------------------------------------------------------------
# Reconstruction relevance range (sensor range is not relevance)
# --------------------------------------------------------------------------

def relevance_range(ego_speed: float, closing_speed: float, velocity_std: float, position_std: float,
                    cfg: ReconstructionConfig) -> float:
    """Clearance below which a target can become a conflict within the prediction horizon (conflict model):
    d_rel = d_min(v_ego) + max(v_close + 3 sigma_v, 0) x H + 3 sigma_pos, with d_min the safe following distance
    of the recorder's speed (``conflict.safe_following_distance``: UN R157 time gap, 2 m floor), v_close the
    rate at which the clearance shrinks, H ``semantics.prediction_horizon_s``.  A far target that does not close
    in stays outside; one closing fast becomes relevant earlier; uncertainty widens it."""
    from .conflict import safe_following_distance
    _, _, d_min = safe_following_distance(max(ego_speed, 0.0), cfg.semantics)
    return d_min + max(closing_speed + 3.0 * velocity_std, 0.0) * cfg.semantics.prediction_horizon_s + 3.0 * position_std


def entity_relevance(group: Sequence[CommonTrack], bodies: Dict[str, Any], cfg: ReconstructionConfig) -> Dict[str, Any]:
    """When an entity first lies within its observers' relevance range, and its smallest clearance-to-range ratio."""
    first, ratio = None, math.inf
    for track in group:
        body = bodies.get(track.recorder)
        if body is None:
            continue
        for s in track.samples:
            if not s.measured:
                continue
            pose = body.pose_at_global(s.t_global)
            line = s.near - s.observer
            clearance = float(np.hypot(*line))
            unit = line / max(clearance, 1e-6)
            closing = -float((s.velocity - np.array([pose.vx, pose.vy])) @ unit)
            limit = relevance_range(math.hypot(pose.vx, pose.vy), closing, s.vel_std,
                                    math.sqrt(measurement_variance(s, cfg)), cfg)
            ratio = min(ratio, clearance / max(limit, 1e-6))
            if clearance <= limit and (first is None or s.t_global < first):
                first = s.t_global
    return {"relevant_from_t_global": None if first is None else round(first, 3),
            "min_clearance_to_relevance_range": None if math.isinf(ratio) else round(ratio, 3)}



# --------------------------------------------------------------------------
# Observable-direction collision evidence, operative relevance, target timelines
# --------------------------------------------------------------------------

def _normal_component_consistent(local: Any, other: Any, window: Sequence[Any], t_o: float, t_p: float,
                                 cfg: ReconstructionConfig) -> Optional[bool]:
    """Is the arriving track's motion compatible with the partner's own speed, in the direction the radar
    observes?  The component of the target's ground velocity along the outward normal of the observer's body
    at the target's near point (the line of sight of the radar that sees it arrive: Doppler) is the observed
    one; a partner whose own speed is below that component by more than 3 sigma (Doppler noise and the track's
    velocity uncertainty) cannot be the arriving body, nor can one faster than the track's whole ground speed by
    3 sigma (the body did not move that fast at all).  The tangential component, poorly observed by a radar,
    can only add to the track's speed and never turns a slower true partner into a contradiction.  Majority over the window; None without enough comparable samples."""
    from .tracking import EgoFootprint  # noqa: F401  (type only)
    fp = local.footprint
    verdicts = []
    for s in window:
        t_partner = s.t_local - t_o + t_p
        if not (other.ego.start <= t_partner <= other.ego.end):
            continue
        own = local.ego.at(s.t_local)
        c, sn = math.cos(own.heading), math.sin(own.heading)
        ego_vx, ego_vy = c * own.vx + sn * own.vy, -sn * own.vx + c * own.vy  # recorder velocity, its own axes
        gx, gy = s.relative_vx_mps + ego_vx, s.relative_vy_mps + ego_vy        # target ground velocity, same axes
        if fp is not None:
            nx, ny = fp.outward(s.longitudinal_m, s.lateral_m)
        else:
            norm = max(math.hypot(s.longitudinal_m, s.lateral_m), 1e-6)
            nx, ny = s.longitudinal_m / norm, s.lateral_m / norm
        observed = abs(gx * nx + gy * ny)
        sigma = math.sqrt(cfg.tracking.radial_speed_std_mps ** 2 + s.vel_std_mps ** 2)
        partner = other.ego.at(t_partner).speed
        # Too slow for the observed (Doppler) component, or faster than the observed body moves at all.
        verdicts.append(observed - 3.0 * sigma <= partner <= math.hypot(gx, gy) + 3.0 * sigma)
    if len(verdicts) < max(3, len(window) // 2):
        return None
    return sum(verdicts) * 2 >= len(verdicts)


def relevant_samples(track: CommonTrack, bodies: Dict[str, Any], cfg: ReconstructionConfig) -> List[bool]:
    """Per sample, inside its observer's relevance envelope (``relevance_range``)?"""
    body = bodies.get(track.recorder)
    out = []
    for s in track.samples:
        if body is None or not s.measured:
            out.append(False)
            continue
        pose = body.pose_at_global(s.t_global)
        line = s.near - s.observer
        clearance = float(np.hypot(*line))
        unit = line / max(clearance, 1e-6)
        closing = -float((s.velocity - np.array([pose.vx, pose.vy])) @ unit)
        limit = relevance_range(math.hypot(pose.vx, pose.vy), closing, s.vel_std,
                                math.sqrt(measurement_variance(s, cfg)), cfg)
        out.append(clearance <= limit)
    return out


def relevant_view(track: CommonTrack, flags: Sequence[bool], other_flags: Sequence[bool], other: CommonTrack) -> CommonTrack:
    """The track with only the instants usable as fusion evidence measured: its own sample relevant, or the
    other observer's simultaneous sample relevant (one of the two observers needs the road user)."""
    other_times = [s.t_global for s, ok in zip(other.samples, other_flags) if ok]

    def usable(s: CommonSample, ok: bool) -> bool:
        return ok or any(abs(s.t_global - t) <= 0.026 for t in other_times)
    return replace(track, samples=[s if (s.measured and usable(s, ok)) else replace(s, measured=False)
                                   for s, ok in zip(track.samples, flags)])


LONG_OVERLAP_FACTOR = 3  # a cross-observer overlap this many times the shared-instant minimum is decided by majority
SHORT_FRAGMENT_MIN_SAMPLES = 5  # fewest instants a short fragment is tested on (a quarter second at 20 Hz)


def short_overlap(evidence: PairEvidence, cfg: ReconstructionConfig) -> bool:
    """The pair was compared on every instant both observers measured, and those are fewer than
    ``fusion.anonymous_min_shared_samples`` (it can never reach the minimum) but at least
    ``SHORT_FRAGMENT_MIN_SAMPLES``."""
    return SHORT_FRAGMENT_MIN_SAMPLES <= evidence.compared < cfg.fusion.anonymous_min_shared_samples


def strict_short(a: CommonTrack, b: CommonTrack, cfg: ReconstructionConfig) -> ReconstructionConfig:
    """The pair test for a short fragment: at least ``SHORT_FRAGMENT_MIN_SAMPLES`` shared instants, every one
    must pass."""
    return replace(cfg, fusion=replace(cfg.fusion, anonymous_min_shared_samples=SHORT_FRAGMENT_MIN_SAMPLES,
                                       anonymous_pass_fraction=1.0))


def resolution_time(a: CommonTrack, b: CommonTrack, cfg: ReconstructionConfig) -> Optional[float]:
    """When the evidence for a pair reaches ``fusion.anonymous_min_shared_samples`` usable shared instants."""
    times = []
    for sa in a.samples:
        if not sa.measured:
            continue
        sb = b.state_at(sa.t_global)
        if sb is not None and sb.measured:
            times.append(sa.t_global)
    need = cfg.fusion.anonymous_min_shared_samples
    return times[need - 1] if len(times) >= need else None


def entity_timeline(group: Sequence[CommonTrack], joins: Sequence[PairEvidence], retro: Sequence[Dict[str, Any]],
                    resolved_at: Dict[frozenset, float], view: Any, locals_: Sequence[Any],
                    cfg: ReconstructionConfig) -> Dict[str, Any]:
    """first_detected / first_tracked / first_relevant / first_identity_resolved / first_hazard_relevant of an
    entity (t_global).  Observation times are the tracks' own; resolution times come after them."""
    detected = min(t.start for t in group)
    tracked = []
    for t in group:
        measured = [s.t_global for s in t.samples if s.measured]
        if len(measured) >= cfg.tracking.min_track_updates:
            tracked.append(measured[cfg.tracking.min_track_updates - 1])
    relevance = entity_relevance(group, view.bodies, cfg)
    members = {t.name for t in group}
    resolutions = [resolved_at[frozenset((e.a, e.b))] for e in joins if frozenset((e.a, e.b)) in resolved_at]
    resolutions += [d["t_new"] for d in retro if d.get("resolved") and set(d["earlier"]) <= members]
    hazards = []
    by_owner = {local.owner: local for local in locals_}
    for t in group:
        local, body = by_owner.get(t.recorder), view.bodies.get(t.recorder)
        if local is None or body is None:
            continue
        for node in local.graph.nodes:
            if node.event_type == "CRITICAL_TTC_START" and node.subject_id == t.track_id:
                hazards.append(round(node.t_local + body.offset_to_global, 4))
    return {"first_detected": round(detected, 4),
            "first_tracked": round(min(tracked), 4) if tracked else None,
            "first_relevant": relevance["relevant_from_t_global"],
            "first_identity_resolved": round(min(resolutions), 4) if resolutions else None,
            "first_hazard_relevant": min(hazards) if hazards else None}


def stitch_density(first: CommonTrack, second: CommonTrack, cfg: ReconstructionConfig,
                   pose_var: float = 0.0) -> float:
    """Gaussian density (1/m^2 per (m/s)^2) of a re-acquisition under the stitch test's own model
    (``anonymous.stitch_evidence``: centre carried across the gap at constant velocity, white acceleration
    ``tracking.acceleration_std_mps2`` over the gap, the two centre estimates' covariances; velocity difference
    against both uncertainties plus the acceleration over the gap), on the measurement uncertainty only (one
    recorder's pose bias is common to both sides; ``pose_var``: the relative pose variance per axis when the two
    tracks are of different recorders).  A long gap spreads it: the density falls.  ``first`` may still be
    observed when ``second`` starts: its last measured state up to then is carried over the remaining gap."""
    a, b = corrected(first, 0.0, cfg), corrected(second, 0.0, cfg)
    nxt = next((s for s in b.samples if s.measured), None)
    if nxt is None:
        return 0.0
    last = next((s for s in reversed(a.samples) if s.measured and s.t_global <= nxt.t_global + 1e-6), None)
    if last is None:
        return 0.0
    gap = nxt.t_global - last.t_global
    if gap < 0.0:
        return 0.0
    ca, pa = _centre_estimate(a.recorder, last, _heading([last], cfg), cfg)
    cb, pb = _centre_estimate(b.recorder, nxt, _heading([nxt], cfg), cfg)
    sigma_a = cfg.tracking.acceleration_std_mps2
    cov = pa + pb + np.eye(2) * ((sigma_a * gap ** 2 / 2.0) ** 2 + (last.vel_std * gap) ** 2 + pose_var)
    miss = cb - (ca + last.velocity * gap)
    var_v = _velocity_sigma(cfg, nxt.vel_std, last.vel_std) ** 2 + (sigma_a * gap) ** 2
    dv = nxt.velocity - last.velocity
    pos = math.exp(-0.5 * float(miss @ np.linalg.solve(cov, miss))) / (2.0 * math.pi * math.sqrt(max(np.linalg.det(cov), 1e-300)))
    vel = math.exp(-0.5 * float(dv @ dv) / var_v) / (2.0 * math.pi * var_v)
    return pos * vel


def decisively_same_body(a: CommonTrack, b: CommonTrack, variance: float, cfg: ReconstructionConfig,
                         rel: RelativePose) -> bool:
    """Two observers' tracks are one body beyond doubt: they passed the one-box and velocity test at every instant
    both measured it (at least two), and their relative uncertainty ``variance`` (m^2) separates bodies a car
    width apart (3 sigma below ``semantics.target_width_m``): a neighbour abreast would have failed the test
    there.  Weaker than an accepted pair (too few shared instants to merge on their own), enough to tell that
    the other observer's track is no alternative body; with a relative uncertainty of a car width or more
    (consumer-grade pose sources) it never holds."""
    if a.recorder == b.recorder or 3.0 * math.sqrt(max(variance, 0.0)) >= cfg.semantics.target_width_m:
        return False
    strict = replace(cfg, fusion=replace(cfg.fusion, anonymous_min_shared_samples=2, anonymous_pass_fraction=1.0))
    evidence = pair_corrected(a, b, strict, rel)
    return evidence is not None and evidence.accepted


def confusable_neighbours(own: Sequence[CommonTrack], t_end: float, tracks: Sequence[CommonTrack],
                          cfg: ReconstructionConfig, rel: RelativePose,
                          exclude: Sequence[str] = ()) -> List[str]:
    """Other observed road users a re-acquisition could not be told apart from: tracks (any observer, not in
    ``own`` nor ``exclude``, not ``own``'s body seen by another observer -- an accepted pair or
    ``decisively_same_body``) measured within a sweep of ``t_end``
    -- the predecessor's last measured instant -- whose point lies within two car widths
    (``semantics.target_width_m``) plus 3 sigma of the two observations' relative uncertainty of ``own``'s point.
    A car abreast in the next lane (3.5 m) is such a neighbour: across a gap, where each radar point may sit up
    to a body half-width off its centre (the median of the visible faces) and the declared covariances do not
    cover that bias, nothing singles out which of the two came back."""
    last = None
    for track in own:
        for s in track.samples:
            if s.measured and abs(s.t_global - t_end) < 1e-6:
                last = (track, s)
    if last is None:
        return []
    mine, sample = last
    names = {t.name for t in own} | set(exclude)
    out = []
    for other in tracks:
        if other.name in names or other.start > t_end + 0.05 or other.end < t_end - 0.05:
            continue
        state = other.state_at(t_end, 0.051)
        if state is None or not state.measured:
            continue
        variance = (sample.pos_std ** 2 + state.pos_std ** 2
                    + (0.0 if other.recorder == mine.recorder else rel.variance(other.recorder, mine.recorder)))
        if other.recorder != mine.recorder and _overlap(other, mine):
            same = pair_corrected(mine, other, cfg, rel)
            if same is not None and same.accepted or decisively_same_body(mine, other, variance, cfg, rel):
                continue
        reach = 2.0 * cfg.semantics.target_width_m + 3.0 * math.sqrt(max(variance, 0.0))
        if float(np.hypot(*(state.point - sample.point))) <= reach:
            out.append(other.name)
    return out


def rival_density(first: CommonTrack, second: CommonTrack, tracks: Sequence[CommonTrack], cfg: ReconstructionConfig,
                  rel: RelativePose) -> Tuple[float, List[str]]:
    """The other observed road users that could equally be ``second``'s body: every track (any observer) other
    than ``first`` measured within ``stitch_max_gap_s`` before ``second``'s first measurement or still then,
    except tracks of ``second``'s observer measured with it (two simultaneous tracks of one observer are two
    bodies) and tracks that are ``first``'s own body seen by another observer (the one-box and velocity test:
    an accepted pair or ``decisively_same_body``).
    Their re-acquisition densities (``stitch_density``, the relative pose variance added across observers) sum
    into the alternative a stitch must beat besides a new road user.  Returns (sum, the rivals' names)."""
    nxt = next((s for s in second.samples if s.measured), None)
    if nxt is None:
        return 0.0, []
    total, names = 0.0, []
    for other in tracks:
        if other.name in (first.name, second.name) or other.start > nxt.t_global + 1e-6:
            continue
        if other.end < nxt.t_global - cfg.fusion.stitch_max_gap_s - 1e-6:
            continue
        if other.recorder == second.recorder and _overlap(other, second):
            continue
        if other.recorder != first.recorder and _overlap(other, first):
            same = pair_corrected(first, other, cfg, rel)
            last = max((s for s in first.samples if s.measured), key=lambda s: s.t_global, default=None)
            state = other.state_at(last.t_global, 0.051) if last is not None else None
            close = (None if state is None else last.pos_std ** 2 + state.pos_std ** 2
                     + rel.variance(other.recorder, first.recorder))
            if (same is not None and same.accepted
                    or close is not None and decisively_same_body(first, other, close, cfg, rel)):
                continue
        variance = 0.0 if other.recorder == second.recorder else rel.variance(other.recorder, second.recorder)
        density = stitch_density(other, second, cfg, variance)
        if density > 0.0:
            total += density
            names.append(other.name)
    return total, names
