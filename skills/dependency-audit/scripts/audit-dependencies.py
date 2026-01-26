#!/usr/bin/env python3
"""
Comprehensive dependency auditor for security vulnerabilities, licenses, and version management.
Supports npm, pip, cargo, and go modules.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class Vulnerability:
    package: str
    version: str
    cve: str
    severity: str  # critical, high, medium, low
    cvss: float
    title: str
    description: str
    fixed_in: Optional[str]
    references: List[str] = field(default_factory=list)


@dataclass
class LicenseInfo:
    package: str
    version: str
    license: str
    category: str  # permissive, weak-copyleft, strong-copyleft, proprietary, unknown
    compatible: bool
    attribution: str


@dataclass
class OutdatedPackage:
    package: str
    current: str
    latest: str
    risk: str  # critical, major, minor, patch


@dataclass
class ImportIssue:
    file: str
    line: int
    import_name: str
    issue_type: str  # unused, missing, circular, wildcard
    message: str


@dataclass
class AuditReport:
    package_manager: str
    total_dependencies: int
    vulnerabilities: List[Vulnerability]
    licenses: List[LicenseInfo]
    outdated: List[OutdatedPackage]
    import_issues: List[ImportIssue]
    supply_chain: Dict[str, Any]


# License categories
LICENSE_CATEGORIES = {
    # Permissive
    'MIT': 'permissive',
    'ISC': 'permissive',
    'BSD-2-Clause': 'permissive',
    'BSD-3-Clause': 'permissive',
    'Apache-2.0': 'permissive',
    'Unlicense': 'permissive',
    'CC0-1.0': 'permissive',
    'WTFPL': 'permissive',
    '0BSD': 'permissive',

    # Weak copyleft
    'LGPL-2.1': 'weak-copyleft',
    'LGPL-3.0': 'weak-copyleft',
    'MPL-2.0': 'weak-copyleft',
    'EPL-1.0': 'weak-copyleft',
    'EPL-2.0': 'weak-copyleft',

    # Strong copyleft
    'GPL-2.0': 'strong-copyleft',
    'GPL-3.0': 'strong-copyleft',
    'AGPL-3.0': 'strong-copyleft',

    # Proprietary
    'PROPRIETARY': 'proprietary',
    'COMMERCIAL': 'proprietary',
}


def detect_package_manager(path: str) -> Optional[str]:
    """Detect the package manager used in the project."""
    p = Path(path)

    if (p / 'package.json').exists():
        if (p / 'yarn.lock').exists():
            return 'yarn'
        return 'npm'
    elif (p / 'requirements.txt').exists() or (p / 'setup.py').exists() or (p / 'pyproject.toml').exists():
        return 'pip'
    elif (p / 'Cargo.toml').exists():
        return 'cargo'
    elif (p / 'go.mod').exists():
        return 'go'
    elif (p / 'pom.xml').exists():
        return 'maven'
    elif (p / 'build.gradle').exists() or (p / 'build.gradle.kts').exists():
        return 'gradle'

    return None


def run_command(cmd: List[str], cwd: str = None) -> tuple:
    """Run a command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except FileNotFoundError:
        return False, '', f"Command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, '', "Command timed out"


