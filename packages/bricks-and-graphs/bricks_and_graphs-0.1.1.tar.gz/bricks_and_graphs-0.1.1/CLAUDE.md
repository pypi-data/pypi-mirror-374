# BAG Framework - Claude Code Assistant Guide

BAG is a collaborative agentic framework for designing dynamic AI agents that work together to resolve complex problems.

## 🚀 Quick Commands

### Development Workflow
- `uv run pytest` - Run all tests (MANDATORY before commits)
- `uv run pytest --cov --cov-branch --cov-fail-under=85` - Test with coverage
- `uv run pre-commit run --all-files` - Run all linting and formatting
- `uv run ruff check .` - Check code style
- `uv run black --target-version py312 .` - Format code
- `uv sync` - Install/update dependencies

### Repository Management
- `npx -y repomix --config repomix.config.json` - Generate repo documentation
- `make diagrams` - Convert Excalidraw diagrams (if converter exists)

## 🧪 CRITICAL: Testing is MANDATORY

**ABSOLUTE REQUIREMENT**: Every single line of code must have comprehensive tests.

### Testing Rules (NON-NEGOTIABLE)
- **Minimum coverage**: 85% total, 90% branch coverage
- **1:1 mapping**: Every source file needs corresponding test file
- **Test-first**: Write tests before implementation
- **All paths**: Test success, failure, and edge cases
- **Mock externals**: Always mock LLM calls, databases, file I/O

### Test Commands
```bash
# Quick test during development
uv run pytest -q

# Full coverage check (run before commits)
uv run pytest --cov=src/bag --cov-branch --cov-report=term-missing --cov-fail-under=85

# Test specific module
uv run pytest tests/core/test_graph.py -v
```

## 🏗️ Architecture Overview

### Core Components
- **AgentBrick**: Base class for all processing units
- **AgentNode**: Orchestrates brick execution in sequence
- **AgentGraph**: Manages node execution and routing
- **AgentContext**: Shared state and data management
- **LiteLLMManager**: Handles LLM integration

### Execution Flow
1. **Graph Validation** → **Node Selection** → **Brick Orchestration**
2. **Brick Sequence**: ACTION → PROMPT → LLM → PROCESSOR → ROUTER
3. **Routing Decision** → **Next Node** or **Completion**

## 💻 Code Style Guidelines

### Python 3.12+ Features (REQUIRED)
- Use PEP 695 generic syntax: `class Box[T]:`
- Use `functools.cached_property` for lazy attributes
- Use PEP 701 debug f-strings: `f"{variable=}"`
- Use pattern matching (`match/case`) over long if/elif chains

### Functional Programming (PREFERRED)
- Write pure functions without hidden I/O or global state
- Use `@dataclass(frozen=True)` for immutability
- Prefer `map`, `filter`, `itertools` over explicit loops
- Pass callables instead of strategy flags
- No side effects in comprehensions

### Type Annotations (MANDATORY)
- All modules must be fully typed
- Use `typing` and `typing_extensions` as needed
- Prefer semantic type aliases: `NodeId: TypeAlias = str`

## 🧱 Standard Patterns

### AgentBrick Implementation
```python
from typing import Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass(frozen=True)
class BrickInput:
    data: Dict[str, Any]
    context: Dict[str, Any] | None = None

@dataclass(frozen=True)
class BrickOutput:
    result: Dict[str, Any]
    metadata: Dict[str, Any]
    next_action: str | None = None

class AgentBrick(ABC):
    def __init__(self, brick_id: str, config: Dict[str, Any]):
        self.brick_id = brick_id
        self.config = config

    @abstractmethod
    def process(self, input_data: BrickInput) -> BrickOutput:
        """Process input and return output - MUST be tested."""
        pass
```

