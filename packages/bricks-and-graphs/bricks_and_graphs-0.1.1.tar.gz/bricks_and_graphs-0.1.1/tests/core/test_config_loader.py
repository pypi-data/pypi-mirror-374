"""Tests for configuration loading functionality."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
import yaml

from bag.core import (
    AgentBrick,
    AgentGraph,
    BrickRegistry,
    BrickType,
    ExecutionContext,
    GraphConfig,
    GraphDefinition,
    load_graph,
    load_graph_definition,
    save_graph_definition,
)


class ConfigTestBrick(AgentBrick):
    """Test brick for configuration loading."""

    def __init__(self, test_value: str = "default", **kwargs):
        super().__init__(**kwargs)
        self.test_value = test_value

    async def execute(self, context: ExecutionContext) -> str:
        return self.test_value


class CustomBrick(AgentBrick):
    """Another test brick."""

    BRICK_TYPE = BrickType.ACTION

    def __init__(self, action: str = "test", **kwargs):
        super().__init__(**kwargs)
        self.action = action

    async def execute(self, context: ExecutionContext) -> dict[str, str]:
        return {"action": self.action}


def test_brick_registry():
    """Test BrickRegistry functionality."""
    registry = BrickRegistry()

    # Register brick classes
    registry.register_brick("TestBrick", ConfigTestBrick)
    registry.register_brick("CustomBrick", CustomBrick)

    # Create bricks
    brick1 = registry.create_brick("TestBrick", {"test_value": "hello"})
    assert isinstance(brick1, ConfigTestBrick)
    assert brick1.test_value == "hello"

    brick2 = registry.create_brick("CustomBrick", {"action": "process"})
    assert isinstance(brick2, CustomBrick)
    assert brick2.action == "process"

    # Test unknown brick type
    with pytest.raises(ValueError, match="Unknown brick type"):
        registry.create_brick("UnknownBrick", {})


def test_brick_registry_factory():
    """Test BrickRegistry with custom factory."""
    registry = BrickRegistry()

    # Custom factory
    class TestFactory:
        def create_brick(self, brick_type: str, config: dict[str, Any]) -> AgentBrick:
            if brick_type == "FactoryBrick":
                return ConfigTestBrick(test_value="from_factory", **config)
            raise ValueError(f"Unknown type: {brick_type}")

    registry.register_factory("FactoryBrick", TestFactory())

    brick = registry.create_brick("FactoryBrick", {"name": "test"})
    assert isinstance(brick, ConfigTestBrick)
    assert brick.test_value == "from_factory"
    assert brick.name == "test"


def test_brick_registry_get_dict():
    """Test getting registry as dictionary."""
    registry = BrickRegistry()
    registry.register_brick("TestBrick", ConfigTestBrick)
    registry.register_brick("CustomBrick", CustomBrick)

    reg_dict = registry.get_registry_dict()
    assert len(reg_dict) == 2
    assert reg_dict["TestBrick"] == ConfigTestBrick
    assert reg_dict["CustomBrick"] == CustomBrick


def test_load_graph_definition_from_dict():
    """Test loading graph definition from dictionary."""
    data = {
        "nodes": [
            {
                "id": "node1",
                "name": "First Node",
                "bricks": [
                    {"type": "TestBrick", "test_value": "test1"},
                ],
            },
            {
                "id": "node2",
                "bricks": [],
            },
        ],
        "edges": [
            {"source": "node1", "target": "node2"},
        ],
        "config": {
            "max_iterations": 50,
            "debug": True,
        },
        "metadata": {
            "version": "1.0",
        },
    }

    definition = load_graph_definition(data)

    assert len(definition.nodes) == 2
    assert definition.nodes[0].id == "node1"
    assert definition.nodes[0].name == "First Node"
    assert len(definition.edges) == 1
    assert definition.edges[0].source == "node1"
    assert definition.config.max_iterations == 50
    assert definition.config.debug is True
    assert definition.metadata["version"] == "1.0"


def test_load_graph_definition_from_yaml_string():
    """Test loading graph definition from YAML string."""
    yaml_content = """
nodes:
  - id: start
    name: Start Node
    bricks:
      - type: TestBrick
        test_value: start_value
edges:
  - source: start
    target: end
  - source: start
    target: middle
config:
  max_loop_count: 5
