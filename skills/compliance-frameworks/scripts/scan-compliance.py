#!/usr/bin/env python3
"""
Compliance scanner for code review.
Scans source code for common compliance issues across multiple frameworks.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import List, Optional


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class Framework(Enum):
    NIST = "nist"
    HIPAA = "hipaa"
    PCI_DSS = "pci-dss"
    SOC2 = "soc2"
    ALL = "all"


@dataclass
class Finding:
    rule_id: str
    severity: str
    framework: str
    control: str
    message: str
    file: str
    line: int
    code_snippet: str
    remediation: str


# Compliance rules with patterns
RULES = [
    # Secret Detection (All frameworks)
    {
        "id": "SEC-001",
        "pattern": r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']',
        "severity": Severity.CRITICAL,
        "frameworks": [Framework.ALL],
        "control": "Secret Management",
        "message": "Hardcoded password detected",
        "remediation": "Use environment variables or a secrets manager"
    },
    {
        "id": "SEC-002",
        "pattern": r'(?i)(api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*["\'][a-zA-Z0-9]{16,}["\']',
        "severity": Severity.CRITICAL,
        "frameworks": [Framework.ALL],
        "control": "Secret Management",
        "message": "Hardcoded API key detected",
        "remediation": "Use environment variables or a secrets manager"
    },
    {
        "id": "SEC-003",
        "pattern": r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
        "severity": Severity.CRITICAL,
        "frameworks": [Framework.ALL],
        "control": "Secret Management",
        "message": "Private key in source code",
        "remediation": "Store private keys in secure key management system"
    },
    {
        "id": "SEC-004",
        "pattern": r'AKIA[0-9A-Z]{16}',
        "severity": Severity.CRITICAL,
        "frameworks": [Framework.ALL],
        "control": "Secret Management",
        "message": "AWS access key detected",
        "remediation": "Use IAM roles or AWS Secrets Manager"
    },

    # SQL Injection (PCI-DSS 6.5.1, NIST SI-10)
    {
        "id": "INJ-001",
        "pattern": r'(?i)(execute|cursor\.execute|query)\s*\([^)]*["\'].*(%s|%d|\{|\+).*["\'][^)]*\)',
        "severity": Severity.HIGH,
        "frameworks": [Framework.PCI_DSS, Framework.NIST],
        "control": "PCI-DSS 6.5.1 / NIST SI-10",
        "message": "Potential SQL injection - string formatting in query",
        "remediation": "Use parameterized queries"
    },
    {
        "id": "INJ-002",
        "pattern": r'(?i)f["\'].*SELECT.*FROM.*\{',
        "severity": Severity.HIGH,
        "frameworks": [Framework.PCI_DSS, Framework.NIST],
        "control": "PCI-DSS 6.5.1 / NIST SI-10",
        "message": "SQL injection via f-string",
        "remediation": "Use parameterized queries instead of f-strings"
    },

    # Command Injection
    {
        "id": "INJ-003",
        "pattern": r'(?i)(os\.system|subprocess\.call|subprocess\.run)\s*\([^)]*shell\s*=\s*True',
        "severity": Severity.HIGH,
        "frameworks": [Framework.ALL],
        "control": "Input Validation",
        "message": "Shell=True with subprocess - potential command injection",
        "remediation": "Use shell=False with list of arguments"
    },
    {
        "id": "INJ-004",
        "pattern": r'(?i)eval\s*\([^)]*\)',
        "severity": Severity.HIGH,
        "frameworks": [Framework.ALL],
        "control": "Input Validation",
        "message": "eval() usage - potential code injection",
        "remediation": "Avoid eval(); use safer alternatives"
    },

    # Encryption (PCI-DSS 3.4/4.1, NIST SC-13/SC-28, HIPAA §164.312(e))
    {
        "id": "CRYPTO-001",
        "pattern": r'(?i)(md5|sha1)\s*\(',
        "severity": Severity.MEDIUM,
        "frameworks": [Framework.PCI_DSS, Framework.NIST, Framework.HIPAA],
        "control": "Cryptographic Standards",
        "message": "Weak hashing algorithm (MD5/SHA1)",
        "remediation": "Use SHA-256 or stronger for security purposes"
    },
    {
        "id": "CRYPTO-002",
        "pattern": r'(?i)(des|rc4|blowfish)',
        "severity": Severity.HIGH,
        "frameworks": [Framework.PCI_DSS, Framework.NIST],
        "control": "PCI-DSS 3.4 / NIST SC-13",
        "message": "Weak encryption algorithm",
        "remediation": "Use AES-256 or other approved algorithms"
    },
    {
        "id": "CRYPTO-003",
        "pattern": r'(?i)verify\s*=\s*False',
        "severity": Severity.HIGH,
        "frameworks": [Framework.PCI_DSS, Framework.NIST],
        "control": "PCI-DSS 4.1 / NIST SC-8",
        "message": "TLS certificate verification disabled",
        "remediation": "Enable certificate verification (verify=True)"
    },

    # PII Handling (HIPAA, GDPR)
    {
        "id": "PII-001",
        "pattern": r'(?i)(ssn|social[_-]?security)[^=]*=',
        "severity": Severity.MEDIUM,
        "frameworks": [Framework.HIPAA, Framework.SOC2],
        "control": "PII Handling",
        "message": "SSN field detected - ensure proper encryption",
        "remediation": "Encrypt SSN at rest and mask in logs/display"
    },
    {
        "id": "PII-002",
        "pattern": r'(?i)print\s*\([^)]*(?:ssn|password|card|pan|credit)',
        "severity": Severity.HIGH,
        "frameworks": [Framework.HIPAA, Framework.PCI_DSS],
        "control": "Data Protection",
        "message": "Potential PII/sensitive data in print statement",
        "remediation": "Never print sensitive data; use masked logging"
    },

    # Logging (All frameworks - AU controls)
    {
        "id": "LOG-001",
        "pattern": r'(?i)log(ger)?\.(info|debug|warn|error)\s*\([^)]*(?:password|secret|key|token|card)',
        "severity": Severity.HIGH,
        "frameworks": [Framework.ALL],
        "control": "Audit Logging",
        "message": "Potential sensitive data in logs",
        "remediation": "Mask or exclude sensitive data from logs"
    },

    # Authentication (All frameworks)
    {
        "id": "AUTH-001",
        "pattern": r'(?i)#\s*TODO.*auth',
        "severity": Severity.MEDIUM,
        "frameworks": [Framework.ALL],
        "control": "Authentication",
        "message": "Authentication TODO comment - incomplete implementation",
        "remediation": "Complete authentication implementation"
    },
    {
        "id": "AUTH-002",
        "pattern": r'(?i)if\s+.*==\s*["\']admin["\']',
        "severity": Severity.LOW,
        "frameworks": [Framework.ALL],
        "control": "Access Control",
        "message": "Hardcoded admin check - use role-based access control",
        "remediation": "Implement proper RBAC instead of hardcoded checks"
    },

    # HTTP Security
    {
        "id": "HTTP-001",
        "pattern": r'http://(?!localhost|127\.0\.0\.1)',
        "severity": Severity.MEDIUM,
        "frameworks": [Framework.PCI_DSS, Framework.NIST],
        "control": "PCI-DSS 4.1 / NIST SC-8",
        "message": "Non-HTTPS URL detected",
        "remediation": "Use HTTPS for all external communications"
    },
]


def scan_file(filepath: Path, frameworks: List[Framework]) -> List[Finding]:
    """Scan a single file for compliance issues."""
    findings = []

    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception as e:
        return [Finding(
            rule_id="SCAN-ERR",
            severity=Severity.INFORMATIONAL.value,
            framework="N/A",
            control="N/A",
            message=f"Could not read file: {e}",
            file=str(filepath),
            line=0,
            code_snippet="",
            remediation="Check file permissions and encoding"
        )]

    for rule in RULES:
        # Check if rule applies to selected frameworks
        if Framework.ALL not in rule["frameworks"]:
            if not any(f in frameworks or f == Framework.ALL for f in rule["frameworks"]):
                continue

        pattern = re.compile(rule["pattern"])

        for line_num, line in enumerate(lines, 1):
            if pattern.search(line):
                # Get framework string
                if Framework.ALL in rule["frameworks"]:
                    fw_str = "All"
                else:
                    fw_str = ", ".join(f.value.upper() for f in rule["frameworks"])

                findings.append(Finding(
                    rule_id=rule["id"],
                    severity=rule["severity"].value,
                    framework=fw_str,
                    control=rule["control"],
                    message=rule["message"],
                    file=str(filepath),
                    line=line_num,
                    code_snippet=line.strip()[:100],
                    remediation=rule["remediation"]
                ))

    return findings


def scan_directory(path: Path, frameworks: List[Framework], extensions: List[str]) -> List[Finding]:
    """Recursively scan directory for compliance issues."""
    findings = []

    for filepath in path.rglob('*'):
        if filepath.is_file() and filepath.suffix.lower() in extensions:
            # Skip common non-code directories
            if any(part in filepath.parts for part in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
                continue
            findings.extend(scan_file(filepath, frameworks))

    return findings


def main():
    parser = argparse.ArgumentParser(description='Scan code for compliance issues')
    parser.add_argument('path', help='File or directory to scan')
    parser.add_argument('--framework', '-f', choices=['nist', 'hipaa', 'pci-dss', 'soc2', 'all'],
                       default='all', help='Compliance framework to check')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low', 'informational'],
                       default='low', help='Minimum severity to report')

    args = parser.parse_args()

    # Parse framework
    framework_map = {
        'nist': Framework.NIST,
        'hipaa': Framework.HIPAA,
        'pci-dss': Framework.PCI_DSS,
        'soc2': Framework.SOC2,
        'all': Framework.ALL
    }
    frameworks = [framework_map[args.framework]]

    # Severity filter
    severity_order = ['informational', 'low', 'medium', 'high', 'critical']
    min_severity_idx = severity_order.index(args.severity)

    # Scan
    path = Path(args.path)
    extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rb', '.php', '.cs', '.c', '.cpp', '.h']

    if path.is_file():
        findings = scan_file(path, frameworks)
    else:
        findings = scan_directory(path, frameworks, extensions)

    # Filter by severity
    findings = [f for f in findings if severity_order.index(f.severity) >= min_severity_idx]

    # Sort by severity
    findings.sort(key=lambda f: severity_order.index(f.severity), reverse=True)

    # Output
    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        if not findings:
            print("No compliance issues found.")
            sys.exit(0)

        print(f"\nCompliance Scan Results - {len(findings)} issue(s) found\n")
        print("=" * 80)

        current_severity = None
        for finding in findings:
            if finding.severity != current_severity:
                current_severity = finding.severity
                print(f"\n[{finding.severity.upper()}]")
                print("-" * 40)

            print(f"\n  {finding.rule_id}: {finding.message}")
            print(f"  File: {finding.file}:{finding.line}")
            print(f"  Framework: {finding.framework} ({finding.control})")
            print(f"  Code: {finding.code_snippet}")
            print(f"  Fix: {finding.remediation}")

        print("\n" + "=" * 80)

        # Summary
        by_severity = {}
        for f in findings:
            by_severity[f.severity] = by_severity.get(f.severity, 0) + 1

        print("\nSummary:")
        for sev in ['critical', 'high', 'medium', 'low', 'informational']:
            if sev in by_severity:
                print(f"  {sev.capitalize()}: {by_severity[sev]}")

    # Exit with error if critical/high issues found
    if any(f.severity in ['critical', 'high'] for f in findings):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
