
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

logger = logging.getLogger(__name__)

class ImportPlacementScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        import_section_end = self._find_import_section_end(lines)
        
        violations.extend(self._check_import_placement(lines, import_section_end, file_path, rule_obj))
        
        return violations
    
    def _find_import_section_end(self, lines: List[str]) -> int:
        import_section_end = 0
        
        while import_section_end < len(lines) and not lines[import_section_end].strip():
            import_section_end += 1
        
        if import_section_end < len(lines):
            line = lines[import_section_end].strip()
            if line.startswith('"""') or line.startswith("'''"):
                quote_char = line[:3]
                import_section_end += 1
                while import_section_end < len(lines):
                    if quote_char in lines[import_section_end]:
                        import_section_end += 1
                        break
                    import_section_end += 1
        
        in_multiline_import = False
        while import_section_end < len(lines):
            line = lines[import_section_end].strip()
            if not line or line.startswith('#'):
                import_section_end += 1
            elif self._is_import_statement(line):
                if '(' in line and ')' not in line:
                    in_multiline_import = True
                import_section_end += 1
            elif in_multiline_import:
                if ')' in line:
                    in_multiline_import = False
                import_section_end += 1
            elif self._is_type_checking_block_start(line):
                import_section_end = self._skip_type_checking_block(lines, import_section_end)
            elif self._is_try_import_error_block_start(line):
                import_section_end = self._skip_try_import_error_block(lines, import_section_end)
            else:
                break
        
        return import_section_end
    
    def _is_type_checking_block_start(self, line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith('if TYPE_CHECKING:')
    
    def _skip_type_checking_block(self, lines: List[str], start_line: int) -> int:
        if start_line >= len(lines):
            return start_line
        
        type_checking_line = lines[start_line]
        base_indent = len(type_checking_line) - len(type_checking_line.lstrip())
        
        current_line = start_line + 1
        
        while current_line < len(lines):
            line = lines[current_line]
            stripped = line.strip()
            
            if not stripped:
                current_line += 1
                continue
            
            if stripped.startswith('#'):
                current_line += 1
                continue
            
            line_indent = len(line) - len(line.lstrip())
            if line_indent <= base_indent:
                break
            
            current_line += 1
        
        return current_line
    
    def _is_try_import_error_block_start(self, line: str) -> bool:
        stripped = line.strip()
        return stripped == 'try:' or stripped.startswith('try:')
    
    def _skip_try_import_error_block(self, lines: List[str], start_line: int) -> int:
        if start_line >= len(lines):
            return start_line
        
        try_line = lines[start_line]
        base_indent = len(try_line) - len(try_line.lstrip())
        
        current_line = start_line + 1
        
        while current_line < len(lines):
            line = lines[current_line]
            stripped = line.strip()
            
            if not stripped:
                current_line += 1
                continue
            
            if stripped.startswith('#'):
                current_line += 1
                continue
            
            line_indent = len(line) - len(line.lstrip())
            if line_indent == base_indent:
                if stripped.startswith('except ImportError:') or stripped.startswith('except ImportError'):
                    current_line += 1
                    while current_line < len(lines):
                        except_line = lines[current_line]
                        except_stripped = except_line.strip()
                        except_indent = len(except_line) - len(except_line.lstrip())
                        
                        if not except_stripped or except_stripped.startswith('#'):
                            current_line += 1
                            continue
                        
                        if except_indent <= base_indent:
                            break
                        
                        current_line += 1
                    break
                else:
                    break
            
            current_line += 1
        
        return current_line
    
    def _is_import_statement(self, line: str) -> bool:
        stripped = line.strip()
        
        if not (stripped.startswith('import ') or stripped.startswith('from ')):
            return False
        
        if stripped.startswith('from '):
            return ' import ' in stripped
        
        return stripped.startswith('import ')
    
    def _check_import_placement(
        self, 
        lines: List[str], 
        import_section_end: int,
        file_path: Path, 
        rule_obj: Any
    ) -> List[Dict[str, Any]]:
        violations = []
        content = '\n'.join(lines)
        
        try:
            tree = ast.parse(content, filename=str(file_path))
            import_nodes = self._find_import_nodes(tree)
            import_line_numbers = {node.lineno for node in import_nodes}
            function_def_lines = self._find_function_def_lines(tree)
        except (SyntaxError, Exception) as e:
            logger.debug(f'AST parsing failed for {file_path}, falling back to line-by-line checking: {type(e).__name__}: {e}')
            import_line_numbers = set()
            function_def_lines = set()
        
        line_num = import_section_end
        while line_num < len(lines):
            line = lines[line_num]
            line_number_1_indexed = line_num + 1
            
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                line_num += 1
                continue
            
            if self._is_type_checking_block_start(stripped):
                line_num = self._skip_type_checking_block(lines, line_num)
                continue
            
            if self._is_try_import_error_block_start(stripped):
                line_num = self._skip_try_import_error_block(lines, line_num)
                continue
            
            is_import = False
            if import_line_numbers and line_number_1_indexed in import_line_numbers:
                is_import = True
            elif self._is_import_statement(line):
                is_import = True
            
            if is_import:
                if function_def_lines and self._is_inside_function(line_number_1_indexed, function_def_lines, lines):
                    line_num += 1
                    continue
                
                violation = self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message='Import statement found after non-import code. Move all imports to the top of the file.',
                    file_path=file_path,
                    line_number=line_number_1_indexed,
                    severity='error',
                    content=content,
                    start_line=line_number_1_indexed
                )
                violations.append(violation)
            
            line_num += 1
        
        return violations
    
    def _find_import_nodes(self, tree: ast.AST) -> List[ast.stmt]:
        import_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
        return import_nodes
    
    def _find_function_def_lines(self, tree: ast.AST) -> Dict[int, int]:
        function_ranges = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = self._find_function_end_line(node, tree)
                function_ranges[start_line] = end_line
        return function_ranges
    
    def _find_function_end_line(self, func_node: ast.FunctionDef, tree: ast.AST) -> int:
        if hasattr(func_node, 'end_lineno') and func_node.end_lineno:
            return func_node.end_lineno
        
        if func_node.body:
            last_stmt = func_node.body[-1]
            if hasattr(last_stmt, 'end_lineno') and last_stmt.end_lineno:
                return last_stmt.end_lineno
        
        logger.debug(f'Function node missing end_lineno at line {func_node.lineno}')
        return func_node.lineno
    
    def _is_inside_function(self, line_number: int, function_ranges: Dict[int, int], lines: List[str]) -> bool:
        for func_start, func_end in function_ranges.items():
            if func_start <= line_number <= func_end:
                return True
        return False

