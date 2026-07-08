SUMMITBRIDGE HEALTH PLAN - ANALYTICS DATA INTEGRATION FRAMEWORK

DATA SOURCES & INTEGRATION LAYER
================================
SOURCE SYSTEMS                    INTEGRATION LAYER      ANALYTICS   
-----------------                 ----------------      ----------  
* Claims Admin System             * ETL Pipeline         * Data      
  (Medical & Pharmacy)              - Daily batch          Warehouse  
* Enrollment/Eligibility System         - CDC for claims     (DuckDB/  
* Provider Directory                    - SCD Type 2 for      Snowflake)
* Clinical/EMR (future)                 enrollment        * Semantic  
* SDoH/Vendor Data (future)         * Data Quality         Layer     
* Member Engagement (future)          Framework            * BI/       
                                    * Master Data Mgmt     Dashboard  
                                      (Member, Provider)     * ML/AI     
                                                                      Platform  

KEY DATA TABLES (Current State)
-------------------------------
1. CLAIMS (Fact Table)
   - Grain: Claim line (medical/pharmacy/institutional)
   - Key: claim_id, member_id, rendering_npi, service_from_date
   - Measures: allowed_amount, paid_amount, billed_amount, units
   - Dimensions: service_category, claim_type, place_of_service, diagnosis, procedure, NDC
   - Refresh: Daily (paid date), Monthly (incurred date complete)

2. MEMBER_MONTHS (Exposure Table)
   - Grain: Member x Plan x Month
   - Key: member_id, plan_id, calendar_month
   - Measure: member_months (1 or 0)
   - Refresh: Monthly

3. ENROLLMENT (Member Dimension)
   - Grain: Member enrollment span
   - Key: member_id
   - Attributes: demographics, plan, LOB, group, geography, PCP attribution, risk_score
   - SCD Type 2: Track enrollment changes, disenrollment reason
   - Refresh: Daily

4. PROVIDERS (Provider Dimension)
   - Grain: Provider (NPI)
   - Key: npi
   - Attributes: name, type, specialty, network_status, location, quality_score, panel_size
   - SCD Type 2: Contract changes, quality score updates
   - Refresh: Monthly

5. AVOIDABLE_ED_REFERENCE (Reference Table)
   - Grain: ICD-10 code
   - Classification: Avoidable / Potentially Avoidable / Non-Avoidable
   - Refresh: Annually (CMS updates)

DERIVED / MART TABLES (To Build)
--------------------------------
1. FCT_CLAIMS_ENRICHED
   - Claims joined to enrollment (member demographics, PCP, risk_score)
   - Claims joined to providers (quality, network, specialty)
   - ED avoidable flag
   - High-cost member flag
   - Refresh: Daily

2. FCT_MEMBER_MONTH_SUMMARY
   - Grain: Member x Month
   - Measures: PMPM, IP admits/1000, ED visits/1000, Rx scripts, OON flag
   - Refresh: Monthly

3. DIM_HIGH_COST_MEMBERS
   - Grain: Member (Top 5% by rolling 12-month allowed)
   - Attributes: Primary cost drivers, comorbidities, CM status, interventions
   - Refresh: Monthly

4. FCT_CARE_MANAGEMENT
   - Grain: Member x Intervention x Date
   - Measures: Engagement, outcomes, savings attribution
   - Refresh: Weekly

REFRESH CADENCE & SLAs
----------------------
| Layer              | Frequency | SLA (Data Ready) | Owner           |
|--------------------|-----------|------------------|-----------------|
| Raw Ingestion      | Daily     | T+1 6:00 AM      | Data Engineering|
| Enriched Claims    | Daily     | T+1 8:00 AM      | Data Engineering|
| Member Month       | Monthly   | 5th business day | Actuarial       |
| KPI Dashboard      | Daily     | T+1 9:00 AM      | Analytics       |
| Care Mgmt Lists    | Weekly    | Monday 8:00 AM   | Care Management |
| Actuarial Extracts | Monthly   | 10th business day| Actuarial       |

DATA QUALITY FRAMEWORK
----------------------
| Check              | Frequency | Threshold | Action                    |
|--------------------|-----------|-----------|---------------------------|
| Claim completeness | Daily     | >99.5%    | Alert + root cause        |
| Allowed > 0        | Daily     | 100%      | Reject/quarantine         |
| Member match       | Daily     | >99%      | Investigate orphans       |
| Provider match     | Daily     | >95%      | Update provider directory |
| Duplicate claims   | Daily     | <0.1%     | Dedupe logic              |
| PMPM outliers      | Monthly   | >3 SD     | Validate with actuarial   |

OWNERSHIP & GOVERNANCE
----------------------
* Data Steward (Claims): Claims Operations Manager
* Data Steward (Enrollment): Membership Director
* Data Steward (Provider): Network Management Director
* Analytics Platform Owner: Director, Healthcare Analytics
* Executive Sponsor: CMO / CFO
* Governance Council: Monthly (data quality, prioritization, access)