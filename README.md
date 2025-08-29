# AI Buddy

A minimal Python project for AI-related tasks and data processing. This project provides a clean foundation for building AI applications with proper data models, data loading utilities, and testing infrastructure. The modular structure allows for easy extension and maintenance of AI workflows.

## Quickstart

### Installation

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e ".[dev]"
```

### Run Data Summaries

```bash
python -m ai_buddy.loader
```

**Expected Output:**
```
Activities Summary:
  Total: 10
  By Type:
    math: 2
    reading: 2
    creativity: 1
    vocab: 2
    logic: 1
    spelling: 1
    storytelling: 1
  By Level:
    easy: 4
    medium: 5
    hard: 1

Profiles Summary:
  Total: 5
  By Reading Level:
    on_grade: 1
    pre_reader: 1
    emergent: 1
    above_grade: 1
    approaching: 1
  By Learning Style:
    visual: 2
    kinesthetic: 1
    logical: 1
    auditory: 1
```

## Installation

```bash
pip install -e .
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest -q
```

## Project Structure

- `src/ai_buddy/` - Main package with core functionality
- `data/` - Data storage directory
- `tests/` - Test suite
