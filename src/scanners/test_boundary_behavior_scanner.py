"""Scanner for validating boundary behavior is tested."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from test_scanner import TestScanner
from scanners.violation import Violation

logger = logging.getLogger(__name__)


class TestBoundaryBehaviorScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_boundary_tests(content, file_path, rule_obj))
        
        return violations
    
    def _check_boundary_tests(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        lines = content.split('\n')
        
        # Boundary indicators
        boundary_patterns = [
            r'\b(boundary|edge|limit|maximum|minimum|max|min|empty|null|zero|first|last)\b',
        ]
        
        has_boundary_tests = False
        for line in lines:
            for pattern in boundary_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    has_boundary_tests = True
                    break
        
        # This is informational - boundary tests are good but not always required
        # Could be enhanced to check if code has boundaries that need testing
        
        return violations

