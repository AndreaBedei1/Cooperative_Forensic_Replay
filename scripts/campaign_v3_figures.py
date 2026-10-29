"""Figures of the campaign v3 report (``scripts/campaign_v3_report.py``): SVG, PDF and PNG at IEEE widths
(``cdf.evaluation.figures.paper_style``).  One measure per axis; categorical colours in a fixed order (radar
levels, recorder strata), a single blue ramp for magnitudes; every figure has its table (CSV) in the report folder."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence

# Categorical slots in fixed order (validated palette, light mode): blue, orange, aqua, yellow, magenta.
SLOTS = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4")
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"
RAMP = ("#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b")
LEVEL_COLOUR = {"nominal": SLOTS[0], "severe": SLOTS[1], "extreme": SLOTS[2]}
SHORT = {"baseline": "G0", "gnss": "GNSS", "radar_v3": "radar", "radar_asym": "radar, subset",
         "radar_gnss_v3": "GNSS x radar", "radar_asym_gnss": "G2 x radar, subset"}


def _style(axis: Any) -> None:
    axis.grid(axis="y", color=GRID, linewidth=0.5)
    axis.set_axisbelow(True)
    for side in ("top", "right"):
        axis.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axis.spines[side].set_color(MUTED)
        axis.spines[side].set_linewidth(0.6)
    axis.tick_params(colors=INK, width=0.6)


def _save(fig: Any, path: Path) -> List[Path]:
    """SVG, PDF and PNG with no date and fixed SVG ids: the figures regenerate byte for byte."""
    import matplotlib
    metadata = {"svg": {"Date": None}, "pdf": {"CreationDate": None}, "png": {}}
    written = []
    with matplotlib.rc_context({"svg.hashsalt": "campaign-v3"}):
        for suffix in ("svg", "pdf", "png"):
            target = path.with_suffix("." + suffix)
            fig.savefig(str(target), dpi=200, bbox_inches="tight", metadata=metadata[suffix])
            written.append(target)
    return written


def _label(row: Mapping[str, Any]) -> str:
    if row["family"] == "baseline":
        return "G0 baseline"
    level = str(row["level"]).replace("gnss ", "").replace(" + radar ", " / ")
    subset = "" if row["subset"] == "all" else " ({0})".format(row["subset"])
    return "{0}: {1}{2}".format(SHORT.get(row["family"], row["family"]), level, subset)


def _dots(axis: Any, rows: Sequence[Mapping[str, Any]], key: str, colour: str) -> None:
    ys = list(range(len(rows)))[::-1]
    for y, row in zip(ys, rows):
        value, interval = row.get(key), row.get(key + "_ci")
        if value is None:
            continue
        if interval:
            axis.plot(interval, [y, y], color=colour, linewidth=2.0, solid_capstyle="round", alpha=0.45)
        axis.plot([value], [y], marker="o", markersize=4.5, color=colour, markeredgecolor="white", markeredgewidth=0.8)
    axis.set_yticks(ys)
    axis.set_yticklabels([_label(r) for r in rows])


def _condition_figure(plt: Any, rows: Sequence[Mapping[str, Any]], panels: Sequence[Sequence[Any]], title: str,
                      path: Path) -> List[Path]:
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN
    fig, axes = plt.subplots(1, len(panels), figsize=(DOUBLE_COLUMN_IN, 0.16 * len(rows) + 1.0), sharey=True)
    axes = list(axes) if len(panels) > 1 else [axes]
    for index, (axis, (key, xlabel, limits)) in enumerate(zip(axes, panels)):
        _dots(axis, rows, key, SLOTS[0])
        axis.set_xlabel(xlabel)
        if limits:
            axis.set_xlim(*limits)
        _style(axis)
        axis.grid(axis="x", color=GRID, linewidth=0.5)
        if index:
            axis.tick_params(labelleft=False)
    fig.suptitle(title, x=0.01, ha="left")
    fig.tight_layout()
    written = _save(fig, path)
    plt.close(fig)
    return written


def _asymmetry_figure(plt: Any, asymmetry: Sequence[Mapping[str, Any]], key: str, ylabel: str, path: Path
                      ) -> List[Path]:
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN
    panels = [(gnss, stratum) for gnss in ("G0", "G2") for stratum in ("2", "3")
              if any(r["gnss"] == gnss and r["recorders"] == stratum for r in asymmetry)]
    if not panels:
        return []
    fig, axes = plt.subplots(1, len(panels), figsize=(DOUBLE_COLUMN_IN, 2.3), sharey=True)
    axes = list(axes) if len(panels) > 1 else [axes]
    order = ("1 (alone)", "all but one", "all")
    for axis, (gnss, stratum) in zip(axes, panels):
        for level in ("nominal", "severe", "extreme"):
            rows = {r["degraded"]: r for r in asymmetry if r["gnss"] == gnss and r["recorders"] == stratum
                    and r["radar"] == level and r.get(key) is not None}
            xs = [i for i, d in enumerate(order) if d in rows]
            if not xs:
                continue
            ys = [rows[order[i]][key] for i in xs]
            axis.plot(xs, ys, color=LEVEL_COLOUR[level], linewidth=2.0, marker="o", markersize=4.5,
                      markeredgecolor="white", markeredgewidth=0.8, label=level)
            for i in xs:
                interval = rows[order[i]].get(key + "_ci")
                if interval:
                    axis.plot([i, i], interval, color=LEVEL_COLOUR[level], linewidth=2.0, alpha=0.4)
        axis.set_xticks(range(len(order)))
        axis.set_xticklabels(["one", "all but one", "all"] if stratum == "3" else ["one", "-", "both"])
        axis.set_title("{0}, {1} recorders".format("ideal GNSS" if gnss == "G0" else "G2 GNSS", stratum))
        axis.set_xlabel("radars degraded")
        _style(axis)
    axes[0].set_ylabel(ylabel)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=LEVEL_COLOUR[level], linewidth=2.0, marker="o", markersize=4.5,
                      markeredgecolor="white", label=level) for level in ("nominal", "severe", "extreme")]
    axes[-1].legend(handles=handles, title="radar level", frameon=False)
    fig.tight_layout()
    written = _save(fig, path)
    plt.close(fig)
    return written


def _interaction_figure(plt: Any, interaction: Sequence[Mapping[str, Any]], path: Path) -> List[Path]:
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN
    metrics = (("represented_rate", "paired change,\nobservable represented"),
               ("phantoms_per_job", "paired change,\nphantoms / job"), ("pos_median", "paired change,\nposition median [m]"))
    rows = [r for r in interaction if r.get("seeds")]
    if not rows:
        return []
    fig, axes = plt.subplots(1, len(metrics), figsize=(DOUBLE_COLUMN_IN, 2.4), sharey=True)
    labels = ["{0} / {1}".format({"rtk": "G1", "degraded": "G2"}[r["gnss"]], r["radar"]) for r in rows]
    ys = list(range(len(rows)))[::-1]
    for axis, (metric, xlabel) in zip(axes, metrics):
        for y, row in zip(ys, rows):
            combined, additive = row.get(metric + "_combined"), row.get(metric + "_additive")
            if combined is not None:
                axis.plot([combined], [y + 0.12], marker="o", markersize=4.5, color=SLOTS[0], linestyle="none")
            if additive is not None:
                axis.plot([additive], [y - 0.12], marker="D", markersize=4.0, color=SLOTS[1], linestyle="none")
        axis.axvline(0.0, color=MUTED, linewidth=0.6)
        axis.set_xlabel(xlabel)
        _style(axis)
        axis.grid(axis="x", color=GRID, linewidth=0.5)
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels(labels)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", markersize=4.5, color=SLOTS[0], linestyle="none", label="observed"),
               Line2D([], [], marker="D", markersize=4.0, color=SLOTS[1], linestyle="none",
                      label="sum of single-sensor changes")]
    axes[0].legend(handles=handles, frameon=False, loc="lower left", bbox_to_anchor=(0.0, 1.02), ncol=2)
    fig.tight_layout()
    written = _save(fig, path)
    plt.close(fig)
    return written


def _scenario_figure(plt: Any, scenarios: Sequence[Mapping[str, Any]], key: str, title: str, path: Path,
                     limits: Optional[Sequence[float]] = None) -> List[Path]:
    from matplotlib.colors import LinearSegmentedColormap
    from cdf.evaluation.figures import DOUBLE_COLUMN_IN
    cells = [r for r in scenarios if r["subset"] == "all" and r.get(key) is not None]
    if not cells:
        return []
    runs = sorted({r["run"] for r in cells})
    conds = []
    for r in cells:
        c = (r["family"], r["level"])
        if c not in conds:
            conds.append(c)
    from campaign_v3_report import FAMILY_ORDER, LEVEL_ORDER
    conds.sort(key=lambda c: (FAMILY_ORDER.index(c[0]) if c[0] in FAMILY_ORDER else 99,
                              LEVEL_ORDER.index(c[1]) if c[1] in LEVEL_ORDER else 99))
    grid = [[None] * len(conds) for _ in runs]
    for r in cells:
        grid[runs.index(r["run"])][conds.index((r["family"], r["level"]))] = r[key]
    import numpy as np
    data = np.array([[np.nan if v is None else v for v in row] for row in grid], dtype=float)
    fig, axis = plt.subplots(figsize=(DOUBLE_COLUMN_IN, 0.17 * len(runs) + 1.4))
    cmap = LinearSegmentedColormap.from_list("blue", RAMP)
    cmap.set_bad(GRID)
    image = axis.imshow(np.ma.masked_invalid(data), aspect="auto", cmap=cmap,
                        vmin=None if not limits else limits[0], vmax=None if not limits else limits[1])
    axis.set_yticks(range(len(runs)))
    axis.set_yticklabels(runs)
    axis.set_xticks(range(len(conds)))
    axis.set_xticklabels(["{0}: {1}".format(SHORT.get(f, f), str(l).replace("gnss ", "").replace(" + radar ", "/"))
                          for f, l in conds], rotation=60, ha="right")
    fig.colorbar(image, ax=axis, fraction=0.03, pad=0.02)
    axis.set_title(title, loc="left")
    fig.tight_layout()
    written = _save(fig, path)
    plt.close(fig)
    return written


def draw(table: Sequence[Mapping[str, Any]], interaction: Sequence[Mapping[str, Any]],
         asymmetry: Sequence[Mapping[str, Any]], scenarios: Sequence[Mapping[str, Any]], out_dir: Path) -> List[Path]:
    from cdf.evaluation.figures import paper_style
    plt = paper_style()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [r for r in table if r["recorders"] == "all"]
    written: List[Path] = []
    written += _condition_figure(plt, rows, [("identified_rate", "collisions identified", (-0.02, 1.02)),
                                             ("invented_per_job", "invented collisions / job", None)],
                                 "Collisions per condition (mean over seeds, 95 % interval)", out_dir / "collisions")
    written += _condition_figure(plt, rows, [("represented_rate", "observable road users represented", (-0.02, 1.02)),
                                             ("duplicates_per_job", "duplicates / job", None),
                                             ("phantoms_per_job", "phantoms / job", None)],
                                 "Completeness of the road users that record nothing", out_dir / "completeness")
    written += _condition_figure(plt, rows, [("pos_median", "position error, median [m]", None),
                                             ("pos_p95", "position error, P95 [m]", None),
                                             ("spd_median", "speed error, median [m/s]", None)],
                                 "Errors of the reconstructed road users", out_dir / "errors")
    written += _asymmetry_figure(plt, asymmetry, "phantoms_per_job", "phantoms / job", out_dir / "asymmetry_phantoms")
    written += _asymmetry_figure(plt, asymmetry, "represented_rate", "observable represented",
                                 out_dir / "asymmetry_represented")
    written += _interaction_figure(plt, interaction, out_dir / "interaction")
    written += _scenario_figure(plt, scenarios, "phantoms", "Phantoms per job, by scenario (mean over seeds)",
                                out_dir / "scenarios_phantoms")
    written += _scenario_figure(plt, scenarios, "pos_med_m", "Position error median [m], by scenario (mean over seeds)",
                                out_dir / "scenarios_position")
    return written
