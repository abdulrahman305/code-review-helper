---
name: review-pr
description: Review a pull request from GitHub, GitLab, or Bitbucket with comprehensive code analysis
argument-hint: "<PR URL or number>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebFetch
  - Write
---

# Review Pull Request

Perform a comprehensive code review of a pull request or merge request from GitHub, GitLab, or Bitbucket.

## Process

### 1. Parse Input and Detect Platform

If the input is a URL, detect the platform from the URL pattern:
- GitHub: `github.com/{owner}/{repo}/pull/{number}`
- GitLab: `gitlab.com/{path}/-/merge_requests/{number}`
- Bitbucket: `bitbucket.org/{workspace}/{repo}/pull-requests/{number}`

If the input is just a number, assume GitHub and use the current repository context.

### 2. Fetch PR Data

**For GitHub (preferred method using gh CLI):**
```bash
gh pr view {number} --json title,body,files,commits,state,baseRefName,headRefName
gh pr diff {number}
```

**For GitLab:**
Use the fetch-pr.py script from the multi-platform-review skill.

**For Bitbucket:**
Use the fetch-pr.py script from the multi-platform-review skill.

### 3. Analyze the Changes

For each file in the diff, analyze:

**Code Quality:**
- Logic correctness and edge cases
- Design patterns and SOLID principles
- Code clarity and naming
- Error handling completeness

**Security:**
- Input validation
- Injection vulnerabilities (SQL, command, XSS)
- Authentication/authorization checks
- Sensitive data handling

**Performance:**
- Algorithmic efficiency
- N+1 queries or database issues
- Memory management
- Resource cleanup

**Compliance:**
- Secret detection (no hardcoded credentials)
- PII handling (if applicable)
- Audit logging (if security-relevant)

### 4. Generate Review Report

Structure the output as:

```markdown
# Code Review: PR #{number}

## Summary
Brief overview of the changes and overall assessment.

## Findings

### Critical
[List any critical issues that must be fixed]

### High
[List high severity issues that should be fixed]

### Medium
[List medium severity issues recommended to fix]

### Low
[List low severity suggestions]

### Informational
[List informational notes and suggestions]

## Files Reviewed
- file1.py: [brief assessment]
- file2.js: [brief assessment]

## Recommendation
[APPROVE / REQUEST CHANGES / NEEDS DISCUSSION]
```

### 5. Severity Guidelines

| Severity | Criteria |
|----------|----------|
| **Critical** | Security vulnerabilities, data loss risk, system crashes |
| **High** | Significant bugs, performance issues, security weaknesses |
| **Medium** | Code quality issues, maintainability concerns |
| **Low** | Minor improvements, style inconsistencies |
| **Informational** | Suggestions, alternatives, educational notes |

## Tips

- Focus on the **changes**, not the entire file unless context is needed
- Be specific: reference exact lines and provide examples
- Be constructive: suggest solutions, not just problems
- Prioritize: critical issues first, then high, etc.
- Consider the PR's purpose when evaluating changes

## Example Usage

```
/review-pr https://github.com/org/repo/pull/123
/review-pr 456
/review-pr https://gitlab.com/group/project/-/merge_requests/78
```
