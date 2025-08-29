"""
AI Buddy - Main session orchestrator.

This module provides the main interface for running educational sessions
with children, including activity recommendations, evaluation, and progress tracking.
"""

import argparse
from datetime import datetime
from typing import Optional, Tuple

from .data_models import Activity, ChildProfile
from .loader import load_activities, load_profiles
from .persist import load_history
from .recommender import recommend_activities
from .evaluate import eval_qna, eval_freeform, choose_outcome_from_eval
from .session import ActivityAttempt, append_attempt
from .persist import save_history, save_child_snapshot
from .simulate import answer


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(value, max_val))


def get_activity_intro(activity: Activity) -> str:
    """Generate a friendly introduction for an activity."""
    intros = {
        "math": f"Let's solve some math! {activity.title}",
        "spelling": f"Time to practice spelling! {activity.title}",
        "storytelling": f"Ready to tell a story? {activity.title}",
        "reading": f"Let's read together! {activity.title}",
        "vocab": f"Vocabulary time! {activity.title}",
        "logic": f"Let's think logically! {activity.title}",
        "creativity": f"Time to be creative! {activity.title}"
    }
    return intros.get(activity.type, f"Let's do this activity: {activity.title}")


def get_encouragement_and_tip(outcome: str) -> tuple[str, str]:
    """Get encouragement and tip based on outcome."""
    encouragements = {
        "success": ("Great job! You did amazing!", "Keep up this excellent work!"),
        "partial": ("Good effort! You're on the right track.", "Try to add a bit more detail next time."),
        "struggle": ("Don't worry, learning takes time!", "Let's practice this skill more together."),
        "skipped": ("That's okay, we can try again later.", "Sometimes it's good to take a break.")
    }
    return encouragements.get(outcome, ("Well done!", "Keep practicing!"))


def run_session_once(
    child_id: str,
    simulate: bool = True,
    activities: Optional[list[Activity]] = None,
    profiles: Optional[list[ChildProfile]] = None,
    history: Optional[list] = None
) -> Tuple[ChildProfile, list]:
    """
    Run a single activity session for testing purposes.
    
    Args:
        child_id: ID of the child to work with
        simulate: Whether to simulate answers or prompt for input
        activities: Pre-loaded activities (optional)
        profiles: Pre-loaded profiles (optional)
        history: Pre-loaded history (optional)
        
    Returns:
        Tuple of (updated_child, history_delta) where history_delta is the new attempts
    """
    # Load data if not provided
    if activities is None:
        activities = load_activities("data/activities.json")
    if profiles is None:
        profiles = load_profiles("data/profiles.json")
    if history is None:
        history = load_history("data/history.json")
    
    # Find child
    child = next((p for p in profiles if p.id == child_id), None)
    if not child:
        raise ValueError(f"Child with ID '{child_id}' not found!")
    
    # Get recommendations
    recommended = recommend_activities(child, activities, history, k=1)  # Just one activity
    
    if not recommended:
        raise ValueError("No activities available!")
    
    activity = recommended[0]
    
    # Get answer
    if simulate:
        user_answer = answer(child, activity)
    else:
        if activity.format == "qna":
            user_answer = input("Your answer: ")
        else:  # freeform
            print("Please write your response (press Enter twice when done):")
            lines = []
            while True:
                line = input()
                if line == "" and lines:  # Empty line after content
                    break
                lines.append(line)
            user_answer = "\n".join(lines)
    
    # Evaluate
    if activity.format == "qna":
        eval_result = eval_qna(user_answer, activity)
    else:
        eval_result = eval_freeform(user_answer, activity)
    
    outcome = choose_outcome_from_eval(eval_result)
    
    # Create activity attempt
    attempt = ActivityAttempt(
        activity_id=activity.id,
        timestamp=datetime.now(),
        outcome=outcome,
        details={
            "eval": eval_result,
            "activity": activity.id
        }
    )
    
    # Update history
    new_history = append_attempt(history, child.id, attempt)
    
    # Apply skill adaptation
    delta_map = {
        "success": 0.03,
        "partial": 0.01,
        "struggle": -0.01,
        "skipped": 0.0
    }
    delta = delta_map.get(outcome, 0.0)
    
    # Create a copy of the child for modification
    updated_child = ChildProfile.model_validate(child.model_dump())
    
    for skill in activity.skills:
        current_skill = updated_child.baseline_skills.get(skill, 0.5)
        new_skill = clamp(current_skill + delta, 0.0, 1.0)
        updated_child.baseline_skills[skill] = new_skill
    
    # Return updated child and the new attempt
    history_delta = [attempt]
    
    return updated_child, history_delta


