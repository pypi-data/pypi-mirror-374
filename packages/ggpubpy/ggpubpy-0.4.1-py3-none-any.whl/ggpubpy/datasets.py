"""
Built-in datasets for ggpubpy examples and testing.

This module provides easy access to commonly used datasets for demonstration
and testing purposes.
"""

import os
from typing import Any, Dict

import pandas as pd


def _get_data_path() -> str:
    """Get the path to the data directory."""
    return os.path.join(os.path.dirname(__file__), "data")


def load_iris() -> pd.DataFrame:
    """
    Load the famous iris dataset.

    The iris dataset contains measurements of sepal and petal dimensions
    for three species of iris flowers (setosa, versicolor, virginica).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: sepal_length, sepal_width, petal_length,
        petal_width, species.

    Examples
    --------
    >>> from ggpubpy.datasets import load_iris
    >>> iris = load_iris()
    >>> iris.head()
    """
    data_path = _get_data_path()
    iris_path = os.path.join(data_path, "iris.csv")
    return pd.read_csv(iris_path)


def load_titanic() -> pd.DataFrame:
    """
    Load the famous Titanic dataset.

    The Titanic dataset contains information about passengers aboard the RMS Titanic,
    including survival status, passenger class, age, gender, and other details.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: PassengerId, Survived, Pclass, Name, Sex, Age,
        SibSp, Parch, Ticket, Fare, Cabin, Embarked.

    Examples
    --------
    >>> from ggpubpy.datasets import load_titanic
    >>> titanic = load_titanic()
    >>> titanic.head()
    """
    data_path = _get_data_path()
    titanic_path = os.path.join(data_path, "titanic.csv")
    return pd.read_csv(titanic_path)


def get_iris_palette() -> Dict[str, str]:
    """
    Get the default color palette for iris species.

    Returns
    -------
    dict
        Dictionary mapping species names to hex colors.
          Examples
    --------
    >>> from ggpubpy.datasets import get_iris_palette
    >>> palette = get_iris_palette()
    >>> print(palette)
    {'setosa': '#00AFBB', 'versicolor': '#E7B800', 'virginica': '#FC4E07'}
    """
    return {"setosa": "#00AFBB", "versicolor": "#E7B800", "virginica": "#FC4E07"}


def get_titanic_palette() -> Dict[str, Dict[str, str]]:
    """
    Get the default color palette for Titanic dataset categories.

    Returns
    -------
    dict
        Dictionary mapping category names to hex colors.

    Examples
    --------
    >>> from ggpubpy.datasets import get_titanic_palette
    >>> palette = get_titanic_palette()
    >>> print(palette)
    {'Survived': {'0': '#E74C3C', '1': '#2ECC71'}, 'Pclass': {'1': '#F39C12', '2': '#3498DB', '3': '#9B59B6'}, 'Sex': {'male': '#3498DB', 'female': '#E91E63'}}
    """
    return {
        "Survived": {
            "0": "#E74C3C",
            "1": "#2ECC71",
        },  # Red for died, Green for survived
        "Pclass": {
            "1": "#F39C12",
            "2": "#3498DB",
            "3": "#9B59B6",
        },  # Orange, Blue, Purple
        "Sex": {
            "male": "#3498DB",
            "female": "#E91E63",
        },  # Blue for male, Pink for female
        "Embarked": {
            "C": "#E74C3C",
            "Q": "#F39C12",
            "S": "#2ECC71",
        },  # Red, Orange, Green
    }


def list_datasets() -> Dict[str, Any]:
    """
    List all available datasets with descriptions.

    Returns
    -------
    dict
        Dictionary with dataset names as keys and descriptions as values.
    """
    return {
        "iris": {
            "description": "The famous iris flower dataset with sepal/petal measurements",
            "shape": (150, 5),
            "columns": [
                "sepal_length",
                "sepal_width",
                "petal_length",
                "petal_width",
                "species",
            ],
            "loader": load_iris,
        },
        "titanic": {
            "description": "The famous Titanic passenger dataset with survival information",
            "shape": (891, 12),
            "columns": [
                "PassengerId",
                "Survived",
                "Pclass",
                "Name",
                "Sex",
                "Age",
                "SibSp",
                "Parch",
                "Ticket",
                "Fare",
                "Cabin",
                "Embarked",
            ],
            "loader": load_titanic,
        },
    }
