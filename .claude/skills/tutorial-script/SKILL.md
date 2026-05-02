---
name: tutorial-script
description: Generate a new self-contained Python tutorial script (.py file) with progressive examples and inline comments. Save to root as <topic>.py.
metadata: 
  - author: claude-code
  - created: 2026-05-02
---

Generate a self-contained Python tutorial script as a root-level `.py` file with progressive examples and inline explanations.

## Instructions

The user will invoke this skill with a topic name (e.g., `/tutorial-script context-managers` or `/tutorial-script async-await`). Your job is to generate a complete, runnable Python tutorial script and save it to the root directory as `<topic_snake_case>.py`.

### Script structure to follow

Model your output on existing tutorial scripts like `decorator-examples.py`, `iterators-generators-eg.py`, and `class-eg.py`. Every script must have:

---

**1. Module Docstring**

Start with a module-level docstring explaining what the script demonstrates:

```python
"""
Topic: <Concept Name>
Description: <One-line summary of what this tutorial covers>

This script demonstrates:
- Feature 1
- Feature 2
- Feature 3
"""
```

**2. Imports**

Include all necessary imports at the top. Use standard aliases:
- `import numpy as np`
- `import pandas as pd`
- `from typing import ...`

Only import shared helpers if necessary: `util.py`, `plot_helper.py`, `zanalyzer.py`

**3. Progressive Examples**

Organize code into sections that build complexity incrementally:

```python
# ============================================================
# Section 1: Basic Usage
# ============================================================

def example_basic():
    """Docstring explaining what this demonstrates."""
    # Step 1: Setup
    # Inline comments explaining the logic
    
    # Step 2: Core concept
    # Explain why this approach works
    
    # Step 3: Output
    print("Result:", result)

example_basic()

# ============================================================
# Section 2: Intermediate Patterns
# ============================================================

# Continue building on concepts from Section 1...
```

**4. Code Style**

- **Heavy inline comments**: Explain *why* and *how*, not just *what*
- **Descriptive names**: `calculate_fibonacci(n)`, not `fib(n)`
- **Show output**: Include `print()` statements or doctest-style output comments
- **Runnable sections**: Each section should be independently executable
- **Pedagogical scratch-pad**: Include commented-out alternative approaches or common mistakes

**5. Examples and Demonstrations**

- Use realistic, relatable examples (not just `foo`/`bar`)
- Show both correct usage and common pitfalls
- Include edge cases and error handling where relevant
- For data-focused topics, load from `data/` directory if needed

---

### Style rules (derived from existing scripts)

- **Headers**: Use comment blocks with `====` separators for major sections
- **Functions**: Include docstrings for all functions/classes
- **Tone**: Instructional; assume reader knows basic Python but not this specific topic
- **Length**: 100–500 lines depending on complexity
- **Imports**: No cross-imports between tutorial files (each is self-contained)
- **No installation docs**: Assume environment is set up
- **Comment ratio**: Aim for ~40% comments, ~60% code

### Common topics and patterns

| Topic | Key elements to include |
|---|---|
| **Decorators** | Function decorators, class decorators, `functools.wraps`, stacking |
| **Classes** | `__init__`, dunder methods, properties, inheritance, composition |
| **Concurrency** | Threading vs multiprocessing, locks, queues, race conditions |
| **Iterators/Generators** | `__iter__`, `__next__`, `yield`, generator expressions |
| **Context Managers** | `__enter__`, `__exit__`, `contextlib.contextmanager` |
| **Async/Await** | `async def`, `await`, `asyncio.run()`, concurrent tasks |

### Output

1. Write the script to `<topic_snake_case>.py` in the root directory
2. Make the script executable: `chmod +x <topic>.py` (optional)
3. Confirm the file path and give a one-line summary of what the script demonstrates

### Example invocation

```
User: /tutorial-script context-managers
Agent: 
[Creates context-managers.py with:]
- Module docstring
- Basic with statement
- Custom context manager class
- contextlib.contextmanager decorator
- Practical examples (file handling, database connections)
- Common pitfalls (suppressing exceptions, cleanup order)
```
