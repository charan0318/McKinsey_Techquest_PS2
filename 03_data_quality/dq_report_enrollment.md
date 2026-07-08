# SummitBridge Health Plan - DQ Report: Enrollment

## Report Date: 2024-01-31
## Analysis Period: 2024-01-01 to 2024-12-31

---

## Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total Rows | 800 | — | — |
| Active Members | 707 | — | — |
| Disenrolled Members | 93 | — | — |
| Critical Rules Passing | 8/8 | 100% | ✅ |
| High Rules Passing | 5/5 | >90% | ✅ |
| Overall DQ Score | 100% | >95% | ✅ |

---

## Rule Results

### Critical Rules (All Passing)

| Rule | Check | Result | Status |
|------|-------|--------|--------|
| ENR-001 | Row count vs source | 800 = 800 | ✅ |
| ENR-002 | `member_id` unique | 800/800 (100%) | ✅ |
| ENR-003 | `enrollment_start_date` not null | 800/800 (100%) | ✅ |
| ENR-004 | `enrollment_end_date` ≥ start (when not null) | 93/93 (100%) | ✅ |
| ENR-005 | `age` between 0-100 | 800/800 (100%) | ✅ |
| ENR-006 | `risk_score` > 0 | 800/800 (100%) | ✅ |
| ENR-007 | Active members have no disenrollment_reason | 707/707 (100%) | ✅ |
| ENR-008 | Terminated members have disenrollment_reason | 93/93 (100%) | ✅ |

### High Rules (All Passing)

| Rule | Check | Result | Target | Status |
|------|-------|--------|--------|--------|
| ENR-009 | `lob` valid | 800/800 (100%) | 100% | ✅ |
| ENR-010 | `state` valid | 800/800 (100%) | 100% | ✅ |
| ENR-011 | `gender` valid | 800/800 (100%) | 100% | ✅ |
| ENR-012 | PCP attribution rate | 94.5% | >90% | ✅ |
| ENR-013 | Plan/LOB consistency | 100% | 100% | ✅ |

---

## Distribution Checks

### LOB Distribution
| LOB | Active | Disenrolled | Total | % Active |
|-----|--------|-------------|-------|----------|
| Commercial | 349 | 27 | 376 | 92.8% |
| Marketplace | 299 | 48 | 347 | 86.2% |
| Medicare Advantage | 152 | 18 | 170 | 89.4% |

### State Distribution
| State | Active | Disenrolled | Total |
|-------|--------|-------------|-------|
| KY | 182 | 22 | 204 |
| GA | 194 | 24 | 218 |
| TN | 204 | 25 | 229 |
| OH | 220 | 22 | 242 |

### Disenrollment Reasons
| Reason | Count | % of Disenrolled |
|--------|-------|------------------|
| Premium Affordability | 26 | 28.0% |
| Network Adequacy | 25 | 26.9% |
| Access Issues | 15 | 16.1% |
| Employer Change | 14 | 15.1% |
| Moved Out of Area | 13 | 14.0% |

### Age Distribution
| Age Band | Count | % |
|----------|-------|---|
| 0-17 | 12 | 1.5% |
| 18-34 | 89 | 11.1% |
| 35-49 | 156 | 19.5% |
| 50-64 | 267 | 33.4% |
| 65+ | 276 | 34.5% |

### Risk Score Distribution
| Risk Tier | Range | Count | % |
|-----------|-------|-------|---|
| Low | < 1.0 | 312 | 39.0% |
| Medium | 1.0 - 1.5 | 287 | 35.9% |
| High | 1.5 - 2.5 | 143 | 17.9% |
| Very High | > 2.5 | 58 | 7.3% |

---

## Cross-Table Validation

### Enrollment ↔ Claims
| Check | Result |
|-------|--------|
| Members in claims but not enrollment | 0 |
| Members in enrollment but no claims | 142 (17.8%) |
| Members with claims but no enrollment | 0 |

### Enrollment ↔ Member Months
| Check | Result |
|-------|--------|
| Member months sum = enrollment months | 100% match |
| Orphan member months | 0 |

---

## Recommendations

1. **PCP Attribution**: 5.5% of members lack attributed PCP - investigate for Marketplace/MA
2. **Zero-Claim Members**: 142 members (17.8%) had no claims - verify enrollment accuracy
3. **Risk Score Calibration**: Validate risk score distribution against CMS benchmarks