---
name: audit-report
description: Generate comprehensive formal audit report covering all 10 audit dimensions with findings in Markdown and JSON formats
argument-hint: "[path] [--output <filename>] [--frameworks <list>]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
---

# Comprehensive Audit Report

Generate a DEEP, FORMAL audit report covering all 10 audit dimensions, suitable for compliance documentation, auditors, regulatory submissions, and board-level reporting. Produces both human-readable Markdown and machine-readable JSON outputs.

## Audit Philosophy

**Comprehensive:** Cover ALL 10 audit dimensions without exception.
**Evidence-Based:** Every finding must have code evidence.
**Actionable:** Every finding includes specific remediation steps.
**Verifiable:** All findings can be independently verified.

## The 10 Audit Dimensions

1. **Security** - Vulnerabilities, authentication, cryptography
2. **Structure** - Architecture, design patterns, organization
3. **Quality** - Logic correctness, SOLID principles, complexity
4. **Accuracy** - Calculation correctness, business logic verification
5. **Documentation** - Comments, references, API docs accuracy
6. **Dependencies** - Imports, licenses, vulnerabilities, versions
7. **Governance** - Regulatory compliance, policy adherence
8. **Confidentiality** - Data classification, access control, leakage
9. **Intellectual Property** - Licenses, copyright, attribution
10. **Input/Output Verification** - Validation, calculations, conclusions

## Process

### 1. Parse Arguments

**Path:** Directory or file(s) to audit (default: current directory)

**Output:** Base filename for reports (default: `audit-report`)
- Creates `{output}.md` for Markdown report
- Creates `{output}.json` for JSON report

**Frameworks:** Comma-separated list (default: all)
- nist, fedramp, soc2, iso27001, hipaa, pci-dss, gdpr, ccpa

### 2. Gather System Information

Collect context about the codebase:
```bash
# Git information
git log --oneline -10
git remote -v
git branch -a

# Project information
ls -la
cat package.json 2>/dev/null || cat requirements.txt 2>/dev/null || cat Cargo.toml 2>/dev/null || echo "No package manifest"

# Count files and lines
find {path} -type f \( -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.java" -o -name "*.go" \) | wc -l
```

### 3. Run All Automated Scans

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
python ${CLAUDE_PLUGIN_ROOT}/skills/code-review-practices/scripts/analyze-complexity.py {path} --json
```

**Dependency Audit:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/dependency-audit/scripts/audit-dependencies.py {path} --format json
```

**License Check:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/dependency-audit/scripts/check-licenses.py {path} --format json
```

**Calculation Verification:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/verification-audit/scripts/verify-calculations.py {path} --format json
```

### 4. Deep Manual Audit - ALL 10 DIMENSIONS

Perform comprehensive manual review across all dimensions:

#### DIMENSION 1: SECURITY
- Authentication/authorization mechanisms
- Injection vulnerability patterns
- Cryptographic implementations
- Secret/credential handling
- Session management
- Input validation

#### DIMENSION 2: STRUCTURE
- Architecture pattern compliance
- Separation of concerns
- Design pattern implementation
- Module organization
- Circular dependencies

#### DIMENSION 3: QUALITY
- Logic correctness verification
- SOLID principles adherence
- Complexity metrics analysis
- Error handling completeness
- Edge case coverage

#### DIMENSION 4: ACCURACY
- Mathematical calculations
- Business logic implementation
- Formula correctness
- Financial calculations (if applicable)
- Date/time handling

#### DIMENSION 5: DOCUMENTATION
- Comment accuracy vs code behavior
- Stale/outdated documentation
- Reference link validity
- API documentation completeness
- Technical debt tracking (TODO/FIXME)

#### DIMENSION 6: DEPENDENCIES
- Unused imports
- Known vulnerabilities (CVEs)
- License compliance
- Version currency
- Supply chain security

#### DIMENSION 7: GOVERNANCE
- Regulatory framework compliance
- Policy adherence verification
- Audit trail completeness
- Change management compliance

#### DIMENSION 8: CONFIDENTIALITY
- Data classification accuracy
- Access control enforcement
- Information leakage prevention
- Third-party data sharing

#### DIMENSION 9: INTELLECTUAL PROPERTY
- License compliance verification
- Copyright header presence
- Attribution requirements
- Open-source obligations

#### DIMENSION 10: INPUT/OUTPUT VERIFICATION
- Input validation completeness
- Output encoding correctness
- Calculation tracing
- API contract compliance

### 5. Generate Comprehensive Markdown Report

Write to `{output}.md`:

```markdown
# Comprehensive Code Audit Report

## Report Metadata
| Field | Value |
|-------|-------|
| **Report ID** | {UUID} |
| **Generated** | {ISO 8601 timestamp} |
| **Audit Scope** | {path} |
| **Auditor** | Claude Code Review Helper v2.0 |
| **Dimensions Covered** | 10/10 |

---

## Executive Summary

### Overall Assessment: {PASS / NEEDS REMEDIATION / CRITICAL FAILURES}

### Risk Score: {1-10}

{Summary paragraph describing the overall posture across all dimensions, key findings, and top recommendations.}

### Dimension Status Overview
| Dimension | Status | Critical | High | Medium | Low | Info |
|-----------|--------|----------|------|--------|-----|------|
| Security | ✓/⚠/✗ | X | X | X | X | X |
| Structure | ✓/⚠/✗ | X | X | X | X | X |
| Quality | ✓/⚠/✗ | X | X | X | X | X |
| Accuracy | ✓/⚠/✗ | X | X | X | X | X |
| Documentation | ✓/⚠/✗ | X | X | X | X | X |
| Dependencies | ✓/⚠/✗ | X | X | X | X | X |
| Governance | ✓/⚠/✗ | X | X | X | X | X |
| Confidentiality | ✓/⚠/✗ | X | X | X | X | X |
| IP Compliance | ✓/⚠/✗ | X | X | X | X | X |
| I/O Verification | ✓/⚠/✗ | X | X | X | X | X |

### Key Statistics
| Metric | Value |
|--------|-------|
| Files Analyzed | {count} |
| Lines of Code | {count} |
| Total Findings | {count} |
| Critical Findings | {count} |
| High Findings | {count} |
| Dependencies Audited | {count} |
| Vulnerabilities Found | {count} |
| License Issues | {count} |

### Top 5 Critical Actions
1. {Most critical action required}
2. {Second critical action}
3. {Third critical action}
4. {Fourth critical action}
5. {Fifth critical action}

---

## Scope and Methodology

### Audit Scope
{Description of what was audited, including files, directories, and any exclusions.}

### Methodology
This audit employed comprehensive analysis across 10 dimensions:

1. **Automated Scanning**
   - Secret detection (credentials, API keys, tokens)
   - Compliance pattern matching (NIST, HIPAA, PCI-DSS, GDPR)
   - Code complexity analysis (cyclomatic, cognitive)
   - Dependency vulnerability scanning (CVE databases)
   - License compliance checking
   - Calculation verification

2. **Manual Deep Review**
   - Security architecture analysis
   - Business logic verification
   - Accuracy validation with test cases
   - Documentation correctness verification
   - Access control audit
   - IP compliance assessment

### Frameworks Assessed
| Framework | Version | Applicability |
|-----------|---------|---------------|
| NIST 800-53 | Rev. 5 | {applicable/N/A} |
| FedRAMP | Moderate | {applicable/N/A} |
| SOC 2 | Type II | {applicable/N/A} |
| ISO 27001 | 2022 | {applicable/N/A} |
| HIPAA | Security Rule | {applicable/N/A} |
| PCI-DSS | v4.0 | {applicable/N/A} |
| GDPR | 2018 | {applicable/N/A} |
| CCPA/CPRA | 2023 | {applicable/N/A} |

---

## Detailed Findings by Dimension

### Dimension 1: Security

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Findings:** {count} total ({critical}, {high}, {medium}, {low})
- **Key Concerns:** {brief summary}

#### Finding S-001: {Title}

| Attribute | Value |
|-----------|-------|
| **Severity** | {CRITICAL/HIGH/MEDIUM/LOW/INFO} |
| **Dimension** | Security |
| **Category** | {Authentication/Injection/Crypto/etc.} |
| **Frameworks** | {NIST SC-X, PCI-DSS Req X, etc.} |
| **File** | `{file path}` |
| **Line** | {line number(s)} |

**Description:**
{Detailed description of the security issue}

**Evidence:**
```{language}
{Code snippet demonstrating the vulnerability}
```

**Impact:**
{Specific impact - data breach risk, compliance violation, etc.}

**Remediation:**
```{language}
{Corrected code example}
```

**Verification:**
{How to verify the fix is correct}

**References:**
- {OWASP reference}
- {CWE reference}
- {Compliance framework reference}

---

[Continue for each Security finding]

---

### Dimension 2: Structure

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Findings:** {count}
- **Architecture:** {identified pattern}
- **Key Concerns:** {brief summary}

[Findings follow same format]

---

### Dimension 3: Quality

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Average Complexity:** {number}
- **Max Complexity:** {number} in {file}
- **SOLID Violations:** {count}
- **Key Concerns:** {brief summary}

[Findings follow same format]

---

### Dimension 4: Accuracy

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Calculations Audited:** {count}
- **Errors Found:** {count}
- **Key Concerns:** {brief summary}

#### Calculation Verification Results
| Calculation | Location | Expected | Actual | Status |
|-------------|----------|----------|--------|--------|
| {name} | {file:line} | {value} | {value} | ✓/✗ |

[Findings follow same format]

---

### Dimension 5: Documentation

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Stale Comments:** {count}
- **Missing Docs:** {count}
- **Invalid References:** {count}

[Findings follow same format]

---

### Dimension 6: Dependencies

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Total Dependencies:** {count}
- **Vulnerabilities:** {count} ({critical}, {high}, {medium})
- **License Issues:** {count}
- **Outdated:** {count}

#### Vulnerability Summary
| Package | Version | CVE | Severity | Fixed In |
|---------|---------|-----|----------|----------|
| {pkg} | {ver} | {cve} | {sev} | {fix} |

#### License Summary
| License Type | Count | Compatible |
|--------------|-------|------------|
| MIT | X | ✓ |
| Apache-2.0 | X | ✓ |
| GPL-3.0 | X | ⚠ Review |

[Findings follow same format]

---

### Dimension 7: Governance

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Frameworks Assessed:** {list}
- **Compliance Gaps:** {count}

#### Compliance Matrix

##### NIST 800-53
| Control Family | Assessed | Pass | Partial | Fail | N/A |
|---------------|----------|------|---------|------|-----|
| AC (Access Control) | X | X | X | X | X |
| AU (Audit) | X | X | X | X | X |
| IA (Identification) | X | X | X | X | X |
| SC (System/Comms) | X | X | X | X | X |
| SI (System Integrity) | X | X | X | X | X |

##### HIPAA (if applicable)
| Safeguard | Status | Gap |
|-----------|--------|-----|
| §164.312(a) Access Control | PASS/FAIL | {gap} |
| §164.312(b) Audit Controls | PASS/FAIL | {gap} |
| §164.312(c) Integrity | PASS/FAIL | {gap} |
| §164.312(d) Authentication | PASS/FAIL | {gap} |
| §164.312(e) Transmission | PASS/FAIL | {gap} |

##### PCI-DSS (if applicable)
| Requirement | Status | Gap |
|-------------|--------|-----|
| Req 3: Protect CHD | PASS/FAIL | {gap} |
| Req 4: Encrypt Transmission | PASS/FAIL | {gap} |
| Req 6: Secure Development | PASS/FAIL | {gap} |
| Req 8: Authentication | PASS/FAIL | {gap} |
| Req 10: Logging | PASS/FAIL | {gap} |

##### GDPR (if applicable)
| Article | Status | Gap |
|---------|--------|-----|
| Art 5: Principles | PASS/FAIL | {gap} |
| Art 25: Privacy by Design | PASS/FAIL | {gap} |
| Art 32: Security | PASS/FAIL | {gap} |
| Art 17: Right to Erasure | PASS/FAIL | {gap} |

[Findings follow same format]

---

### Dimension 8: Confidentiality

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Data Classifications Found:** {list}
- **Leakage Risks:** {count}
- **Access Control Issues:** {count}

#### Data Classification Matrix
| Data Type | Classification | Location | Protection Status |
|-----------|---------------|----------|-------------------|
| {type} | PII/PHI/PCI | {files} | ✓/⚠/✗ |

[Findings follow same format]

---

### Dimension 9: Intellectual Property

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **License Violations:** {count}
- **Attribution Issues:** {count}
- **Copyright Issues:** {count}

#### License Compatibility
| Dependency License | Project License | Compatible |
|-------------------|-----------------|------------|
| {license} | {license} | ✓/✗ |

[Findings follow same format]

---

### Dimension 10: Input/Output Verification

#### Summary
- **Status:** {PASS/PARTIAL/FAIL}
- **Input Sources:** {count} identified
- **Validation Gaps:** {count}
- **Calculation Errors:** {count}

#### Input Validation Matrix
| Input | Source | Type Check | Range Check | Format Check | Sanitized |
|-------|--------|------------|-------------|--------------|-----------|
| {name} | {source} | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ |

[Findings follow same format]

---

## Remediation Roadmap

### Immediate Actions (Block Deployment)
| Priority | Finding | Action | Owner | Due |
|----------|---------|--------|-------|-----|
| 1 | {finding} | {action} | {owner} | Immediate |

### Before Next Release (7 days)
| Priority | Finding | Action | Owner | Due |
|----------|---------|--------|-------|-----|
| 1 | {finding} | {action} | {owner} | 7 days |

### Short-term (30 days)
| Priority | Finding | Action | Owner | Due |
|----------|---------|--------|-------|-----|
| 1 | {finding} | {action} | {owner} | 30 days |

### Long-term (90 days)
| Priority | Finding | Action | Owner | Due |
|----------|---------|--------|-------|-----|
| 1 | {finding} | {action} | {owner} | 90 days |

---

## Positive Observations

{Note exceptional security practices, well-implemented patterns, and areas of strength.}

---

## Appendices

### A. Files Analyzed
{Complete list of all files included in the audit}

### B. Tools and Scripts Used
- Secret Scanner v1.0
- Compliance Scanner v1.0
- Complexity Analyzer v1.0
- Dependency Auditor v1.0
- License Checker v1.0
- Calculation Verifier v1.0

### C. Glossary
| Term | Definition |
|------|------------|
| PII | Personally Identifiable Information |
| PHI | Protected Health Information |
| CHD | Cardholder Data |
| CVE | Common Vulnerabilities and Exposures |

### D. References
- [NIST 800-53 Rev. 5](https://nvd.nist.gov/800-53)
- [OWASP Top 10](https://owasp.org/Top10/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

---

## Audit Certification

This comprehensive audit has covered all 10 dimensions:
1. ✓ Security
2. ✓ Structure
3. ✓ Quality
4. ✓ Accuracy
5. ✓ Documentation
6. ✓ Dependencies
7. ✓ Governance
8. ✓ Confidentiality
9. ✓ Intellectual Property
10. ✓ Input/Output Verification

All findings are evidence-based with specific code references. This report is suitable for regulatory audit documentation and board-level reporting.

**Auditor:** Claude Code Review Helper
**Date:** {date}
**Report ID:** {uuid}
**Signature:** [DIGITAL SIGNATURE PLACEHOLDER]

---

*This report was generated automatically by Code Review Helper. Critical findings should be validated by qualified security personnel before remediation.*
```

