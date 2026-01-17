
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .complexity_metrics import ComplexityMetrics
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class FunctionSizeScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if function.node.name.startswith('_') and function.node.name != '__init__':
                continue
            
            violation = self._check_function_size(function.node, file_path, self.rule, lines, content)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_function_size(self, func_node: ast.FunctionDef, file_path: Path, source_lines: List[str], content: str) -> Optional[Dict[str, Any]]:
        if not hasattr(func_node, 'end_lineno') or not func_node.end_lineno:
            logger.debug(f'Function node missing end_lineno at {file_path}:{func_node.lineno}')
            return None
        
        func_start_line = func_node.lineno - 1
        func_end_line = func_node.end_lineno
        
        if func_start_line < len(source_lines) and func_end_line <= len(source_lines):
            func_source_lines = source_lines[func_start_line:func_end_line]
        else:
            func_source_lines = []
        
        data_structure_line_nums = self._get_data_structure_line_numbers(func_node)
        
        comment_and_docstring_line_nums = self._get_comment_and_docstring_line_numbers(func_node, func_source_lines, func_start_line)
        
        multi_line_expression_line_nums = self._get_multi_line_expression_line_numbers(func_node)
        
        executable_lines = 0
        for i, line in enumerate(func_source_lines):
            line_num = func_start_line + i + 1
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            if line_num in data_structure_line_nums:
                continue
            
            if line_num in comment_and_docstring_line_nums:
                continue
            
            if line_num in multi_line_expression_line_nums:
                continue
            
            executable_lines += 1
        
        cyclomatic = ComplexityMetrics.cyclomatic_complexity(func_node)
        cognitive = ComplexityMetrics.cognitive_complexity(func_node)
        max_nesting = ComplexityMetrics.max_nesting_depth(func_node)
        
        violations = []
        
        line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
        
        if executable_lines > 50:
            violations.append(self._create_violation_with_snippet(
                violation_message=f'Function "{func_node.name}" is {executable_lines} lines - should be under 50 lines (extract complex logic to helper functions)',
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node
            ))
        
        if cyclomatic > 10:
            violations.append(self._create_violation_with_snippet(
                violation_message=(
                    f'Function "{func_node.name}" has high cyclomatic complexity ({cyclomatic}) - '
                    f'should be under 10. Extract decision logic to helper functions.'
                ),
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node
            ))
        
        if cognitive > 15:
            violations.append(self._create_violation_with_snippet(
                violation_message=(
                    f'Function "{func_node.name}" has high cognitive complexity ({cognitive}) - '
                    f'should be under 15. Reduce nesting and extract complex logic.'
                ),
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node
            ))
        
        if max_nesting > 4:
            violations.append(self._create_violation_with_snippet(
                violation_message=(
                    f'Function "{func_node.name}" has deep nesting (depth={max_nesting}) - '
                    f'should be under 4 levels. Extract nested logic to helper functions.'
                ),
                file_path=file_path,
                line_number=line_number,
                severity='info',
                content=content,
                ast_node=func_node
            ))
        
        return violations[0] if violations else None
    
    def _get_multi_line_expression_line_numbers(self, func_node: ast.FunctionDef) -> set:
        multi_line_lines = set()
        
        for stmt in func_node.body:
            lines = self._get_continuation_lines(stmt)
            multi_line_lines.update(lines)
        
        return multi_line_lines
    
    def _get_continuation_lines(self, stmt_node: ast.stmt) -> set:
        if not self._is_multi_line_statement(stmt_node):
            return set()
        
        value = self._get_multi_line_value(stmt_node)
        if not value or not self._is_multi_line_node(value):
            return set()
        
        return set(range(value.lineno + 1, value.end_lineno + 1))
    
    def _is_multi_line_statement(self, node: ast.AST) -> bool:
        if not hasattr(node, 'end_lineno') or not hasattr(node, 'lineno'):
            return False
        return node.end_lineno and node.lineno and node.end_lineno > node.lineno
    
    def _is_multi_line_node(self, node: ast.AST) -> bool:
        if not hasattr(node, 'end_lineno') or not hasattr(node, 'lineno'):
            return False
        return node.end_lineno and node.lineno and node.end_lineno > node.lineno
    
    def _get_multi_line_value(self, stmt_node: ast.stmt) -> Optional[ast.expr]:
        if isinstance(stmt_node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            return getattr(stmt_node, 'value', None)
        if isinstance(stmt_node, ast.Expr):
            value = getattr(stmt_node, 'value', None)
            return value if isinstance(value, ast.Call) else None
        if isinstance(stmt_node, ast.Return):
            return stmt_node.value
        return None
    
    def _get_data_structure_line_numbers(self, func_node: ast.FunctionDef) -> set:
        data_structure_lines = set()
        
        top_level_data_structures = []
        
        def visit_node(node, parent_is_ds=False):
            is_data_structure = isinstance(node, (ast.List, ast.Dict, ast.Set, ast.Tuple))
            
            if is_data_structure and not parent_is_ds:
                top_level_data_structures.append(node)
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, parent_is_ds=is_data_structure)
        
        for child in ast.iter_child_nodes(func_node):
            visit_node(child, parent_is_ds=False)
        
        for ds_node in top_level_data_structures:
            if hasattr(ds_node, 'end_lineno') and hasattr(ds_node, 'lineno') and ds_node.end_lineno and ds_node.lineno:
                ds_lines = ds_node.end_lineno - ds_node.lineno + 1
                if ds_lines > 1:
                    for line_num in range(ds_node.lineno, ds_node.end_lineno + 1):
                        data_structure_lines.add(line_num)
        
        return data_structure_lines
    
    def _get_comment_and_docstring_line_numbers(self, func_node: ast.FunctionDef, source_lines: List[str], func_start_line: int) -> set:
        comment_and_docstring_lines = set()
        
        if func_node.body:
            first_stmt = func_node.body[0]
            if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, (ast.Str, ast.Constant)):
                string_value = first_stmt.value
                if isinstance(string_value, ast.Constant) and isinstance(string_value.value, str):
                    if hasattr(first_stmt, 'end_lineno') and hasattr(first_stmt, 'lineno') and first_stmt.end_lineno and first_stmt.lineno:
                        for line_num in range(first_stmt.lineno, first_stmt.end_lineno + 1):
                            comment_and_docstring_lines.add(line_num)
                elif isinstance(string_value, ast.Str):
                    if hasattr(first_stmt, 'end_lineno') and hasattr(first_stmt, 'lineno') and first_stmt.end_lineno and first_stmt.lineno:
                        for line_num in range(first_stmt.lineno, first_stmt.end_lineno + 1):
                            comment_and_docstring_lines.add(line_num)
        
        func_start = func_node.lineno
        func_end = func_node.end_lineno if hasattr(func_node, 'end_lineno') and func_node.end_lineno else func_start + 20
        
        for line_num in range(func_start, func_end + 1):
            if line_num > len(source_lines):
                break
            
            line = source_lines[line_num - 1]
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            if line_stripped.startswith('#'):
                comment_and_docstring_lines.add(line_num)
        
        return comment_and_docstring_lines
