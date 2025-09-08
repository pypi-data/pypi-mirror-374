"""Base implementation of AgentBrick."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from .types import BrickType, ExecutionContext


class AgentBrick(ABC):
    """Base class for all agent bricks.

    Bricks are the fundamental building blocks that compose nodes.
    Each brick performs a specific function: prompt generation,
    action execution, data processing, or routing decisions.
    """

    # Class-level brick type declaration
    BRICK_TYPE: ClassVar[BrickType] = BrickType.PROCESSOR

    def __init__(
        self,
        brick_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the brick.

        Args:
            brick_id: Unique identifier. Auto-generated if not provided.
            name: Human-readable name for the brick.
            metadata: Additional metadata for the brick.
        """
        self._id = brick_id or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        self._name = name or self.__class__.__name__
        self._metadata = metadata or {}

    @property
    def id(self) -> str:
        """Unique identifier for the brick."""
        return self._id

    @property
    def name(self) -> str:
        """Human-readable name."""
        return self._name

    @property
    def brick_type(self) -> BrickType:
        """Type of the brick."""
        return self.BRICK_TYPE

    @property
    def metadata(self) -> dict[str, Any]:
        """Brick metadata."""
        return self._metadata

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> Any:
        """Execute the brick's logic.

        Args:
            context: Execution context containing data and state.

        Returns:
            Result of brick execution. Type depends on brick implementation.
        """
        pass

    def __repr__(self) -> str:
        """String representation of the brick."""
        return f"{self.__class__.__name__}(id={self.id}, type={self.brick_type.name})"

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> AgentBrick:
        """Create a brick instance from configuration.

        Args:
            config: Dictionary containing brick configuration.

        Returns:
            Configured brick instance.
        """
        # Extract standard parameters
        brick_id = config.get("id")
        name = config.get("name")
        metadata = config.get("metadata", {})

        # Remove standard params to pass remaining as kwargs
        init_params = {
            k: v
            for k, v in config.items()
            if k not in {"id", "name", "metadata", "type"}
        }

        return cls(brick_id=brick_id, name=name, metadata=metadata, **init_params)


class CompositeBrick(AgentBrick):
    """A brick that contains and executes multiple sub-bricks."""

    def __init__(
        self,
        bricks: list[AgentBrick],
        brick_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize composite brick.

        Args:
            bricks: List of bricks to execute in sequence.
            brick_id: Unique identifier.
            name: Human-readable name.
            metadata: Additional metadata.
        """
        super().__init__(brick_id, name, metadata)
        self._bricks = bricks

    @property
    def bricks(self) -> list[AgentBrick]:
        """Get the list of sub-bricks."""
        return self._bricks

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute all sub-bricks in sequence.

        Args:
            context: Execution context.

        Returns:
            Dictionary mapping brick IDs to their outputs.
        """
        results = {}

        for brick in self._bricks:
            result = await brick.execute(context)
            results[brick.id] = result

            # Store in context for downstream bricks
            context.brick_outputs[brick.id] = result

        return results
