
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

class GivenWhenThenHelpersScanner(TestScanner):
    
    MIN_INLINE_LINES = 4
    
    HELPER_PATTERNS = [
        r'given_\w+',
        r'when_\w+',
        r'then_\w+',
        r'create_\w+',
        r'verify_\w+',
    ]
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        helper_functions = self._get_helper_functions(tree, content)
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if function.node.name.startswith('test_'):
                test_violations = self._check_test_method(
                    function.node, content, file_path, rule_obj, helper_functions, tree
                )
                violations.extend(test_violations)
        
        return violations
    
    def _get_helper_functions(self, tree: ast.AST, content: str) -> Set[str]:
        helpers = set()
        
        defined_helpers = self._get_defined_helper_functions(tree)
        helpers.update(defined_helpers.keys())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if any(helper_mod in module for helper_mod in ['conftest', 'test_helpers', '_helpers']):
                    for alias in node.names:
                        name = alias.name
                        for pattern in self.HELPER_PATTERNS:
                            if re.match(pattern, name, re.IGNORECASE):
                                helpers.add(name)
                                break
        
        return helpers
    
    def _get_defined_helper_functions(self, tree: ast.AST) -> Dict[str, int]:
        helpers = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                for pattern in self.HELPER_PATTERNS:
                    if re.match(pattern, func_name, re.IGNORECASE):
                        helpers[func_name] = node.lineno
                        break
        
        return helpers
    
    def _parse_test_file(self, file_path: Path) -> Optional[Tuple[str, ast.AST]]:
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            return (content, tree)
        except (SyntaxError, UnicodeDecodeError):
            return None
    
    def _check_test_method(self, test_node: ast.FunctionDef, content: str, file_path: Path, 
                          rule_obj: Any, helper_functions: Set[str], tree: ast.AST) -> List[Dict[str, Any]]:
        violations = []
        
        test_lines = content.split('\n')
        start_line = test_node.lineno - 1
        end_line = test_node.end_lineno if hasattr(test_node, 'end_lineno') else len(test_lines)
        
        test_body_lines = test_lines[start_line:end_line]
        
        inline_blocks = self._find_inline_code_blocks(test_node, test_body_lines, helper_functions, tree)
        
        for block_start, block_end, block_lines in inline_blocks:
            if len(block_lines) >= self.MIN_INLINE_LINES:
                block_text = '\n'.join(block_lines[:3])
                if len(block_lines) > 3:
                    block_text += '\n...'
                
                violation = Violation(
                    rule=rule_obj,
                    violation_message=(
                        f'Lines {block_start}-{block_end}: Multiple inline steps ({len(block_lines)} lines) '
                        f'should be extracted into a Given/When/Then helper function. '
                        f'Block:\n{block_text}'
                    ),
                    location=str(file_path),
                    line_number=block_start,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _get_docstring_line_range(self, test_node: ast.FunctionDef) -> Optional[Tuple[int, int]]:
        if not test_node.body:
            return None
        
        first_stmt = test_node.body[0]
        if isinstance(first_stmt, ast.Expr):
            is_string_literal = (isinstance(first_stmt.value, ast.Constant) and 
                                isinstance(first_stmt.value.value, str))
            if not is_string_literal and hasattr(ast, 'Str'):
                is_string_literal = isinstance(first_stmt.value, ast.Str)
            
            if is_string_literal:
                docstring_start = first_stmt.lineno
                if not hasattr(first_stmt, 'end_lineno') or not first_stmt.end_lineno:
                    logger.debug(f'Docstring node missing end_lineno at line {docstring_start}')
                    return None
                docstring_end = first_stmt.end_lineno
                return (docstring_start, docstring_end)
        
        return None
    
    def _find_inline_code_blocks(self, test_node: ast.FunctionDef, test_body_lines: List[str],
                                 helper_functions: Set[str], tree: ast.AST) -> List[Tuple[int, int, List[str]]]:
        blocks = []
        current_block_start = None
        current_block_lines = []
        
        body_start_line = test_node.lineno
        
        docstring_range = self._get_docstring_line_range(test_node)
        
        in_multiline_call = False
        paren_balance = 0
        
        for i, line in enumerate(test_body_lines):
            line_num = body_start_line + i
            stripped = line.strip()
            
            if docstring_range and docstring_range[0] <= line_num <= docstring_range[1]:
                if current_block_start is not None:
                    self._end_current_block(blocks, current_block_start, line_num - 1, current_block_lines)
                current_block_start, current_block_lines, in_multiline_call, paren_balance = self._reset_block_state()
                continue
            
            if (not stripped or 
                stripped.startswith('#') or 
                stripped.startswith('@')):
                if current_block_start is not None:
                    self._end_current_block(blocks, current_block_start, line_num - 1, current_block_lines)
                if in_multiline_call:
                    current_block_start, current_block_lines, in_multiline_call, paren_balance = self._reset_block_state()
                    continue
                current_block_start, current_block_lines, in_multiline_call, paren_balance = self._reset_block_state()
                continue
            
            is_helper_call_start = self._is_helper_function_call(stripped, helper_functions, tree)
            
            if is_helper_call_start:
                paren_balance = stripped.count('(') - stripped.count(')')
                in_multiline_call = paren_balance > 0
                if current_block_start is not None:
                    blocks.append((current_block_start, line_num - 1, current_block_lines))
                    current_block_start = None
                    current_block_lines = []
            elif in_multiline_call:
                paren_balance += stripped.count('(') - stripped.count(')')
                if paren_balance == 0:
                    in_multiline_call = False
                continue
            else:
                if current_block_start is None:
                    current_block_start = line_num
                current_block_lines.append(stripped)
                paren_balance = 0
        
        if current_block_start is not None:
            last_line_num = body_start_line + len(test_body_lines) - 1
            blocks.append((current_block_start, last_line_num, current_block_lines))
        
        return blocks
    
    def _is_helper_function_call(self, line: str, helper_functions: Set[str], tree: ast.AST) -> bool:
        for helper_name in helper_functions:
            if re.search(rf'\b{re.escape(helper_name)}\s*\(', line):
                return True
        
        if re.search(r'self\.(given_|when_|then_)\w+\s*\(', line):
            return True
        
        helper_patterns = [
            r'\b(given_|when_|then_|verify_|create_|setup_|bootstrap_)\w+\s*\(',
            r'self\.(given_|when_|then_|verify_|create_|setup_)\w+\s*\(',
        ]
        for pattern in helper_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _end_current_block(self, blocks: List, current_block_start: int, end_line: int, current_block_lines: List[str]) -> None:
        blocks.append((current_block_start, end_line, current_block_lines))
    
    def _reset_block_state(self):
        return None, [], False, 0
    
    def scan_cross_file(
        self,
        rule_obj: Any = None,
        test_files: Optional[List[Path]] = None,
        code_files: Optional[List[Path]] = None,
        all_test_files: Optional[List[Path]] = None,
        all_code_files: Optional[List[Path]] = None,
        status_writer: Optional[Any] = None,
        max_cross_file_comparisons: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        violations = []
        
        if not test_files or len(test_files) < 2:
            return violations
        
        parsed_files = self._get_all_test_files_parsed(test_files)
        
        helper_definitions = {}
        
        for file_path, content, tree in parsed_files:
            defined_helpers = self._get_defined_helper_functions(tree)
            
            for func_name, line_number in defined_helpers.items():
                if func_name not in helper_definitions:
                    helper_definitions[func_name] = []
                helper_definitions[func_name].append((
                    str(file_path),
                    line_number
                ))
        
        for func_name, definitions in helper_definitions.items():
            if len(definitions) > 1:
                files_list = ', '.join([f"{Path(f).name}:{line}" for f, line in definitions])
                violation = Violation(
                    rule=rule_obj,
                    violation_message=(
                        f'Helper function "{func_name}" is defined in {len(definitions)} different files. '
                        f'Consolidate into a shared helper file based on reuse scope. '
                        f'Found in: {files_list}'
                    ),
                    location=definitions[0][0],
                    line_number=definitions[0][1],
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        
        return violations

