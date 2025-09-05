# dsp-toolkit

- [dsp-toolkit](#dsp-toolkit)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Quickstart](#quickstart)
  - [Features](#features)
  - [CLI Usage](#cli-usage)
  - [Extending \& Overriding](#extending--overriding)
  - [Development Workflow](#development-workflow)
  - [CI/CD \& Release](#cicd--release)
  - [Troubleshooting \& FAQ](#troubleshooting--faq)
  - [Local Development \& Testing in Another App](#local-development--testing-in-another-app)
    - [1. Editable Install (Recommended)](#1-editable-install-recommended)
    - [2. Build and Install the Package](#2-build-and-install-the-package)
    - [3. Local Path Dependency in pyproject.toml](#3-local-path-dependency-in-pyprojecttoml)

## Overview

This library is a toolkit for shared code between apps to try and make them consistent.


## Installation

```bash
poetry add dsp-toolkit
```

**NOTE:** Requires Python >=3.12,<4.0.

## Quickstart

```python
from dsp_toolkit.logging import logger

logger.info("I am a logging statement")
```

## Features

- `cli.py`: Reusable CLI for test, lint, release.
- `logging.py`: Centralized logging config.
- `env.py`: Environment variable management.
- `plugins/`: Custom flake8 plugins.

## CLI Usage

- `poetry run test [args]`: Run tests with optional args.
- `poetry run lint [args]`: Run linting with optional args.
- `poetry run release`: Run semantic-release for publishing.


## Extending & Overriding

- **Subclass toolkit modules in your app for custom behavior.**

- **Extend CLI commands:**
  - Create your own `cli.py` in your app (e.g., `src/my_app/cli.py`).
  - Import and reuse commands from `dsp_toolkit.cli`, then add or override as needed:
    ```python
    from dsp_toolkit.cli import test, lint_and_format, release

    def custom_command():
        print("This is my custom command!")

    # You can add an argparse entry point or use Poetry scripts to expose your custom commands.
    ```
  - In your `pyproject.toml`, add a Poetry script for your CLI:
    ```toml
    [tool.poetry.scripts]
    test = "my_app.cli:test"
    custom = "my_app.cli:custom_command"
    ```

- **Register additional plugins in your app's config:**
  - For Flake8 plugins, add them to your app's `setup.cfg` or register via `entry_points` in `pyproject.toml`:
    ```ini
    [flake8:local-plugins]
    extension =
        MYPLUG = my_app.plugins.my_plugin:MyPlugin
    ```
  - For pip-installable plugins, add them to your app's dependencies and Flake8 will auto-discover them.
  - For custom plugin registration, see Flake8 documentation: https://flake8.pycqa.org/en/latest/user/configuration.html#local-plugins

## Development Workflow

- Run tests: `poetry run test`
- Lint: `poetry run lint`
- Build: `poetry build`

## CI/CD & Release

Automated via GitHub Actions and semantic-release. See `.github/workflows/ci.yml` and `.github/workflows/release.yml` for details.

## Troubleshooting & FAQ

- If you encounter dependency issues, check your Python version and Poetry config.
- For local testing, see the section below.


## Local Development & Testing in Another App

You can test `dsp-toolkit` in another app before releasing to PyPI:

### 1. Editable Install (Recommended)

From your app directory:

```bash
poetry add ../path/to/dsp-toolkit --editable
```

or with pip:

```bash
pip install -e ../path/to/dsp-toolkit
```

### 2. Build and Install the Package

Build your library:
```bash
poetry build
```

Then install the wheel or sdist in your app (Recommended):

```bash
poetry add ../path/to/dsp-toolkit/dist/dsp_toolkit-0.1.0-py3-none-any.whl
```

or

```bash
pip install ../path/to/dsp-toolkit/dist/dsp_toolkit-0.1.0-py3-none-any.whl
```

### 3. Local Path Dependency in pyproject.toml

In your app’s `pyproject.toml`:

```toml
[tool.poetry.dependencies]
dsp-toolkit = { path = "../path/to/dsp-toolkit", develop = true }
```

Then run:

```bash
poetry install
```