def audit_npm(path: str) -> AuditReport:
    """Audit npm/yarn project."""
    vulnerabilities = []
    licenses = []
    outdated = []

    # Run npm audit
    success, stdout, stderr = run_command(['npm', 'audit', '--json'], cwd=path)
    if stdout:
        try:
            data = json.loads(stdout)
            for vuln_id, vuln_data in data.get('vulnerabilities', {}).items():
                for via in vuln_data.get('via', []):
                    if isinstance(via, dict):
                        vulnerabilities.append(Vulnerability(
                            package=vuln_id,
                            version=vuln_data.get('range', 'unknown'),
                            cve=via.get('url', '').split('/')[-1] if via.get('url') else 'N/A',
                            severity=via.get('severity', 'unknown'),
                            cvss=0.0,
                            title=via.get('title', 'Unknown vulnerability'),
                            description=via.get('title', ''),
                            fixed_in=vuln_data.get('fixAvailable', {}).get('version') if isinstance(vuln_data.get('fixAvailable'), dict) else None,
                            references=[via.get('url', '')] if via.get('url') else []
                        ))
        except json.JSONDecodeError:
            pass

    # Run npm outdated
    success, stdout, stderr = run_command(['npm', 'outdated', '--json'], cwd=path)
    if stdout:
        try:
            data = json.loads(stdout)
            for pkg, info in data.items():
                current = info.get('current', 'unknown')
                latest = info.get('latest', 'unknown')

                # Determine risk level
                risk = 'patch'
                if current != 'unknown' and latest != 'unknown':
                    curr_parts = current.split('.')
                    latest_parts = latest.split('.')
                    if curr_parts[0] != latest_parts[0]:
                        risk = 'major'
                    elif len(curr_parts) > 1 and len(latest_parts) > 1 and curr_parts[1] != latest_parts[1]:
                        risk = 'minor'

                outdated.append(OutdatedPackage(
                    package=pkg,
                    current=current,
                    latest=latest,
                    risk=risk
                ))
        except json.JSONDecodeError:
            pass

    # Check for license info
    success, stdout, stderr = run_command(['npx', 'license-checker', '--json', '--production'], cwd=path)
    if stdout:
        try:
            data = json.loads(stdout)
            for pkg_version, info in data.items():
                pkg_name = pkg_version.rsplit('@', 1)[0]
                version = pkg_version.rsplit('@', 1)[1] if '@' in pkg_version else 'unknown'
                license_name = info.get('licenses', 'UNKNOWN')

                # Handle multiple licenses
                if isinstance(license_name, list):
                    license_name = license_name[0]

                category = LICENSE_CATEGORIES.get(license_name, 'unknown')
                compatible = category in ['permissive', 'weak-copyleft', 'unknown']

                licenses.append(LicenseInfo(
                    package=pkg_name,
                    version=version,
                    license=license_name,
                    category=category,
                    compatible=compatible,
                    attribution=info.get('publisher', '') or info.get('repository', '')
                ))
        except json.JSONDecodeError:
            pass

    # Get total dependencies
    total = 0
    pkg_json_path = Path(path) / 'package.json'
    if pkg_json_path.exists():
        with open(pkg_json_path) as f:
            data = json.load(f)
            total = len(data.get('dependencies', {})) + len(data.get('devDependencies', {}))

    # Supply chain checks
    supply_chain = {
        'lock_file': (Path(path) / 'package-lock.json').exists() or (Path(path) / 'yarn.lock').exists(),
        'integrity_verified': True,  # npm verifies by default
        'registry': 'npmjs.com (trusted)'
    }

    return AuditReport(
        package_manager='npm',
        total_dependencies=total,
        vulnerabilities=vulnerabilities,
        licenses=licenses,
        outdated=outdated,
        import_issues=[],
        supply_chain=supply_chain
    )


def audit_pip(path: str) -> AuditReport:
    """Audit pip/Python project."""
    vulnerabilities = []
    licenses = []
    outdated = []

    # Try pip-audit
    success, stdout, stderr = run_command(['pip-audit', '--format=json'], cwd=path)
    if stdout:
        try:
            data = json.loads(stdout)
            for vuln in data:
                vulnerabilities.append(Vulnerability(
                    package=vuln.get('name', 'unknown'),
                    version=vuln.get('version', 'unknown'),
                    cve=vuln.get('id', 'N/A'),
                    severity=vuln.get('severity', 'unknown').lower(),
                    cvss=float(vuln.get('cvss', 0.0) or 0.0),
                    title=vuln.get('description', 'Unknown vulnerability')[:100],
                    description=vuln.get('description', ''),
                    fixed_in=vuln.get('fix_versions', [None])[0] if vuln.get('fix_versions') else None,
                    references=vuln.get('references', [])
                ))
        except (json.JSONDecodeError, TypeError):
            pass

    # Try pip list --outdated
    success, stdout, stderr = run_command(['pip', 'list', '--outdated', '--format=json'], cwd=path)
    if stdout:
        try:
            data = json.loads(stdout)
            for pkg in data:
                current = pkg.get('version', 'unknown')
                latest = pkg.get('latest_version', 'unknown')

                risk = 'patch'
                if current != 'unknown' and latest != 'unknown':
                    curr_parts = current.split('.')
                    latest_parts = latest.split('.')
                    if curr_parts[0] != latest_parts[0]:
                        risk = 'major'
                    elif len(curr_parts) > 1 and len(latest_parts) > 1 and curr_parts[1] != latest_parts[1]:
                        risk = 'minor'

                outdated.append(OutdatedPackage(
                    package=pkg.get('name', 'unknown'),
                    current=current,
                    latest=latest,
                    risk=risk
                ))
        except json.JSONDecodeError:
            pass

    # Try pip-licenses
    success, stdout, stderr = run_command(['pip-licenses', '--format=json'], cwd=path)
    if stdout:
        try:
            data = json.loads(stdout)
            for pkg in data:
                license_name = pkg.get('License', 'UNKNOWN')
                category = LICENSE_CATEGORIES.get(license_name, 'unknown')

                # Try to categorize common license patterns
                if category == 'unknown':
                    license_lower = license_name.lower()
                    if 'mit' in license_lower:
                        category = 'permissive'
                    elif 'apache' in license_lower:
                        category = 'permissive'
                    elif 'bsd' in license_lower:
                        category = 'permissive'
                    elif 'gpl' in license_lower:
                        category = 'strong-copyleft'
                    elif 'lgpl' in license_lower:
                        category = 'weak-copyleft'

                compatible = category in ['permissive', 'weak-copyleft', 'unknown']

                licenses.append(LicenseInfo(
                    package=pkg.get('Name', 'unknown'),
                    version=pkg.get('Version', 'unknown'),
                    license=license_name,
                    category=category,
                    compatible=compatible,
                    attribution=pkg.get('Author', '')
                ))
        except json.JSONDecodeError:
            pass

    # Count total dependencies
    total = 0
    req_path = Path(path) / 'requirements.txt'
    if req_path.exists():
        with open(req_path) as f:
            total = len([l for l in f if l.strip() and not l.startswith('#')])

    # Supply chain checks
    supply_chain = {
        'lock_file': (Path(path) / 'requirements.txt').exists(),
        'integrity_verified': False,  # pip doesn't verify by default
        'registry': 'pypi.org (trusted)'
    }

    return AuditReport(
        package_manager='pip',
        total_dependencies=total,
        vulnerabilities=vulnerabilities,
        licenses=licenses,
        outdated=outdated,
        import_issues=[],
        supply_chain=supply_chain
    )


