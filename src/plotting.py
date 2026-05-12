"""
Plot styling helpers.

Each notebook calls ``apply_style()`` once at the top, then uses normal
matplotlib / seaborn. The ``save_fig`` helper enforces consistent DPI and a
predictable output filename.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables"

# Reusable color palette so the same drug looks the same across notebooks.
DRUG_COLORS = {
    "semaglutide":  "#1f77b4",
    "tirzepatide":  "#d62728",
    "liraglutide":  "#2ca02c",
    "dulaglutide":  "#9467bd",
    "exenatide":    "#ff7f0e",
    "lixisenatide": "#8c564b",
    "albiglutide":  "#7f7f7f",
    "orforglipron": "#17becf",
    "retatrutide":  "#bcbd22",
    "cagrilintide-semaglutide": "#e377c2",
}


def apply_style() -> None:
    """Set a consistent seaborn theme. Call once per notebook."""
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams["figure.dpi"] = 110
    plt.rcParams["savefig.dpi"] = 150
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["axes.titlelocation"] = "left"


def save_fig(fig, name: str) -> Path:
    """Save a figure to outputs/figures/<name>.png and return the path."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / (name if name.endswith(".png") else f"{name}.png")
    fig.savefig(out, bbox_inches="tight")
    return out


def save_table(df, name: str) -> Path:
    """Save a DataFrame to outputs/tables/<name>.csv and return the path."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    out = TABLE_DIR / (name if name.endswith(".csv") else f"{name}.csv")
    df.to_csv(out, index=False)
    return out
