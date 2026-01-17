
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

class OpenClosedPrincipleScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_type_switches(tree, content, file_path, rule_obj))
        
        return violations
    
    def _check_type_switches(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
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
                        rule=rule_obj,
                        violation_message=f'Line {line_num} uses type-based conditional - use polymorphism instead to follow open-closed principle',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

