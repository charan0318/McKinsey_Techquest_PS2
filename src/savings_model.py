"""
SummitBridge Analytics - Savings Model
Parameterized scenario modeling for all interventions.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class SavingsScenario:
    """Represents a savings scenario with parameters and results."""
    name: str
    specialty_reduction_pct: float = 0.0
    ed_shift_pct: float = 0.0
    hc_cm_reduction_pct: float = 0.0
    readmission_reduction_pct: float = 0.0
    oon_reduction_pct: float = 0.0
    bh_integration_reduction_pct: float = 0.0


class SavingsModel:
    """Savings modeling engine for SummitBridge interventions."""
    
    def __init__(self, claims: pd.DataFrame, enrollment: pd.DataFrame, 
                 member_months: pd.DataFrame, providers: pd.DataFrame,
                 avoidable_ed: pd.DataFrame):
        self.claims = claims
        self.enrollment = enrollment
        self.member_months = member_months
        self.providers = providers
        self.avoidable_ed = avoidable_ed
        
        # Pre-compute base metrics
        self._compute_base_metrics()
    
    def _compute_base_metrics(self):
        """Compute all base metrics needed for modeling."""
        # Total spend
        self.total_spend = self.claims['allowed_amount'].sum()
        
        # Specialty Rx
        self.specialty_total = self.claims[
            self.claims['service_category'] == 'Specialty Rx'
        ]['allowed_amount'].sum()
        
        # ED
        self.ed_claims = self.claims[self.claims['service_category'] == 'ED'].copy()
        self.ed_claims = self.ed_claims.merge(
            self.avoidable_ed[['icd10_code', 'avoidable_category']], 
            left_on='diagnosis_code_1', right_on='icd10_code', how='left'
        )
        self.avoidable_ed_claims = self.ed_claims[
            self.ed_claims['avoidable_category'].isin(['Avoidable', 'Potentially Avoidable'])
        ]
        self.avoidable_ed_count = len(self.avoidable_ed_claims)
        self.avoidable_ed_total = self.avoidable_ed_claims['allowed_amount'].sum()
        self.ed_avg_allowed = self.ed_claims['allowed_amount'].mean()
        self.uc_avg_allowed = self.claims[
            self.claims['service_category'] == 'Urgent Care'
        ]['allowed_amount'].mean()
        self.savings_per_ed_shift = self.ed_avg_allowed - self.uc_avg_allowed
        
        # High-cost members
        member_total = self.claims.groupby('member_id')['allowed_amount'].sum()
        hc_threshold = member_total.quantile(0.95)
        self.hc_members = member_total[member_total >= hc_threshold].index.tolist()
        self.hc_total = self.claims[
            self.claims['member_id'].isin(self.hc_members)
        ]['allowed_amount'].sum()
        
        # Readmissions
        ip_claims = self.claims[self.claims['service_category'] == 'Inpatient'].copy()
        ip_claims = ip_claims.sort_values(['member_id', 'service_from_date'])
        ip_claims['prev_discharge'] = ip_claims.groupby('member_id')['service_to_date'].shift(1)
        ip_claims['days_since_discharge'] = (ip_claims['service_from_date'] - ip_claims['prev_discharge']).dt.days
        ip_claims['is_readmission_30'] = ip_claims['days_since_discharge'] <= 30
        self.readmit_count = ip_claims['is_readmission_30'].sum()
        self.readmit_total = ip_claims[ip_claims['is_readmission_30']]['allowed_amount'].sum()
        self.total_ip = len(ip_claims)
        
        # OON
        self.oon_total = self.claims[self.claims['in_network_flag'] == 'N']['allowed_amount'].sum()
        
        # BH members
        self.bh_members = self.claims[
            self.claims['service_category'] == 'Behavioral Health'
        ]['member_id'].unique()
        self.bh_member_claims = self.claims[
            self.claims['member_id'].isin(self.bh_members)
        ]
        self.bh_ed_total = self.bh_member_claims[
            self.bh_member_claims['service_category'] == 'ED'
        ]['allowed_amount'].sum()
        self.bh_ip_total = self.bh_member_claims[
            self.bh_member_claims['service_category'] == 'Inpatient'
        ]['allowed_amount'].sum()
    
    def calculate_specialty_savings(self, reduction_pct: float) -> float:
        """Calculate savings from specialty pharmacy reduction."""
        return self.specialty_total * reduction_pct
    
    def calculate_ed_diversion_savings(self, shift_pct: float) -> float:
        """Calculate savings from ED to UC shift."""
        shifted_visits = self.avoidable_ed_count * shift_pct
        return shifted_visits * self.savings_per_ed_shift
    
    def calculate_hc_cm_savings(self, reduction_pct: float) -> float:
        """Calculate savings from high-cost care management."""
        return self.hc_total * reduction_pct
    
    def calculate_readmission_savings(self, reduction_pct: float) -> float:
        """Calculate savings from readmission reduction."""
        return self.readmit_total * reduction_pct
    
    def calculate_oon_savings(self, reduction_pct: float) -> float:
        """Calculate savings from OON leakage reduction."""
        return self.oon_total * reduction_pct
    
    def calculate_bh_integration_savings(self, reduction_pct: float) -> float:
        """Calculate savings from BH integration (ED + IP reduction)."""
        return (self.bh_ed_total + self.bh_ip_total) * reduction_pct
    
    def evaluate_scenario(self, scenario: SavingsScenario) -> Dict:
        """Evaluate a single scenario and return detailed results."""
        savings = {
            'specialty': self.calculate_specialty_savings(scenario.specialty_reduction_pct),
            'ed_diversion': self.calculate_ed_diversion_savings(scenario.ed_shift_pct),
            'hc_cm': self.calculate_hc_cm_savings(scenario.hc_cm_reduction_pct),
            'readmissions': self.calculate_readmission_savings(scenario.readmission_reduction_pct),
            'oon': self.calculate_oon_savings(scenario.oon_reduction_pct),
            'bh_integration': self.calculate_bh_integration_savings(scenario.bh_integration_reduction_pct),
        }
        
        total_savings = sum(savings.values())
        
        return {
            'scenario_name': scenario.name,
            'savings_breakdown': savings,
            'total_savings': total_savings,
            'pct_of_total_spend': total_savings / self.total_spend * 100,
            'parameters': {
                'specialty_reduction_pct': scenario.specialty_reduction_pct,
                'ed_shift_pct': scenario.ed_shift_pct,
                'hc_cm_reduction_pct': scenario.hc_cm_reduction_pct,
                'readmission_reduction_pct': scenario.readmission_reduction_pct,
                'oon_reduction_pct': scenario.oon_reduction_pct,
                'bh_integration_reduction_pct': scenario.bh_integration_reduction_pct,
            }
        }
    
    def evaluate_scenarios(self, scenarios: List[SavingsScenario]) -> pd.DataFrame:
        """Evaluate multiple scenarios and return comparison DataFrame."""
        results = []
        for scenario in scenarios:
            result = self.evaluate_scenario(scenario)
            row = {
                'Scenario': scenario.name,
                'Specialty Savings': result['savings_breakdown']['specialty'],
                'ED Diversion Savings': result['savings_breakdown']['ed_diversion'],
                'HC CM Savings': result['savings_breakdown']['hc_cm'],
                'Readmission Savings': result['savings_breakdown']['readmissions'],
                'OON Savings': result['savings_breakdown']['oon'],
                'BH Integration Savings': result['savings_breakdown']['bh_integration'],
                'Total Savings': result['total_savings'],
                'Pct of Total Spend': result['pct_of_total_spend'],
            }
            results.append(row)
        
        return pd.DataFrame(results)
    
    def get_base_metrics(self) -> Dict:
        """Return all base metrics for reporting."""
        return {
            'total_spend': self.total_spend,
            'specialty_total': self.specialty_total,
            'avoidable_ed_count': self.avoidable_ed_count,
            'avoidable_ed_total': self.avoidable_ed_total,
            'ed_avg_allowed': self.ed_avg_allowed,
            'uc_avg_allowed': self.uc_avg_allowed,
            'savings_per_ed_shift': self.savings_per_ed_shift,
            'hc_member_count': len(self.hc_members),
            'hc_total': self.hc_total,
            'hc_threshold': self.claims.groupby('member_id')['allowed_amount'].sum().quantile(0.95),
            'readmit_count': int(self.readmit_count),
            'readmit_total': self.readmit_total,
            'total_ip': self.total_ip,
            'readmit_rate': self.readmit_count / self.total_ip * 100,
            'oon_total': self.oon_total,
            'bh_member_count': len(self.bh_members),
            'bh_ed_total': self.bh_ed_total,
            'bh_ip_total': self.bh_ip_total,
        }


def create_standard_scenarios() -> List[SavingsScenario]:
    """Create standard scenario set for analysis."""
    return [
        SavingsScenario("Specialty Rx -5%", specialty_reduction_pct=0.05),
        SavingsScenario("Specialty Rx -10%", specialty_reduction_pct=0.10),
        SavingsScenario("Specialty Rx -15%", specialty_reduction_pct=0.15),
        SavingsScenario("ED Avoidable 10%→UC", ed_shift_pct=0.10),
        SavingsScenario("ED Avoidable 20%→UC", ed_shift_pct=0.20),
        SavingsScenario("ED Avoidable 30%→UC", ed_shift_pct=0.30),
        SavingsScenario("ED Avoidable 40%→UC", ed_shift_pct=0.40),
        SavingsScenario("HC Care Mgmt -5%", hc_cm_reduction_pct=0.05),
        SavingsScenario("HC Care Mgmt -10%", hc_cm_reduction_pct=0.10),
        SavingsScenario("HC Care Mgmt -15%", hc_cm_reduction_pct=0.15),
        SavingsScenario("Readmissions -20%", readmission_reduction_pct=0.20),
        SavingsScenario("Readmissions -30%", readmission_reduction_pct=0.30),
        SavingsScenario("OON Leakage -50%", oon_reduction_pct=0.50),
        SavingsScenario("BH Integration -15%", bh_integration_reduction_pct=0.15),
        SavingsScenario("BH Integration -20%", bh_integration_reduction_pct=0.20),
        SavingsScenario("Combined: Spec -10% + ED 20%", specialty_reduction_pct=0.10, ed_shift_pct=0.20),
        SavingsScenario("Combined: Spec -15% + ED 30%", specialty_reduction_pct=0.15, ed_shift_pct=0.30),
        SavingsScenario("Aggressive: Spec -15% + ED 40% + HC 15%", 
                       specialty_reduction_pct=0.15, ed_shift_pct=0.40, hc_cm_reduction_pct=0.15),
        SavingsScenario("Full Portfolio: All Interventions",
                       specialty_reduction_pct=0.10, ed_shift_pct=0.20, hc_cm_reduction_pct=0.10,
                       readmission_reduction_pct=0.20, oon_reduction_pct=0.50, bh_integration_reduction_pct=0.15),
    ]