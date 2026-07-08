# SummitBridge Health Plan - Avoidable ED Reference Data Dictionary

## Table Overview
| Attribute | Value |
|-----------|-------|
| **Table Name** | `avoidable_ed_reference` |
| **Source System** | Clinical Reference / CMS Avoidable ED Algorithm |
| **Grain** | ICD-10-CM Code (one row per diagnosis code) |
| **Refresh Frequency** | Annually (CMS updates) |
| **Analysis Period** | 2024-01-01 to 2024-12-31 |
| **Row Count** | 12 (sample) / ~200+ (production) |
| **Primary Key** | `icd10_code` |

---

## Column Definitions

| Column | Type | Description | Example | Nullable | Notes |
|--------|------|-------------|---------|----------|-------|
| `icd10_code` | string | ICD-10-CM diagnosis code | `R10.9`, `J06.9`, `R51.9` | No | **Primary key**, matches `claims.diagnosis_code_1` |
| `description` | string | Clinical description | `Unspecified abdominal pain`, `Acute upper respiratory infection` | No | Human-readable |
| `avoidable_category` | category | Avoidability classification | `Avoidable`, `Potentially Avoidable`, `Non-Avoidable` | No | **Key analytic dimension** |

---

## Avoidable Category Definitions

| Category | Definition | Examples | Action |
|----------|------------|----------|--------|
| **Avoidable** | Condition treatable in primary care/urgent care; ED visit preventable with timely outpatient care | URI, UTI, uncomplicated headache, minor abrasions, simple rash | **Primary diversion target** - nurse triage → UC/PCP |
| **Potentially Avoidable** | Condition may require ED but could be managed in lower acuity with proper access/coordination | Abdominal pain (non-surgical), back pain, chest pain (low risk), asthma exacerbation | **Secondary target** - improved PCP access, care coordination |
| **Non-Avoidable** | Condition appropriately requires ED resources (life-threatening, time-sensitive) | MI, stroke, major trauma, sepsis, acute surgical abdomen | **Do not divert** - ensure appropriate ED use |

---

## Sample Reference Data (Current)

| ICD-10 | Description | Category |
|--------|-------------|----------|
| `R10.9` | Unspecified abdominal pain | Avoidable |
| `R51.9` | Headache | Potentially Avoidable |
| `J06.9` | Acute upper respiratory infection | Avoidable |
| `R07.9` | Chest pain unspecified | Non-Avoidable |
| `J18.9` | Pneumonia unspecified | Non-Avoidable |
| `N39.0` | Urinary tract infection | Avoidable |
| `H66.90` | Otitis media unspecified | Avoidable |
| `S09.90XA` | Unspecified head injury | Potentially Avoidable |
| `M54.5` | Low back pain | Avoidable |
| `I50.9` | Heart failure unspecified | Non-Avoidable |
| `F32.9` | Major depressive disorder | Potentially Avoidable |
| `K21.9` | GERD without esophagitis | Avoidable |

---

## Data Quality Rules

| Rule | Threshold | Action |
|------|-----------|--------|
| `icd10_code` valid ICD-10-CM format | 100% | Validate against CMS reference |
| `avoidable_category` IN ('Avoidable', 'Potentially Avoidable', 'Non-Avoidable') | 100% | Validate |
| No duplicate `icd10_code` | 100% | Dedupe |
| Coverage of ED diagnosis codes in claims | >95% | Add missing codes |

---

## Join Keys

| This Table | Joins To | On Column(s) | Type |
|------------|----------|--------------|------|
| `avoidable_ed_reference` | `claims` | `icd10_code` = `diagnosis_code_1` | One-to-Many (ED claims only) |

---

## Usage in Analysis

### ED Avoidable Classification
```sql
SELECT 
  c.claim_id,
  c.member_id,
  c.diagnosis_code_1,
  a.description,
  a.avoidable_category,
  c.allowed_amount
FROM claims c
LEFT JOIN avoidable_ed_reference a 
  ON c.diagnosis_code_1 = a.icd10_code
WHERE c.service_category = 'ED'
  AND c.service_from_date BETWEEN '2024-01-01' AND '2024-12-31';
```

### Avoidable ED Summary
```sql
SELECT 
  a.avoidable_category,
  COUNT(*) as visit_count,
  SUM(c.allowed_amount) as total_allowed,
  AVG(c.allowed_amount) as avg_allowed
FROM claims c
JOIN avoidable_ed_reference a 
  ON c.diagnosis_code_1 = a.icd10_code
WHERE c.service_category = 'ED'
  AND c.service_from_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY a.avoidable_category
ORDER BY visit_count DESC;
```

### Top Avoidable Diagnoses
```sql
SELECT 
  c.diagnosis_code_1,
  a.description,
  a.avoidable_category,
  COUNT(*) as visit_count,
  SUM(c.allowed_amount) as total_allowed,
  AVG(c.allowed_amount) as avg_allowed
FROM claims c
JOIN avoidable_ed_reference a 
  ON c.diagnosis_code_1 = a.icd10_code
WHERE c.service_category = 'ED'
  AND a.avoidable_category IN ('Avoidable', 'Potentially Avoidable')
  AND c.service_from_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY c.diagnosis_code_1, a.description, a.avoidable_category
ORDER BY visit_count DESC
LIMIT 20;
```

---

## Maintenance Notes

- **Annual Update**: Refresh with CMS Medicare Avoidable ED Algorithm updates (typically October)
- **Clinical Review**: Validate classifications with Medical Director quarterly
- **Custom Codes**: Add plan-specific codes for local practice patterns
- **Versioning**: Maintain history of classification changes for trend consistency
- **Production Scale**: Full reference contains ~200+ ICD-10 codes covering all ED-presenting diagnoses

---

## Limitations

1. **Diagnosis-Based Only**: Does not consider clinical severity, comorbidities, or social factors
2. **Single Diagnosis**: Uses primary diagnosis only; secondary diagnoses may change classification
3. **Retrospective**: Classification applied post-visit; real-time triage needs clinical protocol
4. **Geographic Variation**: Avoidability may vary by local PCP/UC availability
5. **Pediatric Considerations**: Some codes have different avoidability for children vs adults