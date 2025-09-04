"""
Correlation matrix functionality for ggpubpy.

This module contains the correlation matrix plot function.
"""

from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .helper import significance_stars


def plot_correlation_matrix(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    *,
    figsize: Tuple[int, int] = (10, 10),
    color: str = "#2E86AB",
    alpha: float = 0.6,
    point_size: float = 20,
    show_stats: bool = True,
    method: str = "pearson",
    title: Optional[str] = None,
) -> Tuple[plt.Figure, np.ndarray]:
    """
    Create a correlation matrix plot with scatter plots in lower triangle
    and correlation values in upper triangle and diagonal.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with numeric columns.
    columns : list of str, optional
        Specific columns to include. If None, all numeric columns are used.
    figsize : tuple
        Figure size as (width, height).
    color : str
        Color for scatter points.
    alpha : float
        Transparency of scatter points (0-1).
    point_size : float
        Size of scatter points.
    show_stats : bool
        Whether to show statistical significance stars.
    method : str
        Correlation method: 'pearson', 'spearman', or 'kendall'.
    title : str, optional
        Plot title.

    Returns
    -------
    tuple
        (figure, axes_array) matplotlib objects.
    """
    # Input validation
    assert isinstance(df, pd.DataFrame), "df must be a pandas DataFrame"
    assert not df.empty, "DataFrame cannot be empty"
    assert method in [
        "pearson",
        "spearman",
        "kendall",
    ], "method must be 'pearson', 'spearman', or 'kendall'"
    assert 0 <= alpha <= 1, "alpha must be between 0 and 1"
    assert point_size > 0, "point_size must be positive"

    # Select numeric columns
    if columns is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        assert len(numeric_cols) >= 2, "At least 2 numeric columns required"
        columns = numeric_cols
    else:
        assert isinstance(columns, (list, tuple)), "columns must be a list or tuple"
        assert len(columns) >= 2, "At least 2 columns required"
        for col in columns:
            assert col in df.columns, f"Column '{col}' not found in DataFrame"
            assert pd.api.types.is_numeric_dtype(
                df[col]
            ), f"Column '{col}' must be numeric"

    # Remove rows with any NaN values in selected columns
    data = df[columns].dropna()
    assert not data.empty, "No valid data remaining after removing NaN values"

    n_vars = len(columns)

    # Calculate correlation matrix
    corr_matrix = data.corr(method=method)

    # Calculate p-values for significance testing
    from scipy.stats import kendalltau, pearsonr, spearmanr

    p_matrix = np.ones((n_vars, n_vars))
    for i in range(n_vars):
        for j in range(n_vars):
            if i != j:
                x, y = data.iloc[:, i], data.iloc[:, j]
                if method == "pearson":
                    _, p_val = pearsonr(x, y)
                elif method == "spearman":
                    _, p_val = spearmanr(x, y)
                else:  # kendall
                    _, p_val = kendalltau(x, y)
                p_matrix[i, j] = p_val

    # Create figure and subplots
    fig, axes = plt.subplots(n_vars, n_vars, figsize=figsize)
    if n_vars == 1:
        axes = np.array([[axes]])
    elif n_vars == 2:
        axes = axes.reshape(2, 2)

    # Remove space between subplots
    plt.subplots_adjust(hspace=0.05, wspace=0.05)

    # Add labels on edges
    # Top row: variable names as x-labels
    for j in range(n_vars):
        ax_top = axes[0, j]
        if j == 0:
            # For diagonal, add on top
            ax_top.set_title(columns[j], fontsize=12, fontweight="bold", pad=10)
        else:
            # For upper triangle plots, add as top x-label
            ax_twin = ax_top.twiny()
            ax_twin.set_xlabel(columns[j], fontsize=12, fontweight="bold")
            ax_twin.tick_params(
                labeltop=False, top=False, bottom=False, labelbottom=False
            )

    # Bottom row: variable names as x-labels
    for j in range(n_vars):
        if axes[n_vars - 1, j].get_xlabel() == "":  # Only if not already set
            axes[n_vars - 1, j].set_xlabel(columns[j], fontsize=12, fontweight="bold")

    # Right column: variable names as y-labels
    for i in range(n_vars):
        ax_right = axes[i, n_vars - 1]
        if i < n_vars - 1:  # Not the bottom-right corner
            ax_twin = ax_right.twinx()
            ax_twin.set_ylabel(
                columns[i], fontsize=12, fontweight="bold", rotation=270, labelpad=15
            )
            ax_twin.tick_params(
                labelright=False, right=False, left=False, labelleft=False
            )

    # Left column: variable names as y-labels
    for i in range(1, n_vars):  # Skip the top-left corner
        axes[i, 0].set_ylabel(columns[i], fontsize=12, fontweight="bold")

    for i in range(n_vars):
        for j in range(n_vars):
            ax = axes[i, j]

            if i == j:
                # Diagonal: show histogram with KDE overlay
                ax.hist(
                    data.iloc[:, i],
                    bins=20,
                    color=color,
                    alpha=alpha,
                    edgecolor="black",
                    density=True,
                )

                # Add KDE overlay
                from scipy.stats import gaussian_kde

                kde_data = data.iloc[:, i].dropna()
                if len(kde_data) > 1:
                    kde = gaussian_kde(kde_data)
                    x_range = np.linspace(kde_data.min(), kde_data.max(), 100)
                    kde_values = kde(x_range)
                    ax.plot(x_range, kde_values, color="black", linewidth=2)

                # Configure ticks for diagonal - show ticks but not all labels
                # Bottom row: show x ticks and values
                if i == n_vars - 1:
                    ax.tick_params(
                        labelbottom=True,
                        bottom=True,
                        labelleft=False,
                        left=False,
                        labeltop=False,
                        labelright=False,
                        top=False,
                        right=False,
                    )
                # Left column: show y ticks and values
                elif i == 0:
                    ax.tick_params(
                        labelbottom=False,
                        bottom=False,
                        labelleft=True,
                        left=True,
                        labeltop=False,
                        labelright=False,
                        top=False,
                        right=False,
                    )
                # Middle diagonals: no labels but show ticks for reference
                else:
                    ax.tick_params(
                        labelbottom=False,
                        bottom=True,
                        labelleft=False,
                        left=True,
                        labeltop=False,
                        labelright=False,
                        top=False,
                        right=False,
                    )

            elif i > j:
                # Lower triangle: scatter plots
                x_data, y_data = data.iloc[:, j], data.iloc[:, i]
                ax.scatter(x_data, y_data, color=color, alpha=alpha, s=point_size)

                # Add trend line
                z = np.polyfit(x_data, y_data, 1)
                p = np.poly1d(z)
                ax.plot(x_data, p(x_data), "r--", alpha=0.8, linewidth=1)

                # Configure ticks and labels for scatter plots
                # Bottom row: show x ticks and values
                if i == n_vars - 1:
                    ax.tick_params(labelbottom=True, bottom=True)
                else:
                    ax.tick_params(labelbottom=False, bottom=False)

                # Left column: show y ticks and values
                if j == 0:
                    ax.tick_params(labelleft=True, left=True)
                else:
                    ax.tick_params(labelleft=False, left=False)

                # Always hide top and right ticks
                ax.tick_params(labeltop=False, labelright=False, top=False, right=False)

            else:
                # Upper triangle: correlation values
                corr_val = corr_matrix.iloc[i, j]
                p_val = p_matrix[i, j]

                # Format correlation value
                corr_text = f"Corr:\n{corr_val:.3f}"

                # Add significance stars if requested
                if show_stats:
                    stars = significance_stars(p_val)
                    if stars != "ns":
                        corr_text += f"{stars}"

                # Color based on correlation strength
                if abs(corr_val) >= 0.7:
                    text_color = "darkred" if corr_val > 0 else "darkblue"
                elif abs(corr_val) >= 0.3:
                    text_color = "red" if corr_val > 0 else "blue"
                else:
                    text_color = "black"

                ax.text(
                    0.5,
                    0.5,
                    corr_text,
                    transform=ax.transAxes,
                    fontsize=11,
                    ha="center",
                    va="center",
                    color=text_color,
                    fontweight="bold",
                )

                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.tick_params(
                    labelbottom=False,
                    labelleft=False,
                    bottom=False,
                    left=False,
                    top=False,
                    right=False,
                )

    # Add overall title
    if title:
        fig.suptitle(title, fontsize=16, fontweight="bold", y=0.95)
    else:
        method_name = method.capitalize()
        fig.suptitle(
            f"{method_name} Correlation Matrix", fontsize=16, fontweight="bold", y=0.95
        )

    # Remove spines from all subplots
    for i in range(n_vars):
        for j in range(n_vars):
            for spine in axes[i, j].spines.values():
                spine.set_visible(False)

    return fig, axes
