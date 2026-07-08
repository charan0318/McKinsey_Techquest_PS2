"""
SummitBridge Analytics - Configuration
Centralized paths, parameters, and thresholds.
"""
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_REFERENCE = PROJECT_ROOT / "data" / "reference"

# Raw files
CLAIMS_XLSX = DATA_RAW / "Summitbridge data (1).xlsx"
ENROLLMENT_XLSX = DATA_RAW / "Summitbridge data (1).xlsx"

# Processed files
CLAIMS_CSV = DATA_PROCESSED / "claims.csv"
ENROLLMENT_CSV = DATA_PROCESSED / "enrollment.csv"
MEMBER_MONTHS_CSV = DATA_PROCESSED / "member_months.csv"
PROVIDERS_CSV = DATA_PROCESSED / "providers.csv"

# Reference files
AVOIDABLE_ED_CSV = DATA_REFERENCE / "avoidable_ed_reference.csv"

# Analysis parameters
ANALYSIS_START = "2024-01-01"
ANALYSIS_END = "2024-12-31"
HIGH_COST_PERCENTILE = 0.95  # Top 5%

# KPI Targets
KPI_TARGETS = {
    "high_cost_concentration_pct": 15.0,
    "avoidable_ed_rate_pct": 60.0,
    "ed_visits_per_1000": 45.0,
    "readmission_rate_pct": 12.0,
    "oon_allowed_pct": 1.0,
    "disenrollment_rate_pct": 8.0,
    "cost_access_disenroll_pct": 40.0,
    "medical_pmpm_trend_pct": 5.0,
}

# Savings modeling defaults
SAVINGS_DEFAULTS = {
    "specialty_reduction_pct": [5, 10, 15],
    "ed_shift_pct": [10, 20, 30, 40],
    "hc_cm_reduction_pct": [5, 10, 15, 20],
    "readmission_reduction_pct": [20, 30],
}

# Visualization defaults
VIZ_COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e",
    "success": "#2ca02c",
    "danger": "#d62728",
    "warning": "#ff7f0e",
    "info": "#17a2b8",
}
VIZ_COLOR_SEQ = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

# Service category ordering
SERVICE_CATEGORY_ORDER = [
    "Inpatient",
    "ED",
    "Specialty Rx",
    "PCP",
    "Urgent Care",
    "Behavioral Health",
]

# LOB ordering
LOB_ORDER = ["Commercial", "Marketplace", "Medicare Advantage"]

# State ordering
STATE_ORDER = ["KY", "GA", "TN", "OH"]

# Avoidable ED categories
AVOIDABLE_CATEGORIES = ["Avoidable", "Potentially Avoidable", "Non-Avoidable"]