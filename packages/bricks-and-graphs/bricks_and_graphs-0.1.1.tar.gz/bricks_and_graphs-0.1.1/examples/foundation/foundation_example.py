"""Example demonstrating FoundationBrick usage."""

import asyncio
from typing import Any

from bag.bricks import DataFoundationBrick
from bag.core import AgentBrick, AgentGraph, AgentNode, BrickType, ExecutionContext


class FoundationAwareProcessorBrick(AgentBrick):
    """A processor brick that can access foundation data."""

    BRICK_TYPE = BrickType.PROCESSOR

    def __init__(self, foundation_key: str = "foundation_data", **kwargs):
        super().__init__(**kwargs)
        self.foundation_key = foundation_key

    async def execute(self, context: ExecutionContext) -> dict[str, Any]:
        """Execute by accessing foundation data and processing it."""
        # Get foundation data from agent context
        foundation_data = context.agent_context.get(self.foundation_key, {})

        # Process the foundation data
        processed_result = {
            "foundation_available": bool(foundation_data),
            "foundation_keys": list(foundation_data.keys()) if foundation_data else [],
            "processed_message": self._create_message(foundation_data),
        }

        return processed_result

    def _create_message(self, foundation_data: dict) -> str:
        """Create a message based on foundation data."""
        if not foundation_data:
            return "No foundation data available"

        user = foundation_data.get("user", {})
        project = foundation_data.get("project", {})

        if user and project:
            return (
                f"Hello {user.get('name', 'Unknown')}! "
                f"You're a {user.get('role', 'unknown role')} with "
                f"{user.get('experience', 'unknown')} of experience "
                f"working on {project.get('name', 'unknown project')}, "
                f"which is a {project.get('type', 'unknown type')}. "
                f"How can I help you today?"
            )
        return "Foundation data processed successfully"


async def main():
    """Demonstrate FoundationBrick providing data to other bricks."""

    # Create a graph
    graph = AgentGraph(name="Foundation Example")

    # Create a node with foundation and processor bricks
    node = AgentNode(node_id="example_node")

    # Add a foundation brick that provides user data
    foundation_brick = DataFoundationBrick(
        data={
            "user": {"name": "Alice", "role": "developer", "experience": "5 years"},
            "project": {"name": "bricks-and-graphs", "type": "AI framework"},
        },
        context_key="user_project_data",
        brick_id="user_data_foundation",
    )
    node.add_brick(foundation_brick)

    # Add a processor brick that uses the foundation data
    processor_brick = FoundationAwareProcessorBrick(
        foundation_key="user_project_data", brick_id="foundation_processor"
    )
    node.add_brick(processor_brick)

    # Add node to graph
    graph.add_node(node)

    # Execute the graph
    print("🚀 Executing graph with FoundationBrick...")
    context = await graph.execute()

    # Show results
    print("\n" + "=" * 60)
    print("EXECUTION RESULTS")
    print("=" * 60)

    # Show foundation brick output
    foundation_output = context.node_outputs["example_node"]["user_data_foundation"]
    print("\n📊 Foundation Brick Output:")
    print(f"  Context Key: {foundation_output['context_key']}")
    print(f"  Message: {foundation_output['message']}")

    # Show that data is available in context
    print("\n🗄️  Data in Agent Context:")
    foundation_data = context.agent_context["user_project_data"]
    print(
        f"  User: {foundation_data['user']['name']} ({foundation_data['user']['role']})"
    )
    print(f"  Project: {foundation_data['project']['name']}")

    # Show processor brick output
    processor_output = context.node_outputs["example_node"]["foundation_processor"]
    print("\n⚙️  Processor Brick Output:")
    print(f"  Foundation Available: {processor_output['foundation_available']}")
    print(f"  Foundation Keys: {processor_output['foundation_keys']}")
    print(f"  Processed Message: {processor_output['processed_message']}")

    print("\n✅ Foundation data successfully provided to processor brick!")


if __name__ == "__main__":
    asyncio.run(main())
