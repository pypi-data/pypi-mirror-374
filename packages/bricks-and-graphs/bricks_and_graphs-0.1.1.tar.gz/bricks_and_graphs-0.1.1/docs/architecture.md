# Architecture Guide

This document describes the architecture of the BAG (Bricks and Graphs) framework.

## Table of Contents

1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Execution Model](#execution-model)
4. [Data Flow](#data-flow)
5. [Extension Points](#extension-points)
6. [Design Patterns](#design-patterns)
7. [Architecture Diagram](#architecture-diagram)

## Overview

BAG is a modular framework for building AI agent pipelines with these key principles:

- **Composability** - Build complex behaviors from simple bricks
- **Type Safety** - Strong typing with Python type hints
- **Async-First** - Built on asyncio for concurrent execution
- **Configuration-Driven** - Graphs definable in YAML/JSON
- **Extensible** - Easy to add custom bricks and behaviors

### High-Level Architecture

![BAG Architecture Diagram](images/BAG%20Architecture%20Diagram.svg)

*Figure: BAG Framework Architecture - Layered design showing the relationship between application layer, graph management, node orchestration, brick execution, and integration components.*

## Core Components

### 1. AgentBrick

The fundamental building block:

```python
class AgentBrick(ABC):
    """Base class for all bricks."""

    @property
    @abstractmethod
    def brick_type(self) -> BrickType:
        """Type of brick (PROMPT, PROCESSOR, ROUTER, ACTION)."""
        pass

    @abstractmethod
    async def execute(self, context: ExecutionContext) -> Any:
        """Execute brick logic."""
        pass
```

**Brick Types:**
- **PROMPT** - Generate prompts for LLMs
- **PROCESSOR** - Transform data between formats
- **ROUTER** - Make routing decisions
- **ACTION** - Perform side effects

### 2. AgentNode

Container for bricks with orchestration:

```python
class AgentNode:
    """Execution unit containing multiple bricks."""

    def __init__(self, node_id: str):
        self._bricks: list[AgentBrick] = []
        self._litellm_manager: LiteLLMManager | None = None

    async def run(self, context: ExecutionContext) -> RoutingDecision | None:
        """Orchestrated execution of bricks."""
        # 1. Execute ACTION bricks
        # 2. Collect PROMPT bricks → LLM
        # 3. Process through PROCESSOR bricks
        # 4. Route with ROUTER brick
```

**Key Features:**
- Orchestrated execution flow
- Automatic LLM integration
- Context propagation
- Error handling

### 3. AgentGraph

Directed graph of nodes:

```python
class AgentGraph:
    """Graph structure for agent execution."""

    def __init__(self, config: GraphConfig):
        self._graph = nx.DiGraph()
        self._nodes: dict[str, AgentNode] = {}
        self._agent_context = AgentContext()
        self._litellm_manager: LiteLLMManager | None = None
```

**Capabilities:**
- NetworkX-based graph management
- Cycle detection and handling
- Shared context across nodes
- Configuration-driven setup

### 4. ExecutionContext

Carries state through execution:

```python
class ExecutionContext(BaseModel):
    """Context passed through graph execution."""

    # Core data
    data: dict[str, Any] = {}
    metadata: dict[str, Any] = {}

    # Execution tracking
    visited_nodes: list[str] = []
    loop_counters: dict[str, int] = {}

    # Results
    brick_outputs: dict[str, Any] = {}
    node_outputs: dict[str, Any] = {}

    # Shared state
    agent_context: AgentContext | None = None
    litellm_manager: LiteLLMManager | None = None
```

### 5. AgentContext

Shared state container:

```python
class AgentContext:
    """Dictionary-like shared state for graph execution."""

    def __init__(self):
        self._data: dict[str, Any] = {}

    # Dictionary interface
    def __getitem__(self, key: str) -> Any: ...
    def __setitem__(self, key: str, value: Any) -> None: ...
```

## Execution Model

### Graph Execution Flow

1. **Initialization**
   - Validate graph structure
   - Initialize LiteLLM if configured
   - Create execution context

2. **Node Selection**
   - Start from entry node or specified node
   - Check loop counters
   - Handle cycles

3. **Node Execution**
   - Call `node.run(context)`
   - Orchestrated brick execution
   - Capture outputs

4. **Routing**
   - Router brick determines next node
   - Validate routing decision
   - Move to next node or terminate

### Node Execution Flow (run method)

![Agent Node Processing](images/Agent%20Node%20Processing.svg)

*Figure: Agent Node Processing Flow - Shows the sequential execution of bricks within a node: PROMPT → LLM Execution → LLM Response → PROCESSOR → ROUTER.*

## Data Flow

### 1. Input Data Flow

```
User Input → ExecutionContext → Graph → Node → Brick
                ↓
          AgentContext (shared state)
```

### 2. Inter-Brick Communication

```python
# Processor receives data via context
input_data = context.agent_context.get("_current_processor_input")

# Process data
output = process(input_data)

# Next processor receives this output
context.agent_context["_current_processor_input"] = output
```

### 3. Output Aggregation

```
Brick Output → node_outputs[node_id][brick_id]
      ↓
Node Output → context.node_outputs
      ↓
Graph Result → Final ExecutionContext
```

## Extension Points

### 1. Custom Bricks

```python
class MyCustomBrick(AgentBrick):
    @property
    def brick_type(self) -> BrickType:
        return BrickType.PROCESSOR

    async def execute(self, context: ExecutionContext) -> dict:
        # Custom logic
        return {"result": "processed"}
```

### 2. Custom Routers

```python
class SmartRouter(AgentBrick):
    @property
    def brick_type(self) -> BrickType:
        return BrickType.ROUTER

    async def execute(self, context: ExecutionContext) -> RoutingDecision:
        # Complex routing logic
        return RoutingDecision(next_node_id="best_node")
```

### 3. Data Format Support

```python
# Register new data format
@register_format("custom")
class CustomFormatProcessor:
    def detect(self, data: Any) -> bool: ...
    def process(self, data: Any) -> Any: ...
```

### 4. LLM Providers

```python
# Add via LiteLLM configuration
config = LiteLLMConfig(
    models=[
        LiteLLMModelConfig(
            model="custom-llm",
            custom_llm_provider="my_provider"
        )
    ]
)
```

## Design Patterns

### 1. Strategy Pattern

Bricks implement different strategies for the same interface:

```python
# Different prompt strategies
class SimplePromptBrick(AgentBrick): ...
class TemplatePromptBrick(AgentBrick): ...
class DynamicPromptBrick(AgentBrick): ...
```

### 2. Chain of Responsibility

Processors form a chain, each handling data in sequence:

```python
# Data flows through processors
JSONExtractor → SchemaValidator → DataEnhancer → Output
```

### 3. Factory Pattern

BrickRegistry creates bricks from configuration:

```python
registry = BrickRegistry()
brick = registry.create_brick("bag.bricks.PromptBrick", config)
```

### 4. Observer Pattern

Context changes are observable by all bricks:

```python
# Any brick can read/write context
context.agent_context["shared_data"] = value
```

### 5. Composite Pattern

Nodes compose multiple bricks into complex behaviors:

```python
node = AgentNode()
node.add_brick(prompt_brick)
node.add_brick(processor_brick)
node.add_brick(router_brick)
```

## Architecture Overview

The architecture follows a layered approach where each layer has specific responsibilities and clear interfaces.

## Performance Considerations

### 1. Async Execution

- All bricks execute asynchronously
- Parallel node execution possible
- Non-blocking I/O for external services

### 2. Memory Management

- Context passed by reference
- Large data handled via streaming
- Automatic cleanup after execution

### 3. Scalability

- Graphs can be distributed
- Nodes can run on different workers
- Horizontal scaling via graph partitioning

## Security Considerations

### 1. Input Validation

- Schema validation for brick configs
- Type checking at runtime
- Sanitization of user inputs

### 2. API Key Management

- Environment variable support
- Secure storage recommendations
- Key rotation capabilities

### 3. Execution Isolation

- Bricks run in isolated contexts
- Limited access to system resources
- Configurable execution limits

## Future Architecture Directions

1. **Plugin System** - Dynamic brick loading
2. **Distributed Execution** - Multi-machine graphs
3. **Visual Designer** - GUI for graph creation
4. **Performance Monitoring** - Built-in metrics
5. **State Persistence** - Save/resume execution

## Summary

The BAG architecture provides:

- **Modularity** through the brick system
- **Flexibility** via configuration-driven design
- **Scalability** with async execution
- **Extensibility** through clear interfaces
- **Reliability** with validation and error handling

This architecture enables building complex AI agent systems while maintaining simplicity and maintainability.
