
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import TryBlocks

class ExceptionHandlingScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_exception_misuse(tree, content, file_path, rule_obj))
        
        return violations
    
    def _check_exception_misuse(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        lines = content.split('\n')
        
        try_blocks = TryBlocks(tree)
        for try_block in try_blocks.get_many_try_blocks:
            for handler in try_block.node.handlers:
                handler_body = handler.body
                if len(handler_body) == 0:
                    line_number = handler.lineno if hasattr(handler, 'lineno') else None
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Empty except block at line {line_number} - exceptions should be logged or rethrown, never swallowed',
                        location=str(file_path),
                        line_number=line_number,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
        
        return violations

