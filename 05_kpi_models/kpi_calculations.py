"""
KPI calculations wrapper for SummitBridge analytics.

This module provides a small orchestration layer around the reusable
KPI functions in `src.kpi_calculator` and attaches target/flag information
from `src.config` for easy reporting and export.
"""
from typing import Dict, Any, Optional
import pandas as pd

from src.kpi_calculator import calculate_all_kpis
from src.config import KPI_TARGETS


def compute_all_kpis(claims: pd.DataFrame,
                     enrollment: pd.DataFrame,
                     member_months: pd.DataFrame,
                     providers: pd.DataFrame,
                     avoidable_ed: pd.DataFrame,
                     targets: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """Run all KPI functions and attach targets/status.

    Returns a DataFrame with columns: `kpi`, `value`, `target`, `status`, plus
    any auxiliary fields provided by the KPI functions.
    Status logic: if a numeric `target` is available then `on_target` means
    the value is <= target; otherwise status is `no_target` or `missing`.
    (If a KPI is higher-is-better, pass a custom `targets` mapping with
    negative numbers or adjust after computing.)
    """
    targets = targets or KPI_TARGETS

    df = calculate_all_kpis(claims, enrollment, member_months, providers, avoidable_ed)

    # Ensure DataFrame has expected shape
    if 'kpi' not in df.columns:
        df = pd.DataFrame(df)

    # Attach target and status
    def _status(row: Dict[str, Any]) -> str:
        k = row.get('kpi')
        val = row.get('value')
        tgt = targets.get(k) if k in targets else None
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return 'missing'
        if tgt is None:
            return 'no_target'
        try:
            # simple rule: lower is better
            return 'on_target' if float(val) <= float(tgt) else 'above_target'
        except Exception:
            return 'unknown'

    df = df.copy()
    df['target'] = df['kpi'].map(lambda k: targets.get(k))
    df['status'] = df.apply(_status, axis=1)

    # Reorder columns for readability
    cols = ['kpi', 'value', 'target', 'status'] + [c for c in df.columns if c not in ('kpi','value','target','status')]
    df = df.loc[:, cols]
    return df


def save_kpis(df: pd.DataFrame, path: str) -> None:
    """Save KPI report to CSV at `path`. Overwrites if exists."""
    df.to_csv(path, index=False)
