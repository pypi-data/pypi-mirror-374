"""
Examples for alluvial plots in ggpubpy.

This file demonstrates how to create alluvial (flow) diagrams using the
ggpubpy alluvial plot functions.
"""

import os
import sys
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add parent directory to path to import ggpubpy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ggpubpy import load_iris, load_titanic, plot_alluvial


def titanic_example() -> tuple[Any, Any]:
    """Example using Titanic dataset."""
    print("Creating Titanic alluvial plot...")

    # Load Titanic data
    titanic = load_titanic()

    # Prepare data: remove missing ages and create categories
    titanic = titanic.dropna(subset=["Age"])
    titanic["Class"] = titanic["Pclass"].map({1: "1st", 2: "2nd", 3: "3rd"})
    titanic["AgeCat"] = np.where(titanic["Age"] < 18, "Child", "Adult")
    titanic["Survived"] = (
        titanic["Survived"].astype(str).replace({"0": "No", "1": "Yes"})
    )

    # Create frequency table with alluvium IDs
    titanic_tab = (
        titanic.groupby(["Class", "Sex", "AgeCat", "Survived"])
        .size()
        .reset_index(name="Freq")
        .rename(columns={"AgeCat": "Age"})
    )
    titanic_tab["alluvium"] = titanic_tab.index

    # Create alluvial plot
    fig, ax = plot_alluvial(
        titanic_tab,
        dims=["Class", "Sex", "Age"],
        value_col="Freq",
        color_by="Survived",
        id_col="alluvium",
        orders={
            "Class": ["1st", "2nd", "3rd"],
            "Sex": ["male", "female"],
            "Age": ["Child", "Adult"],
        },
        color_map={"No": "#F17C7E", "Yes": "#6CCECB"},
        title="Titanic Survival Analysis",
        subtitle="Class → Sex → Age",
        alpha=0.7,
    )

    plt.show()
    return fig, ax


def iris_example() -> tuple[Any, Any]:
    """Example using Iris dataset."""
    print("Creating Iris alluvial plot...")

    # Load Iris data
    iris = load_iris()

    # Create categorical variables from continuous ones
    iris["SepalLenCat"] = pd.cut(
        iris["sepal_length"], bins=3, labels=["Short", "Medium", "Long"]
    )
    iris["PetalLenCat"] = pd.cut(
        iris["petal_length"], bins=3, labels=["Short", "Medium", "Long"]
    )

    # Create frequency table with alluvium IDs
    iris_tab = (
        iris.groupby(["SepalLenCat", "PetalLenCat", "species"], observed=True)
        .size()
        .reset_index(name="Freq")
    )
    iris_tab["alluvium"] = iris_tab.index

    # Create alluvial plot
    fig, ax = plot_alluvial(
        iris_tab,
        dims=["SepalLenCat", "PetalLenCat"],
        value_col="Freq",
        color_by="species",
        id_col="alluvium",
        orders={
            "SepalLenCat": ["Short", "Medium", "Long"],
            "PetalLenCat": ["Short", "Medium", "Long"],
        },
        title="Iris Dataset Analysis",
        subtitle="Sepal length → Petal length",
        alpha=0.7,
    )

    plt.show()
    return fig, ax


def custom_example() -> tuple[Any, Any]:
    """Example with custom data."""
    print("Creating custom alluvial plot...")

    # Create custom data
    data = {
        "Department": [
            "Sales",
            "Sales",
            "Sales",
            "Marketing",
            "Marketing",
            "Marketing",
            "IT",
            "IT",
            "IT",
        ],
        "Experience": [
            "Junior",
            "Mid",
            "Senior",
            "Junior",
            "Mid",
            "Senior",
            "Junior",
            "Mid",
            "Senior",
        ],
        "Performance": [
            "Low",
            "High",
            "High",
            "Low",
            "High",
            "High",
            "Low",
            "High",
            "High",
        ],
        "Count": [10, 15, 8, 5, 12, 6, 3, 8, 4],
    }

    df = pd.DataFrame(data)
    df["alluvium"] = df.index

    # Create alluvial plot
    fig, ax = plot_alluvial(
        df,
        dims=["Department", "Experience"],
        value_col="Count",
        color_by="Performance",
        id_col="alluvium",
        orders={
            "Department": ["Sales", "Marketing", "IT"],
            "Experience": ["Junior", "Mid", "Senior"],
        },
        color_map={"Low": "#FF6B6B", "High": "#4ECDC4"},
        title="Employee Performance Analysis",
        subtitle="Department → Experience Level",
        alpha=0.8,
        figsize=(8, 5),
    )

    plt.show()
    return fig, ax


if __name__ == "__main__":
    # Run all examples
    print("Running alluvial plot examples...")
    print("=" * 50)

    # Titanic example
    titanic_example()

    print("\n" + "=" * 50)

    # Iris example
    iris_example()

    print("\n" + "=" * 50)

    # Custom example
    custom_example()

    print("\nAll examples completed!")
