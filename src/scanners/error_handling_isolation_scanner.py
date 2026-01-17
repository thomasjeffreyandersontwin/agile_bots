
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions, TryBlocks

class ErrorHandlingIsolationScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_mixed_error_handling(tree, content, file_path, rule_obj))
        
        return violations
    
    def _check_mixed_error_handling(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            try_blocks_collection = TryBlocks(function.node)
            try_blocks_count = len(try_blocks_collection.get_many_try_blocks)
            if try_blocks_count > 2:
                line_number = function.node.lineno if hasattr(function.node, 'lineno') else None
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Function "{function.node.name}" has {try_blocks_count} try-except blocks - extract error handling to separate functions',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations

