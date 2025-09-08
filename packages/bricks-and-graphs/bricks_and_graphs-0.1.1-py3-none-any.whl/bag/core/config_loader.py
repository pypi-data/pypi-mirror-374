"""Configuration loading utilities for YAML/JSON graph definitions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, TypeVar

import yaml

from .graph import AgentGraph
from .types import EdgeConfig, GraphConfig, GraphDefinition, NodeConfig

if TYPE_CHECKING:
    from .brick import AgentBrick

T = TypeVar("T")


class BrickFactory(Protocol):
    """Protocol for brick factories."""

    def create_brick(self, brick_type: str, config: dict[str, Any]) -> AgentBrick:
        """Create a brick instance from type and config."""
        ...


class BrickRegistry:
    """Registry for brick types and their factories."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._registry: dict[str, type[AgentBrick]] = {}
        self._factories: dict[str, BrickFactory] = {}

    def register_brick(
        self,
        brick_type: str,
        brick_class: type[AgentBrick],
    ) -> None:
        """Register a brick class.

        Args:
            brick_type: Type identifier for the brick.
            brick_class: Brick class to register.
        """
        self._registry[brick_type] = brick_class

    def register_factory(
        self,
        brick_type: str,
        factory: BrickFactory,
    ) -> None:
        """Register a brick factory.

        Args:
            brick_type: Type identifier for the brick.
            factory: Factory to create brick instances.
        """
        self._factories[brick_type] = factory

    def create_brick(self, brick_type: str, config: dict[str, Any]) -> AgentBrick:
        """Create a brick instance.

        Args:
            brick_type: Type of brick to create.
            config: Brick configuration.

        Returns:
            Created brick instance.
        """
        # Try factory first
        if brick_type in self._factories:
            return self._factories[brick_type].create_brick(brick_type, config)

        # Try registered class
        if brick_type in self._registry:
            brick_class = self._registry[brick_type]
            return brick_class.from_config(config)

        raise ValueError(f"Unknown brick type: {brick_type}")

    def get_registry_dict(self) -> dict[str, type[AgentBrick]]:
        """Get the registry as a dictionary."""
        return self._registry.copy()


def load_graph_definition(source: str | Path | dict[str, Any]) -> GraphDefinition:
    """Load a graph definition from various sources.

    Args:
        source: Can be:
            - Path to YAML/JSON file
            - String containing YAML/JSON
            - Dictionary with graph definition

    Returns:
        Parsed graph definition.
    """
    # Handle dictionary input
    if isinstance(source, dict):
        return _parse_graph_dict(source)

    # Handle file path
    if isinstance(source, Path) or (isinstance(source, str) and Path(source).exists()):
        path = Path(source)
        content = path.read_text()

        if path.suffix in {".yaml", ".yml"}:
            data = yaml.safe_load(content)
        elif path.suffix == ".json":
            data = json.loads(content)
        else:
            # Try to parse as YAML first, then JSON
            try:
                data = yaml.safe_load(content)
            except yaml.YAMLError:
                data = json.loads(content)

        return _parse_graph_dict(data)

    # Handle string content
    if isinstance(source, str):
        # Try YAML first, then JSON
        try:
            data = yaml.safe_load(source)
        except yaml.YAMLError:
            data = json.loads(source)

        return _parse_graph_dict(data)

    raise ValueError(f"Invalid source type: {type(source)}")


def _parse_graph_dict(data: dict[str, Any]) -> GraphDefinition:
    """Parse a dictionary into a GraphDefinition.

    Args:
        data: Dictionary containing graph definition.

    Returns:
        Parsed graph definition.
    """
    # Parse nodes
    nodes = []
    for node_data in data.get("nodes", []):
        node_config = NodeConfig(
            id=node_data["id"],
            name=node_data.get("name"),
            brick_configs=node_data.get("bricks", []),
            metadata=node_data.get("metadata", {}),
        )
        nodes.append(node_config)

    # Parse edges
    edges = []
    for edge_data in data.get("edges", []):
        edge_config = EdgeConfig(
            source=edge_data["source"],
            target=edge_data["target"],
            metadata=edge_data.get("metadata", {}),
        )
        edges.append(edge_config)

    # Parse config
    config_data = data.get("config", {})
    config = GraphConfig(
        max_iterations=config_data.get("max_iterations", 100),
        max_loop_count=config_data.get("max_loop_count", 10),
        enable_async=config_data.get("enable_async", True),
        debug=config_data.get("debug", False),
    )

    return GraphDefinition(
        nodes=nodes,
        edges=edges,
        config=config,
        metadata=data.get("metadata", {}),
    )


def save_graph_definition(
    definition: GraphDefinition,
    path: Path,
    format: str = "yaml",
) -> None:
    """Save a graph definition to file.

    Args:
        definition: Graph definition to save.
        path: Path to save to.
        format: Output format ("yaml" or "json").
    """
    # Convert to dictionary
    data = {
        "metadata": definition.metadata,
        "config": {
            "max_iterations": definition.config.max_iterations,
            "max_loop_count": definition.config.max_loop_count,
            "enable_async": definition.config.enable_async,
            "debug": definition.config.debug,
        },
        "nodes": [
            {
                "id": node.id,
                "name": node.name,
                "metadata": node.metadata,
                "bricks": node.brick_configs,
            }
            for node in definition.nodes
        ],
        "edges": [
            {
                "source": edge.source,
                "target": edge.target,
                "metadata": edge.metadata,
            }
            for edge in definition.edges
        ],
    }

    # Write to file
    if format == "yaml":
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    elif format == "json":
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    else:
        raise ValueError(f"Unknown format: {format}")


def load_graph(
    source: str | Path | dict[str, Any],
    brick_registry: BrickRegistry | None = None,
) -> AgentGraph:
    """Load a graph from configuration.

    Args:
        source: Graph definition source.
        brick_registry: Optional brick registry for creating bricks.

    Returns:
        Loaded graph instance.
    """
    definition = load_graph_definition(source)

    registry_dict = None
    if brick_registry:
        registry_dict = brick_registry.get_registry_dict()

    return AgentGraph.from_config(definition, registry_dict)
