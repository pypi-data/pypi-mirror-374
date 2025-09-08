"""Example demonstrating complex multi-step reasoning with different models."""

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


class ProblemAnalysisBrick(AgentBrick):
    """Analyzes a complex problem and breaks it down into components."""

    def __init__(self, brick_id: str = "problem_analysis", problem: str = ""):
        super().__init__(brick_id=brick_id, name="Problem Analysis Brick")
        self.problem = problem

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Analyze the problem using Claude (good for analysis)."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager available"}

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert problem analyst. Break down complex problems "
                    "into clear, manageable components. Be systematic and thorough."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Analyze this problem and break it into 3-5 key components:\n\n"
                    f"{self.problem}\n\n"
                    f"For each component, provide:\n"
                    f"1. A clear description\n"
                    f"2. Why it's important\n"
                    f"3. What approach might work best"
                ),
            },
        ]

        try:
            # Use Claude for analysis (good at reasoning)
            response = await context.litellm_manager.complete(
                messages, model="claude-3-5-sonnet-20241022"
            )

            analysis = response.choices[0].message.content
            context.agent_context["problem_analysis"] = analysis

            return {
                "analysis": analysis,
                "model_used": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }

        except Exception as e:
            return {"error": str(e)}


class SolutionGenerationBrick(AgentBrick):
    """Generates potential solutions based on the problem analysis."""

    def __init__(self, brick_id: str = "solution_generation"):
        super().__init__(brick_id=brick_id, name="Solution Generation Brick")

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Generate solutions using GPT-4 (good for creative solutions)."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager available"}

        # Get the analysis from previous step
        analysis = context.agent_context.get("problem_analysis")
        if not analysis:
            return {"error": "No problem analysis found in context"}

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a creative problem solver. Given a problem analysis, "
                    "generate innovative and practical solutions. Think outside "
                    "the box while remaining realistic."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Based on this problem analysis:\n\n{analysis}\n\n"
                    f"Generate 3-4 different solution approaches. For each solution:\n"
                    f"1. Provide a clear title\n"
                    f"2. Explain the approach\n"
                    f"3. List pros and cons\n"
                    f"4. Estimate implementation difficulty (Easy/Medium/Hard)"
                ),
            },
        ]

        try:
            # Use GPT-4 for creative solution generation
            response = await context.litellm_manager.complete(messages, model="gpt-4")

            solutions = response.choices[0].message.content
            context.agent_context["solutions"] = solutions

            return {
                "solutions": solutions,
                "model_used": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }

        except Exception as e:
            return {"error": str(e)}


class EvaluationBrick(AgentBrick):
    """Evaluates the proposed solutions and recommends the best approach."""

    def __init__(self, brick_id: str = "evaluation"):
        super().__init__(brick_id=brick_id, name="Evaluation Brick")

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Evaluate solutions using Claude (good for analytical evaluation)."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager available"}

        # Get both analysis and solutions
        analysis = context.agent_context.get("problem_analysis")
        solutions = context.agent_context.get("solutions")

        if not analysis or not solutions:
            return {"error": "Missing analysis or solutions in context"}

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert evaluator. Analyze solutions objectively, "
                    "considering feasibility, cost, time, and potential impact. "
                    "Provide clear reasoning for your recommendations."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original Problem Analysis:\n{analysis}\n\n"
                    f"Proposed Solutions:\n{solutions}\n\n"
                    f"Please evaluate these solutions and provide:\n"
                    f"1. A ranking of solutions from best to worst\n"
                    f"2. Detailed reasoning for your ranking\n"
                    f"3. A recommended implementation plan for the top solution\n"
                    f"4. Potential risks and mitigation strategies"
                ),
            },
        ]

        try:
            # Use Claude for analytical evaluation
            response = await context.litellm_manager.complete(
                messages, model="claude-3-5-sonnet-20241022"
            )

            evaluation = response.choices[0].message.content
            context.agent_context["evaluation"] = evaluation

            return {
                "evaluation": evaluation,
                "model_used": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }

        except Exception as e:
            return {"error": str(e)}


