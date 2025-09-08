"""Implementation of AgentGraph with networkx integration."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import networkx as nx

from .litellm_manager import LiteLLMManager
from .node import AgentNode
from .types import (
    AgentContext,
    ExecutionContext,
    GraphConfig,
    GraphDefinition,
    NoExitPathError,
)

if TYPE_CHECKING:
    from .brick import AgentBrick


class AgentGraph:
    """A directed graph of agent nodes.

    Supports cyclic graphs with loop counters and provides
    execution capabilities for running through the graph.
    """

    def __init__(
        self,
        graph_id: str | None = None,
        name: str | None = None,
        config: GraphConfig | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the graph.

        Args:
            graph_id: Unique identifier. Auto-generated if not provided.
            name: Human-readable name for the graph.
            config: Graph configuration.
            metadata: Additional metadata for the graph.
        """
        self._id = graph_id or f"graph_{uuid.uuid4().hex[:8]}"
        self._name = name or f"Graph_{self._id}"
        self._config = config or GraphConfig()
        self._metadata = metadata or {}

        # NetworkX directed graph for structure
        self._graph = nx.DiGraph()

        # Node registry
        self._nodes: dict[str, AgentNode] = {}

        # Entry points (nodes with no incoming edges)
        self._entry_nodes: set[str] = set()

        # Shared agent context for this graph
        self._agent_context = AgentContext()

        # Initialize LiteLLM if configuration provided
        self._litellm_manager: LiteLLMManager | None = None
        if self._config.litellm_config:
            self._litellm_manager = LiteLLMManager(self._config.litellm_config)

    @property
    def id(self) -> str:
        """Unique identifier for the graph."""
        return self._id

    @property
    def name(self) -> str:
        """Human-readable name."""
        return self._name

    @property
    def config(self) -> GraphConfig:
        """Graph configuration."""
        return self._config

    @property
    def metadata(self) -> dict[str, Any]:
        """Graph metadata."""
        return self._metadata

    @property
    def nodes(self) -> dict[str, AgentNode]:
        """All nodes in the graph."""
        return self._nodes.copy()

    @property
    def entry_nodes(self) -> set[str]:
        """Nodes with no incoming edges."""
        return self._entry_nodes.copy()

    @property
    def networkx_graph(self) -> nx.DiGraph:
        """Access to underlying NetworkX graph."""
        return self._graph

    @property
    def agent_context(self) -> AgentContext:
        """Get the shared agent context for this graph."""
        return self._agent_context

    @property
    def litellm_manager(self) -> LiteLLMManager | None:
        """Get the LiteLLM manager for this graph."""
        return self._litellm_manager

    def add_node(self, node: AgentNode) -> None:
        """Add a node to the graph.

        Args:
            node: Node to add.
        """
        self._nodes[node.id] = node
        self._graph.add_node(node.id, node=node)
        node.graph = self

        # Update entry nodes
        self._update_entry_nodes()

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the graph.

        Args:
            node_id: ID of the node to remove.

        Returns:
            True if node was removed, False if not found.
        """
        if node_id not in self._nodes:
            return False

        node = self._nodes[node_id]
        node.graph = None

        del self._nodes[node_id]
        self._graph.remove_node(node_id)

        # Update entry nodes
        self._update_entry_nodes()

        return True

    def get_node(self, node_id: str) -> AgentNode | None:
        """Get a node by ID.

        Args:
            node_id: ID of the node to retrieve.

        Returns:
            The node if found, None otherwise.
        """
        return self._nodes.get(node_id)

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add an edge between nodes.

        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            metadata: Optional edge metadata.
        """
        if source_id not in self._nodes:
            raise ValueError(f"Source node {source_id} not found")
        if target_id not in self._nodes:
            raise ValueError(f"Target node {target_id} not found")

        self._graph.add_edge(source_id, target_id, metadata=metadata or {})

        # Update entry nodes
        self._update_entry_nodes()

    def remove_edge(self, source_id: str, target_id: str) -> bool:
        """Remove an edge between nodes.

        Args:
            source_id: Source node ID.
            target_id: Target node ID.

        Returns:
            True if edge was removed, False if not found.
        """
        if self._graph.has_edge(source_id, target_id):
            self._graph.remove_edge(source_id, target_id)
            self._update_entry_nodes()
            return True
        return False

    def get_successors(self, node_id: str) -> list[str]:
        """Get successor node IDs.

        Args:
            node_id: Node to get successors for.

        Returns:
            List of successor node IDs.
        """
        return list(self._graph.successors(node_id))

    def get_predecessors(self, node_id: str) -> list[str]:
        """Get predecessor node IDs.

        Args:
            node_id: Node to get predecessors for.

        Returns:
            List of predecessor node IDs.
        """
        return list(self._graph.predecessors(node_id))

    def _update_entry_nodes(self) -> None:
        """Update the set of entry nodes."""
        self._entry_nodes = {
            node_id for node_id in self._nodes if self._graph.in_degree(node_id) == 0
        }

    def find_cycles(self) -> list[list[str]]:
        """Find all cycles in the graph.

        Returns:
            List of cycles, where each cycle is a list of node IDs.
        """
        return list(nx.simple_cycles(self._graph))

    def validate(self) -> list[str]:
        """Validate the graph structure.

        Returns:
            List of validation errors. Empty if valid.

        Raises:
            NoExitPathError: If a cycle has no exit path.
            MultipleRouterBricksError: If any node has multiple router bricks.
        """
        errors = []

        # Check for empty graph
        if not self._nodes:
            errors.append("Graph has no nodes")
            return errors

        # Check for entry nodes
        if not self._entry_nodes:
            errors.append("Graph has no entry nodes (all nodes have incoming edges)")

        # Validate individual nodes (this may raise MultipleRouterBricksError)
        for _node_id, node in self._nodes.items():
            node_errors = node.validate()
            errors.extend(node_errors)

        # Check cycles and exit paths
        cycles = self.find_cycles()
        for cycle in cycles:
            # Check if there's an exit path from the cycle
            has_exit = False
            for node_id in cycle:
                successors = set(self.get_successors(node_id))
                if successors - set(cycle):
                    has_exit = True
                    break

            if not has_exit:
                raise NoExitPathError(cycle)

        return errors

    async def execute(
        self,
        context: ExecutionContext | None = None,
        start_node_id: str | None = None,
    ) -> ExecutionContext:
        """Execute the graph from a starting point.

        Args:
            context: Initial execution context. Created if not provided.
            start_node_id: Node to start from. Uses first entry node if not provided.

        Returns:
            Final execution context.

        Raises:
            NoExitPathError: If graph has cycles without exit paths.
            MultipleRouterBricksError: If any node has multiple router bricks.
            ValueError: If graph is invalid or start node not found.
        """
        # Validate graph before execution
        validation_errors = self.validate()
        if validation_errors:
            raise ValueError(f"Graph validation failed: {'; '.join(validation_errors)}")

        # Initialize context
        if context is None:
            context = ExecutionContext()

        # Set the agent context for this execution
        context.agent_context = self._agent_context

        # Set the LiteLLM manager for this execution
        context.litellm_manager = self._litellm_manager

        # Determine starting node
        if start_node_id is None:
            if not self._entry_nodes:
                raise ValueError("No entry nodes available")
            start_node_id = sorted(self._entry_nodes)[0]

        if start_node_id not in self._nodes:
            raise ValueError(f"Start node {start_node_id} not found")

        # Execute graph traversal
        current_node_id: str | None = start_node_id
        iterations = 0

        while current_node_id is not None:
            # Check iteration limit
            iterations += 1
            if iterations > self._config.max_iterations:
                raise RuntimeError(
                    f"Exceeded maximum iterations ({self._config.max_iterations})"
                )

            # Check loop counter for this node
            loop_key = f"{current_node_id}_loop"
            context.loop_counters[loop_key] = context.loop_counters.get(loop_key, 0) + 1

            if context.loop_counters[loop_key] > self._config.max_loop_count:
                # Find alternative path or terminate
                successors = self.get_successors(current_node_id)
                unvisited = [
                    s
                    for s in successors
                    if context.loop_counters.get(f"{s}_loop", 0)
                    < self._config.max_loop_count
                ]

                if unvisited:
                    current_node_id = unvisited[0]
                    continue
                else:
                    break  # No unvisited successors, terminate

            # Execute current node
            node = self._nodes[current_node_id]
            # Use the new run method for orchestrated execution
            routing_decision = await node.run(context)

            # Determine next node
            if routing_decision and not routing_decision.should_terminate:
                next_node_id = routing_decision.next_node_id

                # Validate routing
                if next_node_id and next_node_id in self.get_successors(
                    current_node_id
                ):
                    current_node_id = next_node_id
                else:
                    # Invalid routing, try first valid successor
                    successors = self.get_successors(current_node_id)
                    current_node_id = successors[0] if successors else None
            elif routing_decision and routing_decision.should_terminate:
                # Explicit termination requested
                current_node_id = None
            else:
                # No routing decision (no router brick), try to continue with successors
                successors = self.get_successors(current_node_id)
                current_node_id = successors[0] if successors else None

        return context

    def to_dict(self) -> dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "config": {
                "max_iterations": self.config.max_iterations,
                "max_loop_count": self.config.max_loop_count,
                "enable_async": self.config.enable_async,
                "debug": self.config.debug,
            },
            "metadata": self.metadata,
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "metadata": node.metadata,
                    "bricks": [
                        {
                            "id": brick.id,
                            "type": brick.__class__.__name__,
                            "name": brick.name,
                            "metadata": brick.metadata,
                        }
                        for brick in node.bricks
                    ],
                }
                for node in self._nodes.values()
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "metadata": data.get("metadata", {}),
                }
                for source, target, data in self._graph.edges(data=True)
            ],
        }

    @classmethod
    def from_config(
        cls,
        definition: GraphDefinition,
        brick_registry: dict[str, type[AgentBrick]] | None = None,
    ) -> AgentGraph:
        """Create a graph from configuration.

        Args:
            definition: Graph definition.
            brick_registry: Optional registry mapping brick types to classes.

        Returns:
            Configured graph instance.
        """
        # Create graph
        graph = cls(
            graph_id=definition.metadata.get("id"),
            name=definition.metadata.get("name"),
            config=definition.config,
            metadata=definition.metadata,
        )

        # Create and add nodes
        for node_config in definition.nodes:
            node = AgentNode.from_config(node_config, brick_registry)
            graph.add_node(node)

        # Add edges
        for edge_config in definition.edges:
            graph.add_edge(
                edge_config.source,
                edge_config.target,
                edge_config.metadata,
            )

        return graph

    def __repr__(self) -> str:
        """String representation of the graph."""
        return (
            f"AgentGraph(id={self.id}, name={self.name}, "
            f"nodes={len(self._nodes)}, edges={self._graph.number_of_edges()})"
        )
