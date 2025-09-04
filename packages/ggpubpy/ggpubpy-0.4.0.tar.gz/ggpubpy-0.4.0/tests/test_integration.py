"""
Integration tests for ggpubpy - Test all major functions work together.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

import ggpubpy
from ggpubpy.datasets import load_iris


class TestIntegration:
    """Integration tests for the complete ggpubpy package."""

    def test_import_all_functions(self) -> None:
        """Test that all main functions can be imported."""
        from ggpubpy import (
            plot_boxplot_with_stats,
            plot_correlation_matrix,
            plot_shift,
            plot_violin_with_stats,
            significance_stars,
        )

        # Test that functions are callable
        assert callable(plot_violin_with_stats)
        assert callable(plot_boxplot_with_stats)
        assert callable(plot_shift)
        assert callable(plot_correlation_matrix)
        assert callable(significance_stars)

    def test_iris_dataset_loading(self) -> None:
        """Test that the iris dataset loads correctly."""
        iris = load_iris()

        assert isinstance(iris, pd.DataFrame)
        assert iris.shape == (150, 5)
        assert list(iris.columns) == [
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
            "species",
        ]
        assert set(iris["species"].unique()) == {"setosa", "versicolor", "virginica"}

    def test_violin_plot_with_iris(self) -> None:
        """Test violin plot with iris dataset."""
        iris = load_iris()

        fig, ax = ggpubpy.plot_violin(
            df=iris,
            x="species",
            y="sepal_length",
            x_label="Species",
            y_label="Sepal Length (cm)",
        )

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        assert ax.get_xlabel() == "Species"
        assert ax.get_ylabel() == "Sepal Length (cm)"
        plt.close(fig)

    def test_boxplot_with_iris(self) -> None:
        """Test boxplot with iris dataset."""
        iris = load_iris()

        fig, ax = ggpubpy.plot_boxplot(
            df=iris, x="species", y="petal_length", parametric=True
        )

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        plt.close(fig)

    def test_correlation_matrix_with_iris(self) -> None:
        """Test correlation matrix with iris dataset."""
        iris = load_iris()
        numeric_cols = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

        fig, axes = ggpubpy.plot_correlation_matrix(
            iris,
            columns=numeric_cols,
            figsize=(8, 8),
            show_stats=True,
            method="pearson",
        )

        assert isinstance(fig, plt.Figure)
        assert isinstance(axes, np.ndarray)
        assert axes.shape == (4, 4)
        plt.close(fig)

    def test_shift_plot_with_iris(self) -> None:
        """Test shift plot with iris dataset."""
        iris = load_iris()
        iris_2groups = iris[iris["species"].isin(["setosa", "versicolor"])]

        x = iris_2groups[iris_2groups["species"] == "setosa"]["sepal_length"].values
        y = iris_2groups[iris_2groups["species"] == "versicolor"]["sepal_length"].values

        fig = ggpubpy.plot_shift(
            x,
            y,
            paired=False,
            n_boot=100,  # Reduced for faster testing
            show_quantiles=True,
            show_quantile_diff=False,
            x_name="Setosa",
            y_name="Versicolor",
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_significance_stars_function(self) -> None:
        """Test significance stars function."""
        assert ggpubpy.significance_stars(0.0001) == "****"
        assert ggpubpy.significance_stars(0.001) == "***"
        assert ggpubpy.significance_stars(0.01) == "**"
        assert ggpubpy.significance_stars(0.04) == "*"
        assert ggpubpy.significance_stars(0.1) == "ns"

    def test_default_palette_access(self) -> None:
        """Test that default palette is accessible."""
        palette = ggpubpy.DEFAULT_PALETTE

        assert isinstance(palette, list)
        assert len(palette) == 10
        assert all(color.startswith("#") for color in palette)

    def test_datasets_module(self) -> None:
        """Test datasets module functions."""
        # Test list_datasets
        datasets_info = ggpubpy.datasets.list_datasets()
        assert isinstance(datasets_info, dict)
        assert "iris" in datasets_info

        # Test get_iris_palette
        iris_palette = ggpubpy.datasets.get_iris_palette()
        assert isinstance(iris_palette, dict)
        assert len(iris_palette) == 3
        assert "setosa" in iris_palette
        assert "versicolor" in iris_palette
        assert "virginica" in iris_palette

    def test_parametric_vs_nonparametric(self) -> None:
        """Test that parametric and non-parametric modes work differently."""
        iris = load_iris()
        iris_2groups = iris[iris["species"].isin(["setosa", "versicolor"])]

        # Non-parametric (default)
        fig1, ax1 = ggpubpy.plot_violin(
            df=iris_2groups, x="species", y="sepal_length", parametric=False
        )

        # Parametric
        fig2, ax2 = ggpubpy.plot_violin(
            df=iris_2groups, x="species", y="sepal_length", parametric=True
        )

        # Both should work but may have different statistical test results
        assert isinstance(fig1, plt.Figure)
        assert isinstance(fig2, plt.Figure)

        plt.close(fig1)
        plt.close(fig2)

    def test_custom_palette_usage(self) -> None:
        """Test custom color palette usage."""
        iris = load_iris()
        custom_palette = {
            "setosa": "#FF6B6B",
            "versicolor": "#4ECDC4",
            "virginica": "#45B7D1",
        }

        fig, ax = ggpubpy.plot_violin(
            df=iris, x="species", y="petal_width", palette=custom_palette
        )

        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_correlation_matrix_methods(self) -> None:
        """Test different correlation methods."""
        iris = load_iris()
        numeric_cols = ["sepal_length", "sepal_width", "petal_length"]

        for method in ["pearson", "spearman", "kendall"]:
            fig, axes = ggpubpy.plot_correlation_matrix(
                iris, columns=numeric_cols, method=method, figsize=(6, 6)
            )

            assert isinstance(fig, plt.Figure)
            assert axes.shape == (3, 3)
            plt.close(fig)

    def test_edge_cases(self) -> None:
        """Test various edge cases."""
        iris = load_iris()

        # Single species (edge case)
        setosa_only = iris[iris["species"] == "setosa"]
        fig, ax = ggpubpy.plot_violin(df=setosa_only, x="species", y="sepal_length")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

        # Two species
        two_species = iris[iris["species"].isin(["setosa", "versicolor"])]
        fig, ax = ggpubpy.plot_boxplot(df=two_species, x="species", y="petal_length")
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_missing_values_handling(self) -> None:
        """Test that functions handle missing values gracefully."""
        # Create data with missing values
        data_with_nan = pd.DataFrame(
            {
                "group": ["A", "A", "B", "B", "A", "B"],
                "value": [1.0, 2.0, np.nan, 4.0, 5.0, np.nan],
            }
        )

        fig, ax = ggpubpy.plot_violin(df=data_with_nan, x="group", y="value")

        assert isinstance(fig, plt.Figure)
        plt.close(fig)
