"""
Core plotting functions for ggpubpy.

This module contains the main plotting functions that create publication-ready
plots with statistical annotations.
"""

# Import all plotting functions from their respective modules
from .alluvialplot import plot_alluvial, plot_alluvial_with_stats
from .boxplot import plot_boxplot_with_stats
from .correlation_matrix import plot_correlation_matrix

# Import helper functions for backward compatibility
from .helper import (
    DEFAULT_PALETTE,
    _bias_corrected_ci,
    _get_palette_for_data,
    _perform_statistical_tests,
    _validate_inputs,
    format_p_value,
    harrelldavis,
    significance_stars,
)
from .shiftplot import plot_shift
from .violinplot import plot_violin_with_stats

# Export all functions for backward compatibility
__all__ = [
    "plot_alluvial",
    "plot_alluvial_with_stats",
    "plot_violin_with_stats",
    "plot_boxplot_with_stats",
    "plot_shift",
    "plot_correlation_matrix",
    "DEFAULT_PALETTE",
    "_bias_corrected_ci",
    "_get_palette_for_data",
    "_perform_statistical_tests",
    "_validate_inputs",
    "format_p_value",
    "harrelldavis",
    "significance_stars",
]
