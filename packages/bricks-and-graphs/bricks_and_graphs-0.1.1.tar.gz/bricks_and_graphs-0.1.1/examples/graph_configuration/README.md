# Graph Configuration Examples

This directory contains examples of defining and loading graphs from configuration files.

## Files

- `config_based_graph.yaml` - Complete graph definition in YAML format
- `load_config_graph.py` - Python script that loads and executes the configured graph

## Configuration Structure

The YAML configuration includes:

1. **Metadata** - Graph identification and versioning
2. **Config** - Graph execution settings and LiteLLM configuration
3. **Nodes** - Complete node definitions with their bricks
4. **Edges** - Connections between nodes

## Running the Example

```bash
# Run with mock data (no API key required)
python examples/graph_configuration/load_config_graph.py

# Run with actual LLM (requires OpenAI API key)
export OPENAI_API_KEY="your-api-key"
python examples/graph_configuration/load_config_graph.py
```

## Key Features Demonstrated

1. **Complete Graph Definition** - Entire pipeline defined in YAML
2. **Dynamic Brick Loading** - Bricks loaded by type name
3. **Configuration-driven Routing** - Conditional routing based on data
4. **LiteLLM Integration** - Optional LLM configuration in YAML

## Extending the Example

To add custom bricks:

1. Create your brick class
2. Register it with the BrickRegistry
3. Reference it by full module path in YAML

```python
# Register custom brick
registry.register("mymodule.MyBrick", MyBrick)
```

```yaml
# Use in configuration
bricks:
  - id: "my_brick"
    type: "mymodule.MyBrick"
    config:
      param1: "value1"
```
