"""
AI Buddy - A minimal Python project for AI-related tasks.

This package provides data models, loading utilities, and helper functions
for AI applications.
"""

__version__ = "0.1.0"
__author__ = "AI Buddy Team"

# Import main models
from .data_models import Activity, ChildProfile

# Import loader functions
from .loader import (
    load_json,
    load_activities,
    load_profiles,
    summarize_activities,
    summarize_profiles
)

# Import policy functions
from .policy import (
    WEIGHTS,
    skill_fit,
    interest_fit,
    style_fit,
    level_fit,
    time_fit,
    recency_penalty,
    total_score,
    mean,
    normalize_text
)

# Import session functions
from .session import (
    ActivityAttempt,
    SessionLog,
    recent_activity_ids,
    append_attempt
)

# Import recommender functions
from .recommender import (
    recommend_activities,
    explain_recommendation
)

# Import evaluation functions
from .evaluate import (
    eval_qna,
    eval_freeform,
    choose_outcome_from_eval
)

# Import persistence functions
from .persist import (
    save_history,
    load_history,
    save_child_snapshot
)

# Import simulation functions
from .simulate import answer

# Import buddy functions
from .buddy import run_session, run_session_once

# TODO: Add more imports as modules are implemented
# from .utils import *

__all__ = [
    "__version__",
    "__author__",
    "Activity",
    "ChildProfile",
    "load_json",
    "load_activities",
    "load_profiles",
    "summarize_activities",
    "summarize_profiles",
    "WEIGHTS",
    "skill_fit",
    "interest_fit",
    "style_fit",
    "level_fit",
    "time_fit",
    "recency_penalty",
    "total_score",
    "mean",
    "normalize_text",
    "ActivityAttempt",
    "SessionLog",
    "recent_activity_ids",
    "append_attempt",
    "recommend_activities",
    "explain_recommendation",
    "eval_qna",
    "eval_freeform",
    "choose_outcome_from_eval",
    "save_history",
    "load_history",
    "save_child_snapshot",
    "answer",
    "run_session",
    "run_session_once",
]
