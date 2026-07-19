# Ethiopia Financial Inclusion Forecasting System

**Client:** National Bank of Ethiopia consortium (DFIs, mobile money operators, NBE)  
**Analyst:** Dag Dagne — Selam Analytics  
**Period:** 2026 Week 11 Challenge  

---

## Overview

This project builds a forecasting system that predicts Ethiopia's progress on two core financial inclusion dimensions defined by the World Bank's Global Findex:

| Dimension | Indicator | 2024 Baseline |
|-----------|-----------|---------------|
| **Access** | Account Ownership Rate | 49% |
| **Usage** | Digital Payment Adoption Rate | ~35% |

Forecasts are produced for **2025, 2026, and 2027** using trend regression augmented with event impact modelling.

---

## Project Structure

```
ethiopia-fi-forecast/
├── .github/workflows/
│   └── unittests.yml           # CI pipeline
├── data/
│   ├── raw/                    # Original starter dataset (do not modify)
│   │   ├── ethiopia_fi_unified_data.xlsx
│   │   ├── reference_codes.xlsx
│   │   └── Additional Data Points Guide.xlsx
│   └── processed/              # Enriched analysis-ready data
│       ├── ethiopia_fi_enriched.csv
│       └── impact_links_enriched.csv
├── notebooks/
│   ├── 01_task1_data_exploration_enrichment.ipynb
│   └── 02_task2_eda.ipynb
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # Load raw/processed data
│   └── enrich_data.py          # Enrichment logic + new records
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
├── tests/
│   └── test_data_loader.py
├── models/                     # Saved forecast model outputs
├── reports/figures/            # Generated charts
├── data/data_enrichment_log.md # Documents every data addition
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd ethiopia-fi-forecast

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run data enrichment
python -m src.enrich_data

# 5. Launch the dashboard
streamlit run dashboard/app.py
```

---

## Tasks

| Task | Description | Status |
|------|-------------|--------|
| Task 1 | Data Exploration & Enrichment | ✅ Complete |
| Task 2 | Exploratory Data Analysis | ✅ Complete |
| Task 3 | Event Impact Modelling | ✅ Complete |
| Task 4 | Forecasting 2025–2027 | ✅ Complete |
| Task 5 | Interactive Dashboard | ✅ Complete |

---

## Key Findings (Preview)

- Ethiopia's account ownership grew from **14% (2011) → 49% (2024)** — a remarkable 35pp rise
- The 2021–2024 slowdown (+3pp only) despite 65M+ mobile accounts is explained by the **registered vs active gap** and a **Findex methodology shift**
- The **P2P/ATM crossover** in late 2024 signals genuine usage shift, not just registration
- **Gender gap** narrowed from ~16pp (2017) to ~18pp (2021) to ~18pp (2024) — stubborn but slowly improving
- Forecast: Access reaches **56–62%** by 2027 under base scenario; Usage reaches **44–50%**

---

## Data Sources

- [World Bank Global Findex 2024](https://www.worldbank.org/en/publication/globalfindex)
- [IMF Financial Access Survey](https://data.imf.org/fas)
- [GSMA Mobile Economy SSA 2024](https://www.gsma.com/mobileeconomy/sub-saharan-africa/)
- [Ethio Telecom Reports](https://www.ethiotelecom.et)
- [EthSwitch Annual Reports](https://www.ethswitch.com)
- [National Bank of Ethiopia](https://nbe.gov.et)
- [Fayda / NIDP](https://id.gov.et)

---

## Running Tests

```bash
python -m pytest tests/ -v
```
