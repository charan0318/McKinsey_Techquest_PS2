# SummitBridge Health Plan - Data Quality Framework

## Overview
Comprehensive data quality management for all analytics data sources. Ensures reliability, consistency, and trustworthiness of insights.

---

## Data Quality Dimensions

| Dimension | Definition | Measurement |
|-----------|------------|-------------|
| **Completeness** | All expected records/fields present | % non-null, row count vs source |
| **Validity** | Values conform to defined formats/ranges | % passing format/range checks |
| **Consistency** | Same data across systems matches | Cross-system reconciliation |
| **Accuracy** | Values reflect real-world truth | Sample validation vs source |
| **Timeliness** | Data available when needed | Latency vs SLA |
| **Uniqueness** | No duplicate records | Duplicate rate |

---

## Quality Rules by Table

### Claims (FCT_CLAIMS_ENRICHED)

| Rule ID | Dimension | Check | Threshold | Severity | Action |
|---------|-----------|-------|-----------|----------|--------|
| CLM-001 | Completeness | Row count vs source system | 100% | Critical | Alert + halt |
| CLM-002 | Completeness | `allowed_amount` non-null | 100% | Critical | Quarantine |
| CLM-003 | Validity | `allowed_amount` > 0 | 100% | Critical | Quarantine |
| CLM-004 | Validity | `service_from_date` in analysis period | 100% | Critical | Filter |
| CLM-005 | Validity | `claim_type` IN (Professional, Pharmacy, Institutional) | 100% | Critical | Quarantine |
| CLM-006 | Validity | `service_category` IN (6 valid categories) | 100% | Critical | Quarantine |
| CLM-007 | Validity | `in_network_flag` IN (Y, N) | 100% | Critical | Quarantine |
| CLM-008 | Validity | `lob` IN (Commercial, Marketplace, Medicare Advantage) | 100% | Critical | Quarantine |
| CLM-009 | Consistency | `member_id` exists in enrollment | >99% | High | Investigate |
| CLM-010 | Consistency | `rendering_npi` exists in providers | >95% | High | Update provider dir |
| CLM-011 | Consistency | `plan_id` + `lob` consistent with enrollment | 100% | High | Investigate |
| CLM-012 | Accuracy | `allowed_amount` outliers (>3 SD by category) | <1% | Medium | Validate w/ actuarial |
| CLM-013 | Uniqueness | Duplicate claim lines | <0.1% | High | Dedupe |
| CLM-014 | Timeliness | Data available by T+1 8:00 AM | 100% | Critical | Alert |

### Enrollment

| Rule ID | Dimension | Check | Threshold | Severity | Action |
|---------|-----------|-------|-----------|----------|--------|
| ENR-001 | Completeness | Row count vs source | 100% | Critical | Alert |
| ENR-002 | Validity | `enrollment_start_date` ≤ `enrollment_end_date` | 100% | Critical | Fix |
| ENR-003 | Validity | `age` BETWEEN 0 AND 100 | 100% | Critical | Validate |
| ENR-004 | Validity | `risk_score` > 0 | 100% | Critical | Validate |
| ENR-005 | Validity | `lob` IN (3 valid values) | 100% | Critical | Quarantine |
| ENR-006 | Consistency | Active members have no disenrollment_reason | 100% | High | Fix |
| ENR-007 | Consistency | Terminated members have disenrollment_reason | >95% | High | Investigate |
| ENR-008 | Uniqueness | `member_id` unique per enrollment span | 100% | Critical | Dedupe |

### Member Months

| Rule ID | Dimension | Check | Threshold | Severity | Action |
|---------|-----------|-------|-----------|----------|--------|
| MM-001 | Completeness | Row count vs expected (members × 12) | >95% | High | Investigate gaps |
| MM-002 | Validity | `member_months` IN (0, 1) | 100% | Critical | Validate |
| MM-003 | Validity | `calendar_month` = 1st of month | 100% | Critical | Validate |
| MM-004 | Consistency | Sum per member = enrollment months | 100% | High | Reconcile |
| MM-005 | Consistency | `member_id` exists in enrollment | >99% | High | Investigate |

### Providers

| Rule ID | Dimension | Check | Threshold | Severity | Action |
|---------|-----------|-------|-----------|----------|--------|
| PRV-001 | Validity | `npi` valid 10-digit Luhn | 100% | Critical | Reject |
| PRV-002 | Validity | `quality_score` BETWEEN 1.0 AND 5.0 | 100% | Critical | Validate |
| PRV-003 | Validity | `panel_size` ≥ 0 for individuals | 100% | High | Validate |
| PRV-004 | Consistency | In-network providers have active contract | 100% | High | Validate |
| PRV-005 | Accuracy | PCPs have `panel_size` > 0 | >90% | Medium | Investigate |

### Avoidable ED Reference

| Rule ID | Dimension | Check | Threshold | Severity | Action |
|---------|-----------|-------|-----------|----------|--------|
| AED-001 | Validity | `icd10_code` valid format | 100% | Critical | Validate |
| AED-002 | Validity | `avoidable_category` IN (3 values) | 100% | Critical | Validate |
| AED-003 | Completeness | Coverage of ED diagnosis codes | >95% | High | Add missing |

