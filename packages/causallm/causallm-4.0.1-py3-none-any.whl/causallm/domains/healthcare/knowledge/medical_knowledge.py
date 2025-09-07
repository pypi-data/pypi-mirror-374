"""
Medical domain knowledge for healthcare causal analysis.
"""

from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

from ...base.domain_knowledge import BaseDomainKnowledge, CausalPrior, DomainRule, ConfounderSet


class MedicalDomainKnowledge(BaseDomainKnowledge):
    """
    Medical domain knowledge system for healthcare causal analysis.
    
    This class encodes medical expertise about causal relationships,
    confounders, and clinical reasoning that can guide causal analysis.
    """
    
    def __init__(self):
        super().__init__("healthcare")
        self.load_domain_knowledge()
    
    def load_domain_knowledge(self) -> None:
        """Load medical domain knowledge."""
        
        # Add fundamental medical causal priors
        self._load_demographic_priors()
        self._load_comorbidity_priors()
        self._load_treatment_priors()
        self._load_outcome_priors()
        
        # Add medical domain rules
        self._load_medical_rules()
        
        # Add confounder sets for common analyses
        self._load_confounder_sets()
    
    def _load_demographic_priors(self):
        """Load demographic causal priors."""
        
        # Age effects
        self.add_causal_prior(
            cause="age", effect="comorbidity_count",
            relationship_type="positive", strength=0.9, evidence_level="strong",
            context="Age is strongly associated with increased comorbidity burden"
        )
        
        self.add_causal_prior(
            cause="age", effect="mortality_risk", 
            relationship_type="positive", strength=0.85, evidence_level="strong",
            context="Advanced age increases mortality risk across conditions"
        )
        
        self.add_causal_prior(
            cause="age", effect="recovery_time",
            relationship_type="positive", strength=0.7, evidence_level="strong", 
            context="Older patients typically have longer recovery times"
        )
        
        # Gender effects
        self.add_causal_prior(
            cause="gender", effect="cardiovascular_disease",
            relationship_type="nonlinear", strength=0.6, evidence_level="strong",
            context="Gender affects cardiovascular disease risk differently by age"
        )
    
    def _load_comorbidity_priors(self):
        """Load comorbidity causal relationships."""
        
        # Diabetes effects
        self.add_causal_prior(
            cause="diabetes", effect="cardiovascular_disease",
            relationship_type="positive", strength=0.8, evidence_level="strong",
            context="Diabetes significantly increases cardiovascular disease risk"
        )
        
        self.add_causal_prior(
            cause="diabetes", effect="wound_healing",
            relationship_type="negative", strength=0.75, evidence_level="strong",
            context="Diabetes impairs wound healing and tissue repair"
        )
        
        # Hypertension effects  
        self.add_causal_prior(
            cause="hypertension", effect="stroke_risk",
            relationship_type="positive", strength=0.85, evidence_level="strong",
            context="Hypertension is a major modifiable risk factor for stroke"
        )
        
        # Obesity effects
        self.add_causal_prior(
            cause="obesity", effect="diabetes",
            relationship_type="positive", strength=0.7, evidence_level="strong",
            context="Obesity is a major risk factor for type 2 diabetes"
        )
    
    def _load_treatment_priors(self):
        """Load treatment effect priors."""
        
        # General treatment principles
        self.add_causal_prior(
            cause="early_intervention", effect="treatment_outcome",
            relationship_type="positive", strength=0.8, evidence_level="strong",
            context="Earlier intervention generally leads to better outcomes"
        )
        
        self.add_causal_prior(
            cause="treatment_intensity", effect="side_effects",
            relationship_type="positive", strength=0.7, evidence_level="strong",
            context="More intensive treatments typically have more side effects"
        )
        
        # Medication adherence
        self.add_causal_prior(
            cause="medication_adherence", effect="treatment_effectiveness",
            relationship_type="positive", strength=0.9, evidence_level="strong",
            context="Better medication adherence improves treatment outcomes"
        )
    
    def _load_outcome_priors(self):
        """Load outcome-related priors."""
        
        # Quality of care effects
        self.add_causal_prior(
            cause="care_coordination", effect="patient_satisfaction",
            relationship_type="positive", strength=0.75, evidence_level="strong",
            context="Better care coordination improves patient satisfaction"
        )
        
        self.add_causal_prior(
            cause="care_coordination", effect="readmission_rate",
            relationship_type="negative", strength=0.7, evidence_level="strong",
            context="Better care coordination reduces readmission rates"
        )
        
        # Length of stay effects
        self.add_causal_prior(
            cause="length_of_stay", effect="hospital_acquired_infection",
            relationship_type="positive", strength=0.6, evidence_level="moderate",
            context="Longer hospital stays increase infection risk"
        )
    
    def _load_medical_rules(self):
        """Load medical domain rules and constraints."""
        
        # Age constraints
        self.add_domain_rule(
            name="adult_age_range",
            description="Adult patients should be 18-120 years old",
            rule_type="constraint",
            variables=["age", "patient_age"],
            condition="18 <= age <= 120",
            strength=1.0,
            source="medical_practice"
        )
        
        # Comorbidity rules
        self.add_domain_rule(
            name="comorbidity_age_relationship", 
            description="Comorbidity count should increase with age",
            rule_type="causal",
            variables=["age", "comorbidity_count"],
            condition="correlation(age, comorbidity_count) > 0",
            strength=0.8,
            source="clinical_literature"
        )
        
        # Treatment response rules
        self.add_domain_rule(
            name="treatment_response_variability",
            description="Treatment response varies by patient characteristics",
            rule_type="validity",
            variables=["treatment", "outcome", "age", "comorbidity_count"],
            condition="treatment_effect_varies_by_subgroup",
            strength=0.7,
            source="clinical_evidence"
        )
        
        # Mortality rules
        self.add_domain_rule(
            name="mortality_risk_bounds",
            description="30-day mortality risk should be 0-50% for most conditions",
            rule_type="constraint", 
            variables=["mortality_risk", "30d_mortality"],
            condition="0 <= mortality_risk <= 0.5",
            strength=0.9,
            source="clinical_epidemiology"
        )
    
    def _load_confounder_sets(self):
        """Load known confounder sets for common healthcare analyses."""
        
        # Treatment effectiveness analysis
        self.add_confounder_set(
            treatment="treatment",
            outcome="recovery_time",
            confounders=["age", "gender", "comorbidity_count", "disease_severity", "hospital_type"],
            essential=["age", "disease_severity"],
            optional=["gender", "hospital_type"],
            proxies={"socioeconomic_status": ["insurance_type", "hospital_type"]}
        )
        
        self.add_confounder_set(
            treatment="treatment",
            outcome="mortality",
            confounders=["age", "gender", "charlson_score", "admission_severity", "care_quality"],
            essential=["age", "charlson_score", "admission_severity"],
            optional=["gender", "care_quality"],
            proxies={"frailty": ["functional_status", "comorbidity_count"]}
        )
        
        # Quality improvement analysis
        self.add_confounder_set(
            treatment="care_coordination",
            outcome="patient_satisfaction", 
            confounders=["age", "insurance_type", "length_of_stay", "disease_severity"],
            essential=["disease_severity"],
            optional=["age", "insurance_type"],
            proxies={"expectations": ["insurance_type", "hospital_type"]}
        )
        
        # Cost analysis
        self.add_confounder_set(
            treatment="treatment_intensity",
            outcome="total_cost",
            confounders=["age", "comorbidity_count", "insurance_type", "hospital_type", "disease_severity"],
            essential=["comorbidity_count", "disease_severity"],
            optional=["age", "hospital_type"],
            proxies={"case_complexity": ["comorbidity_count", "length_of_stay"]}
        )
    
    def get_likely_confounders(
        self, 
        treatment: str, 
        outcome: str,
        available_variables: List[str]
    ) -> List[str]:
        """Get likely confounders for a treatment-outcome pair."""
        
        # Check if we have a specific confounder set
        key = f"{treatment}->{outcome}"
        if key in self._confounder_sets:
            confounder_set = self._confounder_sets[key]
            return [c for c in confounder_set.confounders if c in available_variables]
        
        # Use general medical knowledge
        likely_confounders = []
        
        # Age is almost always a confounder in medical studies
        age_vars = [v for v in available_variables if 'age' in v.lower()]
        likely_confounders.extend(age_vars)
        
        # Comorbidity/severity measures
        comorbidity_vars = [v for v in available_variables 
                           if any(term in v.lower() for term in 
                                ['comorbid', 'charlson', 'severity', 'score'])]
        likely_confounders.extend(comorbidity_vars)
        
        # Gender/demographic factors
        demo_vars = [v for v in available_variables
                    if any(term in v.lower() for term in 
                          ['gender', 'sex', 'race', 'ethnicity'])]
        likely_confounders.extend(demo_vars)
        
        # Insurance/socioeconomic factors
        ses_vars = [v for v in available_variables
                   if any(term in v.lower() for term in
                         ['insurance', 'income', 'education', 'social'])]
        likely_confounders.extend(ses_vars)
        
        # Hospital/provider factors
        provider_vars = [v for v in available_variables
                        if any(term in v.lower() for term in
                              ['hospital', 'provider', 'facility', 'site'])]
        likely_confounders.extend(provider_vars)
        
        return list(set(likely_confounders))  # Remove duplicates
    
    def get_causal_priors(self, variables: List[str]) -> List[CausalPrior]:
        """Get causal priors relevant to a set of variables."""
        relevant_priors = []
        
        for prior in self._causal_priors.values():
            if prior.cause in variables or prior.effect in variables:
                relevant_priors.append(prior)
        
        return relevant_priors
    
    def get_medical_interpretation(
        self,
        treatment: str,
        outcome: str, 
        effect_size: float,
        confidence_interval: Tuple[float, float],
        p_value: float
    ) -> str:
        """Generate medical interpretation of causal analysis results."""
        
        interpretation_parts = []
        
        # Statistical significance
        if p_value < 0.001:
            sig_level = "highly statistically significant"
        elif p_value < 0.01:
            sig_level = "statistically significant"
        elif p_value < 0.05:
            sig_level = "statistically significant"
        else:
            sig_level = "not statistically significant"
        
        interpretation_parts.append(
            f"The treatment effect is {sig_level} (p = {p_value:.4f})"
        )
        
        # Clinical significance assessment
        clinical_significance = self._assess_clinical_significance(
            treatment, outcome, effect_size
        )
        interpretation_parts.append(clinical_significance)
        
        # Effect direction and magnitude
        direction = "increases" if effect_size > 0 else "decreases"
        interpretation_parts.append(
            f"The treatment {direction} the outcome by {abs(effect_size):.2f} units"
        )
        
        # Confidence interval interpretation
        ci_lower, ci_upper = confidence_interval
        interpretation_parts.append(
            f"95% confidence interval: [{ci_lower:.2f}, {ci_upper:.2f}]"
        )
        
        return ". ".join(interpretation_parts)
    
    def _assess_clinical_significance(
        self,
        treatment: str,
        outcome: str,
        effect_size: float
    ) -> str:
        """Assess clinical significance of effect size."""
        
        # Domain-specific thresholds (these would be more sophisticated in practice)
        abs_effect = abs(effect_size)
        
        if 'mortality' in outcome.lower():
            if abs_effect > 0.1:
                return "This represents a clinically very significant effect on mortality"
            elif abs_effect > 0.05:
                return "This represents a clinically significant effect on mortality" 
            else:
                return "The mortality effect may have limited clinical significance"
        
        elif 'recovery' in outcome.lower() or 'time' in outcome.lower():
            if abs_effect > 5:
                return "This represents a clinically significant change in recovery time"
            elif abs_effect > 2:
                return "This represents a moderate clinical effect on recovery time"
            else:
                return "The effect on recovery time may have limited clinical impact"
        
        elif 'satisfaction' in outcome.lower():
            if abs_effect > 1.0:
                return "This represents a clinically meaningful improvement in patient satisfaction"
            elif abs_effect > 0.5:
                return "This represents a moderate improvement in patient satisfaction"
            else:
                return "The satisfaction improvement may have limited practical significance"
        
        else:
            # Generic assessment
            if abs_effect > 1.0:
                return "This appears to be a clinically significant effect"
            elif abs_effect > 0.5:
                return "This represents a moderate clinical effect"
            else:
                return "The clinical significance of this effect is uncertain"
    
    def suggest_additional_analyses(
        self,
        treatment: str,
        outcome: str,
        data: pd.DataFrame
    ) -> List[str]:
        """Suggest additional analyses based on medical knowledge."""
        
        suggestions = []
        
        # Subgroup analyses
        if 'age' in data.columns:
            suggestions.append("Consider age-stratified analysis (e.g., <65 vs ≥65 years)")
        
        if 'gender' in data.columns:
            suggestions.append("Examine potential gender differences in treatment response")
        
        # Dose-response analysis
        if treatment.lower() in ['dosage', 'intensity', 'duration']:
            suggestions.append("Examine dose-response relationship")
        
        # Time-to-event analysis
        if 'time' in outcome.lower():
            suggestions.append("Consider survival analysis or time-to-event methods")
        
        # Mediator analysis
        potential_mediators = [col for col in data.columns
                              if any(term in col.lower() for term in
                                    ['adherence', 'compliance', 'coordination'])]
        if potential_mediators:
            suggestions.append(f"Consider mediation analysis with: {potential_mediators}")
        
        return suggestions