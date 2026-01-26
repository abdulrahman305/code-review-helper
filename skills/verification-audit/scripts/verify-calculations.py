#!/usr/bin/env python3
"""
Calculation verifier that identifies and validates mathematical operations in code.
Detects common calculation errors and verifies accuracy.
"""

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path
from decimal import Decimal, InvalidOperation


@dataclass
class CalculationFinding:
    file: str
    line: int
    code: str
    calculation_type: str  # arithmetic, financial, statistical, date, aggregate
    issue: Optional[str]
    severity: str  # critical, high, medium, low, info
    recommendation: str


@dataclass
class VerificationResult:
    expression: str
    expected: Any
    actual: Any
    passed: bool
    error: Optional[str]


# Patterns for detecting calculations
CALCULATION_PATTERNS = {
    'division': r'[^/]/[^/=]',
    'multiplication': r'\*[^*=]',
    'addition': r'[^+]\+[^+=]',
    'subtraction': r'[^-]-[^->=]',
    'modulo': r'%[^%]',
    'power': r'\*\*|\^',
    'percentage': r'[\d.]+\s*[*/%]\s*100|100\s*[*/%]|0\.\d+\s*\*',
    'currency': r'\$|USD|EUR|price|cost|amount|total|fee|tax|discount',
    'interest': r'interest|rate|apr|apy|compound',
    'average': r'mean|average|avg',
    'sum': r'sum\(|total\(|aggregate',
    'count': r'count\(|len\(',
    'statistical': r'std|variance|median|percentile|correlation',
}

# Known problematic patterns
PROBLEMATIC_PATTERNS = [
    # Floating point comparisons
    (r'==\s*0\.\d+|0\.\d+\s*==', 'medium',
     'Floating-point equality comparison',
     'Use approximate comparison: abs(a - b) < epsilon'),

    # Integer division in Python 2 style
    (r'(\d+|\w+)\s*/\s*(\d+|\w+)(?!\s*\.)', 'medium',
     'Potential integer division',
     'Use float division or Decimal for precision'),

    # Currency with float
    (r'(price|cost|amount|total|fee)\s*[*+/-]\s*\d+\.\d+', 'high',
     'Currency calculation using float',
     'Use Decimal for monetary calculations'),

    # Percentage calculation order
    (r'/\s*100\s*\*|/100\*', 'medium',
     'Percentage calculation may lose precision',
     'Consider: (value * percent) / 100 for better precision'),

    # Magic numbers in calculations
    (r'[*/%]\s*(?:365|360|12|52|24|60)', 'low',
     'Magic number in date/time calculation',
     'Use named constants for clarity'),

    # Hardcoded tax rates
    (r'\*\s*0\.0[0-9]{1,2}|\*\s*\.\d{2}', 'low',
     'Hardcoded rate in calculation',
     'Extract rates to configuration'),

    # Cumulative floating point
    (r'\+=\s*[\d.]+|total\s*\+?=', 'medium',
     'Cumulative calculation may accumulate floating-point errors',
     'Use Decimal or compute from source data'),
]


