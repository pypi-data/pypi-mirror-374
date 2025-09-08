"""Example of loading and executing a graph from YAML configuration."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

from bag.core import (
    AgentBrick,
    AgentGraph,
    BrickRegistry,
    BrickType,
    ExecutionContext,
    load_graph,
)


# Custom bricks for the example
class ActionBrick(AgentBrick):
    """Simple action brick for demonstration."""

    def __init__(
        self,
        brick_id: str = None,
        name: str = None,
        metadata: dict = None,
        action: str = None,
        message: str = None,
        **kwargs,
    ):
        # Extract config if passed
        if "config" in kwargs:
            config = kwargs.pop("config")
            action = action or config.get("action")
            message = message or config.get("message")

        super().__init__(brick_id=brick_id, name=name, metadata=metadata)
        self.action = action
        self.message = message

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict:
        """Execute the action."""
        # Log the action
        print(f"[{self.action}] {self.message}")

        # Store in context
        context.agent_context[f"action_{self.id}"] = {
            "action": self.action,
            "message": self.message,
            "timestamp": asyncio.get_event_loop().time(),
        }

        return {"action": self.action, "message": self.message, "status": "completed"}


class JSONExtractorBrick(AgentBrick):
    """Extracts JSON from LLM responses."""

    def __init__(
        self,
        brick_id: str = None,
        name: str = None,
        metadata: dict = None,
        extract_mode: str = "auto",
        validate_schema: bool = False,
        schema: dict[str, Any] = None,
        **kwargs,
    ):
        # Extract config if passed
        if "config" in kwargs:
            config = kwargs.pop("config")
            extract_mode = config.get("extract_mode", extract_mode)
            validate_schema = config.get("validate_schema", validate_schema)
            schema = config.get("schema", schema)

        super().__init__(brick_id=brick_id, name=name, metadata=metadata)
        self.extract_mode = extract_mode
        self.validate_schema = validate_schema
        self.schema = schema or {}

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict:
        """Extract JSON from the LLM response."""
        # Get LLM response from context
        llm_input = context.agent_context.get("_current_processor_input")

        if not llm_input:
            return {"error": "No input provided", "extracted": None}

        # Extract content from LLM response
        content = ""
        if hasattr(llm_input, "choices") and llm_input.choices:
            content = llm_input.choices[0].message.content
        elif isinstance(llm_input, dict) and "response" in llm_input:
            # Handle mock response
            content = llm_input["response"]

        # Try to extract JSON
        try:
            # Find JSON in content (simple approach)
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                extracted = json.loads(json_str)

                # Store in context for router
                context.agent_context["analysis_result"] = extracted

                return extracted
            else:
                return {"error": "No JSON found in response", "raw_content": content}
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON: {e}", "raw_content": content}


async def run_with_sample_text(graph: AgentGraph, text: str):
    """Run the graph with a sample text."""
    print(f"\n{'='*60}")
    print(f"Analyzing: {text[:100]}...")
    print("=" * 60)

    # Set input text in context
    graph.agent_context["input_text"] = text

    # For demo purposes, simulate LLM response since we might not have API keys
    if not os.getenv("OPENAI_API_KEY"):
        # Create a mock response
        mock_response = {
            "sentiment": "positive" if "great" in text.lower() else "neutral",
            "confidence": 0.85 if "great" in text.lower() else 0.6,
            "key_topics": ["technology", "innovation"],
            "category": "technology",
            "summary": "A text about technology and innovation.",
        }

        # Inject mock response into the first processor
        graph.agent_context["_mock_llm_response"] = {
            "response": json.dumps(mock_response, indent=2)
        }

    # Execute the graph
    context = await graph.execute(start_node_id="text_analyzer")

    # Display results
    print("\n--- Execution Results ---")

    # Show analysis result
    if "analysis_result" in context.agent_context:
        result = context.agent_context["analysis_result"]
        print("\nAnalysis Result:")
        print(json.dumps(result, indent=2))

    # Show path taken
    print(f"\nNodes visited: {' -> '.join(context.visited_nodes)}")

    # Show actions taken
    print("\nActions taken:")
    for key in context.agent_context.keys:
        if key.startswith("action_"):
            action_data = context.agent_context[key]
            print(f"  - {action_data['action']}: {action_data['message']}")


async def main():
    """Load and execute a graph from configuration."""
    # Path to configuration file
    config_path = Path(__file__).parent / "config_based_graph.yaml"

    # Create a brick registry with our custom bricks
    registry = BrickRegistry()

    # Register custom bricks
    registry.register_brick("bag.bricks.ActionBrick", ActionBrick)
    registry.register_brick(
        "bag.bricks.processor.JSONExtractorBrick", JSONExtractorBrick
    )

    # For the built-in bricks that might not exist yet, create simple mocks
    class MockPromptBrick(AgentBrick):
        def __init__(
            self,
            brick_id: str = None,
            name: str = None,
            metadata: dict = None,
            content: str = None,
            template: str = None,
            role: str = "user",
            variables: dict = None,
            **kwargs,
        ):
            # Extract config if passed
            if "config" in kwargs:
                config = kwargs.pop("config")
                content = content or config.get("content")
                template = template or config.get("template")
                role = config.get("role", role)
                variables = variables or config.get("variables", {})

            super().__init__(brick_id=brick_id, name=name, metadata=metadata)
            self.content = content
            self.template = template
            self.role = role
            self.variables = variables or {}

        @property
        def brick_type(self) -> BrickType:
            return BrickType.PROMPT

        async def execute(self, context: ExecutionContext) -> dict:
            # For demo, just return the prompt
            if self.content:
                text = self.content
            else:
                text = self.template
                # Simple variable replacement
                for key, value in self.variables.items():
                    if "{{" in value:
                        # Runtime variable
                        var_name = value.replace("{{", "").replace("}}", "").strip()
                        actual_value = context.agent_context.get(var_name, "")
                        text = text.replace("{" + key + "}", str(actual_value))

            return {"role": self.role, "content": text}

    class MockConditionalRouter(AgentBrick):
        def __init__(
            self,
            brick_id: str = None,
            name: str = None,
            metadata: dict = None,
            conditions: dict = None,
            routes: dict = None,
            default_route: str = None,
            **kwargs,
        ):
            # Extract config if passed
            if "config" in kwargs:
                config = kwargs.pop("config")
                conditions = conditions or config.get("conditions", {})
                routes = routes or config.get("routes", {})
                default_route = default_route or config.get("default_route")

            super().__init__(brick_id=brick_id, name=name, metadata=metadata)
            self.conditions = conditions or {}
            self.routes = routes or {}
            self.default_route = default_route

        @property
        def brick_type(self) -> BrickType:
            return BrickType.ROUTER

        async def execute(self, context: ExecutionContext) -> dict:
            # Get analysis result
            analysis = context.agent_context.get("analysis_result", {})

            # Evaluate conditions (simple implementation)
            from bag.core import RoutingDecision

            # Check each condition
            for condition_name, condition_expr in self.conditions.items():
                # Simple evaluation (in production, use safe evaluation)
                if (
                    "positive" in condition_expr
                    and analysis.get("sentiment") == "positive"
                ):
                    if (
                        "confidence > 0.8" in condition_expr
                        and analysis.get("confidence", 0) > 0.8
                    ) or (
                        "confidence <= 0.8" in condition_expr
                        and analysis.get("confidence", 0) <= 0.8
                    ):
                        return RoutingDecision(
                            next_node_id=self.routes.get(condition_name)
                        )
                elif analysis.get("sentiment") in condition_expr:
                    return RoutingDecision(next_node_id=self.routes.get(condition_name))

            # Default route
            return RoutingDecision(next_node_id=self.default_route)

    # Register mock bricks
    registry.register_brick("bag.bricks.PromptBrick", MockPromptBrick)
    registry.register_brick(
        "bag.bricks.router.ConditionalRouter", MockConditionalRouter
    )

    # Load the graph from configuration
    print("Loading graph from configuration...")
    graph = load_graph(config_path, brick_registry=registry)

    print(f"Graph loaded: {graph.name}")
    print(f"Nodes: {list(graph.nodes)}")

    # If we're in mock mode, override the node execution to skip LLM
    if not os.getenv("OPENAI_API_KEY"):
        print("\nNote: Running in mock mode (no OPENAI_API_KEY set)")

        # Patch the text_analyzer node to use mock response

        async def mock_run(context):
            # Execute prompts
            outputs = {}
            for brick in graph._nodes["text_analyzer"]._bricks:
                if brick.brick_type == BrickType.PROMPT:
                    output = await brick.execute(context)
                    outputs[brick.id] = output
                elif brick.brick_type == BrickType.PROCESSOR:
                    # Use mock response
                    context.agent_context["_current_processor_input"] = (
                        context.agent_context.get("_mock_llm_response", {})
                    )
                    output = await brick.execute(context)
                    outputs[brick.id] = output
                elif brick.brick_type == BrickType.ROUTER:
                    context.agent_context["_current_router_input"] = outputs.get(
                        "json_extractor", {}
                    )
                    return await brick.execute(context)

            context.node_outputs["text_analyzer"] = outputs
            return None

        graph._nodes["text_analyzer"].run = mock_run

    # Test with different texts
    sample_texts = [
        (
            "This product is absolutely great! I love how it works and would "
            "recommend it to everyone."
        ),
        "The service was terrible. I'm very disappointed with my experience.",
        "The presentation covered various aspects of the topic. It was informative.",
        "I'm not sure about this. It might work but I have some doubts.",
    ]

    for text in sample_texts:
        await run_with_sample_text(graph, text)
        await asyncio.sleep(0.1)  # Small delay between executions

    print("\n" + "=" * 60)
    print("Configuration-based graph execution completed!")


if __name__ == "__main__":
    asyncio.run(main())
