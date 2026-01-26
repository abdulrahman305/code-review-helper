---
name: review-file
description: Perform deep, comprehensive code audit on one or more files covering all 10 audit dimensions
argument-hint: "<file path(s)>"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Deep File Audit

Perform comprehensive, rigorous code audit on specified file(s), analyzing ALL dimensions: security, structure, quality, accuracy, documentation, dependencies, governance, confidentiality, intellectual property, and input/output verification.

## Audit Philosophy

**Leave No Stone Unturned:** Every line, every function, every import must be examined.
**Verify Everything:** Don't assume correctness - prove it.
**Document Thoroughly:** Every finding needs evidence and remediation.

## Process

### 1. Read and Understand the File(s)

Use the Read tool to read the specified file(s). If a glob pattern is provided (e.g., `src/**/*.py`), use Glob to find matching files first.

For each file:
- Identify the language, framework, and purpose
- Map data flows and trust boundaries
- Identify external dependencies and integrations
- Note the business context and regulatory requirements

### 2. Run Automated Analysis

**Complexity Analysis:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/code-review-practices/scripts/analyze-complexity.py <file>
```

**Secret Detection:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/check-secrets.sh <file>
```

**Compliance Scan:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/scan-compliance.py <file> --framework all
```

**Dependency Audit (for package files):**
```bash
# Check for known vulnerabilities
npm audit --json 2>/dev/null || pip-audit --format=json 2>/dev/null || echo "No package manager detected"
```

### 3. DEEP AUDIT - All 10 Dimensions

For each file, you MUST evaluate ALL dimensions:

---

#### DIMENSION 1: SECURITY AUDIT

**Authentication & Authorization:**
- [ ] All endpoints require proper authentication
- [ ] Authorization checks before sensitive operations
- [ ] Session management is secure (HTTPOnly, Secure, SameSite)
- [ ] Role-based access control properly implemented
- [ ] No privilege escalation paths
- [ ] Token handling is secure (JWT validation, expiry)

**Injection Prevention:**
- [ ] SQL queries use parameterized statements
- [ ] No command injection (subprocess with shell=False)
- [ ] XSS prevention (output encoding, CSP)
- [ ] Path traversal prevention (validate file paths)
- [ ] Template injection prevention
- [ ] LDAP/XML injection prevention

**Cryptographic Security:**
- [ ] Approved algorithms only (AES-256, RSA-2048+, SHA-256+)
- [ ] No deprecated algorithms (MD5, SHA1, DES, RC4)
- [ ] Proper key management (not hardcoded)
- [ ] TLS 1.2+ for all network communications
- [ ] No hardcoded secrets, keys, passwords
- [ ] Certificates properly validated

**Data Protection:**
- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit
- [ ] No sensitive data in logs
- [ ] Proper data masking/redaction
- [ ] Secure data deletion when required

---

#### DIMENSION 2: STRUCTURE AUDIT

**Architecture Compliance:**
- [ ] Follows stated architecture pattern (MVC, microservices, etc.)
- [ ] Clear separation of concerns
- [ ] Layer boundaries respected (presentation/business/data)
- [ ] Dependency injection used appropriately
- [ ] No circular dependencies

**Code Organization:**
- [ ] Logical module/package structure
- [ ] Consistent file naming conventions
- [ ] Functions/classes properly organized
- [ ] Imports organized and grouped correctly
- [ ] Configuration separated from code

**Design Patterns:**
- [ ] Patterns correctly implemented
- [ ] No anti-patterns present
- [ ] Interface contracts honored
- [ ] GRASP principles followed

---

#### DIMENSION 3: CODE QUALITY AUDIT

**Logic Correctness:**
- [ ] Algorithm correctness verified
- [ ] Edge cases handled (null, empty, boundary, overflow)
- [ ] No off-by-one errors
- [ ] Loop termination guaranteed
- [ ] No race conditions or deadlocks
- [ ] Thread safety where required

**SOLID Principles:**
- [ ] Single Responsibility: Each class/function has one purpose
- [ ] Open/Closed: Extensible without modification
- [ ] Liskov Substitution: Subtypes are substitutable
- [ ] Interface Segregation: No forced dependencies
- [ ] Dependency Inversion: Depend on abstractions

**Complexity Metrics:**
- [ ] Cyclomatic complexity < 15
- [ ] Cognitive complexity acceptable
- [ ] Nesting depth ≤ 4 levels
- [ ] Function length ≤ 50 lines
- [ ] Parameter count ≤ 5

**Error Handling:**
- [ ] All error paths handled
- [ ] Exceptions properly caught and handled
- [ ] No sensitive data in error messages
- [ ] Graceful degradation implemented
- [ ] No swallowed exceptions

---

#### DIMENSION 4: ACCURACY AUDIT

**Mathematical Accuracy:**
- [ ] Calculations mathematically correct
- [ ] Unit conversions accurate
- [ ] Floating-point precision handled correctly
- [ ] Date/time calculations correct (timezone-aware)
- [ ] Currency calculations use proper precision (Decimal)

**Business Logic Accuracy:**
- [ ] Business rules correctly implemented
- [ ] Regulatory calculations accurate (tax, interest, fees)
- [ ] Formulas match specifications
- [ ] State machine transitions correct
- [ ] Workflow logic accurate

**Algorithm Verification:**
- [ ] Algorithms produce correct output for test cases
- [ ] Sorting/searching works correctly
- [ ] Graph/tree traversals correct
- [ ] Hash functions work correctly
- [ ] Statistical calculations accurate

---

#### DIMENSION 5: DOCUMENTATION & COMMENTS AUDIT

**Comment Accuracy:**
- [ ] Comments accurately describe code behavior
- [ ] No outdated/stale comments
- [ ] TODO/FIXME/HACK items documented and tracked
- [ ] JSDoc/PyDoc/JavaDoc parameters match actual parameters
- [ ] No misleading comments

**Documentation Completeness:**
- [ ] All public APIs documented
- [ ] Function purposes clearly explained
- [ ] Complex logic has explanatory comments
- [ ] Assumptions documented
- [ ] Edge cases documented

**Reference Accuracy:**
- [ ] URLs/links are valid
- [ ] Cited standards are correct
- [ ] Version numbers accurate
- [ ] External documentation references valid
- [ ] License text accurate and complete

---

#### DIMENSION 6: DEPENDENCY AUDIT

**Import Analysis:**
- [ ] All imports are used (no dead imports)
- [ ] Import sources are trusted
- [ ] No circular imports
- [ ] Imports are appropriate for the context
- [ ] No wildcard imports in production code

**Dependency Security:**
- [ ] No dependencies with known CVEs
- [ ] Dependencies are up-to-date
- [ ] Transitive dependencies audited
- [ ] No dependency confusion vulnerabilities
- [ ] Package integrity verified (checksums)

**License Compliance:**
- [ ] All dependency licenses identified
- [ ] Licenses are compatible with project license
- [ ] GPL/copyleft obligations understood and met
- [ ] Attribution requirements satisfied
- [ ] No license conflicts

**Version Management:**
- [ ] Dependencies properly pinned
- [ ] No deprecated dependencies
- [ ] Breaking change risks identified
- [ ] Semantic versioning respected
- [ ] No abandoned dependencies

---

#### DIMENSION 7: GOVERNANCE & COMPLIANCE AUDIT

**Regulatory Frameworks:**
- [ ] NIST 800-53 controls implemented (if applicable)
- [ ] FedRAMP requirements met (if federal)
- [ ] SOC 2 Trust Services Criteria satisfied
- [ ] ISO 27001 controls aligned
- [ ] GDPR data protection requirements (if EU data)
- [ ] CCPA privacy requirements (if CA data)

**Industry Standards:**
- [ ] HIPAA compliance (healthcare data)
- [ ] PCI-DSS compliance (payment data)
- [ ] FERPA compliance (educational records)
- [ ] GLBA compliance (financial data)
- [ ] COPPA compliance (children's data)

**Coding Standards:**
- [ ] Follows team/organization coding standards
- [ ] Linter rules satisfied
- [ ] Formatting standards met
- [ ] Security coding guidelines followed

---

#### DIMENSION 8: CONFIDENTIALITY AUDIT

**Data Classification:**
- [ ] All data types identified and classified
- [ ] Handling appropriate for classification level
- [ ] Public/Internal/Confidential/Restricted properly separated
- [ ] Need-to-know principle enforced

**Access Control:**
- [ ] Least privilege principle applied
- [ ] Role definitions appropriate
- [ ] No excessive permissions
- [ ] Access is logged
- [ ] Access revocation handled

**Information Leakage Prevention:**
- [ ] No sensitive data in error messages
- [ ] No sensitive data in logs
- [ ] No debug code in production
- [ ] No sensitive data in URLs/query strings
- [ ] Third-party data sharing controlled

---

#### DIMENSION 9: INTELLECTUAL PROPERTY AUDIT

**License Compliance:**
- [ ] Code licensing is clear
- [ ] Third-party code properly attributed
- [ ] Open-source obligations met
- [ ] Patent considerations addressed
- [ ] Trademark usage appropriate

**Copyright Verification:**
- [ ] Copyright headers present (if required)
- [ ] Attribution accurate
- [ ] Derivative work compliance
- [ ] Contributor agreements in place

**Trade Secret Protection:**
- [ ] Proprietary algorithms protected
- [ ] Business logic not unnecessarily exposed
- [ ] Configuration secrets protected
- [ ] No competitive disclosure

---

#### DIMENSION 10: INPUT/OUTPUT VERIFICATION

**Input Verification:**
- [ ] All input sources identified
- [ ] All inputs validated before use
- [ ] Input sanitization applied
- [ ] Input types checked
- [ ] Input ranges validated
- [ ] Malicious input handled safely

**Output Verification:**
- [ ] Output format correct
- [ ] Output encoding prevents XSS
- [ ] Output is complete and accurate
- [ ] Error output is safe (no sensitive data)
- [ ] Output matches API contracts

**Calculation Verification:**
- [ ] Calculations traced end-to-end
- [ ] Intermediate results verified
- [ ] Rounding/precision correct
- [ ] Aggregations accurate
- [ ] Statistical calculations verified

**Conclusion Verification:**
- [ ] Logical conclusions from data are valid
- [ ] Decision tree outcomes correct
- [ ] Conditional logic outcomes verified
- [ ] State transitions correct
- [ ] Workflow completions verified

---

### 4. Generate Comprehensive Audit Report

Structure the output as:

```markdown
# Deep Code Audit Report

