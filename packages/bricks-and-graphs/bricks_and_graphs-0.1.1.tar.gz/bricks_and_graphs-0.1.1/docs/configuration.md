# Configuration Guide

This guide covers all configuration aspects of the BAG (Bricks and Graphs) framework.

## Table of Contents

1. [Graph Configuration](#graph-configuration)
2. [Node Configuration](#node-configuration)
3. [Brick Configuration](#brick-configuration)
4. [LiteLLM Configuration](#litellm-configuration)
5. [Loading from Files](#loading-from-files)
6. [Dynamic Configuration](#dynamic-configuration)

## Graph Configuration

### GraphConfig Class

The `GraphConfig` class controls graph execution behavior:

```python
from bag.core import GraphConfig

config = GraphConfig(
    max_iterations=100,      # Maximum graph execution iterations
    max_loop_count=10,       # Maximum times a node can be revisited
    enable_async=True,       # Enable asynchronous execution
    debug=False,             # Debug mode
    litellm_config=None      # Optional LiteLLM configuration
)
```

### YAML Configuration

Complete graph configuration in YAML:

```yaml
metadata:
  id: "my_graph"
  name: "My Graph"
  description: "Example graph"
  version: "1.0.0"

config:
  max_iterations: 100
  max_loop_count: 10
  enable_async: true
  debug: false
  litellm_config:
    # See LiteLLM Configuration section
```

## Node Configuration

### NodeConfig Class

Nodes are configured with ID, name, and brick definitions:

```python
from bag.core import NodeConfig

node_config = NodeConfig(
    id="processor",
    name="Data Processor",
    brick_configs=[
        {
            "id": "prompt_brick",
            "type": "bag.bricks.PromptBrick",
            "config": {"content": "Process this data"}
        }
    ]
)
```

### YAML Node Definition

```yaml
nodes:
  - id: "analyzer"
    name: "Text Analyzer"
    bricks:
      - id: "system_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          content: "You are a text analyzer"
          role: "system"

      - id: "processor"
        type: "bag.bricks.ProcessorBrick"
        config:
          input_format: "text"
          output_format: "json"
```

## Brick Configuration

### Brick Types and Configuration

Each brick type has specific configuration options:

#### PromptBrick

```yaml
- id: "prompt"
  type: "bag.bricks.PromptBrick"
  config:
    content: "Static prompt text"        # OR
    template: "Process {variable}"       # Template with variables
    role: "user"                        # system/user/assistant
    variables:
      variable: "{{ runtime_value }}"   # Runtime substitution
```

#### ProcessorBrick

```yaml
- id: "processor"
  type: "bag.bricks.ProcessorBrick"
  config:
    input_format: "json"    # json/yaml/text/arrow/pandas/polars
    output_format: "pandas" # Output data format
    schema:                 # Optional validation schema
      type: "object"
      properties:
        field: {"type": "string"}
```

#### RouterBrick

```yaml
- id: "router"
  type: "bag.bricks.RouterBrick"
  config:
    conditions:
      high_score: "score > 0.8"
      low_score: "score <= 0.3"
    routes:
      high_score: "success_node"
      low_score: "retry_node"
    default_route: "review_node"
```

### Custom Brick Configuration

For custom bricks, register them and use in configuration:

```python
# Register custom brick
registry.register_brick("myapp.CustomBrick", CustomBrick)
```

```yaml
- id: "custom"
  type: "myapp.CustomBrick"
  config:
    custom_param: "value"
    nested_config:
      option1: true
      option2: 42
```

## LiteLLM Configuration

### Basic Configuration

```yaml
litellm_config:
  models:
    - model: "gpt-4"
      api_key: "${OPENAI_API_KEY}"
      temperature: 0.7
      max_tokens: 4096
      timeout: 30
      max_retries: 3

  default_model: "gpt-4"
  enable_caching: true
  cache_ttl: 3600
  log_level: "INFO"
```

### Multi-Model Configuration

```yaml
litellm_config:
  models:
    - model: "gpt-4"
      api_key: "${OPENAI_API_KEY}"
      temperature: 0.7

    - model: "claude-3-5-sonnet-20241022"
      api_key: "${ANTHROPIC_API_KEY}"
      temperature: 0.5
      max_tokens: 8192
      custom_llm_provider: "anthropic"

  default_model: "claude-3-5-sonnet-20241022"
  enable_fallback: true
  fallback_order:
    - "claude-3-5-sonnet-20241022"
    - "gpt-4"
```

### Environment Variables

Use environment variables for sensitive data:

```yaml
api_key: "${OPENAI_API_KEY}"  # Resolved at runtime
```

## Loading from Files

### Load Graph from YAML

```python
from bag.core import load_graph, BrickRegistry

# Create registry for custom bricks
registry = BrickRegistry()
registry.register_brick("myapp.CustomBrick", CustomBrick)

# Load graph
graph = load_graph("path/to/graph.yaml", brick_registry=registry)
```

### Load Graph Definition Only

```python
from bag.core import load_graph_definition

# Load definition without instantiating
definition = load_graph_definition("path/to/graph.yaml")

# Create graph later
graph = AgentGraph.from_config(definition)
```

### Supported Formats

- YAML files (`.yaml`, `.yml`)
- JSON files (`.json`)
- Python dictionaries
- String content (YAML or JSON)

## Dynamic Configuration

### Runtime Variable Substitution

Variables can be resolved at runtime:

```yaml
bricks:
  - id: "dynamic_prompt"
    type: "bag.bricks.PromptBrick"
    config:
      template: "Process this: {input_data}"
      variables:
        input_data: "{{ context_variable }}"  # From context
```

### Conditional Configuration

Use router bricks for conditional execution:

```python
# In code
context.agent_context["score"] = 0.9

# In configuration
router:
  conditions:
    high: "score > 0.8"
  routes:
    high: "success_path"
```

### Configuration Validation

The framework validates configuration at multiple levels:

1. **Schema Validation** - Brick config matches expected schema
2. **Type Validation** - Correct data types for parameters
3. **Graph Validation** - Valid node connections and routing
4. **Runtime Validation** - Execution-time checks

### Best Practices

1. **Use Environment Variables** for sensitive data
2. **Version Your Configurations** in the metadata section
3. **Validate Early** with `load_graph_definition()`
4. **Modularize** large configurations into multiple files
5. **Document** your custom brick configurations
6. **Test** configurations in isolation before deployment

## Examples

See the [examples/graph_configuration/](../examples/graph_configuration/) directory for complete working examples of configuration-based graphs.
