---
name: compliance-check
description: Run compliance-specific checks against code for regulatory frameworks
argument-hint: "[path] [--framework <name>]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Compliance Check

Run compliance-focused security and regulatory checks against code, supporting NIST, FedRAMP, SOC 2, ISO 27001, HIPAA, and PCI-DSS frameworks.

## Process

### 1. Parse Arguments

**Path:** File or directory to check (default: current directory)

**Framework:** Specific framework to check against
- `nist` - NIST 800-53 controls
- `fedramp` - FedRAMP requirements (builds on NIST)
- `soc2` - SOC 2 Trust Service Criteria
- `iso27001` - ISO 27001 Annex A controls
- `hipaa` - HIPAA Security Rule
- `pci-dss` - PCI-DSS requirements
- `all` - Check all frameworks (default)

### 2. Run Automated Scans

**Secret Scanner:**
```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/check-secrets.sh {path}
```

**Compliance Scanner:**
```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/scan-compliance.py {path} --framework {framework}
```

### 3. Manual Review Points

Based on framework, check for:

**NIST 800-53 / FedRAMP:**
- [ ] AC-2: Account management with audit trail
- [ ] AC-6: Least privilege implementation
- [ ] AU-2/AU-3: Comprehensive audit logging
- [ ] IA-5: Password complexity and hashing
- [ ] SC-8: TLS for transmission
- [ ] SC-13: FIPS-approved cryptography
- [ ] SC-28: Encryption at rest
- [ ] SI-10: Input validation

**SOC 2:**
- [ ] CC6.1: Logical access controls
- [ ] CC6.6: System boundary protection
- [ ] CC6.7: Data transmission encryption
- [ ] CC7.1: Vulnerability detection
- [ ] CC7.2: Security event monitoring

**HIPAA:**
- [ ] §164.312(a): Access control with unique IDs
- [ ] §164.312(b): PHI access audit trail
- [ ] §164.312(c): Data integrity verification
- [ ] §164.312(d): Person authentication
- [ ] §164.312(e): PHI transmission encryption

**PCI-DSS:**
- [ ] Req 3.4: PAN rendered unreadable
- [ ] Req 4.1: TLS 1.2+ for CHD transmission
- [ ] Req 6.5: Secure coding practices
- [ ] Req 8.2: Strong authentication
- [ ] Req 10.2: Audit trail for CHD access

### 4. Generate Compliance Report

```markdown
# Compliance Check Report

## Scan Details
- **Path:** {path}
- **Framework(s):** {framework}
- **Scan Date:** {date}
- **Files Scanned:** {count}

## Executive Summary
[High-level compliance status and risk assessment]

## Automated Scan Results

### Secret Detection
| Type | Severity | File | Line | Status |
|------|----------|------|------|--------|
| {type} | {severity} | {file} | {line} | {status} |

### Pattern-Based Findings
| Rule | Framework | Control | File | Issue |
|------|-----------|---------|------|-------|
| {rule} | {framework} | {control} | {file} | {issue} |

## Control Assessment

### {Framework} Controls

| Control | Status | Evidence | Gap |
|---------|--------|----------|-----|
| {control_id} | PASS/FAIL/PARTIAL | {evidence} | {gap} |

## Findings by Severity

### Critical
[Issues that would cause audit failure]

### High
[Significant compliance gaps]

### Medium
[Partial implementations needing improvement]

### Low
[Minor improvements for better compliance]

### Informational
[Best practice recommendations]

## Remediation Plan

### Immediate Actions (Critical/High)
1. {action with specific guidance}
2. {action with specific guidance}

### Short-term Actions (Medium)
1. {action with timeline}

### Long-term Improvements
1. {enhancement}

## Compliance Status Summary

| Framework | Critical | High | Medium | Low | Status |
|-----------|----------|------|--------|-----|--------|
| NIST | X | X | X | X | PASS/FAIL |
| HIPAA | X | X | X | X | PASS/FAIL |
| PCI-DSS | X | X | X | X | PASS/FAIL |
```

### 5. Framework-Specific Guidance

**For FedRAMP:**
- FIPS 140-2 validated crypto required
- Continuous monitoring evidence needed
- Boundary protection documentation

**For HIPAA:**
- PHI data flows must be documented
- Business associate considerations
- Minimum necessary principle verification

**For PCI-DSS:**
- Cardholder data environment (CDE) scope
- Never store SAD post-authorization
- PAN masking requirements (first 6, last 4)

## Example Usage

```
/compliance-check
/compliance-check src/
/compliance-check --framework hipaa
/compliance-check src/payment/ --framework pci-dss
/compliance-check . --framework all
```
