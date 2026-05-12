"""
Data loading helpers.

Two responsibilities:
1. Refresh the raw CSVs from Kaggle (so a daily re-run picks up updates).
2. Load each CSV into a tidy pandas DataFrame with the right dtypes / parsed dates.

Hardcoded paths on purpose -- keeps a junior-level analysis script simple.
"""

from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd

# Hardcoded paths -- this script lives in src/, data lives one level up.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Kaggle dataset slug for the GLP-1 Master Dataset (2017-2026).
KAGGLE_DATASET = "devtayyabsajjad/glp-1-weight-loss-drugs-master-dataset-2017-2026"

# Files we expect the Kaggle archive to contain (and that the rest of the project reads).
EXPECTED_FILES = [
    "drugs_overview.csv",
    "adverse_events.csv",
    "adverse_events_summary.csv",
    "clinical_trials.csv",
    "stock_prices.csv",
    "search_trends.csv",
    "wikipedia_summaries.csv",
    "data_dictionary.csv",
]


# ---------------------------------------------------------------------------
# Automated refresh
# ---------------------------------------------------------------------------

def refresh_raw_data(force: bool = False, quiet: bool = False) -> dict:
    """Download (or re-download) the Kaggle dataset into data/raw/.

    Re-runs cheaply: if all expected files already exist and ``force`` is
    False, it just returns without hitting the network. Designed so a daily
    cron / GitHub Action can call this and only do real work when needed.
    Requires the ``kaggle`` package and a ``~/.kaggle/kaggle.json`` token.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    existing = {f: (RAW_DIR / f).exists() for f in EXPECTED_FILES}

    if not force and all(existing.values()):
        if not quiet:
            print(f"[load_data] All {len(EXPECTED_FILES)} raw files already present in {RAW_DIR}. "
                  f"Pass force=True to re-download.")
        return {"downloaded": False, "files": existing}

    # Import lazily so analysis notebooks don't fail just because kaggle isn't
    # configured -- they can read the existing CSVs from disk. The current
    # `kaggle` package calls sys.exit on import when creds are missing, so
    # we have to catch SystemExit too.
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except (ImportError, OSError, SystemExit) as exc:
        raise RuntimeError(
            "Could not import the `kaggle` package. Install with `pip install kaggle` "
            "and place a kaggle.json API token at ~/.kaggle/kaggle.json "
            "(Windows: %USERPROFILE%\\.kaggle\\kaggle.json). See README."
        ) from exc

    api = KaggleApi()
    try:
        api.authenticate()
    except Exception as exc:
        raise RuntimeError(
            "Kaggle auth failed. Drop kaggle.json into ~/.kaggle/ "
            "or set KAGGLE_USERNAME / KAGGLE_KEY env vars."
        ) from exc
    if not quiet:
        print(f"[load_data] Downloading {KAGGLE_DATASET} -> {RAW_DIR}")
    api.dataset_download_files(KAGGLE_DATASET, path=str(RAW_DIR), unzip=True, quiet=quiet)

    # Some Kaggle archives unzip into a nested folder; flatten so callers always
    # see the files at data/raw/<file>.csv regardless of how the archive is shaped.
    _flatten_into_raw_dir()

    final = {f: (RAW_DIR / f).exists() for f in EXPECTED_FILES}
    missing = [f for f, ok in final.items() if not ok]
    if missing and not quiet:
        print(f"[load_data] WARNING: expected files not found after download: {missing}")
    return {"downloaded": True, "files": final}


def _flatten_into_raw_dir() -> None:
    """If the Kaggle archive unzipped into a subfolder, lift its CSVs into RAW_DIR."""
    for subdir in [p for p in RAW_DIR.iterdir() if p.is_dir()]:
        for csv_path in subdir.rglob("*.csv"):
            target = RAW_DIR / csv_path.name
            if not target.exists():
                shutil.move(str(csv_path), str(target))
        # Clean up the now-empty (or junk) subfolder
        shutil.rmtree(subdir, ignore_errors=True)

    # Also unzip any stray .zip the API may leave behind.
    for zip_path in RAW_DIR.glob("*.zip"):
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(RAW_DIR)
        zip_path.unlink()


# ---------------------------------------------------------------------------
# Typed loaders -- one per file, returns a clean DataFrame
# ---------------------------------------------------------------------------

def load_drugs() -> pd.DataFrame:
    """Drug-level reference table (10 rows)."""
    return pd.read_csv(
        RAW_DIR / "drugs_overview.csv",
        parse_dates=["fda_first_approval_date"],
    )


def load_adverse_events() -> pd.DataFrame:
    """One row per (FAERS report, reaction). Has ~2.75 rows per safetyreportid."""
    df = pd.read_csv(
        RAW_DIR / "adverse_events.csv",
        parse_dates=["receive_date"],
        low_memory=False,
    )
    # Normalize the seriousness flag to a real bool -- different snapshots have
    # bool / "1"/"0" / "True"/"False" depending on how openFDA was scraped.
    for col in [
        "serious",
        "seriousness_death",
        "seriousness_lifethreatening",
        "seriousness_hospitalization",
        "seriousness_disabling",
    ]:
        if df[col].dtype != bool:
            df[col] = (
                df[col].astype(str).str.strip()
                .isin({"1", "True", "true", "Y", "y"})
            )
    return df


def load_ae_summary() -> pd.DataFrame:
    """Pre-aggregated AE rates: one row per (drug, reaction)."""
    return pd.read_csv(RAW_DIR / "adverse_events_summary.csv")


def load_clinical_trials() -> pd.DataFrame:
    """ClinicalTrials.gov pulls."""
    return pd.read_csv(
        RAW_DIR / "clinical_trials.csv",
        parse_dates=["start_date", "completion_date"],
    )


def load_stocks() -> pd.DataFrame:
    """Daily OHLCV for LLY and NVO."""
    return pd.read_csv(RAW_DIR / "stock_prices.csv", parse_dates=["date"])


def load_search_trends() -> pd.DataFrame:
    """Monthly Google Trends index, per geo and search term."""
    return pd.read_csv(RAW_DIR / "search_trends.csv", parse_dates=["date"])


def load_wikipedia() -> pd.DataFrame:
    """Wikipedia intro paragraphs + lead image URLs."""
    return pd.read_csv(RAW_DIR / "wikipedia_summaries.csv")


def load_data_dictionary() -> pd.DataFrame:
    """Schema reference for every column in the project."""
    return pd.read_csv(RAW_DIR / "data_dictionary.csv")


def load_all() -> dict[str, pd.DataFrame]:
    """Convenience: load every CSV. Useful at the top of an exploration notebook."""
    return {
        "drugs": load_drugs(),
        "ae": load_adverse_events(),
        "ae_summary": load_ae_summary(),
        "trials": load_clinical_trials(),
        "stocks": load_stocks(),
        "trends": load_search_trends(),
        "wiki": load_wikipedia(),
        "dictionary": load_data_dictionary(),
    }


if __name__ == "__main__":
    # `python -m src.load_data` from the project root will refresh the raw data.
    refresh_raw_data(force=bool(int(os.environ.get("FORCE", "0"))))
