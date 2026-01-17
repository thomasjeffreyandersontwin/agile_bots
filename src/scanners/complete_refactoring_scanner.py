
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

logger = logging.getLogger(__name__)

class CompleteRefactoringScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_fallback_legacy_support(lines, file_path, rule_obj))
        
        return violations
    
    def _check_fallback_legacy_support(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        fallback_comment_pattern = re.compile(
            r'#\s*(fallback|legacy).*',
            re.IGNORECASE
        )
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if fallback_comment_pattern.match(stripped):
                code_line_num = None
                for next_line_num in range(line_num, min(line_num + 5, len(lines) + 1)):
                    if next_line_num > len(lines):
                        break
                    next_line = lines[next_line_num - 1].strip()
                    if next_line and not next_line.startswith('#'):
                        code_line_num = next_line_num
                        break
                
                if code_line_num:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=f'Fallback/legacy support code found (comment at line {line_num}, code at line {code_line_num}) - complete refactoring by removing old pattern support',
                        location=str(file_path),
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations

