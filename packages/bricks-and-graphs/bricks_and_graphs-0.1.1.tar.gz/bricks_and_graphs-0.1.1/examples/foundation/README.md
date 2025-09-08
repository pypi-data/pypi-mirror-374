# Foundation Brick Examples

This directory contains examples demonstrating how to use FoundationBrick to provide foundational data to other bricks in a node.

## What is FoundationBrick?

FoundationBrick is a special type of brick that:

- **Runs first** in node execution, before any other brick type
- **Provides foundational data** that other bricks can use
- **Only one per node** - you can have at most one foundation brick per node
- **Stores data in context** for other bricks to access

## Types of Foundation Bricks

### 1. DataFoundationBrick
Provides static data to other bricks.

```python
foundation = DataFoundationBrick(
    data={"user": {"name": "Alice", "role": "developer"}},
    context_key="user_data"
)
```

### 2. ContextFoundationBrick
Extracts and reorganizes existing context data.

```python
foundation = ContextFoundationBrick(
    source_keys=["user_info", "session_data"],
    target_key="organized_data"
)
```

### 3. ComputedFoundationBrick
Computes data using a custom function.

```python
def compute_user_summary(context):
    return {"summary": "Generated user summary"}

foundation = ComputedFoundationBrick(
    compute_fn=compute_user_summary,
    context_key="computed_data"
)
```

## Execution Order

In a node with multiple brick types, the execution order is:

1. **FoundationBrick** (if present)
2. **ActionBrick** (if present)
3. **PromptBrick** (if present)
4. **LLM Completion** (if prompts exist)
5. **ProcessorBrick** (if present)
6. **RouterBrick** (if present)

## Examples

### Basic Foundation Example

Run the basic example:

```bash
cd examples/foundation
python foundation_example.py
```

This example shows:
- How FoundationBrick provides data first
- How PromptBrick can access that data
- The execution order and data flow

## Use Cases

Foundation bricks are useful for:

- **User Context**: Providing user information to prompts
- **Configuration**: Setting up configuration data for the node
- **Data Preparation**: Pre-processing data before other bricks run
- **Session State**: Maintaining session or request-specific data
- **API Keys/Secrets**: Providing authentication data (be careful with security)
- **Computed Values**: Calculating values that multiple bricks need

## Best Practices

1. **Keep it Simple**: Foundation bricks should provide data, not perform complex logic
2. **Use Descriptive Keys**: Use clear context keys so other bricks can find the data
3. **Document Dependencies**: Make it clear what data your other bricks expect
4. **Handle Missing Data**: Be defensive when accessing foundation data in other bricks
5. **One Per Node**: Remember only one foundation brick is allowed per node

## Integration with Other Bricks

Foundation data can be accessed by other bricks through the execution context:

```python
# In a PromptBrick
async def execute(self, context):
    foundation_data = context.agent_context.get("foundation_key", {})
    # Use foundation_data in your prompt template

# In a ProcessorBrick
async def execute(self, context):
    foundation_data = context.agent_context["foundation_key"]
    # Process using foundation data
```
