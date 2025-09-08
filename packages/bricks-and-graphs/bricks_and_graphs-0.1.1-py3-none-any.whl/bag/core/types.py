"""Type definitions and protocols for the bricks-and-graphs framework."""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel, ConfigDict, Field


# Custom exceptions for validation
class BrickValidationError(Exception):
    """Base exception for brick validation errors."""

    pass


class MultipleRouterBricksError(BrickValidationError):
    """Raised when a node contains more than one router brick."""

    def __init__(self, node_id: str, router_count: int):
        self.node_id = node_id
        self.router_count = router_count
        super().__init__(
            f"Node '{node_id}' contains {router_count} router bricks, "
            "but only 1 is allowed"
        )


class MultipleFoundationBricksError(BrickValidationError):
    """Raised when a node contains more than one foundation brick."""

    def __init__(self, node_id: str, foundation_count: int):
        self.node_id = node_id
        self.foundation_count = foundation_count
        super().__init__(
            f"Node '{node_id}' contains {foundation_count} foundation bricks, "
            "but only 1 is allowed"
        )


class GraphValidationError(Exception):
    """Base exception for graph validation errors."""

    pass


class NoExitPathError(GraphValidationError):
    """Raised when a cyclic graph has no possible exit path."""

    def __init__(self, cycle_nodes: list[str]):
        self.cycle_nodes = cycle_nodes
        super().__init__(
            f"Cyclic graph detected with nodes {cycle_nodes} but no exit path found. "
            "At least one node in the cycle must have a path to a node outside "
            "the cycle."
        )


class BrickType(Enum):
    """Types of bricks that can be used in nodes."""

    FOUNDATION = auto()  # Provides foundational data for other bricks
    PROMPT = auto()  # Part of the prompt for LLM
    ACTION = auto()  # Execute actions (e.g., shoot at LLM)
    PROCESSOR = auto()  # Process data (e.g., response from LLM)
    ROUTER = auto()  # Decide routing to next node


