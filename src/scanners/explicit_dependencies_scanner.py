
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

class ExplicitDependenciesScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_hidden_dependencies(tree, file_path, rule_obj))
        
        return violations
    
    def _check_hidden_dependencies(self, tree: ast.AST, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Global variable usage detected - dependencies should be explicit (passed as parameters)',
                    location=str(file_path),
                    line_number=node.lineno if hasattr(node, 'lineno') else None,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations

