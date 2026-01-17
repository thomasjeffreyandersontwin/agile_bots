
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext

class NoFallbacksScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_fallback_patterns(lines, file_path))
        
        return violations
    
    def _check_fallback_patterns(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        fallback_patterns = [
            r'\bor\s+[A-Z]\w+\(\)',
            r'\bdefault\s*=',
            r'\bfallback\s*=',
            r'\bor\s+None',
            r'\bif\s+.*\s+else\s+["\']',
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in fallback_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Line {line_num} uses fallback/default value - tests should use explicit test data, not fallbacks',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

