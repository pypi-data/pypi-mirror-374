"""Core components of the bricks-and-graphs framework."""

from .brick import AgentBrick, CompositeBrick
from .config_loader import (
    BrickFactory,
    BrickRegistry,
    load_graph,
    load_graph_definition,
    save_graph_definition,
)
from .graph import AgentGraph
from .litellm_manager import LiteLLMManager
from .node import AgentNode
from .types import (
    AgentContext,
    BrickProtocol,
    BrickType,
    BrickValidationError,
    EdgeConfig,
    ExecutionContext,
    GraphConfig,
    GraphDefinition,
    GraphValidationError,
    LiteLLMConfig,
    LiteLLMModelConfig,
    MultipleFoundationBricksError,
    MultipleRouterBricksError,
    NodeConfig,
    NoExitPathError,
    RouterBrickProtocol,
    RoutingDecision,
)

__all__ = [
    # Core classes
    "AgentBrick",
    "AgentGraph",
    "AgentNode",
    "CompositeBrick",
    # Configuration
    "BrickFactory",
    "BrickRegistry",
    "load_graph",
    "load_graph_definition",
    "save_graph_definition",
    # LiteLLM integration
    "LiteLLMManager",
    "LiteLLMConfig",
    "LiteLLMModelConfig",
    # Types and protocols
    "AgentContext",
    "BrickProtocol",
    "BrickType",
    "EdgeConfig",
    "ExecutionContext",
    "GraphConfig",
    "GraphDefinition",
    "NodeConfig",
    "RouterBrickProtocol",
    "RoutingDecision",
    # Exceptions
    "BrickValidationError",
    "GraphValidationError",
    "MultipleFoundationBricksError",
    "MultipleRouterBricksError",
    "NoExitPathError",
]
