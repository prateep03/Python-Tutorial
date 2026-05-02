# AGENTS.md

AI agent instructions for the Python-Tutorial codebase. For environment setup and project structure, see [CLAUDE.md](./CLAUDE.md).

## Quick Reference

- **Generate a lesson**: `/lesson <topic>` → creates `lessons/<topic>.md` following the 4-part structure
- **Lesson format**: Concept intro → Runnable example → Common pitfalls → Practice exercises
- **Run scripts**: `python <script>.py` (all root-level `.py` files are self-contained tutorials)
- **Datasets**: Load from `../data/<file>.csv` (relative to `lessons/`) or `./data/<file>.csv` (from root)

## Common Workflows

### Creating a New Lesson

Use the custom skill:
```bash
/lesson <topic>
```

The skill automatically:
- Creates `lessons/<topic_snake_case>.md`
- Follows the 4-part structure: concept intro, runnable example, common pitfalls, practice exercises
- Uses datasets from `data/` directory
- Includes LaTeX math for ML topics
- Adds styled exercise callouts with HTML `<div class="alert">` blocks

**Manual lesson checklist** (if not using the skill):
1. Start with "when would you use this?" sentence
2. Include runnable code with all imports
3. Show expected output after each code block
4. Add 3–5 concrete pitfalls (wrong code → error → correct code)
5. Provide 2–3 exercises (Easy/Medium/Hard) with hints

### Creating a New Tutorial Script

Root-level `.py` files are standalone tutorials on specific Python concepts:
- **Self-contained**: No imports between tutorial files
- **Heavily commented**: Inline explanations for learners
- **Pedagogical style**: Show progressive complexity
- **Common imports**: `util.py`, `plot_helper.py`, `zanalyzer.py` for shared helpers

Pattern:
```python
"""
Topic: <Concept Name>
Description: <One-line summary>
"""

# Section 1: Basic usage
# Explain the concept...

def example_1():
    """Docstring explaining what this demonstrates."""
    # Step-by-step comments
    pass

# Section 2: Advanced patterns
# ...
```

### Working with Notebooks

The `notebooks/` directory contains 40 Jupyter notebooks. When adding or modifying:
- Use incremental complexity: basic → exploratory → model training → evaluation
- Import conventions: `np`, `pd`, `plt`, individual sklearn modules
- Load datasets from `../data/` (relative path from notebooks/)
- Include markdown cells explaining each step

## Code Conventions for Tutorials

1. **Clarity over cleverness**: Prioritize pedagogical value
2. **Comments**: Explain *why*, not *what*
3. **Variables**: Use descriptive names (`years_experience`, not `x`)
4. **Imports**: Standard aliases (`np`, `pd`, `plt`)
5. **No external setup**: Assume `uv` environment is ready

## Lesson Structure Reference

Every lesson must have these four sections:

### 1. Concept Introduction
- One-sentence "when to use this"
- Plain English explanation
- Math formulas (if applicable)
- 3–6 paragraphs or bullet list

### 2. Runnable Example
- Real datasets from `data/` (or self-contained for pure Python topics)
- Incremental complexity
- All imports in first block
- Expected output shown

### 3. Common Pitfalls
- 3–5 concrete mistakes
- Format: `### Pitfall: <name>` → Wrong code → Error → Correct code

### 4. Practice Exercise
- 2–3 exercises (Easy/Medium/Hard)
- HTML callout blocks:
```html
<div class="alert alert-block alert-success">
<b>Exercise (Easy):</b> ...
<br><br>
<b>Hint:</b> ...
</div>
```

## Available Custom Skills

- **`/lesson <topic>`** — Generate a complete tutorial lesson (see `.claude/skills/lesson/SKILL.md`)

## Testing and Validation

No automated test suite. Validate tutorials by:
1. Running the code blocks in order
2. Verifying output matches documentation
3. Testing edge cases mentioned in pitfalls
4. Completing practice exercises

For notebooks:
```bash
jupyter notebook notebooks/<notebook>.ipynb
# Run all cells and check for errors
```

## Common Pitfalls (for AI Agents)

1. **Don't duplicate imports**: Each tutorial file is self-contained; avoid cross-file imports
2. **Datasets must exist**: Check `data/` directory before referencing CSVs
3. **Relative paths**: Lessons use `../data/`, notebooks use `../data/`, root scripts use `./data/`
4. **No installation docs**: Assume environment is set up
5. **Beginner tone**: Explain concepts clearly but don't over-explain Python basics

## Links

- [CLAUDE.md](./CLAUDE.md) — Environment, commands, project structure
- [README.md](./README.md) — Project overview
- [Lesson skill definition](./.claude/skills/lesson/SKILL.md)
- [Existing lesson example](./lessons/linear_regression.md)
