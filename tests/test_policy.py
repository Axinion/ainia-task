"""
Tests for the policy module.

This module contains tests for the scoring policy functions.
"""

import pytest

from ai_buddy.data_models import Activity, ChildProfile
from ai_buddy.policy import (
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


class TestHelperFunctions:
    """Test cases for helper functions."""
    
    def test_mean(self):
        """Test mean function."""
        assert mean([1, 2, 3]) == 2.0
        assert abs(mean([0.5, 0.7, 0.9]) - 0.7) < 0.001
        assert mean([]) == 0.0
        assert mean([], default=0.5) == 0.5
    
    def test_normalize_text(self):
        """Test normalize_text function."""
        assert normalize_text("Hello World") == "hello world"
        assert normalize_text("  MATH  ") == "math"
        assert normalize_text("") == ""


class TestSkillFit:
    """Test cases for skill_fit function."""
    
    def test_skill_fit_with_matching_skills(self):
        """Test skill_fit when child has matching skills."""
        activity = Activity(
            id="test_001",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["addition", "subtraction"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_001",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.8, "subtraction": 0.7}
        )
        
        score = skill_fit(activity, child)
        assert score == 0.75  # (0.8 + 0.7) / 2
    
    def test_skill_fit_with_missing_skills(self):
        """Test skill_fit when child is missing some skills."""
        activity = Activity(
            id="test_002",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["addition", "multiplication"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_002",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.8}  # Missing multiplication
        )
        
        score = skill_fit(activity, child)
        assert score == 0.65  # (0.8 + 0.5) / 2


class TestInterestFit:
    """Test cases for interest_fit function."""
    
    def test_interest_fit_type_match(self):
        """Test interest_fit when activity type matches child interest."""
        activity = Activity(
            id="test_003",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["addition"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_003",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.8},
            interests=["math", "science"]
        )
        
        score = interest_fit(activity, child)
        assert score == 1.0
    
    def test_interest_fit_tag_match(self):
        """Test interest_fit when activity tags match child interest."""
        activity = Activity(
            id="test_004",
            type="reading",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["comprehension"],
            tags=["puzzles", "logic"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_004",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"comprehension": 0.8},
            interests=["puzzles", "games"]
        )
        
        score = interest_fit(activity, child)
        assert score == 1.0
    
    def test_interest_fit_no_match(self):
        """Test interest_fit when no matches found."""
        activity = Activity(
            id="test_005",
            type="vocab",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["vocabulary"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_005",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"vocabulary": 0.8},
            interests=["math", "science"]
        )
        
        score = interest_fit(activity, child)
        assert score == 0.4


class TestStyleFit:
    """Test cases for style_fit function."""
    
    def test_style_fit_visual(self):
        """Test style_fit for visual learners."""
        activity = Activity(
            id="test_006",
            type="reading",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["comprehension"],
            tags=["visual", "picture"],
            estimated_min=10,
            format="freeform",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_006",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"comprehension": 0.8}
        )
        
        score = style_fit(activity, child)
        assert score == 1.0
    
    def test_style_fit_logical(self):
        """Test style_fit for logical learners."""
        activity = Activity(
            id="test_007",
            type="logic",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["reasoning"],
            tags=["puzzles"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_007",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="logical",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"reasoning": 0.8}
        )
        
        score = style_fit(activity, child)
        assert score == 1.0


class TestLevelFit:
    """Test cases for level_fit function."""
    
    def test_level_fit_easy_aligned(self):
        """Test level_fit for easy level with aligned skills."""
        activity = Activity(
            id="test_008",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["addition"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_008",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.5}  # < 0.6, so aligned with easy
        )
        
        score = level_fit(activity, child)
        assert score == 1.0
    
    def test_level_fit_medium_adjacent(self):
        """Test level_fit for medium level with adjacent skills."""
        activity = Activity(
            id="test_009",
            type="math",
            title="Test Activity",
            description="Test",
            level="medium",
            skills=["addition"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_009",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.5}  # < 0.6, so adjacent to medium
        )
        
        score = level_fit(activity, child)
        assert score == 0.7


class TestTimeFit:
    """Test cases for time_fit function."""
    
    def test_time_fit_within_attention_span(self):
        """Test time_fit when activity fits within attention span."""
        activity = Activity(
            id="test_010",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["addition"],
            estimated_min=15,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_010",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.8}
        )
        
        score = time_fit(activity, child)
        assert score == 1.0
    
    def test_time_fit_exceeds_attention_span(self):
        """Test time_fit when activity exceeds attention span."""
        activity = Activity(
            id="test_011",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["addition"],
            estimated_min=30,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_011",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.8}
        )
        
        score = time_fit(activity, child)
        # ratio = 20/30 = 0.67, score = 0.5 + (0.5 * 0.67) = 0.833...
        assert abs(score - 0.833) < 0.01


class TestRecencyPenalty:
    """Test cases for recency_penalty function."""
    
    def test_recency_penalty_recent_activity(self):
        """Test recency_penalty when activity is recent."""
        history = ["activity_001", "activity_002", "activity_003"]
        penalty = recency_penalty("activity_002", history, recent_k=2)
        assert penalty == 1.0
    
    def test_recency_penalty_not_recent(self):
        """Test recency_penalty when activity is not recent."""
        history = ["activity_001", "activity_002", "activity_003"]
        penalty = recency_penalty("activity_003", history, recent_k=2)
        assert penalty == 0.0
    
    def test_recency_penalty_empty_history(self):
        """Test recency_penalty with empty history."""
        penalty = recency_penalty("activity_001", [], recent_k=2)
        assert penalty == 0.0


class TestTotalScore:
    """Test cases for total_score function."""
    
    def test_total_score_calculation(self):
        """Test total_score calculation."""
        activity = Activity(
            id="test_012",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["addition"],
            estimated_min=15,
            format="qna",
            rubric={}
        )
        
        child = ChildProfile(
            id="child_012",
            name="Test Child",
            age=8,
            grade=3,
            learning_style="logical",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"addition": 0.8},
            interests=["math"]
        )
        
        history = ["other_activity"]
        
        score = total_score(activity, child, history)
        
        # Verify score is calculated and is reasonable
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_weights_export(self):
        """Test that WEIGHTS are exported and have correct values."""
        assert isinstance(WEIGHTS, dict)
        assert "skill_fit" in WEIGHTS
        assert "interest_fit" in WEIGHTS
        assert "style_fit" in WEIGHTS
        assert "level_fit" in WEIGHTS
        assert "time_fit" in WEIGHTS
        assert "recency_penalty" in WEIGHTS
        
        # Verify weights sum to 0.95 (excluding recency_penalty which is subtracted)
        positive_weights = sum(WEIGHTS[k] for k in WEIGHTS if k != "recency_penalty")
        assert abs(positive_weights - 0.95) < 0.001
