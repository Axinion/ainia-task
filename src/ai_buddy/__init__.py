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
]
