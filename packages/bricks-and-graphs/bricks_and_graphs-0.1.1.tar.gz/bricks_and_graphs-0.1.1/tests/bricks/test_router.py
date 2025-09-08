"""Tests for RouterBrick implementation."""

from __future__ import annotations

from typing import Any

import pytest

from bag.bricks import (
    ConditionalRouter,
    DataFieldRouter,
    ProcessingContext,
    RouteDecision,
    RouterBrick,
    WeightedRouter,
)
from bag.core import ExecutionContext, RoutingDecision


class SimpleRouter(RouterBrick):
    """Simple test router."""

    async def compute_route(
        self, data: Any, context: ProcessingContext
    ) -> RouteDecision:
        """Route based on data type."""
        if isinstance(data, dict):
            return RouteDecision(target_node="dict_handler")
        elif isinstance(data, list):
            return RouteDecision(target_node="list_handler")
        else:
            return RouteDecision(target_node="default_handler")


class TestRouterBrick:
    """Tests for RouterBrick base class."""

    def test_router_creation(self):
        """Test creating a router brick."""
        router = SimpleRouter(
            available_routes=["dict_handler", "list_handler", "default_handler"],
            default_route="default_handler",
            brick_id="test_router",
        )

        assert router.available_routes == [
            "dict_handler",
            "list_handler",
            "default_handler",
        ]
        assert router.default_route == "default_handler"
        assert router.id == "test_router"
        assert router.brick_type.name == "ROUTER"
        assert router.stream_support is False

    @pytest.mark.asyncio
    async def test_router_execution(self):
        """Test router execution with different data types."""
        router = SimpleRouter()

        # Test with dict data
        context = ExecutionContext(data={"input": {"key": "value"}})
        result = await router.execute(context)

        assert isinstance(result, RoutingDecision)
        assert result.next_node_id == "dict_handler"
        assert result.metadata["router_id"] == router.id

        # Test with list data
        context = ExecutionContext(data={"input": [1, 2, 3]})
        result = await router.execute(context)
        assert result.next_node_id == "list_handler"

        # Test with other data
        context = ExecutionContext(data={"input": "string"})
        result = await router.execute(context)
        assert result.next_node_id == "default_handler"

    @pytest.mark.asyncio
    async def test_router_with_brick_outputs(self):
        """Test router getting input from previous brick outputs."""
        router = SimpleRouter()
        context = ExecutionContext(brick_outputs={"prev_brick": {"type": "dict"}})

        result = await router.execute(context)
        assert result.next_node_id == "dict_handler"

    @pytest.mark.asyncio
    async def test_router_no_data_uses_default(self):
        """Test router uses default route when no data available."""
        router = SimpleRouter(default_route="fallback")
        assert router.default_route == "fallback"
        context = ExecutionContext()

        result = await router.execute(context)
        assert result.next_node_id == "fallback"
        assert "No input data available" in result.metadata["reason"]

    @pytest.mark.asyncio
    async def test_router_validation_warning(self):
        """Test router adds warning for invalid target nodes."""
        router = SimpleRouter(
            available_routes=["valid_node"], default_route="valid_node"
        )

        context = ExecutionContext(data={"input": {"key": "value"}})
        result = await router.execute(context)

        # dict_handler is not in available routes
        assert "warning" in result.metadata
        assert "not in available routes" in result.metadata["warning"]

    @pytest.mark.asyncio
    async def test_routing_decision_creation(self):
        """Test creating routing decisions with metadata."""
        SimpleRouter()

        # Test with termination
        class TerminatingRouter(RouterBrick):
            async def compute_route(
                self, data: Any, context: ProcessingContext
            ) -> RouteDecision:
                return RouteDecision(
                    target_node=None, should_terminate=True, reason="End of processing"
                )

        term_router = TerminatingRouter()
        context = ExecutionContext(data={"input": "data"})
        result = await term_router.execute(context)

        assert result.should_terminate is True
        assert result.next_node_id is None
        assert result.metadata["reason"] == "End of processing"


