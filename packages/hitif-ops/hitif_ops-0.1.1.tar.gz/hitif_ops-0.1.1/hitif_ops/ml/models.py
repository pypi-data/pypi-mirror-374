"""
Machine learning model utilities.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from typing import Tuple, Any, Dict, Union


def train_model(X: Union[np.ndarray, pd.DataFrame], 
                y: Union[np.ndarray, pd.Series], 
                model_type: str = "random_forest",
                test_size: float = 0.2,
                random_state: int = 42) -> Tuple[Any, Dict[str, Any]]:
    """
    Train a machine learning model.
    
    Args:
        X: Feature matrix
        y: Target variable
        model_type: Type of model to train
        test_size: Proportion of data for testing
        random_state: Random seed for reproducibility
    
    Returns:
        Tuple of (trained_model, metrics_dict)
    """
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Select and train model
    if model_type == "random_forest":
        if len(np.unique(y)) <= 10:  # Classification
            model = RandomForestClassifier(random_state=random_state)
        else:  # Regression
            model = RandomForestRegressor(random_state=random_state)
    elif model_type == "logistic":
        model = LogisticRegression(random_state=random_state)
    elif model_type == "linear":
        model = LinearRegression()
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    if len(np.unique(y)) <= 10:  # Classification
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "classification_report": classification_report(y_test, y_pred)
        }
    else:  # Regression
        metrics = {
            "mse": mean_squared_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred))
        }
    
    return model, metrics


def evaluate_model(model: Any, X_test: Union[np.ndarray, pd.DataFrame], 
                  y_test: Union[np.ndarray, pd.Series]) -> Dict[str, Any]:
    """
    Evaluate a trained model on test data.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test targets
    
    Returns:
        Dictionary of evaluation metrics
    """
    y_pred = model.predict(X_test)
    
    if len(np.unique(y_test)) <= 10:  # Classification
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "classification_report": classification_report(y_test, y_pred)
        }
    else:  # Regression
        metrics = {
            "mse": mean_squared_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred))
        }
    
    return metrics
