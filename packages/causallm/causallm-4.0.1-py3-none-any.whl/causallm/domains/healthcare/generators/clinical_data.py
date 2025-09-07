"""
Clinical data generator for healthcare domain.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import warnings

from ...base.data_generator import BaseDomainDataGenerator, DomainVariable, CausalStructure


class ClinicalDataGenerator(BaseDomainDataGenerator):
    """
    Generates realistic clinical data with proper causal structure.
    
    This generator creates synthetic patient data that reflects real-world
    clinical relationships and can be used for treatment effectiveness analysis,
    outcomes research, and clinical decision support validation.
    """
    
    def __init__(self, random_seed: int = 42):
        super().__init__("healthcare", random_seed)
        
    def get_causal_structure(self) -> CausalStructure:
        """Define causal structure for clinical data."""
        
        variables = [
            # Patient demographics (exogenous)
            DomainVariable(
                name="age",
                description="Patient age in years",
                variable_type="continuous",
                distribution="normal",
                parameters={"mean": 58, "std": 18},
                domain_knowledge="Age is a fundamental confounder in clinical studies"
            ),
            DomainVariable(
                name="gender",
                description="Patient gender",
                variable_type="categorical", 
                possible_values=["Male", "Female"],
                domain_knowledge="Gender affects treatment response and disease progression"
            ),
            
            # Comorbidities (influenced by age)
            DomainVariable(
                name="diabetes",
                description="Diabetes mellitus diagnosis",
                variable_type="binary",
                causal_parents=["age"],
                domain_knowledge="Diabetes prevalence increases with age"
            ),
            DomainVariable(
                name="hypertension", 
                description="Hypertension diagnosis",
                variable_type="binary",
                causal_parents=["age"],
                domain_knowledge="Hypertension prevalence increases with age"
            ),
            DomainVariable(
                name="heart_disease",
                description="Coronary heart disease",
                variable_type="binary", 
                causal_parents=["age", "diabetes", "hypertension"],
                domain_knowledge="Heart disease risk increases with age and comorbidities"
            ),
            
            # Disease severity (influenced by age and comorbidities)
            DomainVariable(
                name="disease_severity",
                description="Disease severity score (0-100)",
                variable_type="continuous",
                causal_parents=["age", "diabetes", "hypertension", "heart_disease"],
                domain_knowledge="Disease severity affected by patient characteristics"
            ),
            
            # Hospital factors
            DomainVariable(
                name="hospital_type",
                description="Type of hospital",
                variable_type="categorical",
                possible_values=["academic", "community", "specialized"],
                domain_knowledge="Hospital type affects treatment protocols"
            ),
            
            # Treatment assignment (influenced by severity and hospital)
            DomainVariable(
                name="treatment",
                description="Treatment received",
                variable_type="categorical",
                possible_values=["standard", "intensive", "experimental"],
                causal_parents=["disease_severity", "hospital_type"],
                domain_knowledge="Treatment choice depends on patient severity and hospital capabilities"
            ),
            
            # Outcomes (influenced by treatment, patient characteristics)
            DomainVariable(
                name="recovery_time",
                description="Time to recovery (days)", 
                variable_type="continuous",
                causal_parents=["treatment", "age", "disease_severity", "diabetes", "hypertension"],
                domain_knowledge="Recovery time depends on treatment and patient characteristics"
            ),
            DomainVariable(
                name="complications",
                description="Post-treatment complications",
                variable_type="binary",
                causal_parents=["treatment", "age", "disease_severity", "heart_disease"],
                domain_knowledge="Complication risk varies by treatment and patient risk factors"
            ),
            DomainVariable(
                name="readmission_30d",
                description="30-day readmission",
                variable_type="binary", 
                causal_parents=["complications", "disease_severity", "age"],
                domain_knowledge="Readmission risk affected by complications and patient characteristics"
            )
        ]
        
        edges = [
            # Age effects
            ("age", "diabetes"),
            ("age", "hypertension"), 
            ("age", "heart_disease"),
            ("age", "disease_severity"),
            ("age", "recovery_time"),
            ("age", "complications"),
            ("age", "readmission_30d"),
            
            # Comorbidity effects
            ("diabetes", "heart_disease"),
            ("diabetes", "disease_severity"),
            ("diabetes", "recovery_time"),
            ("hypertension", "heart_disease"),
            ("hypertension", "disease_severity"),
            ("hypertension", "recovery_time"),
            ("heart_disease", "disease_severity"),
            ("heart_disease", "complications"),
            
            # Treatment selection
            ("disease_severity", "treatment"),
            ("hospital_type", "treatment"),
            
            # Treatment effects
            ("treatment", "recovery_time"),
            ("treatment", "complications"),
            
            # Outcome relationships
            ("disease_severity", "recovery_time"),
            ("disease_severity", "complications"),
            ("disease_severity", "readmission_30d"),
            ("complications", "readmission_30d")
        ]
        
        return CausalStructure(
            variables=variables,
            edges=edges,
            confounders=["age", "diabetes", "hypertension", "disease_severity"],
            mediators=["complications"],
            colliders=["heart_disease"],
            domain_context="Clinical healthcare with treatment assignment and patient outcomes"
        )
    
    def generate_base_variables(self, n_samples: int) -> pd.DataFrame:
        """Generate base/exogenous variables."""
        data = pd.DataFrame()
        
        # Patient demographics
        data['age'] = np.clip(self.np_random.normal(58, 18, n_samples), 18, 95)
        data['gender'] = self.np_random.choice(['Male', 'Female'], n_samples, p=[0.48, 0.52])
        
        # Hospital type (independent of patient characteristics for simplicity)
        data['hospital_type'] = self.np_random.choice(
            ['academic', 'community', 'specialized'], 
            n_samples, 
            p=[0.3, 0.5, 0.2]
        )
        
        return data
    
    def apply_causal_mechanisms(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply causal relationships to generate endogenous variables."""
        n_samples = len(data)
        
        # Comorbidities (influenced by age)
        diabetes_prob = np.clip(0.05 + 0.008 * (data['age'] - 30), 0, 0.4)
        data['diabetes'] = self.np_random.binomial(1, diabetes_prob, n_samples)
        
        hypertension_prob = np.clip(0.1 + 0.012 * (data['age'] - 25), 0, 0.6)
        data['hypertension'] = self.np_random.binomial(1, hypertension_prob, n_samples)
        
        # Heart disease (influenced by age and comorbidities)
        heart_disease_base = 0.02 + 0.006 * (data['age'] - 40)
        heart_disease_prob = heart_disease_base + 0.15 * data['diabetes'] + 0.1 * data['hypertension']
        heart_disease_prob = np.clip(heart_disease_prob, 0, 0.5)
        data['heart_disease'] = self.np_random.binomial(1, heart_disease_prob, n_samples)
        
        # Disease severity (influenced by age and comorbidities)
        comorbidity_count = data['diabetes'] + data['hypertension'] + data['heart_disease']
        severity_base = 20 + 0.8 * (data['age'] - 30) + 15 * comorbidity_count
        data['disease_severity'] = severity_base + self.np_random.normal(0, 12, n_samples)
        data['disease_severity'] = np.clip(data['disease_severity'], 0, 100)
        
        # Treatment assignment (influenced by severity and hospital type)
        treatment_probs = []
        for i in range(n_samples):
            severity = data.loc[i, 'disease_severity']
            hospital = data.loc[i, 'hospital_type']
            
            # Base probabilities by severity
            if severity >= 70:  # Severe
                base_probs = [0.2, 0.3, 0.5]  # More aggressive for severe cases
            elif severity >= 40:  # Moderate  
                base_probs = [0.4, 0.4, 0.2]  # Balanced for moderate
            else:  # Mild
                base_probs = [0.6, 0.3, 0.1]  # Conservative for mild
            
            # Hospital type modifies probabilities
            if hospital == 'academic':
                # Academic hospitals more likely to use experimental
                probs = [base_probs[0] * 0.8, base_probs[1], base_probs[2] * 1.5]
            elif hospital == 'specialized':
                # Specialized hospitals more intensive care
                probs = [base_probs[0] * 0.7, base_probs[1] * 1.3, base_probs[2]]
            else:  # Community
                probs = base_probs
            
            # Normalize probabilities
            probs = np.array(probs) / np.sum(probs)
            treatment_probs.append(probs)
        
        treatments = []
        for i in range(n_samples):
            treatment_idx = self.np_random.choice(3, p=treatment_probs[i])
            treatments.append(['standard', 'intensive', 'experimental'][treatment_idx])
        data['treatment'] = treatments
        
        # Recovery time (influenced by treatment and patient characteristics)
        base_recovery = 15 + 0.3 * data['age'] + 0.4 * data['disease_severity']
        
        # Treatment effects on recovery
        treatment_effect = np.where(
            data['treatment'] == 'standard', 0,
            np.where(data['treatment'] == 'intensive', -3, -5)  # Negative = faster recovery
        )
        
        # Comorbidity effects
        comorbidity_effect = 3 * data['diabetes'] + 2 * data['hypertension']
        
        recovery_time = base_recovery + treatment_effect + comorbidity_effect
        recovery_time += self.np_random.normal(0, 4, n_samples)
        data['recovery_time'] = np.clip(recovery_time, 1, 60)
        
        # Complications (influenced by treatment, age, severity, heart disease)
        complication_base = 0.1 + 0.002 * data['age'] + 0.005 * data['disease_severity']
        
        # Treatment effects on complications
        treatment_complication_effect = np.where(
            data['treatment'] == 'standard', 0,
            np.where(data['treatment'] == 'intensive', 0.05, 0.08)  # More intensive = more complications
        )
        
        complication_prob = complication_base + treatment_complication_effect + 0.1 * data['heart_disease']
        complication_prob = np.clip(complication_prob, 0, 0.5)
        data['complications'] = self.np_random.binomial(1, complication_prob, n_samples)
        
        # 30-day readmission (influenced by complications, severity, age)
        readmission_base = 0.05 + 0.001 * data['age'] + 0.003 * data['disease_severity']
        readmission_prob = readmission_base + 0.2 * data['complications'] 
        readmission_prob = np.clip(readmission_prob, 0, 0.4)
        data['readmission_30d'] = self.np_random.binomial(1, readmission_prob, n_samples)
        
        return data
    
    def generate_clinical_trial_data(
        self,
        n_patients: int = 1000,
        treatment_arms: List[str] = None,
        randomization_ratio: List[float] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate data that resembles a randomized clinical trial.
        
        Args:
            n_patients: Number of patients
            treatment_arms: List of treatment names
            randomization_ratio: Ratio for randomization
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with clinical trial structure
        """
        if treatment_arms is None:
            treatment_arms = ['control', 'treatment']
        if randomization_ratio is None:
            randomization_ratio = [0.5, 0.5]
        
        # Generate base data
        data = self.generate_data(n_patients, **kwargs)
        
        # Override treatment assignment with randomization
        treatment_assignment = self.np_random.choice(
            treatment_arms, 
            n_patients, 
            p=randomization_ratio
        )
        data['treatment'] = treatment_assignment
        
        # Recalculate outcomes based on new treatment assignment
        # (This is a simplified approach - in reality, you'd want more sophisticated modeling)
        if 'treatment' in treatment_arms and 'control' in treatment_arms:
            # Apply treatment effect
            treatment_mask = data['treatment'] == 'treatment'
            data.loc[treatment_mask, 'recovery_time'] *= 0.85  # 15% reduction in recovery time
            
            # Slightly higher complications for treatment group (realistic trade-off)
            complication_increase = self.np_random.binomial(
                1, 0.02, treatment_mask.sum()
            )
            data.loc[treatment_mask, 'complications'] = np.maximum(
                data.loc[treatment_mask, 'complications'], 
                complication_increase
            )
        
        # Add trial-specific variables
        data['study_site'] = self.np_random.choice(
            [f'Site_{i}' for i in range(1, 6)], n_patients
        )
        data['enrollment_date'] = pd.date_range('2023-01-01', periods=n_patients, freq='D')
        
        return data
    
    def generate_patient_cohort_data(
        self,
        n_patients: int = 1000, 
        cohort_type: str = 'mixed',
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate observational cohort data.
        
        Args:
            n_patients: Number of patients
            cohort_type: 'mixed', 'high_risk', 'low_risk', 'elderly'
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with cohort characteristics
        """
        # Adjust parameters based on cohort type
        if cohort_type == 'high_risk':
            # Older patients with more comorbidities
            self._adjust_age_distribution(70, 15)
        elif cohort_type == 'low_risk':
            # Younger, healthier patients
            self._adjust_age_distribution(45, 12)
        elif cohort_type == 'elderly':
            # Elderly patients
            self._adjust_age_distribution(75, 10)
        
        data = self.generate_data(n_patients, **kwargs)
        
        # Add cohort-specific variables
        data['cohort_type'] = cohort_type
        data['follow_up_time'] = self.np_random.exponential(365, n_patients)  # Days
        
        return data
    
    def _adjust_age_distribution(self, mean_age: float, std_age: float):
        """Temporarily adjust age distribution for specific cohorts."""
        # This would modify the age generation parameters
        # Implementation depends on how you want to handle parameter modification
        pass