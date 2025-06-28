import os
from enum import Enum
from dataclasses import dataclass, fields, field, asdict
from typing import Any, Optional, Dict, Literal
import copy

from langchain_core.runnables import RunnableConfig

DEFAULT_REPORT_STRUCTURE = """Use this structure to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for 1 structural element (either a list or table) that distills the main body sections 
   - Provide a concise summary of the report"""

class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    EXA = "exa"
    GOOGLESEARCH = "googlesearch"

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    # Common configuration
    report_structure: str = DEFAULT_REPORT_STRUCTURE # Defaults to the default report structure
    search_api: SearchAPI = SearchAPI.TAVILY # Default to TAVILY
    search_api_config: Optional[Dict[str, Any]] = None
    time_range: Optional[str] = None # Add time_range for date-filtered searches
    process_search_results: Literal["summarize", "split_and_rerank"] | None = None
    # Summarization model for summarizing search results
    # will be used if summarize_search_results is True
    summarization_model_provider: str = "openai"
    summarization_model: str = "gpt-4o-mini"
    # Whether to include search results string in the agent output state
    # This is used for evaluation purposes only
    include_source_str: bool = False
    
    # Graph-specific configuration
    number_of_queries: int = 2 # Number of search queries to generate per iteration
    max_search_depth: int = 2 # Maximum number of reflection + search iterations
    planner_provider: str = "openai"  # Defaults to Anthropic as provider
    planner_model: str = "gpt-4o-mini" # Defaults to claude-3-7-sonnet-latest
    planner_model_kwargs: Optional[Dict[str, Any]] = None # kwargs for planner_model
    writer_provider: str = "openai" # Defaults to Anthropic as provider
    writer_model: str = "gpt-4o-mini" # Defaults to claude-3-5-sonnet-latest
    writer_model_kwargs: Optional[Dict[str, Any]] = None # kwargs for writer_model
    
    # Multi-agent specific configuration
    supervisor_model: str = "openai:gpt-4.1" # Model for supervisor agent in multi-agent setup
    researcher_model: str = "openai:gpt-4.1" # Model for research agents in multi-agent setup 
    ask_for_clarification: bool = False # Whether to ask for clarification from the user
    # MCP server configuration for multi-agent setup
    # see examples here: https://github.com/langchain-ai/langchain-mcp-adapters#client-1
    mcp_server_config: Optional[Dict[str, Any]] = None
    # optional prompt to append to the researcher agent prompt
    mcp_prompt: Optional[str] = None
    # optional list of MCP tool names to include in the researcher agent
    # if not set, all MCP tools across all servers in the config will be included
    mcp_tools_to_include: Optional[list[str]] = None

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**values)

    def copy(self):
        """Return a deep copy of this configuration."""
        return copy.deepcopy(self)
    
    def items(self):
        """Return items as (key, value) pairs like a dictionary."""
        return asdict(self).items()
    
    def keys(self):
        """Return keys like a dictionary."""
        return asdict(self).keys()
    
    def values(self):
        """Return values like a dictionary."""
        return asdict(self).values()
    
    def get(self, key, default=None):
        """Get a value by key, with optional default."""
        return getattr(self, key, default)
    
    def __getitem__(self, key):
        """Allow dictionary-style access."""
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        """Allow dictionary-style assignment."""
        setattr(self, key, value)
    
    def __contains__(self, key):
        """Check if key exists."""
        return hasattr(self, key)
