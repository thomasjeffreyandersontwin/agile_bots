
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Classes

logger = logging.getLogger(__name__)

class EncapsulationScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            violation = self._check_encapsulation(cls.node, content, file_path, rule_obj)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_encapsulation(self, class_node: ast.ClassDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        violations = []
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                method_violations = self._check_method_encapsulation(node, class_node.name, file_path, rule_obj)
                violations.extend(method_violations)
        
        return violations[0] if violations else None
    
    def _check_method_encapsulation(self, method_node: ast.FunctionDef, class_name: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                chain_depth = self._get_method_chain_depth(node)
                if chain_depth >= 3:
                    line_number = node.lineno if hasattr(node, 'lineno') else method_node.lineno
                    violations.append(Violation(
                        rule=rule_obj,
                        violation_message=(
                            f'Method "{method_node.name}" in class "{class_name}" has Law of Demeter violation '
                            f'(method chain depth {chain_depth}) - encapsulate access to related objects'
                        ),
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict())
        
        return violations
    
    def _get_method_chain_depth(self, call_node: ast.Call) -> int:
        depth = 1
        
        current = call_node.func
        while isinstance(current, ast.Attribute):
            if isinstance(current.value, ast.Call):
                depth += 1
                current = current.value.func
            else:
                break
        
        return depth

