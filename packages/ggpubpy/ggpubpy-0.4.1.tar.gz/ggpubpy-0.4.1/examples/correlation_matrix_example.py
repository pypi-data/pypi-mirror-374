#!/usr/bin/env python3
"""
Example script demonstrating the correlation matrix plot functionality.
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add parent directory to path to import ggpubpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ggpubpy import load_iris, plot_correlation_matrix


def create_sample_data() -> pd.DataFrame:
    """Create sample data with different correlation patterns."""
    np.random.seed(42)
    n = 150

    # Create variables with different correlation patterns
    x1 = np.random.normal(50, 10, n)
    x2 = 0.8 * x1 + np.random.normal(0, 5, n)  # Strong positive correlation
    x3 = 0.9 * x1 + np.random.normal(0, 3, n)  # Very strong positive correlation
    x4 = np.random.normal(30, 8, n)  # No correlation with others

    df = pd.DataFrame(
        {"Variable_1": x1, "Variable_2": x2, "Variable_3": x3, "Variable_4": x4}
    )

    return df


def main() -> None:
    """Run correlation matrix plot examples."""
    print("Creating correlation matrix plot examples...")

    # Example 1: Using synthetic data
    print("\n1. Synthetic data example...")
    df_synthetic = create_sample_data()

    fig1, axes1 = plot_correlation_matrix(
        df_synthetic,
        figsize=(8, 8),
        color="#2E86AB",
        alpha=0.6,
        point_size=25,
        show_stats=True,
        method="pearson",
        title="Synthetic Data Correlation Matrix",
    )

    plt.savefig(
        "correlation_matrix_synthetic_example.png", dpi=300, bbox_inches="tight"
    )
    plt.show()

    # Example 2: Using iris dataset - 3 features
    print("\n2. Iris dataset - 3 features example...")
    iris_df = load_iris()
    features_3 = ["sepal_length", "sepal_width", "petal_length"]

    fig2, axes2 = plot_correlation_matrix(
        iris_df,
        columns=features_3,
        figsize=(8, 8),
        color="#3498DB",
        alpha=0.7,
        point_size=25,
        show_stats=True,
        method="pearson",
        title="Iris Dataset - 3 Features Correlation Matrix",
    )

    plt.savefig("correlation_matrix_iris_3features.png", dpi=300, bbox_inches="tight")
    plt.show()

    # Example 3: Using iris dataset - All 4 features
    print("\n3. Iris dataset - All features example...")
    features_4 = ["sepal_length", "sepal_width", "petal_length", "petal_width"]

    fig3, axes3 = plot_correlation_matrix(
        iris_df,
        columns=features_4,
        figsize=(10, 10),
        color="#27AE60",
        alpha=0.6,
        point_size=20,
        show_stats=True,
        method="spearman",
        title="Iris Dataset - All Features Spearman Correlation",
    )

    plt.savefig("correlation_matrix_iris_4features.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("\nCorrelation matrix plots saved successfully!")
    print("Files created:")
    print("- correlation_matrix_synthetic_example.png")
    print("- correlation_matrix_iris_3features.png")
    print("- correlation_matrix_iris_4features.png")


if __name__ == "__main__":
    main()
