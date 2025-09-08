# Basic Examples

Simple examples to get started with the BAG framework.

## Files

- `simple_graph.py` - Basic graph with greeting bricks and routing

## simple_graph.py

Demonstrates:
- Creating custom bricks (GreetingBrick, CombinerBrick, RouterBrick)
- Building a simple graph with multiple nodes
- Using AgentContext to share data between bricks
- Routing based on brick outputs
- Graph execution and result inspection

### Key Concepts

1. **Custom Bricks** - Define your own brick types by inheriting from AgentBrick
2. **Context Sharing** - Use `context.agent_context` to share data
3. **Routing Logic** - Router bricks decide the next node based on data
4. **Graph Structure** - Nodes connected by edges form execution paths

### Running

```bash
uv run python examples/basic/simple_graph.py
```

No API keys required - runs completely locally.
