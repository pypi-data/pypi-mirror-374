"""Tests for AgentContext functionality."""

import pytest

from bag.core import AgentContext, AgentGraph, AgentNode, ExecutionContext
from bag.core.brick import AgentBrick
from bag.core.types import BrickType


class ContextTestBrick(AgentBrick):
    """Test brick that uses agent context."""

    def __init__(self, brick_id: str = "test_brick", action: str = "read"):
        super().__init__(brick_id=brick_id, name="Context Test Brick")
        self.action = action

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict:
        """Execute brick logic using agent context."""
        if context.agent_context is None:
            return {"error": "No agent context available"}

        if self.action == "write":
            # Write to agent context using dict-style access
            context.agent_context["test_key"] = "test_value"
            context.agent_context["counter"] = 42
            context.agent_context["nested"] = {"a": 1, "b": [2, 3]}
            return {"action": "wrote to context"}
        elif self.action == "read":
            # Read from agent context
            return {
                "test_key": context.agent_context.get("test_key"),
                "counter": context.agent_context.get("counter"),
                "nested": context.agent_context.get("nested"),
                "missing": context.agent_context.get("missing", "default"),
            }
        elif self.action == "update":
            # Update counter using dict-style access
            current = context.agent_context.get("counter", 0)
            context.agent_context["counter"] = current + 1
            return {"counter": context.agent_context["counter"]}
        else:
            return {"action": self.action}


class TestAgentContext:
    """Test AgentContext functionality."""

    def test_basic_operations(self):
        """Test basic get/set/delete operations."""
        ctx = AgentContext()

        # Test dict-style set and get
        ctx["key1"] = "value1"
        assert ctx["key1"] == "value1"
        assert ctx.get("key1") == "value1"

        # Test default value with get method
        assert ctx.get("nonexistent") is None
        assert ctx.get("nonexistent", "default") == "default"

        # Test 'in' operator
        assert "key1" in ctx
        assert "nonexistent" not in ctx

        # Test dict-style delete
        del ctx["key1"]
        assert "key1" not in ctx
        assert ctx.get("key1") is None

        # Test KeyError on missing key
        with pytest.raises(KeyError):
            _ = ctx["nonexistent"]

    def test_complex_data_types(self):
        """Test storing complex data types."""
        ctx = AgentContext()

        # Store various types using dict-style access
        ctx["list"] = [1, 2, 3]
        ctx["dict"] = {"a": 1, "b": 2}
        ctx["nested"] = {"list": [1, 2], "dict": {"x": "y"}}
        ctx["tuple"] = (1, 2, 3)
        ctx["set"] = {1, 2, 3}

        # Verify retrieval with both methods
        assert ctx["list"] == [1, 2, 3]
        assert ctx.get("dict") == {"a": 1, "b": 2}
        assert ctx["nested"] == {"list": [1, 2], "dict": {"x": "y"}}
        assert ctx.get("tuple") == (1, 2, 3)
        assert ctx["set"] == {1, 2, 3}

    def test_update_method(self):
        """Test the update method."""
        ctx = AgentContext()

        # Initial data using dict-style
        ctx["a"] = 1
        ctx["b"] = 2

        # Update with new data
        ctx.update({"b": 3, "c": 4, "d": {"nested": True}})

        assert ctx["a"] == 1  # Unchanged
        assert ctx["b"] == 3  # Updated
        assert ctx["c"] == 4  # New
        assert ctx["d"] == {"nested": True}  # New complex

    def test_keys_and_clear(self):
        """Test keys listing and clear operations."""
        ctx = AgentContext()

        # Add some data
        ctx["a"] = 1
        ctx["b"] = 2
        ctx["c"] = 3

        # Test keys property
        assert len(ctx.keys) == 3
        assert set(ctx.keys) == {"a", "b", "c"}

        # Test len
        assert len(ctx) == 3

        # Test clear
        ctx.clear()
        assert len(ctx.keys) == 0
        assert len(ctx) == 0
        assert ctx.get("a") is None

    def test_to_dict(self):
        """Test converting context to dictionary."""
        ctx = AgentContext()

        ctx["x"] = 10
        ctx["y"] = 20
        ctx["data"] = {"nested": "value"}

        data = ctx.to_dict()
        assert data == {"x": 10, "y": 20, "data": {"nested": "value"}}

        # Verify it's a copy
        data["x"] = 999
        assert ctx["x"] == 10  # Original unchanged

    def test_repr(self):
        """Test string representation."""
        ctx = AgentContext()
        ctx["key1"] = "value1"
        ctx["key2"] = "value2"

        repr_str = repr(ctx)
        assert "AgentContext" in repr_str
        assert "key1" in repr_str
        assert "key2" in repr_str

    def test_properties(self):
        """Test new properties."""
        ctx = AgentContext()

        # Test is_empty
        assert ctx.is_empty is True

        ctx["a"] = 1
        ctx["b"] = 2
        ctx["c"] = [3, 4, 5]

        assert ctx.is_empty is False

        # Test values property (can't use set with unhashable list)
        values = ctx.values
        assert 1 in values
        assert 2 in values
        assert [3, 4, 5] in values

        # Test items property
        items = ctx.items
        assert len(items) == 3
        assert ("a", 1) in items
        assert ("b", 2) in items

        # Test pop method
        val = ctx.pop("a")
        assert val == 1
        assert "a" not in ctx

        # Pop with default
        val = ctx.pop("nonexistent", "default")
        assert val == "default"


