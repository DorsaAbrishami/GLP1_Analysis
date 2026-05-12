# GLP-1 Analysis — Running Findings & Limitations Log

A chronological log of issues, data caveats, and key numbers as each notebook
runs. Each notebook appends to its section. `report.md` synthesizes these.

---

## 01 — Data Exploration

### Findings
- 8 CSVs loaded successfully from `data/raw/`; total ~169k rows of useful data.
- Heaviest file is `adverse_events.csv`: **149,209** reaction-level rows
  (~54k unique `safetyreportid` after dedup).
- Date coverage:
  - FAERS: **2012-11-23 → 2025-01-17** (slightly wider than the advertised 2017-2026).
  - Trials `start_date`: 2004-05-28 → 2027-09-01.
  - Stocks: covers 2017 onward for LLY + NVO.
  - Search trends: **2018-01 → 2026-04**.
- 7 approved GLP-1 generics in FAERS:
  semaglutide, tirzepatide, liraglutide, dulaglutide, exenatide,
  lixisenatide, albiglutide.
- Clinical trials cover **9 of 10** drugs (CagriSema missing).

### Issues / Limitations
- **CagriSema (`cagrilintide-semaglutide`) has zero clinical-trial rows.**
  Q6 will cover only orforglipron + retatrutide and explicitly note the gap.
- `country='UNK'` is the **second-largest** country bucket in FAERS
  (~6,038 reports). Must be excluded from Q3 geo plots.
- Search trends covers only **7 geos** (US, GB, IN, PK, SA, AE, WORLD) and
  **5 terms** (GLP-1, Ozempic, Wegovy, Mounjaro, Zepbound). Q3 geographic
  search work is restricted to that footprint.
- `2017` isn't actually present in the trends data (starts 2018-01) — Q3
  growth comparisons will use 2018 vs 2025 instead.
- The `kaggle` Python package calls `sys.exit(1)` at import time when
  credentials are missing. Loader is guarded against this; analysis still
  runs off the cached CSVs even without Kaggle auth.

---

<!-- Subsequent notebooks append below. -->

## 02 — Side Effects (Q1)

### Findings
- Top 3 well-powered drugs by hospitalization-reporting rate: liraglutide (178/1,000, n=9,978), semaglutide (160/1,000, n=14,992), dulaglutide (102/1,000, n=4,994).
- lixisenatide is technically #3 by raw rate but with **n=19** the estimate is unreliable and was excluded from the headline.
- Lowest well-powered rate: tirzepatide (24/1,000, n=9,969) — tied with albiglutide (24/1,000, n=4,982). Tirzepatide is newest, so this likely reflects launch-curve / Weber-effect compression rather than intrinsically lower hospitalization risk.
- exenatide has the **highest death-reporting rate** (72/1,000, vs <35/1,000 for everyone else) — likely the oldest cohort + longest exposure tail.
- Highest-volume drug overall (most FAERS reports): semaglutide (14,992 reports).
- Dedup matters: file is 2.75x larger than the report-level table; ignoring it would over-count multi-reaction reports.

### Issues / Limitations
- Rates are reporting rates, not incidence — no exposure denominator available.
- Small-n drugs (n<500) with unstable rates: ['lixisenatide'].
- Weber-effect / channeling bias means newer drugs (tirzepatide, semaglutide) inflate vs older ones (exenatide).
- No causal inference is possible from FAERS alone.

---

## 03 — Stock vs Search (Q2)

### Findings
- Pearson r (Ozempic search vs LLY adj-close): **+0.865** (p=4.11e-31).
- Pearson r (Ozempic search vs NVO adj-close): **+0.892** (p=1.28e-35).
- Top 5 search-spike months (delta vs 3-mo baseline): 2023-01, 2023-02, 2023-03, 2024-03, 2024-05.
- Rolling 12-month r is broadly positive after 2022, suggesting the search/price link tightened once weight-loss use went viral.

### Issues / Limitations
- Google Trends is a relative index (0-100), not absolute search volume.
- Monthly aggregation hides intra-month moves.
- Strong correlation in the post-2022 era is partly mechanical: both series trend up.
- LLY's main GLP-1 is tirzepatide (Mounjaro/Zepbound), not Ozempic — Ozempic-vs-LLY is a *category* signal, not a product-level one.

---

## 04 — Geographic Patterns (Q3)

### Findings
- FAERS reporting is overwhelmingly US-centric: **US** = 47,414 reports (91% of all geo-tagged reports). Top-10 list saved to `q3_faers_by_country.csv`.
- 72 countries appear in FAERS overall. After the US, the next-largest reporters are CA, GB, JP, BR — all <2% each.
- Trends — highest mean Ozempic search interest (excluding WORLD): **SA** (mean=31.0).
- Trends — biggest absolute growth 2018→2025: **IN** (+64.0 points).

