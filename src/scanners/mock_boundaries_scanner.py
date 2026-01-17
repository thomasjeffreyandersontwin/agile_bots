
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext

class MockBoundariesScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_mock_usage(content, file_path))
        
        return violations
    
    def _check_mock_usage(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        lines = content.split('\n')
        
        mock_patterns = [
            r'@patch\s*\(',
            r'@mock\.',
            r'Mock\s*\(',
            r'mock\.',
            r'@pytest\.fixture.*mock',
        ]
        
        internal_patterns = [
            r'mock.*\b(validate|calculate|process|format|parse)\b',
            r'mock.*\b(helper|util|common|shared)\b',
        ]
        
        for line_num, line in enumerate(lines, 1):
            has_mock = any(re.search(pattern, line, re.IGNORECASE) for pattern in mock_patterns)
            
            if has_mock:
                is_internal = any(re.search(pattern, line, re.IGNORECASE) for pattern in internal_patterns)
                
                if is_internal:
                    violation = Violation(
                        rule=self.rule,
                        violation_message=f'Line {line_num} mocks internal code - mocks should only be used for external boundaries (APIs, databases, file systems)',
                        location=str(file_path),
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
        
        return violations

