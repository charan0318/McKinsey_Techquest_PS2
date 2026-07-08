# SummitBridge Health Plan - Derived Tables Specification

## Overview
Derived/mart tables built from raw sources for analytics, reporting, and dashboarding. These tables implement the semantic layer and business logic.

---

## 1. FCT_CLAIMS_ENRICHED (Daily Grain)

### Purpose
Single enriched fact table for all claims analytics. Joins claims to enrollment, providers, and reference data.

### Grain
Claim line (same as raw claims) + enriched dimensions

### Refresh
Daily (T+1 8:00 AM)

### Columns

| Column | Source | Logic |
|--------|--------|-------|
| All raw claims columns | `claims` | Pass through |
| `member_age` | `enrollment.age` | At service date |
| `member_gender` | `enrollment.gender` | |
| `member_state` | `enrollment.state` | |
| `member_county` | `enrollment.county` | |
| `member_lob` | `enrollment.lob` | |
| `member_risk_score` | `enrollment.risk_score` | |
| `member_attributed_pcp_npi` | `enrollment.attributed_pcp_npi` | |
| `member_disenrollment_reason` | `enrollment.disenrollment_reason` | |
| `rendering_provider_name` | `providers.provider_name` | |
| `rendering_provider_type` | `providers.provider_type` | |
| `rendering_specialty_desc` | `providers.specialty_desc` | |
| `rendering_network_status` | `providers.network_status` | |
| `rendering_quality_score` | `providers.quality_score` | |
| `rendering_accepting_new` | `providers.accepting_new_patients` | |
| `rendering_panel_size` | `providers.panel_size` | |
| `ed_avoidable_category` | `avoidable_ed_reference.avoidable_category` | Left join on diagnosis_code_1 |
| `ed_avoidable_description` | `avoidable_ed_reference.description` | |
| `is_high_cost_member` | Derived | Member in top 5% by rolling 12M allowed |
| `service_month` | Derived | `DATE_TRUNC('month', service_from_date)` |
| `service_year` | Derived | `YEAR(service_from_date)` |
| `service_quarter` | Derived | `QUARTER(service_from_date)` |
| `is_avoidable_ed` | Derived | `ed_avoidable_category` IN ('Avoidable', 'Potentially Avoidable') |
| `is_inpatient` | Derived | `service_category` = 'Inpatient' |
| `is_ed` | Derived | `service_category` = 'ED' |
| `is_specialty_rx` | Derived | `service_category` = 'Specialty Rx' |
| `is_pcp` | Derived | `service_category` = 'PCP' |
| `is_urgent_care` | Derived | `service_category` = 'Urgent Care' |
| `is_behavioral_health` | Derived | `service_category` = 'Behavioral Health' |

### Indexes
- Primary: `claim_id`, `service_from_date`, `rendering_npi`
- Partition: `service_month`
- Index: `member_id`, `service_month`
- Index: `is_high_cost_member`, `service_month`

---

## 2. FCT_MEMBER_MONTH_SUMMARY (Monthly Grain)

### Purpose
Member-level monthly summary for PMPM, utilization rates, and trend analysis.

### Grain
Member × Month

### Refresh
Monthly (5th business day)

### Columns

| Column | Logic |
|--------|-------|
| `member_id` | From member_months |
| `plan_id` | From member_months |
| `lob` | From member_months |
| `state` | From member_months |
| `calendar_month` | From member_months |
| `member_months` | From member_months (1 or 0) |
| `age` | From enrollment |
| `gender` | From enrollment |
| `risk_score` | From enrollment |
| `attributed_pcp_npi` | From enrollment |
| `disenrollment_reason` | From enrollment |
| `total_allowed` | SUM(allowed_amount) from claims in month |
| `total_paid` | SUM(paid_amount) from claims in month |
| `member_cost_share` | SUM(member_cost_share) from claims in month |
| `ip_admits` | COUNT(DISTINCT claim_id) WHERE service_category='Inpatient' |
| `ip_allowed` | SUM(allowed_amount) WHERE service_category='Inpatient' |
| `ed_visits` | COUNT(DISTINCT claim_id) WHERE service_category='ED' |
| `ed_allowed` | SUM(allowed_amount) WHERE service_category='ED' |
| `avoidable_ed_visits` | COUNT WHERE is_avoidable_ed=TRUE |
| `avoidable_ed_allowed` | SUM(allowed_amount) WHERE is_avoidable_ed=TRUE |
| `specialty_rx_scripts` | COUNT WHERE service_category='Specialty Rx' |
| `specialty_rx_allowed` | SUM(allowed_amount) WHERE service_category='Specialty Rx' |
| `pcp_visits` | COUNT WHERE service_category='PCP' |
| `pcp_allowed` | SUM(allowed_amount) WHERE service_category='PCP' |
| `uc_visits` | COUNT WHERE service_category='Urgent Care' |
| `uc_allowed` | SUM(allowed_amount) WHERE service_category='Urgent Care' |
| `bh_visits` | COUNT WHERE service_category='Behavioral Health' |
| `bh_allowed` | SUM(allowed_amount) WHERE service_category='Behavioral Health' |
| `oon_claims` | COUNT WHERE in_network_flag='N' |
| `oon_allowed` | SUM(allowed_amount) WHERE in_network_flag='N' |
| `high_cost_flag` | 1 if member in top 5% rolling 12M else 0 |
| `pmpm` | `total_allowed` / `member_months` (NULL if 0) |
| `ip_admits_per_1000` | `ip_admits` / `member_months` * 1000 |
| `ed_visits_per_1000` | `ed_visits` / `member_months` * 1000 |
| `specialty_rx_pmpm` | `specialty_rx_allowed` / `member_months` |

