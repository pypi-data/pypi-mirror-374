"""Tests for ProcessorBrick implementation."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import polars as pl
import pyarrow as pa
import pytest
import yaml
from litellm import ModelResponse

from bag.bricks import (
    ChainProcessor,
    DataFormat,
    DataTransformProcessor,
    LiteLLMResponseProcessor,
    ProcessingContext,
    ProcessingMode,
    ProcessorBrick,
)
from bag.core import ExecutionContext


class SimpleProcessor(ProcessorBrick):
    """Simple test processor."""

    async def process_data(self, data: Any, context: ProcessingContext) -> Any:
        """Simply return the data with a marker."""
        return {"processed": True, "data": data}


class StreamProcessor(ProcessorBrick):
    """Test processor with streaming support."""

    def __init__(self, **kwargs):
        super().__init__(stream_support=True, **kwargs)

    async def process_data(self, data: Any, context: ProcessingContext) -> Any:
        """Process single data item."""
        return data * 2

    async def process_stream(self, stream, context):
        """Process stream by doubling each item."""
        async for item in stream:
            yield item * 2


class TestProcessorBrick:
    """Tests for ProcessorBrick base class."""

    def test_processor_creation(self):
        """Test creating a processor brick."""
        processor = SimpleProcessor(
            input_format=DataFormat.JSON,
            output_format=DataFormat.TEXT,
            brick_id="test_proc",
        )

        assert processor.input_format == DataFormat.JSON
        assert processor.output_format == DataFormat.TEXT
        assert processor.stream_support is False
        assert processor.id == "test_proc"
        assert processor.brick_type.name == "PROCESSOR"

    @pytest.mark.asyncio
    async def test_processor_execution(self):
        """Test basic processor execution."""
        processor = SimpleProcessor()
        context = ExecutionContext(data={"input": {"test": "data"}})

        result = await processor.execute(context)

        assert result["processed"] is True
        assert result["data"] == {"test": "data"}

    @pytest.mark.asyncio
    async def test_processor_with_brick_outputs(self):
        """Test processor getting input from previous brick outputs."""
        processor = SimpleProcessor()
        context = ExecutionContext(brick_outputs={"prev_brick": {"previous": "output"}})

        result = await processor.execute(context)

        assert result["processed"] is True
        assert result["data"] == {"previous": "output"}

    @pytest.mark.asyncio
    async def test_processor_no_input_error(self):
        """Test processor raises error when no input found."""
        processor = SimpleProcessor()
        context = ExecutionContext()

        with pytest.raises(ValueError, match="No input data found"):
            await processor.execute(context)

    def test_detect_format(self):
        """Test format detection."""
        # JSON
        assert ProcessorBrick.detect_format({"key": "value"}) == DataFormat.JSON

        # Text
        assert ProcessorBrick.detect_format("plain text") == DataFormat.TEXT

        # YAML string
        yaml_str = "key: value\nlist:\n  - item1\n  - item2"
        assert ProcessorBrick.detect_format(yaml_str) == DataFormat.YAML

        # Pandas
        df = pd.DataFrame({"col": [1, 2, 3]})
        assert ProcessorBrick.detect_format(df) == DataFormat.PANDAS

        # Polars
        pl_df = pl.DataFrame({"col": [1, 2, 3]})
        assert ProcessorBrick.detect_format(pl_df) == DataFormat.POLARS

        # Arrow
        arrow_table = pa.table({"col": [1, 2, 3]})
        assert ProcessorBrick.detect_format(arrow_table) == DataFormat.ARROW

        # LiteLLM Response
        mock_response = MagicMock(spec=ModelResponse)
        assert (
            ProcessorBrick.detect_format(mock_response) == DataFormat.LITELLM_RESPONSE
        )

    @pytest.mark.asyncio
    async def test_stream_processing(self):
        """Test stream processing capabilities."""
        processor = StreamProcessor()

        async def create_stream():
            for i in range(3):
                yield i

        stream = create_stream()
        context = ProcessingContext(mode=ProcessingMode.STREAM)

        results = []
        async for result in processor.process_stream(stream, context):
            results.append(result)

        assert results == [0, 2, 4]


class TestLiteLLMResponseProcessor:
    """Tests for LiteLLMResponseProcessor."""

    def create_mock_response(self, content: str) -> ModelResponse:
        """Create a mock LiteLLM response."""
        mock = MagicMock(spec=ModelResponse)
        mock.choices = [MagicMock()]
        mock.choices[0].message.content = content
        mock.model_dump.return_value = {"mock": "response"}
        return mock

    @pytest.mark.asyncio
    async def test_extract_content(self):
        """Test extracting content from LiteLLM response."""
        processor = LiteLLMResponseProcessor(extract_content=True)
        mock_response = self.create_mock_response("Hello, world!")

        context = ProcessingContext()
        result = await processor.process_data(mock_response, context)

        assert result == "Hello, world!"

    @pytest.mark.asyncio
    async def test_parse_json_content(self):
        """Test parsing JSON from LiteLLM response."""
        processor = LiteLLMResponseProcessor(extract_content=True, parse_json=True)
        mock_response = self.create_mock_response('{"key": "value", "number": 42}')

        context = ProcessingContext()
        result = await processor.process_data(mock_response, context)

        assert result == {"key": "value", "number": 42}

    @pytest.mark.asyncio
    async def test_parse_json_error(self):
        """Test handling JSON parse errors."""
        processor = LiteLLMResponseProcessor(extract_content=True, parse_json=True)
        mock_response = self.create_mock_response("Not valid JSON")

        context = ProcessingContext()
        result = await processor.process_data(mock_response, context)

        assert result["error"] == "JSON parse error"
        assert "message" in result
        assert result["content"] == "Not valid JSON"

    @pytest.mark.asyncio
    async def test_full_response(self):
        """Test returning full response without extraction."""
        processor = LiteLLMResponseProcessor(extract_content=False)
        mock_response = self.create_mock_response("Content")

        context = ProcessingContext()
        result = await processor.process_data(mock_response, context)

        assert result == {"mock": "response"}

    @pytest.mark.asyncio
    async def test_invalid_input_type(self):
        """Test error on invalid input type."""
        processor = LiteLLMResponseProcessor()

        context = ProcessingContext()
        with pytest.raises(ValueError, match="Expected ModelResponse"):
            await processor.process_data({"not": "a response"}, context)


class TestDataTransformProcessor:
    """Tests for DataTransformProcessor."""

    @pytest.mark.asyncio
    async def test_json_to_pandas(self):
        """Test transforming JSON to Pandas DataFrame."""
        processor = DataTransformProcessor(
            input_format=DataFormat.JSON, output_format=DataFormat.PANDAS
        )

        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

        context = ProcessingContext()
        result = await processor.process_data(data, context)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == ["name", "age"]
        assert result.iloc[0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_pandas_to_json(self):
        """Test transforming Pandas to JSON."""
        processor = DataTransformProcessor(
            input_format=DataFormat.PANDAS, output_format=DataFormat.JSON
        )

        df = pd.DataFrame({"name": ["Alice", "Bob"], "age": [30, 25]})

        context = ProcessingContext()
        result = await processor.process_data(df, context)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"name": "Alice", "age": 30}

    @pytest.mark.asyncio
    async def test_json_to_yaml(self):
        """Test transforming JSON to YAML."""
        processor = DataTransformProcessor(
            input_format=DataFormat.JSON, output_format=DataFormat.YAML
        )

        data = {"key": "value", "list": [1, 2, 3]}

        context = ProcessingContext()
        result = await processor.process_data(data, context)

        assert isinstance(result, str)
        parsed = yaml.safe_load(result)
        assert parsed == data

    @pytest.mark.asyncio
    async def test_yaml_to_polars(self):
        """Test transforming YAML to Polars DataFrame."""
        processor = DataTransformProcessor(
            input_format=DataFormat.YAML, output_format=DataFormat.POLARS
        )

        yaml_data = """
        - name: Alice
          age: 30
        - name: Bob
          age: 25
        """

        context = ProcessingContext()
        result = await processor.process_data(yaml_data, context)

        assert isinstance(result, pl.DataFrame)
        assert len(result) == 2
        assert result.columns == ["name", "age"]

    @pytest.mark.asyncio
    async def test_arrow_conversion(self):
        """Test Arrow table conversions."""
        # Create Arrow table
        data = {"col1": [1, 2, 3], "col2": ["a", "b", "c"]}
        arrow_table = pa.table(data)

        # Arrow to JSON
        processor = DataTransformProcessor(
            input_format=DataFormat.ARROW, output_format=DataFormat.JSON
        )

        context = ProcessingContext()
        result = await processor.process_data(arrow_table, context)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == {"col1": 1, "col2": "a"}

    @pytest.mark.asyncio
    async def test_text_to_json_conversion(self):
        """Test TEXT format as input."""
        processor = DataTransformProcessor(
            input_format=DataFormat.TEXT, output_format=DataFormat.JSON
        )

        context = ProcessingContext()
        result = await processor.process_data("plain text", context)

        assert result == {"text": "plain text"}

    @pytest.mark.asyncio
    async def test_single_dict_to_dataframe(self):
        """Test converting single dict to DataFrame."""
        processor = DataTransformProcessor(
            input_format=DataFormat.JSON, output_format=DataFormat.PANDAS
        )

        data = {"name": "Charlie", "age": 35}
        context = ProcessingContext()
        result = await processor.process_data(data, context)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["name"] == "Charlie"

    @pytest.mark.asyncio
    async def test_non_dict_list_to_dataframe(self):
        """Test converting list of non-dicts to DataFrame."""
        processor = DataTransformProcessor(
            input_format=DataFormat.JSON, output_format=DataFormat.PANDAS
        )

        data = [1, 2, 3, 4, 5]
        context = ProcessingContext()
        result = await processor.process_data(data, context)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert "data" in result.columns

    @pytest.mark.asyncio
    async def test_stream_transformation(self):
        """Test stream transformation."""
        processor = DataTransformProcessor(
            input_format=DataFormat.JSON, output_format=DataFormat.TEXT
        )

        async def create_json_stream():
            yield {"item": 1}
            yield {"item": 2}
            yield {"item": 3}

        stream = create_json_stream()
        context = ProcessingContext(mode=ProcessingMode.STREAM)

        results = []
        async for result in processor.process_stream(stream, context):
            results.append(result)

        assert len(results) == 3
        assert results[0] == '{"item": 1}'


class TestChainProcessor:
    """Tests for ChainProcessor."""

    @pytest.mark.asyncio
    async def test_chain_processing(self):
        """Test chaining multiple processors."""

        # Create a chain: JSON -> multiply values -> convert to text
        class MultiplyProcessor(ProcessorBrick):
            async def process_data(self, data: Any, context: ProcessingContext) -> Any:
                if isinstance(data, dict):
                    return {
                        k: v * 2 if isinstance(v, int | float) else v
                        for k, v in data.items()
                    }
                return data

        chain = ChainProcessor(
            [
                MultiplyProcessor(),
                DataTransformProcessor(DataFormat.JSON, DataFormat.TEXT),
            ]
        )

        data = {"x": 10, "y": 20, "name": "test"}
        context = ProcessingContext()

        result = await chain.process_data(data, context)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == {"x": 20, "y": 40, "name": "test"}

    def test_chain_format_detection(self):
        """Test that chain detects input/output formats correctly."""
        chain = ChainProcessor(
            [
                DataTransformProcessor(DataFormat.JSON, DataFormat.PANDAS),
                DataTransformProcessor(DataFormat.PANDAS, DataFormat.ARROW),
                DataTransformProcessor(DataFormat.ARROW, DataFormat.TEXT),
            ]
        )

        assert chain.input_format == DataFormat.JSON
        assert chain.output_format == DataFormat.TEXT
        assert chain.stream_support is True  # All transforms support streaming

    def test_empty_chain(self):
        """Test creating an empty chain."""
        chain = ChainProcessor([])

        assert chain.input_format is None
        assert chain.output_format is None
        assert chain.stream_support is True

    @pytest.mark.asyncio
    async def test_processor_missing_execute_method(self):
        """Test processor that doesn't implement required methods."""

        class BadProcessor(ProcessorBrick):
            pass  # Missing process_data implementation

        # This should raise error when trying to instantiate
        with pytest.raises(TypeError):
            BadProcessor()

    @pytest.mark.asyncio
    async def test_collect_stream(self):
        """Test the stream collection utility."""
        processor = SimpleProcessor()

        async def test_stream():
            for i in range(5):
                yield i

        stream = test_stream()
        result = await processor._collect_stream(stream)
        assert result == [0, 1, 2, 3, 4]

    def test_is_stream_detection(self):
        """Test stream detection."""
        processor = SimpleProcessor()

        # Regular data is not a stream
        assert processor._is_stream([1, 2, 3]) is False
        assert processor._is_stream({"key": "value"}) is False

        # Async iterator is a stream
        async def async_gen():
            yield 1

        assert processor._is_stream(async_gen()) is True
