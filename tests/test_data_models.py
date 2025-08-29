"""
Tests for the data models module.

This module contains tests for the Activity and ChildProfile models.
"""

import pytest
from pydantic import ValidationError

from ai_buddy.data_models import Activity, ChildProfile


class TestActivity:
    """Test cases for Activity model."""
    
    def test_valid_activity(self):
        """Test creating a valid Activity instance."""
        activity_data = {
            "id": "math_001",
            "type": "math",
            "title": "Addition Practice",
            "description": "Practice basic addition with single digits",
            "level": "easy",
            "skills": ["addition", "number_sense"],
            "tags": ["elementary", "arithmetic"],
            "estimated_min": 15,
            "format": "qna",
            "rubric": {
                "accuracy": {"excellent": "90-100%", "good": "80-89%", "needs_work": "<80%"},
                "speed": {"excellent": "<2 min", "good": "2-3 min", "needs_work": ">3 min"}
            }
        }
        
        activity = Activity(**activity_data)
        assert activity.id == "math_001"
        assert activity.type == "math"
        assert activity.level == "easy"
        assert len(activity.skills) == 2
        assert activity.estimated_min == 15
    
    def test_invalid_activity_type(self):
        """Test that invalid activity type raises ValidationError."""
        activity_data = {
            "id": "invalid_001",
            "type": "invalid_type",  # Invalid type
            "title": "Invalid Activity",
            "description": "This should fail",
            "level": "easy",
            "skills": ["test"],
            "estimated_min": 10,
            "format": "qna",
            "rubric": {}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Activity(**activity_data)
        
        assert "type" in str(exc_info.value)
    
    def test_invalid_estimated_min(self):
        """Test that negative estimated_min raises ValidationError."""
        activity_data = {
            "id": "test_001",
            "type": "math",
            "title": "Test Activity",
            "description": "Test description",
            "level": "easy",
            "skills": ["test"],
            "estimated_min": 0,  # Invalid: must be > 0
            "format": "qna",
            "rubric": {}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Activity(**activity_data)
        
        assert "Estimated time must be greater than 0 minutes" in str(exc_info.value)
    
    def test_empty_skills(self):
        """Test that empty skills list raises ValidationError."""
        activity_data = {
            "id": "test_001",
            "type": "math",
            "title": "Test Activity",
            "description": "Test description",
            "level": "easy",
            "skills": [],  # Invalid: must be non-empty
            "estimated_min": 10,
            "format": "qna",
            "rubric": {}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            Activity(**activity_data)
        
        assert "Skills list cannot be empty" in str(exc_info.value)
    
    def test_default_tags(self):
        """Test that tags default to empty list."""
        activity_data = {
            "id": "test_001",
            "type": "math",
            "title": "Test Activity",
            "description": "Test description",
            "level": "easy",
            "skills": ["test"],
            "estimated_min": 10,
            "format": "qna",
            "rubric": {}
        }
        
        activity = Activity(**activity_data)
        assert activity.tags == []


class TestChildProfile:
    """Test cases for ChildProfile model."""
    
    def test_valid_child_profile(self):
        """Test creating a valid ChildProfile instance."""
        profile_data = {
            "id": "child_001",
            "name": "Alice Smith",
            "age": 8,
            "grade": 3,
            "interests": ["reading", "art", "science"],
            "learning_style": "visual",
            "attention_span_min": 20,
            "reading_level": "on_grade",
            "baseline_skills": {
                "math": 0.75,
                "reading": 0.85,
                "writing": 0.60
            },
            "goals": ["Improve writing skills", "Learn multiplication"]
        }
        
        profile = ChildProfile(**profile_data)
        assert profile.id == "child_001"
        assert profile.name == "Alice Smith"
        assert profile.age == 8
        assert profile.learning_style == "visual"
        assert profile.attention_span_min == 20
        assert len(profile.baseline_skills) == 3
    
    def test_kindergarten_values(self):
        """Test that 'K' is accepted for age and grade."""
        profile_data = {
            "id": "child_002",
            "name": "Bob Johnson",
            "age": "K",
            "grade": "K",
            "learning_style": "kinesthetic",
            "attention_span_min": 15,
            "reading_level": "pre_reader",
            "baseline_skills": {"social_skills": 0.80}
        }
        
        profile = ChildProfile(**profile_data)
        assert profile.age == "K"
        assert profile.grade == "K"
    
    def test_invalid_learning_style(self):
        """Test that invalid learning style raises ValidationError."""
        profile_data = {
            "id": "child_003",
            "name": "Charlie Brown",
            "age": 7,
            "grade": 2,
            "learning_style": "invalid_style",  # Invalid style
            "attention_span_min": 15,
            "reading_level": "emergent",
            "baseline_skills": {"math": 0.70}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChildProfile(**profile_data)
        
        assert "learning_style" in str(exc_info.value)
    
    def test_invalid_attention_span(self):
        """Test that non-positive attention span raises ValidationError."""
        profile_data = {
            "id": "child_004",
            "name": "Diana Prince",
            "age": 9,
            "grade": 4,
            "learning_style": "auditory",
            "attention_span_min": 0,  # Invalid: must be > 0
            "reading_level": "above_grade",
            "baseline_skills": {"reading": 0.90}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChildProfile(**profile_data)
        
        assert "Attention span must be greater than 0 minutes" in str(exc_info.value)
    
    def test_invalid_baseline_skills(self):
        """Test that baseline skills outside 0-1 range raises ValidationError."""
        profile_data = {
            "id": "child_005",
            "name": "Eve Wilson",
            "age": 6,
            "grade": 1,
            "learning_style": "logical",
            "attention_span_min": 10,
            "reading_level": "approaching",
            "baseline_skills": {
                "math": 1.5,  # Invalid: > 1.0
                "reading": -0.1  # Invalid: < 0.0
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ChildProfile(**profile_data)
        
        error_msg = str(exc_info.value)
        assert "must be between 0.0 and 1.0 inclusive" in error_msg
    
    def test_default_interests_and_goals(self):
        """Test that interests and goals default to empty lists."""
        profile_data = {
            "id": "child_006",
            "name": "Frank Miller",
            "age": 10,
            "grade": 5,
            "learning_style": "visual",
            "attention_span_min": 25,
            "reading_level": "on_grade",
            "baseline_skills": {"science": 0.65}
        }
        
        profile = ChildProfile(**profile_data)
        assert profile.interests == []
        assert profile.goals == []
