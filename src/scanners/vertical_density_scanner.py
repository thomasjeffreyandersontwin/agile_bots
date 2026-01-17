
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

class VerticalDensityScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            violation = self._check_variable_declaration_distance(function.node, content, file_path, rule_obj)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_variable_declaration_distance(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            func_size = func_node.end_lineno - func_node.lineno + 1
            if func_size > 150:
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                return self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Function "{func_node.name}" is {func_size} lines - consider improving vertical density by extracting helper methods and declaring variables near usage',
                    file_path=file_path,
                    line_number=line_number,
                    severity='info',
                    content=content,
                    ast_node=func_node,
                    max_lines=10
                )
        
        return None

