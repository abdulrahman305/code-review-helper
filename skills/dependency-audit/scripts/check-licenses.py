#!/usr/bin/env python3
"""
License compliance checker for project dependencies and source files.
Checks for license compatibility, attribution requirements, and IP compliance.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
from pathlib import Path


@dataclass
class LicenseInfo:
    name: str
    spdx_id: str
    category: str  # permissive, weak-copyleft, strong-copyleft, proprietary, unknown
    obligations: List[str]
    compatible_with: List[str]
    incompatible_with: List[str]


@dataclass
class LicenseFinding:
    file: str
    line: int
    license: str
    category: str
    issue: Optional[str]
    severity: str  # critical, high, medium, low, info


@dataclass
class AttributionIssue:
    package: str
    license: str
    required: str
    found: bool
    location: Optional[str]


# Comprehensive license database
LICENSE_DB: Dict[str, LicenseInfo] = {
    'MIT': LicenseInfo(
        name='MIT License',
        spdx_id='MIT',
        category='permissive',
        obligations=['Include copyright notice', 'Include license text'],
        compatible_with=['Apache-2.0', 'GPL-2.0', 'GPL-3.0', 'BSD-2-Clause', 'BSD-3-Clause'],
        incompatible_with=[]
    ),
    'Apache-2.0': LicenseInfo(
        name='Apache License 2.0',
        spdx_id='Apache-2.0',
        category='permissive',
        obligations=['Include copyright notice', 'Include license text', 'State changes', 'Include NOTICE file'],
        compatible_with=['MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'GPL-3.0'],
        incompatible_with=['GPL-2.0']  # Due to patent clause
    ),
    'GPL-2.0': LicenseInfo(
        name='GNU General Public License v2.0',
        spdx_id='GPL-2.0',
        category='strong-copyleft',
        obligations=['Disclose source', 'License derivatives as GPL-2.0', 'Include copyright notice'],
        compatible_with=['MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'LGPL-2.1'],
        incompatible_with=['Apache-2.0', 'GPL-3.0']
    ),
    'GPL-3.0': LicenseInfo(
        name='GNU General Public License v3.0',
        spdx_id='GPL-3.0',
        category='strong-copyleft',
        obligations=['Disclose source', 'License derivatives as GPL-3.0', 'Include copyright notice', 'Provide installation information'],
        compatible_with=['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'LGPL-3.0'],
        incompatible_with=['GPL-2.0-only']
    ),
    'LGPL-2.1': LicenseInfo(
        name='GNU Lesser General Public License v2.1',
        spdx_id='LGPL-2.1',
        category='weak-copyleft',
        obligations=['Disclose source for library modifications', 'Allow reverse engineering', 'Include copyright notice'],
        compatible_with=['MIT', 'BSD-2-Clause', 'BSD-3-Clause', 'GPL-2.0'],
        incompatible_with=[]
    ),
    'LGPL-3.0': LicenseInfo(
        name='GNU Lesser General Public License v3.0',
        spdx_id='LGPL-3.0',
        category='weak-copyleft',
        obligations=['Disclose source for library modifications', 'Allow reverse engineering', 'Include copyright notice'],
        compatible_with=['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'GPL-3.0'],
        incompatible_with=[]
    ),
    'BSD-2-Clause': LicenseInfo(
        name='BSD 2-Clause "Simplified" License',
        spdx_id='BSD-2-Clause',
        category='permissive',
        obligations=['Include copyright notice', 'Include license text'],
        compatible_with=['MIT', 'Apache-2.0', 'GPL-2.0', 'GPL-3.0'],
        incompatible_with=[]
    ),
    'BSD-3-Clause': LicenseInfo(
        name='BSD 3-Clause "New" or "Revised" License',
        spdx_id='BSD-3-Clause',
        category='permissive',
        obligations=['Include copyright notice', 'Include license text', 'No endorsement clause'],
        compatible_with=['MIT', 'Apache-2.0', 'GPL-2.0', 'GPL-3.0'],
        incompatible_with=[]
    ),
    'MPL-2.0': LicenseInfo(
        name='Mozilla Public License 2.0',
        spdx_id='MPL-2.0',
        category='weak-copyleft',
        obligations=['Disclose source for modified files', 'Include copyright notice'],
        compatible_with=['MIT', 'Apache-2.0', 'GPL-2.0', 'GPL-3.0'],
        incompatible_with=[]
    ),
    'AGPL-3.0': LicenseInfo(
        name='GNU Affero General Public License v3.0',
        spdx_id='AGPL-3.0',
        category='strong-copyleft',
        obligations=['Disclose source', 'License derivatives as AGPL-3.0', 'Network use is distribution'],
        compatible_with=['GPL-3.0'],
        incompatible_with=['MIT', 'Apache-2.0', 'proprietary']  # If combined
    ),
    'ISC': LicenseInfo(
        name='ISC License',
        spdx_id='ISC',
        category='permissive',
        obligations=['Include copyright notice'],
        compatible_with=['MIT', 'Apache-2.0', 'GPL-2.0', 'GPL-3.0'],
        incompatible_with=[]
    ),
    'Unlicense': LicenseInfo(
        name='The Unlicense',
        spdx_id='Unlicense',
        category='permissive',
        obligations=[],
        compatible_with=['MIT', 'Apache-2.0', 'GPL-2.0', 'GPL-3.0'],
        incompatible_with=[]
    ),
    'CC0-1.0': LicenseInfo(
        name='Creative Commons Zero v1.0 Universal',
        spdx_id='CC0-1.0',
        category='permissive',
        obligations=[],
        compatible_with=['MIT', 'Apache-2.0', 'GPL-2.0', 'GPL-3.0'],
        incompatible_with=[]
    ),
}


# License detection patterns
LICENSE_PATTERNS = [
    (r'MIT License|Permission is hereby granted, free of charge', 'MIT'),
    (r'Apache License.*Version 2\.0|Licensed under the Apache License', 'Apache-2.0'),
    (r'GNU GENERAL PUBLIC LICENSE.*Version 3|GPLv3', 'GPL-3.0'),
    (r'GNU GENERAL PUBLIC LICENSE.*Version 2|GPLv2', 'GPL-2.0'),
    (r'GNU LESSER GENERAL PUBLIC LICENSE.*Version 3|LGPLv3', 'LGPL-3.0'),
    (r'GNU LESSER GENERAL PUBLIC LICENSE.*Version 2\.1|LGPLv2\.1', 'LGPL-2.1'),
    (r'BSD 3-Clause|New BSD|Revised BSD', 'BSD-3-Clause'),
    (r'BSD 2-Clause|Simplified BSD|FreeBSD', 'BSD-2-Clause'),
    (r'Mozilla Public License.*2\.0|MPL-2\.0', 'MPL-2.0'),
    (r'GNU AFFERO GENERAL PUBLIC LICENSE|AGPLv3', 'AGPL-3.0'),
    (r'ISC License', 'ISC'),
    (r'The Unlicense|unlicensed', 'Unlicense'),
    (r'CC0|Creative Commons Zero', 'CC0-1.0'),
    (r'SPDX-License-Identifier:\s*(\S+)', None),  # Extract from SPDX header
]


def detect_license_in_file(filepath: str) -> Optional[str]:
    """Detect license from file content."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(10000)  # Read first 10KB

            for pattern, license_id in LICENSE_PATTERNS:
                match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                if match:
                    if license_id is None:  # SPDX pattern
                        return match.group(1)
                    return license_id

    except Exception:
        pass

    return None


