"""
Data models for AI Buddy using Pydantic.

This module contains Pydantic models for data validation and serialization.
"""

from typing import Optional, List, Dict, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict


class BaseDataModel(BaseModel):
    """Base model for all data structures in AI Buddy."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )


class Activity(BaseDataModel):
    """
    Model for educational activities.
    
    Represents an educational activity with metadata, difficulty level,
    and assessment criteria.
    """
    id: str = Field(..., description="Unique identifier for the activity")
    type: Literal["math", "spelling", "storytelling", "reading", "vocab", "logic", "creativity"] = Field(
        ..., description="Type of educational activity"
    )
    title: str = Field(..., description="Title of the activity")
    description: str = Field(..., description="Detailed description of the activity")
    level: Literal["easy", "medium", "hard"] = Field(..., description="Difficulty level")
    skills: List[str] = Field(..., description="Skills targeted by this activity")
    tags: List[str] = Field(default_factory=list, description="Additional tags for categorization")
    estimated_min: int = Field(..., description="Estimated time to complete in minutes")
    format: Literal["qna", "freeform"] = Field(..., description="Activity format")
    rubric: Dict[str, Any] = Field(..., description="Assessment rubric for the activity")
    
    @field_validator('estimated_min')
    @classmethod
    def validate_estimated_min(cls, v):
        """Validate that estimated time is positive."""
        if v <= 0:
            raise ValueError("Estimated time must be greater than 0 minutes")
        return v
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v):
        """Validate that skills list is not empty."""
        if not v:
            raise ValueError("Skills list cannot be empty - at least one skill must be specified")
        return v


class ChildProfile(BaseDataModel):
    """
    Model for child learner profiles.
    
    Represents a child's learning profile including demographics,
    preferences, and baseline assessment data.
    """
    id: str = Field(..., description="Unique identifier for the child")
    name: str = Field(..., description="Child's name")
    age: Union[int, str] = Field(..., description="Child's age (number or 'K' for kindergarten)")
    grade: Union[int, str] = Field(..., description="Child's grade level (number or 'K' for kindergarten)")
    interests: List[str] = Field(default_factory=list, description="Child's interests and hobbies")
    learning_style: Literal["visual", "auditory", "logical", "kinesthetic"] = Field(
        ..., description="Preferred learning style"
    )
    attention_span_min: int = Field(..., description="Typical attention span in minutes")
    reading_level: Literal["pre_reader", "emergent", "approaching", "on_grade", "above_grade"] = Field(
        ..., description="Current reading level"
    )
    baseline_skills: Dict[str, float] = Field(..., description="Baseline skill assessments (0.0-1.0 scale)")
    goals: List[str] = Field(default_factory=list, description="Learning goals and objectives")
    
    @field_validator('attention_span_min')
    @classmethod
    def validate_attention_span(cls, v):
        """Validate that attention span is positive."""
        if v <= 0:
            raise ValueError("Attention span must be greater than 0 minutes")
        return v
    
    @field_validator('baseline_skills')
    @classmethod
    def validate_baseline_skills(cls, v):
        """Validate that baseline skill values are between 0 and 1 inclusive."""
        for skill_name, skill_value in v.items():
            if not isinstance(skill_value, (int, float)):
                raise ValueError(f"Skill value for '{skill_name}' must be a number")
            if skill_value < 0.0 or skill_value > 1.0:
                raise ValueError(
                    f"Skill value for '{skill_name}' must be between 0.0 and 1.0 inclusive, "
                    f"got {skill_value}"
                )
        return v


# Export the main models
__all__ = ["Activity", "ChildProfile"]
