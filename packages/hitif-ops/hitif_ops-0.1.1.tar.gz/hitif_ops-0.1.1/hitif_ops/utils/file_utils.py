"""
File utility functions for file operations and management.
"""

import os
import glob
from pathlib import Path
from typing import List, Optional


def get_file_list(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
    """
    Get a list of files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: File pattern to match (e.g., "*.csv", "*.py")
        recursive: Whether to search recursively in subdirectories
    
    Returns:
        List of file paths
    """
    search_pattern = os.path.join(directory, "**" if recursive else "", pattern)
    return glob.glob(search_pattern, recursive=recursive)


def ensure_directory(directory: str) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory: Directory path to ensure exists
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
    
    Returns:
        File extension (without the dot)
    """
    return Path(file_path).suffix[1:]


def is_file_empty(file_path: str) -> bool:
    """
    Check if a file is empty.
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if file is empty, False otherwise
    """
    return os.path.getsize(file_path) == 0
