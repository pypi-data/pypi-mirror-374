"""
Alluvial plot functionality for ggpubpy.

This module contains the alluvial plot function for creating flow diagrams
similar to ggalluvial in R.
"""

from typing import Dict, List, Optional, Tuple, Union

import matplotlib.patches as mpatches
import matplotlib.path as mpath
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure


def plot_alluvial(
    df: pd.DataFrame,
    dims: List[str],
    value_col: str,
    color_by: str,
    id_col: str,
    *,
    orders: Optional[Dict[str, List[str]]] = None,
    color_map: Optional[Dict[str, str]] = None,
    title: str = "",
    subtitle: str = "",
    figsize: Tuple[int, int] = (9, 6),
    alpha: float = 0.8,
    x_label: str = "Demographic",
    y_label: str = "Frequency",
) -> Tuple[Figure, Axes]:
    """
    Create an alluvial (flow) diagram with explicit alluvium IDs.

    This function creates a flow diagram similar to ggalluvial in R, where
    each unique value of `id_col` represents one flow (alluvium) between
    categorical dimensions.

    Parameters
    ----------
    df : pd.DataFrame
        Input data containing the dimensions, values, and identifiers.
    dims : List[str]
        List of column names representing the dimensions (axes) of the flow.
    value_col : str
        Column name containing the frequency/weight values for each flow.
    color_by : str
        Column name to use for coloring the flows.
    id_col : str
        Column name containing unique identifiers for each flow (alluvium).
    orders : Dict[str, List[str]], optional
        Dictionary mapping dimension names to ordered lists of category values.
        If not provided, categories will be ordered by their appearance in data.
    color_map : Dict[str, str], optional
        Dictionary mapping category values to colors. If not provided,
        a default palette will be used.
    title : str, default ""
        Main title for the plot.
    subtitle : str, default ""
        Subtitle for the plot.
    figsize : Tuple[int, int], default (9, 6)
        Figure size in inches.
    alpha : float, default 0.8
        Transparency level for the flow polygons.
    x_label : str, default "Demographic"
        Label for the x-axis.
    y_label : str, default "Frequency"
        Label for the y-axis.

    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes objects.

    Examples
    --------
    >>> from ggpubpy import load_titanic
    >>> import pandas as pd
    >>> import numpy as np
    >>>
    >>> # Load and prepare Titanic data
    >>> titanic = load_titanic()
    >>> titanic = titanic.dropna(subset=["Age"])
    >>> titanic["Class"] = titanic["Pclass"].map({1: "1st", 2: "2nd", 3: "3rd"})
    >>> titanic["AgeCat"] = np.where(titanic["Age"] < 18, "Child", "Adult")
    >>> titanic["Survived"] = titanic["Survived"].astype(str).replace({"0": "No", "1": "Yes"})
    >>>
    >>> # Create frequency table with alluvium IDs
    >>> titanic_tab = (titanic.groupby(["Class", "Sex", "AgeCat", "Survived"])
    ...                    .size()
    ...                    .reset_index(name="Freq")
    ...                    .rename(columns={"AgeCat": "Age"}))
    >>> titanic_tab["alluvium"] = titanic_tab.index
    >>>
    >>> # Create alluvial plot
    >>> fig, ax = plot_alluvial(
    ...     titanic_tab,
    ...     dims=["Class", "Sex", "Age"],
    ...     value_col="Freq",
    ...     color_by="Survived",
    ...     id_col="alluvium",
    ...     orders={"Class": ["1st", "2nd", "3rd"],
    ...             "Sex": ["male", "female"],
    ...             "Age": ["Child", "Adult"]},
    ...     color_map={"No": "#F17C7E", "Yes": "#6CCECB"},
    ...     title="Titanic Survival Analysis",
    ...     subtitle="Class → Sex → Age",
    ...     alpha=0.7
    ... )
    >>> plt.show()
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    if not isinstance(dims, list) or len(dims) < 2:
        raise ValueError("dims must be a list with at least 2 elements")

    for col in dims + [value_col, color_by, id_col]:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame")

    if df[value_col].dtype not in [np.int64, np.float64]:
        raise ValueError(f"Column '{value_col}' must be numeric")

    # Calculate x positions for each dimension
    x_positions = {d: i for i, d in enumerate(dims)}

    def bezier_curve(
        x0: float, y0: float, x1: float, y1: float, n: int = 40
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create a Bézier curve between two points."""
        dx = x1 - x0
        c1x, c1y = x0 + 0.5 * dx, y0
        c2x, c2y = x1 - 0.5 * dx, y1
        t = np.linspace(0, 1, n)
        x = (
            (1 - t) ** 3 * x0
            + 3 * (1 - t) ** 2 * t * c1x
            + 3 * (1 - t) * t**2 * c2x
            + t**3 * x1
        )
        y = (
            (1 - t) ** 3 * y0
            + 3 * (1 - t) ** 2 * t * c1y
            + 3 * (1 - t) * t**2 * c2y
            + t**3 * y1
        )
        return x, y

    # Calculate total height
    H = df[value_col].sum()

    # Calculate positions for each alluvium at each dimension
    positions: dict[str, dict[str, tuple[float, float]]] = {axis: {} for axis in dims}
    for axis in dims:
        cats = orders[axis] if orders and axis in orders else sorted(df[axis].unique())
        y_cursor = 0.0
        for cat in cats:
            sub_df = df[df[axis] == cat]
            sub = sub_df.sort_values(by=[color_by, id_col])
            for _, row in sub.iterrows():
                aid = row[id_col]
                h = float(row[value_col])
                positions[axis][aid] = (y_cursor, y_cursor + h)
                y_cursor += h

    # Generate color map if not provided
    if not color_map:
        uniq = df[color_by].unique()
        palette = [
            "#F17C7E",
            "#6CCECB",
            "#FFD700",
            "#9370DB",
            "#87CEEB",
            "#FFA07A",
            "#98FB98",
            "#F0E68C",
        ]
        color_map = {u: palette[i % len(palette)] for i, u in enumerate(uniq)}

    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)

    # Draw flow polygons
    for aid, g in df.groupby(id_col):
        c = color_map.get(g[color_by].iloc[0], "gray")
        for a, b in zip(dims[:-1], dims[1:]):
            x0, x1 = x_positions[a], x_positions[b]
            y0b, y0t = positions[a][aid]
            y1b, y1t = positions[b][aid]

            # Create Bézier curves for top and bottom of flow
            xt, yt = bezier_curve(x0, y0t, x1, y1t)
            xb, yb = bezier_curve(x0, y0b, x1, y1b)

            # Combine curves to form polygon
            xs = np.concatenate([xt, xb[::-1]])
            ys = np.concatenate([yt, yb[::-1]])
            codes = [mpath.Path.MOVETO] + [mpath.Path.LINETO] * (len(xs) - 1)

            patch = mpatches.PathPatch(
                mpath.Path(list(zip(xs, ys)), codes),
                facecolor=c,
                edgecolor="none",
                alpha=alpha,
            )
            ax.add_patch(patch)

    # Draw dimension rectangles and labels
    width = 0.18
    for axis in dims:
        cats = orders[axis] if orders and axis in orders else sorted(df[axis].unique())
        y_cursor = 0.0
        for cat in cats:
            h = float(df.loc[df[axis] == cat, value_col].sum())
            rect = mpatches.Rectangle(
                (x_positions[axis] - width / 2, y_cursor),
                width,
                h,
                facecolor="white",
                edgecolor="black",
                zorder=10,
            )
            ax.add_patch(rect)
            ax.text(
                x_positions[axis],
                y_cursor + h / 2,
                cat,
                ha="center",
                va="center",
                fontsize=9,
                zorder=11,
            )
            y_cursor += h

    # Set axis properties
    ax.set_xlim(-0.5, len(dims) - 0.5)
    ax.set_ylim(0, H)
    ax.set_xticks([x_positions[d] for d in dims])
    ax.set_xticklabels(dims)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    # Add title
    if title or subtitle:
        full_title = f"{title}\n{subtitle}" if subtitle else title
        ax.set_title(full_title, loc="left", fontsize=12)

    # Add legend
    handles = [
        mpatches.Patch(facecolor=color_map[k], edgecolor="none", label=k)
        for k in color_map
    ]
    ax.legend(handles=handles, title=color_by, frameon=False, loc="upper right")

    # Clean up spines
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.grid(False)

    plt.tight_layout()
    return fig, ax


