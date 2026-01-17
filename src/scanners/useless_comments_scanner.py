
from typing import List, Dict, Any, Optional
from pathlib import Path
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

logger = logging.getLogger(__name__)

# Configuration constants
CONTEXT_LENGTH = 200  # characters of context to examine

class UselessCommentsScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_useless_docstrings(content, file_path, rule_obj))
        
        violations.extend(self._check_useless_comments(lines, file_path, rule_obj))
        
        return violations
    
    def _check_useless_docstrings(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        docstring_pattern = r'"""(.*?)"""'
        matches = re.finditer(docstring_pattern, content, re.DOTALL)
        
        for match in matches:
            docstring_content = match.group(1).strip()
            
            if self._is_useless_docstring(docstring_content, content, match.start()):
                line_number = content[:match.start()].count('\n') + 1
                end_line = content[:match.end()].count('\n') + 1
                violation = self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Useless docstring that repeats function/class name - delete it or explain WHY, not WHAT',
                    file_path=file_path,
                    line_number=line_number,
                    severity='error',
                    content=content,
                    start_line=line_number,
                    end_line=end_line,
                    context_before=2
                )
                violations.append(violation)
        
        return violations
    
    def _check_useless_comments(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        content = '\n'.join(lines)
        
        useless_patterns = [
            r'#\s*(Load|Get|Set|Return|Execute|Perform|Handle|Process|Create|Delete|Update)\s+\w+',
            r'#\s*(This|The)\s+(function|method|class|variable)\s+(does|gets|sets|returns)',
            r'#\s*(end|End)\s+(if|for|while|class|function)',
            r'#\s*={10,}',
            r'#\s*(Changed|Modified|Added|Removed)\s+by:',
        ]
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            if not line_stripped.startswith('#'):
                continue
            
            if self._is_useful_comment(line_stripped, lines, line_num):
                continue
            
            for pattern in useless_patterns:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    violation = self._create_violation_with_snippet(
                        rule_obj=rule_obj,
                        violation_message=f'Useless comment: "{line_stripped[:60]}" - delete it or improve the code instead',
                        file_path=file_path,
                        line_number=line_num,
                        severity='error',
                        content=content,
                        start_line=line_num,
                        end_line=line_num,
                        context_before=2
                    )
                    violations.append(violation)
                    break
        
        return violations
    
    def _is_useful_comment(self, comment_line: str, lines: List[str], line_num: int) -> bool:
        comment_lower = comment_line.lower()
        
        useful_patterns = [
            r'\?',
            r'(because|since|due to|as|when|if|unless)',
            r'(warning|caution|note|important|critical)',
            r'(todo|fixme|hack|workaround)',
            r'(license|copyright|legal)',
            r'(algorithm|complex|non-obvious)',
            r'(business rule|domain|requirement)',
        ]
        
        for pattern in useful_patterns:
            if re.search(pattern, comment_lower):
                return True
        
        if line_num < len(lines):
            next_line = lines[line_num].strip() if line_num < len(lines) else ""
            if re.search(r'\b(if|for|while|with)\s+[^:]+:', next_line):
                return True
        
        return False
    
    def _is_useless_docstring(self, docstring: str, content: str, docstring_start: int) -> bool:
        before_docstring = content[:docstring_start]
        recent_context = before_docstring[-CONTEXT_LENGTH:] if len(before_docstring) > CONTEXT_LENGTH else before_docstring
        
        lines_before = before_docstring.strip()
        if not lines_before or lines_before.count('\n') == 0:
            return False
        
        lines = recent_context.split('\n')
        
        for i in range(len(lines) - 1, max(0, len(lines) - 5), -1):
            line = lines[i].strip()
            
            if line.startswith('def ') or line.startswith('class '):
                return True
            
            if line and not line.startswith('#'):
                break
        
        return False

