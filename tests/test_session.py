"""
Tests for the session module.

This module contains tests for the session management functions.
"""

import pytest
from datetime import datetime, timedelta

from ai_buddy.session import (
    ActivityAttempt,
    SessionLog,
    recent_activity_ids,
    append_attempt
)


class TestActivityAttempt:
    """Test cases for ActivityAttempt model."""
    
    def test_valid_activity_attempt(self):
        """Test creating a valid ActivityAttempt instance."""
        timestamp = datetime.now()
        attempt = ActivityAttempt(
            activity_id="math_001",
            timestamp=timestamp,
            outcome="success",
            details={"score": 95, "time_taken": 120}
        )
        
        assert attempt.activity_id == "math_001"
        assert attempt.timestamp == timestamp
        assert attempt.outcome == "success"
        assert attempt.details == {"score": 95, "time_taken": 120}
    
    def test_activity_attempt_default_details(self):
        """Test ActivityAttempt with default empty details."""
        timestamp = datetime.now()
        attempt = ActivityAttempt(
            activity_id="reading_001",
            timestamp=timestamp,
            outcome="partial"
        )
        
        assert attempt.details == {}
    
    def test_invalid_outcome(self):
        """Test that invalid outcome raises ValidationError."""
        timestamp = datetime.now()
        
        with pytest.raises(ValueError):
            ActivityAttempt(
                activity_id="test_001",
                timestamp=timestamp,
                outcome="invalid_outcome"  # Invalid outcome
            )


class TestSessionLog:
    """Test cases for SessionLog model."""
    
    def test_valid_session_log(self):
        """Test creating a valid SessionLog instance."""
        timestamp = datetime.now()
        attempt = ActivityAttempt(
            activity_id="math_001",
            timestamp=timestamp,
            outcome="success"
        )
        
        session = SessionLog(
            child_id="child_001",
            attempts=[attempt]
        )
        
        assert session.child_id == "child_001"
        assert len(session.attempts) == 1
        assert session.attempts[0].activity_id == "math_001"
    
    def test_session_log_empty_attempts(self):
        """Test SessionLog with default empty attempts list."""
        session = SessionLog(child_id="child_002")
        
        assert session.attempts == []


class TestRecentActivityIds:
    """Test cases for recent_activity_ids function."""
    
    def test_recent_activity_ids_single_session(self):
        """Test recent_activity_ids with a single session."""
        timestamp1 = datetime.now()
        timestamp2 = timestamp1 + timedelta(minutes=5)
        timestamp3 = timestamp2 + timedelta(minutes=5)
        
        session = SessionLog(
            child_id="child_001",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_001",
                    timestamp=timestamp1,
                    outcome="success"
                ),
                ActivityAttempt(
                    activity_id="activity_002",
                    timestamp=timestamp2,
                    outcome="partial"
                ),
                ActivityAttempt(
                    activity_id="activity_003",
                    timestamp=timestamp3,
                    outcome="struggle"
                )
            ]
        )
        
        history = [session]
        
        # Get 2 most recent
        recent_ids = recent_activity_ids(history, 2)
        assert recent_ids == ["activity_003", "activity_002"]
        
        # Get all 3
        recent_ids = recent_activity_ids(history, 3)
        assert recent_ids == ["activity_003", "activity_002", "activity_001"]
    
    def test_recent_activity_ids_multiple_sessions(self):
        """Test recent_activity_ids across multiple sessions."""
        base_time = datetime.now()
        
        session1 = SessionLog(
            child_id="child_001",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_001",
                    timestamp=base_time,
                    outcome="success"
                ),
                ActivityAttempt(
                    activity_id="activity_002",
                    timestamp=base_time + timedelta(minutes=5),
                    outcome="partial"
                )
            ]
        )
        
        session2 = SessionLog(
            child_id="child_002",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_003",
                    timestamp=base_time + timedelta(minutes=10),
                    outcome="success"
                ),
                ActivityAttempt(
                    activity_id="activity_004",
                    timestamp=base_time + timedelta(minutes=15),
                    outcome="struggle"
                )
            ]
        )
        
        history = [session1, session2]
        
        # Get 3 most recent across all sessions
        recent_ids = recent_activity_ids(history, 3)
        assert recent_ids == ["activity_004", "activity_003", "activity_002"]
    
    def test_recent_activity_ids_empty_history(self):
        """Test recent_activity_ids with empty history."""
        recent_ids = recent_activity_ids([], 5)
        assert recent_ids == []
    
    def test_recent_activity_ids_k_zero(self):
        """Test recent_activity_ids with k=0."""
        session = SessionLog(
            child_id="child_001",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_001",
                    timestamp=datetime.now(),
                    outcome="success"
                )
            ]
        )
        
        recent_ids = recent_activity_ids([session], 0)
        assert recent_ids == []
    
    def test_recent_activity_ids_k_larger_than_attempts(self):
        """Test recent_activity_ids when k is larger than available attempts."""
        session = SessionLog(
            child_id="child_001",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_001",
                    timestamp=datetime.now(),
                    outcome="success"
                )
            ]
        )
        
        recent_ids = recent_activity_ids([session], 5)
        assert recent_ids == ["activity_001"]


