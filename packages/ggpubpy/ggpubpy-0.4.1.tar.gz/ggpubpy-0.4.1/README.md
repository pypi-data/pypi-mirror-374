# ggpubpy

[![Documentation Status](https://readthedocs.org/projects/ggpubpy/badge/?version=latest)](https://ggpubpy.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/ggpubpy.svg)](https://badge.fury.io/py/ggpubpy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**ggpubpy** is a Python library for creating publication-ready plots with built-in statistical tests and automatic p-value annotations. Inspired by R's ggpubr package, ggpubpy provides easy-to-use functions for creating professional visualizations suitable for scientific publications.

## Features

- 📊 **Publication-ready plots**: Clean, professional appearance suitable for scientific publications
- 🔬 **Built-in statistical tests**: Automatic ANOVA, t-tests, correlation analysis, and more
- ⭐ **Automatic annotations**: P-values and significance stars added automatically
- 🎨 **Flexible customization**: Extensive options for colors, styling, and layout
- 📈 **Multiple plot types**: Box plots, violin plots, correlation matrices, shift plots, and alluvial plots
- 🔗 **Easy integration**: Works seamlessly with pandas DataFrames and numpy arrays

## Installation

```bash
pip install ggpubpy
```

## Quick Start

```python
from ggpubpy import plot_boxplot_with_stats, load_iris
import matplotlib.pyplot as plt

# Load sample data
iris = load_iris()

# Create a publication-ready boxplot with statistical annotations
fig, ax = plot_boxplot_with_stats(
    df=iris,
    x="species",
    y="sepal_length",
    title="Sepal Length by Species"
)

plt.show()
```

## Available Plot Types

### 📊 Box Plots
Create box plots with statistical annotations including ANOVA/Kruskal-Wallis tests and pairwise comparisons.

```python
from ggpubpy import plot_boxplot_with_stats, load_iris

fig, ax = plot_boxplot_with_stats(
    df=load_iris(),
    x="species",
    y="sepal_length",
    parametric=False  # Use non-parametric tests
)
```

### 🎻 Violin Plots
Visualize data distributions with violin plots that combine the benefits of box plots and density plots.

```python
from ggpubpy import plot_violin_with_stats, load_iris

fig, ax = plot_violin_with_stats(
    df=load_iris(),
    x="species",
    y="petal_length",
    palette={"setosa": "#FF6B6B", "versicolor": "#4ECDC4", "virginica": "#45B7D1"}
)
```

### 📈 Shift Plots
Perfect for before-after comparisons and paired data analysis.

```python
from ggpubpy import plot_shift
import numpy as np

# Create sample paired data
before = np.random.normal(10, 2, 30)
after = before + np.random.normal(1, 1.5, 30)

fig, ax = plot_shift(
    x=before,
    y=after,
    x_label="Before Treatment",
    y_label="After Treatment"
)
```

### 🔗 Correlation Matrix
Comprehensive visualization of relationships between multiple variables.

```python
from ggpubpy import plot_correlation_matrix, load_iris

fig, ax = plot_correlation_matrix(
    df=load_iris(),
    columns=['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
    title="Iris Dataset Correlation Matrix"
)
```

### 🌊 Alluvial Plots
Flow diagrams showing how data moves between categorical dimensions.

```python
from ggpubpy import plot_alluvial, load_titanic
import pandas as pd
import numpy as np

# Load and prepare data
titanic = load_titanic()
titanic = titanic.dropna(subset=["Age"])
titanic["Class"] = titanic["Pclass"].map({1: "1st", 2: "2nd", 3: "3rd"})
titanic["AgeCat"] = np.where(titanic["Age"] < 18, "Child", "Adult")
titanic["Survived"] = titanic["Survived"].astype(str).replace({"0": "No", "1": "Yes"})

# Create frequency table
titanic_tab = (titanic.groupby(["Class", "Sex", "AgeCat", "Survived"])
                    .size()
                    .reset_index(name="Freq")
                    .rename(columns={"AgeCat": "Age"}))
titanic_tab["alluvium"] = titanic_tab.index

# Create alluvial plot
fig, ax = plot_alluvial(
    titanic_tab,
    dims=["Class", "Sex", "Age"],
    value_col="Freq",
    color_by="Survived",
    id_col="alluvium",
    title="Titanic Survival Analysis"
)
```

## Statistical Tests

ggpubpy automatically performs appropriate statistical tests:

- **Global Tests**: One-way ANOVA, Kruskal-Wallis
- **Pairwise Comparisons**: t-tests, Mann-Whitney U tests
- **Correlation Analysis**: Pearson, Spearman, Kendall
- **Significance Levels**: `***` p < 0.001, `**` p < 0.01, `*` p < 0.05, `ns` p ≥ 0.05

## Documentation

📖 **Complete documentation** is available at [https://ggpubpy.readthedocs.io](https://ggpubpy.readthedocs.io)

The documentation includes:
- Detailed function references
- Comprehensive examples
- Statistical test explanations
- Customization guides
- Best practices

## Examples

Check out the `examples/` directory for complete working examples:

- `basic_usage.py`: Introduction to ggpubpy functions
- `alluvial_examples.py`: Alluvial plot examples
- `correlation_matrix_example.py`: Correlation matrix examples

## Dependencies

- Python 3.8+
- matplotlib
- pandas
- numpy
- scipy (for statistical tests)

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for more information.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use ggpubpy in your research, please cite:

```bibtex
@software{ggpubpy,
  title={ggpubpy: Publication-Ready Plots for Python},
  author={Izzet Turkalp Akbasli},
  year={2024},
  url={https://github.com/yourusername/ggpubpy}
}
```

## Support

For questions, bug reports, or feature requests, please open an issue on our [GitHub repository](https://github.com/yourusername/ggpubpy).

---

**Happy plotting! 📊✨**