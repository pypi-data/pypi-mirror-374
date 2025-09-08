"""Example demonstrating multi-provider LLM comparison."""

import asyncio
import os
from typing import Any

from bag.core import (
    AgentBrick,
    AgentGraph,
    AgentNode,
    BrickType,
    ExecutionContext,
    GraphConfig,
    LiteLLMConfig,
)


class MultiProviderPromptBrick(AgentBrick):
    """Brick that tests the same prompt across multiple LLM providers."""

    def __init__(
        self,
        brick_id: str = "multi_provider_prompt",
        prompt: str = "",
        models: list[str] | None = None,
    ):
        super().__init__(brick_id=brick_id, name="Multi-Provider Prompt Brick")
        self.prompt = prompt
        self.models = models or ["gpt-4", "claude-3-5-sonnet-20241022"]

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute the same prompt across multiple models."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager available"}

        results = {}
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self.prompt},
        ]

        for model in self.models:
            try:
                print(f"  Testing model: {model}")
                response = await context.litellm_manager.complete(messages, model=model)

                content = response.choices[0].message.content
                usage = response.usage.model_dump() if response.usage else {}

                results[model] = {
                    "content": content,
                    "usage": usage,
                    "model": response.model,
                    "success": True,
                }

            except Exception as e:
                results[model] = {
                    "error": str(e),
                    "success": False,
                }

        return {"results": results, "prompt": self.prompt}


class ComparisonAnalysisBrick(AgentBrick):
    """Brick that analyzes the differences between model responses."""

    def __init__(self, brick_id: str = "comparison_analysis"):
        super().__init__(brick_id=brick_id, name="Comparison Analysis Brick")

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Analyze the comparison results from previous brick."""
        # Get results from previous node
        previous_results = context.agent_context.get("multi_provider_results")
        if not previous_results:
            return {"error": "No comparison results found in context"}

        analysis = {
            "total_models_tested": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "token_usage_comparison": {},
            "response_lengths": {},
            "errors": {},
        }

        results = previous_results.get("results", {})

        for model, result in results.items():
            analysis["total_models_tested"] += 1

            if result.get("success"):
                analysis["successful_responses"] += 1
                usage = result.get("usage", {})
                content = result.get("content", "")

                analysis["token_usage_comparison"][model] = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
                analysis["response_lengths"][model] = len(content)
            else:
                analysis["failed_responses"] += 1
                analysis["errors"][model] = result.get("error", "Unknown error")

        return analysis


async def main():
    """Demonstrate multi-provider LLM comparison."""

    # Create LiteLLM configuration
    litellm_config = LiteLLMConfig(
        models=[
            {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            {
                "model": "claude-3-5-sonnet-20241022",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 1000,
                "custom_llm_provider": "anthropic",
            },
        ],
        default_model="gpt-4",
        enable_fallback=True,
    )

    # Create graph configuration
    graph_config = GraphConfig(
        max_iterations=10,
        litellm_config=litellm_config,
    )

    # Create graph
    graph = AgentGraph(
        name="Multi-Provider Comparison Graph",
        config=graph_config,
    )

    # Test prompt
    test_prompt = (
        "Explain the concept of artificial intelligence in exactly 3 sentences. "
        "Make sure to mention both machine learning and neural networks."
    )

    # Create comparison node
    comparison_node = AgentNode(node_id="comparison")
    comparison_node.add_brick(
        MultiProviderPromptBrick(
            brick_id="multi_test",
            prompt=test_prompt,
            models=["gpt-4", "claude-3-5-sonnet-20241022"],
        )
    )

    # Create analysis node
    analysis_node = AgentNode(node_id="analysis")
    analysis_node.add_brick(ComparisonAnalysisBrick())

    # Add nodes to graph
    graph.add_node(comparison_node)
    graph.add_node(analysis_node)
    graph.add_edge("comparison", "analysis")

    # Execute the graph
    print("🚀 Starting multi-provider comparison...")
    print(f"Test prompt: {test_prompt}")
    print()

    context = await graph.execute()

    # Display detailed results
    print("\n" + "=" * 60)
    print("DETAILED RESULTS")
    print("=" * 60)

    # Show comparison results
    comparison_results = context.node_outputs.get("comparison", {})
    for _brick_id, output in comparison_results.items():
        if "results" in output:
            results = output["results"]
            for model, result in results.items():
                print(f"\n📱 Model: {model}")
                print("-" * 40)
                if result.get("success"):
                    content = result["content"]
                    usage = result.get("usage", {})
                    print(f"Response: {content}")
                    print(f"Tokens: {usage.get('total_tokens', 'N/A')}")
                else:
                    print(f"❌ Error: {result.get('error')}")

    # Show analysis results
    print(f"\n{'='*60}")
    print("ANALYSIS SUMMARY")
    print("=" * 60)

    analysis_results = context.node_outputs.get("analysis", {})
    for _brick_id, analysis in analysis_results.items():
        if "error" not in analysis:
            print(f"Models tested: {analysis['total_models_tested']}")
            print(f"Successful: {analysis['successful_responses']}")
            print(f"Failed: {analysis['failed_responses']}")

            print("\n📊 Token Usage Comparison:")
            for model, usage in analysis["token_usage_comparison"].items():
                print(f"  {model}: {usage['total_tokens']} tokens")

            print("\n📏 Response Length Comparison:")
            for model, length in analysis["response_lengths"].items():
                print(f"  {model}: {length} characters")

            if analysis["errors"]:
                print("\n❌ Errors:")
                for model, error in analysis["errors"].items():
                    print(f"  {model}: {error}")


if __name__ == "__main__":
    # Check for required API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        exit(1)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        exit(1)

    # Run the example
    asyncio.run(main())
