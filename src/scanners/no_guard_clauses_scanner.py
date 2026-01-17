
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
import logging
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext

logger = logging.getLogger(__name__)

class NoGuardClausesScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_guard_clause_patterns(lines, file_path))
        violations.extend(self._check_ast_guard_clauses(file_path))
        
        return violations
    
    def _check_guard_clause_patterns(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        guard_patterns = [
            (r'if\s+(not\s+)?\w+\.exists\(\):', 'File existence check - test should fail if file missing'),
            (r'if\s+(not\s+)?isinstance\([^)]+\):', 'Type check guard clause - test should fail if wrong type'),
            (r'if\s+(not\s+)?hasattr\([^)]+\):', 'Attribute existence check - test should fail if attribute missing'),
            (r'if\s+(not\s+)?\w+:', 'Variable truthiness check - test should fail if variable is None/empty'),
        ]
        
        in_test_function = False
        test_function_indent = 0
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.lstrip()
            current_indent = len(line) - len(stripped)
            
            if re.match(r'^\s*def\s+test_', line):
                in_test_function = True
                test_function_indent = current_indent
            elif in_test_function and stripped and current_indent <= test_function_indent and not stripped.startswith('@'):
                in_test_function = False
            
            if not in_test_function:
                continue
            
            if stripped.startswith('"""') or stripped.startswith("'''") or stripped.startswith('#'):
                continue
            
            for pattern, message in guard_patterns:
                if re.search(pattern, line):
                    if 'assert' in line.lower():
                        continue
                    
                    if '@pytest.fixture' in '\n'.join(lines[max(0, line_num-3):line_num]):
                        continue
                    
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Line {line_num}: CRITICAL - {message}. Guard clauses are FORBIDDEN in tests. Assume test code works - if setup is wrong, let the test fail. Remove the guard clause.',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations
    
    def _check_ast_guard_clauses(self, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    violations.extend(self._check_function_guard_clauses(node, file_path))
        
        except (SyntaxError, UnicodeDecodeError, Exception) as e:
            logger.debug(f'Skipping file {file_path} due to {type(e).__name__}: {e}')
        
        return violations
    
    def _check_function_guard_clauses(self, func_node: ast.FunctionDef, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.If):
                guard_patterns = [
                    self._is_file_exists_check,
                    self._is_type_check,
                    self._is_hasattr_check,
                    self._is_variable_truthiness_check,
                ]
                
                for pattern_check in guard_patterns:
                    if pattern_check(node):
                        violation = Violation(
                            rule=self.rule,
                            violation_message=f'Line {node.lineno}: CRITICAL - Guard clause detected. Guard clauses are FORBIDDEN in tests. Assume test code works correctly - if setup is wrong, let the test fail. Remove defensive checks.',
                            location=str(file_path),
                            line_number=node.lineno,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
                        break
        
        return violations
    
    def _is_file_exists_check(self, if_node: ast.If) -> bool:
        if isinstance(if_node.test, ast.Call):
            if isinstance(if_node.test.func, ast.Attribute):
                if if_node.test.func.attr == 'exists':
                    return True
        return False
    
    def _is_type_check(self, if_node: ast.If) -> bool:
        if isinstance(if_node.test, ast.Call):
            if isinstance(if_node.test.func, ast.Name):
                if if_node.test.func.id == 'isinstance':
                    return True
        return False
    
    def _is_hasattr_check(self, if_node: ast.If) -> bool:
        if isinstance(if_node.test, ast.Call):
            if isinstance(if_node.test.func, ast.Name):
                if if_node.test.func.id == 'hasattr':
                    return True
        return False
    
    def _is_variable_truthiness_check(self, if_node: ast.If) -> bool:
        if isinstance(if_node.test, ast.Name):
            return True
        if isinstance(if_node.test, ast.UnaryOp) and isinstance(if_node.test.op, ast.Not):
            if isinstance(if_node.test.operand, ast.Name):
                return True
        return False

