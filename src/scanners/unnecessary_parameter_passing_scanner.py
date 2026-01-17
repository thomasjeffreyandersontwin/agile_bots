
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import Classes

class UnnecessaryParameterPassingScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

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
            class_violations = self._check_class(cls.node, file_path, self.rule, lines, content)
            violations.extend(class_violations)
        
        return violations
    
    def _check_class(self, class_node: ast.ClassDef, file_path: Path, lines: List[str], content: str) -> List[Dict[str, Any]]:
        violations = []
        
        instance_attrs = self._collect_instance_attributes(class_node)
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_'):
                    method_violations = self._check_method_parameters(node, instance_attrs, file_path, self.rule, lines, content)
                    violations.extend(method_violations)
                
                extraction_violations = self._check_property_extraction(node, instance_attrs, file_path, self.rule, lines, content)
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
                                file_path: Path, lines: List[str], content: str) -> List[Dict[str, Any]]:
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
                        rule=self.rule,
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
                                  file_path: Path, lines: List[str], content: str) -> List[Dict[str, Any]]:
        assignments = self._collect_self_attribute_assignments(method_node)
        return self._find_extraction_violations(method_node, assignments, file_path)
    
    def _collect_self_attribute_assignments(self, method_node: ast.FunctionDef) -> List[dict]:
        assignments = []
        for stmt in method_node.body:
            if not isinstance(stmt, ast.Assign):
                continue
            for target in stmt.targets:
                if not isinstance(target, ast.Name):
                    continue
                attr_path = self._extract_self_attribute_path(stmt.value)
                if attr_path:
                    assignments.append({
                        'var_name': target.id,
                        'attr_path': attr_path,
                        'line': stmt.lineno if hasattr(stmt, 'lineno') else None
                    })
        return assignments
    
    def _find_extraction_violations(self, method_node: ast.FunctionDef, assignments: List[dict],
                                   file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        for stmt in method_node.body:
            violation = self._check_call_for_extraction(stmt, assignments, file_path)
            if violation:
                violations.append(violation)
        return violations
    
    def _check_call_for_extraction(self, stmt: ast.stmt, assignments: List[dict],
                                   file_path: Path) -> Optional[Dict[str, Any]]:
        if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
            return None
        
        call = stmt.value
        if not self._is_private_self_method_call(call):
            return None
        
        method_name = call.func.attr
        for arg in call.args:
            if not isinstance(arg, ast.Name):
                continue
            for assignment in assignments:
                if arg.id == assignment['var_name'] and self._is_before_call(assignment, stmt):
                    return self._create_extraction_violation(assignment, method_name, stmt, file_path)
        return None
    
    def _is_private_self_method_call(self, call: ast.Call) -> bool:
        if not isinstance(call.func, ast.Attribute):
            return False
        if not isinstance(call.func.value, ast.Name) or call.func.value.id != 'self':
            return False
        return call.func.attr.startswith('_')
    
    def _is_before_call(self, assignment: dict, stmt: ast.stmt) -> bool:
        return assignment['line'] and hasattr(stmt, 'lineno') and assignment['line'] < stmt.lineno
    
    def _create_extraction_violation(self, assignment: dict, method_name: str, 
                                     stmt: ast.stmt, file_path: Path) -> Dict[str, Any]:
        line_number = stmt.lineno if hasattr(stmt, 'lineno') else None
        return Violation(
            rule=self.rule,
            violation_message=f'Instance property "self.{assignment["attr_path"]}" is extracted to variable "{assignment["var_name"]}" and passed to internal method "{method_name}". Access via self.{assignment["attr_path"]} directly instead.',
            location=str(file_path),
            line_number=line_number,
            severity='warning'
        ).to_dict()
    
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

