
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

class MinimizeMutableStateScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_mutable_patterns(lines, file_path))
        
        return violations
    
    def _check_mutable_patterns(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        mutable_patterns = [
            r'\.push\s*\(',
            r'\.pop\s*\(',
            r'\.splice\s*\(',
            r'\+\+\s*;',
            r'--\s*;',
            r'=\s*\{.*\}\s*\.\w+\s*=',
            r'\.append\s*\(',
            r'\.extend\s*\(',
            r'\.insert\s*\(',
            r'\.remove\s*\(',
            r'\.clear\s*\(',
            r'\+=\s*1\s*$',
            r'-=\s*1\s*$',
            r'\w+\s*\+\+',
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in mutable_patterns:
                if re.search(pattern, line):
                    if 'test_' in line.lower() or 'def test' in line.lower():
                        continue
                    
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Line {line_num} mutates state - prefer immutable data structures (create new objects instead of mutating)',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

