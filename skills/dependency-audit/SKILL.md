---
name: Dependency Audit
description: This skill should be used when auditing library imports, dependencies, licenses, vulnerabilities, and version management. Use for "audit dependencies", "check licenses", "scan vulnerabilities", "review imports", "check packages", or when analyzing package.json, requirements.txt, Cargo.toml, go.mod, or similar dependency files.
version: 1.0.0
---

# Dependency Audit Skill

Comprehensive dependency auditing for security vulnerabilities, license compliance, version management, and import analysis.

## Overview

This skill provides deep auditing of all project dependencies including:
- Security vulnerability scanning (CVE databases)
- License compliance verification
- Version management analysis
- Import usage verification
- Transitive dependency analysis
- Supply chain security checks

## Audit Dimensions

### 1. Security Vulnerability Audit

**CVE Database Checks:**
- National Vulnerability Database (NVD)
- GitHub Advisory Database
- Snyk Vulnerability Database
- OSV (Open Source Vulnerabilities)

**Risk Assessment:**
- CVSS scoring (Critical/High/Medium/Low)
- Exploitability analysis
- Impact assessment
- Available patches/fixes

### 2. License Compliance Audit

**License Categories:**

| Category | Licenses | Obligations |
|----------|----------|-------------|
| **Permissive** | MIT, BSD, Apache 2.0, ISC | Attribution required |
| **Weak Copyleft** | LGPL, MPL | Link/file-level copyleft |
| **Strong Copyleft** | GPL, AGPL | Full source disclosure |
| **Proprietary** | Commercial | License required |
| **Public Domain** | CC0, Unlicense | No obligations |

**Compatibility Matrix:**
- MIT + Apache: Compatible
- MIT + GPL: Compatible (result is GPL)
- Apache + GPL v2: INCOMPATIBLE
- Apache + GPL v3: Compatible

**Audit Checks:**
- License identification for all dependencies
- License compatibility with project license
- Attribution requirements met
- Copyleft obligations identified
- Commercial license compliance

### 3. Version Management Audit

**Versioning Best Practices:**
- Semantic versioning compliance
- Version pinning strategy
- Lock file presence and accuracy
- Outdated dependency identification
- Breaking change risk assessment

**Version States:**
| State | Risk | Action |
|-------|------|--------|
| **Current** | Low | Monitor |
| **Minor Behind** | Low | Plan update |
| **Major Behind** | Medium | Schedule update |
| **Deprecated** | High | Replace urgently |
| **Abandoned** | Critical | Replace immediately |

### 4. Import Analysis

**Checks:**
- Unused imports (dead code)
- Missing imports
- Circular imports
- Import security (trusted sources)
- Import organization

**Language-Specific Patterns:**

**Python:**
```python
# Good: Specific imports
from typing import List, Optional
from datetime import datetime

# Bad: Wildcard imports
from os import *
```

**JavaScript/TypeScript:**
```javascript
// Good: Named imports
import { useState, useEffect } from 'react';

// Bad: Default import when named available
import React from 'react';
const { useState } = React;
```

### 5. Supply Chain Security

**Threats:**
- Dependency confusion attacks
- Typosquatting
- Compromised maintainers
- Malicious packages
- Build system attacks

**Mitigation Checks:**
- Package source verification
- Integrity checking (checksums, signatures)
- Maintainer reputation
- Package age and activity
- Download counts and popularity

## Scripts

### Dependency Scanner

Use `${CLAUDE_PLUGIN_ROOT}/skills/dependency-audit/scripts/audit-dependencies.py` to scan dependencies:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/dependency-audit/scripts/audit-dependencies.py <path> --format json
```

**Options:**
- `--format`: Output format (text, json, sarif)
- `--severity`: Minimum severity to report (critical, high, medium, low)
- `--check-licenses`: Include license audit
- `--check-outdated`: Include version audit

### License Checker

Use `${CLAUDE_PLUGIN_ROOT}/skills/dependency-audit/scripts/check-licenses.py` to audit licenses:

```bash
python ${CLAUDE_PLUGIN_ROOT}/skills/dependency-audit/scripts/check-licenses.py <path> --project-license MIT
```

**Options:**
- `--project-license`: Your project's license for compatibility check
- `--format`: Output format (text, json)
- `--strict`: Fail on any copyleft license

## Package Manager Support

### npm/yarn (JavaScript)
```bash
# Security audit
npm audit --json
yarn audit --json

# Outdated check
npm outdated --json
yarn outdated --json

# License check
npx license-checker --json
```

### pip (Python)
```bash
# Security audit
pip-audit --format=json

# Outdated check
pip list --outdated --format=json

# License check
pip-licenses --format=json
```

### Cargo (Rust)
```bash
# Security audit
cargo audit --json

# Outdated check
cargo outdated --format=json
```

### Go modules
```bash
# Security audit
govulncheck ./...

# Outdated check
go list -u -m all
```

### Maven/Gradle (Java)
```bash
# OWASP dependency check
mvn org.owasp:dependency-check-maven:check

# Outdated check
mvn versions:display-dependency-updates
```

## Output Format

### Vulnerability Report
```json
{
  "vulnerabilities": [
    {
      "package": "lodash",
      "version": "4.17.15",
      "vulnerability": "CVE-2020-8203",
      "severity": "high",
      "cvss": 7.4,
      "title": "Prototype Pollution",
      "description": "...",
      "fixedIn": "4.17.19",
      "references": ["https://nvd.nist.gov/vuln/detail/CVE-2020-8203"]
    }
  ]
}
```

### License Report
```json
{
  "licenses": [
    {
      "package": "react",
      "version": "18.2.0",
      "license": "MIT",
      "category": "permissive",
      "compatible": true,
      "attribution": "Copyright (c) Meta Platforms, Inc."
    }
  ],
  "summary": {
    "total": 150,
    "permissive": 140,
    "copyleft": 8,
    "unknown": 2,
    "compatible": true
  }
}
```

## Integration with Audit Reports

When generating audit reports, include:

```markdown
## Dependency Audit

### Security Vulnerabilities
| Package | Version | CVE | Severity | Fixed In |
|---------|---------|-----|----------|----------|
| lodash | 4.17.15 | CVE-2020-8203 | High | 4.17.19 |

### License Compliance
| License Type | Count | Status |
|--------------|-------|--------|
| MIT | 85 | ✓ Compatible |
| Apache 2.0 | 32 | ✓ Compatible |
| GPL 3.0 | 3 | ⚠ Review Required |

### Outdated Dependencies
| Package | Current | Latest | Risk |
|---------|---------|--------|------|
| webpack | 4.46.0 | 5.88.0 | Major |

### Supply Chain
- Lock file: ✓ Present
- Integrity: ✓ Verified
- Sources: ✓ Trusted registries only
```

## Common Issues

### Critical
- Known CVE with available exploit
- GPL dependency in proprietary project
- Abandoned dependency with security issues
- Dependency confusion vulnerability

### High
- High severity CVE without exploit
- License incompatibility
- Multiple major versions behind
- Deprecated dependency

### Medium
- Medium severity CVE
- Missing attribution
- Minor versions behind
- Unused dependencies

### Low
- Low severity CVE
- Suboptimal version pinning
- Development dependencies in production