def plot_alluvial_with_stats(
    df: pd.DataFrame,
    dims: List[str],
    value_col: str,
    color_by: str,
    id_col: str,
    *,
    orders: Optional[Dict[str, List[str]]] = None,
    color_map: Optional[Dict[str, str]] = None,
    title: str = "",
    subtitle: str = "",
    figsize: Tuple[int, int] = (9, 6),
    alpha: float = 0.8,
    x_label: str = "Demographic",
    y_label: str = "Frequency",
    add_stats: bool = True,
) -> Tuple[Figure, Axes]:
    """
    Create an alluvial plot with optional statistical annotations.

    This is a wrapper around plot_alluvial that can add statistical information
    to the plot. Currently, this function is identical to plot_alluvial, but
    provides a consistent interface for future statistical enhancements.

    Parameters
    ----------
    df : pd.DataFrame
        Input data containing the dimensions, values, and identifiers.
    dims : List[str]
        List of column names representing the dimensions (axes) of the flow.
    value_col : str
        Column name containing the frequency/weight values for each flow.
    color_by : str
        Column name to use for coloring the flows.
    id_col : str
        Column name containing unique identifiers for each flow (alluvium).
    orders : Dict[str, List[str]], optional
        Dictionary mapping dimension names to ordered lists of category values.
    color_map : Dict[str, str], optional
        Dictionary mapping category values to colors.
    title : str, default ""
        Main title for the plot.
    subtitle : str, default ""
        Subtitle for the plot.
    figsize : Tuple[int, int], default (9, 6)
        Figure size in inches.
    alpha : float, default 0.8
        Transparency level for the flow polygons.
    x_label : str, default "Demographic"
        Label for the x-axis.
    y_label : str, default "Frequency"
        Label for the y-axis.
    add_stats : bool, default True
        Whether to add statistical annotations (currently not implemented).

    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        Matplotlib figure and axes objects.
    """
    return plot_alluvial(
        df=df,
        dims=dims,
        value_col=value_col,
        color_by=color_by,
        id_col=id_col,
        orders=orders,
        color_map=color_map,
        title=title,
        subtitle=subtitle,
        figsize=figsize,
        alpha=alpha,
        x_label=x_label,
        y_label=y_label,
    )
