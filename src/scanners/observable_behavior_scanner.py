
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation

class ObservableBehaviorScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_internal_testing(content, file_path, rule_obj))
        
        return violations
    
    def _check_internal_testing(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        lines = content.split('\n')
        
        internal_patterns = [
            r'\.toHaveBeenCalled',
            r'\.assert_called',
            r'\.mock\.',
            r'\.spyOn\(',
            r'assert.*\.call_count',
            r'assert.*\.call_args',
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in internal_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} tests internal implementation (mocks/spies) - tests should focus on observable behavior, not internal calls',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

