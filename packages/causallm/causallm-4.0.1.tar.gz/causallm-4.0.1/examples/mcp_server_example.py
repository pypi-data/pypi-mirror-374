#!/usr/bin/env python3
"""
CausalLLM MCP Server Example

This example demonstrates how to set up and use CausalLLM as an MCP (Model Context Protocol) server.
The MCP server exposes CausalLLM's causal reasoning capabilities as standardized tools that can be
used by MCP-compatible clients like Claude Desktop, VS Code, or other applications.

MCP Tools Provided:
- simulate_counterfactual: Generate counterfactual scenarios
- generate_do_prompt: Create do-calculus intervention prompts
- extract_causal_edges: Extract causal relationships from text
- generate_reasoning_prompt: Create reasoning tasks from causal graphs
- analyze_treatment_effect: Analyze treatment effectiveness

Run as MCP server:
    python examples/mcp_server_example.py --server

Test MCP tools directly:
    python examples/mcp_server_example.py --test
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add causallm to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_mcp_config() -> Dict[str, Any]:
    """Create MCP server configuration."""
    return {
        "server": {
            "name": "causallm-server",
            "version": "1.0.0", 
            "description": "CausalLLM MCP Server for causal reasoning and analysis",
            "transport": "stdio",
            "host": "localhost",
            "port": 8000,
            "max_connections": 10,
            "timeout": 30,
            "log_level": "INFO"
        },
        "tools": {
            "enabled_tools": [
                "simulate_counterfactual",
                "generate_do_prompt",
                "extract_causal_edges", 
                "generate_reasoning_prompt",
                "analyze_treatment_effect"
            ],
            "tool_timeout": 60,
            "max_prompt_length": 10000,
            "enable_streaming": False
        }
    }


def create_sample_mcp_tools():
    """Create sample MCP tools for demonstration."""
    
    class MockCausalTools:
        """Mock implementation of CausalTools for demonstration."""
        
        def __init__(self):
            self.tools = {
                "simulate_counterfactual": {
                    "name": "simulate_counterfactual",
                    "description": "Simulate counterfactual scenarios by comparing factual and hypothetical situations",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "context": {"type": "string", "description": "Background context"},
                            "factual": {"type": "string", "description": "What actually happened"},
                            "intervention": {"type": "string", "description": "Hypothetical intervention"}
                        },
                        "required": ["context", "factual", "intervention"]
                    }
                },
                "generate_do_prompt": {
                    "name": "generate_do_prompt", 
                    "description": "Generate do-calculus intervention prompts for causal analysis",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "context": {"type": "string", "description": "System context"},
                            "variables": {"type": "object", "description": "Variable descriptions"},
                            "intervention": {"type": "object", "description": "Intervention to analyze"}
                        },
                        "required": ["context", "variables", "intervention"]
                    }
                },
                "extract_causal_edges": {
                    "name": "extract_causal_edges",
                    "description": "Extract causal relationships from natural language descriptions",
                    "input_schema": {
                        "type": "object", 
                        "properties": {
                            "scenario_description": {"type": "string", "description": "Scenario with causal relationships"}
                        },
                        "required": ["scenario_description"]
                    }
                }
            }
        
        async def handle_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
            """Handle tool execution."""
            if tool_name == "simulate_counterfactual":
                return await self._simulate_counterfactual(args)
            elif tool_name == "generate_do_prompt":
                return await self._generate_do_prompt(args)
            elif tool_name == "extract_causal_edges":
                return await self._extract_causal_edges(args)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        async def _simulate_counterfactual(self, args: Dict[str, Any]) -> Dict[str, Any]:
            """Simulate counterfactual scenario."""
            context = args.get("context", "")
            factual = args.get("factual", "")
            intervention = args.get("intervention", "")
            
            # Mock analysis
            analysis = f"""
COUNTERFACTUAL ANALYSIS

Context: {context}

Factual Scenario:
{factual}

Hypothetical Intervention:
{intervention}

Analysis:
If we had implemented the intervention '{intervention}' instead of the factual scenario, 
we would expect different outcomes based on the causal mechanisms in this context.

Key Differences:
1. Direct effects of the intervention would manifest
2. Indirect effects through causal pathways would follow
3. Overall system dynamics would shift accordingly

Confidence: This is a mock analysis for demonstration purposes.
"""
            
            return {
                "analysis": analysis,
                "counterfactual_outcome": "Modified outcome based on intervention",
                "confidence": 0.75
            }
        
        async def _generate_do_prompt(self, args: Dict[str, Any]) -> Dict[str, Any]:
            """Generate do-calculus prompt."""
            context = args.get("context", "")
            variables = args.get("variables", {})
            intervention = args.get("intervention", {})
            
            prompt = f"""
DO-CALCULUS ANALYSIS PROMPT

Context: {context}

Variables: {json.dumps(variables, indent=2)}

Intervention: do({json.dumps(intervention)})

Analysis Task:
Calculate the causal effect of the intervention by:
1. Identifying the target variables affected by the intervention
2. Determining which variables need to be controlled for
3. Estimating the magnitude and direction of causal effects
4. Assessing confidence in the causal estimates

