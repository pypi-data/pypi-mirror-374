"""Tests for AgentGraph class."""

from __future__ import annotations

import pytest

from bag.core import (
    AgentBrick,
    AgentGraph,
    AgentNode,
    BrickType,
    ExecutionContext,
    GraphConfig,
    NoExitPathError,
    RoutingDecision,
)


class SimpleBrick(AgentBrick):
    """Simple test brick."""

    def __init__(self, value: str = "test", **kwargs):
        super().__init__(**kwargs)
        self.value = value

    async def execute(self, context: ExecutionContext) -> str:
        return self.value


class RouterBrick(AgentBrick):
    """Router brick for testing."""

    BRICK_TYPE = BrickType.ROUTER

    def __init__(self, route_to: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.route_to = route_to

    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        # Simple routing based on context data
        if self.route_to:
            return RoutingDecision(next_node_id=self.route_to)

        # Route based on context
        if context.data.get("route") == "terminate":
            return RoutingDecision(should_terminate=True)

        next_node = context.data.get("next_node")
        return RoutingDecision(next_node_id=next_node)


def test_graph_creation():
    """Test basic graph creation."""
    graph = AgentGraph(graph_id="test_graph", name="Test Graph")

    assert graph.id == "test_graph"
    assert graph.name == "Test Graph"
    assert graph.nodes == {}
    assert graph.entry_nodes == set()
    assert isinstance(graph.config, GraphConfig)


def test_graph_auto_id():
    """Test automatic ID generation."""
    graph = AgentGraph()

    assert graph.id.startswith("graph_")
    assert graph.name.startswith("Graph_")


def test_add_node():
    """Test adding nodes to graph."""
    graph = AgentGraph()
    node1 = AgentNode(node_id="n1")
    node2 = AgentNode(node_id="n2")

    graph.add_node(node1)
    graph.add_node(node2)

    assert len(graph.nodes) == 2
    assert graph.get_node("n1") == node1
    assert graph.get_node("n2") == node2
    assert node1.graph == graph
    assert node2.graph == graph

    # Both are entry nodes (no incoming edges)
    assert graph.entry_nodes == {"n1", "n2"}


def test_remove_node():
    """Test removing nodes from graph."""
    graph = AgentGraph()
    node = AgentNode(node_id="n1")

    graph.add_node(node)
    assert graph.remove_node("n1") is True
    assert len(graph.nodes) == 0
    assert node.graph is None

    # Remove non-existent node
    assert graph.remove_node("n2") is False


def test_add_edge():
    """Test adding edges between nodes."""
    graph = AgentGraph()
    node1 = AgentNode(node_id="n1")
    node2 = AgentNode(node_id="n2")

    graph.add_node(node1)
    graph.add_node(node2)

    graph.add_edge("n1", "n2", metadata={"weight": 1})

    # Check edge exists
    assert graph.get_successors("n1") == ["n2"]
    assert graph.get_predecessors("n2") == ["n1"]

    # n1 is still entry node, n2 is not
    assert graph.entry_nodes == {"n1"}


def test_add_edge_invalid_nodes():
    """Test adding edge with invalid nodes raises error."""
    graph = AgentGraph()
    node = AgentNode(node_id="n1")
    graph.add_node(node)

    with pytest.raises(ValueError, match="Source node"):
        graph.add_edge("invalid", "n1")

    with pytest.raises(ValueError, match="Target node"):
        graph.add_edge("n1", "invalid")


def test_remove_edge():
    """Test removing edges."""
    graph = AgentGraph()
    node1 = AgentNode(node_id="n1")
    node2 = AgentNode(node_id="n2")

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge("n1", "n2")

    assert graph.remove_edge("n1", "n2") is True
    assert graph.get_successors("n1") == []
    assert graph.entry_nodes == {"n1", "n2"}

    # Remove non-existent edge
    assert graph.remove_edge("n1", "n2") is False


def test_find_cycles():
    """Test cycle detection."""
    graph = AgentGraph()

    # Create nodes
    for i in range(4):
        node = AgentNode(node_id=f"n{i}")
        graph.add_node(node)

    # Create a cycle: n0 -> n1 -> n2 -> n0
    graph.add_edge("n0", "n1")
    graph.add_edge("n1", "n2")
    graph.add_edge("n2", "n0")

    # Add non-cycle edge
    graph.add_edge("n2", "n3")

    cycles = graph.find_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"n0", "n1", "n2"}


def test_validate_empty_graph():
    """Test validation of empty graph."""
    graph = AgentGraph()
    errors = graph.validate()

    assert len(errors) == 1
    assert "no nodes" in errors[0]


def test_validate_no_entry_nodes():
    """Test validation when all nodes have incoming edges."""
    graph = AgentGraph()
    node1 = AgentNode(node_id="n1")
    node2 = AgentNode(node_id="n2")

    graph.add_node(node1)
    graph.add_node(node2)

    # Create cycle with no entry
    graph.add_edge("n1", "n2")
    graph.add_edge("n2", "n1")

    # This will raise NoExitPathError because the cycle has no exit
    with pytest.raises(NoExitPathError):
        graph.validate()


