"""Foundation brick implementations for providing base data to other bricks."""

from __future__ import annotations

from abc import abstractmethod
from typing import Any, ClassVar

from bag.core import AgentBrick, BrickType, ExecutionContext


class FoundationBrick(AgentBrick):
    """Base class for foundation bricks.

    Foundation bricks provide foundational data that other bricks in the same
    node can use. They are executed first, before any other brick type.
    Only one foundation brick is allowed per node.

    Foundation bricks should store their results in the execution context
    so other bricks can access them.
    """

    BRICK_TYPE: ClassVar[BrickType] = BrickType.FOUNDATION

    def __init__(
        self,
        brick_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the foundation brick.

        Args:
            brick_id: Unique identifier for the brick.
            name: Human-readable name for the brick.
            metadata: Additional metadata for the brick.
        """
        super().__init__(brick_id, name, metadata)

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute the foundation brick logic.

        This method should gather foundational data and store it in the
        execution context for other bricks to use.

        Args:
            context: Execution context to store foundation data.

        Returns:
            Dictionary containing the foundation data. This data is also
            typically stored in context.agent_context for other bricks.
        """
        pass


class DataFoundationBrick(FoundationBrick):
    """Foundation brick that provides static data."""

    def __init__(
        self,
        data: dict[str, Any],
        context_key: str = "foundation_data",
        brick_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize with static data.

        Args:
            data: Static data to provide to other bricks.
            context_key: Key to store data in agent context.
            brick_id: Unique identifier for the brick.
            name: Human-readable name for the brick.
            metadata: Additional metadata for the brick.
        """
        super().__init__(brick_id, name, metadata)
        self.data = data
        self.context_key = context_key

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute by storing static data in context.

        Args:
            context: Execution context.

        Returns:
            The static data provided to the brick.
        """
        # Store data in agent context for other bricks to access
        context.agent_context[self.context_key] = self.data

        return {
            "data": self.data,
            "context_key": self.context_key,
            "message": (
                f"Foundation data stored in context under key '{self.context_key}'"
            ),
        }


class ContextFoundationBrick(FoundationBrick):
    """Foundation brick that extracts data from existing context."""

    def __init__(
        self,
        source_keys: list[str],
        target_key: str = "foundation_context",
        brick_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize with context keys to extract.

        Args:
            source_keys: Keys to extract from agent context.
            target_key: Key to store extracted data in agent context.
            brick_id: Unique identifier for the brick.
            name: Human-readable name for the brick.
            metadata: Additional metadata for the brick.
        """
        super().__init__(brick_id, name, metadata)
        self.source_keys = source_keys
        self.target_key = target_key

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute by extracting and reorganizing context data.

        Args:
            context: Execution context.

        Returns:
            Dictionary containing extracted data and metadata.
        """
        extracted_data = {}
        missing_keys = []

        # Extract data from agent context
        for key in self.source_keys:
            if key in context.agent_context:
                extracted_data[key] = context.agent_context[key]
            else:
                missing_keys.append(key)

        # Store extracted data under target key
        context.agent_context[self.target_key] = extracted_data

        return {
            "extracted_data": extracted_data,
            "missing_keys": missing_keys,
            "target_key": self.target_key,
            "message": f"Extracted {len(extracted_data)} items from context",
        }


class ComputedFoundationBrick(FoundationBrick):
    """Foundation brick that computes data using a custom function."""

    def __init__(
        self,
        compute_fn: callable[[ExecutionContext], dict[str, Any]],
        context_key: str = "computed_foundation",
        brick_id: str | None = None,
        name: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Initialize with computation function.

        Args:
            compute_fn: Function that takes ExecutionContext and returns data.
            context_key: Key to store computed data in agent context.
            brick_id: Unique identifier for the brick.
            name: Human-readable name for the brick.
            metadata: Additional metadata for the brick.
        """
        super().__init__(brick_id, name, metadata)
        self.compute_fn = compute_fn
        self.context_key = context_key

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute by computing data using the provided function.

        Args:
            context: Execution context.

        Returns:
            Dictionary containing computed data and metadata.
        """
        # Compute data using the provided function
        computed_data = self.compute_fn(context)

        # Store computed data in agent context
        context.agent_context[self.context_key] = computed_data

        return {
            "computed_data": computed_data,
            "context_key": self.context_key,
            "message": (
                f"Computed foundation data stored under key '{self.context_key}'"
            ),
        }
