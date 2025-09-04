"""
Shift plot functionality for ggpubpy.

This module contains the shift plot function for comparing distributions.
"""

from typing import List, Optional, Tuple, Union, cast

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection
from scipy.stats import mannwhitneyu, ttest_ind

from .helper import _bias_corrected_ci, format_p_value, harrelldavis


def plot_shift(
    x: np.ndarray,
    y: np.ndarray,
    *,
    paired: bool = False,
    n_boot: int = 1000,
    percentiles: np.ndarray = np.arange(10, 100, 10),
    confidence: float = 0.95,
    seed: Optional[int] = None,
    show_median: bool = True,
    violin: bool = True,
    show_quantiles: bool = False,
    show_quantile_diff: bool = False,
    parametric: bool = False,
    x_name: str = "X",
    y_name: str = "Y",
) -> plt.Figure:
    """Shift plot.

    Parameters
    ----------
    x, y : array_like
        First and second set of observations.
    paired : bool
        If True, x and y are paired samples.
    n_boot : int
        Number of bootstrap iterations.
    percentiles : array_like
        Sequence of percentiles (0-100) to compute.
    confidence : float
        Confidence level for intervals.
    seed : int or None
        Random seed.
    show_median : bool
        If True, show median lines.    violin : bool
        If True, plot half-violin densities.
    show_quantiles : bool
        If True, show quantile connection lines between distributions.
    show_quantile_diff : bool
        If True, show bottom subplot with quantile differences.
    parametric : bool
        If True, use t-test; else Mann-Whitney U test.

    Returns
    -------
    fig : matplotlib Figure instance
    """
    # Safety checks
    x = np.asarray(x)
    y = np.asarray(y)
    pct = np.asarray(percentiles) / 100
    assert x.ndim == 1 and y.ndim == 1, "x and y must be 1D."
    assert (
        not np.isnan(x).any() and not np.isnan(y).any()
    ), "Missing values not allowed."
    nx, ny = x.size, y.size
    assert nx >= 10 and ny >= 10, "Each sample must have at least 10 observations."
    assert 0 < confidence < 1, "confidence must be between 0 and 1."
    if paired:
        assert (
            nx == ny
        ), "x and y must have same size when paired=True."  # Harrell-Davis quantiles
    x_per: np.ndarray = harrelldavis(x, pct)
    y_per: np.ndarray = harrelldavis(y, pct)
    delta: np.ndarray = y_per - x_per

    # Statistical test for comparison
    if parametric:
        if paired:
            from scipy.stats import ttest_rel

            stat, p_val = ttest_rel(x, y)
            test_name = "Paired t-test"
        else:
            stat, p_val = ttest_ind(x, y)
            test_name = "Independent t-test"
    else:
        if paired:
            from scipy.stats import wilcoxon

            stat, p_val = wilcoxon(x, y)
            test_name = "Wilcoxon signed-rank"
        else:
            stat, p_val = mannwhitneyu(x, y, alternative="two-sided")
            test_name = "Mann-Whitney U"

    # Bootstrap differences
    rng = np.random.default_rng(seed)
    if paired:
        bootsam = rng.choice(nx, size=(nx, n_boot), replace=True)
        x_boot_q = np.array(
            [harrelldavis(x[bootsam[:, i]], pct) for i in range(n_boot)]
        ).T
        y_boot_q = np.array(
            [harrelldavis(y[bootsam[:, i]], pct) for i in range(n_boot)]
        ).T
        bootstat = y_boot_q - x_boot_q
    else:
        x_boot_q = np.array(
            [harrelldavis(rng.choice(x, nx), pct) for _ in range(n_boot)]
        ).T
        y_boot_q = np.array(
            [harrelldavis(rng.choice(y, ny), pct) for _ in range(n_boot)]
        ).T
        bootstat = y_boot_q - x_boot_q

    # Confidence intervals
    lowers_list: List[float] = []
    medians_list: List[float] = []
    uppers_list: List[float] = []
    for i, d in enumerate(delta):
        ci = _bias_corrected_ci(bootstat[i], d, alpha=1 - confidence)
        ci_low, ci_high = ci[0], ci[1]
        med_val_ci = _bias_corrected_ci(bootstat[i], d, alpha=1)
        med_val = med_val_ci[0]
        lowers_list.append(float(ci_low))
        uppers_list.append(float(ci_high))
        medians_list.append(float(med_val))
    lowers = np.array(lowers_list)
    medians = np.array(medians_list)
    uppers = np.array(uppers_list)  # Prepare data for stripplot
    data = pd.DataFrame(
        {"value": np.concatenate([x, y]), "variable": ["X"] * nx + ["Y"] * ny}
    )  # Plot distributions
    if show_quantile_diff:
        fig = plt.figure(figsize=(10, 6))
        ax1 = plt.subplot2grid((3, 3), (0, 0), rowspan=2, colspan=3)
    else:
        fig, ax1 = plt.subplots(figsize=(10, 4))  # Custom boxplots

    def adj_vals(vals: np.ndarray) -> Tuple[float, float, float, float, float]:
        percentiles_arr = cast(np.ndarray, np.percentile(vals, [25, 50, 75]))
        q1, med, q3 = percentiles_arr[0], percentiles_arr[1], percentiles_arr[2]
        iqr = q3 - q1
        lower = np.clip(q1 - 1.5 * iqr, vals.min(), q1)
        upper = np.clip(q3 + 1.5 * iqr, q3, vals.max())
        return float(q1), float(med), float(q3), float(lower), float(upper)

    for arr, y0 in zip([x, y], [1.2, -0.2]):
        q1, med, q3, lo, hi = adj_vals(np.sort(arr))
        ax1.plot(med, y0, "o", color="white", zorder=10)
        ax1.hlines(y0, q1, q3, color="k", lw=7, zorder=9)
        ax1.hlines(y0, lo, hi, color="k", lw=2, zorder=9)

    # Scatter raw data points without jitter
    ax1.scatter(x, np.full_like(x, 1.2), color="#cfcfcf", s=10, alpha=0.6, zorder=3)
    ax1.scatter(y, np.full_like(y, -0.2), color="#88bedc", s=10, alpha=0.6, zorder=3)

    if violin:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", PendingDeprecationWarning)
            vl = ax1.violinplot([y, x], showextrema=False, vert=False, widths=1)
        bodies = cast(List[PolyCollection], vl["bodies"])
        for idx, color, offset in zip([0, 1], ["#88bedc", "#cfcfcf"], [-1.2, -0.8]):
            path = bodies[idx].get_paths()[0]
            verts: np.ndarray = cast(np.ndarray, path.vertices)
            if idx == 0:
                verts[:, 1][verts[:, 1] >= 1] = 1
            else:
                verts[:, 1][verts[:, 1] <= 2] = 2
            verts[:, 1] += offset
            bodies[idx].set_edgecolor("k")
            bodies[idx].set_facecolor(color)
            bodies[idx].set_alpha(0.8)
        if show_quantile_diff:
            ax1.set_ylim(2.2, -1.2)
        else:
            ax1.set_ylim(1.8, -0.8)  # Connect quantiles (optional)
    if show_quantiles:
        for i in range(len(pct)):
            col = (
                "#4c72b0"
                if uppers[i] < 0
                else ("#c34e52" if lowers[i] > 0 else "darkgray")
            )
            plt.plot([y_per[i], x_per[i]], [0.2, 0.8], "o-", color=col, zorder=10)
            plt.plot([x_per[i]] * 2, [0.8, 1.2], "k--", zorder=9)
            plt.plot([y_per[i]] * 2, [-0.2, 0.2], "k--", zorder=9)

    if show_median:
        m_x, m_y = np.median(x), np.median(y)
        plt.plot([m_x] * 2, [0.8, 1.2], "k-")
        plt.plot([m_y] * 2, [-0.2, 0.2], "k-")

    plt.xlabel("Scores (a.u.)", size=15)
    ax1.set_yticks([1.2, -0.2])
    ax1.set_yticklabels([x_name, y_name], size=15)
    ax1.set_ylabel("")

    # Add statistical test result to title
    p_formatted = format_p_value(p_val)
    plt.title(f"{test_name}: p = {p_formatted}", fontsize=12, pad=10)

    # Quantile shift plot (optional)
    if show_quantile_diff:
        ax2 = plt.subplot2grid((3, 3), (2, 0), colspan=3)
        for i, per in enumerate(x_per):
            col = (
                "#4c72b0"
                if uppers[i] < 0
                else ("#c34e52" if lowers[i] > 0 else "darkgray")
            )
            ax2.plot([per] * 2, [uppers[i], lowers[i]], lw=3, color=col, zorder=10)
            ax2.plot(per, medians[i], "o", ms=10, color=col, zorder=10)
        ax2.axhline(0, ls="--", lw=2, color="gray")
        ax2.set_xlabel(f"{x_name} quantiles", size=15)
        ax2.set_ylabel(f"{y_name} - {x_name} quantiles\ndifferences (a.u.)", size=10)

    plt.tight_layout()
    return fig
