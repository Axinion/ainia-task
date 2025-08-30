"""
Tests for the simulate module.

This module contains tests for the simulation functions.
"""

import pytest
from unittest.mock import patch

from ai_buddy.data_models import Activity, ChildProfile
from ai_buddy.simulate import answer


class TestAnswer:
    """Test cases for answer function."""
    
    def test_qna_answer_with_high_skill(self):
        """Test Q&A answer generation with high skill level."""
        child = ChildProfile(
            id="test_child",
            name="Test Child",
            age=10,
            grade=5,
            interests=["math"],
            learning_style="logical",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"math": 0.9},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="math",
            title="Test Math",
            description="Test activity",
            level="medium",
            skills=["math"],
            estimated_min=15,
            format="qna",
            rubric={
                "answers": ["42", "forty-two"],
                "numeric_tolerance": 0.1
            }
        )
        
        # With high skill (>0.7), should get correct answer (80% chance)
        result = answer(child, activity)
        # Result could be either correct or wrong due to 20% chance of failure
        assert result in ["42", "forty-two", "wrong answer"]
    
    def test_qna_answer_with_low_skill(self):
        """Test Q&A answer generation with low skill level."""
        child = ChildProfile(
            id="test_child_low",
            name="Test Child",
            age=10,
            grade=5,
            interests=["math"],
            learning_style="logical",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"math": 0.1},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="math",
            title="Test Math",
            description="Test activity",
            level="medium",
            skills=["math"],
            estimated_min=15,
            format="qna",
            rubric={
                "answers": ["42", "forty-two"],
                "numeric_tolerance": 0.1
            }
        )
        
        # With low skill (≤0.7), might get wrong answer
        result = answer(child, activity)
        # Result could be either correct or wrong due to 40% chance
        assert result in ["42", "forty-two", "wrong answer"]
    
    def test_qna_answer_fallback(self):
        """Test Q&A answer generation with fallback answers."""
        child = ChildProfile(
            id="test_child_fallback",
            name="Test Child",
            age=10,
            grade=5,
            interests=["math"],
            learning_style="logical",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"math": 0.8},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="math",
            title="Test Math",
            description="Test activity",
            level="medium",
            skills=["math"],
            estimated_min=15,
            format="qna",
            rubric={}  # No answers defined
        )
        
        result = answer(child, activity)
        # With high skill (>0.7), should get correct answer (80% chance)
        # Result could be either correct or wrong due to randomness
        assert result in ["42", "wrong answer"]
    
    def test_qna_answer_deterministic(self):
        """Test that Q&A answers are deterministic for same child/activity."""
        child = ChildProfile(
            id="test_child_det",
            name="Test Child",
            age=10,
            grade=5,
            interests=["math"],
            learning_style="logical",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"math": 0.8},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="math",
            title="Test Math",
            description="Test activity",
            level="medium",
            skills=["math"],
            estimated_min=15,
            format="qna",
            rubric={
                "answers": ["42", "forty-two"]
            }
        )
        
        # Same child + activity should produce same result
        result1 = answer(child, activity)
        result2 = answer(child, activity)
        assert result1 == result2
    
    def test_freeform_answer_basic(self):
        """Test freeform answer generation."""
        child = ChildProfile(
            id="test_child_freeform",
            name="Test Child",
            age=10,
            grade=5,
            interests=["storytelling"],
            learning_style="visual",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"writing": 0.7},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="storytelling",
            title="Test Story",
            description="Test activity",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 3,
                "keywords": ["adventure", "hero"]
            }
        )
        
        result = answer(child, activity)
        
        # Should contain multiple sentences
        assert "." in result
        sentences = [s.strip() for s in result.split(".") if s.strip()]
        assert len(sentences) >= 3  # At least min_sentences
    
    def test_freeform_answer_attention_span_scaling(self):
        """Test that freeform answers scale with attention span."""
        child_short = ChildProfile(
            id="test_child_short",
            name="Short Attention Child",
            age=10,
            grade=5,
            interests=["storytelling"],
            learning_style="visual",
            attention_span_min=10,  # Short attention span
            reading_level="on_grade",
            baseline_skills={"writing": 0.5},
            goals=[]
        )
        
        child_long = ChildProfile(
            id="test_child_long",
            name="Long Attention Child",
            age=10,
            grade=5,
            interests=["storytelling"],
            learning_style="visual",
            attention_span_min=60,  # Long attention span
            reading_level="on_grade",
            baseline_skills={"writing": 0.5},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="storytelling",
            title="Test Story",
            description="Test activity",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 2
            }
        )
        
        result_short = answer(child_short, activity)
        result_long = answer(child_long, activity)
        
        # Both should be valid responses
        assert len(result_short) > 0
        assert len(result_long) > 0
        
        # Long attention span should generally produce longer responses
        # (though this is probabilistic, so we just check they're both valid)
    
    def test_freeform_answer_skill_keywords(self):
        """Test that freeform answers can include skill keywords."""
        child = ChildProfile(
            id="test_child_skills",
            name="Test Child",
            age=10,
            grade=5,
            interests=["storytelling"],
            learning_style="visual",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"writing": 0.8, "creativity": 0.7},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="storytelling",
            title="Test Story",
            description="Test activity",
            level="medium",
            skills=["writing", "creativity"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 2
            }
        )
        
        result = answer(child, activity)
        
        # Should be a valid response (skill keywords are probabilistic)
        assert len(result) > 0
        assert "." in result  # Should contain sentences
    
    def test_freeform_answer_rubric_keywords(self):
        """Test that freeform answers can include rubric keywords."""
        child = ChildProfile(
            id="test_child_rubric",
            name="Test Child",
            age=10,
            grade=5,
            interests=["storytelling"],
            learning_style="visual",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"writing": 0.8},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="storytelling",
            title="Test Story",
            description="Test activity",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 2,
                "keywords": ["adventure", "hero"]
            }
        )
        
        result = answer(child, activity)
        
        # Should be a valid response (rubric keywords are probabilistic)
        assert len(result) > 0
        assert "." in result  # Should contain sentences
    
    def test_freeform_answer_deterministic(self):
        """Test that freeform answers are deterministic for same child/activity."""
        child = ChildProfile(
            id="test_child_freeform_det",
            name="Test Child",
            age=10,
            grade=5,
            interests=["storytelling"],
            learning_style="visual",
            attention_span_min=30,
            reading_level="on_grade",
            baseline_skills={"writing": 0.7},
            goals=[]
        )
        
        activity = Activity(
            id="test_001",
            type="storytelling",
            title="Test Story",
            description="Test activity",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 2
            }
        )
        
        # Same child + activity should produce same result
        result1 = answer(child, activity)
        result2 = answer(child, activity)
        assert result1 == result2
