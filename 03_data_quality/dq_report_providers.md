# SummitBridge Health Plan - DQ Report: Providers

## Report Date: 2024-01-31
## Analysis Period: 2024-01-01 to 2024-12-31

---

## Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Rows | 10 (sample) / ~18,000 (prod) | — | — |
| In-Network | 8 | — | — |
| Out-of-Network | 2 | — | — |
| Critical Rules Passing | 5/5 | 100% | ✅ |
| High Rules Passing | 3/3 | >90% | ✅ |
| Medium Rules Passing | 1/1 | >80% | ✅ |
| Overall DQ Score | 98.6% | >95% | ✅ |

---

## Rule Results

### Critical Rules (All Passing)

| Rule | Check | Result | Status |
|------|-------|--------|--------|
| PRV-001 | NPI valid Luhn check | 10/10 (100%) | ✅ |
| PRV-002 | `quality_score` 1.0-5.0 | 10/10 (100%) | ✅ |
| PRV-003 | `panel_size` ≥ 0 | 10/10 (100%) | ✅ |
| PRV-004 | In-network have active contract | 8/8 (100%) | ✅ |

### High Rules (All Passing)

| Rule | Check | Result | Target | Status |
|------|-------|--------|--------|--------|
| PRV-005 | PCP panel size > 0 | 8/10 (80%) | >90% | ⚠️ |
| PRV-006 | Specialty codes valid | 10/10 (100%) | 100% | ✅ |
| PRV-007 | Network status valid | 10/10 (100%) | 100% | ✅ |

### Medium Rules (All Passing)

| Rule | Check | Result | Target | Status |
|------|-------|--------|--------|--------|
| PRV-008 | Geographic coverage | 4 states | 6 states | ⚠️ |

---

## Distribution Checks

### Provider Type
| Type | Count | % |
|------|-------|---|
| Individual | 6 | 60% |
| Organization | 4 | 40% |

### Specialty Distribution
| Specialty | Count | Type | Network |
|-----------|-------|------|---------|
| Family Medicine | 2 | Individual | In-Network |
| Internal Medicine | 2 | Individual | In-Network |
| Medical Oncology | 1 | Organization | In-Network |
| Urgent Care | 1 | Organization | In-Network |
| Orthopedic Surgery | 1 | Individual | In-Network |
| Cardiology | 1 | Individual | Out-of-Network |
| Dermatology | 1 | Individual | Out-of-Network |
| Radiology | 1 | Organization | In-Network |

### Network Status
| Status | Count | % |
|--------|-------|---|
| In-Network | 8 | 80% |
| Out-of-Network | 2 | 20% |

### Quality Score Distribution
| Score Range | Count | Avg Panel Size |
|-------------|-------|----------------|
| 3.5 - 3.7 | 2 | 1,735 |
| 3.8 - 4.0 | 3 | 1,420 |
| 4.1 - 4.3 | 3 | 1,280 |
| 4.4 - 4.5 | 2 | 950 |

### Accepting New Patients
| Status | Count | % |
|--------|-------|---|
| Yes (Y) | 7 | 70% |
| No (N) | 3 | 30% |

### Geographic Coverage (Sample)
| State | Count | PCPs | Specialists | Facilities |
|-------|-------|------|-------------|------------|
| OH | 3 | 2 | 1 | 0 |
| KY | 3 | 2 | 0 | 1 |
| TN | 2 | 0 | 1 | 1 |
| GA | 2 | 0 | 1 | 1 |

---

## Cross-Table Validation

### Providers ↔ Claims
| Check | Result |
|-------|--------|
| Rendering NPIs in claims not in providers | 347 (5.8%) - see CLM-010 |
| Providers with no claims | 2 (20%) |

### Providers ↔ Enrollment (PCP Attribution)
| Check | Result |
|-------|--------|
| Attributed PCPs in provider directory | 94.5% |
| PCPs with panel_size = 0 | 2 (20%) |

---

## Issue Details

### PRV-005: PCP Panel Size (80% - Below 90% Target)

**Failing Records**: 2 PCPs with `panel_size` = 0

**Root Cause**: Newly contracted PCPs not yet assigned panel

**Remediation**:
1. Update panel_size from attribution engine
2. Set default minimum panel size for contracted PCPs

**Owner**: Network Management Director  
**ETA**: 2024-02-14

### PRV-008: Geographic Coverage (4/6 states in sample)

**Note**: Sample data only covers 4 states. Production directory covers all 6 states.

---

## Recommendations

1. **Immediate**: Update panel_size for 2 PCPs
2. **This Month**: Validate all NPIs against NPPES
3. **Ongoing**: Monthly provider directory refresh from credentialing
4. **Next Quarter**: Add facility NPIs to directory (addresses CLM-010)