# SummitBridge Health Plan - Claims Data Dictionary

## Table Overview
| Attribute | Value |
|-----------|-------|
| **Table Name** | `claims` |
| **Source System** | Claims Administration System (Medical & Pharmacy) |
| **Grain** | Claim line (one row per service line on a claim) |
| **Refresh Frequency** | Daily (paid date), Monthly (incurred date complete) |
| **Analysis Period** | 2024-01-01 to 2024-12-31 |
| **Row Count** | 5,961 |
| **Primary Key** | `claim_id` (business key), composite: `claim_id` + `service_from_date` + `rendering_npi` |

---

## Column Definitions

### Identifiers
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `claim_id` | string | Unique claim identifier | `CLM-000001` | No | Business key from source system |
| `member_id` | string | Member identifier | `M-000001` | No | Foreign key to enrollment |
| `rendering_npi` | int64 | NPI of rendering provider | `9012345678` | Yes | May differ from billing NPI |
| `billing_npi` | int64 | NPI of billing provider | `9012345678` | Yes | For facility claims, often same as rendering |
| `authorization_id` | string | Prior authorization number | `AUTH-12345` | Yes | Null if no PA required |
| `plan_id` | string | Plan identifier | `PLN-COM-250` | No | Foreign key to plan dimension |

### Dates
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `service_from_date` | datetime | First date of service | `2024-12-21` | No | **Primary analysis date** |
| `service_to_date` | datetime | Last date of service | `2024-12-21` | No | For inpatient: discharge date |
| `paid_date` | datetime | Date claim was paid | `2025-01-16` | No | Used for cash flow, IBNR |

### Claim Classification
| Column | Type | Description | Values | Nullable | Notes |
|--------|------|-------------|--------|----------|-------|
| `claim_type` | category | Claim category | `Professional`, `Pharmacy`, `Institutional` | No | Derived from source system |
| `service_category` | category | Clinical service grouping | `Inpatient`, `ED`, `Specialty Rx`, `PCP`, `Urgent Care`, `Behavioral Health` | No | **Key analytic dimension** |
| `place_of_service_code` | int64 | CMS POS code | `11`, `20`, `21`, `22`, `23` | Yes | See POS mapping below |

### Clinical Codes
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `diagnosis_code_1` | string | Primary ICD-10-CM diagnosis | `F32.9`, `I10`, `J06.9` | Yes | Used for avoidable ED classification |
| `procedure_code` | string | CPT/HCPCS procedure code | `99213`, `90837`, `99284` | Yes | Professional claims |
| `ndc_code` | string | National Drug Code (11-digit) | `00002321401` | Yes | Pharmacy claims only |
| `drug_name` | string | Drug name | `Pembrolizumab`, `Semaglutide` | Yes | Specialty Rx only |
| `therapeutic_class` | string | Therapeutic classification | `Oncology Biologic`, `GLP-1 Agonist` | Yes | Specialty Rx only |

### Financial
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `units` | int64 | Service units (days, visits, scripts) | `1`, `30`, `4` | No | Default 1 |
| `billed_amount` | float64 | Provider billed charges | `268.29` | No | Gross charges |
| `allowed_amount` | float64 | **Primary cost metric** - negotiated rate | `198.73` | No | **Use for all analytics** |
| `paid_amount` | float64 | Plan paid amount | `158.98` | No | After member cost share |
| `member_cost_share` | float64 | Member responsibility (copay/coinsurance/deductible) | `39.75` | No | Patient liability |

### Network & Admission
| Column | Type | Description | Values | Nullable | Notes |
|--------|------|-------------|--------|----------|-------|
| `in_network_flag` | category | Network status | `Y`, `N` | No | `Y`=In-network, `N`=Out-of-network |
| `admission_type` | int64 | Admission type (institutional) | `1`=Emergency, `2`=Urgent, `3`=Elective | Yes | Institutional only |
| `discharge_status` | int64 | Patient discharge status | `1`=Home, `2`=Transfer, `3`=SNF, `20`=Expired | Yes | Institutional only |

### Line of Business
| Column | Type | Description | Values | Nullable | Notes |
|--------|------|-------------|--------|----------|-------|
| `lob` | category | Line of business | `Commercial`, `Marketplace`, `Medicare Advantage` | No | **Key segmentation dimension** |

---

## Place of Service Code Mapping

