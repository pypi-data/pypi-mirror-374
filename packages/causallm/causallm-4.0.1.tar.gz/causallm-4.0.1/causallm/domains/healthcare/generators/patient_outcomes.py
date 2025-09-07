"""
Patient outcome data generator for healthcare domain.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

from ...base.data_generator import BaseDomainDataGenerator, DomainVariable, CausalStructure


class PatientOutcomeGenerator(BaseDomainDataGenerator):
    """
    Generates realistic patient outcome data for healthcare analysis.
    
    This generator focuses on patient outcomes, quality metrics,
    and healthcare utilization patterns.
    """
    
    def __init__(self, random_seed: int = 42):
        super().__init__("healthcare_outcomes", random_seed)
    
    def get_causal_structure(self) -> CausalStructure:
        """Define causal structure for patient outcomes."""
        
        variables = [
            # Patient characteristics
            DomainVariable(
                name="patient_age", 
                description="Patient age at admission",
                variable_type="continuous",
                distribution="normal",
                parameters={"mean": 62, "std": 16}
            ),
            DomainVariable(
                name="insurance_type",
                description="Insurance coverage type",
                variable_type="categorical",
                possible_values=["Medicare", "Medicaid", "Commercial", "Uninsured"]
            ),
            DomainVariable(
                name="socioeconomic_status",
                description="Socioeconomic status score",
                variable_type="continuous",
                causal_parents=["insurance_type"]
            ),
            
            # Clinical factors
            DomainVariable(
                name="charlson_score",
                description="Charlson comorbidity index",
                variable_type="continuous", 
                causal_parents=["patient_age"]
            ),
            DomainVariable(
                name="admission_severity",
                description="Severity of illness at admission",
                variable_type="ordinal",
                possible_values=["mild", "moderate", "severe", "critical"],
                causal_parents=["charlson_score", "patient_age"]
            ),
            
            # Process of care
            DomainVariable(
                name="care_coordination",
                description="Quality of care coordination",
                variable_type="continuous",
                causal_parents=["insurance_type", "socioeconomic_status"]
            ),
            DomainVariable(
                name="length_of_stay",
                description="Hospital length of stay (days)",
                variable_type="continuous",
                causal_parents=["admission_severity", "charlson_score", "care_coordination"]
            ),
            
            # Outcomes
            DomainVariable(
                name="patient_satisfaction",
                description="Patient satisfaction score (0-10)",
                variable_type="continuous",
                causal_parents=["care_coordination", "length_of_stay", "insurance_type"]
            ),
            DomainVariable(
                name="functional_status",
                description="Functional status at discharge",
                variable_type="continuous",
                causal_parents=["admission_severity", "patient_age", "care_coordination"]
            ),
            DomainVariable(
                name="mortality_risk",
                description="30-day mortality risk",
                variable_type="continuous",
                causal_parents=["admission_severity", "charlson_score", "care_coordination"]
            )
        ]
        
        edges = [
            ("patient_age", "charlson_score"),
            ("patient_age", "admission_severity"), 
            ("patient_age", "functional_status"),
            ("insurance_type", "socioeconomic_status"),
            ("insurance_type", "care_coordination"),
            ("insurance_type", "patient_satisfaction"),
            ("socioeconomic_status", "care_coordination"),
            ("charlson_score", "admission_severity"),
            ("charlson_score", "length_of_stay"),
            ("charlson_score", "mortality_risk"),
            ("admission_severity", "length_of_stay"),
            ("admission_severity", "functional_status"),
            ("admission_severity", "mortality_risk"),
            ("care_coordination", "length_of_stay"),
            ("care_coordination", "patient_satisfaction"),
            ("care_coordination", "functional_status"),
            ("care_coordination", "mortality_risk"),
            ("length_of_stay", "patient_satisfaction")
        ]
        
        return CausalStructure(
            variables=variables,
            edges=edges,
            confounders=["patient_age", "charlson_score", "insurance_type"],
            mediators=["care_coordination", "length_of_stay"],
            colliders=["admission_severity"],
            domain_context="Patient outcomes and healthcare quality"
        )
    
    def generate_base_variables(self, n_samples: int) -> pd.DataFrame:
        """Generate base variables."""
        data = pd.DataFrame()
        
        # Patient demographics
        data['patient_age'] = np.clip(self.np_random.normal(62, 16, n_samples), 18, 95)
        data['insurance_type'] = self.np_random.choice(
            ["Medicare", "Medicaid", "Commercial", "Uninsured"],
            n_samples,
            p=[0.4, 0.2, 0.35, 0.05]
        )
        
        return data
    
    def apply_causal_mechanisms(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply causal mechanisms."""
        n_samples = len(data)
        
        # Socioeconomic status (influenced by insurance)
        ses_base = self.np_random.normal(50, 15, n_samples)
        insurance_effect = np.where(
            data['insurance_type'] == 'Commercial', 10,
            np.where(data['insurance_type'] == 'Medicare', 0,
                    np.where(data['insurance_type'] == 'Medicaid', -8, -15))
        )
        data['socioeconomic_status'] = np.clip(ses_base + insurance_effect, 0, 100)
        
        # Charlson score (influenced by age)
        charlson_base = 0.1 * (data['patient_age'] - 40) + self.np_random.exponential(1, n_samples)
        data['charlson_score'] = np.clip(charlson_base, 0, 15)
        
        # Admission severity (influenced by age and comorbidity)
        severity_scores = (0.02 * data['patient_age'] + 0.5 * data['charlson_score'] + 
                          self.np_random.normal(0, 2, n_samples))
        severity_categories = pd.cut(
            severity_scores,
            bins=[-np.inf, 2, 5, 8, np.inf],
            labels=["mild", "moderate", "severe", "critical"]
        )
        data['admission_severity'] = severity_categories
        
        # Care coordination (influenced by insurance and SES)
        care_base = 0.3 * data['socioeconomic_status'] + self.np_random.normal(20, 8, n_samples)
        insurance_care_effect = np.where(
            data['insurance_type'] == 'Commercial', 5,
            np.where(data['insurance_type'] == 'Medicare', 2,
                    np.where(data['insurance_type'] == 'Medicaid', -3, -8))
        )
        data['care_coordination'] = np.clip(care_base + insurance_care_effect, 0, 100)
        
        # Length of stay (influenced by severity, comorbidity, care coordination)
        severity_numeric = data['admission_severity'].map({
            "mild": 1, "moderate": 2, "severe": 3, "critical": 4
        })
        los_base = 2 + 1.5 * severity_numeric + 0.3 * data['charlson_score']
        care_effect = -0.05 * data['care_coordination']  # Better care = shorter stay
        los = los_base + care_effect + self.np_random.exponential(1, n_samples)
        data['length_of_stay'] = np.clip(los, 1, 30)
        
        # Patient satisfaction (influenced by care coordination, LOS, insurance)
        satisfaction_base = 0.08 * data['care_coordination'] - 0.1 * data['length_of_stay']
        insurance_satisfaction_effect = np.where(
            data['insurance_type'] == 'Commercial', 1,
            np.where(data['insurance_type'] == 'Medicare', 0.5, 0)
        )
        satisfaction = (satisfaction_base + insurance_satisfaction_effect + 
                       self.np_random.normal(5, 1.5, n_samples))
        data['patient_satisfaction'] = np.clip(satisfaction, 0, 10)
        
        # Functional status (influenced by age, severity, care coordination)
        functional_base = 90 - 0.3 * data['patient_age'] - 5 * severity_numeric
        care_functional_effect = 0.1 * data['care_coordination']
        functional_status = (functional_base + care_functional_effect + 
                           self.np_random.normal(0, 8, n_samples))
        data['functional_status'] = np.clip(functional_status, 0, 100)
        
        # Mortality risk (influenced by severity, comorbidity, care)
        mortality_base = 0.01 + 0.02 * severity_numeric + 0.01 * data['charlson_score']
        care_mortality_effect = -0.001 * data['care_coordination']  # Better care = lower mortality
        mortality_risk = mortality_base + care_mortality_effect
        data['mortality_risk'] = np.clip(mortality_risk, 0, 1)
        
        return data
    
    def generate_quality_metrics_data(
        self,
        n_patients: int = 1000,
        include_outcomes: List[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate data focused on healthcare quality metrics.
        
        Args:
            n_patients: Number of patients
            include_outcomes: Specific outcomes to include
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with quality metrics
        """
        if include_outcomes is None:
            include_outcomes = ['patient_satisfaction', 'functional_status', 'mortality_risk']
        
        data = self.generate_data(n_patients, **kwargs)
        
        # Add additional quality metrics
        data['readmission_30d'] = self.np_random.binomial(
            1, np.clip(data['mortality_risk'] * 3, 0, 0.3), n_patients
        )
        
        data['medication_adherence'] = np.clip(
            80 + 0.2 * data['care_coordination'] - 0.1 * data['patient_age'] +
            self.np_random.normal(0, 10, n_patients), 0, 100
        )
        
        # Hospital-acquired infection risk
        data['hai_risk'] = np.clip(
            0.02 + 0.005 * data['length_of_stay'] - 0.0002 * data['care_coordination'],
            0, 0.2
        )
        
        # Filter to requested outcomes
        outcome_cols = [col for col in data.columns if col in include_outcomes]
        basic_cols = ['patient_age', 'insurance_type', 'charlson_score', 'care_coordination']
        
        return data[basic_cols + outcome_cols]
    
    def generate_cost_analysis_data(
        self,
        n_patients: int = 1000,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate data for healthcare cost analysis.
        
        Args:
            n_patients: Number of patients
            **kwargs: Additional parameters
            
        Returns:
            DataFrame with cost variables
        """
        data = self.generate_data(n_patients, **kwargs)
        
        # Calculate costs based on patient characteristics
        base_cost = 5000  # Base cost per admission
        
        # Length of stay cost
        los_cost = data['length_of_stay'] * 1200  # $1200 per day
        
        # Severity-based cost multiplier
        severity_multiplier = data['admission_severity'].map({
            "mild": 1.0, "moderate": 1.5, "severe": 2.0, "critical": 3.0
        })
        
        # Comorbidity cost
        comorbidity_cost = data['charlson_score'] * 800
        
        # Calculate total cost
        total_cost = (base_cost + los_cost + comorbidity_cost) * severity_multiplier
        total_cost += self.np_random.normal(0, total_cost * 0.1, n_patients)  # Add noise
        data['total_cost'] = np.maximum(total_cost, 1000)  # Minimum cost
        
        # Insurance payment
        payment_rate = data['insurance_type'].map({
            "Medicare": 0.85, "Medicaid": 0.75, "Commercial": 0.95, "Uninsured": 0.3
        })
        data['insurance_payment'] = data['total_cost'] * payment_rate
        data['patient_payment'] = data['total_cost'] - data['insurance_payment']
        
        # Add cost-effectiveness metrics
        data['cost_per_quality_day'] = data['total_cost'] / np.maximum(
            data['functional_status'] / 10, 1
        )
        
        return data
    
    def generate_longitudinal_data(
        self,
        n_patients: int = 500,
        n_timepoints: int = 6,
        follow_up_months: int = 12,
        **kwargs
    ) -> pd.DataFrame:
        """
        Generate longitudinal patient outcome data.
        
        Args:
            n_patients: Number of patients
            n_timepoints: Number of follow-up timepoints
            follow_up_months: Total follow-up period in months
            **kwargs: Additional parameters
            
        Returns:
            DataFrame in long format with repeated measures
        """
        # Generate baseline data
        baseline_data = self.generate_data(n_patients, **kwargs)
        
        # Create time points
        timepoints = np.linspace(0, follow_up_months, n_timepoints)
        
        # Initialize longitudinal dataset
        longitudinal_data = []
        
        for patient_id in range(n_patients):
            patient_baseline = baseline_data.iloc[patient_id]
            
            for time_idx, time_point in enumerate(timepoints):
                patient_record = patient_baseline.copy()
                patient_record['patient_id'] = patient_id
                patient_record['time_point'] = time_point
                patient_record['visit_number'] = time_idx
                
                # Add time-varying effects
                if time_point > 0:
                    # Functional status may improve or decline over time
                    time_effect = self.np_random.normal(0, 2)
                    age_decline = -0.1 * time_point * (patient_baseline['patient_age'] / 65)
                    care_improvement = 0.1 * time_point * (patient_baseline['care_coordination'] / 100)
                    
                    new_functional = (patient_baseline['functional_status'] + 
                                    time_effect + age_decline + care_improvement)
                    patient_record['functional_status'] = np.clip(new_functional, 0, 100)
                    
                    # Patient satisfaction may change
                    satisfaction_change = self.np_random.normal(0, 0.5)
                    new_satisfaction = patient_baseline['patient_satisfaction'] + satisfaction_change
                    patient_record['patient_satisfaction'] = np.clip(new_satisfaction, 0, 10)
                
                longitudinal_data.append(patient_record)
        
        return pd.DataFrame(longitudinal_data)