def test_validate_cycle_without_exit():
    """Test validation of cycle without exit path."""
    graph = AgentGraph()

    # Create nodes with bricks
    for i in range(3):
        node = AgentNode(node_id=f"n{i}")
        node.add_brick(SimpleBrick())
        graph.add_node(node)

    # Create cycle without exit
    graph.add_edge("n0", "n1")
    graph.add_edge("n1", "n2")
    graph.add_edge("n2", "n0")

    # This will raise NoExitPathError
    with pytest.raises(NoExitPathError):
        graph.validate()


@pytest.mark.asyncio
async def test_simple_execution():
    """Test simple graph execution."""
    graph = AgentGraph()

    # Create a simple linear graph: n1 -> n2
    node1 = AgentNode(node_id="n1")
    node1.add_brick(SimpleBrick(value="node1_output"))
    node1.add_brick(RouterBrick(route_to="n2"))

    node2 = AgentNode(node_id="n2")
    node2.add_brick(SimpleBrick(value="node2_output"))

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge("n1", "n2")

    # Execute
    context = await graph.execute()

    # Check execution order
    assert context.visited_nodes == ["n1", "n2"]

    # Check outputs
    assert "n1" in context.node_outputs
    assert "n2" in context.node_outputs


@pytest.mark.asyncio
async def test_execution_with_loops():
    """Test graph execution with loops."""
    graph = AgentGraph(config=GraphConfig(max_loop_count=3))

    # Create entry node
    node0 = AgentNode(node_id="n0")
    node0.add_brick(SimpleBrick(value="n0"))

    # Create a loop: n1 -> n2 -> n1 (with exit to n3)
    node1 = AgentNode(node_id="n1")
    node1.add_brick(SimpleBrick(value="n1"))

    node2 = AgentNode(node_id="n2")
    node2.add_brick(SimpleBrick(value="n2"))

    node3 = AgentNode(node_id="n3")
    node3.add_brick(SimpleBrick(value="n3"))

    # Router that loops once then exits
    class CountingRouter(AgentBrick):
        BRICK_TYPE = BrickType.ROUTER

        async def execute(self, context: ExecutionContext) -> RoutingDecision:
            count = context.data.get("loop_count", 0)
            context.data["loop_count"] = count + 1

            if count < 1:
                return RoutingDecision(next_node_id="n1")
            else:
                return RoutingDecision(next_node_id="n3")

    node2.add_brick(CountingRouter())

    graph.add_node(node0)
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    # n0 is entry, leads to n1
    graph.add_edge("n0", "n1")
    graph.add_edge("n1", "n2")
    graph.add_edge("n2", "n1")
    graph.add_edge("n2", "n3")

    # Execute
    context = await graph.execute()

    # Should have visited: n0 -> n1 -> n2 -> n1 -> n2 -> n3
    assert "n0" in context.visited_nodes
    assert "n1" in context.visited_nodes
    assert "n2" in context.visited_nodes
    assert "n3" in context.visited_nodes
    assert context.visited_nodes == ["n0", "n1", "n2", "n1", "n2", "n3"]
    assert context.data["loop_count"] == 2


@pytest.mark.asyncio
async def test_execution_max_iterations():
    """Test max iterations limit."""
    graph = AgentGraph(config=GraphConfig(max_iterations=5))

    # Create entry node
    node0 = AgentNode(node_id="n0")
    node0.add_brick(SimpleBrick())
    node0.add_brick(RouterBrick(route_to="n1"))

    # Create infinite loop with exit path (required by validation)
    node1 = AgentNode(node_id="n1")
    node1.add_brick(SimpleBrick())
    node1.add_brick(RouterBrick(route_to="n1"))

    # Add a dummy exit node to satisfy validation
    node2 = AgentNode(node_id="n2")
    node2.add_brick(SimpleBrick())

    graph.add_node(node0)
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge("n0", "n1")
    graph.add_edge("n1", "n1")
    graph.add_edge("n1", "n2")  # Exit path (never taken due to router)

    with pytest.raises(RuntimeError, match="Exceeded maximum iterations"):
        await graph.execute()


def test_graph_repr():
    """Test string representation."""
    graph = AgentGraph(graph_id="g1", name="MyGraph")

    node1 = AgentNode(node_id="n1")
    node2 = AgentNode(node_id="n2")

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_edge("n1", "n2")

    repr_str = repr(graph)
    assert "AgentGraph" in repr_str
    assert "g1" in repr_str
    assert "MyGraph" in repr_str
    assert "nodes=2" in repr_str
    assert "edges=1" in repr_str


def test_graph_to_dict():
    """Test graph serialization to dictionary."""
    graph = AgentGraph(graph_id="g1", name="TestGraph")

    node = AgentNode(node_id="n1", name="Node1")
    node.add_brick(SimpleBrick(brick_id="b1", name="Brick1"))

    graph.add_node(node)

    data = graph.to_dict()

    assert data["id"] == "g1"
    assert data["name"] == "TestGraph"
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["id"] == "n1"
    assert len(data["nodes"][0]["bricks"]) == 1
    assert data["edges"] == []