### Indexes
- Primary: `member_id`, `calendar_month`
- Partition: `calendar_month`
- Index: `lob`, `calendar_month`
- Index: `high_cost_flag`, `calendar_month`

---

## 3. DIM_HIGH_COST_MEMBERS (Monthly Snapshot)

### Purpose
Track high-cost member cohort over time for care management and trend analysis.

### Grain
Member × Month (snapshot)

### Refresh
Monthly (after FCT_MEMBER_MONTH_SUMMARY)

### Columns

| Column | Logic |
|--------|-------|
| `member_id` | |
| `snapshot_month` | First day of month |
| `rolling_12m_allowed` | SUM(allowed_amount) over prior 12 months |
| `rolling_12m_member_months` | SUM(member_months) over prior 12 months |
| `rolling_12m_pmpm` | `rolling_12m_allowed` / `rolling_12m_member_months` |
| `current_rank` | RANK() OVER (ORDER BY rolling_12m_allowed DESC) |
| `current_percentile` | PERCENT_RANK() OVER (ORDER BY rolling_12m_allowed) |
| `is_top_5_pct` | `current_percentile` >= 0.95 |
| `is_top_1_pct` | `current_percentile` >= 0.99 |
| `primary_cost_driver` | Service category with highest allowed in period |
| `ip_admits_12m` | COUNT inpatient admits in 12M |
| `ed_visits_12m` | COUNT ED visits in 12M |
| `specialty_rx_scripts_12m` | COUNT specialty Rx in 12M |
| `bh_visits_12m` | COUNT BH visits in 12M |
| `comorbidity_count` | COUNT DISTINCT diagnosis categories (CCSR) |
| `care_management_status` | 'Not Engaged', 'Engaged', 'Graduated', 'Declined' |
| `care_manager_id` | Assigned CM identifier |
| `last_cm_contact_date` | Most recent CM touch |
| `interventions_active` | JSON array of active interventions |
| `projected_savings` | Model-estimated savings from engagement |

### Indexes
- Primary: `member_id`, `snapshot_month`
- Index: `is_top_5_pct`, `snapshot_month`
- Index: `care_management_status`, `snapshot_month`

---

## 4. FCT_CARE_MANAGEMENT (Event Grain)

### Purpose
Track care management interventions, engagement, and outcomes for ROI measurement.

### Grain
Member × Intervention × Date

### Refresh
Weekly (Monday 8:00 AM)

### Columns

| Column | Logic |
|--------|-------|
| `member_id` | |
| `intervention_type` | 'High-Cost CM', 'Transitional Care', 'ED Diversion', 'BH Integration', 'Medication Reconciliation' |
| `intervention_start_date` | |
| `intervention_end_date` | NULL if ongoing |
| `care_manager_id` | |
| `engagement_status` | 'Outreach', 'Engaged', 'Active', 'Graduated', 'Declined', 'Lost' |
| `contact_count` | Cumulative contacts |
| `last_contact_date` | |
| `contact_mode` | 'Phone', 'Video', 'In-Person', 'Digital' |
| `clinical_outcomes` | JSON: {readmissions_avoided, ed_diverted, med_adherence_improved} |
| `financial_outcomes` | JSON: {allowed_savings, paid_savings, roi} |
| `barriers` | JSON array: ['Transportation', 'Health Literacy', 'SDoH', 'Provider Access'] |
| `sdoH_needs` | JSON array: ['Housing', 'Food', 'Employment', 'Social Support'] |

