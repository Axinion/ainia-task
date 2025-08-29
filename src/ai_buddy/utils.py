"""
Utility functions for AI Buddy.

This module contains helper functions and utilities used across the project.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import logging

from .data_models import DataRecord


def generate_id(content: str, prefix: str = "record") -> str:
    """
    Generate a unique ID based on content.
    
    Args:
        content: Content to hash
        prefix: Prefix for the generated ID
        
    Returns:
        Unique ID string
    """
    content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{prefix}_{content_hash}"


def validate_data_path(path: Union[str, Path]) -> Path:
    """
    Validate and return a Path object for data files.
    
    Args:
        path: Path to validate
        
    Returns:
        Path object
        
    Raises:
        ValueError: If path is invalid
    """
    path_obj = Path(path)
    
    if not path_obj.exists():
        raise ValueError(f"Path does not exist: {path}")
    
    if not path_obj.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    return path_obj


def save_records_to_json(records: List[DataRecord], file_path: Union[str, Path]) -> None:
    """
    Save data records to JSON file.
    
    TODO: Implement proper JSON serialization with error handling.
    
    Args:
        records: List of data records to save
        file_path: Output file path
    """
    # TODO: Implement JSON serialization
    data = [record.model_dump() for record in records]
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_records_from_json(file_path: Union[str, Path]) -> List[DataRecord]:
    """
    Load data records from JSON file.
    
    TODO: Implement proper JSON deserialization with validation.
    
    Args:
        file_path: Input file path
        
    Returns:
        List of data records
    """
    # TODO: Implement JSON deserialization with validation
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    records = []
    # TODO: Validate and convert data to DataRecord objects
    # for item in data:
    #     records.append(DataRecord(**item))
    
    return records


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            *([logging.FileHandler(log_file)] if log_file else [])
        ]
    )


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    
    if not path.exists():
        return {"error": "File does not exist"}
    
    return {
        "name": path.name,
        "size": path.stat().st_size,
        "modified": path.stat().st_mtime,
        "extension": path.suffix,
        "exists": True
    }


# TODO: Add more utility functions as needed
# def clean_text(text: str) -> str:
#     """Clean and normalize text data."""
#     pass

# def validate_url(url: str) -> bool:
#     """Validate URL format."""
#     pass

# def chunk_data(data: List[Any], chunk_size: int) -> List[List[Any]]:
#     """Split data into chunks."""
#     pass
