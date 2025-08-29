#!/usr/bin/env python3
"""
Phase 1 Verification Script

This script validates that the AI Buddy Phase 1 implementation is complete and working correctly.
"""

import sys
from pathlib import Path

# Add src to path so we can import from ai_buddy
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_buddy.loader import (
    load_activities,
    load_profiles,
    summarize_activities,
    summarize_profiles
)
import pytest


def main():
    """Main verification function."""
    try:
        print("🔍 Verifying Phase 1 implementation...")
        
        # 1. Load data files
        print("📁 Loading data files...")
        activities = load_activities("data/activities.json")
        profiles = load_profiles("data/profiles.json")
        
        # 2. Validate data requirements
        print("✅ Validating data requirements...")
        
        # Check minimum counts
        if len(activities) < 10:
            raise SystemExit(f"❌ Expected at least 10 activities, got {len(activities)}")
        
        if len(profiles) < 3:
            raise SystemExit(f"❌ Expected at least 3 profiles, got {len(profiles)}")
        
        # Check uniqueness
        activity_ids = [activity.id for activity in activities]
        if len(activity_ids) != len(set(activity_ids)):
            raise SystemExit("❌ Activity IDs are not unique")
        
        profile_names = [profile.name for profile in profiles]
        if len(profile_names) != len(set(profile_names)):
            raise SystemExit("❌ Profile names are not unique")
        
        print(f"✅ Data validation passed: {len(activities)} activities, {len(profiles)} profiles")
        
        # 3. Generate and print summaries
        print("\n📊 Activity Summary:")
        activities_summary = summarize_activities(activities)
        print(f"  Total: {activities_summary['total']}")
        print("  By Type:")
        for activity_type, count in activities_summary["by_type"].items():
            print(f"    {activity_type}: {count}")
        print("  By Level:")
        for level, count in activities_summary["by_level"].items():
            print(f"    {level}: {count}")
        
        print("\n📊 Profile Summary:")
        profiles_summary = summarize_profiles(profiles)
        print(f"  Total: {profiles_summary['total']}")
        print("  By Reading Level:")
        for reading_level, count in profiles_summary["by_reading_level"].items():
            print(f"    {reading_level}: {count}")
        print("  By Learning Style:")
        for learning_style, count in profiles_summary["by_learning_style"].items():
            print(f"    {learning_style}: {count}")
        
        # 4. Run tests programmatically
        print("\n🧪 Running tests...")
        test_result = pytest.main(["-q"])
        if test_result != 0:
            raise SystemExit(f"❌ Tests failed with exit code {test_result}")
        
        print("✅ All tests passed")
        
        # 5. Success message
        print("\n✅ Phase 1 complete")
        
    except ImportError as e:
        raise SystemExit(f"❌ Import error: {e}")
    except FileNotFoundError as e:
        raise SystemExit(f"❌ File not found: {e}")
    except Exception as e:
        raise SystemExit(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
