"""LiteLLM integration and management for the agent framework."""

import logging
from typing import Any

import litellm
from litellm import acompletion

from .types import LiteLLMConfig

logger = logging.getLogger(__name__)


class LiteLLMManager:
    """Manages LiteLLM initialization and configuration."""

    def __init__(self, config: LiteLLMConfig):
        """Initialize the LiteLLM manager with configuration.

        Args:
            config: LiteLLM configuration
        """
        self.config = config
        self._initialized = False
        self._initialize()

    def _initialize(self) -> None:
        """Initialize LiteLLM with the provided configuration."""
        # Set global LiteLLM settings
        litellm.set_verbose = self.config.log_level == "DEBUG"

        # Configure caching
        if self.config.enable_caching:
            litellm.cache = litellm.Cache(
                ttl=self.config.cache_ttl,
                type="memory",  # Can be extended to support redis, etc.
            )

        # Set up API keys for each model
        for model_config in self.config.models:
            if model_config.api_key:
                # Set environment variable based on provider
                if (
                    "gpt" in model_config.model.lower()
                    or "openai" in model_config.model.lower()
                ):
                    import os

                    os.environ["OPENAI_API_KEY"] = model_config.api_key
                elif (
                    "claude" in model_config.model.lower()
                    or "anthropic" in model_config.model.lower()
                ):
                    import os

                    os.environ["ANTHROPIC_API_KEY"] = model_config.api_key
                # Add more providers as needed

        # Configure fallback behavior
        if self.config.enable_fallback and self.config.fallback_order:
            litellm.fallbacks = self.config.fallback_order

        self._initialized = True
        logger.info(f"LiteLLM initialized with {len(self.config.models)} models")

    async def complete(
        self,
        messages: list[dict[str, str]],
        model_name: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute a completion request.

        Args:
            messages: List of message dictionaries
            model_name: Optional model name to use (defaults to config default)
            **kwargs: Additional parameters to pass to litellm

        Returns:
            LiteLLM completion response
        """
        if not self._initialized:
            raise RuntimeError("LiteLLM manager not initialized")

        # Get model configuration
        if model_name:
            model_config = self.config.get_model_config(model_name)
            if not model_config:
                raise ValueError(f"Model '{model_name}' not found in configuration")
        else:
            model_config = self.config.get_default_model_config()

        # Prepare completion parameters
        completion_params = {
            "model": model_config.model,
            "messages": messages,
            "temperature": model_config.temperature,
            "timeout": model_config.timeout,
            "num_retries": model_config.max_retries,
        }

        # Add optional parameters
        if model_config.max_tokens:
            completion_params["max_tokens"] = model_config.max_tokens
        if model_config.top_p:
            completion_params["top_p"] = model_config.top_p
        if model_config.api_base:
            completion_params["api_base"] = model_config.api_base
        if model_config.api_version:
            completion_params["api_version"] = model_config.api_version
        if model_config.custom_llm_provider:
            completion_params["custom_llm_provider"] = model_config.custom_llm_provider

        # Add extra parameters
        completion_params.update(model_config.extra_params)

        # Override with any provided kwargs
        completion_params.update(kwargs)

        # Handle system messages for Anthropic models
        if (
            "claude" in model_config.model.lower()
            or "anthropic" in model_config.model.lower()
        ):
            # Extract system message and prepend to first user message for Anthropic
            system_message = None
            filtered_messages = []

            for message in messages:
                if message.get("role") == "system":
                    system_message = message["content"]
                else:
                    filtered_messages.append(message)

            if system_message and filtered_messages:
                # Find the first user message and prepend system instructions
                for i, message in enumerate(filtered_messages):
                    if message.get("role") == "user":
                        filtered_messages[i] = {
                            "role": "user",
                            "content": f"{system_message}\n\n{message['content']}",
                        }
                        break
                completion_params["messages"] = filtered_messages
            else:
                completion_params["messages"] = messages
        else:
            completion_params["messages"] = messages

        # Execute completion
        try:
            response = await acompletion(**completion_params)
            return response
        except Exception as e:
            logger.error(f"LiteLLM completion error: {e}")
            raise

    def get_available_models(self) -> list[str]:
        """Get list of available model names."""
        return [model.model for model in self.config.models]

    @property
    def default_model(self) -> str:
        """Get the default model name."""
        return self.config.get_default_model_config().model
