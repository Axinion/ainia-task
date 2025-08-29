"""
Tests for the evaluate module.

This module contains tests for the activity evaluation functions.
"""

import pytest

from ai_buddy.data_models import Activity
from ai_buddy.evaluate import (
    eval_qna,
    eval_freeform,
    choose_outcome_from_eval,
    normalize_text
)


class TestNormalizeText:
    """Test cases for normalize_text function."""
    
    def test_normalize_text(self):
        """Test text normalization."""
        assert normalize_text("Hello World") == "hello world"
        assert normalize_text("  MATH  ") == "math"
        assert normalize_text("") == ""


class TestEvalQna:
    """Test cases for eval_qna function."""
    
    def test_qna_correct_string_answer(self):
        """Test Q&A evaluation with correct string answer."""
        activity = Activity(
            id="test_001",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["math"],
            estimated_min=10,
            format="qna",
            rubric={
                "answers": ["42", "forty-two", "42.0"],
                "numeric_tolerance": 0.1
            }
        )
        
        result = eval_qna("42", activity)
        
        assert result["kind"] == "qna"
        assert result["correct"] is True
        assert result["score"] == 1.0
        assert "matches acceptable answer" in result["reason"]
    
    def test_qna_incorrect_string_answer(self):
        """Test Q&A evaluation with incorrect string answer."""
        activity = Activity(
            id="test_002",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["math"],
            estimated_min=10,
            format="qna",
            rubric={
                "answers": ["42", "forty-two"],
                "numeric_tolerance": 0.1
            }
        )
        
        result = eval_qna("43", activity)
        
        assert result["kind"] == "qna"
        assert result["correct"] is False
        assert result["score"] == 0.0
        assert "does not match" in result["reason"]
    
    def test_qna_numeric_answer_with_tolerance(self):
        """Test Q&A evaluation with numeric answer and tolerance."""
        activity = Activity(
            id="test_003",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["math"],
            estimated_min=10,
            format="qna",
            rubric={
                "answers": [42.0, 42],
                "numeric_tolerance": 0.5
            }
        )
        
        # Test within tolerance
        result = eval_qna(42.3, activity)
        assert result["correct"] is True
        assert result["score"] == 1.0
        
        # Test outside tolerance
        result = eval_qna(43.0, activity)
        assert result["correct"] is False
        assert result["score"] == 0.0
    
    def test_qna_case_insensitive(self):
        """Test Q&A evaluation is case insensitive."""
        activity = Activity(
            id="test_004",
            type="vocab",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["vocabulary"],
            estimated_min=10,
            format="qna",
            rubric={
                "answers": ["Apple", "APPLE", "apple"]
            }
        )
        
        result = eval_qna("APPLE", activity)
        assert result["correct"] is True
        assert result["score"] == 1.0
    
    def test_qna_no_answers_defined(self):
        """Test Q&A evaluation when no answers are defined."""
        activity = Activity(
            id="test_005",
            type="math",
            title="Test Activity",
            description="Test",
            level="easy",
            skills=["math"],
            estimated_min=10,
            format="qna",
            rubric={}
        )
        
        result = eval_qna("42", activity)
        
        assert result["kind"] == "qna"
        assert result["correct"] is False
        assert result["score"] == 0.0
        assert "No acceptable answers defined" in result["reason"]


