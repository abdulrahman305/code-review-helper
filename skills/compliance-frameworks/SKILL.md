---
name: Compliance Frameworks
description: This skill should be used when the user asks about "compliance", "NIST", "FedRAMP", "SOC 2", "ISO 27001", "HIPAA", "PCI-DSS", "audit", "regulatory requirements", "government standards", "security controls", or when performing compliance-focused code reviews. Provides comprehensive control mappings and code-level compliance requirements for major regulatory frameworks.
version: 1.0.0
---

# Compliance Frameworks

Comprehensive guidance for evaluating code against major regulatory and security compliance frameworks.

## Overview

Compliance reviews verify that code implementations meet specific regulatory requirements. Each framework has unique controls, but many share common security principles. Apply framework-specific checks based on the project's regulatory requirements.

## Supported Frameworks

| Framework | Focus Area | Industries |
|-----------|------------|------------|
| **NIST 800-53** | Federal security controls | US Government, contractors |
| **FedRAMP** | Cloud service authorization | Government cloud providers |
| **SOC 2** | Trust service criteria | SaaS, cloud services |
| **ISO 27001** | Information security management | International enterprises |
| **HIPAA** | Protected health information | Healthcare, health tech |
| **PCI-DSS** | Payment card data | E-commerce, financial |

## Common Code-Level Requirements

### All Frameworks: Core Security Controls

These controls apply across all compliance frameworks:

**Access Control**
- Role-based access control (RBAC) implementation
- Principle of least privilege enforced
- Session management with timeout
- Multi-factor authentication for privileged access

**Audit Logging**
- Security-relevant events logged (login, access, changes)
- Logs include: timestamp, user, action, resource, result
- Log integrity protected (append-only, signed)
- Retention period meets framework requirements

**Data Protection**
- Encryption at rest (AES-256 or equivalent)
- Encryption in transit (TLS 1.2+)
- Key management procedures documented
- Sensitive data classified and handled appropriately

**Input Validation**
- All external input validated
- Parameterized queries for database access
- Output encoding for injection prevention
- File upload restrictions enforced

## Framework-Specific Requirements

### NIST 800-53 / FedRAMP

Key control families for code review:

| Control | Code Requirement |
|---------|-----------------|
| AC-2 | Account management APIs with approval workflow |
| AC-6 | Privilege escalation prevention |
| AU-2 | Comprehensive audit event logging |
| AU-3 | Audit record content (who, what, when, where, outcome) |
| IA-5 | Password complexity and hashing |
| SC-8 | Transmission confidentiality (TLS) |
| SC-13 | Cryptographic protection (FIPS 140-2 approved) |
| SC-28 | Data at rest protection |
| SI-10 | Input validation checks |

**FedRAMP Specific:**
- FIPS 140-2 validated cryptographic modules required
- Continuous monitoring implementation
- Boundary protection at system interfaces

### SOC 2 Trust Service Criteria

| Criteria | Code Requirement |
|----------|-----------------|
| CC6.1 | Logical access controls implemented |
| CC6.2 | Access provisioning/deprovisioning |
| CC6.3 | Role-based access enforcement |
| CC6.6 | System boundary protection |
| CC6.7 | Data transmission encryption |
| CC7.1 | Vulnerability detection mechanisms |
| CC7.2 | Security event monitoring |

### ISO 27001 Annex A Controls

| Control | Code Requirement |
|---------|-----------------|
| A.9.2 | User access management |
| A.9.4 | System access control |
| A.10.1 | Cryptographic controls |
| A.12.2 | Protection from malware |
| A.12.4 | Logging and monitoring |
| A.14.2 | Security in development |

### HIPAA Security Rule

| Standard | Code Requirement |
|----------|-----------------|
| Access Control (§164.312(a)) | Unique user IDs, automatic logoff |
| Audit Controls (§164.312(b)) | PHI access logging |
| Integrity (§164.312(c)) | Data integrity verification |
| Transmission (§164.312(e)) | Encryption for PHI transmission |
| Person Auth (§164.312(d)) | Identity verification |

**PHI Handling:**
- Minimum necessary access enforced
- PHI encrypted in all states
- Audit trail for all PHI access
- De-identification where possible

### PCI-DSS Requirements

| Requirement | Code Implementation |
|-------------|---------------------|
| 3.4 | PAN encryption (not hashing alone) |
| 3.5 | Key management procedures |
| 4.1 | TLS 1.2+ for cardholder data |
| 6.5 | Secure coding practices |
| 8.2 | Strong authentication |
| 10.2 | Audit trail for cardholder access |

**Cardholder Data:**
- Never log full PAN
- Mask displayed PAN (first 6, last 4 only)
- Encrypt PAN storage
- No SAD after authorization

## Compliance Check Process

### 1. Identify Applicable Frameworks

Determine which frameworks apply based on:
- Industry (healthcare → HIPAA, payments → PCI-DSS)
- Customers (government → FedRAMP/NIST)
- Geography (EU → GDPR considerations)
- Contractual requirements (SOC 2 reports)

### 2. Map Code to Controls

For each relevant control:
1. Identify code components that implement the control
2. Verify implementation meets control requirements
3. Document evidence of compliance
4. Note gaps requiring remediation

### 3. Document Findings

Use 5-tier severity:
- **Critical**: Direct compliance violation, audit failure
- **High**: Significant gap, requires remediation
- **Medium**: Partial implementation, improvement needed
- **Low**: Minor enhancement recommended
- **Informational**: Documentation improvement

## Utility Scripts

### Compliance Scanner

Run `${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/scan-compliance.py` for automated compliance checks:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/scan-compliance.py <path> --framework <framework>
```

### Secret Scanner

Run `${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/check-secrets.sh` to detect hardcoded secrets:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/compliance-frameworks/scripts/check-secrets.sh <path>
```

## Additional Resources

### Reference Files

For detailed control mappings and requirements:
- **`references/nist-controls.md`** - Full NIST 800-53 code-relevant controls
- **`references/hipaa-requirements.md`** - Detailed HIPAA technical safeguards
- **`references/pci-dss-requirements.md`** - PCI-DSS implementation requirements

### Audit Report Generation

Generate formal audit reports using the `/audit-report` command, which produces both Markdown and JSON output documenting compliance status, findings, and remediation guidance.
