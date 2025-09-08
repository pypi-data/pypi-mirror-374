"""Basic example of creating and executing a simple graph."""

import asyncio

from bag.core import (
    AgentBrick,
    AgentGraph,
    AgentNode,
    BrickType,
    ExecutionContext,
    RoutingDecision,
)


class GreetingBrick(AgentBrick):
    """Simple brick that generates a greeting."""

    def __init__(self, person_name: str):
        super().__init__(brick_id=f"greeting_{person_name}")
        self.person_name = person_name

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ACTION

    async def execute(self, context: ExecutionContext) -> dict:
        """Generate a greeting."""
        greeting = f"Hello from {self.person_name}!"

        # Store in context for other nodes
        context.agent_context[f"greeting_{self.person_name}"] = greeting

        return {"greeting": greeting, "from": self.person_name}


class CombinerBrick(AgentBrick):
    """Brick that combines greetings from context."""

    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict:
        """Combine all greetings from context."""
        greetings = []

        # Collect all greetings from context
        for key in context.agent_context.keys:
            if key.startswith("greeting_"):
                greetings.append(context.agent_context[key])

        combined = " | ".join(greetings) if greetings else "No greetings found"

        return {"combined_greetings": combined, "count": len(greetings)}


class SimpleRouterBrick(AgentBrick):
    """Router that decides based on greeting count."""

    @property
    def brick_type(self) -> BrickType:
        return BrickType.ROUTER

    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        """Route based on number of greetings."""
        # Get the processor input
        processor_input = context.agent_context.get("_current_router_input", {})
        count = processor_input.get("count", 0)

        if count >= 2:
            next_node = "multiple_greetings"
        elif count == 1:
            next_node = "single_greeting"
        else:
            next_node = "no_greetings"

        return RoutingDecision(
            next_node_id=next_node, metadata={"greeting_count": count}
        )


async def main():
    """Demonstrate basic graph construction and execution."""
    # Create a simple graph
    graph = AgentGraph(name="Greeting Graph")

    # Create the main node with multiple greeting bricks
    main_node = AgentNode(node_id="greetings")
    main_node.add_brick(GreetingBrick("Alice"))
    main_node.add_brick(GreetingBrick("Bob"))
    main_node.add_brick(CombinerBrick(brick_id="combiner"))
    main_node.add_brick(SimpleRouterBrick(brick_id="router"))

    # Create handler nodes for different cases
    class MultipleHandler(AgentBrick):
        @property
        def brick_type(self) -> BrickType:
            return BrickType.ACTION

        async def execute(self, context: ExecutionContext) -> dict:  # noqa: ARG002
            return {"result": "Handled multiple greetings!"}

    class SingleHandler(AgentBrick):
        @property
        def brick_type(self) -> BrickType:
            return BrickType.ACTION

        async def execute(self, context: ExecutionContext) -> dict:  # noqa: ARG002
            return {"result": "Handled single greeting!"}

    class NoHandler(AgentBrick):
        @property
        def brick_type(self) -> BrickType:
            return BrickType.ACTION

        async def execute(self, context: ExecutionContext) -> dict:  # noqa: ARG002
            return {"result": "No greetings to handle!"}

    multiple_node = AgentNode(node_id="multiple_greetings")
    multiple_node.add_brick(MultipleHandler(brick_id="multi_handler"))

    single_node = AgentNode(node_id="single_greeting")
    single_node.add_brick(SingleHandler(brick_id="single_handler"))

    no_node = AgentNode(node_id="no_greetings")
    no_node.add_brick(NoHandler(brick_id="no_handler"))

    # Add nodes to graph
    graph.add_node(main_node)
    graph.add_node(multiple_node)
    graph.add_node(single_node)
    graph.add_node(no_node)

    # Add edges for routing
    graph.add_edge("greetings", "multiple_greetings")
    graph.add_edge("greetings", "single_greeting")
    graph.add_edge("greetings", "no_greetings")

    # Execute the graph
    print("Executing graph...")
    context = await graph.execute(start_node_id="greetings")

    # Display results
    print("\n=== Execution Results ===")

    # Show greetings node output
    greetings_output = context.node_outputs.get("greetings", {})
    print("\nGreetings node outputs:")
    for brick_id, output in greetings_output.items():
        print(f"  {brick_id}: {output}")

    # Show which path was taken
    visited = context.visited_nodes
    print(f"\nNodes visited: {' -> '.join(visited)}")

    # Show final handler output
    for node_id in ["multiple_greetings", "single_greeting", "no_greetings"]:
        if node_id in context.node_outputs:
            output = context.node_outputs[node_id]
            print(f"\nFinal handler ({node_id}): {output}")
            break

    # Show graph structure
    print("\n=== Graph Structure ===")
    graph_dict = graph.to_dict()
    node_ids = [node["id"] for node in graph_dict["nodes"]]
    print(f"Nodes: {node_ids}")
    print(f"Edges: {graph_dict['edges']}")


if __name__ == "__main__":
    asyncio.run(main())
