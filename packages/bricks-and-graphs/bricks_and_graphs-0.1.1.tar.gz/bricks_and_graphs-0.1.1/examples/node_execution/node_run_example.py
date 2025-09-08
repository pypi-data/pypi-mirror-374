"""Example demonstrating the AgentNode.run() method with orchestrated execution."""

import asyncio
import os

from bag.core import (
    AgentBrick,
    AgentGraph,
    AgentNode,
    BrickType,
    ExecutionContext,
    GraphConfig,
    LiteLLMConfig,
    LiteLLMModelConfig,
    RoutingDecision,
)


class SystemPromptBrick(AgentBrick):
    """System prompt brick."""

    def __init__(self, content: str):
        super().__init__(brick_id="system_prompt")
        self.content = content

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROMPT

    async def execute(self, context: ExecutionContext) -> dict:  # noqa: ARG002
        """Return system prompt message."""
        return {
            "message": {"role": "system", "content": self.content},
            "role": "system",
            "content": self.content,
        }


class UserPromptBrick(AgentBrick):
    """User prompt brick that can use context data."""

    def __init__(self, template: str):
        super().__init__(brick_id="user_prompt")
        self.template = template

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROMPT

    async def execute(self, context: ExecutionContext) -> dict:
        """Render user prompt with context data."""
        # Get data from context if available
        topic = context.agent_context.get("topic", "AI agents")
        content = self.template.format(topic=topic)

        return {
            "message": {"role": "user", "content": content},
            "role": "user",
            "content": content,
        }


class SentimentAnalyzerBrick(AgentBrick):
    """Processor that analyzes sentiment from LLM response."""

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict:
        """Analyze sentiment from LLM response."""
        # Get the LLM response from context
        llm_input = context.agent_context.get("_current_processor_input")

        if not llm_input:
            return {"error": "No input provided", "sentiment": "unknown"}

        # Extract content from LLM response
        content = ""
        if hasattr(llm_input, "choices") and llm_input.choices:
            content = llm_input.choices[0].message.content
        elif isinstance(llm_input, dict) and "error" in llm_input:
            return {"error": llm_input["error"], "sentiment": "error"}

        # Simple sentiment analysis based on keywords
        content_lower = content.lower()
        if any(
            word in content_lower
            for word in ["great", "excellent", "amazing", "wonderful", "positive"]
        ):
            sentiment = "positive"
        elif any(
            word in content_lower
            for word in ["bad", "terrible", "negative", "awful", "horrible"]
        ):
            sentiment = "negative"
        else:
            sentiment = "neutral"

        # Store analysis in context for other nodes
        context.agent_context["sentiment_analysis"] = {
            "sentiment": sentiment,
            "content_length": len(content),
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
        }

        return {
            "sentiment": sentiment,
            "confidence": 0.8,
            "content_analyzed": True,
            "original_content": content,
        }


class SummarizerBrick(AgentBrick):
    """Processor that creates a summary."""

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict:
        """Create summary from previous processor output."""
        # Get input from previous processor
        prev_input = context.agent_context.get("_current_processor_input")

        if not prev_input or not isinstance(prev_input, dict):
            return {"summary": "No data to summarize"}

        # Create summary based on sentiment analysis
        sentiment = prev_input.get("sentiment", "unknown")
        content = prev_input.get("original_content", "")

        summary = f"Analysis complete. Sentiment: {sentiment}. "
        if content:
            word_count = len(content.split())
            summary += f"Content contains {word_count} words."

        return {"summary": summary, "sentiment": sentiment, "processed": True}


class ContentRouterBrick(AgentBrick):
    """Router that decides next node based on content analysis."""

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ROUTER

    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        """Route based on sentiment and content analysis."""
        # Get router input
        router_input = context.agent_context.get("_current_router_input")

        if not router_input or not isinstance(router_input, dict):
            # No valid input, terminate
            return RoutingDecision(
                next_node_id=None,
                should_terminate=True,
                metadata={"reason": "No valid input for routing"},
            )

        sentiment = router_input.get("sentiment", "unknown")

        # Route based on sentiment
        if sentiment == "positive":
            next_node = "positive_handler"
        elif sentiment == "negative":
            next_node = "negative_handler"
        elif sentiment == "error":
            next_node = "error_handler"
        else:
            next_node = "neutral_handler"

        # Store routing decision in context
        context.agent_context["routing_decision"] = {
            "selected_node": next_node,
            "sentiment": sentiment,
            "reason": f"Routing to {next_node} based on {sentiment} sentiment",
        }

        return RoutingDecision(
            next_node_id=next_node,
            metadata={
                "sentiment": sentiment,
                "confidence": router_input.get("confidence", 0.5),
            },
        )


