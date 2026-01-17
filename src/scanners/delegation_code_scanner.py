
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Classes

logger = logging.getLogger(__name__)

class DelegationCodeScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_violations = self._check_delegation(cls.node, content, file_path, rule_obj)
            violations.extend(class_violations)
        
        return violations
    
    def _check_delegation(self, class_node: ast.ClassDef, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        is_collection_class = self._is_collection_class(class_node.name)
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                if node.name == '__init__':
                    continue
                
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.For):
                        if isinstance(stmt.iter, ast.Attribute):
                            if isinstance(stmt.iter.value, ast.Name) and stmt.iter.value.id == 'self':
                                collection_name = stmt.iter.attr
                                
                                if is_collection_class:
                                    class_name_lower = class_node.name.lower()
                                    attr_name_lower = collection_name.lower()
                                    attr_without_underscore = attr_name_lower.lstrip('_')
                                    if attr_name_lower == f"_{class_name_lower}" or attr_name_lower == class_name_lower or attr_without_underscore == class_name_lower:
                                        continue
                                
                                if self._is_plain_collection(class_node, collection_name, content):
                                    continue
                                
                                if self._is_class_constant(class_node, collection_name):
                                    continue
                                
                                if self._is_collection_name(collection_name):
                                    violations.append(
                                        Violation(
                                            rule=rule_obj,
                                            violation_message=f'Method "{node.name}" in class "{class_node.name}" iterates through "{collection_name}" instead of delegating to collection class. Delegate to collection class instead.',
                                            location=str(file_path),
                                            line_number=stmt.lineno,
                                            severity='info'
                                        ).to_dict()
                                    )
        
        return violations
    
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

