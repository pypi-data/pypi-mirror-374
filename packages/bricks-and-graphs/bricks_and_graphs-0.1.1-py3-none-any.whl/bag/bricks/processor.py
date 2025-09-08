"""ProcessorBrick implementation for data processing.

ProcessorBrick provides a flexible interface for processing various data formats
including LiteLLM responses, JSON, YAML, Arrow, Pandas, Polars, and plain text.
It supports both synchronous objects and async streams.

Example:
    >>> # Simple JSON processor
    >>> class JSONExtractor(ProcessorBrick):
    ...     async def process_data(self, data, context):
    ...         if isinstance(data, ModelResponse):
    ...             return json.loads(data.choices[0].message.content)
    ...         return data
    >>>
    >>> # Stream processor
    >>> class StreamAggregator(ProcessorBrick):
    ...     async def process_stream(self, stream, context):
    ...         async for chunk in stream:
    ...             # Process each chunk
    ...             yield self.transform(chunk)
"""

from __future__ import annotations

import json
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

import pandas as pd
import polars as pl
import pyarrow as pa
import yaml
from litellm import ModelResponse

from ..core import AgentBrick, BrickType, ExecutionContext
from .types import (
    DataFormat,
    DataType,
    OutputType,
    ProcessingContext,
    ProcessingMode,
    StreamDataType,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

T = TypeVar("T")


class ProcessorBrick(AgentBrick):
    """Base class for data processing bricks.

    ProcessorBrick provides a flexible interface for handling multiple data formats
    and processing modes (sync/stream). Subclasses should implement either
    process_data() for synchronous processing or process_stream() for stream processing,
    or both.

    Attributes:
        input_format: Expected input data format.
        output_format: Output data format.
        stream_support: Whether this processor supports streaming.
    """

    BRICK_TYPE = BrickType.PROCESSOR

    def __init__(
        self,
        input_format: DataFormat | None = None,
        output_format: DataFormat | None = None,
        stream_support: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize the ProcessorBrick.

        Args:
            input_format: Expected input format (None = auto-detect).
            output_format: Output format (None = same as input).
            stream_support: Whether this processor supports streaming.
            **kwargs: Additional arguments for AgentBrick.
        """
        super().__init__(**kwargs)
        self.input_format = input_format
        self.output_format = output_format
        self.stream_support = stream_support

    async def execute(self, context: ExecutionContext) -> Any:
        """Execute the processor brick.

        Args:
            context: Execution context containing input data.

        Returns:
            Processed output data.
        """
        # Get input data from context
        input_data = context.data.get("input")
        if input_data is None and context.brick_outputs:
            # Get the last output from brick outputs
            input_data = list(context.brick_outputs.values())[-1]

        if input_data is None:
            raise ValueError("No input data found in context")

        # Create processing context
        proc_context = ProcessingContext(
            input_format=self.input_format,
            output_format=self.output_format,
            mode=(
                ProcessingMode.STREAM
                if self._is_stream(input_data)
                else ProcessingMode.SYNC
            ),
        )

        # Process based on type
        if self._is_stream(input_data):
            if not self.stream_support:
                # Convert stream to object
                input_data = await self._collect_stream(input_data)
                proc_context.mode = ProcessingMode.SYNC
                result = await self.process_data(input_data, proc_context)
            else:
                result = self.process_stream(input_data, proc_context)
        else:
            result = await self.process_data(input_data, proc_context)

        return result

    @abstractmethod
    async def process_data(
        self, data: DataType, context: ProcessingContext
    ) -> OutputType:
        """Process synchronous data.

        Args:
            data: Input data object.
            context: Processing context.

        Returns:
            Processed output data.
        """
        pass

    async def process_stream(
        self,
        stream: StreamDataType,
        context: ProcessingContext,
    ) -> AsyncIterator[Any]:
        """Process streaming data.

        Default implementation collects the stream and processes as a batch.
        Override for true streaming support.

        Args:
            stream: Input data stream.
            context: Processing context.

        Yields:
            Processed output chunks.
        """
        # Default: collect and process
        collected = await self._collect_stream(stream)
        result = await self.process_data(collected, context)

        # If result is iterable, yield items
        if hasattr(result, "__iter__") and not isinstance(result, str | bytes):
            for item in result:
                yield item
        else:
            yield result

    def _is_stream(self, data: Any) -> bool:
        """Check if data is a stream."""
        return hasattr(data, "__aiter__")

    async def _collect_stream(self, stream: AsyncIterator[T]) -> list[T]:
        """Collect all items from a stream."""
        items = []
        async for item in stream:
            items.append(item)
        return items

    @staticmethod
    def detect_format(data: Any) -> DataFormat:
        """Detect the format of input data.

        Args:
            data: Input data to analyze.

        Returns:
            Detected data format.
        """
        if isinstance(data, ModelResponse):
            return DataFormat.LITELLM_RESPONSE
        elif isinstance(data, (dict, list)):  # noqa: UP038
            return DataFormat.JSON
        elif isinstance(data, pd.DataFrame):
            return DataFormat.PANDAS
        elif isinstance(data, pl.DataFrame):
            return DataFormat.POLARS
        elif isinstance(data, pa.Table):
            return DataFormat.ARROW
        elif isinstance(data, str):
            # Try to detect YAML vs plain text
            try:
                # Only consider it YAML if it contains YAML-specific characters
                if any(char in data for char in [":", "\n-", "\n ", "{", "["]):
                    yaml.safe_load(data)
                    return DataFormat.YAML
                else:
                    return DataFormat.TEXT
            except yaml.YAMLError:
                return DataFormat.TEXT
        else:
            return DataFormat.TEXT


class LiteLLMResponseProcessor(ProcessorBrick):
    """Processor specifically for handling LiteLLM responses.

    Example:
        >>> processor = LiteLLMResponseProcessor(
        ...     extract_content=True,
        ...     parse_json=True
        ... )
    """

    def __init__(
        self,
        extract_content: bool = True,
        parse_json: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize the LiteLLM processor.

        Args:
            extract_content: Whether to extract message content.
            parse_json: Whether to parse content as JSON.
            **kwargs: Additional arguments for ProcessorBrick.
        """
        super().__init__(
            input_format=DataFormat.LITELLM_RESPONSE,
            output_format=DataFormat.JSON if parse_json else DataFormat.TEXT,
            **kwargs,
        )
        self.extract_content = extract_content
        self.parse_json = parse_json

    async def process_data(
        self,
        data: DataType,
        context: ProcessingContext,  # noqa: ARG002
    ) -> OutputType:
        """Process LiteLLM response.

        Args:
            data: LiteLLM ModelResponse.
            context: Processing context.

        Returns:
            Extracted/processed content.
        """
        if not isinstance(data, ModelResponse):
            raise ValueError(f"Expected ModelResponse, got {type(data)}")

        if self.extract_content:
            content = data.choices[0].message.content

            if self.parse_json:
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    # Return error info
                    return {
                        "error": "JSON parse error",
                        "message": str(e),
                        "content": content,
                    }
            else:
                return content
        else:
            # Return full response as dict
            return data.model_dump()


class DataTransformProcessor(ProcessorBrick):
    """Generic data transformation processor.

    Supports transformations between different data formats.

    Example:
        >>> # JSON to Pandas
        >>> processor = DataTransformProcessor(
        ...     input_format=DataFormat.JSON,
        ...     output_format=DataFormat.PANDAS
        ... )
    """

    def __init__(
        self,
        input_format: DataFormat,
        output_format: DataFormat,
        **kwargs: Any,
    ) -> None:
        """Initialize the data transformer.

        Args:
            input_format: Input data format.
            output_format: Output data format.
            **kwargs: Additional arguments for ProcessorBrick.
        """
        super().__init__(
            input_format=input_format,
            output_format=output_format,
            stream_support=True,
            **kwargs,
        )

    async def process_data(
        self,
        data: DataType,
        context: ProcessingContext,  # noqa: ARG002
    ) -> OutputType:
        """Transform data between formats.

        Args:
            data: Input data.
            context: Processing context.

        Returns:
            Transformed data in output format.
        """
        # Detect actual format if needed
        actual_format = self.detect_format(data)

        # Convert to intermediate format if needed
        if actual_format == DataFormat.JSON:
            json_data = data
        elif actual_format == DataFormat.YAML:
            json_data = yaml.safe_load(data)
        elif actual_format == DataFormat.PANDAS:
            json_data = data.to_dict("records")
        elif actual_format == DataFormat.POLARS:
            json_data = data.to_dicts()
        elif actual_format == DataFormat.ARROW:
            json_data = data.to_pylist()
        elif actual_format == DataFormat.TEXT:
            json_data = {"text": data}
        else:
            json_data = data

        # Convert to target format
        if self.output_format == DataFormat.JSON:
            return json_data
        elif self.output_format == DataFormat.YAML:
            return yaml.dump(json_data)
        elif self.output_format == DataFormat.PANDAS:
            # Handle different input types properly
            if isinstance(json_data, list):
                # If it's a list of dicts, use it directly
                if json_data and isinstance(json_data[0], dict):
                    return pd.DataFrame(json_data)
                else:
                    # Otherwise wrap in a dict
                    return pd.DataFrame({"data": json_data})
            elif isinstance(json_data, dict):
                # Single dict becomes single row
                return pd.DataFrame([json_data])
            else:
                return pd.DataFrame({"data": [json_data]})
        elif self.output_format == DataFormat.POLARS:
            # Similar handling for Polars
            if isinstance(json_data, list):
                if json_data and isinstance(json_data[0], dict):
                    return pl.DataFrame(json_data)
                else:
                    return pl.DataFrame({"data": json_data})
            elif isinstance(json_data, dict):
                return pl.DataFrame([json_data])
            else:
                return pl.DataFrame({"data": [json_data]})
        elif self.output_format == DataFormat.ARROW:
            # Use pandas conversion first
            if isinstance(json_data, list):
                if json_data and isinstance(json_data[0], dict):
                    df = pd.DataFrame(json_data)
                else:
                    df = pd.DataFrame({"data": json_data})
            elif isinstance(json_data, dict):
                df = pd.DataFrame([json_data])
            else:
                df = pd.DataFrame({"data": [json_data]})
            return pa.Table.from_pandas(df)
        elif self.output_format == DataFormat.TEXT:
            return (
                json.dumps(json_data) if not isinstance(json_data, str) else json_data
            )
        else:
            return json_data

    async def process_stream(
        self,
        stream: StreamDataType,
        context: ProcessingContext,
    ) -> AsyncIterator[Any]:
        """Process streaming data with format conversion.

        Args:
            stream: Input data stream.
            context: Processing context.

        Yields:
            Transformed data chunks.
        """
        async for chunk in stream:
            # Process each chunk
            transformed = await self.process_data(chunk, context)
            yield transformed


class ChainProcessor(ProcessorBrick):
    """Processor that chains multiple processors together.

    Example:
        >>> chain = ChainProcessor([
        ...     LiteLLMResponseProcessor(extract_content=True),
        ...     DataTransformProcessor(DataFormat.JSON, DataFormat.PANDAS)
        ... ])
    """

    def __init__(
        self,
        processors: list[ProcessorBrick],
        **kwargs: Any,
    ) -> None:
        """Initialize the chain processor.

        Args:
            processors: List of processors to chain.
            **kwargs: Additional arguments for ProcessorBrick.
        """
        # Determine formats from chain
        input_format = processors[0].input_format if processors else None
        output_format = processors[-1].output_format if processors else None
        stream_support = all(p.stream_support for p in processors)

        super().__init__(
            input_format=input_format,
            output_format=output_format,
            stream_support=stream_support,
            **kwargs,
        )
        self.processors = processors

    async def process_data(
        self,
        data: DataType,
        context: ProcessingContext,  # noqa: ARG002
    ) -> OutputType:
        """Process data through the chain.

        Args:
            data: Input data.
            context: Processing context.

        Returns:
            Final processed output.
        """
        current_data = data

        for processor in self.processors:
            # Update context for each processor
            proc_context = ProcessingContext(
                input_format=processor.input_format,
                output_format=processor.output_format,
                mode=ProcessingMode.SYNC,
                processing_metadata=context.processing_metadata,
            )

            current_data = await processor.process_data(current_data, proc_context)

        return current_data
