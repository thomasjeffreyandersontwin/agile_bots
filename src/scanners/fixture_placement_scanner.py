
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .resources.ast_elements import Imports

class FixturePlacementScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_fixture_imports(tree, file_path))
        
        return violations
    
    def _check_fixture_imports(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        imports = Imports(tree)
        for import_stmt in imports.get_many_imports:
            if isinstance(import_stmt.node, ast.ImportFrom):
                if import_stmt.node.module and 'fixture' in import_stmt.node.module.lower():
                    line_number = import_stmt.node.lineno if hasattr(import_stmt.node, 'lineno') else None
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Fixtures imported from "{import_stmt.node.module}" - fixtures should be defined in test file, not imported',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations

