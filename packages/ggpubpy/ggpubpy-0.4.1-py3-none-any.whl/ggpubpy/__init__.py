"""
ggpubpy: matplotlib Based Publication-Ready Plots

A Python library that provides easy-to-use functions for creating and customizing
matplotlib-based, publication-ready plots with built-in statistical tests and
automatic p-value or significance star annotations.

This project is directly inspired by R's ggpubr package.
"""

from typing import Any, List, Tuple

__version__ = "0.4.0"
__author__ = "Izzet Turkalp Akbasli"
__email__ = "izzetakbasli@gmail.com"

# Import dataset functions (these don't require scipy)
from . import datasets
from .datasets import (
    get_iris_palette,
    get_titanic_palette,
    list_datasets,
    load_iris,
    load_titanic,
)


# Lazy imports to avoid scipy import issues during package import
def _import_plots() -> Tuple[Any, Any, Any, List[str]]:
    """Lazy import of plots module."""
    try:
        from .plots import (
            DEFAULT_PALETTE,
            plot_boxplot_with_stats,
            plot_violin_with_stats,
            significance_stars,
        )

        return (
            plot_violin_with_stats,
            plot_boxplot_with_stats,
            significance_stars,
            DEFAULT_PALETTE,
        )
    except ImportError as e:
        raise ImportError(
            f"Could not import plotting functions. Please ensure scipy is properly installed: {e}"
        )


# Create lazy loading functions
def plot_violin(*args: Any, **kwargs: Any) -> Any:
    """Create violin plot with statistical annotations."""
    plot_violin_with_stats, _, _, _ = _import_plots()
    return plot_violin_with_stats(*args, **kwargs)


def plot_boxplot(*args: Any, **kwargs: Any) -> Any:
    """Create box plot with statistical annotations."""
    _, plot_boxplot_with_stats, _, _ = _import_plots()
    return plot_boxplot_with_stats(*args, **kwargs)


def plot_violin_with_stats(*args: Any, **kwargs: Any) -> Any:
    """Create violin plot with statistical annotations."""
    func, _, _, _ = _import_plots()
    return func(*args, **kwargs)


def plot_boxplot_with_stats(*args: Any, **kwargs: Any) -> Any:
    """Create box plot with statistical annotations."""
    _, func, _, _ = _import_plots()
    return func(*args, **kwargs)


def significance_stars(*args: Any, **kwargs: Any) -> Any:
    """Convert p-values to significance stars."""
    _, _, func, _ = _import_plots()
    return func(*args, **kwargs)


# Lazy DEFAULT_PALETTE access
def get_default_palette() -> List[str]:
    """Get default color palette."""
    _, _, _, palette = _import_plots()
    return palette


# Lazy loader for shift plot
def plot_shift(x: Any, y: Any, *args: Any, **kwargs: Any) -> Any:
    """Shift plot comparing two distributions."""
    try:
        from .plots import plot_shift as _shift
    except ImportError as e:
        raise ImportError(
            f"Could not import shift plot function. Please ensure dependencies are installed: {e}"
        )
    return _shift(x, y, *args, **kwargs)


# Lazy loader for correlation matrix plot
def plot_correlation_matrix(*args: Any, **kwargs: Any) -> Any:
    """Create a correlation matrix plot with scatter plots and correlation values."""
    try:
        from .plots import plot_correlation_matrix as _corr_matrix
    except ImportError as e:
        raise ImportError(
            f"Could not import correlation matrix plot function. Please ensure dependencies are installed: {e}"
        )
    return _corr_matrix(*args, **kwargs)


# Lazy loader for alluvial plot
def plot_alluvial(*args: Any, **kwargs: Any) -> Any:
    """Create an alluvial (flow) diagram with explicit alluvium IDs."""
    try:
        from .alluvialplot import plot_alluvial as _alluvial
    except ImportError as e:
        raise ImportError(
            f"Could not import alluvial plot function. Please ensure dependencies are installed: {e}"
        )
    return _alluvial(*args, **kwargs)


# Lazy loader for alluvial plot with stats
def plot_alluvial_with_stats(*args: Any, **kwargs: Any) -> Any:
    """Create an alluvial plot with optional statistical annotations."""
    try:
        from .alluvialplot import plot_alluvial_with_stats as _alluvial_stats
    except ImportError as e:
        raise ImportError(
            f"Could not import alluvial plot with stats function. Please ensure dependencies are installed: {e}"
        )
    return _alluvial_stats(*args, **kwargs)


# Simple DEFAULT_PALETTE for basic access without scipy dependency
DEFAULT_PALETTE = [
    "#00AFBB",
    "#E7B800",
    "#FC4E07",
    "#4E79A7",
    "#E15759",
    "#59A14F",
    "#EDC948",
    "#B07AA1",
    "#FF9DA7",
    "#9C755F",
]

__all__ = [
    "plot_violin_with_stats",
    "plot_boxplot_with_stats",
    "plot_violin",
    "plot_boxplot",
    "significance_stars",
    "DEFAULT_PALETTE",
    "datasets",
    "load_iris",
    "load_titanic",
    "get_iris_palette",
    "get_titanic_palette",
    "list_datasets",
    "plot_shift",
    "plot_correlation_matrix",
    "plot_alluvial",
    "plot_alluvial_with_stats",
]
