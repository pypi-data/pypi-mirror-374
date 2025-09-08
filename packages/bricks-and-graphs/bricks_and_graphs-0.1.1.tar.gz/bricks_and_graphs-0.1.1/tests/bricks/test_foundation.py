"""Tests for foundation brick implementations."""

import pytest

from bag.bricks.foundation import (
    ComputedFoundationBrick,
    ContextFoundationBrick,
    DataFoundationBrick,
    FoundationBrick,
)
from bag.core import AgentContext, BrickType, ExecutionContext


class TestFoundationBrick:
    """Test the base FoundationBrick class."""

    def test_brick_type(self):
        """Test that FoundationBrick has the correct brick type."""

        class ConcreteFoundationBrick(FoundationBrick):
            async def execute(self, context):
                return {"test": "data"}

        brick = ConcreteFoundationBrick()
        assert brick.brick_type == BrickType.FOUNDATION

    def test_initialization(self):
        """Test FoundationBrick initialization."""

        class ConcreteFoundationBrick(FoundationBrick):
            async def execute(self, context):
                return {"test": "data"}

        brick = ConcreteFoundationBrick(
            brick_id="test_foundation",
            name="Test Foundation",
            metadata={"key": "value"},
        )

        assert brick.id == "test_foundation"
        assert brick.name == "Test Foundation"
        assert brick.metadata == {"key": "value"}


class TestDataFoundationBrick:
    """Test DataFoundationBrick implementation."""

    @pytest.mark.asyncio
    async def test_execute_with_default_key(self):
        """Test executing DataFoundationBrick with default context key."""
        test_data = {"user_id": 123, "preferences": {"theme": "dark"}}
        brick = DataFoundationBrick(data=test_data)

        context = ExecutionContext()
        context.agent_context = AgentContext()

        result = await brick.execute(context)

        # Check return value
        assert result["data"] == test_data
        assert result["context_key"] == "foundation_data"
        assert "Foundation data stored" in result["message"]

        # Check that data was stored in context
        assert context.agent_context["foundation_data"] == test_data

    @pytest.mark.asyncio
    async def test_execute_with_custom_key(self):
        """Test executing DataFoundationBrick with custom context key."""
        test_data = {"config": {"api_url": "https://api.example.com"}}
        brick = DataFoundationBrick(data=test_data, context_key="custom_config")

        context = ExecutionContext()
        context.agent_context = AgentContext()

        result = await brick.execute(context)

        # Check return value
        assert result["data"] == test_data
        assert result["context_key"] == "custom_config"

        # Check that data was stored under custom key
        assert context.agent_context["custom_config"] == test_data
        assert "foundation_data" not in context.agent_context


class TestContextFoundationBrick:
    """Test ContextFoundationBrick implementation."""

    @pytest.mark.asyncio
    async def test_execute_with_existing_keys(self):
        """Test extracting existing keys from context."""
        brick = ContextFoundationBrick(
            source_keys=["user_data", "session_info"],
            target_key="extracted_foundation",
        )

        context = ExecutionContext()
        context.agent_context = AgentContext()
        context.agent_context["user_data"] = {"id": 456, "name": "Alice"}
        context.agent_context["session_info"] = {"token": "abc123"}
        context.agent_context["other_data"] = {"should": "not_be_extracted"}

        result = await brick.execute(context)

        # Check return value
        expected_data = {
            "user_data": {"id": 456, "name": "Alice"},
            "session_info": {"token": "abc123"},
        }
        assert result["extracted_data"] == expected_data
        assert result["missing_keys"] == []
        assert result["target_key"] == "extracted_foundation"
        assert "Extracted 2 items" in result["message"]

        # Check that extracted data was stored
        assert context.agent_context["extracted_foundation"] == expected_data

    @pytest.mark.asyncio
    async def test_execute_with_missing_keys(self):
        """Test extracting keys when some are missing."""
        brick = ContextFoundationBrick(
            source_keys=["existing_key", "missing_key"],
            target_key="partial_extraction",
        )

        context = ExecutionContext()
        context.agent_context = AgentContext()
        context.agent_context["existing_key"] = {"value": "present"}

        result = await brick.execute(context)

        # Check return value
        expected_data = {"existing_key": {"value": "present"}}
        assert result["extracted_data"] == expected_data
        assert result["missing_keys"] == ["missing_key"]
        assert result["target_key"] == "partial_extraction"

        # Check that partial data was stored
        assert context.agent_context["partial_extraction"] == expected_data


