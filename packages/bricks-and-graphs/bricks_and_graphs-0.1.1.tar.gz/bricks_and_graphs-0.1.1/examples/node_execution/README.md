# Node Execution Examples

Examples demonstrating the orchestrated execution flow with the `run()` method.

## Files

- `node_run_example.py` - Complete sentiment analysis pipeline

## Orchestrated Execution Flow

The `run()` method executes bricks in a specific order:

1. **ACTION bricks** - Execute first (for compatibility)
2. **PROMPT bricks** - Collected and combined into LLM messages
3. **LLM Execution** - Calls LLM with combined prompts
4. **PROCESSOR bricks** - Process LLM response in sequence
5. **ROUTER brick** - Makes routing decision based on final output

## node_run_example.py

Demonstrates a complete sentiment analysis pipeline:
- System and user prompts for LLM
- Sentiment analysis processor
- Summary processor (chains from sentiment)
- Content-based routing

### Data Flow

```
Prompts → LLM → SentimentAnalyzer → Summarizer → Router
                     ↓                   ↓           ↓
                 sentiment           summary    routing decision
```

### Running

```bash
# With LLM (requires API key)
export OPENAI_API_KEY="your-key"
uv run python examples/node_execution/node_run_example.py

# Note: The example will indicate if no API key is set
```

## Key Concepts

1. **Brick Ordering** - Bricks execute in type-based order
2. **Data Chaining** - Each processor receives previous output
3. **Context Passing** - Data flows through `_current_processor_input`
4. **Routing Logic** - Router uses final processor output
