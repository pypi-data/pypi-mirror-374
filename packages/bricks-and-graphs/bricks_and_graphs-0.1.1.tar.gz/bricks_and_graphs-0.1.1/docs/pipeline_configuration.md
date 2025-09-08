# Pipeline Configuration Guide

This guide explains how to configure complete AI agent pipelines using the BAG framework.

## Table of Contents

1. [Pipeline Concepts](#pipeline-concepts)
2. [Basic Pipeline Structure](#basic-pipeline-structure)
3. [Prompt-Process-Route Pattern](#prompt-process-route-pattern)
4. [Advanced Pipeline Patterns](#advanced-pipeline-patterns)
5. [Pipeline Examples](#pipeline-examples)

## Pipeline Concepts

A pipeline in BAG consists of:

- **Nodes** - Execution units containing bricks
- **Bricks** - Individual processing components
- **Edges** - Connections defining execution flow
- **Context** - Shared state across the pipeline

### Execution Flow

```
Start Node → Process → Route → Next Node → ... → End
     ↓           ↓        ↓
  Prompts    Transform  Decide
```

## Basic Pipeline Structure

### Minimal Pipeline

```yaml
# Simple linear pipeline
nodes:
  - id: "start"
    bricks:
      - id: "process"
        type: "bag.bricks.ProcessorBrick"

  - id: "end"
    bricks:
      - id: "output"
        type: "bag.bricks.ActionBrick"

edges:
  - source: "start"
    target: "end"
```

### Branching Pipeline

```yaml
# Pipeline with conditional routing
nodes:
  - id: "analyzer"
    bricks:
      - id: "analyze"
        type: "bag.bricks.ProcessorBrick"
      - id: "router"
        type: "bag.bricks.RouterBrick"
        config:
          routes:
            positive: "success_handler"
            negative: "error_handler"

  - id: "success_handler"
    # Handle success case

  - id: "error_handler"
    # Handle error case

edges:
  - source: "analyzer"
    target: "success_handler"
  - source: "analyzer"
    target: "error_handler"
```

## Prompt-Process-Route Pattern

The most common pipeline pattern for LLM applications:

### 1. Prompt Phase

Collect and prepare prompts for LLM:

```yaml
bricks:
  - id: "system_prompt"
    type: "bag.bricks.PromptBrick"
    config:
      content: "You are an AI assistant specialized in data analysis"
      role: "system"

  - id: "user_prompt"
    type: "bag.bricks.PromptBrick"
    config:
      template: |
        Analyze the following data:
        {data}

        Provide:
        1. Summary
        2. Key insights
        3. Recommendations
      role: "user"
      variables:
        data: "{{ input_data }}"
```

### 2. Process Phase

Transform LLM responses and data:

```yaml
bricks:
  - id: "extract_json"
    type: "bag.bricks.processor.JSONExtractor"
    config:
      extract_mode: "auto"

  - id: "validate"
    type: "bag.bricks.processor.SchemaValidator"
    config:
      schema:
        type: "object"
        required: ["summary", "insights", "recommendations"]

  - id: "enhance"
    type: "bag.bricks.processor.DataEnhancer"
    config:
      add_metadata: true
      add_timestamp: true
```

### 3. Route Phase

Make decisions based on processed data:

```yaml
bricks:
  - id: "quality_router"
    type: "bag.bricks.router.ConditionalRouter"
    config:
      conditions:
        high_quality: |
          len(insights) >= 3 and
          confidence > 0.8
        needs_review: |
          confidence < 0.5 or
          'error' in flags
      routes:
        high_quality: "publish_node"
        needs_review: "review_node"
      default_route: "standard_node"
```

## Advanced Pipeline Patterns

### 1. Multi-Stage Processing

```yaml
nodes:
  - id: "stage1_extraction"
    name: "Extract Information"
    bricks:
      - id: "extract_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          content: "Extract key information from the text"
      # Processing bricks...

  - id: "stage2_analysis"
    name: "Analyze Information"
    bricks:
      - id: "analyze_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          template: "Analyze the extracted data: {extracted_data}"
      # Analysis bricks...

  - id: "stage3_synthesis"
    name: "Synthesize Results"
    # Combine results from previous stages
```

### 2. Parallel Processing

```yaml
nodes:
  - id: "splitter"
    bricks:
      - id: "split_data"
        type: "bag.bricks.processor.DataSplitter"
      - id: "parallel_router"
        type: "bag.bricks.router.ParallelRouter"
        config:
          routes:
            - "process_a"
            - "process_b"
            - "process_c"

  # Parallel processing nodes
  - id: "process_a"
  - id: "process_b"
  - id: "process_c"

  - id: "aggregator"
    bricks:
      - id: "combine_results"
        type: "bag.bricks.processor.ResultAggregator"
```

### 3. Retry Pipeline

```yaml
nodes:
  - id: "process_with_retry"
    bricks:
      - id: "process"
        type: "bag.bricks.ProcessorBrick"
      - id: "retry_router"
        type: "bag.bricks.router.RetryRouter"
        config:
          max_retries: 3
          retry_conditions:
            - "error in result"
            - "confidence < 0.3"
          success_route: "next_stage"
          retry_route: "process_with_retry"  # Loop back
          failure_route: "error_handler"
```

### 4. Context Enrichment Pipeline

```yaml
nodes:
  - id: "enrichment"
    bricks:
      # Fetch additional context
      - id: "fetch_context"
        type: "bag.bricks.action.ContextFetcher"
        config:
          sources:
            - "database"
            - "api"
            - "cache"

      # Merge with existing data
      - id: "merge_context"
        type: "bag.bricks.processor.ContextMerger"

      # Generate enriched prompt
      - id: "enriched_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          template: |
            Context: {context}
            Data: {data}
            Task: {task}
```

## Pipeline Examples

### Example 1: Customer Support Pipeline

```yaml
metadata:
  name: "Customer Support Pipeline"

nodes:
  - id: "ticket_classifier"
    bricks:
      - id: "classify_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          content: "Classify this support ticket by urgency and category"

      - id: "classifier"
        type: "bag.bricks.processor.TicketClassifier"

      - id: "urgency_router"
        type: "bag.bricks.router.UrgencyRouter"
        config:
          routes:
            critical: "immediate_response"
            high: "priority_queue"
            normal: "standard_queue"

  - id: "immediate_response"
    bricks:
      - id: "auto_respond"
        type: "bag.bricks.action.AutoResponder"
        config:
          template: "urgent_response_template"
          notify_human: true
```

### Example 2: Content Generation Pipeline

```yaml
metadata:
  name: "Content Generation Pipeline"

nodes:
  - id: "content_planner"
    bricks:
      - id: "plan_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          content: "Create an outline for an article about {topic}"

  - id: "content_generator"
    bricks:
      - id: "generate_sections"
        type: "bag.bricks.processor.SectionGenerator"
        config:
          parallel: true

  - id: "content_reviewer"
    bricks:
      - id: "review_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          content: "Review and improve this content"

      - id: "quality_check"
        type: "bag.bricks.processor.QualityChecker"

      - id: "publish_router"
        type: "bag.bricks.router.PublishRouter"
```

### Example 3: Data Analysis Pipeline

```yaml
metadata:
  name: "Data Analysis Pipeline"

config:
  litellm_config:
    models:
      - model: "gpt-4"
        temperature: 0.3  # Lower for analytical tasks

nodes:
  - id: "data_prep"
    bricks:
      - id: "load_data"
        type: "bag.bricks.action.DataLoader"

      - id: "clean_data"
        type: "bag.bricks.processor.DataCleaner"

  - id: "analysis"
    bricks:
      - id: "analyze_prompt"
        type: "bag.bricks.PromptBrick"
        config:
          template: |
            Analyze this dataset:
            Columns: {columns}
            Sample: {sample}

            Provide statistical insights and patterns.

      - id: "extract_insights"
        type: "bag.bricks.processor.InsightExtractor"

  - id: "visualization"
    bricks:
      - id: "generate_viz"
        type: "bag.bricks.processor.VisualizationGenerator"
        config:
          charts:
            - "distribution"
            - "correlation"
            - "trends"
```

## Best Practices

### 1. Pipeline Design

- **Keep nodes focused** - Each node should have a clear purpose
- **Use meaningful IDs** - Make debugging easier
- **Document metadata** - Include description and version
- **Plan error paths** - Always have error handling nodes

### 2. Context Management

```yaml
# Store intermediate results
- id: "store_result"
  type: "bag.bricks.action.ContextStore"
  config:
    key: "analysis_result"

# Retrieve in later nodes
- id: "use_result"
  type: "bag.bricks.PromptBrick"
  config:
    template: "Based on {analysis_result}, recommend..."
    variables:
      analysis_result: "{{ analysis_result }}"
```

### 3. Performance Optimization

- **Parallel processing** where possible
- **Cache LLM responses** for identical prompts
- **Batch operations** for similar tasks
- **Early termination** for invalid inputs

### 4. Testing Pipelines

```python
# Test individual nodes
node = graph.get_node("analyzer")
result = await node.run(test_context)

# Test full pipeline
context = await graph.execute(
    start_node_id="start",
    context=test_context
)

# Validate results
assert "expected_key" in context.agent_context
```

## Debugging Pipelines

### Enable Debug Mode

```yaml
config:
  debug: true
  log_level: "DEBUG"
```

### Track Execution

```python
# After execution
print(f"Visited nodes: {context.visited_nodes}")
print(f"Node outputs: {context.node_outputs}")
print(f"Final context: {context.agent_context.to_dict()}")
```

### Common Issues

1. **Routing loops** - Check max_loop_count
2. **Missing routes** - Ensure all router outputs have edges
3. **Context conflicts** - Use namespaced keys
4. **Type mismatches** - Validate brick input/output types

## Next Steps

- See [Configuration Guide](configuration.md) for detailed configuration options
- Check [Architecture Guide](architecture.md) for system design
- Explore [examples/](../examples/) for working pipelines