class ImplementationPlanBrick(AgentBrick):
    """Creates a detailed implementation plan for the recommended solution."""

    def __init__(self, brick_id: str = "implementation_plan"):
        super().__init__(brick_id=brick_id, name="Implementation Plan Brick")

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Create implementation plan using GPT-4 (good for structured planning)."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager available"}

        # Get the evaluation
        evaluation = context.agent_context.get("evaluation")
        if not evaluation:
            return {"error": "No evaluation found in context"}

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a project planning expert. Create detailed, actionable "
                    "implementation plans with clear timelines, milestones, and "
                    "resource requirements."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Based on this evaluation:\n\n{evaluation}\n\n"
                    f"Create a detailed implementation plan including:\n"
                    f"1. Phase-by-phase breakdown\n"
                    f"2. Timeline estimates\n"
                    f"3. Resource requirements\n"
                    f"4. Key milestones and deliverables\n"
                    f"5. Success metrics\n"
                    f"6. Contingency plans"
                ),
            },
        ]

        try:
            # Use GPT-4 for structured planning
            response = await context.litellm_manager.complete(messages, model="gpt-4")

            plan = response.choices[0].message.content
            context.agent_context["implementation_plan"] = plan

            return {
                "plan": plan,
                "model_used": response.model,
                "usage": response.usage.model_dump() if response.usage else {},
            }

        except Exception as e:
            return {"error": str(e)}


async def main():
    """Demonstrate complex multi-step reasoning workflow."""

    # Create LiteLLM configuration
    litellm_config = LiteLLMConfig(
        models=[
            {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            {
                "model": "claude-3-5-sonnet-20241022",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "temperature": 0.7,
                "max_tokens": 2000,
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
        name="Complex Reasoning Chain",
        config=graph_config,
    )

    # Complex problem to solve
    problem = (
        "A mid-sized software company (150 employees) is struggling with "
        "declining productivity, increasing technical debt, and low team morale. "
        "They have multiple legacy systems, inconsistent development practices, "
        "and are losing talented developers to competitors. The company needs "
        "to modernize their technology stack while maintaining business operations "
        "and keeping their existing clients happy."
    )

    # Create nodes for each step
    analysis_node = AgentNode(node_id="analysis")
    analysis_node.add_brick(ProblemAnalysisBrick(problem=problem))

    solution_node = AgentNode(node_id="solution_generation")
    solution_node.add_brick(SolutionGenerationBrick())

    evaluation_node = AgentNode(node_id="evaluation")
    evaluation_node.add_brick(EvaluationBrick())

    planning_node = AgentNode(node_id="implementation_planning")
    planning_node.add_brick(ImplementationPlanBrick())

    # Add nodes to graph
    graph.add_node(analysis_node)
    graph.add_node(solution_node)
    graph.add_node(evaluation_node)
    graph.add_node(planning_node)

    # Create the reasoning chain
    graph.add_edge("analysis", "solution_generation")
    graph.add_edge("solution_generation", "evaluation")
    graph.add_edge("evaluation", "implementation_planning")

    # Execute the reasoning chain
    print("🧠 Starting complex reasoning chain...")
    print(f"Problem: {problem}")
    print("\n" + "=" * 80)

    context = await graph.execute()

    # Display results
    steps = [
        ("analysis", "PROBLEM ANALYSIS", "Claude 3.5 Sonnet"),
        ("solution_generation", "SOLUTION GENERATION", "GPT-4"),
        ("evaluation", "SOLUTION EVALUATION", "Claude 3.5 Sonnet"),
        ("implementation_planning", "IMPLEMENTATION PLAN", "GPT-4"),
    ]

    for node_id, title, _expected_model in steps:
        print(f"\n📋 {title}")
        print("=" * len(title))

        outputs = context.node_outputs.get(node_id, {})
        for _brick_id, output in outputs.items():
            if "error" in output:
                print(f"❌ Error: {output['error']}")
            else:
                # Determine the content key
                content_key = None
                for key in ["analysis", "solutions", "evaluation", "plan"]:
                    if key in output:
                        content_key = key
                        break

                if content_key:
                    print(f"Model used: {output.get('model_used', 'Unknown')}")
                    usage = output.get("usage", {})
                    if usage:
                        print(f"Tokens: {usage.get('total_tokens', 'N/A')}")
                    print(f"\nContent:\n{output[content_key]}")
                else:
                    print("No content found in output")

    print(f"\n{'='*80}")
    print("🎉 Reasoning chain completed!")

    # Calculate total token usage
    total_tokens = 0
    for outputs in context.node_outputs.values():
        for output in outputs.values():
            usage = output.get("usage", {})
            total_tokens += usage.get("total_tokens", 0)

    print(f"Total tokens used: {total_tokens}")


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
