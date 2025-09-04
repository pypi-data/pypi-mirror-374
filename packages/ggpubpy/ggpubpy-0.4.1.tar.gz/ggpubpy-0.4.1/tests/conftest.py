"""
Test configuration and fixtures for ggpubpy tests.
"""

from typing import Dict

import matplotlib
import numpy as np
import pandas as pd
import pytest

# Set matplotlib to use Agg backend for headless testing
matplotlib.use("Agg")


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Create sample test data similar to ToothGrowth dataset."""
    np.random.seed(42)  # For reproducible tests

    len_05 = [
        4.2,
        11.5,
        7.3,
        5.8,
        6.4,
        10,
        11.2,
        11.2,
        5.2,
        7,
        16.5,
        16.5,
        15.2,
        17.3,
        22.5,
        13.6,
        14.5,
        18.8,
        15.5,
        23.6,
    ]
    len_1 = [
        15.2,
        21.5,
        17.6,
        9.7,
        14.5,
        16.9,
        18.9,
        18.1,
        19.7,
        22.5,
        25.5,
        26.4,
        22.9,
        23.3,
        29.4,
        23.0,
        24.8,
        30.9,
        26.4,
        27.3,
    ]
    len_2 = [
        26.4,
        32.5,
        26.7,
        21.5,
        27.3,
        25.5,
        26.4,
        30.3,
        29.4,
        31.3,
        30.9,
        31.5,
        30.0,
        30.0,
        29.4,
        34.8,
        35.2,
        32.5,
        33.3,
        37.0,
    ]

    df = pd.DataFrame(
        {"dose": np.repeat([0.5, 1.0, 2.0], len(len_05)), "len": len_05 + len_1 + len_2}
    )

    return df


@pytest.fixture
def sample_palette() -> Dict[float, str]:
    """Create sample color palette."""
    return {0.5: "#00AFBB", 1.0: "#E7B800", 2.0: "#FC4E07"}


@pytest.fixture
def small_data() -> pd.DataFrame:
    """Create minimal test data for edge cases."""
    return pd.DataFrame({"group": ["A", "A", "B", "B"], "value": [1, 2, 3, 4]})


@pytest.fixture
def correlation_test_data() -> pd.DataFrame:
    """Create test data for correlation matrix tests."""
    np.random.seed(42)
    n = 100

    # Create variables with different correlation patterns
    x1 = np.random.normal(50, 10, n)
    x2 = 0.8 * x1 + np.random.normal(0, 5, n)  # Strong positive correlation
    x3 = 0.5 * x1 + np.random.normal(0, 8, n)  # Moderate positive correlation
    x4 = np.random.normal(30, 8, n)  # No correlation with others

    return pd.DataFrame(
        {"Variable_1": x1, "Variable_2": x2, "Variable_3": x3, "Variable_4": x4}
    )


@pytest.fixture
def correlation_data() -> pd.DataFrame:
    """Create alternative correlation test data."""
    np.random.seed(123)
    n = 50

    # Create simple correlated variables
    x1 = np.random.normal(0, 1, n)
    x2 = 0.7 * x1 + np.random.normal(0, 0.5, n)
    x3 = -0.4 * x1 + np.random.normal(0, 0.8, n)

    return pd.DataFrame({"X1": x1, "X2": x2, "X3": x3})