class AgentContext:
    """Shared context for graph execution.

    This context is created per AgentGraph and shared across all nodes
    and bricks during execution. It provides a flexible map that can
    store any type of data for inter-node/brick communication.
    """

    def __init__(self) -> None:
        """Initialize the agent context with an empty data map."""
        self._data: dict[str, Any] = {}

    @property
    def data(self) -> dict[str, Any]:
        """Get the underlying data dictionary (read-only view).

        Returns:
            The context data dictionary.
        """
        return self._data

    @property
    def keys(self) -> list[str]:
        """Get all keys in the context.

        Returns:
            List of all keys.
        """
        return list(self._data.keys())

    @property
    def values(self) -> list[Any]:
        """Get all values in the context.

        Returns:
            List of all values.
        """
        return list(self._data.values())

    @property
    def items(self) -> list[tuple[str, Any]]:
        """Get all key-value pairs in the context.

        Returns:
            List of (key, value) tuples.
        """
        return list(self._data.items())

    @property
    def is_empty(self) -> bool:
        """Check if the context is empty.

        Returns:
            True if no data stored, False otherwise.
        """
        return len(self._data) == 0

    def __getitem__(self, key: str) -> Any:
        """Get a value using dictionary-style access.

        Args:
            key: The key to retrieve.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If key not found.
        """
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value using dictionary-style access.

        Args:
            key: The key to set.
            value: The value to store.
        """
        self._data[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete a key using dictionary-style access.

        Args:
            key: The key to delete.

        Raises:
            KeyError: If key not found.
        """
        del self._data[key]

    def __contains__(self, key: str) -> bool:
        """Check if a key exists using 'in' operator.

        Args:
            key: The key to check.

        Returns:
            True if key exists, False otherwise.
        """
        return key in self._data

    def __len__(self) -> int:
        """Get the number of items in the context.

        Returns:
            Number of key-value pairs.
        """
        return len(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value with optional default.

        Args:
            key: The key to retrieve.
            default: Default value if key not found.

        Returns:
            The value associated with the key, or default if not found.
        """
        return self._data.get(key, default)

    def update(self, data: dict[str, Any]) -> None:
        """Update the context with multiple key-value pairs.

        Args:
            data: Dictionary of key-value pairs to update.
        """
        self._data.update(data)

    def clear(self) -> None:
        """Clear all data from the context."""
        self._data.clear()

    def pop(self, key: str, default: Any = None) -> Any:
        """Remove and return a value.

        Args:
            key: The key to remove.
            default: Default value if key not found.

        Returns:
            The value that was removed, or default if not found.
        """
        return self._data.pop(key, default)

    def to_dict(self) -> dict[str, Any]:
        """Get a copy of the entire context as a dictionary.

        Returns:
            Copy of the context data.
        """
        return self._data.copy()

    def __repr__(self) -> str:
        """String representation of the context."""
        return f"AgentContext(keys={list(self._data.keys())})"


class ExecutionContext(BaseModel):
    """Context passed through the graph during execution."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    # Core context data
    data: dict[str, Any] = {}
    metadata: dict[str, Any] = {}

    # Execution tracking
    visited_nodes: list[str] = []
    loop_counters: dict[str, int] = {}

    # Results from previous bricks/nodes
    brick_outputs: dict[str, Any] = {}
    node_outputs: dict[str, Any] = {}

    # Shared agent context (set by graph during execution)
    agent_context: AgentContext | None = None

    # LiteLLM manager (set by graph during execution)
    litellm_manager: Any | None = None  # Using Any to avoid circular import


@dataclass
class RoutingDecision:
    """Result of router brick execution."""

    next_node_id: str | None
    metadata: dict[str, Any] = field(default_factory=dict)
    should_terminate: bool = False


class BrickProtocol(Protocol):
    """Protocol defining the interface for all bricks."""

    @property
    def id(self) -> str:
        """Unique identifier for the brick."""
        ...

    @property
    def brick_type(self) -> BrickType:
        """Type of the brick."""
        ...

    async def execute(self, context: ExecutionContext) -> Any:
        """Execute the brick's logic."""
        ...


class RouterBrickProtocol(BrickProtocol):
    """Specialized protocol for router bricks."""

    @abc.abstractmethod
    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        """Execute routing logic and return decision."""
        ...


# Type variables for generic implementations
T = TypeVar("T")
BrickT = TypeVar("BrickT", bound=BrickProtocol)
NodeT = TypeVar("NodeT")
GraphT = TypeVar("GraphT")


class LiteLLMModelConfig(BaseModel):
    """Configuration for a single LiteLLM model."""

    model_config = ConfigDict(extra="forbid")

    model: str = Field(..., description="Model name (e.g., 'gpt-4', 'claude-3-sonnet')")
    api_key: str | None = Field(None, description="API key for this model")
    api_base: str | None = Field(None, description="Custom API base URL")
    api_version: str | None = Field(None, description="API version")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, gt=0)
    top_p: float | None = Field(None, ge=0.0, le=1.0)
    timeout: int = Field(600, description="Request timeout in seconds")
    max_retries: int = Field(3, ge=0)
    custom_llm_provider: str | None = Field(None, description="Custom provider name")

    # Additional model-specific parameters
    extra_params: dict[str, Any] = Field(default_factory=dict)


class LiteLLMConfig(BaseModel):
    """Configuration for LiteLLM integration."""

    model_config = ConfigDict(extra="forbid")

    # Model configurations
    models: list[LiteLLMModelConfig] = Field(
        ..., description="List of model configurations", min_length=1
    )

    # Default model to use
    default_model: str | None = Field(
        None, description="Default model name from the models list"
    )

    # Global settings
    enable_caching: bool = Field(False, description="Enable response caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")
    log_level: str = Field("INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    # Fallback configuration
    enable_fallback: bool = Field(True, description="Enable model fallback on errors")
    fallback_order: list[str] | None = Field(
        None, description="Order of models to try on fallback"
    )

    def get_model_config(self, model_name: str) -> LiteLLMModelConfig | None:
        """Get configuration for a specific model."""
        for model in self.models:
            if model.model == model_name:
                return model
        return None

    def get_default_model_config(self) -> LiteLLMModelConfig:
        """Get the default model configuration."""
        if self.default_model:
            config = self.get_model_config(self.default_model)
            if config:
                return config
        return self.models[0]


@dataclass
class GraphConfig:
    """Configuration for graph execution."""

    max_iterations: int = 100
    max_loop_count: int = 10
    enable_async: bool = True
    debug: bool = False
    litellm_config: LiteLLMConfig | None = None


@dataclass
class NodeConfig:
    """Configuration for a single node."""

    id: str
    name: str | None = None
    brick_configs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EdgeConfig:
    """Configuration for graph edges."""

    source: str
    target: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphDefinition:
    """Complete graph definition for serialization."""

    nodes: list[NodeConfig]
    edges: list[EdgeConfig]
    config: GraphConfig = field(default_factory=GraphConfig)
    metadata: dict[str, Any] = field(default_factory=dict)
