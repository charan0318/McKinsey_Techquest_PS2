# SummitBridge Health Plan - DQ Report: Claims

## Report Date: 2024-01-31
## Analysis Period: 2024-01-01 to 2024-12-31

---

## Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Rows (Raw) | 5,961 | — | — |
| Total Rows (Enriched) | 5,961 | 100% match | ✅ |
| Critical Rules Passing | 14/14 | 100% | ✅ |
| High Rules Passing | 8/10 | >90% | ⚠️ |
| Medium Rules Passing | 4/5 | >80% | ✅ |
| Overall DQ Score | 98.2% | >95% | ✅ |

---

## Rule Results

### Critical Rules (All Passing)

| Rule | Check | Result | Status |
|------|-------|--------|--------|
| CLM-001 | Row count vs source | 5,961 = 5,961 | ✅ |
| CLM-002 | `allowed_amount` non-null | 5,961/5,961 (100%) | ✅ |
| CLM-003 | `allowed_amount` > 0 | 5,961/5,961 (100%) | ✅ |
| CLM-004 | `service_from_date` in period | 5,961/5,961 (100%) | ✅ |
| CLM-005 | `claim_type` valid | 5,961/5,961 (100%) | ✅ |
| CLM-006 | `service_category` valid | 5,961/5,961 (100%) | ✅ |
| CLM-007 | `in_network_flag` valid | 5,961/5,961 (100%) | ✅ |
| CLM-008 | `lob` valid | 5,961/5,961 (100%) | ✅ |
| CLM-014 | Data freshness | T+1 day | ✅ |

### High Rules

| Rule | Check | Result | Target | Status |
|------|-------|--------|--------|--------|
| CLM-009 | Member match rate | 99.4% | >99% | ✅ |
| CLM-010 | Provider match rate | 94.2% | >95% | ❌ |
| CLM-011 | Plan/LOB consistency | 100% | 100% | ✅ |

### Medium Rules

| Rule | Check | Result | Target | Status |
|------|-------|--------|--------|--------|
| CLM-012 | Allowed amount outliers | 0.8% | <1% | ✅ |
| CLM-013 | Duplicate claim lines | 0.02% | <0.1% | ✅ |

---

## Issue Details

### CLM-010: Provider Match Rate (94.2% - Below 95% Target)

**Failing Records**: 347 claim lines (5.8%) have `rendering_npi` not found in provider directory

**Root Cause Analysis**:
- 280 lines: Rendering NPI = Billing NPI (facility claims), facility not in provider directory
- 67 lines: New providers contracted after directory extract date

**Remediation**:
1. Load facility NPIs into provider directory (Week 1)
2. Schedule weekly provider directory sync from credentialing system (Week 2)
3. Add facility type to provider dimension

**Owner**: Network Management Director  
**ETA**: 2024-02-14

---

## Distribution Checks

### Service Category Distribution
| Category | Count | % of Total | Allowed $ | % of Allowed |
|----------|-------|------------|-----------|--------------|
| Inpatient | 528 | 8.9% | $8,631,818 | 76.2% |
| ED | 1,209 | 20.3% | $1,362,282 | 12.0% |
| Specialty Rx | 657 | 11.0% | $791,233 | 7.0% |
| PCP | 2,387 | 40.0% | $357,410 | 3.2% |
| Urgent Care | 700 | 11.7% | $94,288 | 0.8% |
| Behavioral Health | 480 | 8.1% | $84,221 | 0.7% |

### LOB Distribution
| LOB | Count | % | Allowed $ | % |
|-----|-------|---|-----------|---|
| Commercial | 2,504 | 42.0% | $4,123,456 | 36.4% |
| Marketplace | 2,225 | 37.3% | $3,891,234 | 34.4% |
| Medicare Advantage | 1,232 | 20.7% | $3,306,562 | 29.2% |

### Network Status
| Status | Count | % | Allowed $ | % | Avg Allowed |
|--------|-------|---|-----------|---|-------------|
| In-Network (Y) | 5,906 | 99.1% | $11,182,517 | 98.8% | $1,893 |
| Out-of-Network (N) | 55 | 0.9% | $138,734 | 1.2% | $2,522 |

---

## Outlier Analysis (CLM-012)

**Method**: >3 standard deviations from service_category mean

| Category | Mean | Std Dev | Threshold (3σ) | Outliers | Max Value |
|----------|------|---------|----------------|----------|-----------|
| Inpatient | $16,348 | $4,231 | $29,041 | 3 | $32,156 |
| ED | $1,127 | $389 | $2,294 | 12 | $3,456 |
| Specialty Rx | $1,204 | $612 | $3,040 | 5 | $4,123 |
| PCP | $150 | $42 | $276 | 8 | $312 |
| Urgent Care | $135 | $38 | $249 | 4 | $287 |
| Behavioral Health | $175 | $58 | $349 | 2 | $398 |

**Action**: 32 outliers flagged for actuarial validation (0.5% of total)

---

## Recommendations

1. **Immediate**: Fix provider directory gap (CLM-010)
2. **This Month**: Validate 32 outlier claims with actuarial
3. **Ongoing**: Monitor duplicate rate (currently well within threshold)
4. **Next Quarter**: Expand provider directory to include all facility NPIs