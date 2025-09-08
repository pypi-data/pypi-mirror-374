"""Tests for type definitions and data structures."""

from __future__ import annotations

from bag.core import (
    BrickType,
    EdgeConfig,
    ExecutionContext,
    GraphConfig,
    GraphDefinition,
    NodeConfig,
    RoutingDecision,
)


def test_brick_type_enum():
    """Test BrickType enum values."""
    assert BrickType.FOUNDATION.value == 1
    assert BrickType.PROMPT.value == 2
    assert BrickType.ACTION.value == 3
    assert BrickType.PROCESSOR.value == 4
    assert BrickType.ROUTER.value == 5

    # Test all members are present
    assert len(BrickType) == 5


def test_execution_context_creation():
    """Test ExecutionContext creation and defaults."""
    context = ExecutionContext()

    assert context.data == {}
    assert context.metadata == {}
    assert context.visited_nodes == []
    assert context.loop_counters == {}
    assert context.brick_outputs == {}
    assert context.node_outputs == {}


def test_execution_context_with_data():
    """Test ExecutionContext with initial data."""
    context = ExecutionContext(
        data={"key": "value"},
        metadata={"version": "1.0"},
    )

    assert context.data["key"] == "value"
    assert context.metadata["version"] == "1.0"


def test_execution_context_extra_fields():
    """Test ExecutionContext allows extra fields."""
    context = ExecutionContext(custom_field="custom_value")
    assert context.custom_field == "custom_value"  # type: ignore


def test_execution_context_mutations():
    """Test ExecutionContext field mutations."""
    context = ExecutionContext()

    # Mutate fields
    context.data["new_key"] = "new_value"
    context.visited_nodes.append("node1")
    context.loop_counters["node1"] = 1

    assert context.data["new_key"] == "new_value"
    assert "node1" in context.visited_nodes
    assert context.loop_counters["node1"] == 1


def test_routing_decision_creation():
    """Test RoutingDecision creation."""
    # Basic routing
    decision = RoutingDecision(next_node_id="next_node")
    assert decision.next_node_id == "next_node"
    assert decision.metadata == {}
    assert decision.should_terminate is False

    # With metadata
    decision = RoutingDecision(
        next_node_id="node2",
        metadata={"reason": "condition_met"},
    )
    assert decision.metadata["reason"] == "condition_met"

    # Termination
    decision = RoutingDecision(
        next_node_id=None,
        should_terminate=True,
    )
    assert decision.next_node_id is None
    assert decision.should_terminate is True


def test_graph_config_defaults():
    """Test GraphConfig default values."""
    config = GraphConfig()

    assert config.max_iterations == 100
    assert config.max_loop_count == 10
    assert config.enable_async is True
    assert config.debug is False


def test_graph_config_custom():
    """Test GraphConfig with custom values."""
    config = GraphConfig(
        max_iterations=50,
        max_loop_count=5,
        enable_async=False,
        debug=True,
    )

    assert config.max_iterations == 50
    assert config.max_loop_count == 5
    assert config.enable_async is False
    assert config.debug is True


def test_node_config():
    """Test NodeConfig creation."""
    # Minimal config
    config = NodeConfig(id="node1")
    assert config.id == "node1"
    assert config.name is None
    assert config.brick_configs == []
    assert config.metadata == {}

    # Full config
    config = NodeConfig(
        id="node2",
        name="Test Node",
        brick_configs=[
            {"type": "TestBrick", "value": 1},
            {"type": "RouterBrick", "route": "next"},
        ],
        metadata={"priority": "high"},
    )

    assert config.id == "node2"
    assert config.name == "Test Node"
    assert len(config.brick_configs) == 2
    assert config.brick_configs[0]["type"] == "TestBrick"
    assert config.metadata["priority"] == "high"


def test_edge_config():
    """Test EdgeConfig creation."""
    # Basic edge
    edge = EdgeConfig(source="n1", target="n2")
    assert edge.source == "n1"
    assert edge.target == "n2"
    assert edge.metadata == {}

    # With metadata
    edge = EdgeConfig(
        source="start",
        target="end",
        metadata={"weight": 1.5, "condition": "always"},
    )
    assert edge.metadata["weight"] == 1.5
    assert edge.metadata["condition"] == "always"


def test_graph_definition():
    """Test GraphDefinition creation."""
    # Create nodes
    nodes = [
        NodeConfig(id="n1", name="Node 1"),
        NodeConfig(id="n2", name="Node 2"),
    ]

    # Create edges
    edges = [
        EdgeConfig(source="n1", target="n2", metadata={"label": "next"}),
    ]

    # Create definition
    definition = GraphDefinition(
        nodes=nodes,
        edges=edges,
        config=GraphConfig(max_iterations=50),
        metadata={"author": "test", "version": "1.0"},
    )

    assert len(definition.nodes) == 2
    assert len(definition.edges) == 1
    assert definition.config.max_iterations == 50
    assert definition.metadata["author"] == "test"
    assert definition.metadata["version"] == "1.0"


def test_graph_definition_defaults():
    """Test GraphDefinition with minimal data."""
    definition = GraphDefinition(nodes=[], edges=[])

    assert definition.nodes == []
    assert definition.edges == []
    assert isinstance(definition.config, GraphConfig)
    assert definition.config.max_iterations == 100  # default
    assert definition.metadata == {}
