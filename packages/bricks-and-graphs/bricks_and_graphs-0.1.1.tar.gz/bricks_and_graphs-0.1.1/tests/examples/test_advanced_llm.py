"""Tests for advanced LLM examples with comprehensive mocking."""

# Import the example bricks
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from bag.core import ExecutionContext

# Add examples to path before importing
examples_path = Path(__file__).parent.parent.parent / "examples" / "advanced_llm"
sys.path.insert(0, str(examples_path))

# Import example modules (after path setup)
from multi_provider_comparison import (  # noqa: E402
    ComparisonAnalysisBrick,
    MultiProviderPromptBrick,
)
from reasoning_chain import (  # noqa: E402
    EvaluationBrick,
    ImplementationPlanBrick,
    ProblemAnalysisBrick,
    SolutionGenerationBrick,
)
from robust_llm_usage import ErrorAnalysisBrick, RobustLLMBrick  # noqa: E402


class TestMultiProviderComparison:
    """Test multi-provider comparison functionality."""

    @pytest.fixture
    def mock_litellm_manager(self):
        """Create a mock LiteLLM manager."""
        manager = MagicMock()
        manager.complete = AsyncMock()
        return manager

    @pytest.fixture
    def execution_context(self, mock_litellm_manager):
        """Create execution context with mocked LiteLLM manager."""
        from bag.core.types import AgentContext

        context = ExecutionContext()
        context.litellm_manager = mock_litellm_manager
        context.agent_context = AgentContext()
        return context

    @pytest.fixture
    def mock_responses(self):
        """Create mock responses for different models."""
        return {
            "gpt-4": {
                "content": (
                    "GPT-4 response about AI: Machine learning uses " "neural networks."
                ),
                "model": "gpt-4",
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 15,
                    "total_tokens": 35,
                },
            },
            "claude-3-5-sonnet-20241022": {
                "content": (
                    "Claude response about AI: Artificial intelligence "
                    "leverages neural networks."
                ),
                "model": "claude-3-5-sonnet-20241022",
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 16,
                    "total_tokens": 36,
                },
            },
        }

    @pytest.mark.asyncio
    async def test_multi_provider_brick_success(
        self, execution_context, mock_responses
    ):
        """Test successful multi-provider comparison."""

        # Setup mock responses
        def mock_complete(messages, model=None, **kwargs):
            response = MagicMock()
            response.choices = [
                MagicMock(message=MagicMock(content=mock_responses[model]["content"]))
            ]
            response.model = mock_responses[model]["model"]
            response.usage = MagicMock()
            response.usage.model_dump.return_value = mock_responses[model]["usage"]
            return response

        execution_context.litellm_manager.complete.side_effect = mock_complete

        # Create and execute brick
        brick = MultiProviderPromptBrick(
            prompt="Explain AI", models=["gpt-4", "claude-3-5-sonnet-20241022"]
        )

        result = await brick.execute(execution_context)

        # Verify results
        assert "results" in result
        assert "gpt-4" in result["results"]
        assert "claude-3-5-sonnet-20241022" in result["results"]

        # Verify GPT-4 result
        gpt4_result = result["results"]["gpt-4"]
        assert gpt4_result["success"] is True
        assert "GPT-4 response" in gpt4_result["content"]
        assert gpt4_result["usage"]["total_tokens"] == 35

        # Verify Claude result
        claude_result = result["results"]["claude-3-5-sonnet-20241022"]
        assert claude_result["success"] is True
        assert "Claude response" in claude_result["content"]
        assert claude_result["usage"]["total_tokens"] == 36

    @pytest.mark.asyncio
    async def test_multi_provider_brick_partial_failure(self, execution_context):
        """Test multi-provider comparison with partial failures."""

        def mock_complete(messages, model=None, **kwargs):
            if model == "gpt-4":
                response = MagicMock()
                response.choices = [
                    MagicMock(message=MagicMock(content="GPT-4 success"))
                ]
                response.model = "gpt-4"
                response.usage = MagicMock()
                response.usage.model_dump.return_value = {"total_tokens": 30}
                return response
            else:
                raise Exception("Claude API error")

        execution_context.litellm_manager.complete.side_effect = mock_complete

        brick = MultiProviderPromptBrick(models=["gpt-4", "claude-3-5-sonnet-20241022"])

        result = await brick.execute(execution_context)

        # Verify mixed results
        assert result["results"]["gpt-4"]["success"] is True
        assert result["results"]["claude-3-5-sonnet-20241022"]["success"] is False
        assert "error" in result["results"]["claude-3-5-sonnet-20241022"]

    @pytest.mark.asyncio
    async def test_multi_provider_brick_no_manager(self):
        """Test multi-provider brick without LiteLLM manager."""
        context = ExecutionContext()  # No LiteLLM manager
        brick = MultiProviderPromptBrick()

        result = await brick.execute(context)
        assert "error" in result
        assert "No LiteLLM manager available" in result["error"]

    @pytest.mark.asyncio
    async def test_comparison_analysis_brick_success(self):
        """Test comparison analysis brick with valid data."""
        from bag.core.types import AgentContext

        context = ExecutionContext()
        context.agent_context = AgentContext()
        context.agent_context["multi_provider_results"] = {
            "results": {
                "gpt-4": {
                    "success": True,
                    "content": "Short response",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                },
                "claude-3-5-sonnet-20241022": {
                    "success": False,
                    "error": "Rate limit exceeded",
                },
            }
        }

        brick = ComparisonAnalysisBrick()
        result = await brick.execute(context)  # Async method

        assert result["total_models_tested"] == 2
        assert result["successful_responses"] == 1
        assert result["failed_responses"] == 1
        assert "gpt-4" in result["token_usage_comparison"]
        assert result["token_usage_comparison"]["gpt-4"]["total_tokens"] == 15
        assert result["response_lengths"]["gpt-4"] == len("Short response")
        assert "Rate limit exceeded" in result["errors"]["claude-3-5-sonnet-20241022"]