def find_license_files(path: str) -> List[str]:
    """Find license files in the project."""
    license_files = []
    license_names = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'LICENCE', 'COPYING', 'COPYING.txt']

    for name in license_names:
        filepath = Path(path) / name
        if filepath.exists():
            license_files.append(str(filepath))

    return license_files


def scan_source_files(path: str) -> List[LicenseFinding]:
    """Scan source files for license headers and issues."""
    findings = []
    extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.rb']

    for ext in extensions:
        for filepath in Path(path).rglob(f'*{ext}'):
            if 'node_modules' in str(filepath) or '.venv' in str(filepath) or 'vendor' in str(filepath):
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    header = ''.join(lines[:30])  # Check first 30 lines for license header

                    # Check for copyright notice
                    has_copyright = bool(re.search(r'[Cc]opyright|©|\(c\)', header))

                    # Check for license identifier
                    license_match = re.search(r'SPDX-License-Identifier:\s*(\S+)', header)
                    has_license = bool(license_match) or any(
                        re.search(pat, header, re.IGNORECASE) for pat, _ in LICENSE_PATTERNS[:5]
                    )

                    detected_license = None
                    if license_match:
                        detected_license = license_match.group(1)
                    else:
                        for pattern, lic_id in LICENSE_PATTERNS:
                            if lic_id and re.search(pattern, header, re.IGNORECASE):
                                detected_license = lic_id
                                break

                    # Determine category
                    category = 'unknown'
                    if detected_license and detected_license in LICENSE_DB:
                        category = LICENSE_DB[detected_license].category

                    # Check for proprietary indicators
                    proprietary_patterns = [
                        r'[Pp]roprietary',
                        r'[Cc]onfidential',
                        r'[Aa]ll [Rr]ights [Rr]eserved',
                        r'[Nn]ot for distribution',
                        r'[Ii]nternal [Uu]se [Oo]nly'
                    ]
                    is_proprietary = any(re.search(p, header) for p in proprietary_patterns)

                    # Report issues
                    if is_proprietary:
                        findings.append(LicenseFinding(
                            file=str(filepath),
                            line=1,
                            license='PROPRIETARY',
                            category='proprietary',
                            issue='File marked as proprietary/confidential',
                            severity='info'
                        ))
                    elif detected_license:
                        issue = None
                        severity = 'info'

                        if category == 'strong-copyleft':
                            issue = f'Strong copyleft license ({detected_license}) - may require source disclosure'
                            severity = 'high'
                        elif category == 'weak-copyleft':
                            issue = f'Weak copyleft license ({detected_license}) - review obligations'
                            severity = 'medium'

                        findings.append(LicenseFinding(
                            file=str(filepath),
                            line=1,
                            license=detected_license,
                            category=category,
                            issue=issue,
                            severity=severity
                        ))

            except Exception:
                pass

    return findings


