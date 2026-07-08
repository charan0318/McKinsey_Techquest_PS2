# SummitBridge Health Plan - Member Months Data Dictionary

## Table Overview
| Attribute | Value |
|-----------|-------|
| **Table Name** | `member_months` |
| **Source System** | Enrollment/Eligibility System (derived) |
| **Grain** | Member × Plan × Month (one row per member per plan per calendar month) |
| **Refresh Frequency** | Monthly (5th business day) |
| **Analysis Period** | 2024-01-01 to 2024-12-31 |
| **Row Count** | 8,462 |
| **Primary Key** | Composite: `member_id` + `plan_id` + `calendar_month` |

---

## Column Definitions

### Identifiers
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `member_id` | string | Member identifier | `M-000001` | No | Foreign key to enrollment |
| `plan_id` | string | Plan identifier | `PLN-COM-250` | No | Foreign key to plan |
| `lob` | category | Line of business | `Commercial`, `Marketplace`, `Medicare Advantage` | No | **Key segmentation** |

### Geography
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `state` | category | Member residence state | `KY`, `GA`, `TN`, `OH` | No | **Key geographic dimension** |

### Time
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `calendar_month` | datetime | First day of calendar month | `2024-02-01` | No | **Primary time dimension** |

### Exposure
| Column | Type | Description | Values | Nullable | Notes |
|--------|------|-------------|--------|----------|-------|
| `member_months` | int64 | Exposure count for month | `1`, `0` | No | **1 = enrolled full month, 0 = not enrolled** |

---

## Data Quality Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| `member_months` IN (0, 1) | 100% | Validate |
| `calendar_month` first day of month | 100% | Validate |
| Each member has ≤ 12 rows per year | 100% | Dedupe |
| `member_id` exists in enrollment | >99% | Investigate orphans |
| `plan_id` + `lob` consistent with enrollment | 100% | Validate |
| Sum of `member_months` per member = enrollment months in period | 100% | Reconcile |

---

## Join Keys

| This Table | Joins To | On Column(s) | Type |
|------------|----------|--------------|------|
| `member_months` | `enrollment` | `member_id`, `plan_id`, `lob` | Many-to-One |
| `member_months` | `claims` | `member_id` (via member) | Many-to-Many |

---

## Derived Fields (Added in Enriched Layer)

| Field | Logic | Purpose |
|-------|-------|---------|
| `calendar_year` | `YEAR(calendar_month)` | Yearly aggregation |
| `calendar_quarter` | `QUARTER(calendar_month)` | Quarterly aggregation |
| `is_enrolled` | `member_months` = 1 | Enrollment flag |
| `member_month_key` | `member_id` + `_` + `FORMAT(calendar_month, 'yyyyMM')` | Unique key |

---

## Key Calculations

### Total Member Months (Exposure)
```sql
SELECT SUM(member_months) as total_member_months
FROM member_months
WHERE calendar_month BETWEEN '2024-01-01' AND '2024-12-31';
```

### Member Months by LOB
```sql
SELECT lob, SUM(member_months) as member_months
FROM member_months
WHERE calendar_month BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY lob;
```

### Member Months by State
```sql
SELECT state, SUM(member_months) as member_months
FROM member_months
WHERE calendar_month BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY state;
```

### PMPM Calculation (Requires Claims Join)
```sql
```sql
WITH member_allowed AS (
  SELECT member_id, SUM(allowed_amount) as total_allowed
  FROM claims
  WHERE service_from_date BETWEEN '2024-01-01' AND '2024-12-31'
  GROUP BY member_id
),
member_exposure AS (
  SELECT member_id, SUM(member_months) as total_mm
  FROM member_months
  WHERE calendar_month BETWEEN '2024-01-01' AND '2024-12-31'
  GROUP BY member_id
)
SELECT 
  COALESCE(ma.member_id, me.member_id) as member_id,
  COALESCE(ma.total_allowed, 0) as total_allowed,
  COALESCE(me.total_mm, 0) as member_months,
  COALESCE(ma.total_allowed, 0) / NULLIF(me.total_mm, 0) as pmpm
FROM member_allowed ma
FULL OUTER JOIN member_exposure me ON ma.member_id = me.member_id;
```

---

## Notes

- **Exposure Table**: This is the denominator for all PMPM and rate calculations
- **Monthly Grain**: Enables trend analysis, seasonality detection, monthly KPI tracking
- **Zero Rows**: Members with `member_months` = 0 for a month are not enrolled that month
- **Consistency**: Must reconcile with enrollment start/end dates
- **Actuarial Use**: Primary exposure basis for rate setting, reserving, trend analysis