#!/usr/bin/env python3
"""
Seed demo history data for AI Buddy.

This script generates realistic activity attempts for the first two children
to populate the history with demo data for testing and demonstration.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path
import random

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_buddy.loader import load_activities, load_profiles
from ai_buddy.persist import load_history, save_history
from ai_buddy.session import SessionLog, ActivityAttempt


def generate_demo_attempts(child_id: str, activities: list, num_attempts: int = 4) -> list[ActivityAttempt]:
    """
    Generate demo activity attempts for a child.
    
    Args:
        child_id: ID of the child
        activities: List of available activities
        num_attempts: Number of attempts to generate
        
    Returns:
        List of ActivityAttempt objects
    """
    attempts = []
    
    # Get timestamps in the last 7 days
    now = datetime.now()
    timestamps = []
    for i in range(num_attempts):
        # Random time in last 7 days
        days_ago = random.uniform(0, 7)
        hours_ago = random.uniform(0, 24)
        timestamp = now - timedelta(days=days_ago, hours=hours_ago)
        timestamps.append(timestamp)
    
    # Sort timestamps (oldest first)
    timestamps.sort()
    
    # Select activities from different types
    activity_types = ["reading", "math", "spelling", "vocab"]
    selected_activities = []
    
    for activity_type in activity_types:
        type_activities = [a for a in activities if a.type == activity_type]
        if type_activities:
            selected_activities.append(random.choice(type_activities))
    
    # If we don't have enough activities, add some random ones
    while len(selected_activities) < num_attempts:
        selected_activities.append(random.choice(activities))
    
    # Generate attempts
    outcomes = ["success", "partial", "struggle"]
    outcome_weights = [0.4, 0.3, 0.3]  # 40% success, 30% partial, 30% struggle
    
    for i in range(num_attempts):
        activity = selected_activities[i % len(selected_activities)]
        outcome = random.choices(outcomes, weights=outcome_weights)[0]
        
        attempt = ActivityAttempt(
            activity_id=activity.id,
            timestamp=timestamps[i],
            outcome=outcome,
            details={
                "demo_generated": True,
                "activity_type": activity.type,
                "activity_level": activity.level
            }
        )
        attempts.append(attempt)
    
    return attempts


def main():
    """Main function to seed demo history data."""
    print("🌱 Seeding demo history data...")
    
    try:
        # Load data
        activities = load_activities("data/activities.json")
        profiles = load_profiles("data/profiles.json")
        existing_history = load_history("data/history.json")
        
        print(f"📊 Loaded {len(activities)} activities, {len(profiles)} profiles")
        
        # Check if history is already populated
        total_attempts = sum(len(session.attempts) for session in existing_history)
        if total_attempts >= 3:
            print("✅ seed: already populated")
            sys.exit(0)
        
        # Get first two children
        if len(profiles) < 2:
            print("❌ Need at least 2 children profiles to seed data")
            sys.exit(1)
        
        children_to_seed = profiles[:2]
        print(f"👥 Seeding data for: {children_to_seed[0].name}, {children_to_seed[1].name}")
        
        # Generate demo sessions
        new_sessions = []
        total_new_attempts = 0
        
        for child in children_to_seed:
            # Generate 3-5 attempts per child
            num_attempts = random.randint(3, 5)
            attempts = generate_demo_attempts(child.id, activities, num_attempts)
            
            session = SessionLog(
                child_id=child.id,
                attempts=attempts
            )
            new_sessions.append(session)
            total_new_attempts += len(attempts)
            
            print(f"   📝 {child.name}: {len(attempts)} attempts")
        
        # Combine with existing history
        all_history = existing_history + new_sessions
        
        # Save to file
        save_history(all_history, "data/history.json")
        
        print(f"💾 Saved {total_new_attempts} new attempts to data/history.json")
        print("✅ Demo history seeding complete!")
        
    except Exception as e:
        print(f"❌ Error seeding history: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
