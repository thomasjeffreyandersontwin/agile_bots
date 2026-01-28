#!/usr/bin/env python3
"""
JavaScript File Validator
Validates all JS files against clean code rules and generates violation report
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


class JSViolation:
    def __init__(self, file_path: str, rule_name: str, line_number: int, description: str, severity: str = "warning"):
        self.file_path = file_path
        self.rule_name = rule_name
        self.line_number = line_number
        self.description = description
        self.severity = severity
    
    def __repr__(self):
        return f"{self.file_path}:{self.line_number} | {self.rule_name} | {self.description}"


class JSValidator:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.violations: List[JSViolation] = []
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """Load all active JavaScript rules"""
        rules_dir = self.workspace_root / 'bots' / 'story_bot' / 'behaviors' / 'code' / 'rules'
        js_rules_dir = rules_dir / 'specializations' / 'javascript'
        
        rules = []
        
        # Load general rules
        for rule_file in rules_dir.glob('*.json'):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rule_data = json.load(f)
                    rule_data['file'] = str(rule_file.relative_to(self.workspace_root))
                    rules.append(rule_data)
            except Exception as e:
                print(f"Error loading rule {rule_file}: {e}")
        
        # Load JS-specific rules
        if js_rules_dir.exists():
            for rule_file in js_rules_dir.glob('*.json'):
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        rule_data = json.load(f)
                        rule_data['file'] = str(rule_file.relative_to(self.workspace_root))
                        rules.append(rule_data)
                except Exception as e:
                    print(f"Error loading JS rule {rule_file}: {e}")
        
        return rules
    
    def validate_file(self, file_path: Path):
        """Validate a single JS file against all rules"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            rel_path = str(file_path.relative_to(self.workspace_root))
            
            # Run all validation checks
            self._check_function_size(rel_path, content, lines)
            self._check_duplication(rel_path, content, lines)
            self._check_useless_comments(rel_path, content, lines)
            self._check_consistent_naming(rel_path, content, lines)
            self._check_domain_language(rel_path, content, lines)
            self._check_magic_numbers(rel_path, content, lines)
            self._check_exception_handling(rel_path, content, lines)
            self._check_single_responsibility(rel_path, content, lines)
            
        except Exception as e:
            print(f"Error validating {file_path}: {e}")
    
    def _check_function_size(self, file_path: str, content: str, lines: List[str]):
        """Check if functions are too large (>20 lines)"""
        # Simple heuristic: count lines between function declarations and closing braces
        func_pattern = re.compile(r'^\s*(async\s+)?function\s+\w+|^\s*\w+\s*[=:]\s*(async\s+)?function|\b(async\s+)?\w+\s*\([^)]*\)\s*\{')
        
        in_function = False
        func_start_line = 0
        brace_count = 0
        
        for i, line in enumerate(lines, 1):
            if func_pattern.search(line):
                in_function = True
                func_start_line = i
                brace_count = line.count('{') - line.count('}')
            elif in_function:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    func_length = i - func_start_line + 1
                    if func_length > 30:
                        self.violations.append(JSViolation(
                            file_path, 
                            "keep_functions_small_focused",
                            func_start_line,
                            f"Function is {func_length} lines long (should be under 20-30 lines)",
                            "warning"
                        ))
                    in_function = False
    
    def _check_duplication(self, file_path: str, content: str, lines: List[str]):
        """Check for code duplication"""
        # Look for repeated patterns (simplified check)
        line_counts = defaultdict(list)
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('//') and len(stripped) > 20:
                line_counts[stripped].append(i)
        
        for line_text, occurrences in line_counts.items():
            if len(occurrences) > 2:
                self.violations.append(JSViolation(
                    file_path,
                    "eliminate_duplication",
                    occurrences[0],
                    f"Duplicate code found on lines {', '.join(map(str, occurrences))}: {line_text[:50]}...",
                    "warning"
                ))
    
    def _check_useless_comments(self, file_path: str, content: str, lines: List[str]):
        """Check for useless or obvious comments"""
        useless_patterns = [
            (r'//\s*initialize', 'Obvious comment about initialization'),
            (r'//\s*create', 'Obvious comment about creation'),
            (r'//\s*set\s+\w+', 'Obvious comment about setting variable'),
            (r'//\s*get\s+\w+', 'Obvious comment about getting variable'),
            (r'//\s*return', 'Obvious comment about return statement'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, message in useless_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.violations.append(JSViolation(
                        file_path,
                        "stop_writing_useless_comments",
                        i,
                        message,
                        "warning"
                    ))
    
    def _check_consistent_naming(self, file_path: str, content: str, lines: List[str]):
        """Check for consistent naming conventions"""
        # Look for inconsistent function naming (get vs fetch vs retrieve)
        get_funcs = re.findall(r'\bget\w+', content)
        fetch_funcs = re.findall(r'\bfetch\w+', content)
        retrieve_funcs = re.findall(r'\bretrieve\w+', content)
        
        verbs = []
        if get_funcs:
            verbs.append('get')
        if fetch_funcs:
            verbs.append('fetch')
        if retrieve_funcs:
            verbs.append('retrieve')
        
        if len(verbs) > 1:
            self.violations.append(JSViolation(
                file_path,
                "use_consistent_naming",
                1,
                f"Inconsistent naming: using {', '.join(verbs)} for similar operations",
                "warning"
            ))
    
    def _check_domain_language(self, file_path: str, content: str, lines: List[str]):
        """Check for generic terms instead of domain language"""
        generic_terms = ['data', 'config', 'parameter', 'result', 'temp', 'tmp']
        
        for i, line in enumerate(lines, 1):
            for term in generic_terms:
                # Look for variable declarations with generic names
                pattern = r'\b(const|let|var)\s+' + term + r'\b(?!\w)'
                if re.search(pattern, line):
                    self.violations.append(JSViolation(
                        file_path,
                        "use_domain_language",
                        i,
                        f"Generic variable name '{term}' - use domain-specific language",
                        "warning"
                    ))
    
    def _check_magic_numbers(self, file_path: str, content: str, lines: List[str]):
        """Check for magic numbers (numbers without explanation)"""
        for i, line in enumerate(lines, 1):
            # Skip comments and const declarations
            if '//' in line or 'const ' in line:
                continue
            
            # Look for numeric literals (except 0, 1, -1)
            numbers = re.findall(r'\b(\d{2,})\b', line)
            for num in numbers:
                if int(num) not in [0, 1, 10, 100, 1000]:  # Common acceptable numbers
                    self.violations.append(JSViolation(
                        file_path,
                        "provide_meaningful_context",
                        i,
                        f"Magic number '{num}' - should be a named constant",
                        "warning"
                    ))
    
    def _check_exception_handling(self, file_path: str, content: str, lines: List[str]):
        """Check for proper exception handling"""
        for i, line in enumerate(lines, 1):
            # Look for empty catch blocks
            if 'catch' in line:
                next_line = lines[i] if i < len(lines) else ''
                if '{}' in line or ('{' in line and '}' in next_line):
                    self.violations.append(JSViolation(
                        file_path,
                        "never_swallow_exceptions",
                        i,
                        "Empty catch block - exceptions should be logged or rethrown",
                        "error"
                    ))
    
    def _check_single_responsibility(self, file_path: str, content: str, lines: List[str]):
        """Check if functions have single responsibility"""
        # Look for function names with 'and' or mixed concerns
        func_and_pattern = re.compile(r'function\s+\w+And\w+')
        
        for i, line in enumerate(lines, 1):
            if func_and_pattern.search(line):
                self.violations.append(JSViolation(
                    file_path,
                    "keep_functions_single_responsibility",
                    i,
                    "Function name contains 'And' - suggests multiple responsibilities",
                    "warning"
                ))
    
    def generate_report(self) -> str:
        """Generate violation report"""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("JavaScript Clean Code Validation Report")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        if not self.violations:
            report_lines.append("✅ No violations found! All JavaScript files comply with clean code rules.")
            return '\n'.join(report_lines)
        
        # Group violations by rule
        by_rule = defaultdict(list)
        for v in self.violations:
            by_rule[v.rule_name].append(v)
        
        # Summary
        report_lines.append(f"Total Violations: {len(self.violations)}")
        report_lines.append(f"Files Checked: {len(set(v.file_path for v in self.violations))}")
        report_lines.append(f"Rules Violated: {len(by_rule)}")
        report_lines.append("")
        
        # Violations by rule
        for rule_name in sorted(by_rule.keys()):
            violations = by_rule[rule_name]
            status = "FAIL"
            report_lines.append(f"{rule_name} | {status} | {len(violations)} violation(s)")
            
            for v in violations[:5]:  # Show first 5 per rule
                report_lines.append(f"  {v.file_path}:{v.line_number} - {v.description}")
            
            if len(violations) > 5:
                report_lines.append(f"  ... and {len(violations) - 5} more")
            report_lines.append("")
        
        return '\n'.join(report_lines)


def main():
    workspace = Path(r"C:\dev\agile_bots")
    validator = JSValidator(workspace)
    
    # Find all JS files excluding node_modules
    js_files = []
    for pattern in ['src/**/*.js', 'test/**/*.js']:
        for file in workspace.glob(pattern):
            if 'node_modules' not in str(file):
                js_files.append(file)
    
    print(f"Found {len(js_files)} JavaScript files to validate (excluding node_modules)")
    
    for js_file in js_files:
        print(f"Validating {js_file.relative_to(workspace)}...")
        validator.validate_file(js_file)
    
    # Generate report
    report = validator.generate_report()
    print("\n" + report)
    
    # Write report to file
    report_path = workspace / 'js_validation_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport written to: {report_path}")


if __name__ == '__main__':
    main()
