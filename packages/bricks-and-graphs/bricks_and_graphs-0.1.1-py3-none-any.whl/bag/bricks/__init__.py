"""Built-in brick implementations for the bricks-and-graphs framework.

This module provides ready-to-use brick implementations for common tasks:

- **FoundationBrick**: Foundational data provision for other bricks
- **PromptBrick**: Text and template management for LLM prompts
- **ProcessorBrick**: Multi-format data processing (JSON, YAML, Arrow, Pandas, etc.)
- **RouterBrick**: Graph-aware routing decisions

Example:
    >>> from bag.bricks import (
    ...     PromptBrick,
    ...     LiteLLMResponseProcessor,
    ...     ConditionalRouter
    ... )
    >>>
    >>> # Create a simple agent workflow
    >>> prompt = PromptBrick(template="Analyze: {data}")
    >>> processor = LiteLLMResponseProcessor(parse_json=True)
    >>> router = ConditionalRouter(
    ...     conditions={"has_error": lambda d: "error" in d},
    ...     routes={"has_error": "error_handler"}
    ... )
"""

from .foundation import (
    ComputedFoundationBrick,
    ContextFoundationBrick,
    DataFoundationBrick,
    FoundationBrick,
)
from .processor import (
    ChainProcessor,
    DataTransformProcessor,
    LiteLLMResponseProcessor,
    ProcessorBrick,
)
from .prompt import PromptAssembler, PromptBrick
from .router import ConditionalRouter, DataFieldRouter, RouterBrick, WeightedRouter
from .types import (
    DataFormat,
    DataType,
    InputType,
    OutputType,
    ProcessingContext,
    ProcessingMode,
    PromptTemplate,
    RouteDecision,
    StreamDataType,
)

__all__ = [
    # Foundation bricks
    "FoundationBrick",
    "DataFoundationBrick",
    "ContextFoundationBrick",
    "ComputedFoundationBrick",
    # Prompt bricks
    "PromptBrick",
    "PromptAssembler",
    "PromptTemplate",
    # Processor bricks
    "ProcessorBrick",
    "LiteLLMResponseProcessor",
    "DataTransformProcessor",
    "ChainProcessor",
    # Router bricks
    "RouterBrick",
    "ConditionalRouter",
    "DataFieldRouter",
    "WeightedRouter",
    # Types
    "DataFormat",
    "DataType",
    "InputType",
    "OutputType",
    "StreamDataType",
    "ProcessingContext",
    "ProcessingMode",
    "RouteDecision",
]
