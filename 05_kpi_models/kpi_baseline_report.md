# KPI Baseline Report — SummitBridge Analytics

Analysis period: 2024-01-01 to 2024-12-31

This document records baseline values and targets for the project's core KPIs (pulled from `kpi_framework.csv`). Use this as the single-source baseline for dashboarding and savings modeling.

| Domain | KPI | Current (baseline) | Target | Frequency | Owner |
|---|---:|---|---|---|---|
| High-Cost Claimants | High-Cost Member Concentration | 20.5% | <15% | Monthly | Care Management |
| High-Cost Claimants | High-Cost Member Count | 40 | Reduce by 10% YoY | Monthly | Care Management |
| Specialty Pharmacy | Specialty Rx PMPM | $93.50 | Reduce 10% YoY | Monthly | Pharmacy Benefits |
| Specialty Pharmacy | Specialty Rx Prior Auth Approval Rate | N/A (baseline needed) | 85-90% | Monthly | Pharmacy Benefits |
| ED Utilization | ED Visits per 1,000 Member Months | 142.9 | <45 | Monthly | Utilization Management |
| ED Utilization | Avoidable ED Visit Rate | 75.6% | <60% | Monthly | Utilization Management |
| ED Utilization | ED-to-Urgent Care Shift Rate | 0% (baseline) | 20% Yr1, 35% Yr2 | Monthly | Care Management |
| ED Utilization | PCP Visit Within 7 Days Post-ED | N/A (baseline needed) | >50% | Monthly | Care Management |
| Behavioral Health | BH Member ED Visit Rate | 1834.7 (per 1,000) | Reduce 15% YoY | Quarterly | Behavioral Health |
| Behavioral Health | BH Member IP Admission Rate | 661.2 (per 1,000) | Reduce 15% YoY | Quarterly | Behavioral Health |
| Behavioral Health | Follow-up Within 7 Days Post-BH Crisis | N/A (baseline needed) | >60% | Monthly | Behavioral Health |
| Readmissions | 30-Day All-Cause Readmission Rate | 6.1% | <12% | Monthly | Care Transitions |
| Readmissions | Post-Discharge PCP Visit Within 7 Days | N/A (baseline needed) | >70% | Monthly | Care Transitions |
| OON Leakage | Out-of-Network Allowed % | 1.2% | <1% | Monthly | Network Management |
| OON Leakage | Network Adequacy - Members per Provider | 24:1 (median) | <1,500:1 PCP; <3,000:1 Specialist | Quarterly | Network Management |
| Member Retention | Annual Disenrollment Rate | 11.6% | <8% | Monthly | Member Experience |
| Member Retention | Disenrollment Due to Cost/Access | 71.0% | <40% of disenrollments | Monthly | Member Experience |
| Member Retention | Cost Transparency Tool Adoption | 0% | >25% Year 1 | Quarterly | Digital/Marketing |
| Provider Quality | Member PMPM by PCP Quality Quartile | See analysis | Reduce gap by 20% | Quarterly | Provider Performance |
| Financial | Total Medical PMPM | $1337.89 | Medical cost trend <5% YoY | Monthly | Actuarial/Finance |
| Financial | Medical Loss Ratio (MLR) | N/A (premium needed) | 85-90% | Monthly | Actuarial/Finance |

Notes and next steps:

- Several KPIs currently state "N/A (baseline needed)" — collect claim sequencing (dates) and prior-auth / utilization management datasets to compute those baselines.
- The baseline values in this file are the canonical source for initial dashboard targets and savings model inputs.
- Action: implement monthly time-series KPI extracts to enable trend charts and cohort comparisons.

Prepared by: SummitBridge Analytics
Date: 2026-07-08
