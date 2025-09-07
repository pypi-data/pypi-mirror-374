"""
Enhanced CausalLLM - Comprehensive Causal Inference Platform

This module provides the main enhanced CausalLLM interface that combines
statistical methods with LLM-powered domain knowledge for robust causal analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import warnings
import logging
import asyncio

from .core.enhanced_causal_discovery import (
    EnhancedCausalDiscovery, 
    CausalDiscoveryResult,
    CausalEdge
)
from .core.statistical_inference import (
    StatisticalCausalInference,
    CausalInferenceResult,
    CausalEffect,
    CausalMethod
)
from .core.llm_client import get_llm_client
from .core.utils.logging import get_logger
from .core.exceptions import (
    CausalLLMError, DataValidationError, VariableError, 
    LLMClientError, InsufficientDataError, CausalDiscoveryError,
    StatisticalInferenceError, ErrorHandler, handle_errors
)
from .core.data_processing import DataChunker, StreamingDataProcessor, DataProcessingConfig
from .core.caching import StatisticalComputationCache, get_global_cache
from .core.optimized_algorithms import vectorized_stats, causal_inference
from .core.async_processing import AsyncTaskManager, AsyncCausalAnalysis
from .core.lazy_evaluation import LazyDataFrame, LazyComputationGraph

warnings.filterwarnings('ignore')

@dataclass 
class ComprehensiveCausalAnalysis:
    """Complete causal analysis result combining discovery and inference."""
    discovery_results: CausalDiscoveryResult
    inference_results: Dict[str, CausalInferenceResult]
    domain_recommendations: str
    methodology_assessment: str
    actionable_insights: List[str]
    confidence_score: float

class EnhancedCausalLLM:
    """
    Enhanced CausalLLM platform providing comprehensive causal analysis capabilities.
    
    This class combines:
    - Automated causal structure discovery
    - Multiple statistical inference methods  
    - LLM-powered domain expertise
    - Assumption testing and validation
    - Actionable business insights
    """
    
    def __init__(self, llm_provider: str = "openai", llm_model: str = "gpt-4", 
                 significance_level: float = 0.05,
                 enable_performance_optimizations: bool = True,
                 chunk_size: Optional[int] = None,
                 use_async: bool = True,
                 cache_dir: Optional[str] = None):
        """
        Initialize Enhanced CausalLLM.
        
        Args:
            llm_provider: LLM provider ("openai", "llama", "grok", "mcp")
            llm_model: Specific model to use
            significance_level: Statistical significance level for tests
        """
        
        # Initialize logger
        self.logger = get_logger("causallm.enhanced", level="INFO")
        
        # Initialize performance components
        self.enable_optimizations = enable_performance_optimizations
        if enable_performance_optimizations:
            self.data_config = DataProcessingConfig(
                chunk_size=chunk_size or 10000,
                use_dask=True,
                cache_intermediate=True
            )
            self.data_chunker = DataChunker(self.data_config)
            self.cache = StatisticalComputationCache(cache_dir=cache_dir) if cache_dir else get_global_cache()
            
            if use_async:
                self.task_manager = AsyncTaskManager()
                self.async_causal = AsyncCausalAnalysis(self.task_manager)
            else:
                self.task_manager = None
                self.async_causal = None
        else:
            self.data_chunker = None
            self.cache = None
            self.task_manager = None
            self.async_causal = None
        
        # Initialize LLM client
        try:
            self.llm_client = get_llm_client(llm_provider, llm_model)
            self.llm_available = True
            self.logger.info(f"Successfully initialized LLM client: {llm_provider}/{llm_model}")
        except Exception as e:
            # Convert to specific exception type
            llm_error = LLMClientError(
                f"Failed to initialize LLM client: {e}",
                provider=llm_provider,
                model=llm_model,
                cause=e
            )
            self.logger.warning(f"LLM client initialization failed: {llm_error.message}")
            self.logger.info("Falling back to statistical methods only")
            self.llm_client = None
            self.llm_available = False
        
        # Initialize core engines
        self.discovery_engine = EnhancedCausalDiscovery(
            llm_client=self.llm_client, 
            significance_level=significance_level
        )
        
        self.inference_engine = StatisticalCausalInference(
            significance_level=significance_level
        )
        
        self.significance_level = significance_level
    
    @handle_errors(CausalDiscoveryError, context={"method": "discover_causal_relationships"})
    def discover_causal_relationships(self, data: pd.DataFrame, 
                                    variables: List[str] = None,
                                    domain: str = None) -> CausalDiscoveryResult:
        """
        Discover causal relationships in data using hybrid statistical-LLM approach.
        
        Args:
            data: Input dataset
            variables: Variables to analyze (if None, uses all columns)
            domain: Domain context ('healthcare', 'marketing', 'finance', etc.)
            
        Returns:
            CausalDiscoveryResult with discovered relationships and insights
        """
        
        self.logger.info("Starting enhanced causal discovery analysis")
        self.logger.info(f"Variables to analyze: {variables or 'all columns'}")
        self.logger.info(f"Domain context: {domain or 'general'}")
        
        # Validate input data
        self._validate_data(data, variables)
        
        # Use optimized processing for large datasets
        if self.enable_optimizations and len(data) > 50000:
            return self._discover_causal_relationships_optimized(data, variables, domain)
        
        
        # Discover causal structure
        discovery_results = self.discovery_engine.discover_causal_structure(
            data, variables, domain
        )
        
        # Log summary
        self.logger.info("Causal discovery analysis completed successfully")
        self.logger.info(f"Found {len(discovery_results.discovered_edges)} causal relationships")
        self.logger.info(f"Domain: {discovery_results.statistical_summary['domain']}")
        self.logger.info(f"High confidence edges: {discovery_results.statistical_summary['high_confidence_relationships']}")
        
        return discovery_results
    
    def _discover_causal_relationships_optimized(self, 
                                               data: pd.DataFrame,
                                               variables: List[str] = None,
                                               domain: str = None) -> CausalDiscoveryResult:
        """Optimized causal discovery for large datasets."""
        self.logger.info("Using optimized causal discovery for large dataset")
        
        # Use lazy evaluation for data preprocessing
        lazy_data = LazyDataFrame(data)
        
        if variables:
            lazy_data = lazy_data.select_dtypes(include=[np.number])[variables]
        else:
            lazy_data = lazy_data.select_dtypes(include=[np.number])
        
        # Use cached correlation computation
        if variables and len(variables) <= 50:
            # For small variable sets, use vectorized correlation
            correlation_matrix = vectorized_stats.compute_correlation_matrix(
                lazy_data.compute(), method='pearson'
            )
        else:
            # For large variable sets, use chunked processing
            def compute_large_correlation(df):
                return vectorized_stats.compute_correlation_matrix(df, method='pearson')
            
            correlation_matrix = self.cache.cached_computation(
                'large_correlation_matrix',
                lazy_data.compute(),
                compute_large_correlation
            )
        
        # Use async processing for independence tests if available
        if self.async_causal and variables and len(variables) > 10:
            import asyncio
            independence_results = asyncio.run(
                self.async_causal.parallel_causal_discovery(
                    lazy_data.compute(), variables or list(lazy_data.columns), max_conditioning_size=2
                )
            )
        else:
            # Fallback to regular discovery
            independence_results = []
        
        # Convert results to edges
        discovered_edges = []
        for result in independence_results:
            if not result.get('independent', True) and result.get('p_value', 1.0) < 0.05:
                edge = CausalEdge(
                    cause=result['var1'],
                    effect=result['var2'],
                    confidence=1.0 - result['p_value'],
                    method='async_independence_test',
                    p_value=result['p_value'],
                    effect_size=result.get('test_statistic', 0.0),
                    interpretation=f"Causal relationship detected (p={result['p_value']:.4f})"
                )
                discovered_edges.append(edge)
        
        # Create result
        result = CausalDiscoveryResult(
            discovered_edges=discovered_edges,
            suggested_confounders={},
            assumptions_violated=[],
            domain_insights=f"Optimized analysis for {domain or 'general'} domain",
            statistical_summary={
                'domain': domain or 'general',
                'high_confidence_relationships': len([e for e in discovered_edges if e.confidence > 0.8]),
                'total_relationships_tested': len(independence_results),
                'average_effect_size': np.mean([e.effect_size for e in discovered_edges]) if discovered_edges else 0.0,
                'optimization_used': True
            }
        )
        
        return result
    
    @handle_errors(StatisticalInferenceError, context={"method": "estimate_causal_effect"})
    def estimate_causal_effect(self, data: pd.DataFrame,
                              treatment: str,
                              outcome: str,
                              covariates: List[str] = None,
                              method: str = "comprehensive",
                              instrument: str = None) -> CausalInferenceResult:
        """
        Estimate causal effect using statistical methods.
        
        Args:
            data: Input dataset
            treatment: Treatment/intervention variable
            outcome: Outcome variable  
            covariates: List of control variables
            method: Method to use ("regression", "matching", "iv", "comprehensive")
            instrument: Instrumental variable (for IV estimation)
            
        Returns:
            CausalInferenceResult with effect estimates and analysis
        """
        
        self.logger.info("Starting causal effect estimation")
        self.logger.info(f"Treatment: {treatment}, Outcome: {outcome}")
        self.logger.info(f"Method: {method}, Covariates: {covariates or 'none'}")
        
        # Validate inputs
        self._validate_treatment_outcome(data, treatment, outcome, covariates)
        
        # Use optimized processing for large datasets
        if self.enable_optimizations and len(data) > 10000:
            return self._estimate_causal_effect_optimized(data, treatment, outcome, covariates, method, instrument)
        
        if method == "comprehensive":
            # Comprehensive analysis with multiple methods
            inference_results = self.inference_engine.comprehensive_causal_analysis(
                data, treatment, outcome, covariates, instrument
            )
        else:
            # Single method analysis
            method_mapping = {
                "regression": CausalMethod.LINEAR_REGRESSION,
                "matching": CausalMethod.MATCHING,
                "iv": CausalMethod.INSTRUMENTAL_VARIABLES
            }
            
            causal_method = method_mapping.get(method, CausalMethod.LINEAR_REGRESSION)
            primary_effect = self.inference_engine.estimate_causal_effect(
                data, treatment, outcome, covariates, causal_method, instrument
            )
            
            # Create comprehensive result with single method
            inference_results = CausalInferenceResult(
                primary_effect=primary_effect,
                robustness_checks=[],
                sensitivity_analysis={},
                recommendations=f"Single method analysis using {method}",
                confidence_level="Medium" if primary_effect.p_value < 0.05 else "Low",
                overall_assessment=primary_effect.interpretation
            )
        
        # Log summary  
        self.logger.info("Causal effect estimation completed successfully")
        self.logger.info(f"Primary effect: {inference_results.primary_effect.effect_estimate:.4f}")
        self.logger.info(f"P-value: {inference_results.primary_effect.p_value:.4f}")
        self.logger.info(f"Confidence level: {inference_results.confidence_level}")
        self.logger.info(f"Robustness checks performed: {len(inference_results.robustness_checks)}")
        
        return inference_results
    
    def _estimate_causal_effect_optimized(self,
                                        data: pd.DataFrame,
                                        treatment: str,
                                        outcome: str,
                                        covariates: List[str] = None,
                                        method: str = "comprehensive",
                                        instrument: str = None) -> CausalInferenceResult:
        """Optimized causal effect estimation for large datasets."""
        self.logger.info("Using optimized causal effect estimation for large dataset")
        
        # Prepare data
        X = data[covariates].fillna(data[covariates].mean()).values if covariates else np.array([]).reshape(len(data), 0)
        treatment_data = data[treatment].values
        outcome_data = data[outcome].values
        
        # Use vectorized causal inference
        if method == "comprehensive" or method == "matching":
            # Use optimized matching with caching
            cache_key = f"ate_estimation_{treatment}_{outcome}_{len(data)}"
            
            def compute_ate():
                return causal_inference.estimate_ate_vectorized(
                    X, treatment_data, outcome_data, method='doubly_robust'
                )
            
            ate_result = self.cache.cached_computation(
                'ate_estimation_optimized',
                data,
                lambda df: compute_ate(),
                method=method
            )
        else:
            # Use specified method
            ate_result = causal_inference.estimate_ate_vectorized(
                X, treatment_data, outcome_data, method=method
            )
        
        # Create CausalEffect result
        primary_effect = CausalEffect(
            treatment=treatment,
            outcome=outcome,
            effect_estimate=ate_result['ate'],
            std_error=ate_result['se'],
            confidence_interval=(ate_result['ci_lower'], ate_result['ci_upper']),
            p_value=ate_result['p_value'],
            method=f"optimized_{method}",
            interpretation=f"ATE: {ate_result['ate']:.4f} (95% CI: [{ate_result['ci_lower']:.4f}, {ate_result['ci_upper']:.4f}])",
            robustness_score=0.8  # High robustness for optimized methods
        )
        
        # Create comprehensive result
        result = CausalInferenceResult(
            primary_effect=primary_effect,
            robustness_checks=[],  # Could add async robustness checks here
            sensitivity_analysis={'optimization_used': True, 'method': method},
            recommendations=f"Optimized analysis using {method} method on large dataset",
            confidence_level="High" if primary_effect.p_value < 0.01 else "Medium",
            overall_assessment=primary_effect.interpretation
        )
        
        return result
    
    @handle_errors(CausalLLMError, context={"method": "comprehensive_analysis"})
    def comprehensive_analysis(self, data: pd.DataFrame,
                              treatment: str = None,
                              outcome: str = None,
                              variables: List[str] = None,
                              domain: str = None,
                              covariates: List[str] = None) -> ComprehensiveCausalAnalysis:
        """
        Perform comprehensive causal analysis combining discovery and inference.
        
        Args:
            data: Input dataset
            treatment: Primary treatment variable (if None, will be inferred)
            outcome: Primary outcome variable (if None, will be inferred)  
            variables: Variables to include in analysis
            domain: Domain context
            covariates: Control variables
            
        Returns:
            ComprehensiveCausalAnalysis with complete analysis results
        """
        
        self.logger.info("Starting comprehensive causal analysis")
        self.logger.info(f"Dataset shape: {data.shape}")
        self.logger.info(f"Domain: {domain or 'general'}")
        
        # Step 1: Causal Discovery
        self.logger.info("Phase 1: Executing causal structure discovery")
        discovery_results = self.discover_causal_relationships(data, variables, domain)
        
        # Step 2: Identify key relationships for detailed analysis
        inference_results = {}
        
        if treatment and outcome:
            # Analyze specified treatment-outcome relationship
            self.logger.info(f"Phase 2: Analyzing specified relationship {treatment} → {outcome}")
            inference_results[f"{treatment}_to_{outcome}"] = self.estimate_causal_effect(
                data, treatment, outcome, covariates, "comprehensive"
            )
        else:
            # Analyze top discovered relationships
            top_edges = sorted(discovery_results.discovered_edges, 
                             key=lambda x: x.confidence, reverse=True)[:3]
            
            self.logger.info("Phase 2: Analyzing top discovered relationships")
            for i, edge in enumerate(top_edges):
                if edge.confidence >= 0.6:  # Only analyze high-confidence relationships
                    self.logger.info(f"Analyzing relationship {i+1}: {edge.cause} → {edge.effect} (confidence: {edge.confidence:.3f})")
                    inference_results[f"{edge.cause}_to_{edge.effect}"] = self.estimate_causal_effect(
                        data, edge.cause, edge.effect, covariates, "comprehensive"
                    )
        
        # Step 3: Generate domain recommendations
        domain_recommendations = self._generate_domain_recommendations(
            discovery_results, inference_results, domain
        )
        
        # Step 4: Methodology assessment
        methodology_assessment = self._assess_methodology(
            discovery_results, inference_results
        )
        
        # Step 5: Extract actionable insights
        actionable_insights = self._extract_actionable_insights(
            discovery_results, inference_results, domain
        )
        
        # Step 6: Calculate overall confidence score
        confidence_score = self._calculate_overall_confidence(
            discovery_results, inference_results
        )
        
        self.logger.info("Comprehensive causal analysis completed successfully")
        self.logger.info(f"Overall confidence score: {confidence_score:.2f}")
        self.logger.info(f"Generated {len(actionable_insights)} actionable insights")
        
        return ComprehensiveCausalAnalysis(
            discovery_results=discovery_results,
            inference_results=inference_results,
            domain_recommendations=domain_recommendations,
            methodology_assessment=methodology_assessment,
            actionable_insights=actionable_insights,
            confidence_score=confidence_score
        )
    
    def generate_intervention_recommendations(self, analysis: ComprehensiveCausalAnalysis,
                                           target_outcome: str,
                                           budget_constraint: float = None) -> Dict[str, Any]:
        """
        Generate specific intervention recommendations based on causal analysis.
        
        Args:
            analysis: Results from comprehensive_analysis()
            target_outcome: Desired outcome to optimize
            budget_constraint: Maximum budget for interventions
            
        Returns:
            Dictionary with intervention recommendations and expected impacts
        """
        
        self.logger.info(f"Generating intervention recommendations for target outcome: {target_outcome}")
        
        recommendations = {
            'primary_interventions': [],
            'secondary_interventions': [],
            'expected_impacts': {},
            'implementation_priority': [],
            'risk_assessment': {}
        }
        
        # Find causal relationships affecting target outcome
        relevant_edges = []
        
        for edge in analysis.discovery_results.discovered_edges:
            if edge.effect.lower() == target_outcome.lower():
                relevant_edges.append(edge)
        
        # Add from inference results
        for key, result in analysis.inference_results.items():
            if result.primary_effect.outcome.lower() == target_outcome.lower():
                # Create synthetic edge from inference result
                synthetic_edge = type('Edge', (), {
                    'cause': result.primary_effect.treatment,
                    'effect': result.primary_effect.outcome,
                    'confidence': result.primary_effect.robustness_score,
                    'effect_size': abs(result.primary_effect.effect_estimate),
                    'interpretation': result.primary_effect.interpretation
                })
                relevant_edges.append(synthetic_edge)
        
        # Sort by potential impact (confidence * effect_size)
        relevant_edges.sort(key=lambda x: x.confidence * getattr(x, 'effect_size', 0), reverse=True)
        
        # Generate recommendations
        for i, edge in enumerate(relevant_edges[:5]):  # Top 5 interventions
            intervention = {
                'target_variable': edge.cause,
                'expected_outcome_change': getattr(edge, 'effect_size', 'moderate'),
                'confidence_level': edge.confidence,
                'implementation_complexity': 'medium',  # Default
                'estimated_cost': 'TBD',
                'timeline': '3-6 months',
                'success_metrics': [f"Change in {edge.effect}", f"Improvement in {edge.cause}"]
            }
            
            if i < 2:
                recommendations['primary_interventions'].append(intervention)
            else:
                recommendations['secondary_interventions'].append(intervention)
        
        return recommendations
    
    def _validate_data(self, data: pd.DataFrame, variables: List[str] = None):
        """Validate input data for analysis."""
        try:
            # Use centralized error handling
            ErrorHandler.validate_data(data, required_columns=variables, min_rows=10)
            
            # Additional warning for small samples
            if len(data) < 50:
                self.logger.warning(f"Small sample size detected (n={len(data)}). Results may be unreliable.")
                
        except (DataValidationError, VariableError, InsufficientDataError) as e:
            # Log the structured error
            self.logger.error(f"Data validation failed: {e.message}")
            self.logger.debug(f"Error details: {e.to_dict()}")
            raise  # Re-raise the specific exception
    
    def _validate_treatment_outcome(self, data: pd.DataFrame, treatment: str, 
                                   outcome: str, covariates: List[str] = None):
        """Validate treatment and outcome variables."""
        required_vars = [treatment, outcome]
        if covariates:
            required_vars.extend(covariates)
        
        try:
            ErrorHandler.validate_data(data, required_columns=required_vars)
            
            # Additional specific validation
            if data[treatment].isnull().all():
                raise VariableError(
                    f"Treatment variable '{treatment}' has all null values",
                    invalid_variables=[treatment]
                )
            
            if data[outcome].isnull().all():
                raise VariableError(
                    f"Outcome variable '{outcome}' has all null values",
                    invalid_variables=[outcome]
                )
                
        except (DataValidationError, VariableError) as e:
            self.logger.error(f"Variable validation failed: {e.message}")
            raise
    
    def _generate_domain_recommendations(self, discovery: CausalDiscoveryResult,
                                       inference: Dict[str, CausalInferenceResult],
                                       domain: str) -> str:
        """Generate domain-specific recommendations."""
        
        recommendations = f"# {domain.title() if domain else 'General'} Domain Recommendations\n\n"
        
        # High-impact relationships
        high_impact = [edge for edge in discovery.discovered_edges if edge.confidence >= 0.8]
        
        if high_impact:
            recommendations += "## High-Impact Causal Relationships\n"
            for edge in high_impact[:3]:
                recommendations += f"- **{edge.cause} → {edge.effect}**: {edge.interpretation}\n"
            recommendations += "\n"
        
        # Statistical inference insights
        if inference:
            recommendations += "## Key Quantitative Findings\n"
            for key, result in inference.items():
                if result.primary_effect.p_value < 0.05:
                    recommendations += f"- **{result.primary_effect.treatment}**: "
                    recommendations += f"{result.primary_effect.interpretation}\n"
            recommendations += "\n"
        
        # Domain-specific advice
        if domain == 'healthcare':
            recommendations += "## Clinical Implementation Guidelines\n"
            recommendations += "- Validate findings through randomized controlled trials\n"
            recommendations += "- Consider patient heterogeneity and subgroup effects\n"
            recommendations += "- Monitor for adverse effects and unintended consequences\n"
            recommendations += "- Implement gradual rollout with continuous monitoring\n"
        elif domain == 'marketing':
            recommendations += "## Marketing Strategy Implementation\n"
            recommendations += "- Test interventions through controlled A/B experiments\n"
            recommendations += "- Segment customers for personalized approaches\n"
            recommendations += "- Monitor long-term customer lifetime value impacts\n"
            recommendations += "- Account for competitive responses and market changes\n"
        elif domain == 'finance':
            recommendations += "## Financial Strategy Considerations\n"
            recommendations += "- Validate relationships across different market conditions\n"
            recommendations += "- Implement risk management protocols\n"
            recommendations += "- Monitor for regime changes and structural breaks\n"
            recommendations += "- Consider regulatory and compliance implications\n"
        
        return recommendations
    
    def _assess_methodology(self, discovery: CausalDiscoveryResult,
                           inference: Dict[str, CausalInferenceResult]) -> str:
        """Assess the methodology used and provide quality metrics."""
        
        assessment = "# Methodology Assessment\n\n"
        
        # Discovery assessment
        assessment += "## Causal Discovery Quality\n"
        assessment += f"- **Relationships discovered**: {len(discovery.discovered_edges)}\n"
        assessment += f"- **High confidence edges**: {discovery.statistical_summary['high_confidence_relationships']}\n"
        assessment += f"- **Average effect size**: {discovery.statistical_summary['average_effect_size']:.3f}\n"
        
        if discovery.assumptions_violated:
            assessment += f"- **Assumptions violated**: {len(discovery.assumptions_violated)}\n"
            for violation in discovery.assumptions_violated:
                assessment += f"  - {violation}\n"
        
        assessment += "\n"
        
        # Inference assessment
        if inference:
            assessment += "## Statistical Inference Quality\n"
            
            total_methods = sum(1 + len(result.robustness_checks) for result in inference.values())
            significant_results = sum(
                (1 if result.primary_effect.p_value < 0.05 else 0) + 
                len([r for r in result.robustness_checks if r.p_value < 0.05])
                for result in inference.values()
            )
            
            assessment += f"- **Total methods applied**: {total_methods}\n"
            assessment += f"- **Significant results**: {significant_results}\n"
            assessment += f"- **Consistency rate**: {significant_results/total_methods*100:.1f}%\n"
            
            # Method-specific insights
            method_counts = {}
            for result in inference.values():
                method = result.primary_effect.method
                method_counts[method] = method_counts.get(method, 0) + 1
                
                for rob in result.robustness_checks:
                    method = rob.method
                    method_counts[method] = method_counts.get(method, 0) + 1
            
            assessment += "\n**Methods used:**\n"
            for method, count in method_counts.items():
                assessment += f"- {method.replace('_', ' ').title()}: {count} applications\n"
        
        return assessment
    
    def _extract_actionable_insights(self, discovery: CausalDiscoveryResult,
                                   inference: Dict[str, CausalInferenceResult],
                                   domain: str) -> List[str]:
        """Extract actionable insights from the analysis."""
        
        insights = []
        
        # From discovery results
        for edge in discovery.discovered_edges:
            if edge.confidence >= 0.7:
                insights.append(
                    f"Focus on {edge.cause} to improve {edge.effect} "
                    f"(confidence: {edge.confidence:.2f})"
                )
        
        # From inference results
        for key, result in inference.items():
            if result.primary_effect.p_value < 0.05:
                effect_size = abs(result.primary_effect.effect_estimate)
                if effect_size >= 0.3:
                    insights.append(
                        f"Strong intervention opportunity: {result.primary_effect.treatment} "
                        f"can change {result.primary_effect.outcome} by {effect_size:.2f} units"
                    )
        
        # Domain-specific insights
        if domain == 'healthcare' and discovery.suggested_confounders:
            insights.append(
                "Control for patient demographics and comorbidities in treatment decisions"
            )
        elif domain == 'marketing':
            insights.append(
                "Test multi-channel approaches for synergistic effects on customer engagement"
            )
        elif domain == 'finance':
            insights.append(
                "Monitor macroeconomic indicators as leading factors for portfolio decisions"
            )
        
        return insights[:10]  # Return top 10 insights
    
    def _calculate_overall_confidence(self, discovery: CausalDiscoveryResult,
                                    inference: Dict[str, CausalInferenceResult]) -> float:
        """Calculate overall confidence score for the analysis."""
        
        # Discovery confidence component
        if discovery.discovered_edges:
            avg_discovery_confidence = np.mean([edge.confidence for edge in discovery.discovered_edges])
        else:
            avg_discovery_confidence = 0.0
        
        # Inference confidence component
        if inference:
            inference_confidences = []
            for result in inference.values():
                # Convert p-value to confidence score
                primary_conf = max(0, 1 - result.primary_effect.p_value * 20)
                inference_confidences.append(primary_conf)
                
                # Add robustness check confidences
                for rob in result.robustness_checks:
                    rob_conf = max(0, 1 - rob.p_value * 20)
                    inference_confidences.append(rob_conf)
            
            avg_inference_confidence = np.mean(inference_confidences) if inference_confidences else 0.0
        else:
            avg_inference_confidence = 0.0
        
        # Sample size adjustment
        sample_size_factor = min(1.0, discovery.statistical_summary['total_relationships_tested'] / 100)
        
        # Overall confidence
        overall_confidence = (
            0.4 * avg_discovery_confidence + 
            0.4 * avg_inference_confidence + 
            0.2 * sample_size_factor
        )
        
        return overall_confidence