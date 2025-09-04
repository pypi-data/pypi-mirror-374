"""
Data preprocessing utilities.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from typing import Tuple, Union, Optional


def preprocess_data(X: Union[np.ndarray, pd.DataFrame],
                   y: Optional[Union[np.ndarray, pd.Series]] = None,
                   handle_missing: str = "mean",
                   scale_features: bool = True,
                   encode_categorical: bool = True) -> Tuple[Union[np.ndarray, pd.DataFrame], 
                                                           Optional[Union[np.ndarray, pd.Series]]]:
    """
    Preprocess data for machine learning.
    
    Args:
        X: Feature matrix
        y: Target variable (optional)
        handle_missing: Strategy for handling missing values
        scale_features: Whether to scale numerical features
        encode_categorical: Whether to encode categorical variables
    
    Returns:
        Tuple of (preprocessed_X, preprocessed_y)
    """
    X_processed = X.copy()
    
    # Handle missing values
    if handle_missing and X_processed.isnull().any().any():
        if handle_missing == "mean":
            imputer = SimpleImputer(strategy="mean")
        elif handle_missing == "median":
            imputer = SimpleImputer(strategy="median")
        elif handle_missing == "most_frequent":
            imputer = SimpleImputer(strategy="most_frequent")
        else:
            raise ValueError(f"Unsupported missing value strategy: {handle_missing}")
        
        X_processed = pd.DataFrame(imputer.fit_transform(X_processed), 
                                 columns=X_processed.columns)
    
    # Encode categorical variables
    if encode_categorical:
        for col in X_processed.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            X_processed[col] = le.fit_transform(X_processed[col].astype(str))
    
    # Scale features
    if scale_features:
        scaler = StandardScaler()
        X_processed = pd.DataFrame(scaler.fit_transform(X_processed), 
                                 columns=X_processed.columns)
    
    # Process target variable if provided
    y_processed = None
    if y is not None:
        y_processed = y.copy()
        if y_processed.dtype == 'object':
            le = LabelEncoder()
            y_processed = le.fit_transform(y_processed)
    
    return X_processed, y_processed


def split_categorical_numerical(X: Union[np.ndarray, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split features into categorical and numerical columns.
    
    Args:
        X: Feature matrix
    
    Returns:
        Tuple of (categorical_features, numerical_features)
    """
    categorical_cols = X.select_dtypes(include=['object']).columns
    numerical_cols = X.select_dtypes(include=[np.number]).columns
    
    return X[categorical_cols], X[numerical_cols]


def remove_outliers(X: Union[np.ndarray, pd.DataFrame], 
                   method: str = "iqr",
                   threshold: float = 1.5) -> Union[np.ndarray, pd.DataFrame]:
    """
    Remove outliers from numerical data.
    
    Args:
        X: Feature matrix
        method: Method for outlier detection ("iqr" or "zscore")
        threshold: Threshold for outlier detection
    
    Returns:
        Data with outliers removed
    """
    if method == "iqr":
        Q1 = X.quantile(0.25)
        Q3 = X.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        
        mask = ~((X < lower_bound) | (X > upper_bound)).any(axis=1)
        return X[mask]
    
    elif method == "zscore":
        z_scores = np.abs((X - X.mean()) / X.std())
        mask = (z_scores < threshold).all(axis=1)
        return X[mask]
    
    else:
        raise ValueError(f"Unsupported outlier removal method: {method}")
