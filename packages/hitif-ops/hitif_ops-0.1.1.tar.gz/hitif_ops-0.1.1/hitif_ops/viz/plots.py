"""
Basic plotting utilities.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List, Union


def create_plot(data: Union[pd.DataFrame, np.ndarray],
                plot_type: str = "line",
                x_col: Optional[str] = None,
                y_col: Optional[str] = None,
                title: str = "",
                figsize: tuple = (10, 6)) -> plt.Figure:
    """
    Create a basic plot.
    
    Args:
        data: Data to plot
        plot_type: Type of plot ("line", "scatter", "bar", "hist")
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Plot title
        figsize: Figure size
    
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    if plot_type == "line":
        if x_col and y_col:
            ax.plot(data[x_col], data[y_col])
        else:
            ax.plot(data)
    elif plot_type == "scatter":
        if x_col and y_col:
            ax.scatter(data[x_col], data[y_col])
        else:
            ax.scatter(data[:, 0], data[:, 1])
    elif plot_type == "bar":
        if x_col and y_col:
            ax.bar(data[x_col], data[y_col])
        else:
            ax.bar(range(len(data)), data)
    elif plot_type == "hist":
        ax.hist(data, bins=30)
    else:
        raise ValueError(f"Unsupported plot type: {plot_type}")
    
    if title:
        ax.set_title(title)
    
    plt.tight_layout()
    return fig


def plot_distribution(data: Union[pd.Series, np.ndarray],
                     title: str = "Distribution Plot",
                     figsize: tuple = (10, 6)) -> plt.Figure:
    """
    Create a distribution plot.
    
    Args:
        data: Data to plot
        title: Plot title
        figsize: Figure size
    
    Returns:
        Matplotlib figure object
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Histogram
    ax1.hist(data, bins=30, alpha=0.7, edgecolor='black')
    ax1.set_title("Histogram")
    ax1.set_xlabel("Value")
    ax1.set_ylabel("Frequency")
    
    # Box plot
    ax2.boxplot(data)
    ax2.set_title("Box Plot")
    ax2.set_ylabel("Value")
    
    fig.suptitle(title)
    plt.tight_layout()
    return fig


def plot_correlation(data: pd.DataFrame,
                    title: str = "Correlation Matrix",
                    figsize: tuple = (10, 8)) -> plt.Figure:
    """
    Create a correlation matrix heatmap.
    
    Args:
        data: DataFrame to analyze
        title: Plot title
        figsize: Figure size
    
    Returns:
        Matplotlib figure object
    """
    # Calculate correlation matrix
    corr_matrix = data.corr()
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, ax=ax)
    
    ax.set_title(title)
    plt.tight_layout()
    return fig


def save_plot(fig: plt.Figure, filename: str, dpi: int = 300) -> None:
    """
    Save a plot to file.
    
    Args:
        fig: Matplotlib figure object
        filename: Output filename
        dpi: Resolution in DPI
    """
    fig.savefig(filename, dpi=dpi, bbox_inches='tight')
    print(f"Plot saved as {filename}")
