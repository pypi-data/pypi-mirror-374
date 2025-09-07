"""
Base analysis templates for domain-specific causal analysis.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import pandas as pd


@dataclass
class AnalysisSpec:
    """Specification for a domain-specific analysis."""
    name: str
    description: str
    treatment_variable: str
    outcome_variable: str
    required_covariates: List[str]
    optional_covariates: List[str]
    analysis_type: str  # 'treatment_effect', 'attribution', 'prediction', 'optimization'
    domain_constraints: Dict[str, Any]
    expected_effect_direction: Optional[str] = None
    minimum_sample_size: Optional[int] = None


@dataclass
class AnalysisResult:
    """Result from a domain-specific analysis."""
    analysis_name: str
    treatment: str
    outcome: str
    effect_estimate: float
    confidence_interval: Tuple[float, float]
    p_value: float
    sample_size: int
    covariates_used: List[str]
    domain_interpretation: str
    business_impact: Dict[str, Any]
    recommendations: List[str]
    validation_results: Dict[str, Any]


class BaseAnalysisTemplate(ABC):
    """
    Base class for domain-specific analysis templates.
    
    This class provides pre-configured analysis workflows
    that are commonly used in specific domains.
    """
    
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self._analysis_specs = {}
        self._default_parameters = {}
        
    @abstractmethod
    def get_available_analyses(self) -> Dict[str, AnalysisSpec]:
        """Get all available analysis templates for this domain."""
        pass
    
    @abstractmethod
    def run_analysis(
        self,
        analysis_name: str,
        data: pd.DataFrame,
        causal_engine,  # CausalLLM engine
        **kwargs
    ) -> AnalysisResult:
        """Run a specific analysis template."""
        pass
    
    def add_analysis_spec(self, spec: AnalysisSpec) -> None:
        """Add an analysis specification to the template."""
        self._analysis_specs[spec.name] = spec
    
    def get_analysis_spec(self, analysis_name: str) -> Optional[AnalysisSpec]:
        """Get specification for a specific analysis."""
        return self._analysis_specs.get(analysis_name)
    
    def validate_data_for_analysis(
        self,
        analysis_name: str,
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Validate that data is suitable for the specified analysis.
        
        Returns:
            Dict with validation results
        """
        spec = self.get_analysis_spec(analysis_name)
        if spec is None:
            return {'valid': False, 'error': f'Unknown analysis: {analysis_name}'}
        
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'missing_variables': [],
            'sample_size_adequate': True
        }
        
        # Check required variables
        missing_required = []
        for var in [spec.treatment_variable, spec.outcome_variable] + spec.required_covariates:
            if var not in data.columns:
                missing_required.append(var)
        
        if missing_required:
            validation['valid'] = False
            validation['errors'].append(f'Missing required variables: {missing_required}')
            validation['missing_variables'] = missing_required
        
        # Check sample size
        if spec.minimum_sample_size and len(data) < spec.minimum_sample_size:
            validation['warnings'].append(
                f'Sample size ({len(data)}) below recommended minimum ({spec.minimum_sample_size})'
            )
            validation['sample_size_adequate'] = False
        
        # Check for missing values in key variables
        if spec.treatment_variable in data.columns:
            missing_treatment = data[spec.treatment_variable].isnull().sum()
            if missing_treatment > 0:
                validation['warnings'].append(
                    f'Treatment variable has {missing_treatment} missing values'
                )
        
        if spec.outcome_variable in data.columns:
            missing_outcome = data[spec.outcome_variable].isnull().sum()
            if missing_outcome > 0:
                validation['warnings'].append(
                    f'Outcome variable has {missing_outcome} missing values'
                )
        
        # Domain-specific validation
        domain_validation = self._validate_domain_constraints(spec, data)
        validation.update(domain_validation)
        
        return validation
    
    def _validate_domain_constraints(
        self,
        spec: AnalysisSpec,
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """Validate domain-specific constraints."""
        # Base implementation - can be overridden in subclasses
        return {'domain_constraints_met': True}
    
    def prepare_data_for_analysis(
        self,
        analysis_name: str,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """
        Prepare data for analysis (cleaning, transformations, etc.).
        
        Returns:
            Prepared DataFrame
        """
        spec = self.get_analysis_spec(analysis_name)
        if spec is None:
            raise ValueError(f'Unknown analysis: {analysis_name}')
        
        prepared_data = data.copy()
        
        # Remove rows with missing treatment or outcome
        analysis_vars = [spec.treatment_variable, spec.outcome_variable]
        prepared_data = prepared_data.dropna(subset=analysis_vars)
        
        # Apply domain-specific data preparation
        prepared_data = self._apply_domain_transformations(spec, prepared_data, **kwargs)
        
        return prepared_data
    
    def _apply_domain_transformations(
        self,
        spec: AnalysisSpec,
        data: pd.DataFrame,
        **kwargs
    ) -> pd.DataFrame:
        """Apply domain-specific data transformations."""
        # Base implementation - can be overridden in subclasses
        return data
    
    def interpret_results(
        self,
        analysis_name: str,
        causal_results,  # Results from causal analysis
        data: pd.DataFrame,
        **kwargs
    ) -> AnalysisResult:
        """
        Interpret causal analysis results in domain context.
        
        Returns:
            AnalysisResult with domain-specific interpretation
        """
        spec = self.get_analysis_spec(analysis_name)
        if spec is None:
            raise ValueError(f'Unknown analysis: {analysis_name}')
        
        # Extract basic results
        if hasattr(causal_results, 'inference_results') and causal_results.inference_results:
            primary_result = list(causal_results.inference_results.values())[0]
            effect_estimate = primary_result.primary_effect.effect_estimate
            confidence_interval = primary_result.primary_effect.confidence_interval
            p_value = primary_result.primary_effect.p_value
            covariates_used = getattr(primary_result.primary_effect, 'covariates', [])
        else:
            # Fallback for different result structures
            effect_estimate = 0.0
            confidence_interval = (0.0, 0.0)
            p_value = 1.0
            covariates_used = []
        
        # Generate domain interpretation
        domain_interpretation = self._generate_domain_interpretation(
            spec, effect_estimate, confidence_interval, p_value
        )
        
        # Calculate business impact
        business_impact = self._calculate_business_impact(
            spec, effect_estimate, data, **kwargs
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            spec, effect_estimate, p_value, business_impact
        )
        
        # Validation results
        validation_results = self.validate_data_for_analysis(analysis_name, data)
        
        return AnalysisResult(
            analysis_name=analysis_name,
            treatment=spec.treatment_variable,
            outcome=spec.outcome_variable,
            effect_estimate=effect_estimate,
            confidence_interval=confidence_interval,
            p_value=p_value,
            sample_size=len(data),
            covariates_used=covariates_used,
            domain_interpretation=domain_interpretation,
            business_impact=business_impact,
            recommendations=recommendations,
            validation_results=validation_results
        )
    
    @abstractmethod
    def _generate_domain_interpretation(
        self,
        spec: AnalysisSpec,
        effect_estimate: float,
        confidence_interval: Tuple[float, float],
        p_value: float
    ) -> str:
        """Generate domain-specific interpretation of results."""
        pass
    
    @abstractmethod
    def _calculate_business_impact(
        self,
        spec: AnalysisSpec,
        effect_estimate: float,
        data: pd.DataFrame,
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate business/practical impact of the effect."""
        pass
    
    @abstractmethod
    def _generate_recommendations(
        self,
        spec: AnalysisSpec,
        effect_estimate: float,
        p_value: float,
        business_impact: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on results."""
        pass
    
    def get_analysis_summary(self, analysis_name: str) -> str:
        """Get a summary description of an analysis."""
        spec = self.get_analysis_spec(analysis_name)
        if spec is None:
            return f'Unknown analysis: {analysis_name}'
        
        return f"""
        Analysis: {spec.name}
        Description: {spec.description}
        Treatment: {spec.treatment_variable}
        Outcome: {spec.outcome_variable}
        Required covariates: {spec.required_covariates}
        Analysis type: {spec.analysis_type}
        """
    
    def list_analyses(self) -> List[str]:
        """List all available analyses for this domain."""
        return list(self._analysis_specs.keys())
    
    def get_recommended_analysis(
        self,
        data: pd.DataFrame,
        treatment: Optional[str] = None,
        outcome: Optional[str] = None
    ) -> Optional[str]:
        """
        Recommend the most appropriate analysis based on data characteristics.
        
        Returns:
            Name of recommended analysis or None
        """
        # Basic implementation - can be enhanced in subclasses
        available_analyses = self.get_available_analyses()
        
        for analysis_name, spec in available_analyses.items():
            validation = self.validate_data_for_analysis(analysis_name, data)
            if validation['valid']:
                if treatment is None or spec.treatment_variable == treatment:
                    if outcome is None or spec.outcome_variable == outcome:
                        return analysis_name
        
        return None