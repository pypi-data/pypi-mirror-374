#!/usr/bin/env python3
"""
Basic usage examples for ggpubpy.

This script demonstrates the core functionality of ggpubpy using the built-in iris dataset.
"""

import os
import sys

# Add the parent directory to sys.path to import ggpubpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt

import ggpubpy


def main() -> None:
    """Run basic usage examples."""
    # Load the iris dataset
    iris = ggpubpy.datasets.load_iris()

    print("ggpubpy Basic Usage Examples")
    print("=" * 40)
    print(f"Loaded iris dataset with {len(iris)} rows")
    print(f"Columns: {list(iris.columns)}")
    print(f"Species: {iris['species'].unique()}")
    print()  # Example 1: Violin plot with 3 groups (all species)
    print("1. Generating violin plot (3 species)...")
    fig, ax = ggpubpy.plot_violin(
        df=iris,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        parametric=False,  # Use non-parametric tests
    )
    plt.suptitle("Iris Dataset: Sepal Length by Species (Violin Plot)", y=1.02)
    plt.tight_layout()
    plt.savefig("violin_3groups_example.png", dpi=150, bbox_inches="tight")
    plt.show()

    # Example 2: Box plot with 3 groups (all species)
    print("2. Generating box plot (3 species)...")
    fig, ax = ggpubpy.plot_boxplot(
        df=iris,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        parametric=False,  # Use non-parametric tests
    )
    plt.suptitle("Iris Dataset: Sepal Length by Species (Box Plot)", y=1.02)
    plt.tight_layout()
    plt.savefig("boxplot_3groups_example.png", dpi=150, bbox_inches="tight")
    plt.show()
    # Example 3: Violin plot with 2 groups (setosa vs versicolor)
    print("3. Generating violin plot (2 species: setosa vs versicolor)...")
    iris_2groups = iris[iris["species"].isin(["setosa", "versicolor"])]

    fig, ax = ggpubpy.plot_violin(
        df=iris_2groups,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        parametric=False,  # Use non-parametric tests
    )
    plt.suptitle(
        "Iris Dataset: Setosa vs Versicolor Sepal Length (Violin Plot)", y=1.02
    )
    plt.tight_layout()
    plt.savefig("violin_2groups_example.png", dpi=150, bbox_inches="tight")
    plt.show()

    # Example 4: Box plot with 2 groups (setosa vs versicolor)
    print("4. Generating box plot (2 species: setosa vs versicolor)...")
    fig, ax = ggpubpy.plot_boxplot(
        df=iris_2groups,
        x="species",
        y="sepal_length",
        x_label="Species",
        y_label="Sepal Length (cm)",
        parametric=False,  # Use non-parametric tests
    )
    plt.suptitle("Iris Dataset: Setosa vs Versicolor Sepal Length (Box Plot)", y=1.02)
    plt.tight_layout()
    plt.savefig("boxplot_2groups_example.png", dpi=150, bbox_inches="tight")
    plt.show()  # Example 5: Custom color palette
    # Example 6: Shift plot with 2 groups (setosa vs versicolor)
    print("6. Generating shift plot (2 species: setosa vs versicolor)...")
    x = iris_2groups[iris_2groups["species"] == "setosa"]["sepal_length"].values
    y = iris_2groups[iris_2groups["species"] == "versicolor"]["sepal_length"].values
    fig = ggpubpy.plot_shift(
        x, y, paired=False, n_boot=500, percentiles=[10, 50, 90], violin=True
    )
    plt.suptitle("Iris Shift Plot: Sepal Length Difference Quantiles", y=1.02)
    plt.tight_layout()
    plt.savefig("shift_plot_example_basic.png", dpi=150, bbox_inches="tight")
    plt.show()

    print("\nExamples completed! Check the generated PNG files.")
    print("Available datasets:")
    print(f"  - {ggpubpy.datasets.list_datasets()}")


if __name__ == "__main__":
    main()
