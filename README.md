# SummitBridge Health Plan - Healthcare Analytics Platform

## Overview
Comprehensive analytics platform for SummitBridge Health Plan addressing:
- **High-Cost Claimant & Specialty Spend Optimization** (Top 5% = 20.5% of spend)
- **Avoidable Utilization Reduction** (76% of ED visits avoidable = $1.03M)
- **Member Experience & Retention** (11.6% annual disenrollment)
- **Data-Driven Decision Making** (KPIs, dashboards, actuarial integration)

## Project Structure
```
summitbridge-analytics/
├── 01_business_understanding/    # Problem framing, stakeholders, success criteria
├── 02_data_dictionary/           # Column definitions, grain, types for all tables
├── 03_data_quality/              # DQ framework, reports, remediation log
├── 04_exploratory_analysis/      # 8 focused analysis notebooks
├── 05_kpi_models/                # KPI framework, calculations, baseline, dashboard
├── 06_savings_models/            # Scenario modeling for each intervention
├── 07_dashboard/                 # Executive, operational, financial, provider views
├── 08_documentation/             # Architecture, governance, roadmap, glossary
├── data/
│   ├── raw/                      # Original Excel files (gitignored)
│   ├── processed/                # Cleaned CSVs/Parquet
│   └── reference/                # Lookup tables (avoidable ED, ICD-10 maps)
├── src/                          # Reusable Python modules
│   ├── config.py
│   ├── data_loader.py
│   ├── kpi_calculator.py
│   ├── savings_model.py
│   └── utils.py
├── notebooks/                    # Symlinks to analysis notebooks
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Exploratory Analysis
```bash
jupyter notebook 04_exploratory_analysis/01_claims_overview.ipynb
```

### 3. Generate KPI Dashboard
```bash
jupyter notebook 05_kpi_models/kpi_dashboard.ipynb
```

### 4. Run Savings Scenarios
```bash
python src/savings_model.py --scenario combined --spec-pct 10 --ed-pct 20
```

## Key Findings (2024 Data)
| Metric | Current | Target |
|--------|---------|--------|
| High-Cost Concentration (Top 5%) | 20.5% | <15% |
| Avoidable ED Rate | 75.6% | <60% |
| ED Visits/1000 | 142.9 | <45 |
| 30-Day Readmission Rate | 6.1% | <12% |
| OON Allowed % | 1.2% | <1% |
| Annual Disenrollment Rate | 11.6% | <8% |
| Total Medical PMPM | $1,337.89 | <5% YoY trend |

## Project Progress

### Completed
- `01_business_understanding/` - case framing, stakeholders, success criteria
- `02_data_dictionary/` - source tables and derived table specs
- `03_data_quality/` - framework, reports, remediation log
- `04_exploratory_analysis/01_claims_overview.ipynb` - claims overview notebook
- `src/` - reusable data loading, KPI, savings, and utility modules

### Pending
- `04_exploratory_analysis/` - remaining 7 analysis notebooks
- `05_kpi_models/` - KPI calculations, dashboard, baseline report
- `06_savings_models/` - scenario notebooks and combined portfolio view
- `07_dashboard/` - executive, operational, financial, and provider dashboards
- `08_documentation/` - implementation roadmap, governance model, glossary

## Savings Opportunity: $500K - $1.2M Annually (4.4% - 10.6% of spend)

| Intervention | Annual Savings | Timeline |
|--------------|----------------|----------|
| Specialty PA & Biosimilars | $40K - $119K | 3-6 mo |
| Site-of-Care Shift (Infusion) | $100K - $200K | 6-12 mo |
| ED Diversion (20-40% shift) | $183K - $366K | 3-6 mo |
| High-Cost Care Management | $115K - $347K | 3-6 mo |
| Transitional Care (Readmissions) | $150K - $250K | 6-9 mo |
| Integrated BH/PCP Model | $150K - $250K | 12-18 mo |

## Data Sources
- **Claims**: 5,961 lines (Medical, Pharmacy, Institutional)
- **Enrollment**: 800 members across Commercial, Marketplace, Medicare Advantage
- **Member Months**: 8,462 exposure records
- **Providers**: 10 providers with quality scores
- **Avoidable ED Reference**: 12 ICD-10 codes classified

## Analysis Period
January 1, 2024 – December 31, 2024

## Metrics Definitions
- **PMPM** = Total Allowed Amount ÷ Member Months
- **ED Visits/1000** = (ED Claims ÷ Member Months) × 1,000
- **High-Cost** = Top 5% of members by allowed spend
- **Allowed Amount** = Primary cost metric (not paid/billed)

## Governance
- **Data Stewards**: Claims Ops, Membership, Network Management
- **Analytics Owner**: Director, Healthcare Analytics
- **Executive Sponsor**: CMO / CFO
- **Review Cadence**: Monthly (data quality), Quarterly (strategy)