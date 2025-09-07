"""
CausalLLM Domain Packages

This module provides domain-specific components for causal analysis across various industries
and use cases. Each domain package includes:

- Data generators for realistic synthetic data
- Domain knowledge and expertise
- Pre-configured analysis templates
- Industry-specific metrics and KPIs

Available Domains:
- healthcare: Clinical analysis, treatment effectiveness, patient outcomes
- insurance: Risk assessment, premium optimization, claims analysis
- marketing: Campaign attribution, ROI optimization, customer analytics
- education: Student outcomes, intervention analysis, policy evaluation
- experimentation: A/B testing, experimental design, causal inference
"""

from .healthcare import HealthcareDomain
from .insurance import InsuranceDomain  
from .marketing import MarketingDomain
from .education import EducationDomain
from .experimentation import ExperimentationDomain

__all__ = [
    'HealthcareDomain',
    'InsuranceDomain', 
    'MarketingDomain',
    'EducationDomain',
    'ExperimentationDomain'
]