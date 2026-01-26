---
name: Code Review Practices
description: This skill should be used when the user asks to "review code", "check code quality", "improve code", "find bugs", "code best practices", "performance review", "maintainability check", or when performing any code review task. Provides comprehensive guidance for code quality, performance, security patterns, and maintainability analysis.
version: 1.0.0
---

# Code Review Practices

Comprehensive guidance for conducting thorough code reviews covering quality, performance, security, and maintainability.

## Overview

Effective code review analyzes multiple dimensions of code quality. Apply these practices systematically to identify issues and provide actionable feedback.

## Review Dimensions

### 1. Code Quality

**Logic and Correctness**
- Verify algorithms produce expected outputs for all input ranges
- Check boundary conditions and edge cases
- Identify potential null/undefined reference errors
- Validate error handling covers all failure modes
- Ensure consistent behavior across code paths

**Design Patterns**
- Identify anti-patterns (God objects, circular dependencies, deep nesting)
- Verify appropriate use of SOLID principles
- Check for proper separation of concerns
- Evaluate abstraction levels (neither too abstract nor too concrete)
- Assess coupling and cohesion

**Code Clarity**
- Variable/function names accurately describe purpose
- Functions have single, clear responsibilities
- Complex logic is commented or extracted to well-named functions
- Magic numbers replaced with named constants
- Consistent formatting and style

### 2. Performance Analysis

**Algorithmic Efficiency**
- Identify O(n²) or worse algorithms that could be optimized
- Check for unnecessary repeated computations
- Look for N+1 query patterns in database access
- Verify appropriate data structure choices
- Identify opportunities for caching

**Resource Management**
- Check for memory leaks (unclosed resources, growing collections)
- Verify proper cleanup in finally blocks or destructors
- Identify potential connection pool exhaustion
- Check for unbounded growth in buffers or queues

**Common Performance Issues**
- String concatenation in loops (use StringBuilder/join)
- Repeated regex compilation (use compiled patterns)
- Synchronous I/O blocking event loops
- Excessive object creation in hot paths
- Missing indexes for database queries

### 3. Security Patterns

**Input Validation**
- All external input validated before use
- Parameterized queries for database access (prevent SQL injection)
- Output encoding for web contexts (prevent XSS)
- File path validation (prevent path traversal)
- Command injection prevention in shell calls

**Authentication/Authorization**
- Verify authorization checks on all protected resources
- Check for IDOR (Insecure Direct Object Reference) vulnerabilities
- Ensure session management follows best practices
- Validate JWT/token handling

**Data Protection**
- Sensitive data not logged or exposed in errors
- Encryption used for sensitive data at rest and in transit
- Secure credential storage (no hardcoded secrets)
- PII handling follows data protection requirements

### 4. Maintainability

**Testability**
- Functions are deterministic and mockable
- Dependencies are injectable
- Side effects are isolated and controllable
- Test coverage for critical paths

**Documentation**
- Public APIs have clear documentation
- Complex business logic explained
- Non-obvious decisions documented
- README/setup instructions current

**Technical Debt Indicators**
- TODO/FIXME/HACK comments
- Duplicated code blocks
- Overly long functions (>50 lines)
- Deep nesting (>3 levels)
- Inconsistent error handling

## Severity Classification

Use 5-tier severity for all findings:

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| **Critical** | Security vulnerabilities, data loss risk, system crashes | Must fix before merge |
| **High** | Significant bugs, performance issues, security weaknesses | Should fix before merge |
| **Medium** | Code quality issues, maintainability concerns | Recommended to fix |
| **Low** | Minor improvements, style inconsistencies | Consider fixing |
| **Informational** | Suggestions, alternatives, FYI notes | Optional |

## Review Process

### Pre-Review Checklist

1. Understand the change's purpose (PR description, linked issues)
2. Identify the scope (which files, what functionality)
3. Note the testing approach (unit tests, integration tests)
4. Consider the risk level (critical path, data handling)

### During Review

1. Start with high-level architecture review
2. Check for obvious security issues first
3. Review logic and correctness
4. Evaluate performance implications
5. Assess maintainability and clarity
6. Verify test coverage

### Providing Feedback

- Be specific: Reference exact lines and provide examples
- Be constructive: Suggest solutions, not just problems
- Prioritize: Focus on critical issues first
- Explain why: Help authors understand the reasoning

## Utility Scripts

### Complexity Analysis

Run `${CLAUDE_PLUGIN_ROOT}/skills/code-review-practices/scripts/analyze-complexity.py` to analyze cyclomatic complexity:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/code-review-practices/scripts/analyze-complexity.py <file>
```

## Additional Resources

### Reference Files

For detailed patterns and checklists:
- **`references/quality-checklist.md`** - Comprehensive quality review checklist
- **`references/performance-patterns.md`** - Common performance issues and fixes
- **`references/security-checklist.md`** - Security review checklist by language

### Language-Specific Considerations

Different languages have specific concerns:
- **JavaScript/TypeScript**: Async handling, prototype pollution, npm vulnerabilities
- **Python**: GIL implications, mutable default arguments, import side effects
- **Go**: Goroutine leaks, defer ordering, nil interface checks
- **Rust**: Unsafe blocks, lifetime issues, panic handling
- **Java**: Null handling, resource management, thread safety
