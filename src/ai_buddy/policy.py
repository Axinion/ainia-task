"""
Deterministic scoring policy for recommending activities to children.

This module provides functions to score activities based on child profiles,
learning preferences, and activity history.
"""

from typing import List, Dict, Any, Optional
from .data_models import Activity, ChildProfile


# Scoring weights for different factors
WEIGHTS = {
    "skill_fit": 0.35,
    "interest_fit": 0.20,
    "style_fit": 0.15,
    "level_fit": 0.15,
    "time_fit": 0.10,
    "recency_penalty": 0.05
}


def mean(lst: List[float], default: float = 0.0) -> float:
    """
    Calculate the mean of a list of numbers.
    
    Args:
        lst: List of numbers
        default: Default value if list is empty
        
    Returns:
        Mean of the list or default value if empty
    """
    if not lst:
        return default
    return sum(lst) / len(lst)


def normalize_text(s: str) -> str:
    """
    Normalize text for case-insensitive matching.
    
    Args:
        s: Input string
        
    Returns:
        Lowercase string with whitespace stripped
    """
    return s.lower().strip()


def skill_fit(activity: Activity, child: ChildProfile) -> float:
    """
    Calculate skill fit between activity and child.
    
    For each skill in activity.skills, look up child.baseline_skills;
    if missing, use 0.5. Return mean.
    
    Args:
        activity: The activity to score
        child: The child profile
        
    Returns:
        Skill fit score between 0.0 and 1.0
    """
    skill_scores = []
    for skill in activity.skills:
        # Look up skill in child's baseline_skills, default to 0.5 if missing
        score = child.baseline_skills.get(skill, 0.5)
        skill_scores.append(score)
    
    return mean(skill_scores, default=0.5)


def interest_fit(activity: Activity, child: ChildProfile) -> float:
    """
    Calculate interest fit between activity and child.
    
    Return 1.0 if activity.type or any activity.tags intersects child.interests
    (case-insensitive, fuzzy contains ok), else 0.4.
    
    Args:
        activity: The activity to score
        child: The child profile
        
    Returns:
        Interest fit score between 0.0 and 1.0
    """
    # Normalize all text for case-insensitive comparison
    activity_type = normalize_text(activity.type)
    activity_tags = [normalize_text(tag) for tag in activity.tags]
    child_interests = [normalize_text(interest) for interest in child.interests]
    
    # Check if activity type matches any child interest
    if activity_type in child_interests:
        return 1.0
    
    # Check if any activity tag matches any child interest (fuzzy contains)
    for tag in activity_tags:
        for interest in child_interests:
            if tag in interest or interest in tag:
                return 1.0
    
    return 0.4


def style_fit(activity: Activity, child: ChildProfile) -> float:
    """
    Calculate learning style fit between activity and child.
    
    Maps child.learning_style to preferred signals:
    - visual -> tags {"visual","picture","drawing"}, formats {"freeform"}
    - auditory -> types {"storytelling","reading"}, formats {"freeform"}
    - logical -> types {"math","logic"}, tags {"puzzles","reasoning"}
    - kinesthetic -> tags {"quick","applied","fluency"}, estimated_min <= attention_span_min
    
    Args:
        activity: The activity to score
        child: The child profile
        
    Returns:
        Style fit score between 0.0 and 1.0
    """
    activity_type = normalize_text(activity.type)
    activity_tags = [normalize_text(tag) for tag in activity.tags]
    activity_format = normalize_text(activity.format)
    
    if child.learning_style == "visual":
        # Visual learners prefer visual content and freeform activities
        preferred_tags = {"visual", "picture", "drawing"}
        preferred_formats = {"freeform"}
        
        if (any(tag in preferred_tags for tag in activity_tags) or 
            activity_format in preferred_formats):
            return 1.0
    
    elif child.learning_style == "auditory":
        # Auditory learners prefer storytelling, reading, and freeform activities
        preferred_types = {"storytelling", "reading"}
        preferred_formats = {"freeform"}
        
        if (activity_type in preferred_types or 
            activity_format in preferred_formats):
            return 1.0
    
    elif child.learning_style == "logical":
        # Logical learners prefer math, logic, puzzles, and reasoning
        preferred_types = {"math", "logic"}
        preferred_tags = {"puzzles", "reasoning"}
        
        if (activity_type in preferred_types or 
            any(tag in preferred_tags for tag in activity_tags)):
            return 1.0
    
    elif child.learning_style == "kinesthetic":
        # Kinesthetic learners prefer quick, applied activities that fit attention span
        preferred_tags = {"quick", "applied", "fluency"}
        time_fits = activity.estimated_min <= child.attention_span_min
        
        if (any(tag in preferred_tags for tag in activity_tags) or 
            time_fits):
            return 1.0
    
    return 0.5


