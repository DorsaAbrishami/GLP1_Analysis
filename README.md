#GLP-1 Analysis
An end-to-end analysis of the GLP-1 receptor agonist drug class (Ozempic, Wegovy, Mounjaro, Zepbound, Trulicity, ...) covering adverse-event reporting, clinical-trial pipeline, demographics, and market signals — built on the GLP-1 Weight Loss Drugs Master Dataset (2017–2026) from Kaggle.
Scope: ~149K FAERS adverse-event reports · 1,953 clinical trials · 611 lead sponsors · 100 months of equity and search-interest data · 7 analytical questions across 8 notebooks.
> **Read this first.** FAERS reports are voluntary and unverified. Every rate below describes *reporting behavior*, not drug-caused incidence. Differences between drugs are heavily confounded by time on market, indication, and news cycles — the analysis treats those confounders explicitly rather than reporting rates as if they were risk. Nothing here is medical, regulatory, or investment advice.
Key findings
#	Question	Finding
Q1	Side-effect profile	Liraglutide (178 hospitalizations per 1,000 reports) and semaglutide (160/1,000) lead; tirzepatide is lowest (24/1,000), but this reflects launch-curve compression and the Weber effect, not a safety advantage.
Q2	Search vs. equity	Ozempic search interest correlates strongly with NVO (r = 0.892) and LLY (r = 0.865) prices, p ≪ 0.001, n = 100 months — but the link only materializes after 2022, when the category went mainstream.
Q3	Geography	The US accounts for ~91% of geo-tagged reports (47K of 52K) — an artifact of openFDA's submission funnel, not an exposure map. On search, Saudi Arabia outpaces the US and India shows the largest 2018→2025 growth.
Q4	Demographics	Reports skew female and middle-aged, with a sharp gradient: tirzepatide 84% female / median age 48 vs. exenatide 61% / age 62 — tracking weight-loss vs. legacy T2D indications.
Q5	Trial pipeline	1,953 trials across 9 drugs; Novo Nordisk (19.9%) and Eli Lilly (10.6%) lead, but 611 distinct sponsors put the HHI at 550 — a competitive market by FTC thresholds.
Q6	Next generation	106 investigational trials (orforglipron 45, CagriSema 32, retatrutide 29), with completions clustering in 2025–2027 — the competitive picture resolves within ~24 months.
Q7	Anomaly detection	A 6-month rolling z-score flagged 71 drug-months at abs(z) > 2, clustering in 2014–2016 and 2021–2024. Only 3 of 71 map to known events, suggesting reporting-cycle dynamics rather than discrete drug signals.
Full write-up with figures in `report.md`. The chronological audit trail — every assumption, scoping call, and data gap — is in `outputs/findings_log.md`.
Methods
Pipeline: modular `src/` with typed loaders and an idempotent Kaggle download (safe to wire into cron or a GitHub Action).
Cleaning: deduplication, age normalization, ISO-3 country mapping.
Statistics: Pearson and rolling 12-month correlation, per-1,000 rate normalization, Herfindahl-Hirschman index for sponsor concentration, 6-month rolling z-score for anomaly detection.
Reproducibility: one CSV source table per figure in `outputs/tables/`, so every chart in the report is traceable back to its inputs.
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
