"""
Activity evaluation system for AI Buddy.

This module provides functions to evaluate child responses to educational activities,
supporting both Q&A and freeform text formats.
"""

from __future__ import annotations
from typing import Literal, Any, Union
from .data_models import Activity, ChildProfile


def normalize_text(text: str) -> str:
    """
    Normalize text for case-insensitive comparison.
    
    Args:
        text: Input string
        
    Returns:
        Lowercase string with whitespace stripped
    """
    return text.lower().strip()


def eval_qna(answer: Union[str, float, int], activity: Activity) -> dict[str, Any]:
    """
    Evaluate a Q&A activity response.
    
    Args:
        answer: Child's answer (string, float, or int)
        activity: The activity being evaluated
        
    Returns:
        Dictionary with evaluation results:
        {
            "kind": "qna",
            "correct": bool,
            "score": float,  # 0..1
            "reason": str
        }
    """
    rubric = activity.rubric
    
    # Get acceptable answers
    acceptable_answers = rubric.get("answers", [])
    if not acceptable_answers:
        return {
            "kind": "qna",
            "correct": False,
            "score": 0.0,
            "reason": "No acceptable answers defined in rubric"
        }
    
    # Get numeric tolerance for numeric answers
    numeric_tolerance = rubric.get("numeric_tolerance", 0.0)
    
    # Check if answer is correct
    correct = False
    reason = ""
    
    for acceptable in acceptable_answers:
        # Handle numeric comparison
        if isinstance(acceptable, (int, float)) and isinstance(answer, (int, float)):
            if abs(answer - acceptable) <= numeric_tolerance:
                correct = True
                reason = f"Answer {answer} matches acceptable answer {acceptable} within tolerance {numeric_tolerance}"
                break
        
        # Handle string comparison
        elif isinstance(acceptable, str) and isinstance(answer, str):
            normalized_answer = normalize_text(answer)
            normalized_acceptable = normalize_text(acceptable)
            if normalized_answer == normalized_acceptable:
                correct = True
                reason = f"Answer '{answer}' matches acceptable answer '{acceptable}'"
                break
    
    if not correct:
        reason = f"Answer '{answer}' does not match any acceptable answers: {acceptable_answers}"
    
    # Calculate score
    score = 1.0 if correct else 0.0
    
    return {
        "kind": "qna",
        "correct": correct,
        "score": score,
        "reason": reason
    }


def eval_freeform(text: str, activity: Activity) -> dict[str, Any]:
    """
    Evaluate a freeform text activity response.
    
    Args:
        text: Child's text response
        activity: The activity being evaluated
        
    Returns:
        Dictionary with evaluation results:
        {
            "kind": "freeform",
            "meets_min_length": bool,
            "keyword_hits": int,
            "score": float,  # 0..1
            "reason": str
        }
    """
    rubric = activity.rubric
    
    # Get minimum sentences requirement
    min_sentences = rubric.get("min_sentences", 3)
    
    # Count sentences (split by periods, remove empty segments)
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    sentence_count = len(sentences)
    meets_min_length = sentence_count >= min_sentences
    
    # Check for keywords
    keywords = rubric.get("keywords", [])
    keyword_hits = 0
    
    if keywords:
        normalized_text = normalize_text(text)
        for keyword in keywords:
            normalized_keyword = normalize_text(keyword)
            if normalized_keyword in normalized_text:
                keyword_hits += 1
    
    # Calculate score
    base_score = 0.6 if meets_min_length else 0.3
    keyword_bonus = min(keyword_hits * 0.1, 0.4)  # Cap at +0.4
    score = min(base_score + keyword_bonus, 1.0)  # Clamp to [0,1]
    
    # Generate reason
    reason_parts = []
    if meets_min_length:
        reason_parts.append(f"Meets minimum length requirement ({sentence_count} sentences >= {min_sentences})")
    else:
        reason_parts.append(f"Below minimum length requirement ({sentence_count} sentences < {min_sentences})")
    
    if keywords:
        reason_parts.append(f"Contains {keyword_hits}/{len(keywords)} keywords")
    
    reason = ". ".join(reason_parts)
    
    return {
        "kind": "freeform",
        "meets_min_length": meets_min_length,
        "keyword_hits": keyword_hits,
        "score": score,
        "reason": reason
    }


def choose_outcome_from_eval(result: dict[str, Any]) -> Literal["success", "partial", "struggle"]:
    """
    Choose an outcome based on evaluation results.
    
    Args:
        result: Evaluation result from eval_qna or eval_freeform
        
    Returns:
        Outcome: "success", "partial", or "struggle"
    """
    kind = result.get("kind")
    score = result.get("score", 0.0)
    
    if kind == "qna":
        if score >= 1.0:
            return "success"
        else:
            return "struggle"
    
    elif kind == "freeform":
        if score >= 0.8:
            return "success"
        elif score >= 0.5:
            return "partial"
        else:
            return "struggle"
    
    else:
        # Default fallback
        if score >= 0.8:
            return "success"
        elif score >= 0.5:
            return "partial"
        else:
            return "struggle"


# Export the functions
__all__ = [
    "eval_qna",
    "eval_freeform", 
    "choose_outcome_from_eval",
    "normalize_text"
]