## File: {filename}

### Audit Metadata
| Field | Value |
|-------|-------|
| **File Path** | {full path} |
| **Language** | {detected language} |
| **Lines of Code** | {count} |
| **Functions/Methods** | {count} |
| **Audit Date** | {ISO 8601 timestamp} |
| **Dimensions Covered** | 10/10 |

### Executive Summary

**Overall Assessment:** [PASS / NEEDS REMEDIATION / CRITICAL FAILURES]

**Risk Score:** [1-10]

| Dimension | Status | Issues |
|-----------|--------|--------|
| Security | ✓/✗ | {count} |
| Structure | ✓/✗ | {count} |
| Quality | ✓/✗ | {count} |
| Accuracy | ✓/✗ | {count} |
| Documentation | ✓/✗ | {count} |
| Dependencies | ✓/✗ | {count} |
| Governance | ✓/✗ | {count} |
| Confidentiality | ✓/✗ | {count} |
| IP Compliance | ✓/✗ | {count} |
| I/O Verification | ✓/✗ | {count} |

---

### Critical Findings (Block Deployment)

#### Finding #1: {Title}
- **Severity:** CRITICAL
- **Dimension:** {dimension}
- **Location:** `{file}:{line}`
- **Standard/Control:** {applicable standard}

**Issue:**
{Detailed description of the problem}

