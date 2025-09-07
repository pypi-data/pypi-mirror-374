"""
Actuarial domain knowledge for insurance causal analysis.
"""

from typing import List
from ...base.domain_knowledge import BaseDomainKnowledge


class ActuarialDomainKnowledge(BaseDomainKnowledge):
    """Insurance domain knowledge system."""
    
    def __init__(self):
        super().__init__("insurance")
        self.load_domain_knowledge()
    
    def load_domain_knowledge(self):
        """Load insurance domain knowledge."""
        # Industry risk factors
        self.add_causal_prior(
            cause="industry", effect="claims_frequency",
            relationship_type="categorical", strength=0.8, evidence_level="strong",
            context="Different industries have varying risk profiles"
        )
        
        # Company size effects
        self.add_causal_prior(
            cause="employee_count", effect="premium",
            relationship_type="positive", strength=0.9, evidence_level="strong", 
            context="Larger companies typically pay higher total premiums"
        )
    
    def get_likely_confounders(self, treatment: str, outcome: str, available_variables: List[str]) -> List[str]:
        """Get likely confounders for insurance analysis."""
        confounders = []
        
        # Common insurance confounders
        insurance_confounders = ['industry', 'company_size', 'employee_count', 'region', 'prior_claims']
        confounders.extend([c for c in insurance_confounders if c in available_variables])
        
        return confounders
    
    def get_causal_priors(self, variables: List[str]):
        """Get causal priors."""
        return list(self._causal_priors.values())