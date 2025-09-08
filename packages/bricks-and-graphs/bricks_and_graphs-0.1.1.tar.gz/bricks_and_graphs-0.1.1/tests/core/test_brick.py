"""Tests for AgentBrick classes."""

from __future__ import annotations

from typing import Any

import pytest

from bag.core import AgentBrick, BrickType, CompositeBrick, ExecutionContext


class SimpleBrick(AgentBrick):
    """Simple test brick implementation."""

    BRICK_TYPE = BrickType.ACTION

    def __init__(
        self,
        value: Any = None,
        brick_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(brick_id, name, metadata)
        self.value = value

    async def execute(self, context: ExecutionContext) -> Any:
        """Execute and return the configured value."""
        return self.value


class ProcessorBrick(AgentBrick):
    """Processor brick that modifies context data."""

    BRICK_TYPE = BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Process and modify context data."""
        # Double all numeric values in context data
        result = {}
        for key, value in context.data.items():
            if isinstance(value, int | float):
                result[key] = value * 2
            else:
                result[key] = value
        return result


@pytest.mark.asyncio
async def test_simple_brick_creation():
    """Test basic brick creation and properties."""
    brick = SimpleBrick(value=42, brick_id="test_brick", name="Test Brick")

    assert brick.id == "test_brick"
    assert brick.name == "Test Brick"
    assert brick.brick_type == BrickType.ACTION
    assert brick.value == 42
    assert isinstance(brick.metadata, dict)


@pytest.mark.asyncio
async def test_brick_auto_id_generation():
    """Test automatic ID generation when not provided."""
    brick = SimpleBrick(value="test")

    assert brick.id.startswith("SimpleBrick_")
    assert len(brick.id) > len("SimpleBrick_")
    assert brick.name == "SimpleBrick"


@pytest.mark.asyncio
async def test_brick_execution():
    """Test brick execution with context."""
    brick = SimpleBrick(value="hello")
    context = ExecutionContext()

    result = await brick.execute(context)
    assert result == "hello"


@pytest.mark.asyncio
async def test_processor_brick_execution():
    """Test processor brick that modifies context."""
    brick = ProcessorBrick()
    context = ExecutionContext(data={"a": 10, "b": 20, "c": "text"})

    result = await brick.execute(context)
    assert result == {"a": 20, "b": 40, "c": "text"}


@pytest.mark.asyncio
async def test_brick_repr():
    """Test string representation of brick."""
    brick = SimpleBrick(brick_id="test_123", name="Test")
    repr_str = repr(brick)

    assert "SimpleBrick" in repr_str
    assert "test_123" in repr_str
    assert "ACTION" in repr_str


@pytest.mark.asyncio
async def test_brick_from_config():
    """Test creating brick from configuration."""
    config = {
        "id": "config_brick",
        "name": "Config Brick",
        "metadata": {"source": "config"},
        "value": "configured_value",
    }

    brick = SimpleBrick.from_config(config)

    assert brick.id == "config_brick"
    assert brick.name == "Config Brick"
    assert brick.metadata == {"source": "config"}
    assert brick.value == "configured_value"


@pytest.mark.asyncio
async def test_composite_brick_creation():
    """Test composite brick creation."""
    brick1 = SimpleBrick(value=1)
    brick2 = SimpleBrick(value=2)
    brick3 = ProcessorBrick()

    composite = CompositeBrick(
        bricks=[brick1, brick2, brick3],
        brick_id="composite_1",
        name="Composite Test",
    )

    assert composite.id == "composite_1"
    assert composite.name == "Composite Test"
    assert len(composite.bricks) == 3
    assert composite.bricks[0] == brick1
    assert composite.bricks[1] == brick2
    assert composite.bricks[2] == brick3


@pytest.mark.asyncio
async def test_composite_brick_execution():
    """Test composite brick executes all sub-bricks."""
    brick1 = SimpleBrick(value="first", brick_id="b1")
    brick2 = SimpleBrick(value="second", brick_id="b2")
    brick3 = ProcessorBrick(brick_id="b3")

    composite = CompositeBrick(bricks=[brick1, brick2, brick3])
    context = ExecutionContext(data={"x": 5})

    result = await composite.execute(context)

    # Check results contain all brick outputs
    assert "b1" in result
    assert "b2" in result
    assert "b3" in result
    assert result["b1"] == "first"
    assert result["b2"] == "second"
    assert result["b3"] == {"x": 10}

    # Check context was updated
    assert context.brick_outputs["b1"] == "first"
    assert context.brick_outputs["b2"] == "second"
    assert context.brick_outputs["b3"] == {"x": 10}


@pytest.mark.asyncio
async def test_brick_metadata():
    """Test brick metadata handling."""
    metadata = {"version": "1.0", "author": "test"}
    brick = SimpleBrick(metadata=metadata)

    assert brick.metadata == metadata
    assert brick.metadata["version"] == "1.0"
    assert brick.metadata["author"] == "test"