class TestEvalFreeform:
    """Test cases for eval_freeform function."""
    
    def test_freeform_meets_min_length(self):
        """Test freeform evaluation that meets minimum length."""
        activity = Activity(
            id="test_006",
            type="storytelling",
            title="Test Activity",
            description="Test",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 3,
                "keywords": ["adventure", "hero", "journey"]
            }
        )
        
        text = "This is the first sentence. This is the second sentence. This is the third sentence."
        result = eval_freeform(text, activity)
        
        assert result["kind"] == "freeform"
        assert result["meets_min_length"] is True
        assert result["keyword_hits"] == 0
        assert result["score"] == 0.6  # Base score for meeting length
        assert "Meets minimum length requirement" in result["reason"]
    
    def test_freeform_below_min_length(self):
        """Test freeform evaluation that doesn't meet minimum length."""
        activity = Activity(
            id="test_007",
            type="storytelling",
            title="Test Activity",
            description="Test",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 3,
                "keywords": ["adventure", "hero"]
            }
        )
        
        text = "This is only one sentence."
        result = eval_freeform(text, activity)
        
        assert result["kind"] == "freeform"
        assert result["meets_min_length"] is False
        assert result["keyword_hits"] == 0
        assert result["score"] == 0.3  # Base score for not meeting length
        assert "Below minimum length requirement" in result["reason"]
    
    def test_freeform_with_keywords(self):
        """Test freeform evaluation with keyword matching."""
        activity = Activity(
            id="test_008",
            type="storytelling",
            title="Test Activity",
            description="Test",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 2,
                "keywords": ["adventure", "hero", "journey"]
            }
        )
        
        text = "This is the first sentence. The hero went on an adventure."
        result = eval_freeform(text, activity)
        
        assert result["kind"] == "freeform"
        assert result["meets_min_length"] is True
        assert result["keyword_hits"] == 2  # "hero" and "adventure"
        assert result["score"] == 0.8  # 0.6 base + 0.2 keyword bonus
        assert "Contains 2/3 keywords" in result["reason"]
    
    def test_freeform_keyword_bonus_cap(self):
        """Test that keyword bonus is capped at 0.4."""
        activity = Activity(
            id="test_009",
            type="storytelling",
            title="Test Activity",
            description="Test",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={
                "min_sentences": 2,
                "keywords": ["a", "b", "c", "d", "e", "f"]  # 6 keywords
            }
        )
        
        text = "This is the first sentence. The text contains a, b, c, d, e, f keywords."
        result = eval_freeform(text, activity)
        
        assert result["kind"] == "freeform"
        assert result["meets_min_length"] is True
        assert result["keyword_hits"] == 6
        assert result["score"] == 1.0  # 0.6 base + 0.4 cap = 1.0
        assert "Contains 6/6 keywords" in result["reason"]
    
    def test_freeform_default_min_sentences(self):
        """Test freeform evaluation with default min_sentences."""
        activity = Activity(
            id="test_010",
            type="storytelling",
            title="Test Activity",
            description="Test",
            level="medium",
            skills=["writing"],
            estimated_min=15,
            format="freeform",
            rubric={}  # No min_sentences specified
        )
        
        text = "Sentence one. Sentence two. Sentence three."
        result = eval_freeform(text, activity)
        
        assert result["kind"] == "freeform"
        assert result["meets_min_length"] is True  # Default is 3
        assert result["score"] == 0.6


class TestChooseOutcomeFromEval:
    """Test cases for choose_outcome_from_eval function."""
    
    def test_qna_success_outcome(self):
        """Test outcome selection for successful Q&A."""
        result = {
            "kind": "qna",
            "correct": True,
            "score": 1.0,
            "reason": "Correct answer"
        }
        
        outcome = choose_outcome_from_eval(result)
        assert outcome == "success"
    
    def test_qna_struggle_outcome(self):
        """Test outcome selection for struggling Q&A."""
        result = {
            "kind": "qna",
            "correct": False,
            "score": 0.0,
            "reason": "Incorrect answer"
        }
        
        outcome = choose_outcome_from_eval(result)
        assert outcome == "struggle"
    
    def test_freeform_success_outcome(self):
        """Test outcome selection for successful freeform."""
        result = {
            "kind": "freeform",
            "meets_min_length": True,
            "keyword_hits": 3,
            "score": 0.9,
            "reason": "Good response"
        }
        
        outcome = choose_outcome_from_eval(result)
        assert outcome == "success"
    
    def test_freeform_partial_outcome(self):
        """Test outcome selection for partial freeform."""
        result = {
            "kind": "freeform",
            "meets_min_length": True,
            "keyword_hits": 1,
            "score": 0.7,
            "reason": "Partial response"
        }
        
        outcome = choose_outcome_from_eval(result)
        assert outcome == "partial"
    
    def test_freeform_struggle_outcome(self):
        """Test outcome selection for struggling freeform."""
        result = {
            "kind": "freeform",
            "meets_min_length": False,
            "keyword_hits": 0,
            "score": 0.3,
            "reason": "Poor response"
        }
        
        outcome = choose_outcome_from_eval(result)
        assert outcome == "struggle"
    
    def test_unknown_kind_fallback(self):
        """Test outcome selection for unknown evaluation kind."""
        result = {
            "kind": "unknown",
            "score": 0.9,
            "reason": "Unknown evaluation"
        }
        
        outcome = choose_outcome_from_eval(result)
        assert outcome == "success"  # Should use default fallback
