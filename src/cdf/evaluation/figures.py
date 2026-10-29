"""Figure style of the paper's plots (evaluation side): IEEE column widths, fonts embedded as TrueType in the
PDF (no Type 3), text kept as text in the SVG, 8 pt text.  Checked by ``scripts/results_qa.py``."""

from __future__ import annotations

from typing import Any

SINGLE_COLUMN_IN = 3.5
DOUBLE_COLUMN_IN = 7.16
FONT_PT = 8


def paper_style() -> Any:
    """matplotlib.pyplot with the paper's settings (Agg backend)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42, "font.family": "DejaVu Sans",
                         "font.size": FONT_PT, "axes.titlesize": FONT_PT, "axes.labelsize": FONT_PT,
                         "xtick.labelsize": FONT_PT - 1, "ytick.labelsize": FONT_PT - 1, "legend.fontsize": FONT_PT - 1,
                         "figure.titlesize": FONT_PT + 1})
    return plt
