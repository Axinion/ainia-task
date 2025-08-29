"""
Tests for the data loader module.

This module contains tests for the loader functions.
"""

import pytest
import json
from pathlib import Path

from ai_buddy.loader import load_activities, load_profiles


def test_load_activities_success():
    """Test loading activities from data/activities.json."""
    activities = load_activities("data/activities.json")
    
    # Assert we have at least 10 activities
    assert len(activities) >= 10
    
    # Assert IDs are unique
    activity_ids = [activity.id for activity in activities]
    assert len(activity_ids) == len(set(activity_ids)), "Activity IDs must be unique"
    
    # Assert all activities are valid Activity objects
    for activity in activities:
        assert hasattr(activity, 'id')
        assert hasattr(activity, 'type')
        assert hasattr(activity, 'title')
        assert hasattr(activity, 'level')


def test_load_profiles_success():
    """Test loading profiles from data/profiles.json."""
    profiles = load_profiles("data/profiles.json")
    
    # Assert we have at least 3 profiles
    assert len(profiles) >= 3
    
    # Assert names are unique
    profile_names = [profile.name for profile in profiles]
    assert len(profile_names) == len(set(profile_names)), "Profile names must be unique"
    
    # Assert all profiles are valid ChildProfile objects
    for profile in profiles:
        assert hasattr(profile, 'id')
        assert hasattr(profile, 'name')
        assert hasattr(profile, 'learning_style')
        assert hasattr(profile, 'reading_level')


def test_validation_errors(tmp_path):
    """Test validation errors with malformed JSON data."""
    # Create a malformed activity with estimated_min = 0 (invalid)
    malformed_activity = {
        "id": "test_001",
        "type": "math",
        "title": "Test Activity",
        "description": "Test description",
        "level": "easy",
        "skills": ["test_skill"],
        "estimated_min": 0,  # Invalid: must be > 0
        "format": "qna",
        "rubric": {}
    }
    
    # Write malformed data to temporary file
    malformed_file = tmp_path / "malformed_activities.json"
    with open(malformed_file, 'w') as f:
        json.dump([malformed_activity], f)
    
    # Assert that loading raises ValueError with validation error
    with pytest.raises(ValueError, match="Activity at index 0"):
        load_activities(str(malformed_file))
    
    # Create a malformed profile with invalid baseline_skills
    malformed_profile = {
        "id": "child_001",
        "name": "Test Child",
        "age": 8,
        "grade": 3,
        "learning_style": "visual",
        "attention_span_min": 20,
        "reading_level": "on_grade",
        "baseline_skills": {
            "math": 1.5  # Invalid: must be between 0.0 and 1.0
        }
    }
    
    # Write malformed profile data to temporary file
    malformed_profile_file = tmp_path / "malformed_profiles.json"
    with open(malformed_profile_file, 'w') as f:
        json.dump([malformed_profile], f)
    
    # Assert that loading raises ValueError with validation error
    with pytest.raises(ValueError, match="Profile at index 0"):
        load_profiles(str(malformed_profile_file))

