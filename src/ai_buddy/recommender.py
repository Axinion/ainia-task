"""
Activity recommendation system for AI Buddy.

This module provides functions to recommend educational activities to children
based on their profiles, available activities, and learning history.
"""

from typing import List, Dict, Any, Optional
from .data_models import Activity, ChildProfile
from .policy import total_score
from .session import SessionLog, recent_activity_ids


def recommend_activities(
    child: ChildProfile,
    activities: List[Activity],
    history: Optional[List[SessionLog]] = None,
    k: int = 3
) -> List[Activity]:
    """
    Recommend activities for a child based on their profile and history.
    
    Algorithm:
    1. Pre-filter: Age/grade soft filter (no-op for now)
    2. Score: Compute total_score for each activity
    3. Sort: Descending by score
    4. Diversity pass: Ensure at least 2 distinct activity types among first k
    5. Safety fallback: If < 2 results, relax recency penalty and re-pick
    6. Return: First min(k, 3) items (cap at 3 by default)
    
    Args:
        child: Child profile for recommendation
        activities: Available activities to choose from
        history: Optional session history for recency penalty
        k: Number of recommendations to return (capped at 3)
        
    Returns:
        List of recommended activities sorted by score
    """
    if not activities:
        return []
    
    # Convert history to list if None
    if history is None:
        history = []
    
    # Step 1: Pre-filter (no-op for now, Phase 2 will add age/grade filtering)
    filtered_activities = activities.copy()
    
    # Step 2: Score each activity
    scored_activities = []
    for activity in filtered_activities:
        score = total_score(activity, child, history)
        scored_activities.append((activity, score))
    
    # Step 3: Sort by score (descending)
    scored_activities.sort(key=lambda x: x[1], reverse=True)
    
    # Step 4: Diversity pass - ensure at least 2 distinct activity types
    selected = []
    selected_types = set()
    
    # Take top k candidates
    top_candidates = scored_activities[:k]
    
    for activity, score in top_candidates:
        selected.append((activity, score))
        selected_types.add(activity.type)
    
    # If we don't have at least 2 distinct types, try to diversify
    if len(selected_types) < 2 and len(scored_activities) > k:
        # Find the lowest-scored activity in our selection
        lowest_scored = min(selected, key=lambda x: x[1])
        lowest_activity, lowest_score = lowest_scored
        
        # Look for a different type among remaining candidates
        for activity, score in scored_activities[k:]:
            if activity.type not in selected_types:
                # Replace the lowest-scored with this different type
                selected.remove(lowest_scored)
                selected.append((activity, score))
                selected_types.add(activity.type)
                break
    
    # Step 5: Safety fallback - if we have less than 2 recommendations
    if len(selected) < 2:
        # Re-score without recency penalty (temporary relaxation)
        relaxed_scores = []
        for activity in filtered_activities:
            # Create a temporary history without recent activities for this specific activity
            temp_history = []
            for session in history:
                temp_session = SessionLog(
                    child_id=session.child_id,
                    attempts=[attempt for attempt in session.attempts if attempt.activity_id != activity.id]
                )
                if temp_session.attempts:
                    temp_history.append(temp_session)
            
            # Recalculate score without recency penalty for this activity
            score = total_score(activity, child, temp_history)
            relaxed_scores.append((activity, score))
        
        # Sort by relaxed scores and take top k
        relaxed_scores.sort(key=lambda x: x[1], reverse=True)
        selected = relaxed_scores[:k]
    
    # Step 6: Return activities (cap at 3)
    k = min(k, 3)
    recommended_activities = [activity for activity, score in selected[:k]]
    
    return recommended_activities