def check_license_compatibility(project_license: str, dependency_licenses: List[str]) -> List[Dict]:
    """Check if dependency licenses are compatible with project license."""
    issues = []

    if project_license not in LICENSE_DB:
        return [{'error': f'Unknown project license: {project_license}'}]

    project_info = LICENSE_DB[project_license]

    for dep_license in dependency_licenses:
        # Normalize license name
        dep_license_normalized = dep_license.replace('-only', '').replace('-or-later', '')

        if dep_license_normalized not in LICENSE_DB:
            issues.append({
                'dependency_license': dep_license,
                'issue': 'Unknown license - manual review required',
                'severity': 'medium'
            })
            continue

        dep_info = LICENSE_DB[dep_license_normalized]

        # Check direct incompatibility
        if project_license in dep_info.incompatible_with or dep_license_normalized in project_info.incompatible_with:
            issues.append({
                'dependency_license': dep_license,
                'issue': f'{dep_license} is incompatible with {project_license}',
                'severity': 'critical'
            })
        # Check copyleft in permissive project
        elif project_info.category == 'permissive' and dep_info.category == 'strong-copyleft':
            issues.append({
                'dependency_license': dep_license,
                'issue': f'Strong copyleft ({dep_license}) in permissive project requires careful integration',
                'severity': 'high'
            })
        elif project_info.category == 'proprietary' and dep_info.category in ['strong-copyleft', 'weak-copyleft']:
            issues.append({
                'dependency_license': dep_license,
                'issue': f'Copyleft license ({dep_license}) may conflict with proprietary distribution',
                'severity': 'critical'
            })

    return issues


def check_attribution(path: str, required_attributions: List[str]) -> List[AttributionIssue]:
    """Check if required attributions are present."""
    issues = []

    # Read all potential attribution files
    attribution_content = ""
    attribution_files = ['NOTICE', 'NOTICE.txt', 'ATTRIBUTION', 'ATTRIBUTION.txt',
                        'THIRD_PARTY_LICENSES', 'THIRD-PARTY-LICENSES.txt', 'CREDITS']

    for filename in attribution_files:
        filepath = Path(path) / filename
        if filepath.exists():
            try:
                with open(filepath) as f:
                    attribution_content += f.read() + "\n"
            except Exception:
                pass

    # Also check LICENSE file
    for lic_file in find_license_files(path):
        try:
            with open(lic_file) as f:
                attribution_content += f.read() + "\n"
        except Exception:
            pass

    # Check each required attribution
    for attr in required_attributions:
        found = attr.lower() in attribution_content.lower()
        issues.append(AttributionIssue(
            package=attr,
            license='MIT/Apache-2.0',  # Generic
            required='Attribution in NOTICE/LICENSE',
            found=found,
            location=None if not found else 'NOTICE or LICENSE file'
        ))

    return issues


