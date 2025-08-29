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

## Phase 2: Recommendations

### Run Activity Recommendations Demo

```bash
python -m ai_buddy.recommender
```

**What it prints:**
- Top 3 personalized activity recommendations for a sample child
- Detailed score component breakdowns for each recommendation
- Shows how skill fit, interest fit, style fit, level fit, time fit, and recency penalty contribute to the final score

**Example Output:**
```
Recommending activities for: Alice Smith (ID: child_001)
Learning style: visual
Reading level: on_grade
Attention span: 20 minutes
Interests: reading, art, science

Top 3 Recommendations:
============================================================

1. Story Comprehension
   Type: reading | Level: medium
   Estimated time: 20 minutes
   Skills: reading_comprehension, vocabulary
   Total Score: 0.655
   Component Scores:
     skill_fit: 0.500 (weight: 0.35)
     interest_fit: 1.000 (weight: 0.20)
     style_fit: 0.500 (weight: 0.15)
     level_fit: 0.700 (weight: 0.15)
     time_fit: 1.000 (weight: 0.10)
     recency_penalty: 0.000 (weight: 0.05)
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
