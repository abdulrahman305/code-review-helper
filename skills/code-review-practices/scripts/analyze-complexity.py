#!/usr/bin/env python3
"""
Analyze cyclomatic complexity of source code files.
Supports Python, JavaScript/TypeScript, and provides basic analysis for other languages.
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def calculate_python_complexity(source: str) -> List[Dict]:
    """Calculate cyclomatic complexity for Python code."""
    results = []

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return [{"error": f"Syntax error: {e}"}]

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            complexity = 1  # Base complexity

            for child in ast.walk(node):
                # Decision points that increase complexity
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(child, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(child, ast.Assert):
                    complexity += 1
                elif isinstance(child, ast.comprehension):
                    complexity += 1
                elif isinstance(child, (ast.And, ast.Or)):
                    complexity += 1
                elif isinstance(child, ast.BoolOp):
                    complexity += len(child.values) - 1
                elif isinstance(child, ast.IfExp):
                    complexity += 1

            results.append({
                "name": node.name,
                "line": node.lineno,
                "complexity": complexity,
                "severity": get_complexity_severity(complexity)
            })

    return results


def calculate_js_complexity(source: str) -> List[Dict]:
    """Calculate cyclomatic complexity for JavaScript/TypeScript using regex patterns."""
    results = []

    # Find function definitions
    function_patterns = [
        r'function\s+(\w+)\s*\([^)]*\)\s*\{',  # function name() {
        r'(\w+)\s*[:=]\s*(?:async\s+)?function\s*\([^)]*\)\s*\{',  # name: function() {
        r'(\w+)\s*[:=]\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{?',  # name = () => {
        r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',  # class method
    ]

    # Decision point patterns
    decision_patterns = [
        r'\bif\s*\(',
        r'\belse\s+if\s*\(',
        r'\bwhile\s*\(',
        r'\bfor\s*\(',
        r'\bcase\s+',
        r'\bcatch\s*\(',
        r'\?\s*[^:]+:',  # ternary
        r'\|\|',  # logical or
        r'&&',  # logical and
        r'\?\?',  # nullish coalescing
    ]

    lines = source.split('\n')
    current_function = None
    brace_count = 0
    function_start = 0
    function_content = []

    for i, line in enumerate(lines, 1):
        # Check for function start
        for pattern in function_patterns:
            match = re.search(pattern, line)
            if match and current_function is None:
                current_function = match.group(1) if match.group(1) else 'anonymous'
                function_start = i
                brace_count = line.count('{') - line.count('}')
                function_content = [line]
                break

        if current_function:
            if line not in function_content:
                function_content.append(line)
            brace_count += line.count('{') - line.count('}')

            if brace_count <= 0:
                # Function ended, calculate complexity
                content = '\n'.join(function_content)
                complexity = 1

                for pattern in decision_patterns:
                    complexity += len(re.findall(pattern, content))

                results.append({
                    "name": current_function,
                    "line": function_start,
                    "complexity": complexity,
                    "severity": get_complexity_severity(complexity)
                })

                current_function = None
                function_content = []

    return results


def get_complexity_severity(complexity: int) -> str:
    """Map complexity score to severity level."""
    if complexity <= 5:
        return "low"
    elif complexity <= 10:
        return "medium"
    elif complexity <= 20:
        return "high"
    else:
        return "critical"


def analyze_file(filepath: str) -> Dict:
    """Analyze a file and return complexity metrics."""
    path = Path(filepath)

    if not path.exists():
        return {"error": f"File not found: {filepath}"}

    content = path.read_text(encoding='utf-8', errors='ignore')
    extension = path.suffix.lower()

    if extension == '.py':
        functions = calculate_python_complexity(content)
    elif extension in ['.js', '.jsx', '.ts', '.tsx', '.mjs']:
        functions = calculate_js_complexity(content)
    else:
        # Basic line-count analysis for other languages
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith(('//', '#', '*', '/*'))])

        return {
            "file": filepath,
            "language": "unknown",
            "total_lines": total_lines,
            "code_lines": code_lines,
            "note": "Detailed complexity analysis not available for this language"
        }

    # Calculate summary statistics
    if functions and not any('error' in f for f in functions):
        complexities = [f['complexity'] for f in functions]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        max_complexity = max(complexities) if complexities else 0
        high_complexity_count = len([c for c in complexities if c > 10])

        return {
            "file": filepath,
            "language": extension,
            "functions": functions,
            "summary": {
                "total_functions": len(functions),
                "average_complexity": round(avg_complexity, 2),
                "max_complexity": max_complexity,
                "high_complexity_functions": high_complexity_count
            }
        }

    return {
        "file": filepath,
        "functions": functions
    }


def main():
    parser = argparse.ArgumentParser(description='Analyze code complexity')
    parser.add_argument('files', nargs='+', help='Files to analyze')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--threshold', type=int, default=10, help='Complexity threshold for warnings')

    args = parser.parse_args()

    results = []
    for filepath in args.files:
        result = analyze_file(filepath)
        results.append(result)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for result in results:
            print(f"\n=== {result.get('file', 'Unknown')} ===")

            if 'error' in result:
                print(f"Error: {result['error']}")
                continue

            if 'note' in result:
                print(f"Lines: {result.get('code_lines', 'N/A')} code / {result.get('total_lines', 'N/A')} total")
                print(result['note'])
                continue

            functions = result.get('functions', [])
            if not functions:
                print("No functions found")
                continue

            print(f"\nFunction Complexity:")
            print("-" * 50)

            for func in sorted(functions, key=lambda x: x.get('complexity', 0), reverse=True):
                if 'error' in func:
                    print(f"  Error: {func['error']}")
                    continue

                severity = func.get('severity', 'unknown')
                indicator = {'low': '✓', 'medium': '~', 'high': '!', 'critical': '✗'}.get(severity, '?')

                print(f"  {indicator} {func['name']} (line {func['line']}): {func['complexity']} [{severity}]")

            summary = result.get('summary', {})
            if summary:
                print(f"\nSummary:")
                print(f"  Total functions: {summary['total_functions']}")
                print(f"  Average complexity: {summary['average_complexity']}")
                print(f"  Max complexity: {summary['max_complexity']}")
                if summary['high_complexity_functions'] > 0:
                    print(f"  ⚠ High complexity functions: {summary['high_complexity_functions']}")

    # Exit with error if any critical complexity found
    for result in results:
        for func in result.get('functions', []):
            if func.get('complexity', 0) > args.threshold:
                sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
