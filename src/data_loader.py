"""
SummitBridge Analytics - Data Loader
Standardized data loading with validation and caching.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

from src.config import (
    CLAIMS_CSV, ENROLLMENT_CSV, MEMBER_MONTHS_CSV, PROVIDERS_CSV,
    AVOIDABLE_ED_CSV, CLAIMS_XLSX, ENROLLMENT_XLSX,
    ANALYSIS_START, ANALYSIS_END
)

logger = logging.getLogger(__name__)


def load_claims(use_cache: bool = True) -> pd.DataFrame:
    """Load claims data with standard preprocessing."""
    if use_cache and CLAIMS_CSV.exists():
        df = pd.read_csv(CLAIMS_CSV)
        logger.info(f"Loaded claims from cache: {len(df):,} rows")
    else:
        df = pd.read_excel(CLAIMS_XLSX, sheet_name='claims')
        df.to_csv(CLAIMS_CSV, index=False)
        logger.info(f"Loaded claims from Excel: {len(df):,} rows")
    
    # Standard preprocessing
    df = _preprocess_claims(df)
    return df


def load_enrollment(use_cache: bool = True) -> pd.DataFrame:
    """Load enrollment data with standard preprocessing."""
    if use_cache and ENROLLMENT_CSV.exists():
        df = pd.read_csv(ENROLLMENT_CSV)
        logger.info(f"Loaded enrollment from cache: {len(df):,} rows")
    else:
        df = pd.read_excel(ENROLLMENT_XLSX, sheet_name='enrollment')
        df.to_csv(ENROLLMENT_CSV, index=False)
        logger.info(f"Loaded enrollment from Excel: {len(df):,} rows")
    
    df = _preprocess_enrollment(df)
    return df


def load_member_months(use_cache: bool = True) -> pd.DataFrame:
    """Load member months exposure data."""
    if use_cache and MEMBER_MONTHS_CSV.exists():
        df = pd.read_csv(MEMBER_MONTHS_CSV)
        logger.info(f"Loaded member_months from cache: {len(df):,} rows")
    else:
        df = pd.read_excel(CLAIMS_XLSX, sheet_name='member_months')
        df.to_csv(MEMBER_MONTHS_CSV, index=False)
        logger.info(f"Loaded member_months from Excel: {len(df):,} rows")
    
    df['calendar_month'] = pd.to_datetime(df['calendar_month'])
    return df


def load_providers(use_cache: bool = True) -> pd.DataFrame:
    """Load provider directory data."""
    if use_cache and PROVIDERS_CSV.exists():
        df = pd.read_csv(PROVIDERS_CSV)
        logger.info(f"Loaded providers from cache: {len(df):,} rows")
    else:
        df = pd.read_excel(CLAIMS_XLSX, sheet_name='providers')
        df.to_csv(PROVIDERS_CSV, index=False)
        logger.info(f"Loaded providers from Excel: {len(df):,} rows")
    
    return df


def load_avoidable_ed(use_cache: bool = True) -> pd.DataFrame:
    """Load avoidable ED ICD-10 reference table."""
    df = pd.read_csv(AVOIDABLE_ED_CSV)
    logger.info(f"Loaded avoidable_ed reference: {len(df):,} rows")
    return df


def load_all(use_cache: bool = True) -> Dict[str, pd.DataFrame]:
    """Load all datasets and return as dictionary."""
    return {
        'claims': load_claims(use_cache),
        'enrollment': load_enrollment(use_cache),
        'member_months': load_member_months(use_cache),
        'providers': load_providers(use_cache),
        'avoidable_ed': load_avoidable_ed(use_cache),
    }


def _preprocess_claims(df: pd.DataFrame) -> pd.DataFrame:
    """Standard claims preprocessing."""
    # Date columns
    date_cols = ['service_from_date', 'service_to_date', 'paid_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Numeric columns
    numeric_cols = ['allowed_amount', 'paid_amount', 'billed_amount', 'member_cost_share', 'units']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Categorical columns
    cat_cols = ['claim_type', 'service_category', 'lob', 'in_network_flag', 'plan_id']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    # Filter to analysis period
    if 'service_from_date' in df.columns:
        mask = (df['service_from_date'] >= ANALYSIS_START) & (df['service_from_date'] <= ANALYSIS_END)
        df = df[mask].copy()
        logger.info(f"Filtered claims to analysis period: {len(df):,} rows")
    
    return df


def _preprocess_enrollment(df: pd.DataFrame) -> pd.DataFrame:
    """Standard enrollment preprocessing."""
    # Date columns
    date_cols = ['enrollment_start_date', 'enrollment_end_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Numeric
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
    if 'risk_score' in df.columns:
        df['risk_score'] = pd.to_numeric(df['risk_score'], errors='coerce')
    
    # Categorical
    cat_cols = ['lob', 'product_name', 'state', 'county', 'gender', 'disenrollment_reason']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')
    
    return df


def get_claims_enriched(claims: pd.DataFrame, enrollment: pd.DataFrame, 
                        providers: pd.DataFrame, avoidable_ed: pd.DataFrame) -> pd.DataFrame:
    """Create enriched claims fact table with all dimensions."""
    df = claims.copy()
    
    # Merge enrollment (member demographics)
    enroll_cols = ['member_id', 'age', 'gender', 'state', 'county', 'lob', 
                   'risk_score', 'attributed_pcp_npi', 'disenrollment_reason']
    df = df.merge(enrollment[enroll_cols], on='member_id', how='left', suffixes=('', '_enroll'))
    
    # Merge provider (rendering provider attributes)
    prov_cols = ['npi', 'provider_name', 'provider_type', 'specialty_desc', 
                 'network_status', 'quality_score', 'accepting_new_patients', 'panel_size']
    df = df.merge(providers[prov_cols], left_on='rendering_npi', right_on='npi', 
                  how='left', suffixes=('', '_prov'))
    
    # Merge avoidable ED flag
    df = df.merge(avoidable_ed[['icd10_code', 'avoidable_category']], 
                  left_on='diagnosis_code_1', right_on='icd10_code', how='left')
    
    # High-cost member flag
    member_total = df.groupby('member_id')['allowed_amount'].sum()
    hc_threshold = member_total.quantile(0.95)
    df['is_high_cost'] = df['member_id'].map(member_total) >= hc_threshold
    
    return df


def calculate_member_pmpm(claims: pd.DataFrame, member_months: pd.DataFrame, 
                          enrollment: pd.DataFrame) -> pd.DataFrame:
    """Calculate PMPM at member level with demographics."""
    # Total allowed by member
    member_allowed = claims.groupby('member_id')['allowed_amount'].sum().reset_index()
    member_allowed.columns = ['member_id', 'total_allowed']
    
    # Total member months by member
    member_mm = member_months.groupby('member_id')['member_months'].sum().reset_index()
    
    # Merge
    pmpm = member_allowed.merge(member_mm, on='member_id', how='outer').fillna(0)
    pmpm['pmpm'] = pmpm['total_allowed'] / pmpm['member_months'].replace(0, 1)
    
    # Add demographics
    demo_cols = ['member_id', 'age', 'gender', 'state', 'lob', 'risk_score', 
                 'attributed_pcp_npi', 'disenrollment_reason']
    pmpm = pmpm.merge(enrollment[demo_cols], on='member_id', how='left')
    
    return pmpm