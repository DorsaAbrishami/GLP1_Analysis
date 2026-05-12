# GLP-1 Analysis

A data-analysis project answering 7 analytical questions about **GLP-1 receptor agonist** drugs (Ozempic, Wegovy, Mounjaro, Zepbound, Trulicity, ...) using the [GLP-1 Weight Loss Drugs Master Dataset (2017-2026)](https://www.kaggle.com/datasets/devtayyabsajjad/glp-1-weight-loss-drugs-master-dataset-2017-2026) from Kaggle.

## Project structure

```
GLP1_Analysis/
├── data/
│   ├── raw/                       # Original CSVs (from Kaggle, auto-refreshable)
│   └── processed/                 # Cleaned intermediate outputs
├── notebooks/
│   ├── 01_data_exploration.ipynb  # Schema, null counts, date ranges
│   ├── 02_side_effects.ipynb      # Q1: FAERS hospitalization rates per drug
│   ├── 03_stock_vs_search.ipynb   # Q2: LLY/NVO price vs Ozempic search
│   ├── 04_geographic_patterns.ipynb  # Q3: AE & search by country
│   ├── 05_demographics.ipynb      # Q4: age + sex by drug x reaction
│   ├── 06_clinical_trials.ipynb   # Q5: phase / sponsor / start-year mix
│   ├── 07_investigational_drugs.ipynb  # Q6: orforglipron, retatrutide, CagriSema
│   └── 08_anomaly_detection.ipynb # Q7: monthly FAERS z-score anomalies
├── src/
│   ├── load_data.py               # Kaggle download + typed loaders
│   ├── cleaning.py                # Dedup, age normalization, ISO-3 mapping
│   └── plotting.py                # Theme + save_fig / save_table helpers
├── outputs/
│   ├── figures/                   # PNG plots (one per notebook section)
│   └── tables/                    # CSV summary tables
├── report.md                      # Final written summary
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Refreshing the raw data (automated)

The raw CSVs in `data/raw/` are downloaded from the Kaggle dataset above.
The loader is idempotent: it skips the download if all expected files are
already present, so you can wire it into a daily cron / GitHub Action.

1. Install the Kaggle CLI token (one-time): grab `kaggle.json` from
   <https://www.kaggle.com/settings> and drop it at `~/.kaggle/kaggle.json`
   (on Windows: `%USERPROFILE%\.kaggle\kaggle.json`). `chmod 600` on Unix.
2. Refresh on demand:

```bash
# Idempotent: only downloads if a file is missing
python -m src.load_data

# Force a fresh re-download (e.g. cron job)
FORCE=1 python -m src.load_data
```

Inside notebooks, the typed loaders all read from `data/raw/`:

```python
from src.load_data import load_all
data = load_all()
ae, trials, stocks = data["ae"], data["trials"], data["stocks"]
```

## How to run

1. `pip install -r requirements.txt`
2. `python -m src.load_data` (or skip — CSVs are already present)
3. Open `notebooks/01_data_exploration.ipynb` and `Run All`
4. Work through `02_…` → `08_…` in order
5. Read `report.md` for the synthesis

## Disclaimer

For research / educational use only. FAERS adverse-event reports are voluntary
and unverified; they reflect *reporting behavior*, not drug-caused incidence.
Nothing here is medical or investment advice.