### Issues / Limitations
- 1,844 reports (3.4% of total) have country='UNK' and were excluded.
- FAERS reporting volumes reflect openFDA reporter mix (US-dominated), not actual exposure or disease burden.
- Search trends covers only 6 real countries; this is not a global view.
- No population normalization — these are absolute counts, not per-capita rates.
- 'Growth' uses 2018 vs 2025 means; for geos that started at zero in 2018 the % growth is undefined (we flagged `from_zero=True` and used absolute change instead).
- True choropleth skipped to avoid geopandas/folium dependency churn — long-tail log bar chart is the substitute.

---

## 05 — Demographics (Q4)

### Findings
- Female skew is strongest for **tirzepatide** (84% female, weighted age 48).
- Lowest female share: **albiglutide** (58%).
- Oldest median-age cohort: **exenatide** (~62 yrs).
- Youngest median-age cohort: **tirzepatide** (~48 yrs).
- Across all GLP-1 drugs the cohort skews female and middle-aged — consistent with the obesity/T2D indications and the post-2022 weight-loss usage shift.

### Issues / Limitations
- `patient_age_unit` had to be normalized to years; raw `patient_age` mixed years/months/weeks.
- `patient_sex` is coded numerically in raw FAERS — defensive mapping needed.
- 'Top 5 reactions' is per-drug, so the heatmap is sparse where two drugs don't share their top reactions.
- % female / % male denominators exclude reports with unknown sex (separately reported as `pct_sex_unknown`).
- Demographics still reflect *who reports*, not *who is treated* — caregivers and family members file disproportionately for women and older patients.

---

## 06 — Clinical Trials (Q5)

### Findings
- 1,953 trials across 9 GLP-1 drugs, dates 2004-05-28 → 2027-09-01.
- Phase mix is heavy on PHASE3 (464) and PHASE4 (367), consistent with post-approval label-expansion work on the older drugs.
- Top sponsor: **Novo Nordisk A/S** with 388 trials (19.9%). Second: **Eli Lilly and Company** with 207 (10.6%).
- HHI = **550** → competitive (HHI < 1,500). Top-4 sponsors run 37% of all GLP-1 trials.
- Trials-started curves: exenatide and liraglutide peaked in the late 2000s / early 2010s; semaglutide and tirzepatide are still ramping.

### Issues / Limitations
- HHI here treats trial count as 'market share', which isn't a perfect proxy for clinical influence (a single huge phase-3 outweighs many small phase-1s).
- 'Phase' has multi-phase combos (`PHASE1, PHASE2`) — kept as their own buckets rather than split arbitrarily.
- `start_date` is sometimes the *planned* start (for not-yet-recruiting trials); year-on-year counts past 2024 may shift downward.
- Sponsor names aren't normalized (e.g. 'Novo Nordisk A/S' vs 'Novo Nordisk') — top-line numbers may slightly understate the biggest sponsors.

---

## 07 — Investigational Drugs (Q6)

### Findings
- Trial counts (after expanding the search to `brief_title`): orforglipron=45, retatrutide=29, CagriSema=32.
- Active vs completed (Active / Completed): orforglipron 14/31, retatrutide 14/15, CagriSema 10/18.
- orforglipron leads on volume (oral GLP-1 from Lilly — easier to test = more trials), CagriSema and retatrutide are catching up.
- Most trials expected to read out in **2025** (24 trials).

### Issues / Limitations
- CagriSema is *not* tagged under `drug_query`; recovered only by searching `brief_title` for 'cagrisema' / 'cagrilintide'. Tag-precision is therefore lower for that drug.
- 'First-match wins' tagging means a trial that mentions both retatrutide and orforglipron gets only one tag (CagriSema first, then orforglipron, then retatrutide) — true cross-drug head-to-heads are rare but possible.
- `completion_date` is anticipated for not-yet-completed trials and can slip; the Gantt represents *planned*, not actual, dates for ongoing trials.
- Trials without a `completion_date` are excluded from the Gantt and completion-year charts.

---

## 08 — Anomaly Detection (Q7)

### Findings
- 71 drug-months flagged at |z|>2 (rolling 6m window).
- Two clear anomaly waves:
  - **2014-2016** (~28 flags) — exenatide-XR / liraglutide ramp era, albiglutide trial failures.
  - **2021-2024** (~28 flags) — semaglutide weight-loss expansion, tirzepatide launch, viral Ozempic cycle.
- Drug with the most anomalies: **tirzepatide** (18) and **semaglutide** (18) tied — both are the high-volume modern launches whose z-scores spike during rapid growth.
- Only **3 of 71** anomalies match an entry in `KNOWN_EVENTS` — most spikes are *not* aligned with the few hand-curated events, suggesting either (a) the event list needs to be extended or (b) most z-spikes are reporting-cycle artifacts (Weber effect, lawsuit volume) rather than discrete events.

### Issues / Limitations
- Rolling z-score assumes (locally) normal data. FAERS counts are integer / right-skewed; |z|>2 over-flags during fast-growing regimes (early launches).
- Window=6 was chosen for simplicity; a 12-month window halves the flag rate, a 3-month doubles it.
- A spike can be reporting-driven (lawsuit, news cycle, MedWatch outreach) as well as drug-driven.
- `KNOWN_EVENTS` is hand-curated and English/US-centric.
- The newest months are noisier because the rolling baseline has fewer prior observations.

---