---

## Data Quality Process

### Daily (Automated)
```
1. Ingestion → Raw Landing Zone
2. Run DQ Rules (CLM-001 through CLM-014, etc.)
3. Generate DQ Report Card
4. If Critical failures → Alert + Quarantine + Halt downstream
5. If High failures → Alert + Continue with warnings
6. Load to Enriched Layer (if no Critical failures)
7. Update DQ Dashboard
```

### Weekly
- Review DQ trends (7-day rolling)
- Investigate recurring High-severity issues
- Update provider directory for missing NPIs
- Reconcile member month exposure

### Monthly
- Full DQ Report Card to Data Stewardship Council
- Actuarial validation of PMPM outliers
- Provider match rate review
- Avoidable ED coverage assessment
- Rule threshold calibration

### Quarterly
- Rule effectiveness review (false positive/negative rates)
- New data source onboarding DQ requirements
- DQ framework version update
- Training for data stewards

---

## DQ Report Card Template

### Summary Section
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Overall DQ Score | 96.2% | >95% | ✅ |
| Critical Rules Passing | 14/14 | 100% | ✅ |
| High Rules Passing | 18/20 | >90% | ⚠️ |
| Medium Rules Passing | 8/10 | >80% | ✅ |
| Data Freshness (Claims) | T+1 day | T+1 day | ✅ |
| Data Freshness (Enrollment) | T+1 day | T+1 day | ✅ |

### By Table
| Table | Completeness | Validity | Consistency | Accuracy | Timeliness | Overall |
|-------|--------------|----------|-------------|----------|------------|---------|
| Claims | 100% | 99.8% | 98.5% | 99.2% | 100% | 99.5% |
| Enrollment | 100% | 100% | 99.1% | 100% | 100% | 99.8% |
| Member Months | 98.5% | 100% | 99.5% | 100% | 100% | 99.6% |
| Providers | 100% | 100% | 98.0% | 95.0% | 100% | 98.6% |

### Top Issues
| Rule | Table | Severity | Current | Target | Trend | Owner | ETA |
|------|-------|----------|---------|--------|-------|-------|-----|
| CLM-010 | Claims | High | 94.2% | >95% | ↓ | Network Mgmt | 2 weeks |
| ENR-007 | Enrollment | High | 93.5% | >95% | → | Membership | 1 week |
| PRV-005 | Providers | Medium | 87.0% | >90% | ↑ | Network Mgmt | 1 month |

---

## Remediation Log

| Date | Rule | Issue | Root Cause | Fix Applied | Verified | Owner |
|------|------|-------|------------|-------------|----------|-------|
| 2024-01-15 | CLM-010 | Provider match 94.2% | 50 new providers not loaded | Bulk load + schedule sync | 2024-01-16 | Network Mgr |
| 2024-01-20 | ENR-007 | Disenrollment reason 93.5% | Manual entry gap for employer changes | Auto-populate from group termination | 2024-01-21 | Membership Dir |
| 2024-02-01 | PRV-005 | PCP panel size 87% | New PCPs not yet paneled | Default to 0, flag for update | 2024-02-02 | Network Mgr |

---

## DQ Dashboard (Automated)

### Metrics Tracked
- Rule pass/fail rates by table, dimension, severity
- Row counts and trends
- Freshness SLAs
- Quarantine volumes
- Remediation aging

### Alerting
| Condition | Channel | Recipients |
|-----------|---------|------------|
| Critical rule failure | PagerDuty + Email | Data Engineer, Analytics Director |
| High rule failure 2+ days | Email | Data Steward, Analytics Consultant |
| Freshness SLA breach | PagerDuty | Data Engineer |
| Quarantine >100 rows | Email | Data Engineer, Analytics Consultant |

---

## Data Quality Tools

| Tool | Purpose |
|------|---------|
| Great Expectations | Rule definition, validation, documentation |
| dbt tests | In-pipeline testing for transformed tables |
| Custom Python | Complex cross-table rules, statistical outliers |
| Airflow/DBT | Orchestration, scheduling, lineage |
| Grafana/Superset | DQ dashboard visualization |

---

## Governance

### Data Stewards
| Domain | Steward | Responsibility |
|--------|---------|----------------|
| Claims | Claims Operations Manager | CLM rules, source system liaison |
| Enrollment | Membership Director | ENR rules, eligibility system |
| Providers | Network Management Director | PRV rules, provider directory |
| Member Months | Actuarial Director | MM rules, exposure reconciliation |

### Escalation
1. **Data Engineer** → Fix pipeline, data loads
2. **Data Steward** → Source system fixes, business rule clarification
3. **Analytics Director** → Cross-domain issues, prioritization
4. **Steering Committee** → Strategic decisions, resource allocation

---

## Continuous Improvement

### Metrics
- **DQ Score Trend**: Monthly overall score
- **Issue Resolution Time**: Mean time to resolve by severity
- **Rule Coverage**: % of critical fields with rules
- **False Positive Rate**: Alerts that were not real issues
- **Downstream Impact**: Analytic errors traced to DQ issues

### Quarterly Review
- Add rules for new analytic use cases
- Retire obsolete rules
- Calibrate thresholds based on business impact
- Update documentation
- Train new team members