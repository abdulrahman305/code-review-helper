---
name: audit-report
description: Generate a formal audit report with findings in Markdown and JSON formats
argument-hint: "[path] [--output <filename>]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
---

# Audit Report

Generate a comprehensive, formal audit report suitable for compliance documentation, auditors, or regulatory submissions. Produces both human-readable Markdown and machine-readable JSON outputs.

## Process

### 1. Parse Arguments

**Path:** Directory or file(s) to audit (default: current directory)

**Output:** Base filename for reports (default: `audit-report`)
- Creates `{output}.md` for Markdown report
- Creates `{output}.json` for JSON report

### 2. Gather System Information

Collect context about the codebase:
```bash
# Git information
git log --oneline -10
git remote -v

# Project information
ls -la
cat package.json 2>/dev/null || cat requirements.txt 2>/dev/null || echo "No package manifest"
```

### 3. Run All Compliance Scans

**Secret Detection:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/check-secrets.sh {path} --json
```

**Compliance Scan:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/scan-compliance.py {path} --json --framework all
```

**Complexity Analysis:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/code-review-practices/scripts/analyze-complexity.py {files} --json
```

### 4. Manual Code Review

Perform targeted review focusing on:

- **Authentication flows** - Login, session management, password handling
- **Authorization checks** - Access control, RBAC implementation
- **Data handling** - PII, PHI, cardholder data, encryption
- **API security** - Input validation, output encoding, rate limiting
- **Audit logging** - Event coverage, log integrity, retention
- **Cryptography** - Algorithms, key management, TLS configuration

### 5. Generate Markdown Report

Write to `{output}.md`:

```markdown
# Security & Compliance Audit Report

## Report Metadata
| Field | Value |
|-------|-------|
| **Report ID** | {UUID} |
| **Generated** | {ISO 8601 timestamp} |
| **Audit Scope** | {path} |
| **Auditor** | Claude Code Review Helper |
| **Version** | 1.0.0 |

## Executive Summary

### Overall Risk Rating: {CRITICAL/HIGH/MEDIUM/LOW}

{Summary paragraph describing the overall security and compliance posture, key findings, and recommendations.}

### Key Statistics
| Metric | Value |
|--------|-------|
| Files Analyzed | {count} |
| Lines of Code | {count} |
| Critical Findings | {count} |
| High Findings | {count} |
| Medium Findings | {count} |
| Low Findings | {count} |
| Informational | {count} |

## Scope and Methodology

### Audit Scope
{Description of what was audited, including any exclusions.}

### Methodology
This audit employed:
1. Automated secret detection scanning
2. Pattern-based compliance rule checking
3. Static code complexity analysis
4. Manual code review for business logic
5. Framework-specific control assessment

### Frameworks Assessed
- NIST 800-53 Rev. 5
- SOC 2 Type II
- ISO 27001:2013
- HIPAA Security Rule
- PCI-DSS v4.0

## Detailed Findings

### Finding #{number}: {Title}

| Attribute | Value |
|-----------|-------|
| **Severity** | {CRITICAL/HIGH/MEDIUM/LOW/INFO} |
| **Framework** | {applicable frameworks} |
| **Control** | {control ID} |
| **Status** | OPEN |
| **File** | {file path} |
| **Line** | {line number} |

**Description:**
{Detailed description of the finding}

**Evidence:**
```{language}
{Code snippet demonstrating the issue}
```

**Risk:**
{Explanation of the risk and potential impact}

**Remediation:**
{Specific steps to remediate the issue}

**References:**
- {Link to relevant standard or documentation}

---

[Repeat for each finding]

## Compliance Summary

### NIST 800-53

| Control Family | Assessed | Passed | Failed | N/A |
|---------------|----------|--------|--------|-----|
| Access Control (AC) | X | X | X | X |
| Audit (AU) | X | X | X | X |
| Identification (IA) | X | X | X | X |
| System Protection (SC) | X | X | X | X |
| System Integrity (SI) | X | X | X | X |

### SOC 2 Trust Services

| Criteria | Status | Notes |
|----------|--------|-------|
| Security (CC6) | PASS/FAIL | {notes} |
| Availability | N/A | {notes} |
| Processing Integrity | N/A | {notes} |
| Confidentiality | PASS/FAIL | {notes} |
| Privacy | N/A | {notes} |

### HIPAA Security Rule

| Standard | Status | Notes |
|----------|--------|-------|
| Access Control §164.312(a) | PASS/FAIL | {notes} |
| Audit Controls §164.312(b) | PASS/FAIL | {notes} |
| Integrity §164.312(c) | PASS/FAIL | {notes} |
| Authentication §164.312(d) | PASS/FAIL | {notes} |
| Transmission §164.312(e) | PASS/FAIL | {notes} |

### PCI-DSS

| Requirement | Status | Notes |
|-------------|--------|-------|
| Req 3: Protect CHD | PASS/FAIL | {notes} |
| Req 4: Encrypt Transmission | PASS/FAIL | {notes} |
| Req 6: Secure Systems | PASS/FAIL | {notes} |
| Req 8: Authentication | PASS/FAIL | {notes} |
| Req 10: Logging | PASS/FAIL | {notes} |

## Remediation Roadmap

### Immediate (0-7 days)
Critical and high findings requiring immediate attention:
1. {Finding with remediation}

### Short-term (1-4 weeks)
Medium findings and quick wins:
1. {Finding with remediation}

### Long-term (1-3 months)
Process improvements and enhancements:
1. {Improvement}

## Appendices

### A. Files Analyzed
{List of all files included in the audit}

### B. Tools Used
- Secret Scanner v1.0
- Compliance Scanner v1.0
- Complexity Analyzer v1.0

### C. Glossary
{Definitions of technical terms}

---

*This report was generated automatically by Code Review Helper. Findings should be validated by qualified security personnel.*
```

### 6. Generate JSON Report

Write to `{output}.json`:

```json
{
  "metadata": {
    "reportId": "{UUID}",
    "generatedAt": "{ISO 8601}",
    "scope": "{path}",
    "version": "1.0.0"
  },
  "summary": {
    "overallRisk": "HIGH",
    "filesAnalyzed": 100,
    "linesOfCode": 15000,
    "findingCounts": {
      "critical": 1,
      "high": 3,
      "medium": 8,
      "low": 12,
      "informational": 5
    }
  },
  "findings": [
    {
      "id": "FINDING-001",
      "severity": "critical",
      "title": "Hardcoded Database Credentials",
      "frameworks": ["NIST", "SOC2", "PCI-DSS"],
      "control": "NIST SC-28",
      "file": "src/config.py",
      "line": 42,
      "description": "Database password hardcoded in source",
      "evidence": "db_password = 'secret123'",
      "remediation": "Use environment variables or secrets manager",
      "status": "open"
    }
  ],
  "compliance": {
    "nist": {"passed": 45, "failed": 3, "na": 12},
    "soc2": {"passed": 20, "failed": 2, "na": 8},
    "hipaa": {"passed": 10, "failed": 1, "na": 4},
    "pciDss": {"passed": 15, "failed": 2, "na": 3}
  }
}
```

### 7. Output Files

Write both reports:
1. Use Write tool for `{output}.md`
2. Use Write tool for `{output}.json`

Report the file locations to the user.

## Example Usage

```
/audit-report
/audit-report src/
/audit-report . --output security-audit-2024-01
/audit-report src/api/ --output api-compliance-report
```