| POS Code | Description | Service Category Mapping |
|----------|-------------|-------------------------|
| `11` | Office | PCP, Behavioral Health, Specialist |
| `20` | Urgent Care Facility | Urgent Care |
| `21` | Inpatient Hospital | Inpatient |
| `22` | Outpatient Hospital | ED, Outpatient Surgery, Specialty Rx (infusion) |
| `23` | Emergency Room - Hospital | ED |

---

## Service Category Definitions

| Category | Claim Types | POS Codes | Key Characteristics |
|----------|-------------|-----------|---------------------|
| **Inpatient** | Institutional | 21 | Admission required, high cost ($16K avg) |
| **ED** | Institutional/Professional | 23 | Emergency dept, avoidable classification available |
| **Specialty Rx** | Pharmacy | 22 (infusion), 11 (self-admin) | High-cost drugs, PA required, 4 drugs |
| **PCP** | Professional | 11 | Primary care visits, low cost ($150 avg) |
| **Urgent Care** | Professional | 20 | Walk-in, lower cost than ED ($135 avg) |
| **Behavioral Health** | Professional | 11, 22 | Therapy, psychiatry, low unit cost ($175 avg) |

---

## Data Quality Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| `allowed_amount` > 0 | 100% | Reject/quarantine |
| `service_from_date` within analysis period | 100% | Filter |
| `member_id` exists in enrollment | >99% | Investigate orphans |
| `rendering_npi` exists in provider directory | >95% | Update provider directory |
| Duplicate claim lines (same claim_id, service_from_date, rendering_npi, procedure_code) | <0.1% | Dedupe logic |
| `allowed_amount` outliers (>3 SD from category mean) | Flag | Validate with actuarial |

---

## Join Keys

| This Table | Joins To | On Column(s) | Type |
|------------|----------|--------------|------|
| `claims` | `enrollment` | `member_id` | Many-to-One |
| `claims` | `member_months` | `member_id`, `plan_id`, `lob` | Many-to-Many (via member) |
| `claims` | `providers` | `rendering_npi` = `npi` | Many-to-One |
| `claims` | `avoidable_ed_reference` | `diagnosis_code_1` = `icd10_code` | Many-to-One (ED only) |

---

## Derived Fields (Added in Enriched Layer)

| Field | Logic | Purpose |
|-------|-------|---------|
| `is_high_cost_member` | Member in top 5% by total allowed | High-cost flag |
| `is_avoidable_ed` | `avoidable_category` IN ('Avoidable', 'Potentially Avoidable') | ED diversion target |
| `service_month` | `DATE_TRUNC('month', service_from_date)` | Monthly aggregation |
| `allowed_pmpm` | `allowed_amount` / member_months | PMPM calculation |
| `claim_year` | `YEAR(service_from_date)` | Yearly trends |

---

## Sample Queries

### Total Allowed by Service Category
```sql
SELECT service_category,
       COUNT(*) as claim_count,
       SUM(allowed_amount) as total_allowed,
       AVG(allowed_amount) as avg_allowed,
       COUNT(DISTINCT member_id) as unique_members
FROM claims
WHERE service_from_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY service_category
ORDER BY total_allowed DESC;
```

### High-Cost Members (Top 5%)
```sql
WITH member_spend AS (
  SELECT member_id, SUM(allowed_amount) as total_allowed
  FROM claims
  WHERE service_from_date BETWEEN '2024-01-01' AND '2024-12-31'
  GROUP BY member_id
),
threshold AS (
  SELECT QUANTILE(total_allowed, 0.95) as p95_threshold FROM member_spend
)
SELECT ms.member_id, ms.total_allowed
FROM member_spend ms, threshold t
WHERE ms.total_allowed >= t.p95_threshold
ORDER BY ms.total_allowed DESC;
```

### Avoidable ED Visits
```sql
SELECT c.diagnosis_code_1, a.avoidable_category,
       COUNT(*) as visit_count,
       SUM(c.allowed_amount) as total_allowed,
       AVG(c.allowed_amount) as avg_allowed
FROM claims c
JOIN avoidable_ed_reference a ON c.diagnosis_code_1 = a.icd10_code
WHERE c.service_category = 'ED'
  AND c.service_from_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY c.diagnosis_code_1, a.avoidable_category
ORDER BY visit_count DESC;
```