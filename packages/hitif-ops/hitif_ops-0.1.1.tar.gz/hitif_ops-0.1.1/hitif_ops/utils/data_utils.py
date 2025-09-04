"""
Data utility functions for loading, processing, and saving data.
"""

import pandas as pd
import numpy as np
from typing import Union, Optional, Any
import json
import pickle


def load_data(file_path: str, file_type: Optional[str] = None) -> Union[pd.DataFrame, np.ndarray, Any]:
    """
    Load data from various file formats.
    
    Args:
        file_path: Path to the data file
        file_type: Type of file (auto-detected if None)
    
    Returns:
        Loaded data object
    """
    if file_type is None:
        file_type = file_path.split('.')[-1].lower()
    
    if file_type in ['csv']:
        return pd.read_csv(file_path)
    elif file_type in ['xlsx', 'xls']:
        return pd.read_excel(file_path)
    elif file_type in ['json']:
        with open(file_path, 'r') as f:
            return json.load(f)
    elif file_type in ['pkl', 'pickle']:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    elif file_type in ['npy']:
        return np.load(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def save_data(data: Any, file_path: str, file_type: Optional[str] = None) -> None:
    """
    Save data to various file formats.
    
    Args:
        data: Data to save
        file_path: Path where to save the file
        file_type: Type of file (auto-detected if None)
    """
    if file_type is None:
        file_type = file_path.split('.')[-1].lower()
    
    if file_type in ['csv']:
        if isinstance(data, pd.DataFrame):
            data.to_csv(file_path, index=False)
        else:
            pd.DataFrame(data).to_csv(file_path, index=False)
    elif file_type in ['xlsx']:
        if isinstance(data, pd.DataFrame):
            data.to_excel(file_path, index=False)
        else:
            pd.DataFrame(data).to_excel(file_path, index=False)
    elif file_type in ['json']:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    elif file_type in ['pkl', 'pickle']:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    elif file_type in ['npy']:
        np.save(file_path, data)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def process_files(file_paths: list, processor_func: callable) -> list:
    """
    Process multiple files using a given function.
    
    Args:
        file_paths: List of file paths to process
        processor_func: Function to apply to each file
    
    Returns:
        List of processed results
    """
    results = []
    for file_path in file_paths:
        try:
            result = processor_func(file_path)
            results.append(result)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            results.append(None)
    return results