### Test Template (MANDATORY for every class)
```python
import pytest
from unittest.mock import Mock, patch

class TestMyBrick:
    @pytest.fixture
    def brick_config(self):
        return {"param": "value", "timeout": 30}

    @pytest.fixture
    def sample_input(self):
        return BrickInput(data={"key": "value"})

    @pytest.fixture
    def brick(self, brick_config):
        return MyBrick("test_brick", brick_config)

    def test_initialization(self, brick, brick_config):
        assert brick.brick_id == "test_brick"
        assert brick.config == brick_config

    def test_process_success(self, brick, sample_input):
        result = brick.process(sample_input)
        assert isinstance(result, BrickOutput)

    def test_process_invalid_input(self, brick):
        with pytest.raises(ValueError):
            brick.process(None)

    @pytest.mark.parametrize("input_data,expected", [
        ({"key": "value"}, True),
        ({}, False),
        (None, False),
    ])
    def test_validation(self, brick, input_data, expected):
        # Test validation logic
        pass
```

## 🔧 Configuration & Environment

### Project Structure
```
src/bag/                 # Main source code
├── core/               # Core framework components
├── bricks/             # Brick implementations
├── api/               # API endpoints
└── cli/               # Command-line interface

tests/                  # Test files (mirrors src structure)
├── core/              # Core component tests
├── bricks/            # Brick tests
└── fixtures/          # Test fixtures

docs/                  # Documentation
├── architecture.md    # System architecture
├── configuration.md   # Configuration guide
└── images/           # Diagrams and images
```

### Key Files
- `pyproject.toml` - Project configuration, dependencies, tool settings
- `.pre-commit-config.yaml` - Pre-commit hooks for quality assurance
- `repomix.config.json` - Repository documentation generation
- `CLAUDE.md` - This file (Claude Code assistant guide)

## 🚨 Anti-Patterns (AVOID)

### Code Without Tests
```python
# ❌ NEVER: Code without corresponding tests
class MyBrick(AgentBrick):  # Missing test_my_brick.py
    def process(self, input_data):  # Missing test methods
        return "result"
```

### Untested Error Paths
```python
# ❌ NEVER: Exception handling without tests
def risky_operation():
    if condition:
        raise ValueError("Error")  # Missing pytest.raises test
```

### Direct LLM Calls in Tests
```python
# ❌ NEVER: Tests that call real APIs
@patch('litellm.completion')  # ✅ Always mock external calls
def test_llm_integration(mock_completion):
    mock_completion.return_value = Mock(...)
```

## 🔍 Debugging & Development

### Logging
- Use structured logging with context
- Include execution metadata in logs
- Use debug f-strings for temporary logging: `f"{variable=}"`

### Error Handling
- Use exception groups for fan-out error handling
- Provide meaningful error messages with context
- Test all error paths thoroughly

### Performance
- Profile LLM token usage and costs
- Monitor execution time for graph operations
- Use async patterns for I/O-bound operations

## 📚 Documentation Standards

- Use Google-style docstrings for public APIs
- Include type information in docstrings
- Provide usage examples for complex functions
- Keep documentation up-to-date with code changes

## 🔄 Workflow Integration

### Pre-commit Process
1. Write tests first (test-driven development)
2. Implement functionality
3. Run `uv run pytest --cov` to verify coverage ≥85%
4. Run `uv run pre-commit run --all-files`
5. Commit only after all checks pass

### CI/CD Pipeline
- All tests must pass
- Coverage must meet minimum thresholds
- Linting and formatting must be clean
- Type checking must pass (when enabled)

## 🎯 Best Practices Summary

1. **Test Everything**: 85% coverage minimum, test-first development
2. **Type Everything**: Full type annotations required
3. **Pure Functions**: Prefer immutable, side-effect-free code
4. **Modern Python**: Use Python 3.12+ features and patterns
5. **Documentation**: Keep docs current and comprehensive
6. **Quality Gates**: Use pre-commit hooks and CI checks
7. **Mock External**: Always mock LLM calls, databases, file I/O
8. **Semantic Types**: Use meaningful type aliases
9. **Error Handling**: Test all failure paths
10. **Performance**: Monitor costs and execution time

Remember: Quality is non-negotiable. Every line of code must be tested, typed, and documented.
