
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

class ExplicitDependenciesScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_hidden_dependencies(tree, file_path))
        
        return violations
    
    def _check_hidden_dependencies(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                violation = Violation(
                    rule=self.rule,
                    violation_message=f'Global variable usage detected - dependencies should be explicit (passed as parameters)',
                    location=str(file_path),
                    line_number=node.lineno if hasattr(node, 'lineno') else None,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations

