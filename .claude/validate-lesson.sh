#!/bin/bash
# Validates that lesson files follow the 4-part structure

set -euo pipefail

# Get list of staged .md files in lessons/
staged_lessons=$(git diff --cached --name-only --diff-filter=ACM | grep -E '^lessons/.*\.md$' || true)

if [[ -z "$staged_lessons" ]]; then
    # No lesson files staged, validation passes
    exit 0
fi

validation_failed=0

echo "Validating lesson structure..."

for file in $staged_lessons; do
    if [[ ! -f "$file" ]]; then
        continue
    fi

    echo "Checking: $file"

    # Check for the 4 required sections
    missing_sections=()

    if ! grep -qE '^##\s+(1\.\s+)?Concept Introduction' "$file"; then
        missing_sections+=("Concept Introduction")
    fi

    if ! grep -qE '^##\s+(2\.\s+)?Runnable Example' "$file"; then
        missing_sections+=("Runnable Example")
    fi

    if ! grep -qE '^##\s+(3\.\s+)?Common Pitfalls' "$file"; then
        missing_sections+=("Common Pitfalls")
    fi

    if ! grep -qE '^##\s+(4\.\s+)?Practice Exercise' "$file"; then
        missing_sections+=("Practice Exercise")
    fi

    if [[ ${#missing_sections[@]} -gt 0 ]]; then
        echo "  ❌ Missing sections: ${missing_sections[*]}"
        validation_failed=1
    else
        echo "  ✓ All sections present"
    fi
done

if [[ $validation_failed -eq 1 ]]; then
    echo ""
    echo "Lesson validation failed! Each lesson must have these 4 sections:"
    echo "  1. Concept Introduction"
    echo "  2. Runnable Example"
    echo "  3. Common Pitfalls"
    echo "  4. Practice Exercise"
    echo ""
    echo "Use /lesson <topic> to generate a properly structured lesson."
    exit 1
fi

echo "Lesson validation passed ✓"
exit 0
