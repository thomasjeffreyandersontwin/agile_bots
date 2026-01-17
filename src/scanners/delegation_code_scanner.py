
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import Classes

logger = logging.getLogger(__name__)

class DelegationCodeScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_violations = self._check_delegation(cls.node, content, file_path)
            violations.extend(class_violations)
        
        return violations
    
    def _check_delegation(self, class_node: ast.ClassDef, content: str, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        is_collection_class = self._is_collection_class(class_node.name)
        
        for method in self._get_methods(class_node):
            method_violations = self._check_method_for_loops(
                method, class_node, is_collection_class, content, file_path, self.rule
            )
            violations.extend(method_violations)
        
        return violations
    
    def _get_methods(self, class_node: ast.ClassDef):
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and node.name != '__init__':
                yield node
    
    def _check_method_for_loops(self, method: ast.FunctionDef, class_node: ast.ClassDef,
                                is_collection_class: bool, content: str, 
                                file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        for stmt in ast.walk(method):
            if not self._is_self_attribute_loop(stmt):
                continue
            
            collection_name = stmt.iter.attr
            if self._should_skip_collection(class_node, collection_name, is_collection_class, content):
                continue
            
            if self._is_collection_name(collection_name):
                violations.append(self._create_delegation_violation(
                    method.name, class_node.name, collection_name, stmt.lineno, file_path, self.rule
                ))
        return violations
    
    def _is_self_attribute_loop(self, stmt: ast.stmt) -> bool:
        if not isinstance(stmt, ast.For):
            return False
        if not isinstance(stmt.iter, ast.Attribute):
            return False
        return isinstance(stmt.iter.value, ast.Name) and stmt.iter.value.id == 'self'
    
    def _should_skip_collection(self, class_node: ast.ClassDef, collection_name: str,
                                is_collection_class: bool, content: str) -> bool:
        if is_collection_class and self._is_same_name_collection(class_node.name, collection_name):
            return True
        if self._is_plain_collection(class_node, collection_name, content):
            return True
        if self._is_class_constant(class_node, collection_name):
            return True
        return False
    
    def _is_same_name_collection(self, class_name: str, collection_name: str) -> bool:
        class_lower = class_name.lower()
        attr_lower = collection_name.lower()
        attr_stripped = attr_lower.lstrip('_')
        return attr_lower == f"_{class_lower}" or attr_lower == class_lower or attr_stripped == class_lower
    
    def _create_delegation_violation(self, method_name: str, class_name: str, collection_name: str,
                                     line_number: int, file_path: Path) -> Dict[str, Any]:
        return Violation(
            rule=self.rule,
            violation_message=f'Method "{method_name}" in class "{class_name}" iterates through "{collection_name}" instead of delegating to collection class. Delegate to collection class instead.',
            location=str(file_path),
            line_number=line_number,
            severity='info'
        ).to_dict()
    
    def _is_collection_class(self, class_name: str) -> bool:
        name_lower = class_name.lower()
        return (name_lower.endswith('s') and len(name_lower) > 3) or 'collection' in name_lower
    
    def _is_plain_collection(self, class_node: ast.ClassDef, attr_name: str, content: str) -> bool:
        attr_name_lower = attr_name.lower()
        
        if attr_name_lower.startswith('_'):
            plain_list_indicators = ['pattern', 'spec', 'config', 'item', 'entry', 'element', 'adapter', 'line', 'file', 'path']
            if any(indicator in attr_name_lower for indicator in plain_list_indicators):
                return True
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == attr_name:
                    if isinstance(node.annotation, ast.Subscript):
                        if isinstance(node.annotation.value, ast.Name):
                            if node.annotation.value.id in ('List', 'list', 'Dict', 'dict', 'Set', 'set'):
                                return True
                elif isinstance(node.target, ast.Attribute) and node.target.attr == attr_name:
                    if isinstance(node.annotation, ast.Subscript):
                        if isinstance(node.annotation.value, ast.Name):
                            if node.annotation.value.id in ('List', 'list', 'Dict', 'dict', 'Set', 'set'):
                                return True
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and target.attr == attr_name:
                        if isinstance(node.value, (ast.List, ast.Dict)):
                            return True
        
        return False
    
    def _is_class_constant(self, class_node: ast.ClassDef, attr_name: str) -> bool:
        attr_name_upper = attr_name.upper()
        
        if attr_name == attr_name_upper or attr_name.isupper():
            for node in class_node.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == attr_name:
                            if isinstance(node.value, (ast.List, ast.Dict, ast.Tuple)):
                                return True
                        elif isinstance(target, ast.Attribute) and target.attr == attr_name:
                            if isinstance(node.value, (ast.List, ast.Dict, ast.Tuple)):
                                return True
                
                if isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name) and node.target.id == attr_name:
                        if isinstance(node.value, (ast.List, ast.Dict, ast.Tuple)):
                            return True
        
        constant_patterns = ['PATTERNS', 'RULES', 'PATTERN', 'RULE', 'CONSTANTS', 'CONFIG', 'SETTINGS']
        if attr_name in constant_patterns or any(attr_name.endswith(f'_{p}') for p in constant_patterns):
            return True
        
        return False
    
    def _is_collection_name(self, name: str) -> bool:
        name_lower = name.lower()
        
        if name_lower.startswith('_'):
            plain_list_indicators = ['pattern', 'spec', 'config', 'item', 'entry', 'element', 'adapter', 'line', 'file', 'path']
            if any(indicator in name_lower for indicator in plain_list_indicators):
                return False
        
        if name.isupper() or name == name.upper():
            return False
        
        return (name_lower.endswith('s') and len(name_lower) > 3) or 'collection' in name_lower