def level_fit(activity: Activity, child: ChildProfile) -> float:
    """
    Calculate difficulty level fit between activity and child.
    
    Compute child_mean_skill over activity.skills.
    - "easy": aligned if mean_skill < 0.6
    - "medium": aligned if 0.6 <= mean_skill <= 0.8
    - "hard": aligned if mean_skill > 0.8
    
    Return 1.0 if aligned, 0.7 if "adjacent" band, else 0.4.
    
    Args:
        activity: The activity to score
        child: The child profile
        
    Returns:
        Level fit score between 0.0 and 1.0
    """
    # Calculate mean skill level for the activity's skills
    skill_scores = []
    for skill in activity.skills:
        score = child.baseline_skills.get(skill, 0.5)
        skill_scores.append(score)
    
    mean_skill = mean(skill_scores, default=0.5)
    
    # Define skill bands
    if activity.level == "easy":
        aligned_band = mean_skill < 0.6
        adjacent_band = 0.6 <= mean_skill <= 0.8
    elif activity.level == "medium":
        aligned_band = 0.6 <= mean_skill <= 0.8
        adjacent_band = (mean_skill < 0.6) or (mean_skill > 0.8)
    else:  # hard
        aligned_band = mean_skill > 0.8
        adjacent_band = 0.6 <= mean_skill <= 0.8
    
    if aligned_band:
        return 1.0
    elif adjacent_band:
        return 0.7
    else:
        return 0.4


def time_fit(activity: Activity, child: ChildProfile) -> float:
    """
    Calculate time fit between activity and child's attention span.
    
    If activity.estimated_min <= child.attention_span_min: 1.0
    Else linearly decay to 0.5 using ratio child.attention_span_min / estimated_min,
    clamped [0.5,1.0].
    
    Args:
        activity: The activity to score
        child: The child profile
        
    Returns:
        Time fit score between 0.0 and 1.0
    """
    if activity.estimated_min <= child.attention_span_min:
        return 1.0
    
    # Calculate ratio and apply linear decay
    ratio = child.attention_span_min / activity.estimated_min
    # Linear decay from 1.0 to 0.5 as ratio decreases
    score = 0.5 + (0.5 * ratio)
    
    # Clamp between 0.5 and 1.0
    return max(0.5, min(1.0, score))


def recency_penalty(activity_id: str, history: List[str], recent_k: int = 2) -> float:
    """
    Calculate recency penalty for an activity.
    
    If activity_id present among last recent_k attempts: 1.0 else 0.0.
    
    Args:
        activity_id: The activity ID to check
        history: List of recent activity IDs (most recent first)
        recent_k: Number of recent activities to check
        
    Returns:
        Recency penalty score (1.0 if recently attempted, 0.0 otherwise)
    """
    if not history:
        return 0.0
    
    # Check if activity_id is in the last recent_k attempts
    recent_activities = history[:recent_k]
    return 1.0 if activity_id in recent_activities else 0.0


def total_score(activity: Activity, child: ChildProfile, history: List[str]) -> float:
    """
    Calculate total recommendation score for an activity.
    
    Args:
        activity: The activity to score
        child: The child profile
        history: List of recent activity IDs (most recent first)
        
    Returns:
        Total recommendation score
    """
    skill_score = skill_fit(activity, child)
    interest_score = interest_fit(activity, child)
    style_score = style_fit(activity, child)
    level_score = level_fit(activity, child)
    time_score = time_fit(activity, child)
    recency_penalty_score = recency_penalty(activity.id, history)
    
    # Calculate weighted total score
    total = (
        WEIGHTS["skill_fit"] * skill_score +
        WEIGHTS["interest_fit"] * interest_score +
        WEIGHTS["style_fit"] * style_score +
        WEIGHTS["level_fit"] * level_score +
        WEIGHTS["time_fit"] * time_score -
        WEIGHTS["recency_penalty"] * recency_penalty_score
    )
    
    return total


# Export the weights for external tuning
__all__ = [
    "WEIGHTS",
    "skill_fit",
    "interest_fit", 
    "style_fit",
    "level_fit",
    "time_fit",
    "recency_penalty",
    "total_score",
    "mean",
    "normalize_text"
]
