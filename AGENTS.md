# AI Agent Instructions for this Project

You are an expert AI software engineer. This repository uses **uv** by Astral for all Python package, environment, and tool management. Follow the guidelines below strictly.

## Core Rules

* **Never** use bare `python`, `pip`, `venv`, or `pytest`.
* **Always** prefix commands with `uv run` or use corresponding `uv` workflows.
* **Do not** manually edit lockfiles; use `uv` tracking commands instead.

## Build and Environment Setup

### 1. Initialize & Synchronize Dependencies

To set up or sync the virtual environment with the `pyproject.toml` and `uv.lock` requirements, run:

```bash
uv sync
```

### 2. Adding Dependencies

* Add a standard project dependency:

  ```bash
  uv add <package_name>
  ```

* Add a development-only dependency (e.g., test or lint utilities):

  ```bash
  uv add --dev <package_name>
  ```

### 3. Removing Dependencies

```bash
uv remove <package_name>
```

## Running the Application

Always run scripts or entrypoints inside the managed `uv` environment:

* Run a local script/module:

  ```bash
  uv run python -m src.main
  ```

* Run a single, self-contained inline script with dynamic requirements:

  ```bash
  uv run script.py
  ```

## Quality Assurance & Testing

### Code Quality (Linting & Formatting)

We use Ruff for linting and code style consistency. Run and fix issues via:

```bash
uv run ruff check --fix
uv run ruff format
```

### Running Tests

Execute unit and integration test suites via pytest wrapped in the `uv` environment:

```bash
uv run pytest
```

## Project Structure Conventions

* Core application logic resides in the `src/` directory.
* The explicit lockfile tracking file is `uv.lock`.
