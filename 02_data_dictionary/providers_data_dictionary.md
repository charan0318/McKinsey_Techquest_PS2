# SummitBridge Health Plan - Providers Data Dictionary

## Table Overview
| Attribute | Value |
|-----------|-------|
| **Table Name** | `providers` |
| **Source System** | Provider Directory / Credentialing System |
| **Grain** | Provider (NPI) - one row per provider |
| **Refresh Frequency** | Monthly |
| **Analysis Period** | 2024-01-01 to 2024-12-31 |
| **Row Count** | 10 (sample) / ~18,000 (production) |
| **Primary Key** | `npi` (National Provider Identifier) |

---

## Column Definitions

### Identifiers
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `provider_id` | string | Internal provider ID | `PRV-001` | No | System-generated |
| `npi` | int64 | National Provider Identifier | `2345678901` | No | **Primary key**, 10-digit |

### Provider Info
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `provider_name` | string | Provider/organization name | `Dr. Emily Carter`, `Blue Ridge Oncology` | No | |
| `provider_type` | category | Individual vs Organization | `Individual`, `Organization` | No | Key distinction |

### Specialty
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `specialty_code` | string | Taxonomy code | `207Q00000X` | Yes | NUCC taxonomy |
| `specialty_desc` | string | Specialty description | `Family Medicine`, `Medical Oncology` | Yes | **Key analytic dimension** |

### Network Status
| Column | Type | Description | Values | Nullable | Notes |
|--------|------|-------------|--------|----------|-------|
| `network_status` | category | Contract status | `In-Network`, `Out-of-Network` | No | **Critical for OON analysis** |

### Contract Dates
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `contract_effective_date` | datetime | Contract start | `2022-01-01` | No | |
| `contract_term_date` | datetime | Contract end | `2025-12-31` | Yes | Null = active |

### Affiliation & Location
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `facility_affiliation` | string | Health system/group | `Summit Primary Care`, `Blue Ridge Health` | Yes | For organization providers |
| `city` | string | Practice city | `Columbus`, `Louisville` | Yes | |
| `state` | category | Practice state | `OH`, `KY`, `TN` | Yes | **Geographic dimension** |
| `zip` | string | Practice ZIP | `43215`, `40202` | Yes | |
| `latitude` | float64 | Latitude | `39.9612` | Yes | Geo-mapping |
| `longitude` | float64 | Longitude | `-82.9988` | Yes | Geo-mapping |

### Capacity & Quality
| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `accepting_new_patients` | category | Panel open status | `Y`, `N` | Yes | **Access metric** |
| `quality_score` | float64 | Quality composite (1-5) | `4.2`, `3.8`, `4.5` | Yes | **Key quality metric** |
| `panel_size` | int64 | Attributed member count | `1850`, `1620`, `420` | Yes | For individual PCPs |

---

## Specialty Categories (Sample)

| Specialty Code | Description | Type | Typical Network Status |
|----------------|-------------|------|------------------------|
| `207Q00000X` | Family Medicine | Individual | In-Network |
| `207R00000X` | Internal Medicine | Individual | In-Network |
| `207RX0202X` | Medical Oncology | Organization | In-Network |
| `261QU0200X` | Urgent Care | Organization | In-Network |
| `207X00000X` | Orthopedic Surgery | Individual | In-Network |

---

## Data Quality Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| `npi` valid 10-digit with Luhn check | 100% | Reject invalid |
| `quality_score` between 1.0 and 5.0 | 100% | Validate |
| `panel_size` ≥ 0 for individuals | 100% | Validate |
| `contract_effective_date` ≤ `contract_term_date` (when not null) | 100% | Fix dates |
| In-network providers have active contract | 100% | Validate |
| PCPs (`specialty_desc` IN Family/Internal Med) have `panel_size` > 0 | >90% | Investigate |

---

## Join Keys

| This Table | Joins To | On Column(s) | Type |
|------------|----------|--------------|------|
| `providers` | `claims` | `npi` = `rendering_npi` | One-to-Many |
| `providers` | `enrollment` | `npi` = `attributed_pcp_npi` | One-to-Many |

---

## Derived Fields (Added in Enriched Layer)

| Field | Logic | Purpose |
|-------|-------|---------|
| `is_pcp` | `specialty_desc` IN ('Family Medicine', 'Internal Medicine') | PCP identification |
| `is_specialist` | NOT `is_pcp` AND `provider_type` = 'Individual' | Specialist identification |
| `is_facility` | `provider_type` = 'Organization' | Facility identification |
| `quality_tier` | CASE WHEN quality_score >= 4.2 THEN 'High' ... | Quality stratification |
| `network_adequacy_flag` | `accepting_new_patients` = 'N' AND `is_pcp` | Access gap flag |
| `members_per_provider` | `panel_size` / 1 (for PCPs) | Capacity metric |

---

## Sample Queries

### Network Adequacy by State/County
```sql
SELECT 
  state, county,
  COUNT(*) as provider_count,
  SUM(CASE WHEN is_pcp THEN 1 ELSE 0 END) as pcp_count,
  SUM(CASE WHEN is_specialist THEN 1 ELSE 0 END) as specialist_count,
  SUM(CASE WHEN is_facility THEN 1 ELSE 0 END) as facility_count
FROM providers
WHERE network_status = 'In-Network'
  AND contract_effective_date <= '2024-12-31'
  AND (contract_term_date IS NULL OR contract_term_date >= '2024-01-01')
GROUP BY state, county
ORDER BY state, county;
```

### PCP Quality Distribution
```sql
SELECT 
  quality_score,
  COUNT(*) as pcp_count,
  AVG(panel_size) as avg_panel_size,
  SUM(panel_size) as total_panel
FROM providers
WHERE is_pcp = TRUE
  AND network_status = 'In-Network'
GROUP BY quality_score
ORDER BY quality_score;
```

### Provider Access Gaps
```sql
SELECT 
  state, county,
  COUNT(*) as total_pcp,
  SUM(CASE WHEN accepting_new_patients = 'N' THEN 1 ELSE 0 END) as closed_pcp,
  SUM(CASE WHEN accepting_new_patients = 'N' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as pct_closed
FROM providers
WHERE is_pcp = TRUE
  AND network_status = 'In-Network'
GROUP BY state, county
HAVING COUNT(*) > 0
ORDER BY pct_closed DESC;
```

### Quality vs Cost Efficiency (Requires Claims Join)
```sql
-- In enriched layer: FCT_CLAIMS_ENRICHED joined to providers
SELECT 
  p.npi,
  p.provider_name,
  p.specialty_desc,
  p.quality_score,
  p.panel_size,
  COUNT(DISTINCT c.member_id) as attributed_members,
  SUM(c.allowed_amount) / COUNT(DISTINCT c.member_id) as pmpm,
  SUM(c.allowed_amount) / SUM(c.member_months) as risk_adj_pmpm
FROM providers p
JOIN fct_claims_enriched c ON p.npi = c.rendering_npi
WHERE p.is_pcp = TRUE
  AND p.network_status = 'In-Network'
GROUP BY p.npi, p.provider_name, p.specialty_desc, p.quality_score, p.panel_size
ORDER BY pmpm;
```