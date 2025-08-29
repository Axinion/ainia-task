"""
Tests for the persist module.

This module contains tests for the data persistence functions.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from ai_buddy.data_models import ChildProfile
from ai_buddy.session import SessionLog, ActivityAttempt
from ai_buddy.persist import save_history, load_history, save_child_snapshot


class TestSaveHistory:
    """Test cases for save_history function."""
    
    def test_save_history_creates_file(self, tmp_path):
        """Test that save_history creates the file and directory."""
        history_path = tmp_path / "data" / "history.json"
        
        # Create sample history
        attempt = ActivityAttempt(
            activity_id="test_001",
            timestamp=datetime.now(),
            outcome="success",
            details={"score": 0.9}
        )
        session = SessionLog(
            child_id="child_001",
            attempts=[attempt]
        )
        history = [session]
        
        # Save history
        save_history(history, str(history_path))
        
        # Check file exists
        assert history_path.exists()
        
        # Check content
        with open(history_path, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]["child_id"] == "child_001"
        assert len(data[0]["attempts"]) == 1
        assert data[0]["attempts"][0]["activity_id"] == "test_001"
    
    def test_save_history_empty_list(self, tmp_path):
        """Test saving empty history list."""
        history_path = tmp_path / "data" / "history.json"
        
        save_history([], str(history_path))
        
        assert history_path.exists()
        
        with open(history_path, 'r') as f:
            data = json.load(f)
        
        assert data == []
    
    def test_save_history_multiple_sessions(self, tmp_path):
        """Test saving multiple sessions."""
        history_path = tmp_path / "data" / "history.json"
        
        # Create multiple sessions
        sessions = []
        for i in range(3):
            attempt = ActivityAttempt(
                activity_id=f"test_{i:03d}",
                timestamp=datetime.now(),
                outcome="success" if i % 2 == 0 else "partial",
                details={"session": i}
            )
            session = SessionLog(
                child_id=f"child_{i:03d}",
                attempts=[attempt]
            )
            sessions.append(session)
        
        save_history(sessions, str(history_path))
        
        with open(history_path, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 3
        for i, session_data in enumerate(data):
            assert session_data["child_id"] == f"child_{i:03d}"
            assert session_data["attempts"][0]["activity_id"] == f"test_{i:03d}"


class TestLoadHistory:
    """Test cases for load_history function."""
    
    def test_load_history_existing_file(self, tmp_path):
        """Test loading history from existing file."""
        history_path = tmp_path / "data" / "history.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create sample data
        sample_data = [
            {
                "child_id": "child_001",
                "attempts": [
                    {
                        "activity_id": "test_001",
                        "timestamp": "2024-01-01T10:00:00",
                        "outcome": "success",
                        "details": {"score": 0.9}
                    }
                ]
            }
        ]
        
        with open(history_path, 'w') as f:
            json.dump(sample_data, f)
        
        # Load history
        history = load_history(str(history_path))
        
        assert len(history) == 1
        assert history[0].child_id == "child_001"
        assert len(history[0].attempts) == 1
        assert history[0].attempts[0].activity_id == "test_001"
        assert history[0].attempts[0].outcome == "success"
    
    def test_load_history_missing_file(self, tmp_path):
        """Test loading history when file doesn't exist."""
        history_path = tmp_path / "nonexistent" / "history.json"
        
        history = load_history(str(history_path))
        
        assert history == []
    
    def test_load_history_invalid_json(self, tmp_path):
        """Test loading history with invalid JSON."""
        history_path = tmp_path / "data" / "history.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write invalid JSON
        with open(history_path, 'w') as f:
            f.write("invalid json content")
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            load_history(str(history_path))
    
    def test_load_history_invalid_schema(self, tmp_path):
        """Test loading history with invalid schema."""
        history_path = tmp_path / "data" / "history.json"
        history_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write valid JSON but invalid schema
        invalid_data = [{"invalid": "data"}]
        
        with open(history_path, 'w') as f:
            json.dump(invalid_data, f)
        
        with pytest.raises(ValueError, match="Failed to load history"):
            load_history(str(history_path))


