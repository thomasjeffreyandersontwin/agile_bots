
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import Functions

class SimplifyControlFlowScanner(CodeScanner):
    
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
            violation = self._check_nesting_depth(function.node, file_path, self.rule, content)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_nesting_depth(self, func_node: ast.FunctionDef, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        max_depth = self._get_max_nesting_depth(func_node)
        
        if max_depth > 3:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            return self._create_violation_with_snippet(
                                violation_message=f'Function "{func_node.name}" has nesting depth of {max_depth} - use guard clauses and extract nested blocks to reduce nesting',
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node,
                max_lines=15
            )
        
        return None
    
    def _get_max_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                depth = self._get_max_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
            else:
                depth = self._get_max_nesting_depth(child, current_depth)
                max_depth = max(max_depth, depth)
        
        return max_depth

