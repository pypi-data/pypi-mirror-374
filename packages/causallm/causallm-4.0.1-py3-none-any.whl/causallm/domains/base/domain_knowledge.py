"""
Base domain knowledge system for causal analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import pandas as pd


@dataclass
class DomainRule:
    """A domain-specific rule or constraint."""
    name: str
    description: str
    rule_type: str  # 'causal', 'constraint', 'measurement', 'validity'
    variables: List[str]
    condition: str
    strength: float  # 0-1 confidence in the rule
    source: str  # 'literature', 'expert', 'empirical', 'theoretical'


@dataclass
class CausalPrior:
    """Prior knowledge about causal relationships."""
    cause: str
    effect: str
    relationship_type: str  # 'positive', 'negative', 'nonlinear', 'threshold'
    strength: float  # 0-1 confidence
    context: str
    evidence_level: str  # 'strong', 'moderate', 'weak', 'speculative'
    conditions: Optional[List[str]] = None


@dataclass
class ConfounderSet:
    """Known confounders for a treatment-outcome relationship."""
    treatment: str
    outcome: str
    confounders: List[str]
    essential_confounders: List[str]  # Must be controlled for
    optional_confounders: List[str]   # Nice to control for
    proxy_variables: Dict[str, List[str]]  # Proxies for unmeasured confounders


class BaseDomainKnowledge(ABC):
    """
    Base class for domain-specific knowledge systems.
    
    This class provides framework for encoding domain expertise
    that can guide causal analysis.
    """
    
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self._causal_priors = {}
        self._domain_rules = {}
        self._confounder_sets = {}
        self._variable_constraints = {}
        
    @abstractmethod
    def load_domain_knowledge(self) -> None:
        """Load domain-specific knowledge base."""
        pass
    
    @abstractmethod
    def get_likely_confounders(
        self, 
        treatment: str, 
        outcome: str,
        available_variables: List[str]
    ) -> List[str]:
        """Get likely confounders for a treatment-outcome pair."""
        pass
    
    @abstractmethod
    def get_causal_priors(self, variables: List[str]) -> List[CausalPrior]:
        """Get causal priors for a set of variables."""
        pass
    
    def add_causal_prior(
        self,
        cause: str,
        effect: str, 
        relationship_type: str,
        strength: float,
        evidence_level: str,
        context: str = "",
        conditions: Optional[List[str]] = None
    ) -> None:
        """Add a causal prior to the knowledge base."""
        prior = CausalPrior(
            cause=cause,
            effect=effect,
            relationship_type=relationship_type,
            strength=strength,
            context=context,
            evidence_level=evidence_level,
            conditions=conditions
        )
        
        key = f"{cause}->{effect}"
        self._causal_priors[key] = prior
    
    def add_domain_rule(
        self,
        name: str,
        description: str,
        rule_type: str,
        variables: List[str],
        condition: str,
        strength: float,
        source: str
    ) -> None:
        """Add a domain rule to the knowledge base."""
        rule = DomainRule(
            name=name,
            description=description,
            rule_type=rule_type,
            variables=variables,
            condition=condition,
            strength=strength,
            source=source
        )
        
        self._domain_rules[name] = rule
    
    def add_confounder_set(
        self,
        treatment: str,
        outcome: str,
        confounders: List[str],
        essential: Optional[List[str]] = None,
        optional: Optional[List[str]] = None,
        proxies: Optional[Dict[str, List[str]]] = None
    ) -> None:
        """Add known confounders for a treatment-outcome pair."""
        confounder_set = ConfounderSet(
            treatment=treatment,
            outcome=outcome,
            confounders=confounders,
            essential_confounders=essential or [],
            optional_confounders=optional or [],
            proxy_variables=proxies or {}
        )
        
        key = f"{treatment}->{outcome}"
        self._confounder_sets[key] = confounder_set
    
    def validate_analysis_assumptions(
        self,
        treatment: str,
        outcome: str,
        covariates: List[str],
        data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Validate assumptions for causal analysis based on domain knowledge.
        
        Returns:
            Dict with validation results and recommendations
        """
        validation_results = {
            'assumptions_met': [],
            'assumptions_violated': [],
            'missing_confounders': [],
            'recommendations': [],
            'confidence_score': 1.0
        }
        
        # Check for essential confounders
        key = f"{treatment}->{outcome}"
        if key in self._confounder_sets:
            confounder_set = self._confounder_sets[key]
            
            missing_essential = [
                conf for conf in confounder_set.essential_confounders
                if conf not in covariates
            ]
            
            if missing_essential:
                validation_results['assumptions_violated'].append(
                    f"Missing essential confounders: {missing_essential}"
                )
                validation_results['missing_confounders'].extend(missing_essential)
                validation_results['confidence_score'] *= 0.5
                
            missing_optional = [
                conf for conf in confounder_set.optional_confounders
                if conf not in covariates
            ]
            
            if missing_optional:
                validation_results['recommendations'].append(
                    f"Consider adding optional confounders: {missing_optional}"
                )
                validation_results['confidence_score'] *= 0.8
        
        # Check domain rules
        for rule_name, rule in self._domain_rules.items():
            if treatment in rule.variables and outcome in rule.variables:
                # Rule applies to this analysis
                if rule.rule_type == 'constraint':
                    if data is not None:
                        # Check if constraint is satisfied in data
                        try:
                            constraint_satisfied = eval(rule.condition, {}, {
                                'data': data,
                                'treatment': data.get(treatment),
                                'outcome': data.get(outcome),
                                **{var: data.get(var) for var in rule.variables if var in data.columns}
                            })
                            
                            if constraint_satisfied:
                                validation_results['assumptions_met'].append(
                                    f"Domain constraint satisfied: {rule.description}"
                                )
                            else:
                                validation_results['assumptions_violated'].append(
                                    f"Domain constraint violated: {rule.description}"
                                )
                                validation_results['confidence_score'] *= (1 - rule.strength * 0.3)
                        except:
                            # If constraint can't be evaluated, add as recommendation
                            validation_results['recommendations'].append(
                                f"Check domain constraint: {rule.description}"
                            )
        
        return validation_results
    
    def get_variable_interpretation(self, variable_name: str) -> Optional[str]:
        """Get domain-specific interpretation for a variable."""
        # Check if there are any rules or priors involving this variable
        interpretations = []
        
        for prior in self._causal_priors.values():
            if variable_name in [prior.cause, prior.effect]:
                interpretations.append(f"{prior.context}: {prior.relationship_type} relationship")
        
        for rule in self._domain_rules.values():
            if variable_name in rule.variables:
                interpretations.append(f"{rule.description}")
        
        return "; ".join(interpretations) if interpretations else None
    
    def suggest_additional_variables(
        self,
        treatment: str,
        outcome: str,
        current_variables: List[str]
    ) -> List[str]:
        """Suggest additional variables that might be important."""
        suggestions = []
        
        # Check confounder sets
        key = f"{treatment}->{outcome}"
        if key in self._confounder_sets:
            confounder_set = self._confounder_sets[key]
            
            missing_confounders = [
                conf for conf in confounder_set.confounders
                if conf not in current_variables
            ]
            suggestions.extend(missing_confounders)
            
            # Check for proxy variables
            for unmeasured, proxies in confounder_set.proxy_variables.items():
                if unmeasured not in current_variables:
                    available_proxies = [p for p in proxies if p not in current_variables]
                    if available_proxies:
                        suggestions.extend(available_proxies[:2])  # Suggest up to 2 proxies
        
        # Check causal priors for relevant variables
        for prior in self._causal_priors.values():
            if prior.cause == treatment or prior.effect == outcome:
                other_var = prior.effect if prior.cause == treatment else prior.cause
                if other_var not in current_variables and other_var not in [treatment, outcome]:
                    suggestions.append(other_var)
        
        return list(set(suggestions))  # Remove duplicates
    
    def get_analysis_recommendations(
        self,
        treatment: str,
        outcome: str,
        available_variables: List[str]
    ) -> Dict[str, Any]:
        """Get comprehensive recommendations for causal analysis."""
        recommendations = {
            'suggested_confounders': self.get_likely_confounders(treatment, outcome, available_variables),
            'additional_variables': self.suggest_additional_variables(treatment, outcome, available_variables),
            'causal_priors': self.get_causal_priors([treatment, outcome]),
            'analysis_notes': [],
            'methodological_suggestions': []
        }
        
        # Add domain-specific methodological suggestions
        key = f"{treatment}->{outcome}"
        if key in self._confounder_sets:
            confounder_set = self._confounder_sets[key]
            if confounder_set.essential_confounders:
                recommendations['analysis_notes'].append(
                    "Essential confounders must be included for valid inference"
                )
            
            if confounder_set.proxy_variables:
                recommendations['methodological_suggestions'].append(
                    "Consider instrumental variable methods if proxies available"
                )
        
        return recommendations