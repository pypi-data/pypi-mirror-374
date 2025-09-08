"""Tests for validation logic in nodes and graphs."""

from typing import Any

import pytest

from bag.core import (
    AgentBrick,
    AgentGraph,
    AgentNode,
    BrickType,
    ExecutionContext,
    MultipleRouterBricksError,
    NoExitPathError,
    RoutingDecision,
)


class ValidTestBrick(AgentBrick):
    """Simple test brick for validation tests."""

    def __init__(self, brick_id: str, brick_type: BrickType):
        super().__init__(brick_id=brick_id, name=f"Test {brick_type.name}")
        self._brick_type = brick_type

    @property
    def brick_type(self) -> BrickType:
        return self._brick_type

    async def execute(self, context: ExecutionContext) -> Any:
        if self.brick_type == BrickType.ROUTER:
            return RoutingDecision(next_node_id="next")
        return {"result": "test"}


class TestNodeValidation:
    """Test node validation logic."""

    def test_node_with_single_router_brick(self):
        """Test that a node with one router brick validates successfully."""
        node = AgentNode(node_id="test")
        node.add_brick(ValidTestBrick("prompt1", BrickType.PROMPT))
        node.add_brick(ValidTestBrick("processor1", BrickType.PROCESSOR))
        node.add_brick(ValidTestBrick("router1", BrickType.ROUTER))

        # Should validate without errors
        errors = node.validate()
        assert errors == []

    def test_node_with_multiple_router_bricks_raises_exception(self):
        """Test that a node with multiple router bricks raises exception."""
        node = AgentNode(node_id="test")
        node.add_brick(ValidTestBrick("router1", BrickType.ROUTER))
        node.add_brick(ValidTestBrick("router2", BrickType.ROUTER))

        # Should raise MultipleRouterBricksError
        with pytest.raises(MultipleRouterBricksError) as exc_info:
            node.validate()

        assert exc_info.value.node_id == "test"
        assert exc_info.value.router_count == 2
        assert "contains 2 router bricks" in str(exc_info.value)

    def test_node_with_router_not_at_end(self):
        """Test that a router brick not at the end is reported as error."""
        node = AgentNode(node_id="test")
        node.add_brick(ValidTestBrick("router1", BrickType.ROUTER))
        node.add_brick(ValidTestBrick("processor1", BrickType.PROCESSOR))

        errors = node.validate()
        assert len(errors) == 1
        assert "router brick not at the end" in errors[0]

    def test_node_with_no_bricks(self):
        """Test that a node with no bricks is reported as error."""
        node = AgentNode(node_id="test")

        errors = node.validate()
        assert len(errors) == 1
        assert "has no bricks" in errors[0]