class TestAgentContextInGraph:
    """Test AgentContext integration with graph execution."""

    @pytest.mark.asyncio
    async def test_context_shared_across_nodes(self):
        """Test that agent context is shared across all nodes."""
        graph = AgentGraph()

        # Create nodes that interact with context
        node1 = AgentNode(node_id="writer")
        node1.add_brick(ContextTestBrick(brick_id="write_brick", action="write"))

        node2 = AgentNode(node_id="reader")
        node2.add_brick(ContextTestBrick(brick_id="read_brick", action="read"))

        node3 = AgentNode(node_id="updater")
        node3.add_brick(ContextTestBrick(brick_id="update_brick", action="update"))

        # Add nodes and edges
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        graph.add_edge("writer", "reader")
        graph.add_edge("reader", "updater")

        # Execute graph
        context = await graph.execute()

        # Verify results - node_outputs contains all brick outputs for each node
        writer_outputs = context.node_outputs["writer"]
        assert writer_outputs["write_brick"]["action"] == "wrote to context"

        reader_outputs = context.node_outputs["reader"]
        reader_output = reader_outputs["read_brick"]
        assert reader_output["test_key"] == "test_value"
        assert reader_output["counter"] == 42
        assert reader_output["nested"] == {"a": 1, "b": [2, 3]}
        assert reader_output["missing"] == "default"

        updater_outputs = context.node_outputs["updater"]
        assert updater_outputs["update_brick"]["counter"] == 43  # Incremented

    @pytest.mark.asyncio
    async def test_context_persists_across_executions(self):
        """Test that agent context persists between graph executions."""
        graph = AgentGraph()

        # Create a simple node
        node = AgentNode(node_id="counter")
        node.add_brick(ContextTestBrick(brick_id="counter_brick", action="update"))
        graph.add_node(node)

        # First execution
        context1 = await graph.execute()
        assert context1.node_outputs["counter"]["counter_brick"]["counter"] == 1

        # Second execution - context should persist
        context2 = await graph.execute()
        assert context2.node_outputs["counter"]["counter_brick"]["counter"] == 2

        # Third execution
        context3 = await graph.execute()
        assert context3.node_outputs["counter"]["counter_brick"]["counter"] == 3

    def test_graph_has_agent_context(self):
        """Test that every graph has its own agent context."""
        graph1 = AgentGraph()
        graph2 = AgentGraph()

        # Each graph should have its own context
        assert graph1.agent_context is not graph2.agent_context

        # Test isolation using dict-style access
        graph1.agent_context["key"] = "value1"
        graph2.agent_context["key"] = "value2"

        assert graph1.agent_context["key"] == "value1"
        assert graph2.agent_context["key"] == "value2"

    @pytest.mark.asyncio
    async def test_execution_context_has_agent_context(self):
        """Test that ExecutionContext receives agent context."""
        graph = AgentGraph()

        # Set some data in graph's agent context
        graph.agent_context["pre_execution"] = "data"

        # Create a simple node
        node = AgentNode(node_id="test")

        class VerifyContextBrick(AgentBrick):
            @property
            def brick_type(self) -> BrickType:
                return BrickType.PROCESSOR

            async def execute(self, context: ExecutionContext) -> dict:
                return {
                    "has_agent_context": context.agent_context is not None,
                    "pre_execution_data": (
                        context.agent_context.get("pre_execution")
                        if context.agent_context
                        else None
                    ),
                }

        node.add_brick(VerifyContextBrick(brick_id="verify"))
        graph.add_node(node)

        # Execute
        context = await graph.execute()

        # Verify
        output = context.node_outputs["test"]["verify"]
        assert output["has_agent_context"] is True
        assert output["pre_execution_data"] == "data"