class TestReasoningChain:
    """Test reasoning chain functionality."""

    @pytest.fixture
    def execution_context_with_manager(self):
        """Create execution context with mocked LiteLLM manager."""
        from bag.core.types import AgentContext

        context = ExecutionContext()
        context.litellm_manager = MagicMock()
        context.litellm_manager.complete = AsyncMock()
        context.agent_context = AgentContext()
        return context

    @pytest.mark.asyncio
    async def test_problem_analysis_brick(self, execution_context_with_manager):
        """Test problem analysis brick."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Problem breakdown: 1. Issue A 2. Issue B")
            )
        ]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {"total_tokens": 100}

        execution_context_with_manager.litellm_manager.complete.return_value = (
            mock_response
        )

        brick = ProblemAnalysisBrick(problem="Complex business problem")
        result = await brick.execute(execution_context_with_manager)

        assert "analysis" in result
        assert "Problem breakdown" in result["analysis"]
        assert result["model_used"] == "claude-3-5-sonnet-20241022"
        assert (
            execution_context_with_manager.agent_context["problem_analysis"]
            == result["analysis"]
        )

    @pytest.mark.asyncio
    async def test_solution_generation_brick(self, execution_context_with_manager):
        """Test solution generation brick."""
        # Setup context with analysis
        execution_context_with_manager.agent_context["problem_analysis"] = (
            "Analysis: Problem has 3 components"
        )

        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Solution 1: Approach A\nSolution 2: Approach B"
                )
            )
        ]
        mock_response.model = "gpt-4"
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {"total_tokens": 150}

        execution_context_with_manager.litellm_manager.complete.return_value = (
            mock_response
        )

        brick = SolutionGenerationBrick()
        result = await brick.execute(execution_context_with_manager)

        assert "solutions" in result
        assert "Solution 1" in result["solutions"]
        assert result["model_used"] == "gpt-4"
        assert (
            execution_context_with_manager.agent_context["solutions"]
            == result["solutions"]
        )

    @pytest.mark.asyncio
    async def test_solution_generation_brick_no_analysis(
        self, execution_context_with_manager
    ):
        """Test solution generation brick without prior analysis."""
        brick = SolutionGenerationBrick()
        result = await brick.execute(execution_context_with_manager)

        assert "error" in result
        assert "No problem analysis found" in result["error"]

    @pytest.mark.asyncio
    async def test_evaluation_brick(self, execution_context_with_manager):
        """Test evaluation brick."""
        # Setup context with analysis and solutions
        execution_context_with_manager.agent_context.update(
            {
                "problem_analysis": "Problem has 3 components",
                "solutions": "Solution 1: A\nSolution 2: B",
            }
        )

        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Ranking: Solution 1 is best"))
        ]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {"total_tokens": 200}

        execution_context_with_manager.litellm_manager.complete.return_value = (
            mock_response
        )

        brick = EvaluationBrick()
        result = await brick.execute(execution_context_with_manager)

        assert "evaluation" in result
        assert "Ranking" in result["evaluation"]
        assert result["model_used"] == "claude-3-5-sonnet-20241022"

    @pytest.mark.asyncio
    async def test_implementation_plan_brick(self, execution_context_with_manager):
        """Test implementation plan brick."""
        # Setup context with evaluation
        execution_context_with_manager.agent_context["evaluation"] = (
            "Solution 1 is recommended"
        )

        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content="Phase 1: Setup\nPhase 2: Implementation")
            )
        ]
        mock_response.model = "gpt-4"
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {"total_tokens": 250}

        execution_context_with_manager.litellm_manager.complete.return_value = (
            mock_response
        )

        brick = ImplementationPlanBrick()
        result = await brick.execute(execution_context_with_manager)

        assert "plan" in result
        assert "Phase 1" in result["plan"]
        assert result["model_used"] == "gpt-4"


class TestRobustLLMUsage:
    """Test robust LLM usage functionality."""

    @pytest.fixture
    def execution_context_with_manager(self):
        """Create execution context with mocked LiteLLM manager."""
        from bag.core.types import AgentContext

        context = ExecutionContext()
        context.litellm_manager = MagicMock()
        context.litellm_manager.complete = AsyncMock()
        context.agent_context = AgentContext()
        return context

    @pytest.mark.asyncio
    async def test_robust_llm_brick_success_first_try(
        self, execution_context_with_manager
    ):
        """Test robust LLM brick succeeding on first try."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Success response"))
        ]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage = MagicMock()
        mock_response.usage.model_dump.return_value = {"total_tokens": 50}

        execution_context_with_manager.litellm_manager.complete.return_value = (
            mock_response
        )

        brick = RobustLLMBrick(prompt="Test prompt")
        result = await brick.execute(execution_context_with_manager)

        assert result["success"] is True
        assert result["content"] == "Success response"
        assert result["total_attempts"] == 1
        assert len(result["attempts"]) == 1
        assert result["attempts"][0]["success"] is True

    @pytest.mark.asyncio
    async def test_robust_llm_brick_retry_then_success(
        self, execution_context_with_manager
    ):
        """Test robust LLM brick failing then succeeding on retry."""
        call_count = 0

        def mock_complete(messages, model=None, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary error")
            else:
                response = MagicMock()
                response.choices = [
                    MagicMock(message=MagicMock(content="Success after retry"))
                ]
                response.model = model
                response.usage = MagicMock()
                response.usage.model_dump.return_value = {"total_tokens": 60}
                return response

        execution_context_with_manager.litellm_manager.complete.side_effect = (
            mock_complete
        )

        brick = RobustLLMBrick(
            prompt="Test prompt",
            preferred_model="claude-3-5-sonnet-20241022",
            max_retries=2,
        )
        result = await brick.execute(execution_context_with_manager)

        assert result["success"] is True
        assert result["content"] == "Success after retry"
        assert result["total_attempts"] == 2
        assert result["attempts"][0]["success"] is False
        assert result["attempts"][1]["success"] is True

    @pytest.mark.asyncio
    async def test_robust_llm_brick_fallback_to_different_model(
        self, execution_context_with_manager
    ):
        """Test robust LLM brick falling back to different model."""

        def mock_complete(messages, model=None, **kwargs):
            if model == "claude-3-5-sonnet-20241022":
                raise Exception("Claude error")
            else:  # GPT-4
                response = MagicMock()
                response.choices = [
                    MagicMock(message=MagicMock(content="GPT-4 fallback success"))
                ]
                response.model = "gpt-4"
                response.usage = MagicMock()
                response.usage.model_dump.return_value = {"total_tokens": 70}
                return response

        execution_context_with_manager.litellm_manager.complete.side_effect = (
            mock_complete
        )

        brick = RobustLLMBrick(
            prompt="Test prompt",
            preferred_model="claude-3-5-sonnet-20241022",
            fallback_models=["gpt-4"],
            max_retries=1,
        )
        result = await brick.execute(execution_context_with_manager)

        assert result["success"] is True
        assert result["content"] == "GPT-4 fallback success"
        assert result["model_used"] == "gpt-4"
        # Should have 1 failed attempt for Claude + 1 successful for GPT-4
        assert result["total_attempts"] == 2

    @pytest.mark.asyncio
    async def test_robust_llm_brick_all_failures(self, execution_context_with_manager):
        """Test robust LLM brick when all attempts fail."""
        execution_context_with_manager.litellm_manager.complete.side_effect = Exception(
            "All models failed"
        )

        brick = RobustLLMBrick(
            prompt="Test prompt",
            preferred_model="claude-3-5-sonnet-20241022",
            fallback_models=["gpt-4"],
            max_retries=2,
        )
        result = await brick.execute(execution_context_with_manager)

        assert result["success"] is False
        assert "All models and retries failed" in result["error"]
        # Should have 2 models * 2 retries each = 4 attempts
        assert result["total_attempts"] == 4
        assert all(not attempt["success"] for attempt in result["attempts"])

    @pytest.mark.asyncio
    async def test_error_analysis_brick_success(self):
        """Test error analysis brick with valid attempt data."""
        context = ExecutionContext()
        # Mock node outputs with attempt data
        context.node_outputs = {
            "test_node": {
                "robust_llm": {
                    "attempts": [
                        {
                            "model": "claude-3-5-sonnet-20241022",
                            "retry": 1,
                            "success": False,
                            "error_type": "TimeoutError",
                        },
                        {
                            "model": "claude-3-5-sonnet-20241022",
                            "retry": 2,
                            "success": False,
                            "error_type": "RateLimitError",
                        },
                        {
                            "model": "gpt-4",
                            "retry": 1,
                            "success": True,
                            "usage": {"total_tokens": 100},
                        },
                    ]
                }
            }
        }

        brick = ErrorAnalysisBrick()
        result = await brick.execute(context)  # Async method

        assert result["total_attempts"] == 3
        assert result["successful_attempts"] == 1
        assert result["failed_attempts"] == 2
        assert "claude-3-5-sonnet-20241022" in result["models_tried"]
        assert "gpt-4" in result["models_tried"]
        assert result["error_types"]["TimeoutError"] == 1
        assert result["error_types"]["RateLimitError"] == 1
        assert result["success_rate_by_model"]["gpt-4"]["rate"] == 1.0
        assert (
            result["success_rate_by_model"]["claude-3-5-sonnet-20241022"]["rate"] == 0.0
        )

    @pytest.mark.asyncio
    async def test_error_analysis_brick_no_data(self):
        """Test error analysis brick without attempt data."""
        context = ExecutionContext()
        context.node_outputs = {}

        brick = ErrorAnalysisBrick()
        result = await brick.execute(context)

        assert "error" in result
        assert "No attempt data found" in result["error"]


@pytest.mark.asyncio
async def test_integration_example_imports():
    """Test that example modules can be imported without errors."""
    # This test ensures our examples are syntactically correct
    # and can be imported without runtime errors

    # Test imports work
    assert MultiProviderPromptBrick is not None
    assert ComparisonAnalysisBrick is not None
    assert ProblemAnalysisBrick is not None
    assert SolutionGenerationBrick is not None
    assert EvaluationBrick is not None
    assert ImplementationPlanBrick is not None
    assert RobustLLMBrick is not None
    assert ErrorAnalysisBrick is not None

    # Test basic instantiation works
    brick1 = MultiProviderPromptBrick(prompt="test")
    assert brick1.prompt == "test"

    brick2 = RobustLLMBrick(prompt="test", max_retries=1)
    assert brick2.max_retries == 1
