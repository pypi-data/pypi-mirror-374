"""RouterBrick implementation for graph routing decisions.

RouterBrick provides an interface for making routing decisions based on
processed data. It has access to the graph structure and can route to
any available node.

Example:
    >>> # Conditional router based on data content
    >>> class ConditionalRouter(RouterBrick):
    ...     async def compute_route(self, data, context):
    ...         if isinstance(data, dict) and data.get("status") == "error":
    ...             return RouteDecision(
    ...                 target_node="error_handler",
    ...                 reason="Error status detected"
    ...             )
    ...         return RouteDecision(target_node="success_handler")
    >>>
    >>> # LLM-based intelligent router
    >>> class LLMRouter(RouterBrick):
    ...     async def compute_route(self, data, context):
    ...         # Use LLM to decide routing
    ...         prompt = f"Given {data}, should we go to A or B?"
    ...         # ... LLM call logic ...
    ...         return RouteDecision(target_node=decision)
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from ..core import BrickType, ExecutionContext, RoutingDecision
from .processor import ProcessorBrick
from .types import (
    DataFormat,
    DataType,
    ProcessingContext,
    ProcessingMode,
    RouteDecision,
)


class RouterBrick(ProcessorBrick):
    """Base class for routing bricks.

    RouterBrick extends ProcessorBrick to provide routing capabilities.
    It can process data in the same formats as ProcessorBrick but returns
    routing decisions instead of transformed data.

    Attributes:
        available_routes: List of available node IDs for routing.
        default_route: Default node to route to if no decision is made.
    """

    BRICK_TYPE = BrickType.ROUTER

    def __init__(
        self,
        available_routes: list[str] | None = None,
        default_route: str | None = None,
        input_format: DataFormat | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the RouterBrick.

        Args:
            available_routes: List of available node IDs (auto-detected if None).
            default_route: Default node to route to.
            input_format: Expected input format for routing decision.
            **kwargs: Additional arguments for ProcessorBrick.
        """
        # Routers output routing decisions, not data
        super().__init__(
            input_format=input_format,
            output_format=None,  # Routers don't transform data
            stream_support=False,  # Routers need complete data for decisions
            **kwargs,
        )
        self.available_routes = available_routes or []
        self.default_route = default_route

    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        """Execute the router brick to make a routing decision.

        Args:
            context: Execution context containing input data.

        Returns:
            RoutingDecision for the graph executor.
        """
        # Get available routes from graph if not set
        if not self.available_routes and hasattr(context, "graph"):
            # Get successor nodes from current node
            # This would be set by the graph executor
            self.available_routes = context.metadata.get("available_routes", [])

        # Get input data
        input_data = context.data.get("input")
        if input_data is None and context.brick_outputs:
            input_data = list(context.brick_outputs.values())[-1]

        if input_data is None:
            # No data, use default route
            return self._create_routing_decision(
                self.default_route,
                reason="No input data available",
            )

        # Create processing context with available routes
        proc_context = ProcessingContext(
            input_format=self.input_format,
            output_format=None,
            mode=ProcessingMode.SYNC,
            available_routes=self.available_routes,
            processing_metadata=context.metadata,
        )

        # Compute route
        route_decision = await self.compute_route(input_data, proc_context)

        # Validate and convert to core RoutingDecision
        return self._create_routing_decision(
            route_decision.target_node,
            reason=route_decision.reason,
            metadata=route_decision.metadata,
            should_terminate=route_decision.should_terminate,
        )

    @abstractmethod
    async def compute_route(
        self,
        data: DataType,
        context: ProcessingContext,  # noqa: ARG002
    ) -> RouteDecision:
        """Compute the routing decision based on input data.

        Args:
            data: Input data for routing decision.
            context: Processing context with available routes.

        Returns:
            RouteDecision with target node and metadata.
        """
        pass

    async def process_data(
        self,
        data: DataType,
        context: ProcessingContext,
    ) -> Any:
        """Process data for routing (converts to routing decision).

        Args:
            data: Input data.
            context: Processing context.

        Returns:
            RouteDecision (not transformed data).
        """
        return await self.compute_route(data, context)

    def _create_routing_decision(
        self,
        target_node: str | None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
        should_terminate: bool = False,
    ) -> RoutingDecision:
        """Create a core RoutingDecision from route decision.

        Args:
            target_node: Target node ID.
            reason: Reason for the decision.
            metadata: Additional metadata.
            should_terminate: Whether to terminate execution.

        Returns:
            Core RoutingDecision object.
        """
        # Validate target node if available routes are known
        if (
            target_node
            and self.available_routes
            and target_node not in self.available_routes
        ):
            # Log warning but allow it (graph will handle validation)
            metadata = metadata or {}
            metadata["warning"] = f"Target node '{target_node}' not in available routes"

        return RoutingDecision(
            next_node_id=target_node,
            metadata={
                "router_id": self.id,
                "reason": reason,
                **(metadata or {}),
            },
            should_terminate=should_terminate,
        )


