# SummitBridge Health Plan - Business Understanding

## Case Context
**Organization**: SummitBridge Health Plan  
**Type**: Mid-sized regional health insurance company  
**Footprint**: 6 states across Midwest and Southeast (KY, GA, TN, OH + 2 more)  
**Covered Lives**: ~420,000 across 3 product lines  
**Network**: ~18,000 contracted providers  
**Annual Medical Spend**: ~$2.1B in allowed claims  

## Product Lines
| Product | Description | Key Characteristics |
|---------|-------------|---------------------|
| Commercial | Employer-sponsored plans | Group contracts, PPO/HMO, employer-driven |
| Marketplace (ACA) | Individual ACA plans | Bronze/Silver/Gold, subsidy-eligible, high churn |
| Medicare Advantage | MA plans for 65+ | CMS risk-adjusted, Star ratings, regulatory |

## Problem Statement
Despite strong clinical partnerships and competitive premiums, SummitBridge faces pressure on medical cost management from two major drivers:

### 1. High-Cost Utilization
- Specialty drugs, inpatient stays, ED visits
- May be avoidable or better managed in lower-cost settings
- Small share of members drives disproportionate spend

### 2. Inefficient Care Patterns
- Duplicative services
- Out-of-network leakage
- Gaps in preventive/primary care driving downstream cost

## Key Issues Identified

| Issue | Description | Impact |
|-------|-------------|--------|
| Rising High-Cost Claimants | Top members drive disproportionate spend (specialty pharmacy, oncology, behavioral health) | 20.5% of spend from 5% of members |
| Avoidable ED Utilization | ED visits treatable in urgent care or primary care | 76% of ED visits avoidable = $1.03M |
| Out-of-Network Leakage | Members receiving care outside contracted network | 1.2% of spend, avg $2,522 vs $1,893 in-network |
| Member Retention & Satisfaction | Commercial group renewals slipping; exit surveys cite cost confusion and access issues | 11.6% annual disenrollment |

## Goals & Objectives

### Primary Goal
Develop a strategy to optimize utilization, reduce costs, and improve retention while maintaining high-quality patient care.

### Specific Objectives
1. **High-Cost Claimant Optimization**: Identify top 5% members, analyze cost drivers, recommend interventions
2. **Specialty Spend Optimization**: Model savings from PA refinement, site-of-care shifts, formulary adjustments
3. **Avoidable Utilization Reduction**: Pinpoint avoidable ED, BH, readmissions; propose diversion programs
4. **Member Retention**: Analyze churn drivers, correlate with access gaps, improve cost transparency
5. **Data-Driven Decision Making**: Build integrated data framework, KPIs, dashboard, actuarial support

## Stakeholders

| Role | Interest | Decision Authority |
|------|----------|-------------------|
| CMO / CFO | Executive sponsors, budget approval | Final go/no-go on interventions |
| VP Medical Management | UM, CM, quality programs | Clinical intervention design |
| VP Pharmacy Benefits | Formulary, PA, specialty strategy | Pharmacy interventions |
| VP Network Management | Provider contracts, adequacy | Network interventions |
| VP Member Experience | Retention, satisfaction, digital tools | Member-facing programs |
| Actuarial Director | Pricing, reserving, trend assumptions | Rate filing, IBNR, trend |
| Director, Healthcare Analytics | Analytics platform, KPIs, reporting | Analytic methodology, tools |
| Claims Operations Manager | Data quality, claims processing | Claims data stewardship |
| Membership Director | Enrollment, eligibility, disenrollment | Enrollment data stewardship |

## Success Criteria

| Metric | Current | Target | Timeline |
|--------|---------|--------|----------|
| High-Cost Concentration (Top 5%) | 20.5% | <15% | 18 months |
| Avoidable ED Rate | 75.6% | <60% | 12 months |
| ED Visits per 1,000 | 142.9 | <45 | 18 months |
| 30-Day Readmission Rate | 6.1% | <12% | 12 months |
| OON Allowed % | 1.2% | <1% | 12 months |
| Annual Disenrollment Rate | 11.6% | <8% | 18 months |
| Medical PMPM Trend | Baseline | <5% YoY | Ongoing |
| Total Savings Realized | $0 | $500K-$1.2M | 18 months |

## Constraints & Assumptions

### Constraints
- **Regulatory**: CMS MA requirements, ACA MLR, No Surprises Act, state insurance regulations
- **Contractual**: Provider contracts, employer group agreements, pharmacy rebates
- **Operational**: Staffing for care management, IT systems for ED diversion, provider buy-in
- **Financial**: Investment budget, ROI thresholds, premium competitiveness

### Assumptions
- Analysis period: January 1, 2024 – December 31, 2024
- Allowed amount = primary cost metric
- High-cost = top 5% by allowed spend in period
- PMPM = Total Allowed ÷ Member Months
- ED/1000 = (ED Claims ÷ Member Months) × 1,000
- Avoidable ED classification based on ICD-10 reference table
- Readmission proxy = IP admit within 30 days of prior discharge

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Provider resistance to site-of-care shifts | High | High | Phased approach, shared savings, quality safeguards |
| Member disruption from ED diversion | Medium | High | Clear communication, 24/7 nurse line, seamless UC access |
| Data quality issues in claims/enrollment | Medium | Medium | DQ framework, automated checks, stewardship |
| Actuarial credibility of savings estimates | Medium | High | Conservative assumptions, sensitivity analysis, pilot measurement |
| Regulatory changes | Low | High | Legal review, compliance monitoring |
| Competitive premium pressure | High | Medium | Demonstrate value, quality outcomes, member satisfaction |

## Timeline & Phases

### Phase 1: Quick Wins (Months 1-3)
- Deploy ED diversion: 24/7 nurse triage + telehealth UC
- Refine Specialty Rx PA criteria (step therapy, biosimilars)
- Launch high-cost claimant care management (top 5%)
- Build KPI dashboard (production)
- Member cost transparency tool MVP

### Phase 2: Foundation Building (Months 4-9)
- Site-of-care contracting (infusion centers, home health)
- PCP access guarantees + extended hours incentives
- Network adequacy analysis → targeted recruitment
- Transitional care program (48h follow-up, 7-day PCP visit)
- Provider TCO scorecards (quarterly)

### Phase 3: Transformation (Months 10-18)
- Integrated BH/PCP collaborative care model
- Value-based contracts with high-performing PCP groups
- Predictive modeling for high-cost identification (pre-emptive)
- SDoH screening & community resource integration
- Advanced analytics: ML for readmission risk, churn prediction