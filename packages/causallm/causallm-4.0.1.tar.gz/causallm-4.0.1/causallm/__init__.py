"""
CausalLLM - Open Source Causal Inference Library

Discover cause-and-effect relationships in your data using Large Language Models 
and statistical validation.

MIT License - Free for commercial and non-commercial use.
For enterprise features, visit: https://causallm.com/enterprise
"""

from .core.causal_llm_core import CausalLLMCore
from .core.dag_parser import DAGParser
from .core.do_operator import DoOperatorSimulator
from .core.counterfactual_engine import CounterfactualEngine
from .core.statistical_methods import PCAlgorithm, ConditionalIndependenceTest
from .core.causal_discovery import DiscoveryMethod
from .core.llm_client import get_llm_client
from .core.utils.logging import setup_package_logging, get_logger
from .core.factory import get_default_factory
from .core.interfaces import CausalEffect

# Create main CausalLLM class
class CausalLLM:
    """Main CausalLLM interface for causal inference."""
    
    def __init__(self, llm_client=None, method="hybrid", enable_logging=True, log_level="INFO", factory=None):
        """Initialize CausalLLM."""
        # Set up logging if enabled
        if enable_logging:
            setup_package_logging(level=log_level, log_to_file=True, json_format=False)
        
        self.logger = get_logger("causallm.main", level=log_level)
        self.factory = factory or get_default_factory()
        
        # Initialize LLM client
        self.llm_client = llm_client or self._create_default_client()
        self.method = method
        
        # Initialize components using factory
        try:
            self.discovery_engine = self.factory.create_discovery_engine(llm_client=self.llm_client)
            self.dag_parser = DAGParser
            self.do_operator = self.factory.create_do_operator()
            self.counterfactual_engine = self.factory.create_counterfactual_engine(llm_client=self.llm_client)
            self.logger.info("CausalLLM initialized successfully with factory")
        except Exception as e:
            self.logger.error(f"Failed to initialize CausalLLM components: {e}")
            # Fallback to direct instantiation
            self.discovery_engine = self._create_discovery_engine()
            self.dag_parser = DAGParser
            self.do_operator = self._create_do_operator()
            self.counterfactual_engine = CounterfactualEngine(self.llm_client)
            self.logger.warning("Fell back to direct component instantiation")
    
    def _create_default_client(self):
        """Create default LLM client."""
        try:
            return self.factory.create_llm_client("openai", "gpt-4")
        except Exception as e:
            self.logger.warning(f"Failed to create default LLM client: {e}")
            return None
    
    def _create_discovery_engine(self):
        """Create discovery engine (fallback method)."""
        try:
            from .core.causal_discovery import PCAlgorithmEngine
            return PCAlgorithmEngine(significance_level=0.05)
        except Exception as e:
            self.logger.error(f"Failed to create discovery engine: {e}")
            return None
    
    def _create_do_operator(self):
        """Create do-operator (fallback method)."""
        try:
            return DoOperatorSimulator()
        except Exception as e:
            self.logger.error(f"Failed to create do-operator: {e}")
            return None
    
    async def discover_causal_relationships(self, data, variables, domain_context="", **kwargs):
        """Discover causal relationships."""
        # Convert variables list to dict format expected by discovery engine
        if isinstance(variables, list):
            variables_dict = {var: "continuous" for var in variables}
        else:
            variables_dict = variables
            
        return await self.discovery_engine.discover_structure(data, variables_dict, domain_context, **kwargs)
    
    async def estimate_causal_effect(self, data, treatment, outcome, **kwargs):
        """Estimate causal effect."""
        return await self.do_operator.estimate_effect(data, treatment, outcome, **kwargs)
    
    async def generate_counterfactuals(self, data, intervention, **kwargs):
        """Generate counterfactual scenarios."""
        return await self.counterfactual_engine.generate_counterfactuals(data, intervention, **kwargs)
    
    def parse_causal_graph(self, graph_data):
        """Parse causal graph."""
        return graph_data  # Simplified implementation
    
    def get_enterprise_info(self):
        """Get enterprise information."""
        return {
            "licensed": False,
            "features": {},
            "info": "Enterprise features available at https://causallm.com/enterprise",
            "benefits": [
                "Advanced security and authentication",
                "Auto-scaling and load balancing", 
                "Advanced monitoring and observability",
                "ML model lifecycle management",
                "Compliance and audit logging",
                "Cloud platform integrations",
                "Priority support and SLA"
            ]
        }

# Import version info from centralized source
from ._version import __version__, get_version_info, get_version_string

# Additional metadata
__license__ = "MIT"
__author__ = "CausalLLM Team"
__email__ = "opensource@causallm.com"

# Import enhanced components
try:
    from .enhanced_causallm import EnhancedCausalLLM
    from .core.enhanced_causal_discovery import EnhancedCausalDiscovery
    from .core.statistical_inference import StatisticalCausalInference
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Import domain packages
try:
    from . import domains
    from .domains import HealthcareDomain, InsuranceDomain, MarketingDomain, EducationDomain, ExperimentationDomain
    DOMAINS_AVAILABLE = True
except ImportError:
    DOMAINS_AVAILABLE = False

# Main exports
__all__ = [
    'CausalLLM',
    'CausalLLMCore',
    'DAGParser', 
    'DoOperatorSimulator',
    'CounterfactualEngine',
    'DiscoveryMethod',
    'PCAlgorithm',
    'ConditionalIndependenceTest',
    'get_llm_client'
]

# Add enhanced components if available
if ENHANCED_AVAILABLE:
    __all__.extend([
        'EnhancedCausalLLM',
        'EnhancedCausalDiscovery', 
        'StatisticalCausalInference'
    ])

# Add domain packages if available
if DOMAINS_AVAILABLE:
    __all__.extend([
        'domains',
        'HealthcareDomain',
        'InsuranceDomain', 
        'MarketingDomain',
        'EducationDomain',
        'ExperimentationDomain'
    ])