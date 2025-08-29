"""
Session management for activity attempts and learning history.

This module provides data models and functions for tracking child activity
attempts and managing session logs.
"""

from datetime import datetime
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class ActivityAttempt(BaseModel):
    """
    Model for tracking a single activity attempt by a child.
    
    Represents the outcome of a child's attempt at an educational activity
    with timestamp and optional details.
    """
    activity_id: str = Field(..., description="ID of the activity that was attempted")
    timestamp: datetime = Field(..., description="When the attempt occurred")
    outcome: Literal["success", "partial", "struggle", "skipped"] = Field(
        ..., description="Result of the activity attempt"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Additional details about the attempt"
    )

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )


class SessionLog(BaseModel):
    """
    Model for tracking a child's learning session.
    
    Contains a list of activity attempts made by a child during a session.
    """
    child_id: str = Field(..., description="ID of the child who participated in the session")
    attempts: List[ActivityAttempt] = Field(
        default_factory=list,
        description="List of activity attempts in this session"
    )

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )


def recent_activity_ids(history: List[SessionLog], k: int) -> List[str]:
    """
    Return activity_ids from most recent k attempts across sessions.
    
    Flattens all attempts from all sessions, sorts by timestamp (newest first),
    and returns the activity_ids from the most recent k attempts.
    
    Args:
        history: List of session logs containing activity attempts
        k: Number of most recent activity IDs to return
        
    Returns:
        List of activity IDs from most recent k attempts (newest first)
    """
    if k <= 0:
        return []
    
    # Flatten all attempts from all sessions
    all_attempts = []
    for session in history:
        all_attempts.extend(session.attempts)
    
    # Sort by timestamp (newest first)
    sorted_attempts = sorted(all_attempts, key=lambda x: x.timestamp, reverse=True)
    
    # Extract activity_ids from the most recent k attempts
    recent_ids = [attempt.activity_id for attempt in sorted_attempts[:k]]
    
    return recent_ids


def append_attempt(history: List[SessionLog], child_id: str, attempt: ActivityAttempt) -> List[SessionLog]:
    """
    Append an attempt to the latest session for a child, or create a new session.
    
    If a session exists for the child, append the attempt to it.
    If no session exists, create a new SessionLog for the child.
    
    Args:
        history: Current list of session logs
        child_id: ID of the child making the attempt
        attempt: ActivityAttempt to append
        
    Returns:
        Updated list of session logs with the new attempt added
    """
    # Create a copy of the history to avoid modifying the original
    updated_history = history.copy()
    
    # Find the latest session for this child
    latest_session = None
    for session in updated_history:
        if session.child_id == child_id:
            latest_session = session
            break
    
    if latest_session is not None:
        # Append to existing session
        latest_session.attempts.append(attempt)
    else:
        # Create new session for this child
        new_session = SessionLog(
            child_id=child_id,
            attempts=[attempt]
        )
        updated_history.append(new_session)
    
    return updated_history


# Export the models and functions
__all__ = [
    "ActivityAttempt",
    "SessionLog", 
    "recent_activity_ids",
    "append_attempt"
]
