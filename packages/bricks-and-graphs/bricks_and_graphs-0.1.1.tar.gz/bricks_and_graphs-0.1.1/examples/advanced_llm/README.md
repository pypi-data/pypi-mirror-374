# Advanced LLM Integration Examples

This directory contains examples demonstrating advanced usage of LLM integration with the BAG framework, including:

- Multiple LLM provider usage (OpenAI, Anthropic)
- Model comparison and fallback strategies
- Complex multi-step reasoning workflows
- Error handling and retry logic
- Token usage optimization

## Prerequisites

Set your API keys as environment variables:

```bash
export OPENAI_API_KEY="your-openai-key-here"
export ANTHROPIC_API_KEY="your-anthropic-key-here"
```

## Examples

### 1. Multi-Provider Comparison (`multi_provider_comparison.py`)
Demonstrates how to use multiple LLM providers for the same task and compare results.

### 2. Complex Reasoning Chain (`reasoning_chain.py`)
Shows a multi-step reasoning workflow using different models for different steps.

### 3. Error Handling and Fallbacks (`robust_llm_usage.py`)
Demonstrates robust error handling, retries, and fallback strategies.

## Running the Examples

```bash
# Run from the project root
cd examples/advanced_llm

# Multi-provider comparison
python multi_provider_comparison.py

# Complex reasoning chain
python reasoning_chain.py

# Robust error handling
python robust_llm_usage.py
```

## Note on API Keys

These examples use real LLM APIs and will consume tokens. Make sure you have valid API keys and understand the pricing for each provider before running.
