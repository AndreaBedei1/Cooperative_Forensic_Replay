"""Figures of the event validation (``scripts/event_validation.py``): SVG, PDF and PNG, the style and palette of the
campaign v3 figures.  Every figure has its table in the results folder; the scenes are drawn from the kept jobs."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

import numpy as np

from campaign_v3_figures import GRID, INK, MUTED, SLOTS, _save, _style

CONDITIONS = ("G0", "radar nominal", "radar severe", "radar extreme")
CLASS_COLOUR = {"correct": SLOTS[0], "wrong vehicle": SLOTS[1], "unsupported": SLOTS[2], "duplicate": SLOTS[3]}
KIND_COLOUR = {"phantom": SLOTS[1], "ghost of a colliding recorder": SLOTS[4], "ghost of another recorder": SLOTS[3],
               "other vehicle": SLOTS[0], "colliding vehicle": SLOTS[0]}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from cdf.evaluation.figures import paper_style
    paper_style()
    return plt


def draw(results: Sequence[Mapping[str, Any]], tables: Mapping[str, Sequence[Mapping[str, Any]]],
         out_dir: Path) -> List[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    plt = _plt()
    written: List[Path] = []
    written += _classes(plt, results, out_dir / "event_classes")
    written += _phantoms_at_impact(plt, tables, out_dir / "phantoms_at_impact")
    written += _state_errors(plt, tables, out_dir)
    scene = _pick_scene(results)
    if scene is not None:
        written += _scene(plt, scene, out_dir / "impact_scene")
    rec = _pick_recovery(results)
    if rec is not None:
        written += _recovery(plt, rec, out_dir / "recovery_example")
    return written


def _condition(job: Mapping[str, Any]) -> str:
    return "G0" if job["family"] == "baseline" else "radar {0}".format(job["level"])


def _classes(plt: Any, results: Sequence[Mapping[str, Any]], path: Path) -> List[Path]:
    """Share of the predicted conflict events (before contact) by class, per condition and family."""
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN
    families = ("CRITICAL_TTC", "EGO_PATH", "CUT_IN_LEFT", "CUT_IN_RIGHT")
    fig, axes = plt.subplots(1, len(families), figsize=(DOUBLE_COLUMN_IN, 2.0), sharey=True)
    for axis, family in zip(axes, families):
        for y, cond in enumerate(CONDITIONS[::-1]):
            preds = [p for r in results if _condition(r["job"]) == cond for p in r["predictions"]
                     if p["family"] == family and p["phase"] != "after contact" and p["class"] != "not evaluable"]
            left = 0.0
            for cls, colour in CLASS_COLOUR.items():
                share = sum(p["class"] == cls for p in preds) / len(preds) if preds else 0.0
                if share:
                    axis.barh(y, share, left=left, color=colour, height=0.62, edgecolor="white", linewidth=1.0)
                left += share
            axis.text(0.99, y + 0.36, "n = {0}".format(len(preds)), va="bottom", ha="right", fontsize=6, color=MUTED)
        axis.set_title(family.replace("_", " ").lower(), fontsize=8)
        axis.set_xlim(0, 1)
        axis.set_xticks([0, 0.5, 1])
        axis.set_xticklabels(["0", "0.5", "1"])
        _style(axis)
        axis.grid(axis="x", color=GRID, linewidth=0.5)
        axis.grid(axis="y", visible=False)
    axes[0].set_yticks(range(len(CONDITIONS)))
    axes[0].set_yticklabels(CONDITIONS[::-1])
    from matplotlib.patches import Patch
    axes[0].legend(handles=[Patch(color=c, label=k) for k, c in CLASS_COLOUR.items()], frameon=False, ncol=4,
                   loc="lower left", bbox_to_anchor=(0.0, 1.12))
    fig.tight_layout(rect=(0.0, 0.07, 1.0, 1.0), w_pad=1.6)
    fig.text(0.55, 0.01, "share of the predicted events before contact", ha="center", fontsize=8)
    written = _save(fig, path)
    plt.close(fig)
    return written


def _phantoms_at_impact(plt: Any, tables: Mapping[str, Sequence[Mapping[str, Any]]], path: Path) -> List[Path]:
    """Phantoms per contact present at the impact, by full-box clearance to the colliding pair."""
    from cdf.evaluation.figures import SINGLE_COLUMN_IN
    rows = {r["condition"]: r for r in tables.get("proximity", []) if r["kind"] == "phantom"}
    bins = ("at_impact <=2 m", "at_impact (2,4] m", "at_impact (4,5] m")
    fig, axis = plt.subplots(figsize=(SINGLE_COLUMN_IN, 2.0))
    width = 0.26
    for k, (col, colour) in enumerate(zip(bins, SLOTS)):
        values = [rows[c][col] / rows[c]["contacts"] if c in rows and rows[c]["contacts"] else 0.0 for c in CONDITIONS]
        axis.bar(np.arange(len(CONDITIONS)) + (k - 1) * width, values, width=width - 0.03, color=colour,
                 label=col.replace("at_impact ", ""))
    axis.set_xticks(range(len(CONDITIONS)))
    axis.set_xticklabels([c.replace("radar ", "") for c in CONDITIONS])
    axis.set_ylabel("phantoms per contact")
    axis.legend(frameon=False, title="clearance at impact", fontsize=7, title_fontsize=7)
    _style(axis)
    fig.tight_layout()
    written = _save(fig, path)
    plt.close(fig)
    return written


def _state_errors(plt: Any, tables: Mapping[str, Sequence[Mapping[str, Any]]], out_dir: Path) -> List[Path]:
    """Median and P95 of the saved-state errors, measured and predicted, per condition."""
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN
    rows = tables.get("states", [])
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COLUMN_IN, 1.9), sharey=True)
    for axis, (prefix, title) in zip(axes, (("track", "local track point to its vehicle's box [m]"),
                                            ("entity", "road-user centre error [m]"))):
        for k, (kind, colour) in enumerate((("measured", SLOTS[0]), ("predicted", SLOTS[1]))):
            for y, cond in enumerate(CONDITIONS[::-1]):
                row = next((r for r in rows if r["condition"] == cond and r["states"] == prefix + "_" + kind), None)
                if not row or not row.get("n"):
                    continue
                yy = y + (0.15 if k == 0 else -0.15)
                axis.plot([row["median"], row["p95"]], [yy, yy], color=colour, linewidth=2.0, alpha=0.45,
                          solid_capstyle="round")
                axis.plot([row["median"]], [yy], marker="o", markersize=4.0, color=colour,
                          label=kind if y == 0 else None)
        axis.set_xlabel(title + " (dot: median; bar to P95)")
        _style(axis)
        axis.grid(axis="x", color=GRID, linewidth=0.5)
    axes[0].set_yticks(range(len(CONDITIONS)))
    axes[0].set_yticklabels(CONDITIONS[::-1])
    axes[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    written = _save(fig, out_dir / "state_errors")
    plt.close(fig)
    return written


def _pick_scene(results: Sequence[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
    """The extreme-radar job with the most phantoms within 5 m of a colliding pair at its impact."""
    best, best_n = None, 0
    for r in results:
        if r["job"]["family"] != "radar_v3" or r["job"]["level"] != "extreme":
            continue
        for c in r["contacts"]:
            n = sum(1 for x in r["proximity"] if x["contact"] == c["index"] and x["kind"] == "phantom"
                    and x["clearance_at_impact_m"] is not None and x["clearance_at_impact_m"] <= 5.0)
            if n > best_n:
                best, best_n = {"result": r, "contact": c["index"]}, n
    return best


def _scene(plt: Any, scene: Mapping[str, Any], path: Path) -> List[Path]:
    """Bird's-eye view at the impact: true boxes (colliding pair dark), estimated road users by kind."""
    from matplotlib.patches import Polygon
    from cdf.evaluation import event_validation as ev
    from cdf.evaluation.figures import SINGLE_COLUMN_IN
    r, k = scene["result"], scene["contact"]
    data = ev.RunData(Path(r["job"]["kept"]))
    contact = next(c for c in data.contacts() if c["index"] == k)
    sim = contact["sim"]
    fig, axis = plt.subplots(figsize=(SINGLE_COLUMN_IN, SINGLE_COLUMN_IN))
    centre = None
    for vehicle, track in data.truth.items():
        state = track.at(sim)
        if state is None:
            continue
        rect = ev.true_rect(state)
        corners = ev._corners(*rect)
        pair = vehicle in contact["pair"]
        axis.add_patch(Polygon(corners, closed=True, facecolor="none", edgecolor=INK if pair else MUTED,
                               linewidth=1.6 if pair else 0.8))
        axis.text(rect[0], rect[1], vehicle, ha="center", va="center", fontsize=6, color=INK)
        if pair:
            centre = (rect[0], rect[1]) if centre is None else ((centre[0] + rect[0]) / 2, (centre[1] + rect[1]) / 2)
    kinds = {x["entity"]: x["kind"] for x in r["proximity"] if x["contact"] == k}
    seen = set()
    for e in data.entities:
        state = min(e.get("trajectory", []), key=lambda s: abs(data.reference_sim + s["t_global"] - sim), default=None)
        if state is None or abs(data.reference_sim + state["t_global"] - sim) > ev.ENTITY_AT_S:
            continue
        kind = kinds.get(e["id"], "phantom")
        corners = ev._corners(*ev.entity_rect(state, e.get("footprint") or {}))
        axis.add_patch(Polygon(corners, closed=True, facecolor=KIND_COLOUR[kind], alpha=0.35, edgecolor=KIND_COLOUR[kind],
                               linewidth=0.6, label=None if kind in seen else kind))
        seen.add(kind)
    if centre is not None:
        axis.set_xlim(centre[0] - 25, centre[0] + 25)
        axis.set_ylim(centre[1] - 25, centre[1] + 25)
    axis.set_aspect("equal")
    axis.set_xlabel("x [m]")
    axis.set_ylabel("y [m]")
    job = r["job"]
    axis.set_title("{0}, radar {1}, seed {2}: impact {3}".format(job["run"], job["level"], job["seed"],
                                                                  "-".join(contact["pair"])), fontsize=7)
    axis.legend(frameon=False, fontsize=6, loc="upper right")
    _style(axis)
    fig.tight_layout()
    written = _save(fig, path)
    plt.close(fig)
    return written


