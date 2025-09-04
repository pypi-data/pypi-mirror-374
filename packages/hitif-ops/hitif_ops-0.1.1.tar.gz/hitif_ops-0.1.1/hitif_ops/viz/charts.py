"""
Advanced chart utilities.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, List, Union


def create_subplots(data: pd.DataFrame,
                   plot_types: List[str],
                   columns: Optional[List[str]] = None,
                   figsize: tuple = (15, 10)) -> plt.Figure:
    """
    Create multiple subplots.
    
    Args:
        data: DataFrame to plot
        plot_types: List of plot types for each subplot
        columns: Columns to use for each subplot
        figsize: Figure size
    
    Returns:
        Matplotlib figure object
    """
    n_plots = len(plot_types)
    n_cols = min(3, n_plots)
    n_rows = (n_plots + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
    if n_plots == 1:
        axes = [axes]
    elif n_rows == 1:
        axes = axes.reshape(1, -1)
    else:
        axes = axes.flatten()
    
    for i, (plot_type, ax) in enumerate(zip(plot_types, axes)):
        if columns and i < len(columns):
            col = columns[i]
            if plot_type == "hist":
                ax.hist(data[col].dropna(), bins=30, alpha=0.7)
                ax.set_title(f"{col} - Histogram")
            elif plot_type == "box":
                ax.boxplot(data[col].dropna())
                ax.set_title(f"{col} - Box Plot")
            elif plot_type == "line":
                ax.plot(data[col].dropna())
                ax.set_title(f"{col} - Line Plot")
        
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    return fig


def plot_time_series(data: pd.DataFrame,
                    time_col: str,
                    value_cols: List[str],
                    title: str = "Time Series Plot",
                    figsize: tuple = (12, 8)) -> plt.Figure:
    """
    Create a time series plot.
    
    Args:
        data: DataFrame with time series data
        time_col: Column containing time information
        value_cols: Columns containing values to plot
        title: Plot title
        figsize: Figure size
    
    Returns:
        Matplotlib figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    for col in value_cols:
        ax.plot(data[time_col], data[col], label=col, marker='o', markersize=3)
    
    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45)
    
    plt.tight_layout()
    return fig


def create_dashboard(data: pd.DataFrame,
                    metrics: List[str],
                    figsize: tuple = (16, 12)) -> plt.Figure:
    """
    Create a dashboard with multiple visualizations.
    
    Args:
        data: DataFrame to visualize
        metrics: List of metric columns to include
        figsize: Figure size
    
    Returns:
        Matplotlib figure object
    """
    fig = plt.figure(figsize=figsize)
    
    # Create grid layout
    gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
    
    # Summary statistics
    ax1 = fig.add_subplot(gs[0, :2])
    summary_stats = data[metrics].describe()
    ax1.table(cellText=summary_stats.values,
              rowLabels=summary_stats.index,
              colLabels=summary_stats.columns,
              cellLoc='center',
              loc='center')
    ax1.set_title("Summary Statistics")
    ax1.axis('off')
    
    # Correlation heatmap
    ax2 = fig.add_subplot(gs[0, 2:])
    corr_matrix = data[metrics].corr()
    im = ax2.imshow(corr_matrix, cmap='coolwarm', aspect='auto')
    ax2.set_xticks(range(len(metrics)))
    ax2.set_yticks(range(len(metrics)))
    ax2.set_xticklabels(metrics, rotation=45)
    ax2.set_yticklabels(metrics)
    ax2.set_title("Correlation Matrix")
    
    # Add colorbar
    cbar = fig.colorbar(im, ax=ax2)
    
    # Distribution plots
    for i, metric in enumerate(metrics[:4]):
        row = (i // 2) + 1
        col = (i % 2) * 2
        ax = fig.add_subplot(gs[row, col:col+2])
        ax.hist(data[metric].dropna(), bins=20, alpha=0.7, edgecolor='black')
        ax.set_title(f"{metric} Distribution")
        ax.set_xlabel(metric)
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.3)
    
    plt.suptitle("Data Dashboard", fontsize=16)
    return fig
