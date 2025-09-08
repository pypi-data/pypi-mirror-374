# lilpipe

A tiny, typed, sequential pipeline engine for Python.

[![PyPI](https://img.shields.io/pypi/v/lilpipe.svg)](https://pypi.org/project/lilpipe/)
[![Python Version](https://img.shields.io/pypi/pyversions/lilpipe.svg)](https://pypi.org/project/lilpipe/)
[![CI](https://github.com/andrewruba/lilpipe/actions/workflows/ci.yaml/badge.svg)](https://github.com/andrewruba/lilpipe/actions)
[![Coverage](https://codecov.io/gh/andrewruba/lilpipe/branch/main/graph/badge.svg)](https://codecov.io/gh/andrewruba/lilpipe)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/your-username/lilpipe/blob/main/LICENSE)

**lilpipe** is a lightweight, Pydantic-powered library for building and running sequential workflows in Python. It’s ideal for data processing, scientific workflows, and any task that benefits from a clear, linear sequence of steps. With built-in caching and simple control signals, lilpipe is small, typed, and practical.

## Features

- **Sequential workflows** — run steps in a fixed order.
- **Type-safe context** — Pydantic-based `PipelineContext`.
- **Smart caching** — `fingerprint_keys` to skip unchanged work.
- **Flow control** — `ctx.abort_pass()` and `ctx.abort_pipeline()`.
- **Composable steps** — nest via `Step(name, children=[...])`.
- **Tiny surface area** — minimal API and dependencies.

## Installation

```bash
pip install lilpipe
````

> See `pyproject.toml` for supported Python versions.

## Example Notebook

The full, runnable demo lives here:

* **examples/example.ipynb** (in repo):
  [https://github.com/andrewruba/lilpipe/blob/HEAD/examples/example.ipynb](https://github.com/andrewruba/lilpipe/blob/HEAD/examples/example.ipynb)

* **nbviewer (rendered view):**
  [https://nbviewer.org/github/andrewruba/lilpipe/blob/HEAD/examples/example.ipynb](https://nbviewer.org/github/andrewruba/lilpipe/blob/HEAD/examples/example.ipynb)

* **Google Colab (optional):**
  [https://colab.research.google.com/github/andrewruba/lilpipe/blob/HEAD/examples/example.ipynb](https://colab.research.google.com/github/andrewruba/lilpipe/blob/HEAD/examples/example.ipynb)
  *Tip: in Colab, add a cell `!pip install lilpipe` before running the notebook.*

## License

Licensed under the [Apache 2.0 License](LICENSE).

## Links

* Issues: [https://github.com/andrewruba/lilpipe/issues](https://github.com/andrewruba/lilpipe/issues)
* PyPI: [https://pypi.org/project/lilpipe/](https://pypi.org/project/lilpipe/)
