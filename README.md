# Python-Tutorial

A comprehensive Python programming tutorial repository covering core concepts, OOP, concurrency, and machine learning fundamentals.

## Quick Start

```bash
# Run any tutorial script
python <script>.py

# Launch Jupyter for notebooks
jupyter notebook notebooks/

# Generate a new lesson (if using Claude Code)
/lesson <topic>
```

## Repository Structure

- **Root `.py` files** — Standalone tutorials on specific topics (decorators, classes, iterators, threading, etc.)
- **`lessons/`** — Markdown tutorial lessons following a 4-part structure (concept → example → pitfalls → exercises)
- **`notebooks/`** — 40 Jupyter notebooks on ML/data science (NumPy, Pandas, regression, classification, clustering, PCA)
- **`data/`** — Sample datasets (Iris, Boston Housing, Churn, MovieLens, etc.)
- **`mesa_examples/`** — Agent-based modeling examples

## For AI Coding Agents

See [AGENTS.md](./AGENTS.md) for AI agent instructions, custom skills, and workflow patterns.

## Environment

- Python 3.12 (via `pyenv`)
- Package manager: `uv`
- See [CLAUDE.md](./CLAUDE.md) for detailed setup