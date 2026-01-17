
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation

class NoFallbacksScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_fallback_patterns(lines, file_path, rule_obj))
        
        return violations
    
    def _check_fallback_patterns(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
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
                        rule=rule_obj,
                        violation_message=f'Line {line_num} uses fallback/default value - tests should use explicit test data, not fallbacks',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