**Evidence:**
```{language}
{code snippet showing the issue}
```

**Impact:**
{What could happen if not fixed - business, security, legal impact}

**Remediation:**
```{language}
{corrected code}
```

**Verification:**
{How to verify the fix is correct}

**References:**
- {Link to relevant standard or documentation}

---

[Continue for all Critical findings]

### High Severity Findings
[Same detailed format]

### Medium Severity Findings
[Same format with summary for simpler issues]

### Low Severity Findings
[Summary format: line number, brief description, quick fix]

### Informational Notes
[Brief suggestions and best practice recommendations]

---

### Dimension Details

#### Security Audit
- **Status:** PASS/FAIL
- **Checks Performed:** {count}
- **Issues Found:** {count}
- **Summary:** {1-2 sentence summary}

#### Structure Audit
- **Status:** PASS/FAIL
- **Architecture:** {identified pattern}
- **Issues Found:** {count}
- **Summary:** {1-2 sentence summary}

#### Quality Audit
- **Status:** PASS/FAIL
- **Avg Complexity:** {number}
- **Max Complexity:** {number}
- **SOLID Violations:** {count}
- **Summary:** {1-2 sentence summary}

#### Accuracy Audit
- **Status:** PASS/FAIL
- **Calculations Verified:** {count}
- **Errors Found:** {count}
- **Summary:** {1-2 sentence summary}

