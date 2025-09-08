"""Type definitions for brick implementations."""

from __future__ import annotations

from collections.abc import AsyncIterator
from enum import Enum, auto
from typing import Any, Protocol, TypeAlias, TypeVar

import pandas as pd
import polars as pl
import pyarrow as pa
from litellm import ModelResponse
from pydantic import BaseModel, ConfigDict, Field


class DataFormat(Enum):
    """Supported data formats for processor and router bricks."""

    JSON = auto()
    YAML = auto()
    ARROW = auto()
    PANDAS = auto()
    POLARS = auto()
    TEXT = auto()
    LITELLM_RESPONSE = auto()


# Type definitions for different data formats
DataType = (
    dict[str, Any]  # JSON
    | str  # YAML/Text
    | pa.Table  # Arrow
    | pd.DataFrame  # Pandas
    | pl.DataFrame  # Polars
    | ModelResponse  # LiteLLM response
)

StreamDataType = (
    AsyncIterator[dict[str, Any]]  # JSON stream
    | AsyncIterator[str]  # Text/YAML stream
    | AsyncIterator[pa.RecordBatch]  # Arrow stream
    | AsyncIterator[pd.DataFrame]  # Pandas chunks
    | AsyncIterator[pl.DataFrame]  # Polars chunks
)

InputType: TypeAlias = DataType | StreamDataType  # noqa: UP040
OutputType: TypeAlias = DataType | StreamDataType  # noqa: UP040

T = TypeVar("T")
InputT = TypeVar("InputT", bound=InputType, contravariant=True)
OutputT = TypeVar("OutputT", bound=OutputType, covariant=True)


class ProcessingMode(Enum):
    """Processing mode for data handling."""

    SYNC = auto()  # Synchronous processing
    STREAM = auto()  # Stream processing


class PromptTemplate(BaseModel):
    """Template for prompt construction."""

    model_config = ConfigDict(extra="forbid")

    template: str = Field(..., description="The prompt template with {placeholders}")
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="Variables to fill in the template",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the prompt",
    )

    def render(self, **kwargs: Any) -> str:
        """Render the template with provided variables.

        Args:
            **kwargs: Additional variables to override defaults.

        Returns:
            Rendered prompt string.
        """
        variables = {**self.variables, **kwargs}
        return self.template.format(**variables)


class ProcessingContext(BaseModel):
    """Extended context for processing operations."""

    model_config = ConfigDict(extra="allow")

    # Input/output format hints
    input_format: DataFormat | None = None
    output_format: DataFormat | None = None

    # Processing mode
    mode: ProcessingMode = ProcessingMode.SYNC

    # Node outputs from the graph (for RouterBrick)
    available_routes: list[str] = Field(
        default_factory=list,
        description="Available node IDs for routing",
    )

    # Processing metadata
    processing_metadata: dict[str, Any] = Field(default_factory=dict)


class DataProcessor(Protocol[InputT, OutputT]):
    """Protocol for data processing functions."""

    async def process(self, data: InputT, context: ProcessingContext) -> OutputT:
        """Process input data and return output.

        Args:
            data: Input data in specified format.
            context: Processing context with metadata.

        Returns:
            Processed output data.
        """
        ...


class RouteDecision(BaseModel):
    """Enhanced routing decision with metadata."""

    model_config = ConfigDict(extra="forbid")

    target_node: str | None = Field(
        None,
        description="Target node ID to route to",
    )
    confidence: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Confidence score for the routing decision",
    )
    reason: str | None = Field(
        None,
        description="Explanation for the routing decision",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional routing metadata",
    )
    should_terminate: bool = Field(
        False,
        description="Whether to terminate graph execution",
    )
