
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .resources.ast_elements import Functions

class CoverAllPathsScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        test_methods = [function.node for function in functions.get_many_functions if function.node.name.startswith('test_')]
        
        for test_method in test_methods:
            found_code_node = None
            for stmt in test_method.body:
                if isinstance(stmt, ast.Pass):
                    continue
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                    continue
                else:
                    for node in ast.walk(stmt):
                        if isinstance(node, (ast.Call, ast.Assign, ast.Assert, ast.Return, ast.Raise)):
                            found_code_node = node
                            break
                    if found_code_node is not None:
                        break
            
            if found_code_node is None:
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=f'Test method "{test_method.name}" has no actual test code - tests must exercise behavior paths, not just contain pass statements',
                    location=str(file_path),
                    line_number=test_method.lineno,
                    severity='error'
                ).to_dict())
        
        return violations

