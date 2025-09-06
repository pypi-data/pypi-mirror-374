# PromptDev

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=for-the-badge)](https://github.com/astral-sh/ruff)
[![CI](https://github.com/artefactop/promptdev/workflows/CI/badge.svg)](https://github.com/artefactop/promptdev/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/artefactop/promptdev/branch/main/graph/badge.svg)](https://codecov.io/gh/artefactop/promptdev)
[![Security](https://github.com/artefactop/promptdev/workflows/Security%20&%20Dependencies/badge.svg)](https://github.com/artefactop/promptdev/actions/workflows/security.yml)

**Python-native prompt evaluation tool using PydanticAI**

PromptDev is a modern prompt evaluation framework that provides comprehensive testing for AI agents across multiple providers. Built on [PydanticAI](https://ai.pydantic.dev/), it combines type safety with powerful evaluation capabilities.

> [!WARNING]
>
> promptdev is in preview and is not ready for production use.
>
> We're working hard to make it stable and feature-complete, but until then, expect to encounter bugs,
> missing features, and fatal errors.

## Features

- 🔒 **Type Safe** - Full Pydantic validation for inputs, outputs, and configurations  
- 🤖 **PydanticAI Integration** - Native support for PydanticAI agents and [evaluation framework](https://ai.pydantic.dev/evals/)
- 📊 **Multi-Provider Testing** - Test across OpenAI, Together.ai, Ollama, Bedrock, and more
- ⚡ **Performance Optimized** - File-based caching with TTL for faster repeated evaluations
- 📈 **Rich Reporting** - Beautiful console output with detailed failure analysis and provider comparisons
- 🧪 **Promptfoo Compatible** - Works with (some) existing promptfoo YAML configs and datasets
- 🎯 **Comprehensive Assertions** - Built-in evaluators plus custom Python assertion support

## Quick Start

### Installation

#### From PyPI (when available)
```bash
pip install promptdev
```

#### From Source
```bash
git clone https://github.com/artefactop/promptdev.git
cd promptdev
pip install -e .
```

#### For Development
```bash
git clone https://github.com/artefactop/promptdev.git
cd promptdev
uv sync
uv run promptdev --help
```

### Basic Usage

```bash
# Run evaluation
promptdev eval examples/calendar_event_summary.yaml

# Override provider  
promptdev eval examples/calendar_event_summary.yaml --provider pydantic-ai:openai

# Disable caching for a run
promptdev eval examples/calendar_event_summary.yaml --no-cache

# Export results
promptdev eval examples/calendar_event_summary.yaml --output json
promptdev eval examples/calendar_event_summary.yaml --output html

# Validate configuration
promptdev validate examples/calendar_event_summary.yaml

# Cache management
promptdev cache stats
promptdev cache clear
```

## Assertion Types

PromptDev supports a comprehensive set of evaluators for different testing scenarios:

| Type                            | Status             | Description                                | Example Usage                                  |
| ------------------------------- | ------------------ | ------------------------------------------ | ---------------------------------------------- |
| **Core PydanticAI Evaluators**  |
| `exact`                         | ✅                  | Exact string/value matching                | `type: exact`                                  |
| `is_instance`                   | ✅                  | Type checking                              | `type: is_instance, value: "str"`              |
| `llm_judge`                     | ✅                  | LLM-based semantic evaluation              | `type: llm_judge, rubric: "Evaluate accuracy"` |
| **PromptDev Custom Evaluators** |
| `json_schema`                   | ✅                  | JSON schema validation                     | `type: json_schema, value: {schema}`           |
| `python`                        | ✅                  | Custom Python assertions                   | `type: python, value: "./assert.py"`           |
| `contains`                      | ✅                  | Substring matching                         | `type: contains, value: "expected text"`       |
| **Promptfoo Compatibility**     |
| `contains-json`                 | ✅ **(Deprecated)** | JSON schema validation (use `json_schema`) | `type: contains-json, value: {schema}`         |
| `llm-rubric`                    | ✅ **(Deprecated)** | LLM evaluation (use `llm_judge`)           | `type: llm-rubric, value: "rubric text"`       |
| `g-eval`                        | ✅ **(Deprecated)** | G-Eval methodology (use `llm_judge`)       | `type: g-eval, value: "criteria"`              |

### Promptfoo Compatibility

PromptDev maintains compatibility with promptfoo configurations to ease migration:

- **YAML configs** - Most promptfoo YAML configs work with minimal changes
- **JSONL datasets** - Existing test datasets are fully supported
- **Python assertions** - Custom `get_assert` functions work without modification
- **JSON schemas** - Schema validation uses the same format

**Migration Notes:**
- Use `json_schema` instead of `contains-json` for new projects
- Use `llm_judge` instead of `llm-rubric` or `g-eval` for better performance
- Provider IDs use `pydantic-ai:` prefix (e.g., `pydantic-ai:openai`)
- Model names follow PydanticAI format (e.g., `openai:gpt-4`)

## Configuration

PromptDev uses YAML configuration files compatible with promptfoo format:

```yaml
description: "Calendar event summary evaluation"

prompts:
  - file://./prompts/calendar_event_summary.yaml

providers:
  - id: "pydantic-ai:openai"
    model: "openai:gpt-4"
    config:
      temperature: 0.0
  - id: "pydantic-ai:ollama"
    model: "ollama:llama3.2:3b"

tests:
  - file: "./datasets/calendar_events.jsonl"

default_test:
  assert:
    - type: "json_schema"
      value:
        type: "object"
        required: ["name", "event_type", "out_of_office"]
        properties:
          name: {type: "string"}
          event_type: {type: "string"}
          out_of_office: {type: "boolean"}
    - type: "python" 
      value: "./assertions/calendar_assert.py"
    - type: "llm_judge"
      rubric: "Evaluate if the output correctly extracts calendar event information"
      model: "openai:gpt-4"
```

## Advanced Features

### PydanticAI Evals Integration

PromptDev leverages [PydanticAI's pydantic_evals system](https://ai.pydantic.dev/evals/) for robust, type-safe evaluations:

- **LLMJudge Evaluator**: Advanced semantic evaluation using LLMs with customizable rubrics
- **Type-safe Evaluation**: Built on Pydantic's validation framework for reliable results
- **Schema Resolution**: Comprehensive `$ref` resolution for assertion templates and schemas
- **Error Collection**: Structured error reporting with detailed context and stack traces

### Custom Python Assertions

Create powerful custom evaluators:

```python
# examples/assertions/calendar_assert.py
def get_assert():
    def assert_expected(output, context):
        import json
        
        try:
            # Parse JSON from LLM output
            data = json.loads(output)
            
            # Get expected values from test variables
            expected_name = context['vars']['expected_name']
            expected_event_type = context['vars']['expected_event_type']
            
            # Detailed field-by-field validation
            details = []
            score = 0
            total_fields = 2
            
            # Validate name
            if data.get('name') == expected_name:
                details.append({'field': 'Name', 'actual': data.get('name'), 'expected': expected_name, 'passed': True})
                score += 1
            else:
                details.append({'field': 'Name', 'actual': data.get('name'), 'expected': expected_name, 'passed': False})
            
            # Validate event type
            if data.get('event_type', '').lower() == expected_event_type.lower():
                details.append({'field': 'Event Type', 'actual': data.get('event_type'), 'expected': expected_event_type, 'passed': True})
                score += 1
            else:
                details.append({'field': 'Event Type', 'actual': data.get('event_type'), 'expected': expected_event_type, 'passed': False})
            
            return {
                'pass': score == total_fields,
                'score': score / total_fields,
                'reason': f'Field validation results: {total_fields - score} failed checks' if score < total_fields else 'All fields validated successfully',
                'details': details
            }
            
        except Exception as e:
            return {
                'pass': False,
                'score': 0.0,
                'reason': f'JSON parsing failed: {str(e)}',
                'details': []
            }
    
    return assert_expected
```

### Caching System

PromptDev includes a high-performance file-based cache:

- **Automatic Caching**: Caches agent outputs based on model, prompt, and inputs
- **TTL Support**: Configurable time-to-live for cache entries
- **Thread-Safe**: Concurrent evaluation support with atomic file operations
- **Cache Management**: CLI commands for stats and cleanup

### Rich Reporting

Comprehensive evaluation reports include:

- **Provider Comparison**: Side-by-side performance across multiple providers
- **Detailed Failure Analysis**: Field-level breakdowns for failed assertions
- **Hierarchical Test Display**: Tree view of failures organized by provider
- **Performance Metrics**: Pass rates, scores, and timing information
- **Error Summary**: Collected evaluation errors with full context

## Development

```bash
# Setup development environment
uv sync --extra dev

# Run tests
uv run pytest

# Format code
uv run ruff check promptdev/

# Type checking
uv run mypy promptdev/
```

## Roadmap

- [x] Core evaluation engine with PydanticAI integration
- [x] Multi-provider support for major AI platforms
- [x] YAML configuration loading with promptfoo compatibility
- [x] Comprehensive assertion types (JSON schema, Python, LLM-based)
- [x] File-based caching system with TTL support
- [x] Rich console reporting with failure analysis
- [ ] Simple file disk cache
- [ ] Better integration with PydanticAI, do not reinvent the wheel
- [ ] Testing
- [ ] Concurrent execution for faster large-scale evaluations
- [ ] Code cleanup
- [ ] Testing pensero promptfoo files
- [ ] Add support to run multiple test_cases
- [ ] CI/CD integration helpers with change detection
- [ ] Red team security testing capabilities
- [ ] Turso persistence for evaluation history and analytics
- [ ] Performance benchmarking and regression detection
- [ ] Distributed evaluation across multiple machines

## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `uv sync`
4. Make your changes and add tests
5. Run tests: `uv run pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/artefactop/promptdev.git
cd promptdev
uv sync
uv run pytest  # Run tests
uv run promptdev --help  # Test CLI
```

### Code Style

We use `ruff` for code formatting and linting, and `pytest` for testing. Please ensure your code follows these standards:

```bash
uv run ruff check .       # Lint code
uv run ruff format .      # Format code
uv run pytest           # Run tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on [PydanticAI](https://ai.pydantic.dev/) for type-safe AI agent development
- Inspired by [promptfoo](https://github.com/promptfoo/promptfoo) for evaluation concepts
- Uses [Rich](https://github.com/Textualize/rich) for beautiful console output