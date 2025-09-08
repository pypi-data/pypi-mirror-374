# BAG Examples

This directory contains examples demonstrating various features and use cases of the Bricks and Graphs (BAG) framework.

## Directory Structure

- **[basic/](basic/)** - Simple examples to get started with BAG
  - Basic brick creation and usage
  - Simple graph construction
  - Minimal working examples

- **[litellm/](litellm/)** - LiteLLM integration examples
  - LiteLLM configuration
  - Multi-model setup with fallbacks
  - Using LLMs in bricks

- **[advanced_llm/](advanced_llm/)** - Advanced LLM usage patterns
  - Multi-provider comparison and analysis
  - Complex multi-step reasoning workflows
  - Robust error handling and fallback strategies
  - Real LLM API integration with proper mocking in tests

- **[node_execution/](node_execution/)** - Node execution patterns
  - Orchestrated execution with `run()` method
  - Prompt → Process → Route pipelines
  - Custom execution flows

- **[graph_configuration/](graph_configuration/)** - Configuration-driven graphs
  - YAML-based graph definitions
  - Dynamic graph loading
  - Complete pipeline configurations

## Running Examples

Most examples require environment variables for API keys:

```bash
# For OpenAI models
export OPENAI_API_KEY="your-api-key"

# For Anthropic models
export ANTHROPIC_API_KEY="your-api-key"
```

Then run any example:

```bash
# Basic examples (no API keys required)
python examples/basic/simple_graph.py
python examples/node_execution/node_run_example.py

# LLM examples (API keys required)
python examples/litellm/litellm_config_example.py
python examples/advanced_llm/multi_provider_comparison.py
python examples/advanced_llm/reasoning_chain.py
python examples/advanced_llm/robust_llm_usage.py
```

## Prerequisites

Make sure you have installed BAG:

```bash
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```
