
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

class OpenClosedPrincipleScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_type_switches(tree, content, file_path))
        
        return violations
    
    def _check_type_switches(self, tree: ast.AST, content: str, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        lines = content.split('\n')
        
        type_switch_patterns = [
            r'\.type\s*==',
            r'\.kind\s*==',
            r'\.type\s*!=',
            r'\.kind\s*!=',
        ]
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
            
            for pattern in type_switch_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Line {line_num} uses type-based conditional - use polymorphism instead to follow open-closed principle',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