class PythonCalculationVisitor(ast.NodeVisitor):
    """AST visitor to find calculations in Python code."""

    def __init__(self, source_lines: List[str]):
        self.findings: List[CalculationFinding] = []
        self.source_lines = source_lines

    def get_source(self, node: ast.AST) -> str:
        """Get source code for a node."""
        try:
            return ast.unparse(node)
        except:
            if hasattr(node, 'lineno') and node.lineno <= len(self.source_lines):
                return self.source_lines[node.lineno - 1].strip()
            return "<unknown>"

    def visit_BinOp(self, node: ast.BinOp):
        """Visit binary operations."""
        source = self.get_source(node)
        line = getattr(node, 'lineno', 0)

        # Check for division
        if isinstance(node.op, ast.Div):
            # Check if using integers
            if isinstance(node.left, ast.Constant) and isinstance(node.left.value, int):
                if isinstance(node.right, ast.Constant) and isinstance(node.right.value, int):
                    self.findings.append(CalculationFinding(
                        file='',
                        line=line,
                        code=source,
                        calculation_type='arithmetic',
                        issue='Integer division may truncate in Python 2',
                        severity='low',
                        recommendation='Explicitly use float or Decimal if precision needed'
                    ))

        # Check for floor division
        if isinstance(node.op, ast.FloorDiv):
            self.findings.append(CalculationFinding(
                file='',
                line=line,
                code=source,
                calculation_type='arithmetic',
                issue='Floor division truncates result',
                severity='info',
                recommendation='Verify truncation is intentional'
            ))

        # Check for percentage-like calculations
        if isinstance(node.op, (ast.Mult, ast.Div)):
            if isinstance(node.right, ast.Constant):
                if node.right.value in [100, 0.01, 0.1]:
                    self.findings.append(CalculationFinding(
                        file='',
                        line=line,
                        code=source,
                        calculation_type='percentage',
                        issue='Percentage calculation detected',
                        severity='info',
                        recommendation='Verify calculation order and precision'
                    ))

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Visit function calls that might be calculations."""
        source = self.get_source(node)
        line = getattr(node, 'lineno', 0)

        func_name = ''
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Check for statistical functions
        if func_name in ['mean', 'average', 'avg', 'median', 'std', 'var', 'sum']:
            self.findings.append(CalculationFinding(
                file='',
                line=line,
                code=source,
                calculation_type='statistical',
                issue=f'Statistical calculation: {func_name}',
                severity='info',
                recommendation='Verify empty collection handling and precision'
            ))

        # Check for round function
        if func_name == 'round':
            self.findings.append(CalculationFinding(
                file='',
                line=line,
                code=source,
                calculation_type='arithmetic',
                issue='round() uses banker\'s rounding in Python 3',
                severity='medium',
                recommendation='Use Decimal.quantize() for predictable rounding'
            ))

        self.generic_visit(node)


def analyze_python_file(filepath: str) -> List[CalculationFinding]:
    """Analyze a Python file for calculations."""
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
            lines = source.split('\n')

        # Parse AST
        try:
            tree = ast.parse(source)
            visitor = PythonCalculationVisitor(lines)
            visitor.visit(tree)
            for finding in visitor.findings:
                finding.file = filepath
                findings.append(finding)
        except SyntaxError:
            pass

        # Pattern-based analysis
        for i, line in enumerate(lines, 1):
            for pattern, severity, issue, recommendation in PROBLEMATIC_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(CalculationFinding(
                        file=filepath,
                        line=i,
                        code=line.strip(),
                        calculation_type='pattern',
                        issue=issue,
                        severity=severity,
                        recommendation=recommendation
                    ))

    except Exception as e:
        findings.append(CalculationFinding(
            file=filepath,
            line=0,
            code='',
            calculation_type='error',
            issue=f'Error analyzing file: {str(e)}',
            severity='info',
            recommendation='Manual review required'
        ))

    return findings


def analyze_javascript_file(filepath: str) -> List[CalculationFinding]:
    """Analyze a JavaScript/TypeScript file for calculations."""
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            # Check for toFixed (common source of issues)
            if 'toFixed' in line:
                findings.append(CalculationFinding(
                    file=filepath,
                    line=i,
                    code=line.strip(),
                    calculation_type='arithmetic',
                    issue='toFixed() returns string, may cause type coercion issues',
                    severity='medium',
                    recommendation='Use Number(x.toFixed(2)) or a decimal library'
                ))

            # Check for parseFloat in calculations
            if re.search(r'parseFloat\s*\(.*\)\s*[+\-*/]', line):
                findings.append(CalculationFinding(
                    file=filepath,
                    line=i,
                    code=line.strip(),
                    calculation_type='arithmetic',
                    issue='parseFloat may introduce floating-point errors',
                    severity='medium',
                    recommendation='Consider using a decimal library for financial calculations'
                ))

            # Check for Math.round usage
            if 'Math.round' in line:
                findings.append(CalculationFinding(
                    file=filepath,
                    line=i,
                    code=line.strip(),
                    calculation_type='arithmetic',
                    issue='Math.round rounds to nearest integer',
                    severity='low',
                    recommendation='For currency: Math.round(value * 100) / 100'
                ))

            # Pattern-based checks
            for pattern, severity, issue, recommendation in PROBLEMATIC_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(CalculationFinding(
                        file=filepath,
                        line=i,
                        code=line.strip(),
                        calculation_type='pattern',
                        issue=issue,
                        severity=severity,
                        recommendation=recommendation
                    ))

    except Exception as e:
        findings.append(CalculationFinding(
            file=filepath,
            line=0,
            code='',
            calculation_type='error',
            issue=f'Error analyzing file: {str(e)}',
            severity='info',
            recommendation='Manual review required'
        ))

    return findings


def verify_calculation(expression: str, expected: Any) -> VerificationResult:
    """Verify a calculation produces expected result."""
    try:
        # Safe eval for simple expressions
        allowed_names = {
            'Decimal': Decimal,
            'abs': abs,
            'round': round,
            'sum': sum,
            'min': min,
            'max': max,
            'len': len,
        }
        actual = eval(expression, {"__builtins__": {}}, allowed_names)

        # Compare with tolerance for floats
        if isinstance(expected, float) and isinstance(actual, float):
            passed = abs(actual - expected) < 1e-9
        else:
            passed = actual == expected

        return VerificationResult(
            expression=expression,
            expected=expected,
            actual=actual,
            passed=passed,
            error=None
        )
    except Exception as e:
        return VerificationResult(
            expression=expression,
            expected=expected,
            actual=None,
            passed=False,
            error=str(e)
        )


def format_text_report(findings: List[CalculationFinding]) -> str:
    """Format report as human-readable text."""
    output = []
    output.append("=" * 60)
    output.append("CALCULATION VERIFICATION REPORT")
    output.append("=" * 60)

    # Group by severity
    by_severity = {'critical': [], 'high': [], 'medium': [], 'low': [], 'info': []}
    for f in findings:
        by_severity.get(f.severity, by_severity['info']).append(f)

    total = len(findings)
    output.append(f"\nTotal Findings: {total}")
    output.append(f"  Critical: {len(by_severity['critical'])}")
    output.append(f"  High: {len(by_severity['high'])}")
    output.append(f"  Medium: {len(by_severity['medium'])}")
    output.append(f"  Low: {len(by_severity['low'])}")
    output.append(f"  Info: {len(by_severity['info'])}")

    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        if by_severity[severity]:
            output.append(f"\n{'='*60}")
            output.append(f"[{severity.upper()}] ({len(by_severity[severity])})")
            output.append("=" * 60)

            for f in by_severity[severity]:
                output.append(f"\n{f.file}:{f.line}")
                output.append(f"  Type: {f.calculation_type}")
                output.append(f"  Code: {f.code[:80]}{'...' if len(f.code) > 80 else ''}")
                if f.issue:
                    output.append(f"  Issue: {f.issue}")
                output.append(f"  Fix: {f.recommendation}")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(description='Verify calculations in source code')
    parser.add_argument('path', help='File or directory to analyze')
    parser.add_argument('--format', choices=['text', 'json'], default='text')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low', 'info'],
                       default='info', help='Minimum severity to report')
    parser.add_argument('--trace', action='store_true', help='Show calculation trace')

    args = parser.parse_args()
    path = Path(args.path)

    findings = []

    if path.is_file():
        if path.suffix == '.py':
            findings = analyze_python_file(str(path))
        elif path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
            findings = analyze_javascript_file(str(path))
    elif path.is_dir():
        # Scan Python files
        for py_file in path.rglob('*.py'):
            if 'node_modules' not in str(py_file) and '.venv' not in str(py_file):
                findings.extend(analyze_python_file(str(py_file)))

        # Scan JavaScript files
        for ext in ['*.js', '*.ts', '*.jsx', '*.tsx']:
            for js_file in path.rglob(ext):
                if 'node_modules' not in str(js_file) and 'dist' not in str(js_file):
                    findings.extend(analyze_javascript_file(str(js_file)))
    else:
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    # Filter by severity
    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
    min_severity = severity_order.get(args.severity, 4)
    findings = [f for f in findings if severity_order.get(f.severity, 4) <= min_severity]

    # Output
    if args.format == 'json':
        output = {
            'findings': [asdict(f) for f in findings],
            'summary': {
                'total': len(findings),
                'by_severity': {
                    'critical': len([f for f in findings if f.severity == 'critical']),
                    'high': len([f for f in findings if f.severity == 'high']),
                    'medium': len([f for f in findings if f.severity == 'medium']),
                    'low': len([f for f in findings if f.severity == 'low']),
                    'info': len([f for f in findings if f.severity == 'info']),
                },
                'by_type': {}
            }
        }
        for f in findings:
            output['summary']['by_type'][f.calculation_type] = \
                output['summary']['by_type'].get(f.calculation_type, 0) + 1
        print(json.dumps(output, indent=2))
    else:
        print(format_text_report(findings))

    # Exit code
    critical = len([f for f in findings if f.severity == 'critical'])
    high = len([f for f in findings if f.severity == 'high'])

    if critical > 0:
        sys.exit(2)
    elif high > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
