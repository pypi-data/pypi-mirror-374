"""
Violin plot functionality for ggpubpy.

This module contains the violin plot function with statistical annotations.
"""

from typing import Dict, List, Optional, Tuple, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection

from .helper import (
    _get_palette_for_data,
    _perform_statistical_tests,
    _validate_inputs,
    format_p_value,
    significance_stars,
)


def plot_violin_with_stats(
    df: pd.DataFrame,
    x: str,
    y: str,
    *,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    order: Optional[List] = None,
    palette: Optional[Dict] = None,
    figsize: Tuple[int, int] = (6, 6),
    figsize_scale: float = 1.0,
    add_jitter: bool = True,
    jitter_std: float = 0.04,
    violin_width: float = 0.6,
    box_width: float = 0.15,
    global_test: bool = True,
    pairwise_test: bool = True,
    parametric: bool = False,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Draw a violin + boxplot + jitter + stats.

    Parameters
    ----------
    df : pd.DataFrame
        Your data.
    x : str
        Categorical column name.
    y : str
        Numeric column name.
    x_label : str, optional
        Custom label for the x-axis.
    y_label : str, optional
        Custom label for the y-axis.
    order : list, optional
        Order of x categories. Defaults to sorted unique values.
    palette : dict, optional
        Mapping from category -> color.
    figsize : tuple
        Figure size.
    figsize_scale : float
        Scale factor for figure size.
    add_jitter : bool
        Whether to add jittered points.
    jitter_std : float
        Standard deviation for horizontal jitter.
    violin_width : float
        Width of violin plots.
    box_width : float
        Width of boxplots inside violins.
    global_test : bool
        Whether to perform global statistical test.
    pairwise_test : bool
        Whether to perform pairwise statistical tests.
    parametric : bool
        If True, use parametric tests (ANOVA + t-test).
        If False, use non-parametric tests (Kruskal-Wallis + Mann-Whitney U).

    Returns
    -------
    tuple
        (figure, axes) matplotlib objects.
    """
    # Validate inputs
    _validate_inputs(df, x, y, order)
    assert (
        isinstance(figsize, (tuple, list)) and len(figsize) == 2
    ), "figsize must be a tuple/list of length 2"
    assert figsize_scale > 0, "figsize_scale must be positive"
    assert jitter_std >= 0, "jitter_std must be non-negative"
    assert violin_width > 0, "violin_width must be positive"
    assert box_width > 0, "box_width must be positive"
    assert isinstance(
        parametric, bool
    ), "parametric must be a boolean"  # Prepare category levels and corresponding data
    levels = order if order is not None else sorted(df[x].unique())
    groups = [df[df[x] == lvl][y].dropna().values for lvl in levels]
    positions = np.arange(len(levels)) + 1

    # Generate color palette
    color_palette = _get_palette_for_data(levels, palette)

    # Statistical tests
    global_stat, global_p, pairwise = _perform_statistical_tests(groups, parametric)

    # Filter pairwise results if pairwise_test is False
    if not pairwise_test:
        pairwise = []  # Create figure
    scaled_figsize = (figsize[0] * figsize_scale, figsize[1] * figsize_scale)
    fig, ax = plt.subplots(figsize=scaled_figsize)

    # Violin plots
    violin_parts = ax.violinplot(
        groups,
        positions=positions,
        widths=violin_width,
        showextrema=True,
        showmedians=False,
        showmeans=False,
    )  # Color the violins with palette
    bodies = cast(List[PolyCollection], violin_parts["bodies"])
    for idx, body in enumerate(bodies):
        level = levels[idx]
        color = color_palette[level]
        body.set_facecolor(color)
        body.set_edgecolor("black")
        body.set_alpha(1.0)  # Fully filled violin

    # Color the violin extrema lines if they exist (these are LineCollection objects)
    if "cmins" in violin_parts and violin_parts["cmins"] is not None:
        violin_parts["cmins"].set_color("black")
        violin_parts["cmins"].set_linewidth(1)
    if "cmaxes" in violin_parts and violin_parts["cmaxes"] is not None:
        violin_parts["cmaxes"].set_color("black")
        violin_parts["cmaxes"].set_linewidth(1)
    if "cbars" in violin_parts and violin_parts["cbars"] is not None:
        violin_parts["cbars"].set_color("black")
        violin_parts["cbars"].set_linewidth(1)

    # Boxplots - white background
    ax.boxplot(
        groups,
        positions=positions,
        widths=box_width,
        patch_artist=True,
        showfliers=False,
        boxprops=dict(facecolor="white", color="black"),
        whiskerprops=dict(color="black"),
        capprops=dict(color="black"),
        medianprops=dict(color="black"),
    )

    # Add jittered points
    if add_jitter:
        rng = np.random.default_rng(0)
        for pos, values in zip(positions, groups):
            xs = rng.normal(pos, jitter_std, size=len(values))
            ax.scatter(
                xs, values, s=15, color="k", alpha=0.6, zorder=3
            )  # Statistical annotations
    data_min: float = np.min([np.min(g) for g in groups if len(g) > 0])
    data_max: float = np.max([np.max(g) for g in groups if len(g) > 0])
    span = data_max - data_min
    base = data_max + 0.1 * span
    step = 0.1 * span  # Pairwise annotations
    for idx, (i, j, pval) in enumerate(pairwise):
        i_pos, j_pos = positions[i], positions[j]
        y0 = base + step * idx
        p_text = significance_stars(pval)
        ax.plot(
            [i_pos, i_pos, j_pos, j_pos],
            [y0, y0 + 0.02 * span, y0 + 0.02 * span, y0],
            color="black",
        )
        ax.text((i_pos + j_pos) / 2, y0 + 0.03 * span, p_text, ha="center", va="bottom")

    # Global test annotation
    if global_test and not np.isnan(global_p):
        test_name = "One-way ANOVA" if parametric else "Kruskal-Wallis"
        p_formatted = format_p_value(global_p)
        ax.text(
            positions[0],
            base + step * (len(pairwise) + 0.4),
            f"{test_name} p = {p_formatted}",
            fontsize=10,
            va="bottom",
        )  # Axis labels
    ax.set_xticks(positions)
    ax.set_xticklabels(levels)
    ax.set_xlabel(x_label or x)
    ax.set_ylabel(y_label or y)

    # Legend
    import matplotlib.patches as mpatches
    handles = [mpatches.Patch(color=color_palette[l], label=l) for l in levels]
    ax.legend(handles=handles, title=(x_label or x))

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(data_min - 0.05 * span, base + step * (len(pairwise) + 0.6))
    plt.tight_layout()
    return fig, ax
