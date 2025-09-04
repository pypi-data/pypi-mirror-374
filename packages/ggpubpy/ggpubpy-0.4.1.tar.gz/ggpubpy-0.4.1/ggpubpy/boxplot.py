"""
Boxplot functionality for ggpubpy.

This module contains the boxplot function with statistical annotations.
"""

from typing import Dict, List, Optional, Tuple

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .helper import (
    _get_palette_for_data,
    _perform_statistical_tests,
    _validate_inputs,
    format_p_value,
    significance_stars,
)


def plot_boxplot_with_stats(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    order: Optional[List] = None,
    palette: Optional[Dict] = None,
    figsize: Tuple[int, int] = (6, 6),
    add_jitter: bool = True,
    jitter_std: float = 0.04,
    box_width: float = 0.6,
    global_test: bool = True,
    pairwise_test: bool = True,
    parametric: bool = False,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Draw a colored boxplot with jittered points and statistical annotations.

    Parameters
    ----------
    df : pd.DataFrame
        Your data.
    x : str
        Column name for categories (must be categorical).
    y : str
        Column name for numeric values.
    x_label, y_label : str, optional        Axis labels. Defaults to column names.
    order : list, optional
        Order of x categories. Defaults to sorted unique values.
    palette : dict, optional
        Mapping from category -> color.
    figsize : tuple
        Figure size.
    add_jitter : bool
        Whether to add jittered points.
    jitter_std : float
        Standard deviation for horizontal jitter.    box_width : float
        Width of each box in the plot.
    global_test : bool
        Whether to perform and display global statistical test.
    pairwise_test : bool
        Whether to perform and display pairwise comparisons.
    parametric : bool
        If True, use parametric tests (ANOVA + t-test).
        If False, use non-parametric tests (Kruskal-Wallis + Mann-Whitney U).

    Returns
    -------
    tuple        (figure, axes) matplotlib objects.
    """  # Validate inputs
    _validate_inputs(df, x, y, order)
    assert (
        isinstance(figsize, (tuple, list)) and len(figsize) == 2
    ), "figsize must be a tuple/list of length 2"
    assert isinstance(add_jitter, bool), "add_jitter must be a boolean"
    assert jitter_std >= 0, "jitter_std must be non-negative"
    assert box_width > 0, "box_width must be positive"
    assert isinstance(parametric, bool), "parametric must be a boolean"

    # Prepare category levels and corresponding data
    levels = order if order is not None else sorted(df[x].unique())
    groups = [df[df[x] == lvl][y].dropna().values for lvl in levels]
    positions = np.arange(len(levels)) + 1

    # Generate color palette
    color_palette = _get_palette_for_data(levels, palette)  # Statistical tests
    global_stat, global_p, pairwise_p = _perform_statistical_tests(groups, parametric)

    # Filter pairwise results if pairwise_test is False
    if not pairwise_test:
        pairwise_p = []

    # Create figure
    fig, ax = plt.subplots(figsize=figsize)  # Create boxplots
    bp = ax.boxplot(
        groups,
        positions=positions,
        widths=box_width,
        patch_artist=True,
        notch=False,
        showfliers=False,
    )
    # Define different marker shapes for each group
    markers = ["o", "s", "^", "D", "v", "<", ">", "p", "*", "h"]

    # Color all box elements with palette colors
    for idx, level in enumerate(levels):
        color = color_palette[level]

        # Box outline
        bp["boxes"][idx].set_facecolor("none")  # Boş iç
        bp["boxes"][idx].set_edgecolor(color)  # Colored edge
        bp["boxes"][idx].set_linewidth(2)  # Kalın kenar

        # Whiskers (her box için 2 whisker var)
        bp["whiskers"][idx * 2].set_color(color)
        bp["whiskers"][idx * 2].set_linewidth(2)
        bp["whiskers"][idx * 2 + 1].set_color(color)
        bp["whiskers"][idx * 2 + 1].set_linewidth(2)

        # Caps (her box için 2 cap var)
        bp["caps"][idx * 2].set_color(color)
        bp["caps"][idx * 2].set_linewidth(2)
        bp["caps"][idx * 2 + 1].set_color(color)
        bp["caps"][idx * 2 + 1].set_linewidth(2)
        # Median line
        bp["medians"][idx].set_color(color)
        bp["medians"][idx].set_linewidth(2)

    # Add jittered points with different markers for each group
    if add_jitter:
        rng = np.random.default_rng(0)
        for idx, (pos, values) in enumerate(zip(positions, groups)):
            level = levels[idx]
            color = color_palette[level]
            marker = markers[idx % len(markers)]  # Different marker shapes
            xs = rng.normal(pos, jitter_std, size=len(values))
            ax.scatter(
                xs, values, s=20, color=color, alpha=0.7, marker=marker, zorder=3
            )  # Statistical annotations
    y_min: float = np.min([np.min(g) for g in groups if len(g) > 0])
    y_max: float = np.max([np.max(g) for g in groups if len(g) > 0])
    span = y_max - y_min
    base = y_max + 0.1 * span
    step = 0.1 * span  # Pairwise annotations
    for idx, (i, j, pval) in enumerate(pairwise_p):
        i_pos, j_pos = positions[i], positions[j]
        y0 = base + step * idx
        p_text = significance_stars(pval)
        ax.plot(
            [i_pos, i_pos, j_pos, j_pos],
            [y0, y0 + 0.02 * span, y0 + 0.02 * span, y0],
            color="black",
        )
        ax.text(
            (i_pos + j_pos) / 2, y0 + 0.03 * span, p_text, ha="center", va="bottom"
        )  # Global test annotation
    if global_test and not np.isnan(global_p):
        test_name = "One-way ANOVA" if parametric else "Kruskal-Wallis"
        p_formatted = format_p_value(global_p)
        ax.text(
            positions[0],
            base + step * (len(pairwise_p) + 0.4),
            f"{test_name} p = {p_formatted}",
            fontsize=10,
            va="bottom",
        )  # Axis labels
    ax.set_xticks(positions)
    ax.set_xticklabels(levels)
    ax.set_xlabel(x_label or x)
    ax.set_ylabel(y_label or y)

    # Legend
    handles = [mpatches.Patch(color=color_palette[l], label=l) for l in levels]
    ax.legend(handles=handles, title=x_label or x)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(y_min - 0.05 * span, base + step * (len(pairwise_p) + 0.8))
    plt.tight_layout()
    return fig, ax