class TestConditionalRouter:
    """Tests for ConditionalRouter."""

    def test_conditional_router_creation(self):
        """Test creating a conditional router."""
        router = ConditionalRouter(
            conditions={
                "is_error": lambda d: d.get("status") == "error",
                "is_success": lambda d: d.get("status") == "success",
            },
            routes={
                "is_error": "error_handler",
                "is_success": "success_handler",
            },
            default_route="unknown_handler",
        )

        assert len(router.conditions) == 2
        assert len(router.routes) == 2
        assert router.default_route == "unknown_handler"

    @pytest.mark.asyncio
    async def test_condition_matching(self):
        """Test routing based on conditions."""
        router = ConditionalRouter(
            conditions={
                "has_error": lambda d: "error" in d,
                "is_large": lambda d: isinstance(d, dict) and len(d) > 5,
                "is_list": lambda d: isinstance(d, list),
            },
            routes={
                "has_error": "error_node",
                "is_large": "large_processor",
                "is_list": "list_processor",
            },
            default_route="default_node",
        )

        context = ProcessingContext()

        # Test error condition
        result = await router.compute_route({"error": "Something went wrong"}, context)
        assert result.target_node == "error_node"
        assert result.reason == "Condition 'has_error' matched"
        assert result.metadata["matched_condition"] == "has_error"

        # Test list condition
        result = await router.compute_route([1, 2, 3], context)
        assert result.target_node == "list_processor"

        # Test default route
        result = await router.compute_route({"small": "data"}, context)
        assert result.target_node == "default_node"
        assert result.reason == "No conditions matched"
        assert "evaluated_conditions" in result.metadata

    @pytest.mark.asyncio
    async def test_condition_with_simple_values(self):
        """Test conditions with simple equality checks."""
        router = ConditionalRouter(
            conditions={
                "is_prod": "production",
                "is_dev": "development",
            },
            routes={
                "is_prod": "prod_handler",
                "is_dev": "dev_handler",
            },
        )

        context = ProcessingContext()

        # Test equality condition
        result = await router.compute_route("production", context)
        assert result.target_node == "prod_handler"

        result = await router.compute_route("development", context)
        assert result.target_node == "dev_handler"

    @pytest.mark.asyncio
    async def test_condition_evaluation_error(self):
        """Test handling of condition evaluation errors."""

        def bad_condition(data):
            raise ValueError("Condition error")

        router = ConditionalRouter(
            conditions={
                "bad": bad_condition,
                "good": lambda d: True,
            },
            routes={
                "bad": "bad_node",
                "good": "good_node",
            },
            default_route="default",
        )

        context = ProcessingContext()

        # Should skip bad condition and match good one
        result = await router.compute_route({}, context)
        assert result.target_node == "good_node"


class TestDataFieldRouter:
    """Tests for DataFieldRouter."""

    def test_field_router_creation(self):
        """Test creating a field-based router."""
        router = DataFieldRouter(
            field="action",
            field_routes={
                "create": "create_handler",
                "update": "update_handler",
                "delete": "delete_handler",
            },
            default_route="unknown_action",
        )

        assert router.field == "action"
        assert len(router.field_routes) == 3
        assert router.default_route == "unknown_action"

    @pytest.mark.asyncio
    async def test_field_routing_dict(self):
        """Test routing based on dictionary field."""
        router = DataFieldRouter(
            field="action",
            field_routes={
                "create": "create_node",
                "update": "update_node",
                "delete": "delete_node",
            },
            default_route="default_node",
        )

        context = ProcessingContext()

        # Test matching field
        result = await router.compute_route(
            {"action": "create", "data": "..."}, context
        )
        assert result.target_node == "create_node"
        assert result.reason == "Field 'action' = 'create'"
        assert result.metadata["field"] == "action"
        assert result.metadata["value"] == "create"

        # Test non-matching value
        result = await router.compute_route({"action": "read"}, context)
        assert result.target_node == "default_node"

        # Test missing field
        result = await router.compute_route({"other": "data"}, context)
        assert result.target_node == "default_node"
        assert "not found" in result.reason

    @pytest.mark.asyncio
    async def test_field_routing_object(self):
        """Test routing based on object attribute."""
        router = DataFieldRouter(
            field="status",
            field_routes={
                "active": "active_handler",
                "inactive": "inactive_handler",
            },
        )

        # Create mock object with status attribute
        class MockObject:
            def __init__(self, status):
                self.status = status

        context = ProcessingContext()

        obj = MockObject("active")
        result = await router.compute_route(obj, context)
        assert result.target_node == "active_handler"

    @pytest.mark.asyncio
    async def test_field_routing_numeric_values(self):
        """Test routing with numeric field values."""
        router = DataFieldRouter(
            field="code",
            field_routes={
                "200": "success_handler",
                "404": "not_found_handler",
                "500": "error_handler",
            },
        )

        context = ProcessingContext()

        # Numeric values are converted to strings for matching
        result = await router.compute_route({"code": 200}, context)
        assert result.target_node == "success_handler"

        result = await router.compute_route({"code": 404}, context)
        assert result.target_node == "not_found_handler"


