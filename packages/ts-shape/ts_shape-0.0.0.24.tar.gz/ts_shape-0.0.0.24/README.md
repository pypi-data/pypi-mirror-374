# ts-shape | Timeseries Shaper

[![pypi version](https://img.shields.io/pypi/v/ts-shape.svg)](https://pypi.org/project/ts-shape/)
[![downloads](https://static.pepy.tech/badge/ts-shape/week)](https://pepy.tech/projects/ts-shape)
![documentation workflow](https://github.com/jakobgabriel/ts-shape/actions/workflows/generate_docs.yml/badge.svg)
[![documentation](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://jakobgabriel.github.io/ts-shape/)

----

This repository contains the *ts-shape* python package. The abbreviation stands for

*"Time Series shaping with rule based methods"*.

ts-shape is a Python library for efficiently transforms, contextualizes and extracts events from time series data. It provides a set of tools to handle various transformations, making data preparation tasks easier and more intuitive.

Besides that multiple engineering specific methods are utilized to make it fast and easy to work with time series data.

## Features | Concept


| **Category**  | **Feature**                                            | **Status** |
|---------------|--------------------------------------------------------|------------|
| **Transform** | Filters: Datatype-specific filters                     | ✔️         |
|               | Functions: Lambda functions for transformations        | ✔️         |
|               | Time Functions: Time-specific transformations          | ✔️         |
|               | Calculator: Calculation-based transformations          | ✔️         |
| **Features**  | Stats: Datatype-specific statistics                    | ✔️         |
|               | Time Stats: Timestamp-specific statistics              | ✔️         |
| **Context**   | Contextualize Timeseries datasets with foreign sources | ❌          |
| **Events**    | Quality Events                                         | ❌          |
|               | Maintenance Events                                     | ❌          |
|               | Production Events                                      | ❌          |
|               | Engineering Events                                     | ❌          |


## Installation

Install ts-shape using pip:

```bash
pip install ts-shape
```

## Documentation

For full documentation, visit [GitHub Pages](https://jakobgabriel.github.io/ts-shape/) or check out the docstrings in the code.

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please ensure to update tests as appropriate.

## License

Distributed under the MIT License. See LICENSE for more information.

## Acknowledgements

!TODO