async def main():
    """Demonstrate the node run method with full pipeline."""

    # Create LiteLLM configuration
    litellm_config = LiteLLMConfig(
        models=[
            LiteLLMModelConfig(
                model="gpt-3.5-turbo",  # Using a cheaper model for demo
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.7,
                max_tokens=150,
            )
        ]
    )

    # Create graph with LiteLLM
    graph_config = GraphConfig(litellm_config=litellm_config)
    graph = AgentGraph(name="Sentiment Analysis Pipeline", config=graph_config)

    # Create main analysis node with full pipeline
    analysis_node = AgentNode(node_id="analyzer")

    # Add prompt bricks
    analysis_node.add_brick(
        SystemPromptBrick(
            "You are a helpful assistant that provides thoughtful "
            "responses about various topics."
        )
    )
    analysis_node.add_brick(
        UserPromptBrick(
            "Tell me your thoughts about {topic}. Be specific and include your opinion."
        )
    )

    # Add processor bricks
    analysis_node.add_brick(SentimentAnalyzerBrick(brick_id="sentiment"))
    analysis_node.add_brick(SummarizerBrick(brick_id="summarizer"))

    # Add router brick
    analysis_node.add_brick(ContentRouterBrick(brick_id="router"))

    # Create handler nodes with simple processor bricks
    class HandlerBrick(AgentBrick):
        def __init__(self, handler_type: str, **kwargs):
            super().__init__(**kwargs)
            self.handler_type = handler_type

        @property
        def brick_type(self) -> BrickType:
            return BrickType.PROCESSOR

        async def execute(self, context: ExecutionContext) -> dict:
            routing_decision = context.agent_context.get("routing_decision", {})
            return {
                "handler_type": self.handler_type,
                "handled": True,
                "routing_info": routing_decision,
                "message": f"Handled by {self.handler_type} handler",
            }

    positive_node = AgentNode(node_id="positive_handler")
    positive_node.add_brick(HandlerBrick("positive", brick_id="positive_processor"))

    negative_node = AgentNode(node_id="negative_handler")
    negative_node.add_brick(HandlerBrick("negative", brick_id="negative_processor"))

    neutral_node = AgentNode(node_id="neutral_handler")
    neutral_node.add_brick(HandlerBrick("neutral", brick_id="neutral_processor"))

    error_node = AgentNode(node_id="error_handler")
    error_node.add_brick(HandlerBrick("error", brick_id="error_processor"))

    # Add nodes to graph
    graph.add_node(analysis_node)
    graph.add_node(positive_node)
    graph.add_node(negative_node)
    graph.add_node(neutral_node)
    graph.add_node(error_node)

    # Add edges from analyzer to handlers
    graph.add_edge("analyzer", "positive_handler")
    graph.add_edge("analyzer", "negative_handler")
    graph.add_edge("analyzer", "neutral_handler")
    graph.add_edge("analyzer", "error_handler")

    # Test with different topics
    topics = ["artificial intelligence", "climate change", "pizza"]

    for topic in topics:
        print(f"\n{'='*60}")
        print(f"Analyzing topic: {topic}")
        print("=" * 60)

        # Set topic in agent context
        graph.agent_context["topic"] = topic

        # Execute the graph
        context = await graph.execute(start_node_id="analyzer")

        # Display results
        analyzer_outputs = context.node_outputs.get("analyzer", {})

        # Show prompts sent
        if "_llm_completion" in analyzer_outputs:
            llm_data = analyzer_outputs["_llm_completion"]
            if "messages" in llm_data:
                print("\nPrompts sent to LLM:")
                for msg in llm_data["messages"]:
                    print(f"  [{msg['role']}]: {msg['content'][:100]}...")

        # Show processor results
        if "sentiment" in analyzer_outputs:
            sentiment_result = analyzer_outputs["sentiment"]
            print("\nSentiment Analysis:")
            print(f"  Sentiment: {sentiment_result.get('sentiment', 'unknown')}")
            print(f"  Confidence: {sentiment_result.get('confidence', 0)}")

        if "summarizer" in analyzer_outputs:
            summary = analyzer_outputs["summarizer"]
            print(f"\nSummary: {summary.get('summary', 'No summary')}")

        # Show routing decision
        routing = context.agent_context.get("routing_decision", {})
        if routing:
            print("\nRouting Decision:")
            print(f"  Next Node: {routing.get('selected_node', 'none')}")
            print(f"  Reason: {routing.get('reason', 'unknown')}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Please set OPENAI_API_KEY environment variable")
        print("You can also modify this example to use other models like Claude")
        exit(1)

    # Run the example
    asyncio.run(main())
