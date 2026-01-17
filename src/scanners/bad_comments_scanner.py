
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import re
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

logger = logging.getLogger(__name__)

class BadCommentsScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_commented_code(lines, file_path))
        
        violations.extend(self._check_html_in_comments(lines, file_path))
        
        violations.extend(self._check_misleading_todos(lines, file_path))
        
        return violations
    
    def _check_commented_code(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        commented_block_start = None
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('//') or stripped.startswith('#'):
                comment_content = stripped[2:].strip()
                
                if self._is_actual_commented_code(comment_content, lines, line_num):
                    if commented_block_start is None:
                        commented_block_start = line_num
                elif commented_block_start:
                    prev_comment = lines[line_num - 2].strip() if line_num > 1 else ""
                    if (prev_comment.startswith('//') or prev_comment.startswith('#')) and \
                       self._is_actual_commented_code(prev_comment[2:].strip(), lines, line_num - 1):
                        pass
                    else:
                        if commented_block_start:
                            violations.append(self._create_commented_code_violation(self.rule, file_path, commented_block_start))
                            commented_block_start = None
                else:
                    commented_block_start = None
            else:
                if commented_block_start:
                    violations.append(self._create_commented_code_violation(self.rule, file_path, commented_block_start))
                    commented_block_start = None
        
        if commented_block_start:
            violations.append(self._create_commented_code_violation(self.rule, file_path, commented_block_start))
        
        return violations
    
    def _create_commented_code_violation(self, file_path: Path, line_num: int) -> Dict[str, Any]:
        try:
            content = file_path.read_text(encoding='utf-8')
            return self._create_violation_with_snippet(
                                violation_message=f"Has commented-out code - delete it (it's in git history if needed)",
                file_path=file_path,
                line_number=line_num,
                severity='warning',
                content=content,
                start_line=line_num,
                end_line=line_num,
                context_before=1,
                max_lines=3
            )
        except Exception:
            return Violation(
                rule=self.rule,
                violation_message=f"Line {line_num} has commented-out code - delete it (it's in git history if needed)",
                location=str(file_path),
                line_number=line_num,
                severity='warning'
            ).to_dict()
    
    def _is_actual_commented_code(self, comment_content: str, lines: List[str], line_num: int) -> bool:
        if not comment_content:
            return False
        
        for i in range(1, min(3, len(lines) - line_num + 1)):
            if line_num + i - 1 < len(lines):
                next_line = lines[line_num + i - 1].strip()
                if next_line and not next_line.startswith('//') and not next_line.startswith('#'):
                    if re.search(r'\b(def|class|if|for|while|return|import|from|=\s*[^=]|\(|\[|\{)\b', next_line):
                        return False
        
        code_patterns = [
            r'^\s*\w+\s*=\s*[^=]',
            r'\w+\s*\+=\s*',
            r'\w+\s*-=\s*',
            r'\w+\s*\*=\s*',
            r'\w+\s*/=\s*',
            
            r'\b(def|function|class|const|let|var)\s+\w+\s*[\(:]',
            
            r'\w+\s*\([^)]+\)',
            r'\w+\.\w+\s*\(',
            
            r'\bif\s+[^:]+:',
            r'\bif\s*\([^)]+\)',
            r'\bfor\s+[^:]+:',
            r'\bfor\s*\([^)]+\)',
            r'\bwhile\s+[^:]+:',
            r'\bwhile\s*\([^)]+\)',
            
            r'\breturn\s+[^;]+;',
            r'\breturn\s+[^#\n]+$',
            
            r'\[[^\]]+\]',
            r'\{[^}]+\}',
            
            r'[+\-*/%]=\s*\w',
            r'\w+\s*[+\-*/%]\s*\w',
            r'\w+\s*(==|!=|<=|>=|<|>)\s*\w',
            
            r'\w+\.\w+\.\w+',
            
            r'^\s*(import|from|require)\s+',
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, comment_content):
                explanatory_patterns = [
                    r'^\s*(case|return|tuple|is|are|will|should|does|do|use|create|set|get)\s+\w+',
                    r'^\s*\w+\s+(case|is|are|will|should|does|do)',
                    r'^\s*#\s*(Default|Likely|Use|Create|Set|Get|Ensure|Check)',
                ]
                
                is_explanatory = False
                for exp_pattern in explanatory_patterns:
                    if re.search(exp_pattern, comment_content, re.IGNORECASE):
                        if not re.search(r'[=\(\)\[\]\{\}\+\-\*/%;]', comment_content):
                            is_explanatory = True
                            break
                
                if not is_explanatory:
                    return True
        
        return False
    
    def _check_html_in_comments(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        html_patterns = [
            r'<p>', r'</p>', r'<ul>', r'</ul>', r'<li>', r'</li>',
            r'<div>', r'</div>', r'<span>', r'</span>', r'<br>', r'<br/>'
        ]
        
        for line_num, line in enumerate(lines, 1):
            comment_text = self._extract_comment_text(line)
            
            if comment_text:
                for pattern in html_patterns:
                    if re.search(pattern, comment_text, re.IGNORECASE):
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            violation = self._create_violation_with_snippet(
                                                                violation_message=f'Line contains HTML markup in comment - remove HTML, use plain text',
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
                            violation = Violation(
                                rule=self.rule,
                                violation_message=f'Line contains HTML markup in comment - remove HTML, use plain text',
                                location=str(file_path),
                                line_number=line_num,
                                severity='error'
                            ).to_dict()
                        violations.append(violation)
                        break
        
        return violations
    
    def _extract_comment_text(self, line: str) -> Optional[str]:
        in_single_quote = False
        in_double_quote = False
        in_triple_single = False
        in_triple_double = False
        escape_next = False
        
        i = 0
        while i < len(line):
            char = line[i]
            
            if escape_next:
                escape_next = False
                i += 1
                continue
            
            if char == '\\':
                escape_next = True
                i += 1
                continue
            
            if i + 2 < len(line):
                triple = line[i:i+3]
                if triple == '"""' and not in_single_quote and not in_triple_single:
                    in_triple_double = not in_triple_double
                    i += 3
                    continue
                if triple == "'''" and not in_double_quote and not in_triple_double:
                    in_triple_single = not in_triple_single
                    i += 3
                    continue
            
            if not in_triple_single and not in_triple_double:
                if char == '"' and not in_single_quote:
                    in_double_quote = not in_double_quote
                elif char == "'" and not in_double_quote:
                    in_single_quote = not in_single_quote
            
            if not in_single_quote and not in_double_quote and not in_triple_single and not in_triple_double:
                if char == '#' and (i == 0 or line[i-1] != '#' or (i > 0 and line[i-1:i+1] != '##')):
                    return line[i+1:].strip()
                if i + 1 < len(line) and line[i:i+2] == '//':
                    return line[i+2:].strip()
                if i + 1 < len(line) and line[i:i+2] == '/*':
                    end = line.find('*/', i + 2)
                    if end != -1:
                        return line[i+2:end].strip()
                    return line[i+2:].strip()
            
            i += 1
        
        return None
    
    def _check_misleading_todos(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        for line_num, line in enumerate(lines, 1):
            if 'TODO' in line.upper() or 'FIXME' in line.upper():
                if 'needs to be implemented' in line.lower() or 'not implemented' in line.lower():
                    next_lines = lines[line_num:line_num+5]
                    has_implementation = any(
                        re.search(r'\b(function|def|class|return|if|for|while)\b', l)
                        for l in next_lines
                    )
                    
                    if has_implementation:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            violation = self._create_violation_with_snippet(
                                                                violation_message=f'Misleading TODO comment: "{line.strip()}" - code IS implemented, update or delete TODO',
                                file_path=file_path,
                                line_number=line_num,
                                severity='warning',
                                content=content,
                                start_line=line_num,
                                end_line=line_num,
                                context_before=1,
                                max_lines=5
                            )
                        except Exception:
                            violation = Violation(
                                rule=self.rule,
                                violation_message=f'Misleading TODO comment: "{line.strip()}" - code IS implemented, update or delete TODO',
                                location=str(file_path),
                                line_number=line_num,
                                severity='warning'
                            ).to_dict()
                        violations.append(violation)
        
        return violations