class TestWeightedRouter:
    """Tests for WeightedRouter."""

    def test_weighted_router_creation(self):
        """Test creating a weighted router."""
        router = WeightedRouter(
            weights={
                "fast": 0.6,
                "normal": 0.3,
                "slow": 0.1,
            }
        )

        # Weights should be normalized
        assert router.weights["fast"] == 0.6
        assert router.weights["normal"] == 0.3
        assert router.weights["slow"] == 0.1
        assert sum(router.weights.values()) == pytest.approx(1.0)

    def test_weight_normalization(self):
        """Test that weights are normalized to sum to 1."""
        router = WeightedRouter(
            weights={
                "a": 2,
                "b": 2,
                "c": 1,
            }
        )

        # Should normalize to 0.4, 0.4, 0.2
        assert router.weights["a"] == pytest.approx(0.4)
        assert router.weights["b"] == pytest.approx(0.4)
        assert router.weights["c"] == pytest.approx(0.2)

    @pytest.mark.asyncio
    async def test_weighted_routing_deterministic(self):
        """Test weighted routing with fixed seed."""
        router = WeightedRouter(
            weights={
                "option_a": 0.5,
                "option_b": 0.3,
                "option_c": 0.2,
            },
            seed=42,
        )

        context = ProcessingContext()

        # With fixed seed, results should be deterministic
        results = []
        for _ in range(5):
            result = await router.compute_route({}, context)
            results.append(result.target_node)

        # Check we get consistent results with seed
        router2 = WeightedRouter(
            weights={
                "option_a": 0.5,
                "option_b": 0.3,
                "option_c": 0.2,
            },
            seed=42,
        )

        results2 = []
        for _ in range(5):
            result = await router2.compute_route({}, context)
            results2.append(result.target_node)

        assert results == results2

    @pytest.mark.asyncio
    async def test_weighted_routing_distribution(self):
        """Test that weighted routing follows expected distribution."""
        router = WeightedRouter(
            weights={
                "high": 0.7,
                "low": 0.3,
            },
            seed=12345,
        )

        context = ProcessingContext()

        # Run many iterations to check distribution
        counts = {"high": 0, "low": 0}
        iterations = 1000

        for _ in range(iterations):
            result = await router.compute_route({}, context)
            counts[result.target_node] += 1

        # Check distribution is roughly correct (with some tolerance)
        high_ratio = counts["high"] / iterations
        assert 0.65 < high_ratio < 0.75  # Should be around 0.7

    @pytest.mark.asyncio
    async def test_weighted_routing_metadata(self):
        """Test that routing decisions include weight metadata."""
        router = WeightedRouter(weights={"a": 0.8, "b": 0.2}, seed=99)

        context = ProcessingContext()
        result = await router.compute_route({}, context)

        assert "weight" in result.metadata
        assert "random_value" in result.metadata
        assert result.metadata["weight"] in [0.8, 0.2]
