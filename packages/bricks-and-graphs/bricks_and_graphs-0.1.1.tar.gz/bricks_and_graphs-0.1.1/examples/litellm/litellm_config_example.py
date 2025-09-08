"""Example of using LiteLLM configuration with AgentGraph."""

import asyncio
import os
import re
from pathlib import Path

import yaml

from bag.core import (
    AgentBrick,
    AgentGraph,
    AgentNode,
    BrickType,
    ExecutionContext,
    GraphConfig,
    LiteLLMConfig,
)


class LLMPromptBrick(AgentBrick):
    """Example brick that uses LiteLLM for completion."""

    def __init__(self, brick_id: str = "llm_prompt", prompt: str = ""):
        super().__init__(brick_id=brick_id, name="LLM Prompt Brick")
        self.prompt = prompt

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict:
        """Execute LLM completion using the graph's LiteLLM manager."""
        if not context.litellm_manager:
            return {"error": "No LiteLLM manager available"}

        # Prepare messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": self.prompt},
        ]

        try:
            # Use the LiteLLM manager from context
            response = await context.litellm_manager.complete(messages)

            # Extract the response content
            content = response.choices[0].message.content

            # Store in agent context for other nodes
            context.agent_context["llm_response"] = content

            return {
                "model": response.model,
                "content": content,
                "usage": response.usage.model_dump() if response.usage else None,
            }
        except Exception as e:
            return {"error": str(e)}


async def main():
    """Demonstrate LiteLLM integration with AgentGraph."""

    # Load LiteLLM configuration from YAML
    config_path = Path(__file__).parent / "litellm_config.yaml"
    with open(config_path) as f:
        config_content = f.read()

    # Expand environment variables in the config
    def expand_env_vars(text: str) -> str:
        """Expand ${VAR} syntax with environment variables."""

        def replacer(match):
            var_name = match.group(1)
            return os.getenv(var_name, match.group(0))  # Return original if not found

        return re.sub(r"\$\{([^}]+)\}", replacer, text)

    expanded_config = expand_env_vars(config_content)
    config_data = yaml.safe_load(expanded_config)

    # Create LiteLLMConfig from the loaded data
    litellm_config = LiteLLMConfig(**config_data)

    # Create GraphConfig with LiteLLM configuration
    graph_config = GraphConfig(max_iterations=10, litellm_config=litellm_config)

    # Create graph with LiteLLM configuration
    graph = AgentGraph(name="LiteLLM Example Graph", config=graph_config)

    # Create nodes with LLM bricks
    node1 = AgentNode(node_id="greeting")
    node1.add_brick(
        LLMPromptBrick(
            brick_id="greet",
            prompt="Generate a creative greeting for someone interested in AI agents.",
        )
    )

    node2 = AgentNode(node_id="followup")
    node2.add_brick(
        LLMPromptBrick(
            brick_id="elaborate",
            prompt=(
                "Based on the previous greeting, suggest three ways "
                "AI agents can help in daily life. Be specific and practical."
            ),
        )
    )

    node3 = AgentNode(node_id="summary")
    node3.add_brick(
        LLMPromptBrick(
            brick_id="summarize",
            prompt=(
                "Summarize the conversation so far in one concise paragraph, "
                "highlighting the key benefits of AI agents mentioned."
            ),
        )
    )

    # Add nodes to graph
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    graph.add_edge("greeting", "followup")
    graph.add_edge("followup", "summary")

    # Execute the graph
    print("Executing graph with LiteLLM...")
    context = await graph.execute()

    # Display results
    print("\n=== Results ===")
    for node_id, outputs in context.node_outputs.items():
        print(f"\nNode: {node_id}")
        for _, output in outputs.items():
            if "error" in output:
                print(f"  Error: {output['error']}")
            else:
                print(f"  Model: {output.get('model', 'unknown')}")
                print(f"  Response: {output.get('content', 'No content')[:200]}...")
                if output.get("usage"):
                    print(f"  Tokens: {output['usage']}")


if __name__ == "__main__":
    # Ensure API keys are set
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables")
        exit(1)

    # Run the example
    asyncio.run(main())