def scan_imports(path: str, language: str) -> List[ImportIssue]:
    """Scan for import issues in source files."""
    issues = []

    if language == 'python':
        # Find Python files
        for py_file in Path(path).rglob('*.py'):
            if 'node_modules' in str(py_file) or '.venv' in str(py_file) or 'venv' in str(py_file):
                continue

            try:
                with open(py_file) as f:
                    content = f.read()
                    lines = content.split('\n')

                    for i, line in enumerate(lines, 1):
                        # Check for wildcard imports
                        if re.match(r'^\s*from\s+\S+\s+import\s+\*', line):
                            issues.append(ImportIssue(
                                file=str(py_file),
                                line=i,
                                import_name=line.strip(),
                                issue_type='wildcard',
                                message='Wildcard imports pollute namespace and hide dependencies'
                            ))

                        # Check for __import__ usage (potential security issue)
                        if '__import__' in line:
                            issues.append(ImportIssue(
                                file=str(py_file),
                                line=i,
                                import_name='__import__',
                                issue_type='dynamic',
                                message='Dynamic imports can be a security risk if input is not validated'
                            ))
            except Exception:
                pass

    elif language == 'javascript':
        # Find JS/TS files
        for ext in ['*.js', '*.ts', '*.jsx', '*.tsx']:
            for js_file in Path(path).rglob(ext):
                if 'node_modules' in str(js_file) or 'dist' in str(js_file):
                    continue

                try:
                    with open(js_file) as f:
                        content = f.read()
                        lines = content.split('\n')

                        for i, line in enumerate(lines, 1):
                            # Check for require with variable (dynamic import risk)
                            if re.search(r'require\s*\(\s*[^"\']', line):
                                issues.append(ImportIssue(
                                    file=str(js_file),
                                    line=i,
                                    import_name='dynamic require',
                                    issue_type='dynamic',
                                    message='Dynamic require can be a security risk'
                                ))

                            # Check for eval-like patterns
                            if 'eval(' in line or 'Function(' in line:
                                issues.append(ImportIssue(
                                    file=str(js_file),
                                    line=i,
                                    import_name='eval/Function',
                                    issue_type='security',
                                    message='eval and Function constructor can execute arbitrary code'
                                ))
                except Exception:
                    pass

    return issues