class TestAppendAttempt:
    """Test cases for append_attempt function."""
    
    def test_append_attempt_new_child(self):
        """Test append_attempt for a new child (creates new session)."""
        history = []
        timestamp = datetime.now()
        attempt = ActivityAttempt(
            activity_id="math_001",
            timestamp=timestamp,
            outcome="success"
        )
        
        updated_history = append_attempt(history, "child_001", attempt)
        
        assert len(updated_history) == 1
        assert updated_history[0].child_id == "child_001"
        assert len(updated_history[0].attempts) == 1
        assert updated_history[0].attempts[0].activity_id == "math_001"
    
    def test_append_attempt_existing_child(self):
        """Test append_attempt for existing child (adds to existing session)."""
        timestamp1 = datetime.now()
        timestamp2 = timestamp1 + timedelta(minutes=5)
        
        # Create initial session
        initial_session = SessionLog(
            child_id="child_001",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_001",
                    timestamp=timestamp1,
                    outcome="success"
                )
            ]
        )
        history = [initial_session]
        
        # Append new attempt
        new_attempt = ActivityAttempt(
            activity_id="activity_002",
            timestamp=timestamp2,
            outcome="partial"
        )
        
        updated_history = append_attempt(history, "child_001", new_attempt)
        
        assert len(updated_history) == 1
        assert len(updated_history[0].attempts) == 2
        assert updated_history[0].attempts[0].activity_id == "activity_001"
        assert updated_history[0].attempts[1].activity_id == "activity_002"
    
    def test_append_attempt_multiple_children(self):
        """Test append_attempt with multiple children in history."""
        timestamp = datetime.now()
        
        # Create history with two children
        session1 = SessionLog(
            child_id="child_001",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_001",
                    timestamp=timestamp,
                    outcome="success"
                )
            ]
        )
        session2 = SessionLog(
            child_id="child_002",
            attempts=[
                ActivityAttempt(
                    activity_id="activity_002",
                    timestamp=timestamp + timedelta(minutes=5),
                    outcome="partial"
                )
            ]
        )
        history = [session1, session2]
        
        # Append attempt for child_001
        new_attempt = ActivityAttempt(
            activity_id="activity_003",
            timestamp=timestamp + timedelta(minutes=10),
            outcome="struggle"
        )
        
        updated_history = append_attempt(history, "child_001", new_attempt)
        
        assert len(updated_history) == 2
        
        # Find child_001's session
        child_001_session = None
        for session in updated_history:
            if session.child_id == "child_001":
                child_001_session = session
                break
        
        assert child_001_session is not None
        assert len(child_001_session.attempts) == 2
        assert child_001_session.attempts[1].activity_id == "activity_003"
    
    def test_append_attempt_immutability(self):
        """Test that append_attempt doesn't modify the original history."""
        history = []
        timestamp = datetime.now()
        attempt = ActivityAttempt(
            activity_id="math_001",
            timestamp=timestamp,
            outcome="success"
        )
        
        updated_history = append_attempt(history, "child_001", attempt)
        
        # Original history should remain unchanged
        assert len(history) == 0
        
        # Updated history should have the new session
        assert len(updated_history) == 1
