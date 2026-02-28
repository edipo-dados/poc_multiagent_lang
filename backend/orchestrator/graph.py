"""
LangGraph Orchestrator - Deterministic Agent Pipeline

This module implements the RegulatoryAnalysisGraph class that orchestrates
the execution of six agents in a deterministic sequence using LangGraph.

The pipeline executes agents in this order:
1. Sentinel Agent - Change detection and risk assessment
2. Translator Agent - Regulatory text structuring
3. CodeReader Agent - Relevant file identification
4. Impact Agent - Technical impact analysis
5. SpecGenerator Agent - Technical specification generation
6. KiroPrompt Agent - Development prompt generation

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""

import logging
import asyncio
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, END
from backend.models.state import GlobalState
from backend.agents.sentinel import sentinel_agent
from backend.agents.translator import translator_agent
from backend.agents.code_reader import code_reader_agent as code_reader_agent_async
from backend.agents.impact import impact_agent
from backend.agents.spec_generator import spec_generator_agent as spec_generator_agent_impl
from backend.agents.kiro_prompt import kiro_prompt_agent as kiro_prompt_agent_impl


logger = logging.getLogger(__name__)

# Thread pool for running async code_reader
_executor = ThreadPoolExecutor(max_workers=1)


# Wrapper for async code_reader_agent
def code_reader_agent(state: GlobalState) -> GlobalState:
    """
    CodeReader Agent - Identify relevant code files.
    
    Synchronous wrapper that runs the async code_reader_agent using asyncio.
    
    Args:
        state: GlobalState containing regulatory_model
        
    Returns:
        Updated GlobalState with impacted_files list
    """
    try:
        # Run async code_reader_agent in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(code_reader_agent_async(state))
            return result
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"CodeReader Agent wrapper failed: {str(e)}", exc_info=True)
        # Return empty list on error to allow pipeline to continue
        state.impacted_files = []
        return state


def spec_generator_agent(state: GlobalState) -> GlobalState:
    """
    SpecGenerator Agent - Generate technical specification.
    
    Delegates to the actual implementation in backend.agents.spec_generator.
    
    Args:
        state: GlobalState containing regulatory_model and impact_analysis
        
    Returns:
        Updated GlobalState with technical_spec
    """
    return spec_generator_agent_impl(state)


def kiro_prompt_agent_wrapper(state: GlobalState) -> GlobalState:
    """
    KiroPrompt Agent - Generate development prompt.
    
    Delegates to the actual implementation in backend.agents.kiro_prompt.
    
    Args:
        state: GlobalState containing technical_spec and impact_analysis
        
    Returns:
        Updated GlobalState with kiro_prompt
    """
    return kiro_prompt_agent_impl(state)


class RegulatoryAnalysisGraph:
    """
    LangGraph orchestrator for deterministic agent pipeline execution.
    
    This class manages the execution of six agents in a fixed sequence,
    ensuring deterministic behavior and proper error handling.
    
    The graph structure:
    - Entry point: sentinel
    - Edges: sentinel → translator → code_reader → impact → spec_generator → kiro_prompt → END
    - State: GlobalState passed through all agents
    
    Requirements:
        - 2.1: Execute agents in deterministic sequence
        - 2.2: Pass Global State between agents
        - 2.3: Automatically trigger next agent
        - 2.4: Update Global State at each step
        - 2.5: Halt execution on agent failure
    """
    
    def __init__(self):
        """Initialize the LangGraph orchestrator with agent pipeline."""
        logger.info("Initializing RegulatoryAnalysisGraph")
        
        # Create StateGraph with GlobalState as the state type
        self.graph = StateGraph(GlobalState)
        
        # Build the graph structure
        self._build_graph()
        
        # Compile the graph for execution
        self.compiled_graph = self.graph.compile()
        
        logger.info("RegulatoryAnalysisGraph initialized successfully")
    
    def _build_graph(self) -> None:
        """
        Build the LangGraph structure with nodes and edges.
        
        Defines:
        - Six agent nodes (sentinel, translator, code_reader, impact, spec_generator, kiro_prompt)
        - Deterministic edges connecting agents in sequence
        - Entry point at sentinel agent
        - Exit point after kiro_prompt agent
        """
        logger.debug("Building graph structure")
        
        # Add nodes for all six agents
        # Each node wraps the agent function with error handling
        self.graph.add_node("sentinel", self._wrap_agent(sentinel_agent, "Sentinel"))
        self.graph.add_node("translator", self._wrap_agent(translator_agent, "Translator"))
        self.graph.add_node("code_reader", self._wrap_agent(code_reader_agent, "CodeReader"))
        self.graph.add_node("impact", self._wrap_agent(impact_agent, "Impact"))
        self.graph.add_node("spec_generator", self._wrap_agent(spec_generator_agent, "SpecGenerator"))
        self.graph.add_node("kiro_prompt_gen", self._wrap_agent(kiro_prompt_agent_wrapper, "KiroPrompt"))
        
        # Set entry point
        self.graph.set_entry_point("sentinel")
        
        # Define deterministic edges in sequence
        self.graph.add_edge("sentinel", "translator")
        self.graph.add_edge("translator", "code_reader")
        self.graph.add_edge("code_reader", "impact")
        self.graph.add_edge("impact", "spec_generator")
        self.graph.add_edge("spec_generator", "kiro_prompt_gen")
        self.graph.add_edge("kiro_prompt_gen", END)
        
        logger.debug("Graph structure built successfully")
    
    def _wrap_agent(self, agent_func, agent_name: str):
        """
        Wrap an agent function with error handling and logging.
        
        This wrapper:
        - Logs agent execution start and completion
        - Catches exceptions and sets state.error
        - Re-raises exceptions to halt pipeline execution
        - Ensures proper error propagation
        
        Args:
            agent_func: The agent function to wrap
            agent_name: Name of the agent for logging
            
        Returns:
            Wrapped agent function with error handling
        """
        def wrapped_agent(state: GlobalState) -> GlobalState:
            """Wrapped agent with error handling."""
            logger.info(f"=== {agent_name} Agent Starting ===")
            logger.debug(f"Execution ID: {state.execution_id}")
            
            try:
                # Execute the agent
                updated_state = agent_func(state)
                
                logger.info(f"=== {agent_name} Agent Completed Successfully ===")
                return updated_state
                
            except Exception as e:
                # Log the error
                logger.error(f"=== {agent_name} Agent Failed ===", exc_info=True)
                logger.error(f"Error: {str(e)}")
                
                # Set error in state
                error_msg = f"{agent_name} Agent error: {str(e)}"
                state.error = error_msg
                
                # Re-raise to halt execution
                raise RuntimeError(error_msg) from e
        
        return wrapped_agent
    
    def execute(self, initial_state: GlobalState) -> GlobalState:
        """
        Execute the agent pipeline with the given initial state.
        
        This method:
        1. Validates the initial state
        2. Invokes the compiled graph
        3. Handles execution errors
        4. Returns the final state (or partial state on failure)
        
        Args:
            initial_state: GlobalState with raw_regulatory_text and execution_id set
            
        Returns:
            Final GlobalState after all agents execute (or partial state on failure)
            
        Raises:
            RuntimeError: If agent execution fails
            ValueError: If initial state is invalid
            
        Requirements:
            - 2.1: Executes agents in deterministic sequence
            - 2.2: Passes Global State between agents
            - 2.5: Halts execution on agent failure
        """
        logger.info(f"Starting graph execution for execution_id: {initial_state.execution_id}")
        
        # Validate initial state
        if not initial_state.raw_regulatory_text:
            raise ValueError("raw_regulatory_text is required in initial state")
        
        if not initial_state.execution_id:
            raise ValueError("execution_id is required in initial state")
        
        try:
            # Execute the compiled graph
            logger.info("Invoking compiled graph")
            final_state_dict = self.compiled_graph.invoke(initial_state)
            
            # Convert dict back to GlobalState if needed
            if isinstance(final_state_dict, dict):
                final_state = GlobalState(**final_state_dict)
            else:
                final_state = final_state_dict
            
            logger.info(f"Graph execution completed successfully for execution_id: {initial_state.execution_id}")
            logger.info(f"Final state - change_detected: {final_state.change_detected}, risk_level: {final_state.risk_level}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Graph execution failed for execution_id: {initial_state.execution_id}", exc_info=True)
            logger.error(f"Error: {str(e)}")
            
            # If state has error set, return it (partial state)
            if hasattr(initial_state, 'error') and initial_state.error:
                logger.info("Returning partial state with error information")
                return initial_state
            
            # Otherwise, set error and re-raise
            initial_state.error = f"Graph execution failed: {str(e)}"
            raise RuntimeError(f"Graph execution failed: {str(e)}") from e