#### Documentation Audit
- **Status:** PASS/FAIL
- **Coverage:** {percentage}
- **Stale Comments:** {count}
- **Summary:** {1-2 sentence summary}

#### Dependency Audit
- **Status:** PASS/FAIL
- **Dependencies:** {count}
- **Vulnerabilities:** {count}
- **License Issues:** {count}
- **Summary:** {1-2 sentence summary}

#### Governance Audit
- **Status:** PASS/FAIL
- **Frameworks Assessed:** {list}
- **Compliance Gaps:** {count}
- **Summary:** {1-2 sentence summary}

#### Confidentiality Audit
- **Status:** PASS/FAIL
- **Data Types:** {list}
- **Leakage Risks:** {count}
- **Summary:** {1-2 sentence summary}

#### IP Compliance Audit
- **Status:** PASS/FAIL
- **Licenses Found:** {list}
- **Issues:** {count}
- **Summary:** {1-2 sentence summary}

#### I/O Verification Audit
- **Status:** PASS/FAIL
- **Inputs Validated:** {count}/{total}
- **Calculations Verified:** {count}
- **Summary:** {1-2 sentence summary}

---

### Remediation Roadmap

#### Immediate (Block Deployment)
1. [ ] {Critical finding} - {action}

#### Before Merge
1. [ ] {High finding} - {action}

#### Within Sprint
1. [ ] {Medium finding} - {action}

#### Backlog
1. [ ] {Low finding} - {action}

---

### Positive Observations
{Note any particularly good patterns, practices, or implementations}

### Audit Certification
This audit has comprehensively covered all 10 dimensions. All findings represent verified issues requiring attention.
```

### 5. Severity Guidelines

| Severity | Criteria | Examples |
|----------|----------|----------|
| **Critical** | Security vulnerabilities, data breach risk, compliance violations, calculation errors affecting financial/safety outcomes | SQL injection, hardcoded credentials, incorrect interest calculations, HIPAA violations |
| **High** | Significant bugs, data integrity issues, missing security controls | Missing auth checks, race conditions, memory leaks, incorrect business logic |
| **Medium** | Code quality issues, documentation errors, moderate risk items | High complexity, stale comments, missing validation, outdated dependencies |
| **Low** | Minor improvements, style issues, minor documentation gaps | Naming conventions, code formatting, minor refactoring opportunities |
| **Informational** | Best practices, educational notes, optimization suggestions | Alternative patterns, performance tips, industry best practices |

## Example Usage

```
/review-file src/auth/login.py
/review-file "src/**/*.ts"
/review-file package.json src/index.js
/review-file --dimensions=security,accuracy src/finance/calculations.py
```
