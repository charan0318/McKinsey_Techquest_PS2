# SummitBridge Health Plan - Enrollment Data Dictionary

## Table Overview
| Attribute | Value |
|-----------|-------|
| **Table Name** | `enrollment` |
| **Source System** | Enrollment/Eligibility System |
| **Grain** | Member enrollment span (one row per member per enrollment period) |
| **Refresh Frequency** | Daily |
| **Analysis Period** | 2024-01-01 to 2024-12-31 |
| **Row Count** | 800 |
| **Primary Key** | `member_id` (business key) |
| **SCD Type** | Type 2 (track enrollment changes, disenrollment reason) |

---

## Column Definitions

### Identifiers
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `member_id` | string | Unique member identifier | `M-000001` | No | Primary key |
| `subscriber_id` | string | Subscriber/policyholder ID | `S-000001` | No | For group plans, may = member_id |

### Enrollment Dates
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `enrollment_start_date` | datetime | Coverage effective date | `2024-02-19` | No | **Primary analysis date** |
| `enrollment_end_date` | datetime | Coverage termination date | `2024-06-05` | Yes | Null = currently enrolled |

### Plan & Product
| Column | Type | Description | Values | Nullable | Notes |
|--------|------|-------------|--------|----------|-------|
| `plan_id` | string | Plan identifier | `PLN-COM-250` | No | Links to claims, member_months |
| `lob` | category | Line of business | `Commercial`, `Marketplace`, `Medicare Advantage` | No | **Key segmentation** |
| `product_name` | string | Marketing product name | `PPO Gold`, `Bronze HMO`, `Silver HMO` | Yes | Benefit design detail |
| `group_id` | string | Employer group ID | `GRP-ACME-01` | Yes | Null for individual plans |

### Geography
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `state` | category | Member residence state | `KY`, `GA`, `TN`, `OH` | No | **Key geographic dimension** |
| `county` | string | Member residence county | `Jefferson`, `Fulton`, `Davidson` | Yes | Network adequacy analysis |
| `zip` | string | Member residence ZIP | `40202`, `30303`, `37203` | Yes | Granular geo analysis |

### Demographics
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `age` | int64 | Member age at enrollment | `53`, `36`, `24` | No | **Key risk dimension** |
| `gender` | category | Member gender | `M`, `F` | No | |
| `risk_score` | float64 | CMS-HCC or internal risk score | `0.82`, `1.27`, `2.08` | No | **Risk adjustment** |

### Provider Attribution
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `attributed_pcp_npi` | int64 | Attributed PCP NPI | `9012345678` | Yes | Links to provider quality |

### Disenrollment
| Column | Type | Description | Values | Nullable | Notes |
|--------|------|-------------|--------|----------|-------|
| `disenrollment_reason` | category | Reason for termination | `Premium Affordability`, `Network Adequacy`, `Access Issues`, `Employer Change`, `Moved Out of Area` | Yes | **Null = active member** |

---

## Disenrollment Reason Definitions

| Reason | Description | Actionable? |
|--------|-------------|-------------|
| `Premium Affordability` | Member cites cost of premiums | Yes - benefit design, subsidies |
| `Network Adequacy` | Insufficient providers in area | Yes - network recruitment |
| `Access Issues` | Difficulty getting appointments | Yes - PCP access programs |
| `Employer Change` | Group coverage change | No - external factor |
| `Moved Out of Area` | Relocation outside service area | No - external factor |

---

## Data Quality Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| `enrollment_start_date` ≤ `enrollment_end_date` (when not null) | 100% | Fix dates |
| `age` between 0 and 100 | 100% | Validate |
| `risk_score` > 0 | 100% | Validate |
| `member_id` unique per enrollment span | 100% | Dedupe |
| Active members (`enrollment_end_date` IS NULL) have no disenrollment_reason | 100% | Fix |
| Terminated members have disenrollment_reason | >95% | Investigate |

---

## Join Keys

| This Table | Joins To | On Column(s) | Type |
|------------|----------|--------------|------|
| `enrollment` | `claims` | `member_id` | One-to-Many |
| `enrollment` | `member_months` | `member_id`, `plan_id`, `lob` | One-to-Many |
| `enrollment` | `providers` | `attributed_pcp_npi` = `npi` | Many-to-One |

---

## Derived Fields (Added in Enriched Layer)

| Field | Logic | Purpose |
|-------|-------|---------|
| `enrollment_months` | Months between start/end (or analysis end) | Tenure calculation |
| `is_active` | `enrollment_end_date` IS NULL | Active filter |
| `age_band` | CASE WHEN age < 18 THEN '0-17' ... | Age segmentation |
| `risk_tier` | CASE WHEN risk_score < 1.0 THEN 'Low' ... | Risk stratification |
| `disenrolled_in_period` | `enrollment_end_date` BETWEEN analysis_start AND analysis_end | Churn analysis |

---

## Sample Queries

### Active Members by LOB and State
```sql
SELECT lob, state, COUNT(*) as member_count
FROM enrollment
WHERE enrollment_end_date IS NULL
  AND enrollment_start_date <= '2024-12-31'
GROUP BY lob, state
ORDER BY lob, state;
```

### Disenrollment Analysis
```sql
SELECT disenrollment_reason, lob, state, COUNT(*) as count
FROM enrollment
WHERE disenrollment_reason IS NOT NULL
  AND enrollment_end_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY disenrollment_reason, lob, state
ORDER BY count DESC;
```

### Member Risk Profile
```sql
SELECT 
  lob,
  AVG(risk_score) as avg_risk_score,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY risk_score) as median_risk_score,
  COUNT(*) as member_count
FROM enrollment
WHERE enrollment_end_date IS NULL
GROUP BY lob;
```

### PCP Attribution Coverage
```sql
SELECT 
  lob,
  COUNT(*) as total_members,
  COUNT(attributed_pcp_npi) as attributed_members,
  COUNT(attributed_pcp_npi) * 1.0 / COUNT(*) as attribution_rate
FROM enrollment
WHERE enrollment_end_date IS NULL
GROUP BY lob;
```