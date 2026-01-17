"""Scanner for validating test quality (FIRST principles)."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from test_scanner import TestScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)


class TestQualityScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        # Only scan test files - skip production code
        if not self._is_test_file(file_path):
            return violations
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_test_independence(tree, content, file_path, rule_obj))
        violations.extend(self._check_test_names_quality(tree, file_path, rule_obj))
        
        return violations
    
    def _is_test_file(self, file_path: Path) -> bool:
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        path_parts = [part.lower() for part in file_path.parts]
        if 'test' in path_parts or 'tests' in path_parts:
            return True
        
        if file_name.startswith('test_'):
            return True
        
        if file_name.endswith('_test.py'):
            return True
        
        return False
    
    def _check_test_independence(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                line_number = node.lineno if hasattr(node, 'lineno') else None
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Line {line_number} uses global state - tests should be independent, not share state',
                    location=str(file_path),
                    line_number=line_number,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _check_test_names_quality(self, tree: ast.AST, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        generic_names = ['test_1', 'test_2', 'test_basic', 'test_simple', 'test_default']
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if not function.node.name.startswith('test_'):
                continue
            if function.node.name not in generic_names:
                continue
            
            line_number = function.node.lineno if hasattr(function.node, 'lineno') else None
            violation = Violation(
                rule=rule_obj,
                violation_message=f'Test "{function.node.name}" uses generic name - use descriptive name that explains what is being tested',
                location=str(file_path),
                line_number=line_number,
                severity='error'
            ).to_dict()
            violations.append(violation)
        
        return violations
    
    def scan_story_node(self, node: Any, rule_obj: Any) -> List[Dict[str, Any]]:
        # TestQualityScanner focuses on test files, not story graph
        return []

