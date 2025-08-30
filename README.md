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

## Phase 3: Buddy Session

### Run Complete Educational Sessions

**Simulated run (automated answers):**
```bash
python -m ai_buddy.buddy --child C001 --simulate
```

**Manual run (type your own answers):**
```bash
python -m ai_buddy.buddy --child C001
```

**What it does:**
- Loads activities, profiles, and session history
- Recommends 3 personalized activities for the child
- For each activity:
  - Presents the activity with friendly introduction
  - Gets answer (simulated or manual input)
  - Evaluates the response and provides feedback
  - Updates child's skills based on performance
  - Saves progress automatically

**Console Output:**
```
Loading activities and profiles...
👋 Hello Alice Smith! Let's have a great learning session!
📚 Reading level: on_grade | 🎯 Learning style: visual

🤔 Finding the perfect activities for you...
✨ I found 3 great activities for you!

--- Activity 1/3 ---
Let's read together! Story Comprehension
📝 Read a short story and answer comprehension questions
⏱️  Estimated time: 20 minutes

🤖 Simulated answer: comprehension

💡 Don't worry, learning takes time!
💭 Tip: Let's practice this skill more together.

💾 Saving your progress...
🎉 Session complete! You're doing great!
📊 Your skills have been updated and saved.
```

**Saved Files:**
- `data/history.json` - Complete session history with all attempts
- `data/snapshots/C001.json` - Updated child profile with new skill levels

## Phase 4: Parent Reports

### Generate Parent Reports

**Generate for one child (7 days):**
```bash
python -m ai_buddy.report --child C001 --period 7d --format md
```

**Generate for all children (Markdown + JSON):**
```bash
python -m ai_buddy.report --all --period 7d --format both
```

**What it does:**
- Analyzes child's activity history over the specified period
- Calculates skill performance metrics and identifies strengths/growth areas
- Generates personalized activity recommendations
- Provides actionable tips for home learning

**Output Files:**
- Writes to `./reports/{child_id}_YYYY-MM-DD.md` and `.json`
- Creates reports directory automatically if it doesn't exist

**Report Sections:**
- **Highlights** - Sparks (strengths) and growth areas based on performance
- **Activity Snapshot** - Performance breakdown by activity type and skill
- **Recommended Next Activities** - Personalized suggestions for continued learning
- **Try at Home** - Practical tips for parents to support learning at home

**Example Output:**
```
Wrote:
 - reports/C001_2024-01-15.md
 - reports/C001_2024-01-15.json
```

## Phase 5: Demo & Submission

### Quick Start

**One command demo:**
```bash
make demo
```

**First-time setup (optional):**
```bash
make seed
```

**Generate reports for all:**
```bash
make report-all
```

**Run tests:**
```bash
make test
```

**Create a shareable bundle:**
```bash
make bundle
```

### Troubleshooting

- **If Streamlit can't find modules**: Run `python -m pip install -e .`
- **If history is empty**: Click "Seed demo data" in the UI or run `make seed`

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
