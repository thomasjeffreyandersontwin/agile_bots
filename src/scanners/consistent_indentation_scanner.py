
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

class ConsistentIndentationScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_mixed_indentation(lines, file_path))
        
        return violations
    
    def _check_mixed_indentation(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        has_tabs = False
        has_spaces = False
        
        for line_num, line in enumerate(lines, 1):
            if line.startswith('\t'):
                has_tabs = True
            elif line.startswith(' '):
                has_spaces = True
        
        if has_tabs and has_spaces:
            violation = Violation(
                rule=self.rule,
                violation_message='File mixes tabs and spaces for indentation - use consistent indentation (prefer spaces)',
                location=str(file_path),
                severity='error'
            ).to_dict()
            violations.append(violation)
        
        return violations

