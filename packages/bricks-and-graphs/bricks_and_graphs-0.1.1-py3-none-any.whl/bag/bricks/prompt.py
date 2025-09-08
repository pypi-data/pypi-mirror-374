"""PromptBrick implementation for assembling prompts.

The PromptBrick is a simple text holder that can be combined with other
PromptBricks to create complex prompts. Nodes handle the actual LLM execution.

Example:
    >>> # Single prompt brick
    >>> system_prompt = PromptBrick(
    ...     content="You are a helpful AI assistant.",
    ...     role="system"
    ... )
    >>>
    >>> # Template-based prompt
    >>> user_prompt = PromptBrick(
    ...     template="Analyze the following {data_type}: {content}",
    ...     role="user"
    ... )
    >>>
    >>> # Render with variables
    >>> rendered = await user_prompt.execute(
    ...     ExecutionContext(data={"data_type": "JSON", "content": "..."})
    ... )
"""

from __future__ import annotations

from typing import Any

from ..core import AgentBrick, BrickType, ExecutionContext
from .types import PromptTemplate


class PromptBrick(AgentBrick):
    """A brick that holds and manages prompt content.

    PromptBricks can be assembled together to create complex prompts.
    They support both static content and template-based dynamic content.

    Attributes:
        content: Static prompt content.
        template: Template string with {placeholders}.
        role: The role for this prompt (system, user, assistant).
        merge_strategy: How to merge with other prompts.
    """

    BRICK_TYPE = BrickType.PROMPT

    def __init__(
        self,
        content: str | None = None,
        template: str | None = None,
        role: str = "user",
        variables: dict[str, Any] | None = None,
        merge_strategy: str = "append",
        **kwargs: Any,
    ) -> None:
        """Initialize the PromptBrick.

        Args:
            content: Static prompt content.
            template: Template string with {placeholders}.
            role: The role for this prompt (system, user, assistant).
            variables: Default variables for template rendering.
            merge_strategy: How to merge with other prompts (append/prepend/replace).
            **kwargs: Additional arguments for AgentBrick.

        Raises:
            ValueError: If neither content nor template is provided.
        """
        super().__init__(**kwargs)

        if content is None and template is None:
            raise ValueError("Either content or template must be provided")

        self.content = content
        self.template = template
        self.role = role
        self.variables = variables or {}
        self.merge_strategy = merge_strategy

        # Create internal template if needed
        self._prompt_template: PromptTemplate | None
        if template:
            self._prompt_template = PromptTemplate(
                template=template,
                variables=self.variables,
            )
        else:
            self._prompt_template = None

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute the prompt brick to generate prompt content.

        Args:
            context: Execution context containing variables for template rendering.

        Returns:
            Dictionary containing:
                - content: The rendered prompt content
                - role: The role for this prompt
                - metadata: Additional prompt metadata
        """
        # Render content
        if self._prompt_template:
            # Merge context data with default variables
            render_vars = {**self.variables, **context.data}
            rendered_content = self._prompt_template.render(**render_vars)
        else:
            rendered_content = self.content or ""

        # Return prompt data
        return {
            "content": rendered_content,
            "role": self.role,
            "metadata": {
                "brick_id": self.id,
                "merge_strategy": self.merge_strategy,
                "has_template": self._prompt_template is not None,
            },
        }

    def set_variables(self, **variables: Any) -> None:
        """Update default variables for template rendering.

        Args:
            **variables: Variables to update.
        """
        self.variables.update(variables)
        if self._prompt_template:
            self._prompt_template.variables.update(variables)

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> PromptBrick:
        """Create a PromptBrick from configuration.

        Args:
            config: Configuration dictionary.

        Returns:
            Configured PromptBrick instance.
        """
        # Extract prompt-specific parameters
        content = config.get("content")
        template = config.get("template")
        role = config.get("role", "user")
        variables = config.get("variables", {})
        merge_strategy = config.get("merge_strategy", "append")

        # Create instance
        return cls(
            content=content,
            template=template,
            role=role,
            variables=variables,
            merge_strategy=merge_strategy,
            brick_id=config.get("id"),
            name=config.get("name"),
            metadata=config.get("metadata"),
        )

    def __repr__(self) -> str:
        """String representation of the PromptBrick."""
        content_info = "template" if self._prompt_template else "static"
        return f"PromptBrick(id={self.id}, role={self.role}, type={content_info})"


class PromptAssembler:
    """Utility class for assembling multiple PromptBricks into a single prompt.

    This is typically used by nodes to combine multiple PromptBricks.

    Example:
        >>> assembler = PromptAssembler()
        >>> prompts = [system_prompt, user_prompt]
        >>> combined = assembler.assemble(prompts, context)
    """

    @staticmethod
    def assemble(
        prompt_bricks: list[PromptBrick],
        context: ExecutionContext,
    ) -> list[dict[str, Any]]:
        """Assemble multiple PromptBricks into a prompt list.

        Args:
            prompt_bricks: List of PromptBricks to assemble.
            context: Execution context for rendering templates.

        Returns:
            List of prompt dictionaries ready for LLM consumption.
        """
        assembled: list[dict[str, Any]] = []

        for brick in prompt_bricks:
            # Execute brick synchronously (it's a simple operation)
            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're already in an async context
                import nest_asyncio

                nest_asyncio.apply()

            result = asyncio.run(brick.execute(context))

            # Handle merge strategies
            if result["metadata"]["merge_strategy"] == "replace":
                # Replace all prompts with the same role
                assembled = [p for p in assembled if p.get("role") != result["role"]]
                assembled.append(result)
            elif result["metadata"]["merge_strategy"] == "prepend":
                # Find the first prompt with the same role and prepend
                found = False
                for i, prompt in enumerate(assembled):
                    if prompt.get("role") == result["role"]:
                        assembled[i]["content"] = (
                            result["content"] + "\n" + prompt["content"]
                        )
                        found = True
                        break
                if not found:
                    assembled.append(result)
            else:  # append (default)
                # Find the last prompt with the same role and append
                found = False
                for i in range(len(assembled) - 1, -1, -1):
                    if assembled[i].get("role") == result["role"]:
                        assembled[i]["content"] = (
                            assembled[i]["content"] + "\n" + result["content"]
                        )
                        found = True
                        break
                if not found:
                    assembled.append(result)

        return assembled
