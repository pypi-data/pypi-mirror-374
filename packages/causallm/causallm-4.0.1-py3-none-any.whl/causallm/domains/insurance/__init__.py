"""
Insurance Domain Package for CausalLLM

This package provides insurance-specific components for causal analysis:

- Data generators for insurance scenarios (stop loss, claims, underwriting)
- Insurance domain knowledge and expertise  
- Analysis templates for risk assessment, premium optimization, and claims analysis

Key Features:
- Stop loss insurance analysis
- Claims frequency and severity modeling
- Risk factor assessment
- Premium optimization
- Underwriting decision support
"""

from .generators.insurance_data import InsuranceDataGenerator
from .knowledge.actuarial_knowledge import ActuarialDomainKnowledge
from .templates.risk_analysis import RiskAnalysisTemplate

class InsuranceDomain:
    """Main insurance domain interface."""
    
    def __init__(self):
        self.data_generator = InsuranceDataGenerator()
        self.domain_knowledge = ActuarialDomainKnowledge()
        self.risk_template = RiskAnalysisTemplate()
    
    def generate_stop_loss_data(self, n_policies: int = 1000, **kwargs):
        """Generate synthetic stop loss insurance data."""
        return self.data_generator.generate_stop_loss_data(n_policies, **kwargs)
    
    def analyze_risk_factors(self, data, risk_factor, outcome, **kwargs):
        """Analyze insurance risk factors."""
        return self.risk_template.run_analysis('risk_assessment', data, **kwargs)
    
    def get_insurance_confounders(self, treatment: str, outcome: str, available_vars: list):
        """Get insurance confounders for analysis."""
        return self.domain_knowledge.get_likely_confounders(treatment, outcome, available_vars)

__all__ = [
    'InsuranceDomain',
    'InsuranceDataGenerator', 
    'ActuarialDomainKnowledge',
    'RiskAnalysisTemplate'
]