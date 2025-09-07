"""
Healthcare Domain Package for CausalLLM

This package provides healthcare-specific components for causal analysis:

- Data generators for clinical scenarios
- Medical domain knowledge and expertise
- Analysis templates for treatment effectiveness, outcomes research, and clinical decision support

Key Features:
- Patient outcome analysis
- Treatment effectiveness evaluation
- Clinical trial simulation
- Healthcare cost analysis
- Risk assessment and prediction
"""

from .generators.clinical_data import ClinicalDataGenerator
from .generators.patient_outcomes import PatientOutcomeGenerator
from .knowledge.medical_knowledge import MedicalDomainKnowledge
from .templates.treatment_analysis import TreatmentEffectivenessTemplate
from .templates.outcomes_research import ClinicalOutcomesTemplate

class HealthcareDomain:
    """Main healthcare domain interface."""
    
    def __init__(self):
        self.data_generator = ClinicalDataGenerator()
        self.outcome_generator = PatientOutcomeGenerator()
        self.domain_knowledge = MedicalDomainKnowledge()
        self.treatment_template = TreatmentEffectivenessTemplate()
        self.outcomes_template = ClinicalOutcomesTemplate()
    
    def generate_clinical_trial_data(self, n_patients: int = 1000, **kwargs):
        """Generate synthetic clinical trial data."""
        return self.data_generator.generate_clinical_trial_data(n_patients, **kwargs)
    
    def generate_patient_cohort_data(self, n_patients: int = 1000, **kwargs):
        """Generate synthetic patient cohort data."""
        return self.data_generator.generate_patient_cohort_data(n_patients, **kwargs)
    
    def analyze_treatment_effectiveness(self, data, treatment, outcome, **kwargs):
        """Analyze treatment effectiveness using domain-specific template."""
        return self.treatment_template.run_analysis('treatment_effectiveness', data, **kwargs)
    
    def get_medical_confounders(self, treatment: str, outcome: str, available_vars: list):
        """Get medical confounders for treatment-outcome pair."""
        return self.domain_knowledge.get_likely_confounders(treatment, outcome, available_vars)

__all__ = [
    'HealthcareDomain',
    'ClinicalDataGenerator',
    'PatientOutcomeGenerator', 
    'MedicalDomainKnowledge',
    'TreatmentEffectivenessTemplate',
    'ClinicalOutcomesTemplate'
]