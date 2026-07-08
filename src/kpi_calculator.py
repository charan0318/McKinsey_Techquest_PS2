"""
SummitBridge Analytics - KPI Calculator
Reusable KPI computation functions for all 20 KPIs.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_high_cost_concentration(claims: pd.DataFrame, 
                                       percentile: float = 0.95) -> Dict[str, Any]:
    """KPI: High-Cost Member Concentration - Top 5% share of total allowed spend."""
    member_total = claims.groupby('member_id')['allowed_amount'].sum()
    threshold = member_total.quantile(percentile)
    hc_members = member_total[member_total >= threshold]
    
    return {
        'kpi': 'high_cost_concentration_pct',
        'value': hc_members.sum() / member_total.sum() * 100,
        'threshold': threshold,
        'hc_member_count': len(hc_members),
        'total_members': len(member_total),
        'hc_total_allowed': hc_members.sum(),
        'total_allowed': member_total.sum(),
    }


def calculate_specialty_rx_pmpm(claims: pd.DataFrame, member_months: pd.DataFrame) -> Dict[str, Any]:
    """KPI: Specialty Rx PMPM."""
    specialty_allowed = claims[claims['service_category'] == 'Specialty Rx']['allowed_amount'].sum()
    total_mm = member_months['member_months'].sum()
    
    return {
        'kpi': 'specialty_rx_pmpm',
        'value': specialty_allowed / total_mm,
        'specialty_total_allowed': specialty_allowed,
        'total_member_months': total_mm,
    }


def calculate_ed_visits_per_1000(claims: pd.DataFrame, member_months: pd.DataFrame) -> Dict[str, Any]:
    """KPI: ED Visits per 1,000 Member Months."""
    ed_visits = len(claims[claims['service_category'] == 'ED'])
    total_mm = member_months['member_months'].sum()
    
    return {
        'kpi': 'ed_visits_per_1000',
        'value': ed_visits / total_mm * 1000,
        'ed_visits': ed_visits,
        'total_member_months': total_mm,
    }


def calculate_avoidable_ed_rate(claims: pd.DataFrame, avoidable_ed: pd.DataFrame) -> Dict[str, Any]:
    """KPI: Avoidable ED Visit Rate (% of ED visits avoidable/potentially avoidable)."""
    ed_claims = claims[claims['service_category'] == 'ED'].copy()
    ed_claims = ed_claims.merge(avoidable_ed[['icd10_code', 'avoidable_category']], 
                                 left_on='diagnosis_code_1', right_on='icd10_code', how='left')
    
    total_ed = len(ed_claims)
    avoidable_count = ed_claims['avoidable_category'].isin(['Avoidable', 'Potentially Avoidable']).sum()
    
    return {
        'kpi': 'avoidable_ed_rate_pct',
        'value': avoidable_count / total_ed * 100 if total_ed > 0 else 0,
        'avoidable_visits': int(avoidable_count),
        'total_ed_visits': total_ed,
    }


def calculate_ed_to_uc_shift_rate(claims: pd.DataFrame, avoidable_ed: pd.DataFrame,
                                   shifted_visits: int = 0) -> Dict[str, Any]:
    """KPI: ED-to-Urgent Care Shift Rate (% of avoidable ED redirected)."""
    ed_claims = claims[claims['service_category'] == 'ED'].copy()
    ed_claims = ed_claims.merge(avoidable_ed[['icd10_code', 'avoidable_category']], 
                                 left_on='diagnosis_code_1', right_on='icd10_code', how='left')
    
    avoidable_count = ed_claims['avoidable_category'].isin(['Avoidable', 'Potentially Avoidable']).sum()
    
    return {
        'kpi': 'ed_to_uc_shift_rate_pct',
        'value': shifted_visits / avoidable_count * 100 if avoidable_count > 0 else 0,
        'shifted_visits': shifted_visits,
        'avoidable_visits': int(avoidable_count),
    }


def calculate_pcp_visit_post_ed(claims: pd.DataFrame, days: int = 7) -> Dict[str, Any]:
    """KPI: PCP Visit Within N Days Post-ED."""
    # This requires claim-level date logic - placeholder for now
    return {
        'kpi': 'pcp_visit_post_ed_pct',
        'value': None,
        'note': 'Requires claim date sequencing logic',
    }


def calculate_bh_member_ed_rate(claims: pd.DataFrame) -> Dict[str, Any]:
    """KPI: BH Member ED Visit Rate (per 1,000)."""
    bh_members = claims[claims['service_category'] == 'Behavioral Health']['member_id'].unique()
    bh_claims = claims[claims['member_id'].isin(bh_members)]
    
    ed_visits = len(bh_claims[bh_claims['service_category'] == 'ED'])
    bh_member_months = len(bh_members) * 12  # Approximate
    
    return {
        'kpi': 'bh_member_ed_per_1000',
        'value': ed_visits / bh_member_months * 1000 if bh_member_months > 0 else 0,
        'bh_members': len(bh_members),
        'ed_visits': ed_visits,
    }


def calculate_bh_member_ip_rate(claims: pd.DataFrame) -> Dict[str, Any]:
    """KPI: BH Member IP Admission Rate (per 1,000)."""
    bh_members = claims[claims['service_category'] == 'Behavioral Health']['member_id'].unique()
    bh_claims = claims[claims['member_id'].isin(bh_members)]
    
    ip_admits = len(bh_claims[bh_claims['service_category'] == 'Inpatient'])
    bh_member_months = len(bh_members) * 12
    
    return {
        'kpi': 'bh_member_ip_per_1000',
        'value': ip_admits / bh_member_months * 1000 if bh_member_months > 0 else 0,
        'bh_members': len(bh_members),
        'ip_admits': ip_admits,
    }


def calculate_readmission_rate(claims: pd.DataFrame) -> Dict[str, Any]:
    """KPI: 30-Day All-Cause Readmission Rate."""
    ip_claims = claims[claims['service_category'] == 'Inpatient'].copy()
    ip_claims = ip_claims.sort_values(['member_id', 'service_from_date'])
    
    ip_claims['prev_discharge'] = ip_claims.groupby('member_id')['service_to_date'].shift(1)
    ip_claims['days_since_discharge'] = (ip_claims['service_from_date'] - ip_claims['prev_discharge']).dt.days
    ip_claims['is_readmission_30'] = ip_claims['days_since_discharge'] <= 30
    
    total_admits = len(ip_claims)
    readmits = ip_claims['is_readmission_30'].sum()
    
    return {
        'kpi': 'readmission_rate_pct',
        'value': readmits / total_admits * 100 if total_admits > 0 else 0,
        'readmissions': int(readmits),
        'total_admissions': total_admits,
    }


def calculate_oon_allowed_pct(claims: pd.DataFrame) -> Dict[str, Any]:
    """KPI: Out-of-Network Allowed %."""
    oon_allowed = claims[claims['in_network_flag'] == 'N']['allowed_amount'].sum()
    total_allowed = claims['allowed_amount'].sum()
    
    return {
        'kpi': 'oon_allowed_pct',
        'value': oon_allowed / total_allowed * 100 if total_allowed > 0 else 0,
        'oon_allowed': oon_allowed,
        'total_allowed': total_allowed,
    }


def calculate_disenrollment_rate(enrollment: pd.DataFrame) -> Dict[str, Any]:
    """KPI: Annual Disenrollment Rate."""
    total = len(enrollment)
    disenrolled = enrollment['disenrollment_reason'].notna().sum()
    
    return {
        'kpi': 'disenrollment_rate_pct',
        'value': disenrolled / total * 100 if total > 0 else 0,
        'disenrolled': int(disenrolled),
        'total_members': total,
    }


def calculate_cost_access_disenroll_pct(enrollment: pd.DataFrame) -> Dict[str, Any]:
    """KPI: Disenrollment Due to Cost/Access (% of disenrollments)."""
    disenrolled = enrollment[enrollment['disenrollment_reason'].notna()]
    total_disenrolled = len(disenrolled)
    
    cost_access_reasons = ['Premium Affordability', 'Network Adequacy', 'Access Issues']
    cost_access_count = disenrolled['disenrollment_reason'].isin(cost_access_reasons).sum()
    
    return {
        'kpi': 'cost_access_disenroll_pct',
        'value': cost_access_count / total_disenrolled * 100 if total_disenrolled > 0 else 0,
        'cost_access_disenrollments': int(cost_access_count),
        'total_disenrollments': total_disenrolled,
    }


def calculate_total_medical_pmpm(claims: pd.DataFrame, member_months: pd.DataFrame) -> Dict[str, Any]:
    """KPI: Total Medical PMPM."""
    total_allowed = claims['allowed_amount'].sum()
    total_mm = member_months['member_months'].sum()
    
    return {
        'kpi': 'total_medical_pmpm',
        'value': total_allowed / total_mm if total_mm > 0 else 0,
        'total_allowed': total_allowed,
        'total_member_months': total_mm,
    }


def calculate_all_kpis(claims: pd.DataFrame, enrollment: pd.DataFrame, 
                       member_months: pd.DataFrame, providers: pd.DataFrame,
                       avoidable_ed: pd.DataFrame) -> pd.DataFrame:
    """Calculate all KPIs and return as DataFrame."""
    kpis = []
    
    # High-Cost Claimants
    kpis.append(calculate_high_cost_concentration(claims))
    
    # Specialty Pharmacy
    kpis.append(calculate_specialty_rx_pmpm(claims, member_months))
    
    # ED Utilization
    kpis.append(calculate_ed_visits_per_1000(claims, member_months))
    kpis.append(calculate_avoidable_ed_rate(claims, avoidable_ed))
    kpis.append(calculate_ed_to_uc_shift_rate(claims, avoidable_ed))
    kpis.append(calculate_pcp_visit_post_ed(claims))
    
    # Behavioral Health
    kpis.append(calculate_bh_member_ed_rate(claims))
    kpis.append(calculate_bh_member_ip_rate(claims))
    
    # Readmissions
    kpis.append(calculate_readmission_rate(claims))
    
    # OON Leakage
    kpis.append(calculate_oon_allowed_pct(claims))
    
    # Member Retention
    kpis.append(calculate_disenrollment_rate(enrollment))
    kpis.append(calculate_cost_access_disenroll_pct(enrollment))
    
    # Financial
    kpis.append(calculate_total_medical_pmpm(claims, member_months))
    
    return pd.DataFrame(kpis)