class TestSaveChildSnapshot:
    """Test cases for save_child_snapshot function."""
    
    def test_save_child_snapshot_creates_file(self, tmp_path):
        """Test that save_child_snapshot creates the file and directory."""
        snapshot_path = tmp_path / "data" / "snapshots" / "child_001.json"
        
        # Create sample child
        child = ChildProfile(
            id="child_001",
            name="Alice Smith",
            age=8,
            grade=3,
            interests=["reading", "art"],
            learning_style="visual",
            attention_span_min=20,
            reading_level="on_grade",
            baseline_skills={"math": 0.7, "reading": 0.8},
            goals=["improve math skills"]
        )
        
        # Save snapshot
        save_child_snapshot(child, str(snapshot_path))
        
        # Check file exists
        assert snapshot_path.exists()
        
        # Check content
        with open(snapshot_path, 'r') as f:
            data = json.load(f)
        
        assert data["id"] == "child_001"
        assert data["name"] == "Alice Smith"
        assert data["age"] == 8
        assert data["learning_style"] == "visual"
        assert data["baseline_skills"]["math"] == 0.7
    
    def test_save_child_snapshot_complex_child(self, tmp_path):
        """Test saving a child with complex data."""
        snapshot_path = tmp_path / "snapshots" / "complex_child.json"
        
        # Create child with string age/grade
        child = ChildProfile(
            id="child_002",
            name="Bob Johnson",
            age="K",  # String age
            grade="K",  # String grade
            interests=["science", "math", "puzzles"],
            learning_style="logical",
            attention_span_min=30,
            reading_level="emergent",
            baseline_skills={
                "math": 0.9,
                "reading": 0.3,
                "vocabulary": 0.6,
                "logic": 0.8
            },
            goals=["learn to read", "solve harder puzzles"]
        )
        
        save_child_snapshot(child, str(snapshot_path))
        
        with open(snapshot_path, 'r') as f:
            data = json.load(f)
        
        assert data["id"] == "child_002"
        assert data["age"] == "K"
        assert data["grade"] == "K"
        assert data["learning_style"] == "logical"
        assert len(data["baseline_skills"]) == 4
        assert data["baseline_skills"]["math"] == 0.9


class TestPersistenceIntegration:
    """Integration tests for save and load operations."""
    
    def test_save_and_load_history_roundtrip(self, tmp_path):
        """Test that saving and loading history preserves data."""
        history_path = tmp_path / "data" / "history.json"
        
        # Create original history
        original_history = []
        for i in range(2):
            attempts = []
            for j in range(2):
                attempt = ActivityAttempt(
                    activity_id=f"test_{i}_{j}",
                    timestamp=datetime.now(),
                    outcome=["success", "partial", "struggle"][j % 3],
                    details={"session": i, "attempt": j}
                )
                attempts.append(attempt)
            
            session = SessionLog(
                child_id=f"child_{i:03d}",
                attempts=attempts
            )
            original_history.append(session)
        
        # Save and load
        save_history(original_history, str(history_path))
        loaded_history = load_history(str(history_path))
        
        # Compare
        assert len(loaded_history) == len(original_history)
        
        for i, (original, loaded) in enumerate(zip(original_history, loaded_history)):
            assert original.child_id == loaded.child_id
            assert len(original.attempts) == len(loaded.attempts)
            
            for j, (orig_attempt, load_attempt) in enumerate(zip(original.attempts, loaded.attempts)):
                assert orig_attempt.activity_id == load_attempt.activity_id
                assert orig_attempt.outcome == load_attempt.outcome
                assert orig_attempt.details == load_attempt.details
    
    def test_save_and_load_child_snapshot_roundtrip(self, tmp_path):
        """Test that saving and loading child snapshot preserves data."""
        snapshot_path = tmp_path / "snapshots" / "test_child.json"
        
        # Create original child
        original_child = ChildProfile(
            id="test_child",
            name="Test Child",
            age=10,
            grade=5,
            interests=["coding", "gaming"],
            learning_style="kinesthetic",
            attention_span_min=45,
            reading_level="above_grade",
            baseline_skills={"programming": 0.8, "reading": 0.9},
            goals=["build a game", "learn Python"]
        )
        
        # Save snapshot
        save_child_snapshot(original_child, str(snapshot_path))
        
        # Load and validate manually
        with open(snapshot_path, 'r') as f:
            data = json.load(f)
        
        # Check key fields
        assert data["id"] == original_child.id
        assert data["name"] == original_child.name
        assert data["age"] == original_child.age
        assert data["grade"] == original_child.grade
        assert data["interests"] == original_child.interests
        assert data["learning_style"] == original_child.learning_style
        assert data["attention_span_min"] == original_child.attention_span_min
        assert data["reading_level"] == original_child.reading_level
        assert data["baseline_skills"] == original_child.baseline_skills
        assert data["goals"] == original_child.goals