def _pick_recovery(results: Sequence[Mapping[str, Any]]) -> Optional[Mapping[str, Any]]:
    """A degraded-radar track of a collision partner that loses the partner before the 5 m zone and regains it
    before the impact (the longest history first), else any recovered one."""
    best, best_len = None, -1.0
    for r in results:
        if r["job"]["family"] == "baseline":
            continue
        for x in r["recovery"]:
            if x["zone_5m"] == "established after entry, before impact" and x["track_start_s"] < -2.0:
                length = -x["track_start_s"]
                if length > best_len:
                    best, best_len = {"result": r, "row": x}, length
    if best is None:
        for r in results:
            for x in r["recovery"]:
                if r["job"]["family"] != "baseline" and x["first_support_s"] is not None:
                    return {"result": r, "row": x}
    return best


def _recovery(plt: Any, pick: Mapping[str, Any], path: Path) -> List[Path]:
    """Distance of one partner track to the partner's true box against time to the contact, with the 1.5 m identity
    rule, the established support and the entries into the 5, 4 and 2 m zones."""
    from cdf.evaluation import event_validation as ev
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN
    r, row = pick["result"], pick["row"]
    data = ev.RunData(Path(r["job"]["kept"]))
    contact = next(c for c in data.contacts() if c["index"] == row["contact"])
    rows = data.samples[row["track"]]
    t = np.array([s["sim"] - contact["sim"] for s in rows])
    d = np.array([data.distance_to(s, row["partner"]) or np.nan for s in rows])
    fig, axis = plt.subplots(figsize=(DOUBLE_COLUMN_IN, 2.0))
    measured = np.array([bool(s["measured"]) for s in rows])
    axis.plot(t[measured], d[measured], "o", markersize=2.5, color=SLOTS[0], label="measured")
    axis.plot(t[~measured], d[~measured], "o", markersize=2.5, color=SLOTS[1], label="predicted")
    axis.axhline(ev.IDENTITY_M, color=MUTED, linewidth=0.8, linestyle="--")
    support = ev.runs_of([s["sim"] for s in rows], [x is not None and x <= ev.IDENTITY_M for x in
                                                    (data.distance_to(s, row["partner"]) for s in rows)])
    for start, established, end in support:
        axis.axvspan(established - contact["sim"], end - contact["sim"], color=SLOTS[2], alpha=0.15, linewidth=0)
    top = float(np.nanmax(d))
    for n, (zone, entry) in enumerate(ev.zone_entries(data, contact["pair"], contact["sim"]).items()):
        if entry is not None:
            axis.axvline(entry - contact["sim"], color=INK, linewidth=0.6)
            axis.text(entry - contact["sim"], top * (1.0 - 0.12 * n), " {0:g} m".format(zone), fontsize=6, color=INK,
                      va="top")
    axis.axvline(0.0, color=INK, linewidth=1.2)
    job = r["job"]
    axis.set_title("{0}, radar {1}, seed {2}: {3} on partner {4} (shaded: established support)".format(
        job["run"], job["level"], job["seed"], row["track"], row["partner"]), fontsize=7)
    axis.set_xlabel("time to the contact [s]")
    axis.set_ylabel("distance to the partner's box [m]")
    axis.legend(frameon=False, fontsize=7)
    _style(axis)
    fig.tight_layout()
    written = _save(fig, path)
    plt.close(fig)
    return written