"""

    definition = load_graph_definition(yaml_content)

    assert len(definition.nodes) == 1
    assert definition.nodes[0].id == "start"
    assert len(definition.edges) == 2
    assert definition.config.max_loop_count == 5


def test_load_graph_definition_from_json_string():
    """Test loading graph definition from JSON string."""
    json_content = json.dumps(
        {
            "nodes": [{"id": "n1"}, {"id": "n2"}],
            "edges": [{"source": "n1", "target": "n2"}],
        }
    )

    definition = load_graph_definition(json_content)

    assert len(definition.nodes) == 2
    assert definition.nodes[0].id == "n1"
    assert definition.nodes[1].id == "n2"


def test_load_graph_definition_from_yaml_file():
    """Test loading graph definition from YAML file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(
            {
                "nodes": [{"id": "file_node"}],
                "edges": [],
            },
            f,
        )
        temp_path = Path(f.name)

    try:
        # Load from Path
        definition = load_graph_definition(temp_path)
        assert len(definition.nodes) == 1
        assert definition.nodes[0].id == "file_node"

        # Load from string path
        definition = load_graph_definition(str(temp_path))
        assert len(definition.nodes) == 1
    finally:
        temp_path.unlink()


def test_load_graph_definition_from_json_file():
    """Test loading graph definition from JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "nodes": [{"id": "json_node"}],
                "edges": [],
            },
            f,
        )
        temp_path = Path(f.name)

    try:
        definition = load_graph_definition(temp_path)
        assert len(definition.nodes) == 1
        assert definition.nodes[0].id == "json_node"
    finally:
        temp_path.unlink()


def test_save_graph_definition_yaml():
    """Test saving graph definition to YAML."""
    from bag.core import EdgeConfig, NodeConfig

    definition = GraphDefinition(
        nodes=[NodeConfig(id="n1", name="Node 1")],
        edges=[EdgeConfig(source="n1", target="n2")],
        config=GraphConfig(max_iterations=25),
        metadata={"author": "test"},
    )

    with tempfile.NamedTemporaryFile(mode="r", suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)

    try:
        save_graph_definition(definition, temp_path, format="yaml")

        # Read back and verify
        with open(temp_path) as f:
            data = yaml.safe_load(f)

        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["id"] == "n1"
        assert data["config"]["max_iterations"] == 25
        assert data["metadata"]["author"] == "test"
    finally:
        temp_path.unlink()


def test_save_graph_definition_json():
    """Test saving graph definition to JSON."""
    from bag.core import NodeConfig

    definition = GraphDefinition(
        nodes=[NodeConfig(id="n1")],
        edges=[],
    )

    with tempfile.NamedTemporaryFile(mode="r", suffix=".json", delete=False) as f:
        temp_path = Path(f.name)

    try:
        save_graph_definition(definition, temp_path, format="json")

        # Read back and verify
        with open(temp_path) as f:
            data = json.load(f)

        assert len(data["nodes"]) == 1
        assert data["nodes"][0]["id"] == "n1"
    finally:
        temp_path.unlink()


def test_load_graph():
    """Test loading complete graph with brick registry."""
    registry = BrickRegistry()
    registry.register_brick("TestBrick", ConfigTestBrick)

    graph_data = {
        "metadata": {"id": "test_graph", "name": "Test Graph"},
        "nodes": [
            {
                "id": "n1",
                "bricks": [
                    {"type": "TestBrick", "test_value": "hello", "id": "b1"},
                ],
            },
        ],
        "edges": [],
    }

    graph = load_graph(graph_data, registry)

    assert isinstance(graph, AgentGraph)
    assert graph.id == "test_graph"
    assert graph.name == "Test Graph"
    assert len(graph.nodes) == 1

    node = graph.get_node("n1")
    assert node is not None
    assert len(node.bricks) == 1
    assert isinstance(node.bricks[0], ConfigTestBrick)
    assert node.bricks[0].test_value == "hello"


def test_load_graph_without_registry():
    """Test loading graph without brick registry raises error."""
    graph_data = {
        "nodes": [
            {
                "id": "n1",
                "bricks": [{"type": "TestBrick"}],
            },
        ],
        "edges": [],
    }

    with pytest.raises(NotImplementedError, match="Dynamic brick loading"):
        load_graph(graph_data)


def test_invalid_source_type():
    """Test invalid source type for load_graph_definition."""
    with pytest.raises(ValueError, match="Invalid source type"):
        load_graph_definition(123)  # type: ignore


def test_invalid_save_format():
    """Test invalid format for save_graph_definition."""
    definition = GraphDefinition(nodes=[], edges=[])

    with (
        tempfile.NamedTemporaryFile() as f,
        pytest.raises(ValueError, match="Unknown format"),
    ):
        save_graph_definition(definition, Path(f.name), format="xml")
