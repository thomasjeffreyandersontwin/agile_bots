
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import Functions

class VerticalDensityScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            violation = self._check_variable_declaration_distance(function.node, content, file_path)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_variable_declaration_distance(self, func_node: ast.FunctionDef, content: str, file_path: Path) -> Optional[Dict[str, Any]]:
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            func_size = func_node.end_lineno - func_node.lineno + 1
            if func_size > 150:
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                return self._create_violation_with_snippet(
                                        violation_message=f'Function "{func_node.name}" is {func_size} lines - consider improving vertical density by extracting helper methods and declaring variables near usage',
                    file_path=file_path,
                    line_number=line_number,
                    severity='info',
                    content=content,
                    ast_node=func_node,
                    max_lines=10
                )
        
        return None

