"""
Simulation utilities for AI Buddy.

This module provides functions to simulate child responses for testing purposes.
"""

from __future__ import annotations
import random
from typing import Union
from .data_models import Activity, ChildProfile


def answer(child: ChildProfile, activity: Activity) -> str:
    """
    Returns a deterministic pseudo-random answer depending on child skill level and activity type.
    
    Args:
        child: The child profile
        activity: The activity being answered
        
    Returns:
        Simulated answer (string, float, or int)
    """
    # Seed random generator using child.id + activity.id for repeatability
    seed_value = hash(child.id + activity.id) % (2**32)
    random.seed(seed_value)
    
    if activity.format == "qna":
        # Calculate mean skill for activity skills
        mean_skill = 0.5  # default
        if activity.skills:
            skill_values = [child.baseline_skills.get(skill, 0.5) for skill in activity.skills]
            mean_skill = sum(skill_values) / len(skill_values)
        
        # Determine success probability based on skill level
        if mean_skill > 0.7:
            success_chance = 0.8  # 80% chance for high skill
        else:
            success_chance = 0.4  # 40% chance for lower skill
        
        # Generate answer based on success probability
        if random.random() < success_chance:
            # Return correct answer
            if activity.rubric.get("answers"):
                # Pick from available answers if they exist
                available_answers = [ans for ans in activity.rubric["answers"] if isinstance(ans, str)]
                if available_answers:
                    return random.choice(available_answers)
            
            # Fallback correct answers based on activity type
            fallbacks = {
                "math": "42",
                "spelling": "correct",
                "vocab": "definition",
                "logic": "true",
                "reading": "comprehension",
                "storytelling": "narrative",
                "creativity": "creative"
            }
            return fallbacks.get(activity.type, "answer")
        else:
            # Return incorrect answer
            return "wrong answer"
    
    else:  # freeform
        # Calculate base sentence count based on attention span and mean skill
        base_sentences = max(2, child.attention_span_min // 10)  # 1 sentence per 10 minutes
        
        # Adjust based on mean skill
        mean_skill = 0.5
        if activity.skills:
            skill_values = [child.baseline_skills.get(skill, 0.5) for skill in activity.skills]
            mean_skill = sum(skill_values) / len(skill_values)
        
        # Add skill bonus (0-3 extra sentences)
        skill_bonus = int(mean_skill * 3)
        total_sentences = base_sentences + skill_bonus
        
        # Ensure minimum sentences if specified in rubric
        if activity.rubric.get("min_sentences"):
            total_sentences = max(total_sentences, activity.rubric["min_sentences"])
        
        # Generate sentences
        sentences = []
        for i in range(total_sentences):
            if activity.type == "storytelling":
                sentences.append(f"This is sentence {i+1} of my story.")
            elif activity.type == "reading":
                sentences.append(f"I read and understood sentence {i+1}.")
            else:
                sentences.append(f"This is my response sentence {i+1}.")
        
        # Occasionally include activity skills as keywords
        if activity.skills and random.random() < 0.7:
            skill_keyword = random.choice(activity.skills)
            sentences.append(f"I think about {skill_keyword}.")
        
        # Occasionally include rubric keywords if available
        if activity.rubric.get("keywords") and random.random() < 0.5:
            keyword = random.choice(activity.rubric["keywords"])
            sentences.append(f"I mention {keyword} in my response.")
        
        return " ".join(sentences)


# Export the function
__all__ = ["answer"]
