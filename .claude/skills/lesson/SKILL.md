---
name: lesson
description: Generate a new Python tutorial lesson with concept intro, runnable example, common pitfalls, and practice exercise. Save to lessons/<topic>.md.
metadata: 
  - author: prateep.mukherjee
  - created: 2024-06-01
---

Generate a new Python tutorial lesson with: 1) concept intro, 2) runnable example, 3) common pitfalls, 4) practice exercise. Save to lessons/<topic>.md.

## Instructions

The user will invoke this skill with a topic name (e.g., `/lesson decorators` or `/lesson pandas groupby`). Your job is to generate a complete, self-contained tutorial lesson and save it to `lessons/<topic>.md` (use snake_case for the filename).

### Lesson structure to follow

Model your output on the patterns found in `notebooks/` — every lesson must have these four sections in order:

---

**1. Concept Introduction**

- Open with one sentence answering "when would you use this?"
- Explain the concept in plain English before any code or formulas
- If the topic has underlying math or an algorithm, include the formula/pseudocode after the plain-English explanation
- Use `**bold**` for key terms on first use
- Keep this section concise: 3–6 short paragraphs or a mix of prose and a bullet list

**2. Runnable Example**

- Use a real, relatable dataset where possible (see `data/` directory for available CSVs: iris.csv, adult.csv, Churn.csv, Boston_Housing_Prices.csv, movies.csv, ratings.csv, etc.)
- For pure Python topics (decorators, generators, etc.), use self-contained examples with no external dependencies
- Build complexity incrementally: start with the simplest version, then layer on one feature at a time
- Each code block must be runnable as-is (include all imports at the top of the first block)
- Show expected output immediately below each code block as a fenced block or inline comment
- Keep individual code blocks focused on one idea — split long examples into multiple blocks with explanatory prose in between

**3. Common Pitfalls**

- List 3–5 concrete mistakes beginners make with this topic
- For each pitfall: show the broken code, the error or wrong output it produces, and the correct version
- Use this format:

  ```
  ### Pitfall: <short name>
  **Wrong:**
  ```python
  # broken code
  ```
  **Error:** `TypeError: ...`

  **Correct:**
  ```python
  # fixed code
  ```
  ```

**4. Practice Exercise**

- Provide 2–3 exercises of increasing difficulty (Easy / Medium / Hard)
- Each exercise must have a clear goal, any starter code needed, and a hint (but not the solution)
- Format exercises in a styled callout block using HTML (matching notebook style):

  ```html
  <div class="alert alert-block alert-success">
  <b>Exercise (Easy):</b> ...
  <br><br>
  <b>Hint:</b> ...
  </div>
  ```

---

### Style rules (derived from the existing notebooks)

- **Headers:** Use `#` for title, `##` for the four main sections, `###` for subsections
- **Code:** Always specify the language in fenced blocks (` ```python `)
- **Tone:** Beginner-friendly; assume the reader knows basic Python syntax but not the specific topic
- **Length:** Aim for a lesson that takes 20–30 minutes to work through
- **Datasets:** Load from `../data/<file>.csv` (relative to the `lessons/` directory)
- **Imports:** NumPy as `np`, Pandas as `pd`, scikit-learn modules individually — match the conventions in the notebooks
- **Do not** include installation instructions (the environment is already set up with `uv`)
- **Do not** explain what Python is or what a variable is — assume basic Python literacy

### Output

1. Create the `lessons/` directory if it does not exist
2. Write the lesson to `lessons/<topic_snake_case>.md`
3. Confirm the file path and give the user a one-line summary of what the lesson covers
