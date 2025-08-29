"""
Tests for the loader functions.

This module contains tests for the JSON loading, activity/profile loading,
and summarization functions.
"""

import pytest
import tempfile
import json
from pathlib import Path

from ai_buddy.loader import (
    load_json,
    load_activities,
    load_profiles,
    summarize_activities,
    summarize_profiles
)
from ai_buddy.data_models import Activity, ChildProfile


class TestLoadJson:
    """Test cases for load_json function."""
    
    def test_load_valid_json(self):
        """Test loading valid JSON data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data", "number": 42}, f)
            temp_file = f.name
        
        try:
            data = load_json(temp_file)
            assert data == {"test": "data", "number": 42}
        finally:
            Path(temp_file).unlink()
    
    def test_load_nonexistent_file(self):
        """Test that loading non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            load_json("nonexistent_file.json")
    
    def test_load_invalid_json(self):
        """Test that loading invalid JSON raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json, missing: quotes}')
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid JSON"):
                load_json(temp_file)
        finally:
            Path(temp_file).unlink()


class TestLoadActivities:
    """Test cases for load_activities function."""
    
    def test_load_valid_activities(self):
        """Test loading valid activities data."""
        activities_data = [
            {
                "id": "test_001",
                "type": "math",
                "title": "Test Activity",
                "description": "Test description",
                "level": "easy",
                "skills": ["test_skill"],
                "estimated_min": 10,
                "format": "qna",
                "rubric": {}
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(activities_data, f)
            temp_file = f.name
        
        try:
            activities = load_activities(temp_file)
            assert len(activities) == 1
            assert isinstance(activities[0], Activity)
            assert activities[0].id == "test_001"
            assert activities[0].type == "math"
        finally:
            Path(temp_file).unlink()
    
    def test_load_activities_not_list(self):
        """Test that loading non-list data raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"not": "a list"}, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Expected list of activities"):
                load_activities(temp_file)
        finally:
            Path(temp_file).unlink()
    
    def test_load_activities_validation_error(self):
        """Test that validation errors include item index."""
        activities_data = [
            {
                "id": "test_001",
                "type": "math",
                "title": "Test Activity",
                "description": "Test description",
                "level": "easy",
                "skills": ["test_skill"],
                "estimated_min": 10,
                "format": "qna",
                "rubric": {}
            },
            {
                "id": "test_002",
                "type": "invalid_type",  # Invalid type
                "title": "Invalid Activity",
                "description": "Test description",
                "level": "easy",
                "skills": ["test_skill"],
                "estimated_min": 10,
                "format": "qna",
                "rubric": {}
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(activities_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Activity at index 1"):
                load_activities(temp_file)
        finally:
            Path(temp_file).unlink()


class TestLoadProfiles:
    """Test cases for load_profiles function."""
    
    def test_load_valid_profiles(self):
        """Test loading valid profiles data."""
        profiles_data = [
            {
                "id": "child_001",
                "name": "Test Child",
                "age": 8,
                "grade": 3,
                "learning_style": "visual",
                "attention_span_min": 20,
                "reading_level": "on_grade",
                "baseline_skills": {"math": 0.75}
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(profiles_data, f)
            temp_file = f.name
        
        try:
            profiles = load_profiles(temp_file)
            assert len(profiles) == 1
            assert isinstance(profiles[0], ChildProfile)
            assert profiles[0].id == "child_001"
            assert profiles[0].name == "Test Child"
        finally:
            Path(temp_file).unlink()
    
    def test_load_profiles_not_list(self):
        """Test that loading non-list data raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"not": "a list"}, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Expected list of profiles"):
                load_profiles(temp_file)
        finally:
            Path(temp_file).unlink()
    
    def test_load_profiles_validation_error(self):
        """Test that validation errors include item index."""
        profiles_data = [
            {
                "id": "child_001",
                "name": "Test Child",
                "age": 8,
                "grade": 3,
                "learning_style": "visual",
                "attention_span_min": 20,
                "reading_level": "on_grade",
                "baseline_skills": {"math": 0.75}
            },
            {
                "id": "child_002",
                "name": "Invalid Child",
                "age": 7,
                "grade": 2,
                "learning_style": "invalid_style",  # Invalid style
                "attention_span_min": 15,
                "reading_level": "emergent",
                "baseline_skills": {"reading": 0.70}
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(profiles_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="Profile at index 1"):
                load_profiles(temp_file)
        finally:
            Path(temp_file).unlink()


class TestSummarizeActivities:
    """Test cases for summarize_activities function."""
    
    def test_summarize_activities(self):
        """Test activity summarization."""
        activities = [
            Activity(
                id="math_001",
                type="math",
                title="Math Activity",
                description="Test",
                level="easy",
                skills=["addition"],
                estimated_min=10,
                format="qna",
                rubric={}
            ),
            Activity(
                id="reading_001",
                type="reading",
                title="Reading Activity",
                description="Test",
                level="medium",
                skills=["comprehension"],
                estimated_min=15,
                format="qna",
                rubric={}
            ),
            Activity(
                id="math_002",
                type="math",
                title="Another Math Activity",
                description="Test",
                level="hard",
                skills=["multiplication"],
                estimated_min=20,
                format="freeform",
                rubric={}
            )
        ]
        
        summary = summarize_activities(activities)
        
        assert summary["total"] == 3
        assert summary["by_type"]["math"] == 2
        assert summary["by_type"]["reading"] == 1
        assert summary["by_level"]["easy"] == 1
        assert summary["by_level"]["medium"] == 1
        assert summary["by_level"]["hard"] == 1


class TestSummarizeProfiles:
    """Test cases for summarize_profiles function."""
    
    def test_summarize_profiles(self):
        """Test profile summarization."""
        profiles = [
            ChildProfile(
                id="child_001",
                name="Alice",
                age=8,
                grade=3,
                learning_style="visual",
                attention_span_min=20,
                reading_level="on_grade",
                baseline_skills={"math": 0.75}
            ),
            ChildProfile(
                id="child_002",
                name="Bob",
                age=7,
                grade=2,
                learning_style="auditory",
                attention_span_min=15,
                reading_level="emergent",
                baseline_skills={"reading": 0.70}
            ),
            ChildProfile(
                id="child_003",
                name="Charlie",
                age=9,
                grade=4,
                learning_style="visual",
                attention_span_min=25,
                reading_level="above_grade",
                baseline_skills={"writing": 0.85}
            )
        ]
        
        summary = summarize_profiles(profiles)
        
        assert summary["total"] == 3
        assert summary["by_learning_style"]["visual"] == 2
        assert summary["by_learning_style"]["auditory"] == 1
        assert summary["by_reading_level"]["on_grade"] == 1
        assert summary["by_reading_level"]["emergent"] == 1
        assert summary["by_reading_level"]["above_grade"] == 1