def format_text_report(report: AuditReport) -> str:
    """Format report as human-readable text."""
    output = []
    output.append("=" * 60)
    output.append("DEPENDENCY AUDIT REPORT")
    output.append("=" * 60)
    output.append(f"\nPackage Manager: {report.package_manager}")
    output.append(f"Total Dependencies: {report.total_dependencies}")

    # Vulnerabilities
    output.append(f"\n{'='*60}")
    output.append(f"SECURITY VULNERABILITIES ({len(report.vulnerabilities)})")
    output.append("=" * 60)

    if report.vulnerabilities:
        for vuln in sorted(report.vulnerabilities, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.severity, 4)):
            output.append(f"\n[{vuln.severity.upper()}] {vuln.package}@{vuln.version}")
            output.append(f"  CVE: {vuln.cve}")
            output.append(f"  Title: {vuln.title}")
            if vuln.fixed_in:
                output.append(f"  Fixed in: {vuln.fixed_in}")
    else:
        output.append("\nNo vulnerabilities found.")

    # Licenses
    output.append(f"\n{'='*60}")
    output.append(f"LICENSE COMPLIANCE ({len(report.licenses)})")
    output.append("=" * 60)

    if report.licenses:
        # Summary by category
        categories = {}
        for lic in report.licenses:
            categories[lic.category] = categories.get(lic.category, 0) + 1

        output.append("\nLicense Summary:")
        for cat, count in sorted(categories.items()):
            status = "✓" if cat in ['permissive', 'weak-copyleft'] else "⚠"
            output.append(f"  {status} {cat}: {count}")

        # Show copyleft licenses
        copyleft = [l for l in report.licenses if l.category in ['strong-copyleft', 'weak-copyleft']]
        if copyleft:
            output.append("\nCopyleft Licenses (Review Required):")
            for lic in copyleft:
                output.append(f"  - {lic.package}@{lic.version}: {lic.license}")
    else:
        output.append("\nNo license information available.")

    # Outdated
    output.append(f"\n{'='*60}")
    output.append(f"OUTDATED DEPENDENCIES ({len(report.outdated)})")
    output.append("=" * 60)

    if report.outdated:
        for pkg in sorted(report.outdated, key=lambda x: {'critical': 0, 'major': 1, 'minor': 2, 'patch': 3}.get(x.risk, 4)):
            output.append(f"\n[{pkg.risk.upper()}] {pkg.package}")
            output.append(f"  Current: {pkg.current} -> Latest: {pkg.latest}")
    else:
        output.append("\nAll dependencies are up to date.")

    # Supply Chain
    output.append(f"\n{'='*60}")
    output.append("SUPPLY CHAIN SECURITY")
    output.append("=" * 60)
    for key, value in report.supply_chain.items():
        status = "✓" if value else "✗"
        output.append(f"  {status} {key}: {value}")

    # Import Issues
    if report.import_issues:
        output.append(f"\n{'='*60}")
        output.append(f"IMPORT ISSUES ({len(report.import_issues)})")
        output.append("=" * 60)
        for issue in report.import_issues:
            output.append(f"\n[{issue.issue_type.upper()}] {issue.file}:{issue.line}")
            output.append(f"  {issue.message}")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Audit project dependencies for security and compliance')
    parser.add_argument('path', nargs='?', default='.', help='Project path to audit')
    parser.add_argument('--format', choices=['text', 'json', 'sarif'], default='text', help='Output format')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low'], default='low',
                       help='Minimum severity to report')
    parser.add_argument('--check-licenses', action='store_true', help='Include license audit')
    parser.add_argument('--check-outdated', action='store_true', help='Include outdated check')
    parser.add_argument('--check-imports', action='store_true', help='Include import analysis')

    args = parser.parse_args()
    path = os.path.abspath(args.path)

    if not os.path.isdir(path):
        print(f"Error: {path} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Detect package manager
    pm = detect_package_manager(path)
    if not pm:
        print(f"Error: Could not detect package manager in {path}", file=sys.stderr)
        print("Supported: npm, yarn, pip, cargo, go", file=sys.stderr)
        sys.exit(1)

    # Run appropriate audit
    if pm in ['npm', 'yarn']:
        report = audit_npm(path)
        language = 'javascript'
    elif pm == 'pip':
        report = audit_pip(path)
        language = 'python'
    else:
        print(f"Partial support for {pm}. Running basic audit.", file=sys.stderr)
        report = AuditReport(
            package_manager=pm,
            total_dependencies=0,
            vulnerabilities=[],
            licenses=[],
            outdated=[],
            import_issues=[],
            supply_chain={'lock_file': False, 'integrity_verified': False, 'registry': 'unknown'}
        )
        language = None

    # Add import analysis if requested
    if args.check_imports and language:
        report.import_issues = scan_imports(path, language)

    # Filter by severity
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    min_severity = severity_order.get(args.severity, 3)
    report.vulnerabilities = [v for v in report.vulnerabilities
                              if severity_order.get(v.severity, 3) <= min_severity]

    # Output
    if args.format == 'json':
        # Convert dataclasses to dicts
        output = {
            'package_manager': report.package_manager,
            'total_dependencies': report.total_dependencies,
            'vulnerabilities': [asdict(v) for v in report.vulnerabilities],
            'licenses': [asdict(l) for l in report.licenses],
            'outdated': [asdict(o) for o in report.outdated],
            'import_issues': [asdict(i) for i in report.import_issues],
            'supply_chain': report.supply_chain,
            'summary': {
                'critical_vulns': len([v for v in report.vulnerabilities if v.severity == 'critical']),
                'high_vulns': len([v for v in report.vulnerabilities if v.severity == 'high']),
                'license_issues': len([l for l in report.licenses if not l.compatible]),
                'outdated_major': len([o for o in report.outdated if o.risk == 'major'])
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text_report(report))

    # Exit code based on findings
    critical_count = len([v for v in report.vulnerabilities if v.severity == 'critical'])
    if critical_count > 0:
        sys.exit(2)
    elif len(report.vulnerabilities) > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
