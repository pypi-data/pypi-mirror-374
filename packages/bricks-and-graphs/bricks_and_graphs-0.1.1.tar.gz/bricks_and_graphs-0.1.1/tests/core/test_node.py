"""Tests for AgentNode class."""

from __future__ import annotations

from typing import Any

import pytest

from bag.core import (
    AgentBrick,
    AgentNode,
    BrickType,
    ExecutionContext,
    MultipleRouterBricksError,
    RoutingDecision,
)


class NodeTestBrick(AgentBrick):
    """Simple test brick."""

    def __init__(
        self,
        result: Any = None,
        brick_type: BrickType = BrickType.PROCESSOR,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.result = result
        self.BRICK_TYPE = brick_type

    async def execute(self, context: ExecutionContext) -> Any:
        return self.result


class NodeTestRouterBrick(AgentBrick):
    """Test router brick."""

    BRICK_TYPE = BrickType.ROUTER

    def __init__(self, next_node: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.next_node = next_node

    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        return RoutingDecision(
            next_node_id=self.next_node,
            metadata={"source": "test_router"},
        )


def test_node_creation():
    """Test basic node creation."""
    node = AgentNode(node_id="test_node", name="Test Node")

    assert node.id == "test_node"
    assert node.name == "Test Node"
    assert node.bricks == []
    assert node.metadata == {}
    assert node.graph is None


def test_node_auto_id():
    """Test automatic ID generation."""
    node = AgentNode()

    assert node.id.startswith("node_")
    assert node.name.startswith("Node_")


def test_add_brick():
    """Test adding bricks to node."""
    node = AgentNode()
    brick1 = NodeTestBrick(result="test1", brick_id="b1")
    brick2 = NodeTestBrick(result="test2", brick_id="b2")

    node.add_brick(brick1)
    node.add_brick(brick2)

    assert len(node.bricks) == 2
    assert node.bricks[0] == brick1
    assert node.bricks[1] == brick2


def test_remove_brick():
    """Test removing brick from node."""
    node = AgentNode()
    brick1 = NodeTestBrick(brick_id="b1")
    brick2 = NodeTestBrick(brick_id="b2")

    node.add_brick(brick1)
    node.add_brick(brick2)

    # Remove existing brick
    assert node.remove_brick("b1") is True
    assert len(node.bricks) == 1
    assert node.bricks[0] == brick2

    # Remove non-existent brick
    assert node.remove_brick("b3") is False
    assert len(node.bricks) == 1


def test_get_brick():
    """Test getting brick by ID."""
    node = AgentNode()
    brick1 = NodeTestBrick(brick_id="b1")
    brick2 = NodeTestBrick(brick_id="b2")

    node.add_brick(brick1)
    node.add_brick(brick2)

    assert node.get_brick("b1") == brick1
    assert node.get_brick("b2") == brick2
    assert node.get_brick("b3") is None


def test_router_brick_property():
    """Test router brick detection."""
    node = AgentNode()

    # No bricks
    assert node.router_brick is None
    assert node.has_router is False

    # Only processor bricks
    node.add_brick(NodeTestBrick(brick_id="b1"))
    node.add_brick(NodeTestBrick(brick_id="b2"))
    assert node.router_brick is None
    assert node.has_router is False

    # Router brick at the end
    router = NodeTestRouterBrick(next_node="next", brick_id="router")
    node.add_brick(router)
    assert node.router_brick == router
    assert node.has_router is True


@pytest.mark.asyncio
async def test_node_execution():
    """Test node execution."""
    node = AgentNode(node_id="test_node")
    brick1 = NodeTestBrick(result="result1", brick_id="b1")
    brick2 = NodeTestBrick(result={"data": "result2"}, brick_id="b2")

    node.add_brick(brick1)
    node.add_brick(brick2)

    context = ExecutionContext()
    outputs, routing = await node.execute(context)

    # Check outputs
    assert outputs["b1"] == "result1"
    assert outputs["b2"] == {"data": "result2"}

    # Check no routing decision
    assert routing is None

    # Check context updates
    assert "test_node" in context.visited_nodes
    assert context.brick_outputs["b1"] == "result1"
    assert context.brick_outputs["b2"] == {"data": "result2"}
    assert context.node_outputs["test_node"] == outputs


@pytest.mark.asyncio
async def test_node_execution_with_router():
    """Test node execution with router brick."""
    node = AgentNode(node_id="test_node")
    brick1 = NodeTestBrick(result="data", brick_id="b1")
    router = NodeTestRouterBrick(next_node="next_node", brick_id="router")

    node.add_brick(brick1)
    node.add_brick(router)

    context = ExecutionContext()
    outputs, routing = await node.execute(context)

    # Check routing decision
    assert routing is not None
    assert routing.next_node_id == "next_node"
    assert routing.metadata["source"] == "test_router"

    # Check outputs include router output
    assert outputs["router"] == routing


def test_node_validate_empty():
    """Test validation of empty node."""
    node = AgentNode(node_id="empty_node")
    errors = node.validate()

    assert len(errors) == 1
    assert "no bricks" in errors[0]


def test_node_validate_valid():
    """Test validation of valid node."""
    node = AgentNode()
    node.add_brick(NodeTestBrick())

    errors = node.validate()
    assert errors == []


def test_node_validate_router_position():
    """Test validation of router brick position."""
    node = AgentNode(node_id="test")

    # Router not at the end
    router = NodeTestRouterBrick(brick_id="r1")
    processor = NodeTestBrick(brick_id="p1")

    node.add_brick(router)
    node.add_brick(processor)

    errors = node.validate()
    assert len(errors) == 1
    assert "not at the end" in errors[0]


def test_node_validate_multiple_routers():
    """Test validation with multiple router bricks."""
    node = AgentNode(node_id="test")

    router1 = NodeTestRouterBrick(brick_id="r1")
    router2 = NodeTestRouterBrick(brick_id="r2")

    node.add_brick(router1)
    node.add_brick(router2)

    # Should raise MultipleRouterBricksError
    with pytest.raises(MultipleRouterBricksError) as exc_info:
        node.validate()

    assert exc_info.value.node_id == "test"
    assert exc_info.value.router_count == 2


def test_node_repr():
    """Test string representation."""
    node = AgentNode(node_id="test_123", name="My Node")
    node.add_brick(NodeTestBrick())

    repr_str = repr(node)
    assert "AgentNode" in repr_str
    assert "test_123" in repr_str
    assert "My Node" in repr_str
    assert "1 bricks" in repr_str

    # Add router
    node.add_brick(NodeTestRouterBrick())
    repr_str = repr(node)
    assert "2 bricks" in repr_str
    assert "with router" in repr_str


def test_node_metadata():
    """Test node metadata."""
    metadata = {"version": "1.0", "tags": ["test", "example"]}
    node = AgentNode(metadata=metadata)

    assert node.metadata == metadata
    assert node.metadata["version"] == "1.0"
    assert "test" in node.metadata["tags"]


def test_node_graph_reference():
    """Test graph reference setting."""
    from bag.core import AgentGraph

    node = AgentNode()
    graph = AgentGraph()

    assert node.graph is None

    node.graph = graph
    assert node.graph == graph
