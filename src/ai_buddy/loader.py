"""
Data loading utilities for AI Buddy.

This module provides functions for loading and processing data from various sources.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from pydantic import ValidationError

from .data_models import Activity, ChildProfile


def load_json(path: str) -> Any:
    """
    Load and parse JSON data from a file.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If JSON parsing fails
    """
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}")


def load_activities(path: str) -> List[Activity]:
    """
    Load activities from a JSON file and validate with Pydantic models.
    
    Args:
        path: Path to the JSON file containing activities
        
    Returns:
        List of validated Activity objects
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If validation fails with item index and error details
    """
    data = load_json(path)
    
    if not isinstance(data, list):
        raise ValueError(f"Expected list of activities in {path}, got {type(data).__name__}")
    
    activities = []
    for i, item in enumerate(data):
        try:
            activity = Activity(**item)
            activities.append(activity)
        except ValidationError as e:
            raise ValueError(f"Activity at index {i} in {path} failed validation: {e}")
    
    return activities


def load_profiles(path: str) -> List[ChildProfile]:
    """
    Load child profiles from a JSON file and validate with Pydantic models.
    
    Args:
        path: Path to the JSON file containing child profiles
        
    Returns:
        List of validated ChildProfile objects
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If validation fails with item index and error details
    """
    data = load_json(path)
    
    if not isinstance(data, list):
        raise ValueError(f"Expected list of profiles in {path}, got {type(data).__name__}")
    
    profiles = []
    for i, item in enumerate(data):
        try:
            profile = ChildProfile(**item)
            profiles.append(profile)
        except ValidationError as e:
            raise ValueError(f"Profile at index {i} in {path} failed validation: {e}")
    
    return profiles


def summarize_activities(activities: List[Activity]) -> Dict[str, Any]:
    """
    Create a summary of activities with counts by type and level.
    
    Args:
        activities: List of Activity objects
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        "total": len(activities),
        "by_type": {},
        "by_level": {}
    }
    
    # Count by type
    for activity in activities:
        activity_type = activity.type
        summary["by_type"][activity_type] = summary["by_type"].get(activity_type, 0) + 1
    
    # Count by level
    for activity in activities:
        level = activity.level
        summary["by_level"][level] = summary["by_level"].get(level, 0) + 1
    
    return summary


def summarize_profiles(profiles: List[ChildProfile]) -> Dict[str, Any]:
    """
    Create a summary of child profiles with counts by reading level and learning style.
    
    Args:
        profiles: List of ChildProfile objects
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        "total": len(profiles),
        "by_reading_level": {},
        "by_learning_style": {}
    }
    
    # Count by reading level
    for profile in profiles:
        reading_level = profile.reading_level
        summary["by_reading_level"][reading_level] = summary["by_reading_level"].get(reading_level, 0) + 1
    
    # Count by learning style
    for profile in profiles:
        learning_style = profile.learning_style
        summary["by_learning_style"][learning_style] = summary["by_learning_style"].get(learning_style, 0) + 1
    
    return summary


if __name__ == "__main__":
    """Main guard for running summaries when module is executed directly."""
    try:
        # Load and summarize activities
        activities_path = "data/activities.json"
        if Path(activities_path).exists():
            activities = load_activities(activities_path)
            activities_summary = summarize_activities(activities)
            print("Activities Summary:")
            print(f"  Total: {activities_summary['total']}")
            print("  By Type:")
            for activity_type, count in activities_summary["by_type"].items():
                print(f"    {activity_type}: {count}")
            print("  By Level:")
            for level, count in activities_summary["by_level"].items():
                print(f"    {level}: {count}")
        else:
            print(f"Activities file not found: {activities_path}")
        
        print()
        
        # Load and summarize profiles
        profiles_path = "data/profiles.json"
        if Path(profiles_path).exists():
            profiles = load_profiles(profiles_path)
            profiles_summary = summarize_profiles(profiles)
            print("Profiles Summary:")
            print(f"  Total: {profiles_summary['total']}")
            print("  By Reading Level:")
            for reading_level, count in profiles_summary["by_reading_level"].items():
                print(f"    {reading_level}: {count}")
            print("  By Learning Style:")
            for learning_style, count in profiles_summary["by_learning_style"].items():
                print(f"    {learning_style}: {count}")
        else:
            print(f"Profiles file not found: {profiles_path}")
            
    except Exception as e:
        print(f"Error: {e}")