### 6. Generate JSON Report

Write to `{output}.json`:

```json
{
  "metadata": {
    "reportId": "{UUID}",
    "generatedAt": "{ISO 8601}",
    "scope": "{path}",
    "version": "2.0.0",
    "dimensionsCovered": 10
  },
  "summary": {
    "overallAssessment": "NEEDS_REMEDIATION",
    "riskScore": 7,
    "filesAnalyzed": 150,
    "linesOfCode": 25000,
    "totalFindings": 45,
    "findingsBySeverity": {
      "critical": 2,
      "high": 8,
      "medium": 15,
      "low": 12,
      "informational": 8
    },
    "findingsByDimension": {
      "security": {"total": 10, "critical": 2, "high": 3},
      "structure": {"total": 5, "critical": 0, "high": 1},
      "quality": {"total": 8, "critical": 0, "high": 2},
      "accuracy": {"total": 3, "critical": 0, "high": 1},
      "documentation": {"total": 4, "critical": 0, "high": 0},
      "dependencies": {"total": 6, "critical": 0, "high": 2},
      "governance": {"total": 5, "critical": 0, "high": 1},
      "confidentiality": {"total": 3, "critical": 0, "high": 1},
      "intellectualProperty": {"total": 2, "critical": 0, "high": 0},
      "inputOutputVerification": {"total": 4, "critical": 0, "high": 1}
    }
  },
  "dimensions": {
    "security": {
      "status": "PARTIAL",
      "findings": [...]
    },
    "structure": {
      "status": "PASS",
      "findings": [...]
    }
  },
  "findings": [
    {
      "id": "S-001",
      "dimension": "security",
      "severity": "critical",
      "title": "SQL Injection Vulnerability",
      "category": "injection",
      "frameworks": ["NIST SI-10", "PCI-DSS 6.5.1", "OWASP A03"],
      "file": "src/api/users.py",
      "line": 45,
      "description": "User input directly concatenated into SQL query",
      "evidence": "query = f\"SELECT * FROM users WHERE id = {user_id}\"",
      "impact": "Full database compromise, data breach",
      "remediation": "Use parameterized queries",
      "remediationCode": "query = \"SELECT * FROM users WHERE id = %s\"\ncursor.execute(query, (user_id,))",
      "references": ["https://owasp.org/www-community/attacks/SQL_Injection"],
      "status": "open"
    }
  ],
  "compliance": {
    "nist": {
      "assessed": 97,
      "passed": 85,
      "partial": 8,
      "failed": 4,
      "na": 0
    },
    "hipaa": {
      "assessed": 15,
      "passed": 12,
      "partial": 2,
      "failed": 1,
      "na": 0
    },
    "pciDss": {
      "assessed": 12,
      "passed": 10,
      "partial": 1,
      "failed": 1,
      "na": 0
    },
    "gdpr": {
      "assessed": 8,
      "passed": 6,
      "partial": 1,
      "failed": 1,
      "na": 0
    }
  },
  "dependencies": {
    "total": 85,
    "vulnerabilities": {
      "critical": 0,
      "high": 2,
      "medium": 5,
      "low": 8
    },
    "licenses": {
      "permissive": 70,
      "weakCopyleft": 10,
      "strongCopyleft": 3,
      "unknown": 2
    },
    "outdated": {
      "major": 5,
      "minor": 12,
      "patch": 20
    }
  },
  "remediationRoadmap": {
    "immediate": [...],
    "shortTerm": [...],
    "longTerm": [...]
  }
}
```

### 7. Output Files

Write both reports:
1. Use Write tool for `{output}.md`
2. Use Write tool for `{output}.json`

Report the file locations to the user with summary statistics.

## Example Usage

```
/audit-report
/audit-report src/
/audit-report . --output security-audit-2024-01
/audit-report src/api/ --output api-compliance-report
/audit-report . --frameworks hipaa,pci-dss --output healthcare-payment-audit
```
