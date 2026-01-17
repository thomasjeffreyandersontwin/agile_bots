
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Classes

class PropertyEncapsulationCodeScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_violations = self._check_encapsulation(cls.node, content, file_path, rule_obj)
            violations.extend(class_violations)
        
        return violations
    
    def _check_encapsulation(self, class_node: ast.ClassDef, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        class_source = ast.get_source_segment(content, class_node) or ''
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        if not field_name.startswith('_') and not field_name.startswith('__'):
                            parent = self._get_parent_function(node)
                            if parent and isinstance(parent, ast.FunctionDef) and parent.name == '__init__':
                                violations.append(
                                    Violation(
                                        rule=rule_obj,
                                        violation_message=f'Class "{class_node.name}" has public field "{field_name}". Use private field (prefix with _) and expose via property if needed.',
                                        location=str(file_path),
                                        line_number=node.lineno,
                                        severity='warning'
                                    ).to_dict()
                                )
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Return) and stmt.value:
                        if isinstance(stmt.value, ast.Attribute):
                            violations.append(
                                Violation(
                                    rule=rule_obj,
                                    violation_message=f'Method "{node.name}" in class "{class_node.name}" returns mutable reference. Return defensive copy or use property.',
                                    location=str(file_path),
                                    line_number=stmt.lineno,
                                    severity='warning'
                                ).to_dict()
                            )
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                method_name_lower = node.name.lower()
                if method_name_lower.startswith(('calculate_', 'compute_', 'derive_')):
                    if len(node.args.args) <= 1:
                        violations.append(
                            Violation(
                                rule=rule_obj,
                                violation_message=f'Method "{node.name}" in class "{class_node.name}" should be a property instead of a method (use @property decorator).',
                                location=str(file_path),
                                line_number=node.lineno,
                                severity='warning'
                            ).to_dict()
                        )
        
        return violations
    
    def _get_parent_function(self, node: ast.AST) -> Optional[ast.FunctionDef]:
        for parent in ast.walk(node):
            if isinstance(parent, ast.FunctionDef):
                for child in ast.walk(parent):
                    if child == node:
                        return parent
        return None

