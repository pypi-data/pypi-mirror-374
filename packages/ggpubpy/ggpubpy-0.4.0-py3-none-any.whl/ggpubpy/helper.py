"""
Helper functions for ggpubpy plotting modules.

This module contains shared utility functions used across different plotting modules.
"""

import itertools
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection
from scipy.stats import (
    beta,
    f_oneway,
    gaussian_kde,
    kruskal,
    mannwhitneyu,
    norm,
    ttest_ind,
)

# Default color palette - updated with new colors
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


def _validate_inputs(
    df: pd.DataFrame, x: str, y: str, order: Optional[List] = None
) -> None:
    """
    Validate input parameters for plotting functions.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe.
    x : str
        Column name for categories.
    y : str
        Column name for numeric values.
    order : list, optional
        Order of categories.

    Raises
    ------
    AssertionError
        If inputs are invalid.
    """
    assert isinstance(df, pd.DataFrame), "df must be a pandas DataFrame"
    assert not df.empty, "DataFrame cannot be empty"
    assert x in df.columns, f"Column '{x}' not found in DataFrame"
    assert y in df.columns, f"Column '{y}' not found in DataFrame"
    assert pd.api.types.is_numeric_dtype(df[y]), f"Column '{y}' must be numeric"

    # Check if we have valid data after dropping NaN
    valid_data = df[[x, y]].dropna()
    assert not valid_data.empty, "No valid data remaining after removing NaN values"

    unique_groups = valid_data[x].unique()
    assert len(unique_groups) >= 1, f"Column '{x}' must have at least 1 unique value"

    if order is not None:
        assert isinstance(order, (list, tuple)), "order must be a list or tuple"
        assert all(
            item in unique_groups for item in order
        ), "All items in order must exist in the data"


def _perform_statistical_tests(
    groups: List[np.ndarray], parametric: bool = False
) -> Tuple[float, float, List[Tuple[int, int, float]]]:
    """
    Perform statistical tests on groups.

    Parameters
    ----------
    groups : list of arrays
        List of numeric arrays for each group.
    parametric : bool
        If True, use parametric tests (ANOVA, t-test).
        If False, use non-parametric tests (Kruskal-Wallis, Mann-Whitney U).

    Returns
    -------
    tuple
        (global_stat, global_p, pairwise_results)
        where pairwise_results is list of (i, j, p_value) tuples.
    """
    assert len(groups) >= 1, "At least one group is required"

    # Filter out empty groups
    valid_groups = [g for g in groups if len(g) > 0]
    assert len(valid_groups) >= 1, "At least one non-empty group is required"

    if len(valid_groups) == 1:
        return np.nan, np.nan, []

    # Global test
    if parametric:
        # One-way ANOVA for parametric case
        global_stat, global_p = f_oneway(*valid_groups)
    else:
        # Kruskal-Wallis for non-parametric case
        global_stat, global_p = kruskal(*valid_groups)

    # Pairwise tests
    pairwise_results = []
    valid_indices = [i for i, g in enumerate(groups) if len(g) > 0]

    for i, j in itertools.combinations(range(len(valid_indices)), 2):
        idx_i, idx_j = valid_indices[i], valid_indices[j]

        if parametric:
            # Independent t-test for parametric case
            _, p_val = ttest_ind(groups[idx_i], groups[idx_j])
        else:
            # Mann-Whitney U test for non-parametric case
            _, p_val = mannwhitneyu(
                groups[idx_i], groups[idx_j], alternative="two-sided"
            )

        pairwise_results.append((idx_i, idx_j, p_val))

    return global_stat, global_p, pairwise_results


def significance_stars(p: float) -> str:
    """
    Convert a p-value into star notation.

    Parameters
    ----------
    p : float
        The p-value to convert.

    Returns
    -------
    str
        Star notation: "****" for p <= 1e-4, "***" for p <= 1e-3,
        "**" for p <= 0.01, "*" for p <= 0.05, "ns" for p > 0.05.
    """
    if p <= 1e-4:
        return "****"
    if p <= 1e-3:
        return "***"
    if p <= 0.01:
        return "**"
    if p <= 0.05:
        return "*"
    return "ns"


def format_p_value(p: float) -> str:
    """
    Format p-value for display in statistical annotations.

    Parameters
    ----------
    p : float
        The p-value to format.

    Returns
    -------
    str
        Formatted p-value string. Shows "<0.001" for very small values.
    """
    if p <= 0.001:
        return "<0.001"
    elif p < 0.01:
        return f"{p:.3f}"
    else:
        return f"{p:.2f}"


def _get_palette_for_data(levels: List, palette: Optional[Dict] = None) -> Dict:
    """
    Generate a color palette for the given data levels.

    Parameters
    ----------
    levels : list
        List of unique category levels.
    palette : dict, optional
        User-provided palette mapping levels to colors.

    Returns
    -------
    dict
        Dictionary mapping each level to a color.
    """
    if palette is not None:
        # Use provided palette, fill missing levels with defaults
        result_palette = {}
        for i, level in enumerate(levels):
            if level in palette:
                result_palette[level] = palette[level]
            else:
                result_palette[level] = DEFAULT_PALETTE[i % len(DEFAULT_PALETTE)]
        return result_palette
    else:
        # Use default palette
        return {
            level: DEFAULT_PALETTE[i % len(DEFAULT_PALETTE)]
            for i, level in enumerate(levels)
        }


def _bias_corrected_ci(
    bootdist: np.ndarray, sample_point: float, alpha: float = 0.05
) -> np.ndarray:
    """Bias-corrected confidence intervals."""
    z0 = norm.ppf(np.mean(bootdist < sample_point))
    ll = norm.cdf(2 * z0 + norm.ppf(alpha / 2)) * 100
    ul = norm.cdf(2 * z0 + norm.ppf(1 - alpha / 2)) * 100
    return cast(np.ndarray, np.percentile(bootdist, [ll, ul]))


def harrelldavis(
    x: np.ndarray, quantile: Union[float, List[float], np.ndarray] = 0.5, axis: int = -1
) -> np.ndarray:
    """Harrell-Davis robust quantile estimator."""
    x = np.asarray(x)
    assert x.ndim <= 2, "Only 1D or 2D arrays supported."
    assert axis in [0, 1, -1], "Axis must be 0, 1, or -1."
    x = np.sort(x, axis=axis)
    n = x.shape[axis]
    vec = np.arange(n)
    qs = np.atleast_1d(quantile)
    res = []
    for q in qs:
        m1, m2 = (n + 1) * q, (n + 1) * (1 - q)
        w = cast(
            np.ndarray,
            beta.cdf((vec + 1) / n, m1, m2) - beta.cdf(vec / n, m1, m2),
        )
        if x.ndim > 1 and axis == 0:
            w = w[:, np.newaxis]  # Broadcast weights for column-wise operations
        val = (w * x).sum(axis=axis)
        res.append(val)
    result: np.ndarray = np.squeeze(np.array(res, dtype=np.float64))
    # Always return as array for consistent typing
    return cast(np.ndarray, np.atleast_1d(result))
