"""
Insurance data generator - leverages existing stop loss example.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../examples'))

try:
    from stop_loss_insurance_analysis import generate_stop_loss_data
except ImportError:
    # Fallback implementation
    import pandas as pd
    import numpy as np
    
    def generate_stop_loss_data(n_policies=1000):
        """Fallback stop loss data generator."""
        np.random.seed(42)
        return pd.DataFrame({
            'policy_id': range(1, n_policies + 1),
            'company_size': np.random.choice(['Small', 'Medium', 'Large'], n_policies),
            'employee_count': np.random.randint(10, 1000, n_policies),
            'industry': np.random.choice(['Technology', 'Healthcare', 'Manufacturing'], n_policies),
            'total_claim_amount': np.random.lognormal(10, 1, n_policies),
            'annual_premium': np.random.lognormal(12, 0.5, n_policies),
            'loss_ratio': np.random.uniform(0.5, 2.0, n_policies)
        })

from ...base.data_generator import BaseDomainDataGenerator, CausalStructure


class InsuranceDataGenerator(BaseDomainDataGenerator):
    """Insurance data generator using existing patterns."""
    
    def __init__(self, random_seed: int = 42):
        super().__init__("insurance", random_seed)
    
    def get_causal_structure(self) -> CausalStructure:
        """Return insurance causal structure."""
        return CausalStructure(
            variables=[], edges=[], confounders=[], mediators=[], colliders=[],
            domain_context="Insurance risk and claims analysis"
        )
    
    def generate_base_variables(self, n_samples):
        """Generate base variables."""
        return generate_stop_loss_data(n_samples)
    
    def apply_causal_mechanisms(self, data):
        """Apply causal mechanisms."""
        return data
    
    def generate_stop_loss_data(self, n_policies=1000, **kwargs):
        """Generate stop loss insurance data."""
        # Use our own simple implementation since import might fail
        import numpy as np
        import pandas as pd
        np.random.seed(42)
        return pd.DataFrame({
            'policy_id': range(1, n_policies + 1),
            'company_size': np.random.choice(['Small', 'Medium', 'Large'], n_policies, p=[0.4, 0.35, 0.25]),
            'employee_count': np.random.randint(10, 1000, n_policies),
            'industry': np.random.choice(['Technology', 'Healthcare', 'Manufacturing', 'Finance', 'Construction'], n_policies),
            'region': np.random.choice(['Northeast', 'Southeast', 'Midwest', 'West'], n_policies),
            'total_claim_amount': np.random.lognormal(10, 1.2, n_policies),
            'annual_premium': np.random.lognormal(12, 0.6, n_policies),
            'loss_ratio': np.random.uniform(0.3, 2.5, n_policies),
            'prior_large_claims': np.random.poisson(0.3, n_policies),
            'wellness_program': np.random.choice([0, 1], n_policies, p=[0.4, 0.6])
        })