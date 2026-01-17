
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import TryBlocks

class ExceptionHandlingScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_exception_misuse(tree, content, file_path))
        
        return violations
    
    def _check_exception_misuse(self, tree: ast.AST, content: str, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        lines = content.split('\n')
        
        try_blocks = TryBlocks(tree)
        for try_block in try_blocks.get_many_try_blocks:
            for handler in try_block.node.handlers:
                handler_body = handler.body
                if len(handler_body) == 0:
                    line_number = handler.lineno if hasattr(handler, 'lineno') else None
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Empty except block at line {line_number} - exceptions should be logged or rethrown, never swallowed',
                        location=str(file_path),
                        line_number=line_number,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
        
        return violations

