---
name: review-file
description: Perform a comprehensive code review on one or more files
argument-hint: "<file path(s)>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Review File

Perform a comprehensive code review on specified file(s), analyzing code quality, security, performance, and compliance.

## Process

### 1. Read the File(s)

Use the Read tool to read the specified file(s). If a glob pattern is provided (e.g., `src/**/*.py`), use Glob to find matching files first.

### 2. Analyze Each File

For each file, evaluate:

**Code Quality:**
- Function/method complexity (target < 20 cyclomatic complexity)
- Single responsibility principle adherence
- Naming clarity and consistency
- Error handling completeness
- Test coverage indicators

**Security:**
- Input validation patterns
- SQL injection vulnerabilities
- Command injection risks
- XSS vulnerabilities (for web code)
- Hardcoded secrets or credentials
- Insecure cryptographic usage

**Performance:**
- Algorithmic efficiency
- Database query patterns (N+1, missing indexes)
- Memory management (leaks, unbounded growth)
- Resource cleanup (connections, file handles)

**Compliance:**
- Audit logging implementation
- Access control checks
- Data encryption usage
- PII handling patterns

**Maintainability:**
- Code duplication
- Documentation quality
- Dependency management
- Technical debt indicators (TODO, FIXME, HACK)

### 3. Run Analysis Scripts

If applicable, run the complexity analyzer:
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/code-review-practices/scripts/analyze-complexity.py <file>
```

Run the secret scanner:
```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/check-secrets.sh <file>
```

### 4. Generate Review Report

Structure the output as:

```markdown
# File Review: {filename}

## Overview
- **Language:** {detected language}
- **Lines of Code:** {count}
- **Functions/Methods:** {count}
- **Complexity:** {average/max}

## Findings

### Critical
[Critical issues requiring immediate attention]

### High
[High severity issues]

### Medium
[Medium severity issues]

### Low
[Low severity suggestions]

### Informational
[General observations and suggestions]

## Code Quality Metrics
- Average function complexity: X
- Functions exceeding threshold: Y
- Documentation coverage: Z%

## Security Assessment
[Summary of security-related findings]

## Recommendations
[Prioritized list of improvements]
```

### 5. Severity Guidelines

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Security vulnerability, data loss risk | SQL injection, hardcoded credentials, unencrypted PII |
| **High** | Significant bug or design flaw | Missing error handling, race conditions, memory leaks |
| **Medium** | Code quality issue | High complexity, poor naming, missing validation |
| **Low** | Minor improvement | Style issues, minor refactoring opportunities |
| **Informational** | Educational note | Alternative approaches, best practice references |

## Tips

- Consider the file's purpose and context
- Look for patterns across the codebase, not just individual issues
- Provide actionable remediation guidance
- Reference specific line numbers
- Suggest concrete improvements, not vague advice

## Example Usage

```
/review-file src/auth/login.py
/review-file "src/**/*.ts"
/review-file package.json src/index.js
```
