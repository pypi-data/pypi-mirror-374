# LiteLLM Integration Examples

Examples demonstrating LiteLLM integration with BAG.

## Files

- `litellm_config.yaml` - LiteLLM configuration with multiple models
- `litellm_config_example.py` - Using LiteLLM in graph execution

## Configuration

The `litellm_config.yaml` shows how to configure:
- Multiple models (GPT-4, Claude 3, Claude 3.5)
- API key management (via environment variables)
- Model-specific parameters (temperature, max_tokens, etc.)
- Fallback configuration
- Caching settings

## Running the Example

```bash
# Set your API key(s)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Run the example
uv run python examples/litellm/litellm_config_example.py
```

## Key Features

1. **Multi-Model Support** - Configure multiple LLM providers
2. **Automatic Fallback** - Falls back to alternative models on error
3. **Unified Interface** - Same API for all LLM providers
4. **Graph Integration** - LiteLLM manager available to all nodes

## Customization

To use different models:
1. Update the `litellm_config.yaml`
2. Add appropriate API keys
3. Modify model parameters as needed