class TestGraphValidation:
    """Test graph validation logic."""

    def test_graph_with_cycle_and_exit_path(self):
        """Test that a cycle with an exit path validates successfully."""
        graph = AgentGraph()

        # Create nodes
        node0 = AgentNode(node_id="n0")  # Entry node
        node0.add_brick(ValidTestBrick("router0", BrickType.ROUTER))

        node1 = AgentNode(node_id="n1")
        node1.add_brick(ValidTestBrick("router1", BrickType.ROUTER))

        node2 = AgentNode(node_id="n2")
        node2.add_brick(ValidTestBrick("router2", BrickType.ROUTER))

        node3 = AgentNode(node_id="n3")
        node3.add_brick(ValidTestBrick("processor3", BrickType.PROCESSOR))

        # Add nodes to graph
        graph.add_node(node0)
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)

        # n0 is entry node, leads to cycle
        graph.add_edge("n0", "n1")

        # Create cycle between n1 and n2 with exit to n3
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n1")  # Creates cycle
        graph.add_edge("n2", "n3")  # Exit path from cycle

        # Should validate without errors
        errors = graph.validate()
        assert errors == []

    def test_graph_with_cycle_no_exit_raises_exception(self):
        """Test that a cycle without exit path raises exception."""
        graph = AgentGraph()

        # Create nodes
        node1 = AgentNode(node_id="n1")
        node1.add_brick(ValidTestBrick("router1", BrickType.ROUTER))

        node2 = AgentNode(node_id="n2")
        node2.add_brick(ValidTestBrick("router2", BrickType.ROUTER))

        # Add nodes to graph
        graph.add_node(node1)
        graph.add_node(node2)

        # Create cycle with no exit
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n1")

        # Should raise NoExitPathError
        with pytest.raises(NoExitPathError) as exc_info:
            graph.validate()

        assert set(exc_info.value.cycle_nodes) == {"n1", "n2"}
        assert "no exit path found" in str(exc_info.value)

    def test_graph_validation_propagates_node_exceptions(self):
        """Test that node validation exceptions are propagated."""
        graph = AgentGraph()

        # Create node with multiple router bricks
        node = AgentNode(node_id="n1")
        node.add_brick(ValidTestBrick("router1", BrickType.ROUTER))
        node.add_brick(ValidTestBrick("router2", BrickType.ROUTER))

        graph.add_node(node)

        # Should raise MultipleRouterBricksError from node validation
        with pytest.raises(MultipleRouterBricksError) as exc_info:
            graph.validate()

        assert exc_info.value.node_id == "n1"

    def test_graph_with_no_entry_nodes(self):
        """Test that a graph with no entry nodes is reported as error."""
        graph = AgentGraph()

        # Create nodes
        node1 = AgentNode(node_id="n1")
        node1.add_brick(ValidTestBrick("router1", BrickType.ROUTER))

        node2 = AgentNode(node_id="n2")
        node2.add_brick(ValidTestBrick("router2", BrickType.ROUTER))

        node3 = AgentNode(node_id="n3")
        node3.add_brick(ValidTestBrick("processor3", BrickType.PROCESSOR))

        # Create an isolated node to have valid exit paths
        node4 = AgentNode(node_id="n4")
        node4.add_brick(ValidTestBrick("processor4", BrickType.PROCESSOR))

        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        graph.add_node(node4)

        # Create a cycle where all nodes in cycle have incoming edges
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n3")
        graph.add_edge("n3", "n1")  # Completes cycle, all have incoming edges

        # Add exit paths to avoid NoExitPathError
        graph.add_edge("n1", "n4")  # Exit from cycle
        graph.add_edge("n2", "n4")  # Another exit

        # n4 also needs incoming edge to ensure no entry nodes
        # but we already have edges to n4

        # Should report no entry nodes
        errors = graph.validate()
        assert any("no entry nodes" in error for error in errors)

    @pytest.mark.asyncio
    async def test_execute_validates_graph(self):
        """Test that execute() validates the graph before running."""
        graph = AgentGraph()

        # Create node with multiple router bricks
        node = AgentNode(node_id="n1")
        node.add_brick(ValidTestBrick("router1", BrickType.ROUTER))
        node.add_brick(ValidTestBrick("router2", BrickType.ROUTER))

        graph.add_node(node)

        # Execute should raise validation error
        with pytest.raises(MultipleRouterBricksError):
            await graph.execute()

    @pytest.mark.asyncio
    async def test_execute_with_cycle_no_exit_fails(self):
        """Test that executing a graph with no exit cycle fails."""
        graph = AgentGraph()

        # Create nodes
        node1 = AgentNode(node_id="n1")
        node1.add_brick(ValidTestBrick("router1", BrickType.ROUTER))

        node2 = AgentNode(node_id="n2")
        node2.add_brick(ValidTestBrick("router2", BrickType.ROUTER))

        # Add nodes to graph
        graph.add_node(node1)
        graph.add_node(node2)

        # Create cycle with no exit
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n1")

        # Execute should raise NoExitPathError
        with pytest.raises(NoExitPathError):
            await graph.execute(start_node_id="n1")


class TestComplexGraphValidation:
    """Test validation of more complex graph structures."""

    def test_multiple_cycles_with_mixed_exits(self):
        """Test graph with multiple cycles, some with exits, some without."""
        graph = AgentGraph()

        # Create nodes
        for i in range(5):
            node = AgentNode(node_id=f"n{i}")
            node.add_brick(ValidTestBrick(f"router{i}", BrickType.ROUTER))
            graph.add_node(node)

        # First cycle (n0 -> n1 -> n0) with exit to n2
        graph.add_edge("n0", "n1")
        graph.add_edge("n1", "n0")
        graph.add_edge("n1", "n2")

        # Second cycle (n3 -> n4 -> n3) with no exit
        graph.add_edge("n2", "n3")
        graph.add_edge("n3", "n4")
        graph.add_edge("n4", "n3")

        # Should raise NoExitPathError for the second cycle
        with pytest.raises(NoExitPathError) as exc_info:
            graph.validate()

        assert set(exc_info.value.cycle_nodes) == {"n3", "n4"}

    def test_self_loop_with_exit(self):
        """Test that a self-loop with an exit path validates."""
        graph = AgentGraph()

        node0 = AgentNode(node_id="n0")  # Entry node
        node0.add_brick(ValidTestBrick("router0", BrickType.ROUTER))

        node1 = AgentNode(node_id="n1")
        node1.add_brick(ValidTestBrick("router1", BrickType.ROUTER))

        node2 = AgentNode(node_id="n2")
        node2.add_brick(ValidTestBrick("processor2", BrickType.PROCESSOR))

        graph.add_node(node0)
        graph.add_node(node1)
        graph.add_node(node2)

        # n0 is entry, leads to n1 which has self-loop
        graph.add_edge("n0", "n1")

        # Self-loop with exit
        graph.add_edge("n1", "n1")  # Self-loop
        graph.add_edge("n1", "n2")  # Exit path

        # Should validate successfully
        errors = graph.validate()
        assert errors == []

    def test_self_loop_no_exit(self):
        """Test that a self-loop with no exit raises exception."""
        graph = AgentGraph()

        node = AgentNode(node_id="n1")
        node.add_brick(ValidTestBrick("router1", BrickType.ROUTER))

        graph.add_node(node)

        # Self-loop with no other edges
        graph.add_edge("n1", "n1")

        # Should raise NoExitPathError
        with pytest.raises(NoExitPathError) as exc_info:
            graph.validate()

        assert exc_info.value.cycle_nodes == ["n1"]