def run_session(
    child_id: Optional[str] = None,
    simulate: bool = False,
    history_path: str = "data/history.json"
) -> None:
    """
    Run a complete session for one child.
    
    Args:
        child_id: ID of the child to work with (None = first child)
        simulate: Whether to simulate answers or prompt for input
        history_path: Path to history file
    """
    # Load data
    print("Loading activities and profiles...")
    activities = load_activities("data/activities.json")
    profiles = load_profiles("data/profiles.json")
    history = load_history(history_path)
    
    # Select child
    if child_id:
        child = next((p for p in profiles if p.id == child_id), None)
        if not child:
            print(f"❌ Child with ID '{child_id}' not found!")
            return
    else:
        child = profiles[0] if profiles else None
        if not child:
            print("❌ No children profiles found!")
            return
    
    print(f"👋 Hello {child.name}! Let's have a great learning session!")
    print(f"📚 Reading level: {child.reading_level} | 🎯 Learning style: {child.learning_style}")
    print()
    
    # Get recommendations
    print("🤔 Finding the perfect activities for you...")
    recommended = recommend_activities(child, activities, history, k=3)
    
    if not recommended:
        print("❌ No activities available!")
        return
    
    print(f"✨ I found {len(recommended)} great activities for you!")
    print()
    
    # Run through each activity
    for i, activity in enumerate(recommended, 1):
        print(f"--- Activity {i}/{len(recommended)} ---")
        print(get_activity_intro(activity))
        print(f"📝 {activity.description}")
        print(f"⏱️  Estimated time: {activity.estimated_min} minutes")
        print()
        
        # Get answer
        if simulate:
            user_answer = answer(child, activity)
            print(f"🤖 Simulated answer: {user_answer}")
        else:
            if activity.format == "qna":
                user_answer = input("Your answer: ")
            else:  # freeform
                print("Please write your response (press Enter twice when done):")
                lines = []
                while True:
                    line = input()
                    if line == "" and lines:  # Empty line after content
                        break
                    lines.append(line)
                user_answer = "\n".join(lines)
        
        print()
        
        # Evaluate
        if activity.format == "qna":
            eval_result = eval_qna(user_answer, activity)
        else:
            eval_result = eval_freeform(user_answer, activity)
        
        outcome = choose_outcome_from_eval(eval_result)
        
        # Create activity attempt
        attempt = ActivityAttempt(
            activity_id=activity.id,
            timestamp=datetime.now(),
            outcome=outcome,
            details={
                "eval": eval_result,
                "activity": activity.id
            }
        )
        
        # Update history
        history = append_attempt(history, child.id, attempt)
        
        # Apply skill adaptation
        delta_map = {
            "success": 0.03,
            "partial": 0.01,
            "struggle": -0.01,
            "skipped": 0.0
        }
        delta = delta_map.get(outcome, 0.0)
        
        for skill in activity.skills:
            current_skill = child.baseline_skills.get(skill, 0.5)
            new_skill = clamp(current_skill + delta, 0.0, 1.0)
            child.baseline_skills[skill] = new_skill
        
        # Print feedback
        encouragement, tip = get_encouragement_and_tip(outcome)
        print(f"💡 {encouragement}")
        print(f"💭 Tip: {tip}")
        print()
    
    # Save progress
    print("💾 Saving your progress...")
    save_history(history, history_path)
    save_child_snapshot(child, f"data/snapshots/{child.id}.json")
    
    print("🎉 Session complete! You're doing great!")
    print(f"📊 Your skills have been updated and saved.")


def main():
    """Main entry point for the buddy module."""
    parser = argparse.ArgumentParser(description="AI Buddy - Educational Session Runner")
    parser.add_argument("--child", help="Child ID to work with (e.g., C001)")
    parser.add_argument("--simulate", action="store_true", help="Simulate answers instead of prompting")
    parser.add_argument("--history", default="data/history.json", help="Path to history file")
    
    args = parser.parse_args()
    
    try:
        run_session(
            child_id=args.child,
            simulate=args.simulate,
            history_path=args.history
        )
    except KeyboardInterrupt:
        print("\n👋 Session interrupted. See you next time!")
    except Exception as e:
        print(f"❌ Error during session: {e}")


if __name__ == "__main__":
    main()