def explain_recommendation(
    child: ChildProfile,
    activity: Activity,
    history: Optional[List[SessionLog]] = None
) -> Dict[str, Any]:
    """
    Explain why an activity was recommended by breaking down the scoring components.
    
    Args:
        child: Child profile
        activity: Activity to explain
        history: Optional session history
        
    Returns:
        Dictionary with component scores and total score
    """
    if history is None:
        history = []
    
    # Import policy functions for component scoring
    from .policy import (
        skill_fit,
        interest_fit,
        style_fit,
        level_fit,
        time_fit,
        recency_penalty,
        WEIGHTS
    )
    
    # Get recent activity IDs for recency penalty
    recent_ids = recent_activity_ids(history, k=2)
    
    # Calculate each component score
    skill_score = skill_fit(activity, child)
    interest_score = interest_fit(activity, child)
    style_score = style_fit(activity, child)
    level_score = level_fit(activity, child)
    time_score = time_fit(activity, child)
    recency_penalty_score = recency_penalty(activity.id, recent_ids)
    
    # Calculate weighted total
    total = (
        WEIGHTS["skill_fit"] * skill_score +
        WEIGHTS["interest_fit"] * interest_score +
        WEIGHTS["style_fit"] * style_score +
        WEIGHTS["level_fit"] * level_score +
        WEIGHTS["time_fit"] * time_score -
        WEIGHTS["recency_penalty"] * recency_penalty_score
    )
    
    return {
        "activity_id": activity.id,
        "activity_title": activity.title,
        "activity_type": activity.type,
        "activity_level": activity.level,
        "component_scores": {
            "skill_fit": {
                "score": skill_score,
                "weight": WEIGHTS["skill_fit"],
                "weighted_score": WEIGHTS["skill_fit"] * skill_score
            },
            "interest_fit": {
                "score": interest_score,
                "weight": WEIGHTS["interest_fit"],
                "weighted_score": WEIGHTS["interest_fit"] * interest_score
            },
            "style_fit": {
                "score": style_score,
                "weight": WEIGHTS["style_fit"],
                "weighted_score": WEIGHTS["style_fit"] * style_score
            },
            "level_fit": {
                "score": level_score,
                "weight": WEIGHTS["level_fit"],
                "weighted_score": WEIGHTS["level_fit"] * level_score
            },
            "time_fit": {
                "score": time_score,
                "weight": WEIGHTS["time_fit"],
                "weighted_score": WEIGHTS["time_fit"] * time_score
            },
            "recency_penalty": {
                "score": recency_penalty_score,
                "weight": WEIGHTS["recency_penalty"],
                "weighted_score": WEIGHTS["recency_penalty"] * recency_penalty_score
            }
        },
        "total_score": total,
        "child_id": child.id,
        "child_name": child.name,
        "child_learning_style": child.learning_style,
        "child_reading_level": child.reading_level
    }


if __name__ == "__main__":
    """Main guard for running recommendations when module is executed directly."""
    from .loader import load_activities, load_profiles
    
    try:
        # Load data
        print("Loading activities and profiles...")
        activities = load_activities("data/activities.json")
        profiles = load_profiles("data/profiles.json")
        
        if not activities or not profiles:
            print("Error: Could not load activities or profiles")
            exit(1)
        
        # Pick the first child for demonstration
        child = profiles[0]
        print(f"\nRecommending activities for: {child.name} (ID: {child.id})")
        print(f"Learning style: {child.learning_style}")
        print(f"Reading level: {child.reading_level}")
        print(f"Attention span: {child.attention_span_min} minutes")
        print(f"Interests: {', '.join(child.interests) if child.interests else 'None'}")
        
        # Get recommendations
        print(f"\nGenerating recommendations...")
        recommended = recommend_activities(child, activities, history=None, k=3)
        
        if not recommended:
            print("No recommendations found.")
            exit(0)
        
        # Print recommendations with score breakdowns
        print(f"\nTop {len(recommended)} Recommendations:")
        print("=" * 60)
        
        for i, activity in enumerate(recommended, 1):
            explanation = explain_recommendation(child, activity, history=None)
            
            print(f"\n{i}. {activity.title}")
            print(f"   Type: {activity.type} | Level: {activity.level}")
            print(f"   Estimated time: {activity.estimated_min} minutes")
            print(f"   Skills: {', '.join(activity.skills)}")
            print(f"   Total Score: {explanation['total_score']:.3f}")
            
            # Show component scores
            print("   Component Scores:")
            for component, data in explanation['component_scores'].items():
                print(f"     {component}: {data['score']:.3f} (weight: {data['weight']:.2f})")
        
        print(f"\nRecommendation complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
