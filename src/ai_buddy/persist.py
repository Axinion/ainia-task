"""
Data persistence utilities for AI Buddy.

This module provides functions for saving and loading session history
and child profile snapshots to/from JSON files.
"""

from __future__ import annotations
from pathlib import Path
import json
import tempfile
import shutil
from typing import Any
from .session import SessionLog, ActivityAttempt
from .data_models import ChildProfile


def save_history(history: list[SessionLog], path: str = "data/history.json") -> None:
    """
    Save session history to a JSON file.
    
    Args:
        history: List of session logs to save
        path: File path to save to (default: "data/history.json")
        
    Raises:
        OSError: If unable to write to the file
    """
    file_path = Path(path)
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON-serializable format
    history_data = [session.model_dump() for session in history]
    
    # Atomic write: write to temp file first, then replace
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            dir=file_path.parent,
            delete=False
        ) as temp_file:
            json.dump(history_data, temp_file, indent=2, default=str)
            temp_path = temp_file.name
        
        # Atomic move
        shutil.move(temp_path, file_path)
        
    except (OSError, IOError) as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals():
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass
        raise OSError(f"Failed to save history to {path}: {e}")


def load_history(path: str = "data/history.json") -> list[SessionLog]:
    """
    Load session history from a JSON file.
    
    Args:
        path: File path to load from (default: "data/history.json")
        
    Returns:
        List of session logs. Returns empty list if file doesn't exist.
        
    Raises:
        ValueError: If the JSON data is malformed or doesn't match expected schema
    """
    file_path = Path(path)
    
    if not file_path.exists():
        return []
    
    try:
        with open(file_path, 'r') as f:
            history_data = json.load(f)
        
        # Validate and convert back to SessionLog objects
        history = []
        for session_data in history_data:
            session = SessionLog.model_validate(session_data)
            history.append(session)
        
        return history
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")
    except Exception as e:
        raise ValueError(f"Failed to load history from {path}: {e}")


def save_child_snapshot(child: ChildProfile, path: str) -> None:
    """
    Save a child profile snapshot to a JSON file.
    
    Args:
        child: Child profile to save
        path: File path to save to (e.g., "data/snapshots/{child.id}.json")
        
    Raises:
        OSError: If unable to write to the file
    """
    file_path = Path(path)
    
    # Ensure parent directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON-serializable format
    child_data = child.model_dump()
    
    # Atomic write: write to temp file first, then replace
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            dir=file_path.parent,
            delete=False
        ) as temp_file:
            json.dump(child_data, temp_file, indent=2, default=str)
            temp_path = temp_file.name
        
        # Atomic move
        shutil.move(temp_path, file_path)
        
    except (OSError, IOError) as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals():
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass
        raise OSError(f"Failed to save child snapshot to {path}: {e}")


# Export the functions
__all__ = [
    "save_history",
    "load_history", 
    "save_child_snapshot"
]