class ConditionalRouter(RouterBrick):
    """Router that makes decisions based on conditions.

    Example:
        >>> router = ConditionalRouter(
        ...     conditions={
        ...         "error": lambda d: d.get("status") == "error",
        ...         "retry": lambda d: d.get("retry_count", 0) < 3,
        ...     },
        ...     routes={
        ...         "error": "error_handler",
        ...         "retry": "retry_node",
        ...     },
        ...     default_route="success_node"
        ... )
    """

    def __init__(
        self,
        conditions: dict[str, Any],
        routes: dict[str, str],
        default_route: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the conditional router.

        Args:
            conditions: Dictionary of condition name to callable.
            routes: Dictionary of condition name to target node.
            default_route: Default node if no conditions match.
            **kwargs: Additional arguments for RouterBrick.
        """
        super().__init__(default_route=default_route, **kwargs)
        self.conditions = conditions
        self.routes = routes

    async def compute_route(
        self,
        data: DataType,
        context: ProcessingContext,  # noqa: ARG002
    ) -> RouteDecision:
        """Compute route based on conditions.

        Args:
            data: Input data to evaluate.
            context: Processing context.

        Returns:
            RouteDecision based on first matching condition.
        """
        # Evaluate conditions in order
        for name, condition in self.conditions.items():
            try:
                result = condition(data) if callable(condition) else data == condition

                if result:
                    target = self.routes.get(name)
                    if target:
                        return RouteDecision(
                            target_node=target,
                            reason=f"Condition '{name}' matched",
                            metadata={"matched_condition": name},
                        )
            except Exception:
                # Log condition evaluation error
                continue

        # No conditions matched, use default
        return RouteDecision(
            target_node=self.default_route,
            reason="No conditions matched",
            metadata={"evaluated_conditions": list(self.conditions.keys())},
        )


class DataFieldRouter(RouterBrick):
    """Router that routes based on specific data fields.

    Example:
        >>> router = DataFieldRouter(
        ...     field="action",
        ...     field_routes={
        ...         "create": "create_handler",
        ...         "update": "update_handler",
        ...         "delete": "delete_handler",
        ...     },
        ...     default_route="unknown_action"
        ... )
    """

    def __init__(
        self,
        field: str,
        field_routes: dict[str, str],
        default_route: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the data field router.

        Args:
            field: Field name to extract from data.
            field_routes: Mapping of field values to target nodes.
            default_route: Default node if field not found or no match.
            **kwargs: Additional arguments for RouterBrick.
        """
        super().__init__(default_route=default_route, **kwargs)
        self.field = field
        self.field_routes = field_routes

    async def compute_route(
        self,
        data: DataType,
        context: ProcessingContext,  # noqa: ARG002
    ) -> RouteDecision:
        """Compute route based on data field value.

        Args:
            data: Input data containing the field.
            context: Processing context.

        Returns:
            RouteDecision based on field value.
        """
        # Extract field value
        field_value = None

        if isinstance(data, dict):
            field_value = data.get(self.field)
        elif hasattr(data, self.field):
            field_value = getattr(data, self.field)
        elif hasattr(data, "get"):
            field_value = data.get(self.field)

        # Find matching route
        if field_value is not None:
            target = self.field_routes.get(str(field_value))
            if target:
                return RouteDecision(
                    target_node=target,
                    reason=f"Field '{self.field}' = '{field_value}'",
                    metadata={
                        "field": self.field,
                        "value": field_value,
                    },
                )

        # No match or field not found
        return RouteDecision(
            target_node=self.default_route,
            reason=f"Field '{self.field}' not found or no matching route",
            metadata={
                "field": self.field,
                "value": field_value,
                "available_routes": list(self.field_routes.keys()),
            },
        )


class WeightedRouter(RouterBrick):
    """Router that makes probabilistic routing decisions.

    Example:
        >>> router = WeightedRouter(
        ...     weights={
        ...         "fast_path": 0.7,
        ...         "thorough_path": 0.2,
        ...         "experimental_path": 0.1,
        ...     }
        ... )
    """

    def __init__(
        self,
        weights: dict[str, float],
        seed: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the weighted router.

        Args:
            weights: Dictionary of node to weight (must sum to 1.0).
            seed: Random seed for reproducibility.
            **kwargs: Additional arguments for RouterBrick.
        """
        super().__init__(**kwargs)

        # Normalize weights
        total = sum(weights.values())
        self.weights = {k: v / total for k, v in weights.items()}

        # Setup random state
        import random

        self.rng = random.Random(seed)

    async def compute_route(
        self,
        data: DataType,  # noqa: ARG002
        context: ProcessingContext,  # noqa: ARG002
    ) -> RouteDecision:
        """Compute route based on weighted probability.

        Args:
            data: Input data (not used for decision).
            context: Processing context.

        Returns:
            RouteDecision based on weighted random selection.
        """
        # Random selection based on weights
        rand_val = self.rng.random()
        cumulative = 0.0

        for node, weight in self.weights.items():
            cumulative += weight
            if rand_val <= cumulative:
                return RouteDecision(
                    target_node=node,
                    reason=f"Weighted selection (p={weight:.2f})",
                    metadata={
                        "weight": weight,
                        "random_value": rand_val,
                    },
                )

        # Shouldn't reach here, but use first node as fallback
        first_node = list(self.weights.keys())[0]
        return RouteDecision(
            target_node=first_node,
            reason="Fallback selection",
        )
