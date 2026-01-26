---
name: review-diff
description: Review staged changes or a specific git diff
argument-hint: "[commit range or --staged]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Review Diff

Review code changes from git diff, staged changes, or a specific commit range.

## Process

### 1. Get the Diff

Based on the argument provided:

**No argument (default: staged changes):**
```bash
git diff --staged
```

**`--staged` or `--cached`:**
```bash
git diff --staged
```

**Commit range (e.g., `main..HEAD`, `abc123..def456`):**
```bash
git diff {commit_range}
```

**Single commit:**
```bash
git show {commit} --format="%H %s" --stat
git diff {commit}^..{commit}
```

**Against main/master:**
```bash
git diff main...HEAD
```

### 2. Parse the Diff

Extract from the diff:
- Files changed
- Lines added/removed
- Type of change (modified, added, deleted, renamed)

### 3. Analyze Changes

For each changed file, focus on the **changed lines** while considering context:

**Code Quality:**
- Are the changes logically correct?
- Do they introduce edge case issues?
- Is error handling complete?
- Are new functions/methods well-named?

**Security:**
- Do changes introduce vulnerabilities?
- Is input validation added where needed?
- Are secrets or credentials exposed?
- Is authentication/authorization preserved?

**Performance:**
- Do changes degrade performance?
- Are there new N+1 query risks?
- Is resource management correct?

**Compliance:**
- Are audit events added for security actions?
- Is sensitive data handled properly?
- Are access controls maintained?

### 4. Generate Review Report

```markdown
# Diff Review

## Changes Summary
- **Files Changed:** {count}
- **Lines Added:** {count}
- **Lines Removed:** {count}

## Findings

### Critical
[Critical issues in the changes]

### High
[High severity issues]

### Medium
[Medium severity issues]

### Low
[Low severity suggestions]

### Informational
[Notes and observations]

## File-by-File Analysis

### {filename}
**Change Type:** {modified/added/deleted}
**Assessment:** [Brief assessment]
**Issues:** [Any issues found]

## Pre-Commit Checklist
- [ ] No secrets or credentials in diff
- [ ] Input validation added where needed
- [ ] Error handling is complete
- [ ] Tests cover the changes (if applicable)
- [ ] No debug/console statements left
- [ ] Changes match intended scope

## Recommendation
[READY TO COMMIT / NEEDS CHANGES / REQUIRES DISCUSSION]
```

### 5. Special Handling

**For large diffs (>1000 lines):**
- Focus on high-risk files first (auth, payments, data handling)
- Summarize routine changes
- Deep-dive on complex logic changes

**For configuration changes:**
- Verify no secrets exposed
- Check for security implications
- Validate syntax where possible

**For dependency changes (package.json, requirements.txt, etc.):**
- Note new dependencies
- Flag known vulnerable versions
- Check for major version bumps

## Tips

- Focus on what changed, not the entire file
- Consider the intent of the changes
- Look for incomplete changes (partial refactoring)
- Check for corresponding test changes
- Verify documentation updates if needed

## Example Usage

```
/review-diff
/review-diff --staged
/review-diff main..HEAD
/review-diff abc123
/review-diff HEAD~3..HEAD
```
