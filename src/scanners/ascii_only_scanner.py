
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
import re

class AsciiOnlyScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        for line_num, line in enumerate(lines, 1):
            violation = self._check_unicode_characters(line, file_path, line_num)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_unicode_characters(self, line: str, file_path: Path, line_num: int) -> Optional[Dict[str, Any]]:
        try:
            line.encode('ascii')
        except UnicodeEncodeError:
            unicode_chars = []
            for char in line:
                try:
                    char.encode('ascii')
                except UnicodeEncodeError:
                    unicode_chars.append(char)
            
            if unicode_chars:
                problematic = [c for c in unicode_chars if ord(c) > 127]
                if problematic:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        return self._create_violation_with_snippet(
                                                        violation_message=f'Line contains Unicode characters: {", ".join(set(problematic[:3]))} - use ASCII alternatives like [PASS], [ERROR], [FAIL]',
                            file_path=file_path,
                            line_number=line_num,
                            severity='error',
                            content=content,
                            start_line=line_num,
                            end_line=line_num,
                            context_before=1,
                            max_lines=3
                        )
                    except Exception:
                        location = f"{file_path}:{line_num}"
                        return Violation(
                            rule=self.rule,
                            violation_message=f'Line contains Unicode characters: {", ".join(set(problematic[:3]))} - use ASCII alternatives like [PASS], [ERROR], [FAIL]',
                            location=location,
                            line_number=line_num,
                            severity='error'
                        ).to_dict()
        
        return None

