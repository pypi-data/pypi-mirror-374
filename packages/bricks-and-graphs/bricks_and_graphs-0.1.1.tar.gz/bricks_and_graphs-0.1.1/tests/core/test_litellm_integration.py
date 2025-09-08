"""Tests for LiteLLM integration with AgentGraph."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bag.core import (
    AgentBrick,
    AgentGraph,
    AgentNode,
    BrickType,
    ExecutionContext,
    GraphConfig,
    LiteLLMConfig,
    LiteLLMManager,
    LiteLLMModelConfig,
)


class MockLLMBrick(AgentBrick):
    """Mock brick that uses LiteLLM."""

    def __init__(self, brick_id: str = "mock_llm"):
        super().__init__(brick_id=brick_id)

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict:
        """Execute using LiteLLM manager."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager"}

        # Verify it's a LiteLLMManager instance
        if not isinstance(context.litellm_manager, LiteLLMManager):
            return {"error": "Invalid LiteLLM manager type"}

        return {
            "has_manager": True,
            "default_model": context.litellm_manager.default_model,
            "available_models": context.litellm_manager.get_available_models(),
        }


class TestLiteLLMIntegration:
    """Test LiteLLM integration with AgentGraph."""

    def test_litellm_config_creation(self):
        """Test creating LiteLLM configuration."""
        model_config = LiteLLMModelConfig(
            model="gpt-4",
            api_key="test-key",
            temperature=0.5,
            max_tokens=1000,
        )

        litellm_config = LiteLLMConfig(
            models=[model_config],
            default_model="gpt-4",
            enable_caching=True,
            cache_ttl=1800,
        )

        assert len(litellm_config.models) == 1
        assert litellm_config.default_model == "gpt-4"
        assert litellm_config.enable_caching is True
        assert litellm_config.get_default_model_config().model == "gpt-4"

    def test_litellm_config_multiple_models(self):
        """Test LiteLLM config with multiple models."""
        models = [
            LiteLLMModelConfig(model="gpt-4", temperature=0.7),
            LiteLLMModelConfig(model="claude-3-sonnet-20240229", temperature=0.5),
            LiteLLMModelConfig(model="claude-3-5-sonnet-20241022", temperature=0.8),
        ]

        litellm_config = LiteLLMConfig(
            models=models,
            default_model="claude-3-5-sonnet-20241022",
            fallback_order=[
                "claude-3-5-sonnet-20241022",
                "gpt-4",
                "claude-3-sonnet-20240229",
            ],
        )

        assert len(litellm_config.models) == 3
        assert litellm_config.get_model_config("gpt-4").temperature == 0.7
        assert litellm_config.get_model_config("nonexistent") is None
        assert (
            litellm_config.get_default_model_config().model
            == "claude-3-5-sonnet-20241022"
        )

    @patch("bag.core.litellm_manager.litellm")
    def test_litellm_manager_initialization(self, mock_litellm):
        """Test LiteLLM manager initialization."""
        litellm_config = LiteLLMConfig(
            models=[
                LiteLLMModelConfig(model="gpt-4", api_key="openai-key"),
                LiteLLMModelConfig(model="claude-3-sonnet", api_key="anthropic-key"),
            ],
            enable_caching=True,
            log_level="DEBUG",
        )

        manager = LiteLLMManager(litellm_config)

        assert manager.config == litellm_config
        assert manager._initialized is True
        assert manager.default_model == "gpt-4"
        assert manager.get_available_models() == ["gpt-4", "claude-3-sonnet"]

    def test_graph_with_litellm_config(self):
        """Test creating graph with LiteLLM configuration."""
        litellm_config = LiteLLMConfig(models=[LiteLLMModelConfig(model="gpt-4")])

        graph_config = GraphConfig(
            max_iterations=5,
            litellm_config=litellm_config,
        )

        graph = AgentGraph(
            name="Test Graph",
            config=graph_config,
        )

        assert graph.litellm_manager is not None
        assert isinstance(graph.litellm_manager, LiteLLMManager)
        assert graph.litellm_manager.config == litellm_config

    def test_graph_without_litellm_config(self):
        """Test graph without LiteLLM configuration."""
        graph = AgentGraph(name="Test Graph")
        assert graph.litellm_manager is None

    def test_litellm_manager_propagation_to_nodes(self):
        """Test that LiteLLM manager propagates to nodes."""
        litellm_config = LiteLLMConfig(models=[LiteLLMModelConfig(model="gpt-4")])

        graph_config = GraphConfig(litellm_config=litellm_config)
        graph = AgentGraph(config=graph_config)

        node = AgentNode(node_id="test_node")
        graph.add_node(node)

        # Verify node has access to LiteLLM manager
        assert node.litellm_manager is not None
        assert node.litellm_manager == graph.litellm_manager

    @pytest.mark.asyncio
    async def test_litellm_manager_in_execution_context(self):
        """Test that LiteLLM manager is available in execution context."""
        litellm_config = LiteLLMConfig(models=[LiteLLMModelConfig(model="gpt-4")])

        graph_config = GraphConfig(litellm_config=litellm_config)
        graph = AgentGraph(config=graph_config)

        # Create node with mock LLM brick
        node = AgentNode(node_id="llm_node")
        node.add_brick(MockLLMBrick())
        graph.add_node(node)

        # Execute graph
        context = await graph.execute()

        # Verify LiteLLM manager was available
        output = context.node_outputs["llm_node"]["mock_llm"]
        assert output["has_manager"] is True
        assert output["default_model"] == "gpt-4"
        assert "gpt-4" in output["available_models"]

    @pytest.mark.asyncio
    async def test_litellm_complete_method(self):
        """Test LiteLLM manager complete method."""
        litellm_config = LiteLLMConfig(
            models=[LiteLLMModelConfig(model="gpt-4", temperature=0.5)]
        )

        manager = LiteLLMManager(litellm_config)

        # Mock the completion function
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_response.model = "gpt-4"

        with patch(
            "bag.core.litellm_manager.acompletion", new_callable=AsyncMock
        ) as mock_completion:
            mock_completion.return_value = mock_response

            messages = [{"role": "user", "content": "Hello"}]
            response = await manager.complete(messages)
            assert response is not None

            # Verify completion was called with correct parameters
            mock_completion.assert_called_once()
            call_args = mock_completion.call_args[1]
            assert call_args["model"] == "gpt-4"
            assert call_args["messages"] == messages
            assert call_args["temperature"] == 0.5

    @pytest.mark.asyncio
    async def test_litellm_complete_with_override(self):
        """Test LiteLLM complete with parameter override."""
        litellm_config = LiteLLMConfig(
            models=[
                LiteLLMModelConfig(model="gpt-4", temperature=0.7),
                LiteLLMModelConfig(model="claude-3", temperature=0.5),
            ]
        )

        manager = LiteLLMManager(litellm_config)

        with patch(
            "bag.core.litellm_manager.acompletion", new_callable=AsyncMock
        ) as mock_completion:
            mock_response = MagicMock()
            mock_completion.return_value = mock_response

            messages = [{"role": "user", "content": "Hello"}]
            await manager.complete(
                messages,
                model_name="claude-3",
                temperature=0.9,  # Override temperature
            )

            # Verify override worked
            call_args = mock_completion.call_args[1]
            assert call_args["model"] == "claude-3"
            assert call_args["temperature"] == 0.9  # Overridden value

    def test_litellm_manager_error_handling(self):
        """Test error handling in LiteLLM manager."""
        litellm_config = LiteLLMConfig(models=[LiteLLMModelConfig(model="gpt-4")])
        manager = LiteLLMManager(litellm_config)

        # Test invalid model name
        with pytest.raises(ValueError, match="Model 'invalid-model' not found"):
            import asyncio

            asyncio.run(manager.complete([], model_name="invalid-model"))
