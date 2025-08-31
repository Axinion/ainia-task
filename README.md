# AI Buddy

An educational AI system that creates personalized learning experiences for children. It recommends activities, runs interactive sessions, and generates parent reports to track progress.

Built with Python, Streamlit, and Pydantic for a robust, type-safe foundation.

## Quickstart

### Installation

```bash
pip install -e ".[dev]"
```

### Check Your Data

```bash
python -m ai_buddy.loader
```

This shows a summary of your activities and child profiles.

## Activity Recommendations

### Run Activity Recommendations Demo

```bash
python -m ai_buddy.recommender
```

**What it does:**
- Shows top 3 activity recommendations for a child
- Breaks down how each recommendation was scored
- Explains why certain activities were chosen

**Example:**
```
Recommending activities for: Alice Smith
Top 3 Recommendations:
1. Story Comprehension (reading, medium)
2. Word Building (spelling, easy) 
3. Math Puzzles (logic, medium)
```

## Interactive Learning Sessions

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

## Parent Reports

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

## Demo & Submission

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

## Onboarding (Option B)

### First-Run Experience

The AI Buddy app features a comprehensive onboarding experience for new users:

**One-Scroll Landing Page:**
- **Hero Section**: "Meet your child's new learning buddy—safe, kind, and actually fun"
- **Child Selection**: Choose a child to preview with "Name (ID)" format
- **Why Parents Trust Us**: Privacy-focused value propositions
- **How It Works**: 3-step process explanation
- **Privacy Choices**: Configurable data collection preferences
- **Sample Report Preview**: Real report generation for selected child

**Key Features:**
- **Personalized Preview**: Select any child profile to see customized sample reports
- **Privacy Controls**: Three configurable settings with sensible defaults
- **Real Sample Data**: Uses actual report generation system for authentic previews
- **Seamless Transition**: Selected child becomes default in main app

### Accessing the Full App

**From Onboarding:**
- Click "Start in under a minute" to reveal the complete 3-tab interface
- Your child selection and privacy choices are preserved

**Re-opening Onboarding:**
- **Method 1**: Clear Streamlit session state via Menu → Rerun
- **Method 2**: Add `?onboard=1` query parameter to the URL
  - Example: `http://localhost:8501/?onboard=1`

### Privacy Management

**Onboarding Privacy Settings:**
- **Analytics**: Allow basic analytics (default: OFF)
- **Save Progress**: Save progress for personalized picks (default: ON)
- **Email Reports**: Email weekly reports (default: OFF)

**Main App Integration:**
- Privacy section in sidebar shows current choices
- "Edit choices" button for inline editing
- "Privacy Page" button for dedicated privacy settings page
- All changes persist across sessions

### Screenshot

![Onboarding Experience](docs/onboarding-screenshot.png)

*Screenshot placeholder: Shows the onboarding landing page with hero section, child selection, trust indicators, and sample report preview.*

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
