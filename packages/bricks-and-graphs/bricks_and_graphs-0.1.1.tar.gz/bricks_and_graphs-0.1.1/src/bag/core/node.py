"""Implementation of AgentNode."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from .types import (
    BrickType,
    ExecutionContext,
    MultipleFoundationBricksError,
    MultipleRouterBricksError,
    NodeConfig,
    RouterBrickProtocol,
    RoutingDecision,
)

if TYPE_CHECKING:
    from .brick import AgentBrick
    from .graph import AgentGraph
    from .litellm_manager import LiteLLMManager


class AgentNode:
    """A node in the agent graph composed of multiple bricks.

    Nodes are the execution units in the graph. Each node contains
    multiple bricks that are executed in sequence, with the final
    brick being a RouterBrick if the node needs to route to other nodes.
    """

    def __init__(
        self,
        node_id: str | None = None,
        name: str | None = None,
        bricks: list[AgentBrick] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the node.

        Args:
            node_id: Unique identifier. Auto-generated if not provided.
            name: Human-readable name for the node.
            bricks: List of bricks that compose this node.
            metadata: Additional metadata for the node.
        """
        self._id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        self._name = name or f"Node_{self._id}"
        self._bricks = bricks or []
        self._metadata = metadata or {}
        self._graph: AgentGraph | None = None
        self._litellm_manager: LiteLLMManager | None = None

    @property
    def id(self) -> str:
        """Unique identifier for the node."""
        return self._id

    @property
    def name(self) -> str:
        """Human-readable name."""
        return self._name

    @property
    def bricks(self) -> list[AgentBrick]:
        """List of bricks in this node."""
        return self._bricks

    @property
    def metadata(self) -> dict[str, Any]:
        """Node metadata."""
        return self._metadata

    @property
    def graph(self) -> AgentGraph | None:
        """Parent graph containing this node."""
        return self._graph

    @graph.setter
    def graph(self, graph: AgentGraph) -> None:
        """Set the parent graph and inherit LiteLLM manager."""
        self._graph = graph
        # Inherit LiteLLM manager from graph
        if graph and graph.litellm_manager:
            self._litellm_manager = graph.litellm_manager

    def add_brick(self, brick: AgentBrick) -> None:
        """Add a brick to the node.

        Args:
            brick: Brick to add.
        """
        self._bricks.append(brick)

    def remove_brick(self, brick_id: str) -> bool:
        """Remove a brick by ID.

        Args:
            brick_id: ID of the brick to remove.

        Returns:
            True if brick was removed, False if not found.
        """
        initial_count = len(self._bricks)
        self._bricks = [b for b in self._bricks if b.id != brick_id]
        return len(self._bricks) < initial_count

    def get_brick(self, brick_id: str) -> AgentBrick | None:
        """Get a brick by ID.

        Args:
            brick_id: ID of the brick to retrieve.

        Returns:
            The brick if found, None otherwise.
        """
        for brick in self._bricks:
            if brick.id == brick_id:
                return brick
        return None

    @property
    def router_brick(self) -> RouterBrickProtocol | None:
        """Get the router brick if present.

        Returns:
            The last brick if it's a router, None otherwise.
        """
        if not self._bricks:
            return None

        last_brick = self._bricks[-1]
        if last_brick.brick_type == BrickType.ROUTER:
            return last_brick  # type: ignore

        return None

    @property
    def has_router(self) -> bool:
        """Check if this node has a router brick."""
        return self.router_brick is not None

    @property
    def litellm_manager(self) -> LiteLLMManager | None:
        """Get the LiteLLM manager from the parent graph."""
        return self._litellm_manager

    async def execute(
        self, context: ExecutionContext
    ) -> tuple[Any, RoutingDecision | None]:
        """Execute all bricks in the node.

        Args:
            context: Execution context.

        Returns:
            Tuple of (node output, routing decision).
            Routing decision is None if no router brick present.
        """
        # Track node visit
        context.visited_nodes.append(self.id)

        # Execute all bricks in sequence
        outputs = {}
        routing_decision = None

        for brick in self._bricks:
            output = await brick.execute(context)
            outputs[brick.id] = output

            # Store in context
            context.brick_outputs[brick.id] = output

            # If this is a router brick, capture the routing decision
            if brick.brick_type == BrickType.ROUTER:
                routing_decision = output

        # Store node output in context
        context.node_outputs[self.id] = outputs

        return outputs, routing_decision

    async def run(self, context: ExecutionContext) -> RoutingDecision | None:
        """Run the node with foundation->prompt->processor->router execution flow.

        This method orchestrates the execution of bricks in a specific order:
        1. Execute foundation brick (if present) to provide base data
        2. Collect and join all prompt bricks
        3. Execute LLM completion if prompts exist
        4. Pass results through processor bricks in order
        5. Pass final result to router brick (if exists)

        Args:
            context: Execution context.

        Returns:
            RoutingDecision from router brick, or None if no router present.

        Raises:
            RuntimeError: If LiteLLM manager is not available when prompts exist.
        """
        # Track node visit
        context.visited_nodes.append(self.id)

        # Separate bricks by type
        foundation_brick = None
        prompt_bricks = []
        processor_bricks = []
        router_brick = None
        other_bricks = []  # ACTION and other types

        for brick in self._bricks:
            if brick.brick_type == BrickType.FOUNDATION:
                foundation_brick = brick
            elif brick.brick_type == BrickType.PROMPT:
                prompt_bricks.append(brick)
            elif brick.brick_type == BrickType.PROCESSOR:
                processor_bricks.append(brick)
            elif brick.brick_type == BrickType.ROUTER:
                router_brick = brick
            else:
                # ACTION and other brick types
                other_bricks.append(brick)

        # Initialize node outputs dict
        outputs = {}
        current_data = None

        # Step 0: Execute foundation brick first (if present)
        if foundation_brick:
            foundation_output = await foundation_brick.execute(context)
            outputs[foundation_brick.id] = foundation_output
            context.brick_outputs[foundation_brick.id] = foundation_output

        # Step 1: Execute other bricks (ACTION, etc.)
        for brick in other_bricks:
            output = await brick.execute(context)
            outputs[brick.id] = output
            context.brick_outputs[brick.id] = output

        # Step 2: Execute prompt bricks and collect messages
        messages = []
        if prompt_bricks:
            for brick in prompt_bricks:
                # Execute prompt brick to get rendered content
                output = await brick.execute(context)
                outputs[brick.id] = output
                context.brick_outputs[brick.id] = output

                # Extract message from prompt brick output
                if isinstance(output, dict):
                    # Handle PromptBrick output format
                    if "message" in output:
                        messages.append(output["message"])
                    elif "content" in output and "role" in output:
                        messages.append(
                            {"role": output["role"], "content": output["content"]}
                        )

            # Step 3: Execute LLM completion if we have messages
            if messages and self._litellm_manager:
                try:
                    # Execute LLM completion
                    llm_response = await self._litellm_manager.complete(messages)

                    # Store LLM response in outputs
                    llm_output = {"response": llm_response, "messages": messages}
                    outputs["_llm_completion"] = llm_output
                    context.brick_outputs[f"{self.id}_llm_completion"] = llm_output

                    # Set current data to LLM response for processors
                    current_data = llm_response

                except Exception as e:
                    error_output = {"error": str(e), "messages": messages}
                    outputs["_llm_completion"] = error_output
                    context.brick_outputs[f"{self.id}_llm_completion"] = error_output
                    # Continue with error as current_data
                    current_data = error_output
            elif messages and not self._litellm_manager:
                raise RuntimeError(
                    f"Node {self.id} has prompt bricks but no LiteLLM manager available"
                )

        # Step 4: Process through processor bricks
        if processor_bricks:
            for brick in processor_bricks:
                # Pass current data to processor
                # Store current data in context for processor to access
                if current_data is not None:
                    context.agent_context["_current_processor_input"] = current_data

                # Execute processor
                output = await brick.execute(context)
                outputs[brick.id] = output
                context.brick_outputs[brick.id] = output

                # Update current data with processor output
                current_data = output

                # Clean up temporary context
                if "_current_processor_input" in context.agent_context:
                    del context.agent_context["_current_processor_input"]

        # Step 4: Execute router brick
        routing_decision = None
        if router_brick:
            # Pass current data to router
            if current_data is not None:
                context.agent_context["_current_router_input"] = current_data

            # Execute router
            output = await router_brick.execute(context)
            outputs[router_brick.id] = output
            context.brick_outputs[router_brick.id] = output

            # Extract routing decision
            if isinstance(output, RoutingDecision):
                routing_decision = output
            elif isinstance(output, dict) and "next_node_id" in output:
                # Handle dict-based routing decision
                routing_decision = RoutingDecision(
                    next_node_id=output.get("next_node_id"),
                    should_terminate=output.get("should_terminate", False),
                    metadata=output.get("metadata", {}),
                )

            # Clean up temporary context
            if "_current_router_input" in context.agent_context:
                del context.agent_context["_current_router_input"]

        # Store all outputs in context
        context.node_outputs[self.id] = outputs

        return routing_decision

    def validate(self) -> list[str]:
        """Validate the node configuration.

        Returns:
            List of validation errors. Empty if valid.

        Raises:
            MultipleFoundationBricksError: If node has more than one foundation brick.
            MultipleRouterBricksError: If node has more than one router brick.
        """
        errors = []

        if not self._bricks:
            errors.append(f"Node {self.id} has no bricks")

        # Check foundation bricks - only one allowed
        foundation_bricks = [
            b for b in self._bricks if b.brick_type == BrickType.FOUNDATION
        ]

        if len(foundation_bricks) > 1:
            raise MultipleFoundationBricksError(self.id, len(foundation_bricks))

        # Check if router brick is at the end if present
        router_bricks = [
            (i, b)
            for i, b in enumerate(self._bricks)
            if b.brick_type == BrickType.ROUTER
        ]

        if router_bricks:
            if len(router_bricks) > 1:
                raise MultipleRouterBricksError(self.id, len(router_bricks))

            router_idx, _ = router_bricks[0]
            if router_idx != len(self._bricks) - 1:
                errors.append(f"Node {self.id} has router brick not at the end")

        return errors

    def __repr__(self) -> str:
        """String representation of the node."""
        brick_info = f"{len(self._bricks)} bricks"
        if self.has_router:
            brick_info += " (with router)"
        return f"AgentNode(id={self.id}, name={self.name}, {brick_info})"

    @classmethod
    def from_config(
        cls,
        config: NodeConfig,
        brick_registry: dict[str, type[AgentBrick]] | None = None,
    ) -> AgentNode:
        """Create a node from configuration.

        Args:
            config: Node configuration.
            brick_registry: Optional registry mapping brick types to classes.

        Returns:
            Configured node instance.
        """
        # Create bricks from configs
        bricks = []
        for brick_config in config.brick_configs:
            brick_type = brick_config.get("type")
            if not brick_type:
                raise ValueError(f"Brick config missing 'type': {brick_config}")

            if brick_registry and brick_type in brick_registry:
                brick_class = brick_registry[brick_type]
                brick = brick_class.from_config(brick_config)
            else:
                # Fallback: attempt dynamic import
                # This would be implemented based on your module structure
                raise NotImplementedError(
                    f"Dynamic brick loading for type '{brick_type}' not implemented. "
                    "Please provide a brick_registry."
                )

            bricks.append(brick)

        return cls(
            node_id=config.id,
            name=config.name,
            bricks=bricks,
            metadata=config.metadata,
        )