### Indexes
- Primary: `member_id`, `intervention_type`, `intervention_start_date`
- Index: `engagement_status`, `intervention_start_date`
- Index: `care_manager_id`, `intervention_start_date`

---

## 5. DIM_PROVIDER_PERFORMANCE (Quarterly)

### Purpose
Provider-level TCO, quality, and efficiency scorecards for VBC and network management.

### Grain
Provider (NPI) × Quarter

### Refresh
Quarterly (10th business day after quarter end)

### Columns

| Column | Logic |
|--------|-------|
| `npi` | |
| `provider_name` | |
| `provider_type` | |
| `specialty_desc` | |
| `network_status` | |
| `state` | |
| `quarter` | Quarter start date |
| `attributed_members` | COUNT DISTINCT members with this PCP |
| `total_allowed` | SUM allowed for attributed members |
| `pmpm` | `total_allowed` / attributed_member_months |
| `risk_adj_pmpm` | `pmpm` / avg risk_score |
| `ip_admits_per_1000` | |
| `ed_visits_per_1000` | |
| `specialty_rx_pmpm` | |
| `pcp_visit_rate` | PCP visits / attributed members |
| `quality_score` | From provider dimension |
| `hcc_coding_completeness` | HCCs captured / expected |
| `generic_dispensing_rate` | For attributed members |
| `ed_avoidable_rate` | Avoidable ED / total ED for attributed |
| `readmission_rate` | 30-day readmit for attributed |
| `efficiency_quartile` | NTILE(4) OVER (ORDER BY risk_adj_pmpm) |
| `quality_quartile` | NTILE(4) OVER (ORDER BY quality_score) |
| `vbc_eligible` | efficiency_quartile IN (1,2) AND quality_quartile IN (3,4) |

### Indexes
- Primary: `npi`, `quarter`
- Index: `vbc_eligible`, `quarter`
- Index: `efficiency_quartile`, `quality_quartile`, `quarter`

---

## Build Dependencies

```
Raw Tables (02_data_dictionary)
    │
    ├── claims ──────────────────────┐
    ├── enrollment ──────────────────┤
    ├── member_months ───────────────┼──▶ FCT_CLAIMS_ENRICHED (Daily)
    ├── providers ───────────────────┤
    └── avoidable_ed_reference ──────┘
                │
                ▼
    FCT_CLAIMS_ENRICHED + member_months
                │
                ▼
    FCT_MEMBER_MONTH_SUMMARY (Monthly)
                │
                ▼
    DIM_HIGH_COST_MEMBERS (Monthly Snapshot)
                │
                ▼
    FCT_CARE_MANAGEMENT (Weekly)
                │
                ▼
    DIM_PROVIDER_PERFORMANCE (Quarterly)
```

---

## Data Quality Checks per Table

| Table | Check | Frequency | Threshold |
|-------|-------|-----------|-----------|
| FCT_CLAIMS_ENRICHED | Row count vs raw claims | Daily | 100% match |
| FCT_CLAIMS_ENRICHED | Member match rate | Daily | >99% |
| FCT_CLAIMS_ENRICHED | Provider match rate | Daily | >95% |
| FCT_CLAIMS_ENRICHED | Avoidable ED coverage | Daily | >95% of ED claims |
| FCT_MEMBER_MONTH_SUMMARY | Member month reconciliation | Monthly | 100% vs member_months |
| FCT_MEMBER_MONTH_SUMMARY | PMPM outlier rate | Monthly | <1% >3 SD |
| DIM_HIGH_COST_MEMBERS | Top 5% stability | Monthly | <10% turnover MoM |
| FCT_CARE_MANAGEMENT | Engagement tracking | Weekly | 100% active members have contact |
| DIM_PROVIDER_PERFORMANCE | Attribution completeness | Quarterly | >95% members attributed |

---

## Retention Policy

| Table | Retention | Archive Strategy |
|-------|-----------|------------------|
| FCT_CLAIMS_ENRICHED | 3 years online, 7 years archive | Partition by year, compress |
| FCT_MEMBER_MONTH_SUMMARY | 5 years online, 10 years archive | Partition by year |
| DIM_HIGH_COST_MEMBERS | 3 years (snapshots) | Keep all snapshots |
| FCT_CARE_MANAGEMENT | 3 years | Keep all events |
| DIM_PROVIDER_PERFORMANCE | 5 years | Keep all quarters |