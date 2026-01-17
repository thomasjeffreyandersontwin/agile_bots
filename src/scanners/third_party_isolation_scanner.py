
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

class ThirdPartyIsolationScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_third_party_usage(lines, file_path, rule_obj))
        
        return violations
    
    def _check_third_party_usage(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        third_party_patterns = [
            r'from\s+requests\s+import',
            r'from\s+boto3\s+import',
            r'from\s+sqlalchemy\s+import',
            r'import\s+requests',
            r'import\s+boto3',
        ]
        
        has_third_party_import = False
        for line_num, line in enumerate(lines, 1):
            for pattern in third_party_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    has_third_party_import = True
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Line {line_num} imports third-party library directly - wrap third-party APIs behind your own interfaces',
                        location=str(file_path),
                        line_number=line_num,
                        severity='info'
                    ).to_dict()
                    violations.append(violation)
                    break
        
        return violations

