# bja_utils

[![PyPI version](https://img.shields.io/pypi/v/bja_utils.svg)](https://pypi.org/project/bja_utils/)
[![Python Version](https://img.shields.io/pypi/pyversions/bja_utils.svg)](https://pypi.org/project/bja_utils/)

`bja_utils` is a Python package providing convenience functions for **mass spectrometry proteomics and lipidomics analysis**, data parsing, statistics, biological interpretation, and plotting. It is designed to streamline common workflows and reduce repetitive coding for omics researchers.

---

## Features

- Data processing and transformation
- Statistical analysis functions
- Visualization and plotting utilities
- Parsing tools for common data formats
- Biological interpretation helpers

---

## Package Structure

The package is organized into the following modules:

### `processing`
Functions for data preprocessing, multi-processing of computationally intensive tasks, normalization, imputation, and cleaning. 
Includes tools for handling missing values, scaling, and aggregating omics data.

### `analysis`
Statistical functions and models for downstream analysis. Supports descriptive statistics, hypothesis testing, regression models, and more.

### `plotting`
Helper functions for common plotting tasks `matplotlib` and `plotly`. 
Simplifies custom styling, multi-panel figures, and specialized omics visualizations.

### `parsing`
Functions for reading, parsing, and converting glycoproteomics and lipidomics identifiers.

### `utils`
General helper functions for file handling, logging, and other repetitive tasks that don’t fit into other modules.



---

## Installation

You can install the latest release via PyPI:

```bash
pip install bja_utils