class TestComputedFoundationBrick:
    """Test ComputedFoundationBrick implementation."""

    @pytest.mark.asyncio
    async def test_execute_with_computation(self):
        """Test executing ComputedFoundationBrick with computation function."""

        def compute_function(context):
            # Simple computation based on context
            return {
                "computed_value": 42,
                "timestamp": "2024-01-01T00:00:00Z",
                "context_keys": list(context.agent_context.keys),
            }

        brick = ComputedFoundationBrick(
            compute_fn=compute_function,
            context_key="computed_foundation",
        )

        context = ExecutionContext()
        context.agent_context = AgentContext()
        context.agent_context["existing_data"] = "test"

        result = await brick.execute(context)

        # Check return value
        expected_computed = {
            "computed_value": 42,
            "timestamp": "2024-01-01T00:00:00Z",
            "context_keys": ["existing_data"],
        }
        assert result["computed_data"] == expected_computed
        assert result["context_key"] == "computed_foundation"
        assert "Computed foundation data stored" in result["message"]

        # Check that computed data was stored
        assert context.agent_context["computed_foundation"] == expected_computed

    @pytest.mark.asyncio
    async def test_execute_with_context_dependent_computation(self):
        """Test computation that depends on existing context data."""

        def context_dependent_compute(context):
            user_data = context.agent_context.get("user_data", {})
            return {
                "user_summary": (
                    f"User {user_data.get('name', 'Unknown')} "
                    f"has ID {user_data.get('id', 'N/A')}"
                ),
                "data_available": len(context.agent_context) > 0,
            }

        brick = ComputedFoundationBrick(
            compute_fn=context_dependent_compute,
            context_key="user_summary",
        )

        context = ExecutionContext()
        context.agent_context = AgentContext()
        context.agent_context["user_data"] = {"id": 789, "name": "Bob"}

        result = await brick.execute(context)

        expected_computed = {
            "user_summary": "User Bob has ID 789",
            "data_available": True,
        }
        assert result["computed_data"] == expected_computed
        assert context.agent_context["user_summary"] == expected_computed


@pytest.mark.asyncio
async def test_foundation_brick_integration():
    """Test that foundation bricks work in integration scenarios."""
    # This test simulates how foundation bricks might be used together

    context = ExecutionContext()
    context.agent_context = AgentContext()

    # Step 1: Use DataFoundationBrick to provide initial data
    data_brick = DataFoundationBrick(
        data={"base_config": {"env": "test", "debug": True}},
        context_key="config",
    )
    await data_brick.execute(context)

    # Step 2: Use ComputedFoundationBrick to process the initial data
    def enhance_config(ctx):
        base_config = ctx.agent_context.get("config", {})
        return {
            "enhanced_config": {
                **base_config,
                "computed_at": "2024-01-01",
                "is_enhanced": True,
            }
        }

    computed_brick = ComputedFoundationBrick(
        compute_fn=enhance_config,
        context_key="enhanced_data",
    )
    await computed_brick.execute(context)

    # Step 3: Use ContextFoundationBrick to extract final data
    context_brick = ContextFoundationBrick(
        source_keys=["config", "enhanced_data"],
        target_key="final_foundation",
    )
    result = await context_brick.execute(context)

    # Verify the integration worked
    assert "config" in result["extracted_data"]
    assert "enhanced_data" in result["extracted_data"]
    assert (
        context.agent_context["final_foundation"]["config"]["base_config"]["env"]
        == "test"
    )
    assert (
        context.agent_context["final_foundation"]["enhanced_data"]["enhanced_config"][
            "is_enhanced"
        ]
        is True
    )