This prompt can be used with causal inference methods to estimate intervention effects.
"""
            
            return {
                "do_prompt": prompt,
                "intervention_variables": list(intervention.keys()),
                "target_variables": list(variables.keys())
            }
        
        async def _extract_causal_edges(self, args: Dict[str, Any]) -> Dict[str, Any]:
            """Extract causal relationships from text."""
            scenario = args.get("scenario_description", "")
            
            # Mock extraction - in reality this would use NLP/LLM
            edges = [
                ["age", "health_outcome"],
                ["treatment", "recovery_time"], 
                ["socioeconomic_status", "treatment_access"],
                ["treatment_access", "health_outcome"]
            ]
            
            return {
                "causal_edges": edges,
                "extracted_variables": ["age", "health_outcome", "treatment", "recovery_time", 
                                       "socioeconomic_status", "treatment_access"],
                "confidence_scores": [0.9, 0.85, 0.8, 0.75],
                "scenario_analyzed": scenario[:100] + "..." if len(scenario) > 100 else scenario
            }
    
    return MockCausalTools()


async def test_mcp_tools():
    """Test MCP tools functionality."""
    print("🧪 Testing CausalLLM MCP Tools")
    print("=" * 50)
    
    tools = create_sample_mcp_tools()
    
    # Test 1: Counterfactual simulation
    print("\n1. Testing Counterfactual Simulation")
    print("-" * 35)
    
    counterfactual_args = {
        "context": "A clinical trial testing a new drug for diabetes patients",
        "factual": "Patients received standard insulin therapy",
        "intervention": "Patients received the new experimental drug instead"
    }
    
    result = await tools.handle_tool("simulate_counterfactual", counterfactual_args)
    print("Result:", result["analysis"][:200] + "..." if len(result["analysis"]) > 200 else result["analysis"])
    
    # Test 2: Do-calculus prompt generation
    print("\n2. Testing Do-Calculus Prompt Generation")
    print("-" * 40)
    
    do_prompt_args = {
        "context": "Healthcare system analyzing treatment effectiveness",
        "variables": {
            "age": "Patient age in years",
            "treatment": "Type of treatment received", 
            "outcome": "Recovery time in days"
        },
        "intervention": {"treatment": "intensive_therapy"}
    }
    
    result = await tools.handle_tool("generate_do_prompt", do_prompt_args)
    print("Generated prompt preview:", result["do_prompt"][:300] + "...")
    
    # Test 3: Causal edge extraction
    print("\n3. Testing Causal Edge Extraction")
    print("-" * 35)
    
    extraction_args = {
        "scenario_description": """
        In this healthcare study, we observe that older patients tend to have worse health outcomes.
        The treatment received affects recovery time. Patients with higher socioeconomic status
        have better access to treatments, which in turn leads to better health outcomes.
        """
    }
    
    result = await tools.handle_tool("extract_causal_edges", extraction_args)
    print("Extracted edges:", result["causal_edges"])
    print("Variables found:", result["extracted_variables"])
    
    print("\n✅ MCP Tools Testing Complete")


def print_mcp_server_info():
    """Print information about running MCP server."""
    config = create_mcp_config()
    
    print("🖥️  CausalLLM MCP Server")
    print("=" * 40)
    print(f"Server Name: {config['server']['name']}")
    print(f"Version: {config['server']['version']}")
    print(f"Description: {config['server']['description']}")
    print(f"Transport: {config['server']['transport']}")
    print()
    
    print("Available Tools:")
    for tool in config['tools']['enabled_tools']:
        print(f"  • {tool}")
    
    print("\nMCP Configuration:")
    print(json.dumps(config, indent=2))
    
    print("\nTo use with Claude Desktop, add this to your config:")
    claude_config = {
        "mcpServers": {
            "causallm": {
                "command": "python",
                "args": [os.path.abspath(__file__), "--server"],
                "env": {}
            }
        }
    }
    print(json.dumps(claude_config, indent=2))


async def run_mcp_server():
    """Run the MCP server (mock implementation)."""
    print("🚀 Starting CausalLLM MCP Server...")
    print("(This is a demonstration - actual MCP server implementation needs debugging)")
    print()
    
    # In a real implementation, this would:
    # 1. Initialize the MCP server with proper transports
    # 2. Register causal tools
    # 3. Handle MCP protocol messages
    # 4. Run event loop for client connections
    
    print("Mock server running... Press Ctrl+C to stop")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping MCP server...")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--server":
            print_mcp_server_info()
            print("\nStarting server mode...")
            asyncio.run(run_mcp_server())
        elif sys.argv[1] == "--test":
            asyncio.run(test_mcp_tools())
        elif sys.argv[1] == "--config":
            print_mcp_server_info()
        else:
            print("Usage: python mcp_server_example.py [--server|--test|--config]")
    else:
        print(__doc__)
        print("\nOptions:")
        print("  --server  Start MCP server")
        print("  --test    Test MCP tools")  
        print("  --config  Show configuration")


if __name__ == "__main__":
    main()