def format_text_report(findings: List[LicenseFinding], compat_issues: List[Dict],
                       attr_issues: List[AttributionIssue]) -> str:
    """Format report as human-readable text."""
    output = []
    output.append("=" * 60)
    output.append("LICENSE COMPLIANCE AUDIT REPORT")
    output.append("=" * 60)

    # License Findings
    output.append(f"\n{'='*60}")
    output.append(f"LICENSE FINDINGS ({len(findings)})")
    output.append("=" * 60)

    # Group by severity
    critical = [f for f in findings if f.severity == 'critical']
    high = [f for f in findings if f.severity == 'high']
    medium = [f for f in findings if f.severity == 'medium']

    if critical:
        output.append("\n[CRITICAL]")
        for f in critical:
            output.append(f"  {f.file}:{f.line}")
            output.append(f"    License: {f.license} ({f.category})")
            output.append(f"    Issue: {f.issue}")

    if high:
        output.append("\n[HIGH]")
        for f in high:
            output.append(f"  {f.file}:{f.line}")
            output.append(f"    License: {f.license} ({f.category})")
            output.append(f"    Issue: {f.issue}")

    if medium:
        output.append("\n[MEDIUM]")
        for f in medium:
            output.append(f"  {f.file}:{f.line}")
            output.append(f"    License: {f.license}")
            if f.issue:
                output.append(f"    Issue: {f.issue}")

    # Summary by category
    output.append("\nLicense Category Summary:")
    categories = {}
    for f in findings:
        categories[f.category] = categories.get(f.category, 0) + 1
    for cat, count in sorted(categories.items()):
        status = "✓" if cat in ['permissive', 'unknown'] else "⚠"
        output.append(f"  {status} {cat}: {count}")

    # Compatibility Issues
    if compat_issues:
        output.append(f"\n{'='*60}")
        output.append("COMPATIBILITY ISSUES")
        output.append("=" * 60)
        for issue in compat_issues:
            severity = issue.get('severity', 'unknown').upper()
            output.append(f"\n[{severity}] {issue.get('dependency_license', 'Unknown')}")
            output.append(f"  Issue: {issue.get('issue', 'Unknown issue')}")

    # Attribution Issues
    missing_attr = [a for a in attr_issues if not a.found]
    if missing_attr:
        output.append(f"\n{'='*60}")
        output.append("MISSING ATTRIBUTIONS")
        output.append("=" * 60)
        for attr in missing_attr:
            output.append(f"\n  Package: {attr.package}")
            output.append(f"  Required: {attr.required}")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Audit license compliance')
    parser.add_argument('path', nargs='?', default='.', help='Project path to audit')
    parser.add_argument('--project-license', default='MIT', help='Project license for compatibility check')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    parser.add_argument('--strict', action='store_true', help='Fail on any copyleft license')
    parser.add_argument('--check-attributions', nargs='*', default=[], help='Check for specific attributions')

    args = parser.parse_args()
    path = os.path.abspath(args.path)

    if not os.path.isdir(path):
        print(f"Error: {path} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Find and analyze license files
    license_files = find_license_files(path)
    project_detected_license = None
    if license_files:
        project_detected_license = detect_license_in_file(license_files[0])
        if project_detected_license:
            print(f"Detected project license: {project_detected_license}", file=sys.stderr)

    # Scan source files
    findings = scan_source_files(path)

    # Check compatibility
    found_licenses = list(set(f.license for f in findings if f.license))
    compat_issues = check_license_compatibility(args.project_license, found_licenses)

    # Check attributions
    attr_issues = check_attribution(path, args.check_attributions)

    # Output
    if args.format == 'json':
        output = {
            'project_license': args.project_license,
            'detected_license': project_detected_license,
            'license_files': license_files,
            'findings': [asdict(f) for f in findings],
            'compatibility_issues': compat_issues,
            'attribution_issues': [asdict(a) for a in attr_issues],
            'summary': {
                'total_files_scanned': len(findings),
                'permissive': len([f for f in findings if f.category == 'permissive']),
                'weak_copyleft': len([f for f in findings if f.category == 'weak-copyleft']),
                'strong_copyleft': len([f for f in findings if f.category == 'strong-copyleft']),
                'proprietary': len([f for f in findings if f.category == 'proprietary']),
                'unknown': len([f for f in findings if f.category == 'unknown']),
                'critical_issues': len([f for f in findings if f.severity == 'critical']),
                'high_issues': len([f for f in findings if f.severity == 'high'])
            }
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text_report(findings, compat_issues, attr_issues))

    # Exit code
    critical_count = len([f for f in findings if f.severity == 'critical'])
    high_count = len([f for f in findings if f.severity == 'high'])

    if args.strict:
        copyleft_count = len([f for f in findings if f.category in ['strong-copyleft', 'weak-copyleft']])
        if copyleft_count > 0:
            sys.exit(2)

    if critical_count > 0:
        sys.exit(2)
    elif high_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
