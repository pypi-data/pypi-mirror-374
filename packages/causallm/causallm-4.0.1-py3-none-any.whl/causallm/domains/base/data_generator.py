"""
Base data generator for domain-specific synthetic data generation.
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass


@dataclass
class DomainVariable:
    """Definition of a domain-specific variable."""
    name: str
    description: str
    variable_type: str  # 'continuous', 'categorical', 'binary', 'ordinal'
    possible_values: Optional[List[Any]] = None
    distribution: Optional[str] = None  # 'normal', 'lognormal', 'binomial', etc.
    parameters: Optional[Dict[str, Any]] = None
    causal_parents: Optional[List[str]] = None
    domain_knowledge: Optional[str] = None


@dataclass 
class CausalStructure:
    """Definition of causal relationships between variables."""
    variables: List[DomainVariable]
    edges: List[Tuple[str, str]]  # (cause, effect) pairs
    confounders: List[str]
    mediators: List[str]
    colliders: List[str]
    domain_context: str


class BaseDomainDataGenerator(ABC):
    """
    Base class for domain-specific data generators.
    
    This class provides the framework for generating realistic synthetic data
    with proper causal structure for specific domains.
    """
    
    def __init__(self, domain_name: str, random_seed: int = 42):
        self.domain_name = domain_name
        self.random_seed = random_seed
        self.np_random = np.random.RandomState(random_seed)
        self.causal_structure = None
        
    @abstractmethod
    def get_causal_structure(self) -> CausalStructure:
        """Define the causal structure for this domain."""
        pass
    
    @abstractmethod
    def generate_base_variables(self, n_samples: int) -> pd.DataFrame:
        """Generate base/exogenous variables."""
        pass
    
    @abstractmethod 
    def apply_causal_mechanisms(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply causal relationships to generate endogenous variables."""
        pass
    
    def generate_data(self, n_samples: int, **kwargs) -> pd.DataFrame:
        """
        Generate complete synthetic dataset with proper causal structure.
        
        Args:
            n_samples: Number of samples to generate
            **kwargs: Domain-specific parameters
            
        Returns:
            DataFrame with synthetic data
        """
        # Set random seed for reproducibility
        np.random.seed(self.random_seed)
        
        # Get causal structure
        if self.causal_structure is None:
            self.causal_structure = self.get_causal_structure()
            
        # Generate base variables
        data = self.generate_base_variables(n_samples)
        
        # Apply causal mechanisms
        data = self.apply_causal_mechanisms(data)
        
        # Add metadata
        data.attrs['domain'] = self.domain_name
        data.attrs['n_samples'] = n_samples
        data.attrs['random_seed'] = self.random_seed
        data.attrs['causal_structure'] = self.causal_structure
        
        return data
    
    def get_variable_info(self, variable_name: str) -> Optional[DomainVariable]:
        """Get information about a specific variable."""
        if self.causal_structure is None:
            self.causal_structure = self.get_causal_structure()
            
        for var in self.causal_structure.variables:
            if var.name == variable_name:
                return var
        return None
    
    def get_causal_parents(self, variable_name: str) -> List[str]:
        """Get causal parents of a variable."""
        if self.causal_structure is None:
            self.causal_structure = self.get_causal_structure()
            
        parents = []
        for cause, effect in self.causal_structure.edges:
            if effect == variable_name:
                parents.append(cause)
        return parents
    
    def get_causal_children(self, variable_name: str) -> List[str]:
        """Get causal children of a variable."""
        if self.causal_structure is None:
            self.causal_structure = self.get_causal_structure()
            
        children = []
        for cause, effect in self.causal_structure.edges:
            if cause == variable_name:
                children.append(effect)
        return children
    
    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Validate the quality of generated data."""
        quality_report = {
            'n_samples': len(data),
            'n_variables': len(data.columns),
            'missing_values': data.isnull().sum().sum(),
            'duplicate_rows': data.duplicated().sum(),
            'variable_types': data.dtypes.to_dict(),
        }
        
        # Domain-specific validation can be added in subclasses
        return quality_report
    
    def generate_treatment_control_data(
        self, 
        n_samples: int,
        treatment_variable: str,
        treatment_probability: float = 0.5,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate data with treatment/control assignment.
        
        Args:
            n_samples: Number of samples
            treatment_variable: Name of treatment variable
            treatment_probability: Probability of treatment assignment
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with treatment assignment
        """
        data = self.generate_data(n_samples, **kwargs)
        
        # Add treatment assignment
        treatment = self.np_random.binomial(1, treatment_probability, n_samples)
        data[treatment_variable] = treatment
        
        return data
    
    def add_noise(self, data: pd.DataFrame, noise_level: float = 0.1) -> pd.DataFrame:
        """Add realistic noise to continuous variables."""
        noisy_data = data.copy()
        
        for col in data.select_dtypes(include=[np.number]).columns:
            std = data[col].std()
            noise = self.np_random.normal(0, std * noise_level, len(data))
            noisy_data[col] = data[col] + noise
            
        return noisy_data
    
    def create_missing_data_pattern(
        self, 
        data: pd.DataFrame, 
        missing_variables: List[str],
        missing_mechanism: str = 'MAR',
        missing_rate: float = 0.1
    ) -> pd.DataFrame:
        """
        Create realistic missing data patterns.
        
        Args:
            data: Input DataFrame
            missing_variables: Variables to introduce missingness
            missing_mechanism: 'MCAR', 'MAR', or 'MNAR'
            missing_rate: Proportion of missing values
            
        Returns:
            DataFrame with missing values
        """
        data_with_missing = data.copy()
        
        for var in missing_variables:
            if var not in data.columns:
                continue
                
            n_missing = int(len(data) * missing_rate)
            
            if missing_mechanism == 'MCAR':
                # Missing completely at random
                missing_idx = self.np_random.choice(
                    len(data), size=n_missing, replace=False
                )
            elif missing_mechanism == 'MAR':
                # Missing at random (depends on observed variables)
                # Simple implementation: higher missingness for certain values
                if data[var].dtype in ['int64', 'float64']:
                    # Higher missingness for extreme values
                    probs = np.abs(data[var] - data[var].mean()) / data[var].std()
                    probs = probs / probs.sum()
                else:
                    probs = np.ones(len(data)) / len(data)
                missing_idx = self.np_random.choice(
                    len(data), size=n_missing, replace=False, p=probs
                )
            else:  # MNAR
                # Missing not at random (depends on unobserved values)
                # Higher missingness for high/low values of the variable itself
                if data[var].dtype in ['int64', 'float64']:
                    probs = np.abs(data[var]) / np.sum(np.abs(data[var]))
                    missing_idx = self.np_random.choice(
                        len(data), size=n_missing, replace=False, p=probs
                    )
                else:
                    missing_idx = self.np_random.choice(
                        len(data), size=n_missing, replace=False
                    )
            
            data_with_missing.loc[missing_idx, var] = np.nan
            
        return data_with_missing