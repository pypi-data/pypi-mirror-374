"""Tests for brick type definitions."""

from __future__ import annotations

import pytest

from bag.bricks import (
    DataFormat,
    ProcessingContext,
    ProcessingMode,
    PromptTemplate,
    RouteDecision,
)


class TestDataFormat:
    """Tests for DataFormat enum."""

    def test_data_format_values(self):
        """Test that all data formats are defined."""
        formats = [f.name for f in DataFormat]
        expected = [
            "JSON",
            "YAML",
            "ARROW",
            "PANDAS",
            "POLARS",
            "TEXT",
            "LITELLM_RESPONSE",
        ]
        assert formats == expected

    def test_data_format_access(self):
        """Test accessing data format values."""
        assert DataFormat.JSON.name == "JSON"
        assert DataFormat.PANDAS.name == "PANDAS"
        assert isinstance(DataFormat.ARROW, DataFormat)


class TestProcessingMode:
    """Tests for ProcessingMode enum."""

    def test_processing_modes(self):
        """Test available processing modes."""
        modes = [m.name for m in ProcessingMode]
        assert modes == ["SYNC", "STREAM"]

        assert ProcessingMode.SYNC != ProcessingMode.STREAM


class TestPromptTemplate:
    """Tests for PromptTemplate model."""

    def test_prompt_template_creation(self):
        """Test creating a prompt template."""
        template = PromptTemplate(template="Hello {name}!", variables={"name": "World"})

        assert template.template == "Hello {name}!"
        assert template.variables == {"name": "World"}
        assert template.metadata == {}

    def test_prompt_template_validation(self):
        """Test template validation."""
        # Extra fields should be forbidden
        with pytest.raises(ValueError):
            PromptTemplate(template="Test", extra_field="not allowed")

    def test_prompt_template_render_basic(self):
        """Test basic template rendering."""
        template = PromptTemplate(template="Hello {name}, you have {count} messages")

        result = template.render(name="Alice", count=5)
        assert result == "Hello Alice, you have 5 messages"

    def test_prompt_template_render_with_defaults(self):
        """Test rendering with default variables."""
        template = PromptTemplate(
            template="Hello {name} from {city}!", variables={"city": "Paris"}
        )

        # Use default city
        result = template.render(name="Bob")
        assert result == "Hello Bob from Paris!"

        # Override city
        result = template.render(name="Bob", city="London")
        assert result == "Hello Bob from London!"

    def test_prompt_template_metadata(self):
        """Test template with metadata."""
        template = PromptTemplate(
            template="Test {var}", metadata={"version": "1.0", "author": "test"}
        )

        assert template.metadata["version"] == "1.0"
        assert template.metadata["author"] == "test"


class TestProcessingContext:
    """Tests for ProcessingContext model."""

    def test_processing_context_creation(self):
        """Test creating a processing context."""
        context = ProcessingContext()

        assert context.input_format is None
        assert context.output_format is None
        assert context.mode == ProcessingMode.SYNC
        assert context.available_routes == []
        assert context.processing_metadata == {}

    def test_processing_context_with_values(self):
        """Test context with initial values."""
        context = ProcessingContext(
            input_format=DataFormat.JSON,
            output_format=DataFormat.PANDAS,
            mode=ProcessingMode.STREAM,
            available_routes=["node1", "node2"],
            processing_metadata={"key": "value"},
        )

        assert context.input_format == DataFormat.JSON
        assert context.output_format == DataFormat.PANDAS
        assert context.mode == ProcessingMode.STREAM
        assert context.available_routes == ["node1", "node2"]
        assert context.processing_metadata == {"key": "value"}

    def test_processing_context_extra_fields(self):
        """Test that context allows extra fields."""
        context = ProcessingContext(custom_field="custom_value", another_field=123)

        assert context.custom_field == "custom_value"  # type: ignore
        assert context.another_field == 123  # type: ignore


class TestRouteDecision:
    """Tests for RouteDecision model."""

    def test_route_decision_creation(self):
        """Test creating a route decision."""
        decision = RouteDecision()

        assert decision.target_node is None
        assert decision.confidence == 1.0
        assert decision.reason is None
        assert decision.metadata == {}
        assert decision.should_terminate is False

    def test_route_decision_with_values(self):
        """Test route decision with all values."""
        decision = RouteDecision(
            target_node="next_node",
            confidence=0.85,
            reason="High probability match",
            metadata={"score": 0.85, "method": "ml"},
            should_terminate=False,
        )

        assert decision.target_node == "next_node"
        assert decision.confidence == 0.85
        assert decision.reason == "High probability match"
        assert decision.metadata["score"] == 0.85
        assert decision.should_terminate is False

    def test_route_decision_termination(self):
        """Test termination decision."""
        decision = RouteDecision(should_terminate=True, reason="Processing complete")

        assert decision.target_node is None
        assert decision.should_terminate is True
        assert decision.reason == "Processing complete"

    def test_route_decision_confidence_validation(self):
        """Test confidence score validation."""
        # Valid confidence
        decision = RouteDecision(confidence=0.5)
        assert decision.confidence == 0.5

        # Edge cases
        decision = RouteDecision(confidence=0.0)
        assert decision.confidence == 0.0

        decision = RouteDecision(confidence=1.0)
        assert decision.confidence == 1.0

        # Invalid confidence should raise error
        with pytest.raises(ValueError):
            RouteDecision(confidence=1.5)

        with pytest.raises(ValueError):
            RouteDecision(confidence=-0.1)

    def test_route_decision_validation(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValueError):
            RouteDecision(target_node="node", extra_field="not allowed")
