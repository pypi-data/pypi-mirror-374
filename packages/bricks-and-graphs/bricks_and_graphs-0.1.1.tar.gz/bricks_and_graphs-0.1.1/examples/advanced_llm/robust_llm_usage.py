"""Example demonstrating robust LLM usage with error handling and fallbacks."""

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


class RobustLLMBrick(AgentBrick):
    """A brick that demonstrates robust LLM usage with comprehensive error handling."""

    def __init__(
        self,
        brick_id: str = "robust_llm",
        prompt: str = "",
        preferred_model: str = "claude-3-5-sonnet-20241022",
        fallback_models: list[str] | None = None,
        max_retries: int = 3,
    ):
        super().__init__(brick_id=brick_id, name="Robust LLM Brick")
        self.prompt = prompt
        self.preferred_model = preferred_model
        self.fallback_models = fallback_models or ["gpt-4", "claude-3-sonnet-20240229"]
        self.max_retries = max_retries

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute with robust error handling and fallback strategies."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager available"}

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self.prompt},
        ]

        # Track all attempts
        attempts = []
        models_to_try = [self.preferred_model] + self.fallback_models

        for model in models_to_try:
            for retry in range(self.max_retries):
                attempt_info = {
                    "model": model,
                    "retry": retry + 1,
                    "timestamp": asyncio.get_event_loop().time(),
                }

                try:
                    print(
                        f"  🔄 Attempting {model} "
                        f"(retry {retry + 1}/{self.max_retries})"
                    )

                    response = await context.litellm_manager.complete(
                        messages, model=model, timeout=30
                    )

                    # Success!
                    content = response.choices[0].message.content
                    usage = response.usage.model_dump() if response.usage else {}

                    attempt_info.update(
                        {
                            "success": True,
                            "content": content,
                            "usage": usage,
                            "actual_model": response.model,
                        }
                    )
                    attempts.append(attempt_info)

                    print(f"  ✅ Success with {model}")

                    return {
                        "content": content,
                        "model_used": response.model,
                        "usage": usage,
                        "attempts": attempts,
                        "total_attempts": len(attempts),
                        "success": True,
                    }

                except Exception as e:
                    error_msg = str(e)
                    attempt_info.update(
                        {
                            "success": False,
                            "error": error_msg,
                            "error_type": type(e).__name__,
                        }
                    )
                    attempts.append(attempt_info)

                    print(f"  ❌ Failed with {model} (retry {retry + 1}): {error_msg}")

                    # If it's a rate limit error, wait before retrying
                    if "rate limit" in error_msg.lower():
                        wait_time = 2**retry  # Exponential backoff
                        print(f"  ⏳ Rate limit detected, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)

                    # If it's not the last retry, continue
                    if retry < self.max_retries - 1:
                        continue

                    # If it's not the last model, try the next one
                    break

        # All models and retries failed
        return {
            "error": "All models and retries failed",
            "attempts": attempts,
            "total_attempts": len(attempts),
            "success": False,
        }


class ErrorAnalysisBrick(AgentBrick):
    """Analyzes the error patterns from LLM attempts."""

    def __init__(self, brick_id: str = "error_analysis"):
        super().__init__(brick_id=brick_id, name="Error Analysis Brick")

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Analyze error patterns from previous attempts."""
        # Get results from previous brick
        previous_results = None
        for outputs in context.node_outputs.values():
            for output in outputs.values():
                if "attempts" in output:
                    previous_results = output
                    break

        if not previous_results:
            return {"error": "No attempt data found"}

        attempts = previous_results["attempts"]

        analysis = {
            "total_attempts": len(attempts),
            "successful_attempts": 0,
            "failed_attempts": 0,
            "models_tried": set(),
            "error_types": {},
            "retry_patterns": {},
            "success_rate_by_model": {},
        }

        # Analyze each attempt
        for attempt in attempts:
            model = attempt["model"]
            analysis["models_tried"].add(model)

            if attempt["success"]:
                analysis["successful_attempts"] += 1
            else:
                analysis["failed_attempts"] += 1
                error_type = attempt.get("error_type", "Unknown")
                analysis["error_types"][error_type] = (
                    analysis["error_types"].get(error_type, 0) + 1
                )

            # Track retry patterns
            retry_key = f"{model}_retry_{attempt['retry']}"
            analysis["retry_patterns"][retry_key] = attempt["success"]

        # Calculate success rates by model
        for model in analysis["models_tried"]:
            model_attempts = [a for a in attempts if a["model"] == model]
            successful = sum(1 for a in model_attempts if a["success"])
            total = len(model_attempts)
            analysis["success_rate_by_model"][model] = {
                "successful": successful,
                "total": total,
                "rate": successful / total if total > 0 else 0,
            }

        analysis["models_tried"] = list(analysis["models_tried"])

        return analysis


async def main():
    """Demonstrate robust LLM usage with comprehensive error handling."""

    # Create LiteLLM configuration with potential issues
    litellm_config = LiteLLMConfig(
        models=[
            {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 10,  # Short timeout to potentially trigger timeouts
            },
            {
                "model": "claude-3-5-sonnet-20241022",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 10,
                "custom_llm_provider": "anthropic",
            },
            {
                "model": "claude-3-sonnet-20240229",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 15,
                "custom_llm_provider": "anthropic",
            },
        ],
        default_model="claude-3-5-sonnet-20241022",
        enable_fallback=True,
    )

    # Create graph configuration
    graph_config = GraphConfig(
        max_iterations=10,
        litellm_config=litellm_config,
    )

    # Create graph
    graph = AgentGraph(
        name="Robust LLM Usage Graph",
        config=graph_config,
    )

    # Test scenarios
    test_scenarios = [
        {
            "name": "Simple Task",
            "prompt": "Write a haiku about artificial intelligence.",
            "node_id": "simple_task",
        },
        {
            "name": "Complex Task",
            "prompt": (
                "Explain quantum computing in simple terms, then provide "
                "a detailed technical explanation of quantum entanglement, "
                "and finally discuss the potential implications for cryptography. "
                "This should be comprehensive and well-structured."
            ),
            "node_id": "complex_task",
        },
    ]

    # Create nodes for each scenario
    for i, scenario in enumerate(test_scenarios):
        # Robust LLM node
        llm_node = AgentNode(node_id=scenario["node_id"])
        llm_node.add_brick(
            RobustLLMBrick(
                brick_id=f"robust_llm_{i}",
                prompt=scenario["prompt"],
                preferred_model="claude-3-5-sonnet-20241022",
                fallback_models=["gpt-4", "claude-3-sonnet-20240229"],
                max_retries=2,
            )
        )

        # Analysis node
        analysis_node = AgentNode(node_id=f"analysis_{scenario['node_id']}")
        analysis_node.add_brick(ErrorAnalysisBrick(brick_id=f"analysis_{i}"))

        # Add nodes and connect them
        graph.add_node(llm_node)
        graph.add_node(analysis_node)
        graph.add_edge(scenario["node_id"], f"analysis_{scenario['node_id']}")

    # Execute the graph
    print("🛡️ Testing robust LLM usage with error handling...")
    print("\n" + "=" * 80)

    context = await graph.execute()

    # Display results for each scenario
    for scenario in test_scenarios:
        print(f"\n📋 SCENARIO: {scenario['name']}")
        print("=" * 60)
        print(f"Prompt: {scenario['prompt'][:100]}...")

        # Show LLM results
        llm_outputs = context.node_outputs.get(scenario["node_id"], {})
        for _brick_id, output in llm_outputs.items():
            if output.get("success"):
                print("\n✅ SUCCESS")
                print(f"Model used: {output['model_used']}")
                print(f"Total attempts: {output['total_attempts']}")
                usage = output.get("usage", {})
                if usage:
                    print(f"Tokens: {usage.get('total_tokens', 'N/A')}")
                print(f"Response: {output['content'][:200]}...")
            else:
                print(f"\n❌ FAILED after {output['total_attempts']} attempts")
                print(f"Error: {output['error']}")

        # Show analysis results
        analysis_outputs = context.node_outputs.get(
            f"analysis_{scenario['node_id']}", {}
        )
        for _brick_id, analysis in analysis_outputs.items():
            if "error" not in analysis:
                print("\n📊 ANALYSIS:")
                print(f"Total attempts: {analysis['total_attempts']}")
                success_rate = (
                    f"{analysis['successful_attempts']}/{analysis['total_attempts']}"
                )
                print(f"Success rate: {success_rate}")

                print(f"\nModels tried: {', '.join(analysis['models_tried'])}")

                print("\nSuccess rate by model:")
                for model, stats in analysis["success_rate_by_model"].items():
                    rate_pct = stats["rate"] * 100
                    success_info = (
                        f"{stats['successful']}/{stats['total']} ({rate_pct:.1f}%)"
                    )
                    print(f"  {model}: {success_info}")

                if analysis["error_types"]:
                    print("\nError types encountered:")
                    for error_type, count in analysis["error_types"].items():
                        print(f"  {error_type}: {count}")

    print(f"\n{'='*80}")
    print("🎉 Robust LLM testing completed!")


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
