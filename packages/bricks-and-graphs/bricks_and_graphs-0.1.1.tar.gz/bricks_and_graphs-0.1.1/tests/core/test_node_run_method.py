"""Tests for the AgentNode.run() method."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from bag.core import (
    AgentBrick,
    AgentContext,
    AgentNode,
    BrickType,
    ExecutionContext,
    LiteLLMManager,
    RoutingDecision,
)


class MockPromptBrick(AgentBrick):
    """Mock prompt brick for testing."""

    def __init__(self, brick_id: str, content: str, role: str = "user"):
        super().__init__(brick_id=brick_id)
        self.content = content
        self.role = role

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROMPT

    async def execute(self, context: ExecutionContext) -> dict:
        """Return prompt message."""
        return {
            "message": {"role": self.role, "content": self.content},
            "role": self.role,
            "content": self.content,
        }


class MockProcessorBrick(AgentBrick):
    """Mock processor brick for testing."""

    def __init__(self, brick_id: str, process_fn=None):
        super().__init__(brick_id=brick_id)
        self.process_fn = process_fn or (lambda x: {"processed": x})

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict:
        """Process the input from context."""
        # Get input from context
        input_data = context.agent_context.get("_current_processor_input")

        # Store input for verification
        context.agent_context[f"{self.id}_input"] = input_data

        # Process
        result = self.process_fn(input_data)

        # Store output
        context.agent_context[f"{self.id}_output"] = result

        return result


class MockRouterBrick(AgentBrick):
    """Mock router brick for testing."""

    def __init__(self, brick_id: str, routing_fn=None):
        super().__init__(brick_id=brick_id)
        self.routing_fn = routing_fn or (lambda x: "next_node")

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ROUTER

    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        """Route based on input."""
        # Get input from context
        input_data = context.agent_context.get("_current_router_input")

        # Store input for verification
        context.agent_context[f"{self.id}_input"] = input_data

        # Determine routing
        next_node = self.routing_fn(input_data)

        if next_node is None:
            return RoutingDecision(next_node_id=None, should_terminate=True)

        return RoutingDecision(
            next_node_id=next_node, metadata={"input": input_data, "confidence": 0.9}
        )


class TestNodeRunMethod:
    """Test the node run method."""

    @pytest.mark.asyncio
    async def test_run_with_prompts_only(self):
        """Test run with only prompt bricks."""
        # Create node with prompt bricks
        node = AgentNode(node_id="test_node")
        node.add_brick(
            MockPromptBrick("system", "You are a helpful assistant", "system")
        )
        node.add_brick(MockPromptBrick("user", "Hello, how are you?", "user"))

        # Create mock LiteLLM manager
        mock_manager = MagicMock(spec=LiteLLMManager)
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="I'm doing well!"))
        ]
        mock_manager.complete = AsyncMock(return_value=mock_response)
        node._litellm_manager = mock_manager

        # Create context
        context = ExecutionContext(agent_context=AgentContext())

        # Run the node
        result = await node.run(context)

        # Verify LLM was called with correct messages
        mock_manager.complete.assert_called_once()
        messages = mock_manager.complete.call_args[0][0]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hello, how are you?"

        # Verify outputs stored in context
        assert "test_node" in context.node_outputs
        assert "_llm_completion" in context.node_outputs["test_node"]

        # No router, so result should be None
        assert result is None

    @pytest.mark.asyncio
    async def test_run_without_litellm_manager_raises_error(self):
        """Test that run raises error when prompts exist but no LiteLLM manager."""
        node = AgentNode(node_id="test_node")
        node.add_brick(MockPromptBrick("user", "Hello"))

        context = ExecutionContext(agent_context=AgentContext())

        with pytest.raises(RuntimeError, match="no LiteLLM manager available"):
            await node.run(context)

    @pytest.mark.asyncio
    async def test_run_with_prompt_and_processors(self):
        """Test run with prompts followed by processors."""
        node = AgentNode(node_id="test_node")
        node.add_brick(MockPromptBrick("prompt", "Process this text"))

        # Add processors that transform the data
        node.add_brick(MockProcessorBrick("proc1", lambda x: {"step": 1, "data": x}))
        node.add_brick(MockProcessorBrick("proc2", lambda x: {"step": 2, "prev": x}))

        # Create mock LiteLLM manager
        mock_manager = MagicMock(spec=LiteLLMManager)
        mock_response = MagicMock()
        mock_response.model = "gpt-4"
        mock_manager.complete = AsyncMock(return_value=mock_response)
        node._litellm_manager = mock_manager

        context = ExecutionContext(agent_context=AgentContext())

        # Run the node
        result = await node.run(context)

        # Verify processors received correct inputs
        assert context.agent_context["proc1_input"] == mock_response
        assert context.agent_context["proc2_input"]["step"] == 1
        assert context.agent_context["proc2_input"]["data"] == mock_response

        # Verify final output
        assert context.node_outputs["test_node"]["proc2"]["step"] == 2
        assert result is None  # No router

    @pytest.mark.asyncio
    async def test_run_with_full_pipeline(self):
        """Test run with prompts, processors, and router."""
        node = AgentNode(node_id="test_node")

        # Add bricks
        node.add_brick(MockPromptBrick("prompt", "Analyze this"))
        node.add_brick(
            MockProcessorBrick("processor", lambda x: {"analyzed": True, "data": x})
        )

        # Router that routes based on analysis
        def route(x):
            if isinstance(x, dict) and x.get("analyzed"):
                return "success_node"
            return "failure_node"

        node.add_brick(MockRouterBrick("router", route))

        # Setup LiteLLM
        mock_manager = MagicMock(spec=LiteLLMManager)
        mock_response = MagicMock()
        mock_manager.complete = AsyncMock(return_value=mock_response)
        node._litellm_manager = mock_manager

        context = ExecutionContext(agent_context=AgentContext())

        # Run the node
        result = await node.run(context)

        # Verify routing decision
        assert isinstance(result, RoutingDecision)
        assert result.next_node_id == "success_node"
        assert result.metadata["confidence"] == 0.9
        assert not result.should_terminate

    @pytest.mark.asyncio
    async def test_run_with_processors_only(self):
        """Test run with only processor bricks (no prompts)."""
        node = AgentNode(node_id="test_node")

        # Add processors
        node.add_brick(MockProcessorBrick("proc1", lambda x: {"value": 42}))
        node.add_brick(
            MockProcessorBrick(
                "proc2", lambda x: {"doubled": x.get("value", 0) * 2 if x else 0}
            )
        )

        context = ExecutionContext(agent_context=AgentContext())

        # Run the node
        result = await node.run(context)

        # First processor should get None as input
        assert context.agent_context["proc1_input"] is None

        # Second processor should get first processor's output
        assert context.agent_context["proc2_input"]["value"] == 42
        assert context.node_outputs["test_node"]["proc2"]["doubled"] == 84

        assert result is None

    @pytest.mark.asyncio
    async def test_run_with_router_only(self):
        """Test run with only a router brick."""
        node = AgentNode(node_id="test_node")

        # Router that always terminates
        node.add_brick(MockRouterBrick("router", lambda x: None))

        context = ExecutionContext(agent_context=AgentContext())

        # Run the node
        result = await node.run(context)

        assert isinstance(result, RoutingDecision)
        assert result.next_node_id is None
        assert result.should_terminate

    @pytest.mark.asyncio
    async def test_run_with_llm_error_handling(self):
        """Test run handles LLM errors gracefully."""
        node = AgentNode(node_id="test_node")
        node.add_brick(MockPromptBrick("prompt", "Test"))
        node.add_brick(MockProcessorBrick("processor"))

        # Setup failing LLM
        mock_manager = MagicMock(spec=LiteLLMManager)
        mock_manager.complete = AsyncMock(side_effect=Exception("LLM API Error"))
        node._litellm_manager = mock_manager

        context = ExecutionContext(agent_context=AgentContext())

        # Run should not raise, but pass error to processor
        await node.run(context)

        # Verify error was captured
        llm_output = context.node_outputs["test_node"]["_llm_completion"]
        assert "error" in llm_output
        assert "LLM API Error" in llm_output["error"]

        # Verify processor received error
        proc_input = context.agent_context["processor_input"]
        assert "error" in proc_input

    @pytest.mark.asyncio
    async def test_run_stores_all_outputs(self):
        """Test that run stores all outputs in context correctly."""
        node = AgentNode(node_id="test_node")
        node.add_brick(MockPromptBrick("p1", "First"))
        node.add_brick(MockPromptBrick("p2", "Second"))
        node.add_brick(MockProcessorBrick("proc"))
        node.add_brick(MockRouterBrick("router"))

        # Setup LLM
        mock_manager = MagicMock(spec=LiteLLMManager)
        mock_manager.complete = AsyncMock(return_value=MagicMock())
        node._litellm_manager = mock_manager

        context = ExecutionContext(agent_context=AgentContext())

        await node.run(context)

        # Verify all outputs stored
        outputs = context.node_outputs["test_node"]
        assert "p1" in outputs
        assert "p2" in outputs
        assert "proc" in outputs
        assert "router" in outputs
        assert "_llm_completion" in outputs

        # Verify brick outputs
        assert "p1" in context.brick_outputs
        assert "p2" in context.brick_outputs
        assert "test_node_llm_completion" in context.brick_outputs
