"""
Cleaning helpers used across notebooks.

Each function does one small thing and returns a new DataFrame (never mutates
the input). Keeps notebooks short and avoids copy-pasted cleaning code.
"""

from __future__ import annotations

import pandas as pd
import numpy as np


# Approved GLP-1 generics with non-trivial FAERS volume -- used to filter noise
# (e.g. an investigational drug with <50 reports isn't worth ranking).
APPROVED_GLP1_DRUGS = [
    "semaglutide",
    "tirzepatide",
    "liraglutide",
    "dulaglutide",
    "exenatide",
    "lixisenatide",
    "albiglutide",
]


def dedupe_reports(ae: pd.DataFrame) -> pd.DataFrame:
    """Collapse the AE table to one row per safety report.

    FAERS stores one row per (report, reaction). Counting reports without
    deduping over-counts any report that had multiple reactions.
    """
    # First row per safetyreportid keeps all the report-level fields; the
    # reaction column is no longer meaningful at this level.
    return (
        ae.sort_values(["safetyreportid", "receive_date"])
          .drop_duplicates(subset="safetyreportid", keep="first")
          .reset_index(drop=True)
    )


def normalize_age_to_years(ae: pd.DataFrame) -> pd.DataFrame:
    """Convert patient_age into years using patient_age_unit.

    FAERS reports age in years/months/weeks/days/decades. Without this,
    a 6-month-old looks the same as a 6-year-old.
    """
    out = ae.copy()
    unit_to_years = {
        "Year": 1.0,
        "Decade": 10.0,
        "Month": 1 / 12,
        "Week": 1 / 52,
        "Day": 1 / 365.25,
        "Hour": 1 / (365.25 * 24),
    }
    factor = out["patient_age_unit"].map(unit_to_years).fillna(1.0)
    out["age_years"] = out["patient_age"] * factor
    # Clip nonsense values: ages > 120 are data errors in FAERS.
    out.loc[out["age_years"] > 120, "age_years"] = np.nan
    return out


def country_to_iso3(series: pd.Series) -> pd.Series:
    """Map FAERS 2-letter country codes (ISO alpha-2) to ISO alpha-3.

    Needed because choropleths and most geo libs want alpha-3. Returns NaN
    for unknown / 'UNK' / missing codes -- the caller decides whether to
    drop or relabel them.
    """
    try:
        import pycountry
    except ImportError as exc:
        raise ImportError("pip install pycountry") from exc

    cache: dict[str, str | None] = {}

    def _lookup(code) -> str | None:
        if not isinstance(code, str) or len(code) != 2:
            return None
        if code in cache:
            return cache[code]
        try:
            result = pycountry.countries.get(alpha_2=code.upper())
            cache[code] = result.alpha_3 if result else None
        except (KeyError, AttributeError):
            cache[code] = None
        return cache[code]

    return series.map(_lookup)


def top_reactions_per_drug(ae: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Return the top-N reactions (by report count) for each drug.

    Operates on the reaction-level AE table (NOT the deduped one), since each
    (report, reaction) pair is the unit we're counting.
    """
    counts = (
        ae.groupby(["generic_name", "reaction"], dropna=False)
          .size()
          .reset_index(name="n_reports")
    )
    counts["rank"] = counts.groupby("generic_name")["n_reports"].rank(
        method="first", ascending=False
    )
    return (
        counts[counts["rank"] <= top_n]
        .sort_values(["generic_name", "rank"])
        .reset_index(drop=True)
    )
