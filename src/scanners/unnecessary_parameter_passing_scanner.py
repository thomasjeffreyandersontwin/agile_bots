
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Classes

class UnnecessaryParameterPassingScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        if self._is_test_file(file_path):
            return violations
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_violations = self._check_class(cls.node, file_path, rule_obj, lines, content)
            violations.extend(class_violations)
        
        return violations
    
    def _check_class(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any, lines: List[str], content: str) -> List[Dict[str, Any]]:
        violations = []
        
        instance_attrs = self._collect_instance_attributes(class_node)
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_'):
                    method_violations = self._check_method_parameters(node, instance_attrs, file_path, rule_obj, lines, content)
                    violations.extend(method_violations)
                
                extraction_violations = self._check_property_extraction(node, instance_attrs, file_path, rule_obj, lines, content)
                violations.extend(extraction_violations)
        
        return violations
    
    def _collect_instance_attributes(self, class_node: ast.ClassDef) -> set:
        attrs = set()
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    attrs.add(target.attr)
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    attrs.add(target.attr)
        
        return attrs
    
    def _check_method_parameters(self, method_node: ast.FunctionDef, instance_attrs: set, 
                                file_path: Path, rule_obj: Any, lines: List[str], content: str) -> List[Dict[str, Any]]:
        violations = []
        
        if not method_node.name.startswith('_'):
            return violations
        
        if method_node.name.startswith('__') and method_node.name.endswith('__'):
            return violations
        
        for arg in method_node.args.args:
            if arg.arg == 'self':
                continue
            
            if arg.arg in instance_attrs:
                if self._parameter_used_like_instance_attr(method_node, arg.arg):
                    line_number = method_node.lineno if hasattr(method_node, 'lineno') else None
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Internal method "{method_node.name}" receives parameter "{arg.arg}" that matches instance attribute. Consider accessing via self.{arg.arg} instead.',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations
    
    def _parameter_used_like_instance_attr(self, method_node: ast.FunctionDef, param_name: str) -> bool:
        for node in ast.walk(method_node):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == param_name:
                    return False
            
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == param_name:
                        return False
        
        return True
    
    def _check_property_extraction(self, method_node: ast.FunctionDef, instance_attrs: set,
                                  file_path: Path, rule_obj: Any, lines: List[str], content: str) -> List[Dict[str, Any]]:
        violations = []
        
        assignments = []
        for i, stmt in enumerate(method_node.body):
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        attr_path = self._extract_self_attribute_path(stmt.value)
                        if attr_path:
                            assignments.append({
                                'var_name': target.id,
                                'attr_path': attr_path,
                                'line': stmt.lineno if hasattr(stmt, 'lineno') else None
                            })
        
        for i, stmt in enumerate(method_node.body):
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                call = stmt.value
                if isinstance(call.func, ast.Attribute):
                    if isinstance(call.func.value, ast.Name) and call.func.value.id == 'self':
                        method_name = call.func.attr
                        if method_name.startswith('_'):
                            for arg in call.args:
                                if isinstance(arg, ast.Name):
                                    for assignment in assignments:
                                        if arg.id == assignment['var_name']:
                                            if assignment['line'] and hasattr(stmt, 'lineno'):
                                                if assignment['line'] < stmt.lineno:
                                                    line_number = stmt.lineno if hasattr(stmt, 'lineno') else None
                                                    violation = Violation(
                                                        rule=rule_obj,
                                                        violation_message=f'Instance property "self.{assignment["attr_path"]}" is extracted to variable "{assignment["var_name"]}" and passed to internal method "{method_name}". Access via self.{assignment["attr_path"]} directly instead.',
                                                        location=str(file_path),
                                                        line_number=line_number,
                                                        severity='warning'
                                                    ).to_dict()
                                                    violations.append(violation)
        
        return violations
    
    def _extract_self_attribute_path(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Attribute):
            current = node
            path_parts = []
            
            while isinstance(current, ast.Attribute):
                path_parts.insert(0, current.attr)
                current = current.value
            
            if isinstance(current, ast.Name) and current.id == 'self':
                return '.'.join(path_parts)
        
        return None

