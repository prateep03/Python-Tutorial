# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python tutorial codebase. Code examples should prioritize clarity and pedagogical value over cleverness. Include inline comments explaining concepts for learners.

## Environment

- **Python version:** 3.12 (see `.python-version`)
- **Package manager:** `uv`
- **No external dependencies** — all examples use the standard library or commonly available packages (numpy, pandas, scikit-learn, etc.)

## Documentation Style
- Use Markdown for all docs
- Include runnable code examples for each concept
- Keep explanations beginner-friendly with minimal jargon

## Common Commands

```bash
# Run any tutorial script directly
python <script>.py

# Run a Jupyter notebook
jupyter notebook notebooks/<notebook>.ipynb

# Add a new dependency (if needed)
uv add <package>

# Sync environment
uv sync
```

## Repository Structure

Each `.py` file at the root is a standalone tutorial on a specific topic:

| File | Topic |
|---|---|
| `starters.py` | Basic Python (lists, tuples, dicts, sets) |
| `class-eg.py` | Comprehensive OOP (935 lines) |
| `class-eg-inheritance.py` | Inheritance patterns |
| `class-eg-classmethods.py` | Class methods |
| `decorator-examples.py` | Decorator patterns |
| `iterators-generators-eg.py` | Iterator/generator protocols |
| `threading-example.py` | Multi-threading |
| `multiprocessing-example.py` | Multi-processing |
| `race-condition-example.py` | Concurrency issues |
| `util.py` | Database/file utility functions |
| `plot_helper.py` | Data visualization helpers |
| `zanalyzer.py` | Data analysis utilities |
| `flan-t5-scan-summarization.py` | NLP model training (FLAN-T5) |
| `flan-t5-scan-inferencer.py` | NLP model inference |
| `sqltest.py` | SQL/MySQL database examples |

**`notebooks/`** — 40 Jupyter notebooks covering ML topics: NumPy/Pandas, regression, classification (KNN, Naive Bayes, Decision Trees), ensemble methods, clustering, PCA, encoding, and feature engineering.

**`data/`** — Sample datasets (MovieLens, Boston Housing, Churn, Iris, etc.) used by the notebooks.

**`mesa_examples/`** — Agent-based modeling examples using the Mesa library.

**`demo/`** — Function parameter passing examples.

## Architecture Notes

- Each root-level `.py` file is completely self-contained — there are no imports between tutorial files.
- `util.py`, `plot_helper.py`, and `zanalyzer.py` are shared helpers imported by some notebooks and scripts.
- The `data/` directory is the single source of datasets for all notebooks.
- There is no test suite; correctness is verified by running scripts and observing output.
