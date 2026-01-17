
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .resources.ast_elements import Functions, IfStatements

logger = logging.getLogger(__name__)

class ExcessiveGuardsScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        # Hard-coded exclusion: Don't run this rule on scanner files themselves
        # Scanners need defensive guards to handle various code patterns safely
        file_path_str = str(file_path).lower()
        if 'scanners' in file_path_str and file_path_str.endswith('_scanner.py'):
            return violations
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if function.is_test_function:
                continue
            
            if function.name.startswith('_') and function.name != '__init__':
                continue
            
            func_violations = self._check_function_guards(function.node, file_path, lines, content)
            violations.extend(func_violations)
        
        return violations
    
    def _check_function_guards(self, func_node: ast.FunctionDef, file_path: Path, source_lines: List[str], content: str) -> List[Dict[str, Any]]:
        violations = []
        
        # Extract parameter defaults to identify truly optional parameters
        optional_params = self._get_optional_parameters(func_node)
        
        if_statements = IfStatements(func_node)
        for if_stmt in if_statements.get_many_if_statements:
            if self._is_guard_clause(if_stmt.node, source_lines):
                violation = self._check_guard_pattern(if_stmt.node, file_path, source_lines, content, func_node, optional_params)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _is_guard_clause(self, if_node: ast.If, source_lines: List[str]) -> bool:
        # Skip if this has elif/else - that's legitimate branching
        if if_node.orelse:
            # Check if orelse is another if (elif) or actual else block
            if len(if_node.orelse) > 0:
                return False
        
        body_is_simple = len(if_node.body) == 1
        if body_is_simple:
            first_stmt = if_node.body[0]
            is_early_exit = isinstance(first_stmt, (ast.Return, ast.Continue, ast.Break))
            
            # Pattern 1: Actual guard clause (early exit)
            if is_early_exit:
                return self._is_guard_pattern(if_node.test)
        
        # Pattern 2: Inverted guard (positive check without else)
        # Only flag if it's a validation pattern (None check, truthiness check)
        if not if_node.orelse and self._is_guard_pattern(if_node.test):
            return True
        
        return False
    
    def _is_guard_pattern(self, test_node: ast.AST) -> bool:
        if self._is_guard_call_pattern(test_node):
            return True
        
        if isinstance(test_node, ast.Name):
            return True
        if isinstance(test_node, ast.UnaryOp) and isinstance(test_node.op, ast.Not):
            if isinstance(test_node.operand, ast.Name):
                return True
        
        if isinstance(test_node, ast.Compare) and self._compare_checks_none(test_node):
            return True
        
        return False
    
    def _is_guard_call_pattern(self, test_node: ast.AST) -> bool:
        """Check if test is a guard-related call (hasattr, isinstance, exists)."""
        if not isinstance(test_node, ast.Call):
            return False
        
        if isinstance(test_node.func, ast.Name):
            return test_node.func.id in ('hasattr', 'isinstance')
        
        if isinstance(test_node.func, ast.Attribute):
            return test_node.func.attr == 'exists'
        
        return False
    
    def _compare_checks_none(self, test_node: ast.Compare) -> bool:
        """Check if comparison checks for None."""
        for op in test_node.ops:
            if isinstance(op, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
                for comparator in test_node.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value is None:
                        return True
                    if isinstance(comparator, ast.NameConstant) and comparator.value is None:
                        return True
        return False
    
    def _get_violation_message(self, message_key: str, line_number: int, **format_args) -> str:
        if self.rule and hasattr(self.rule, 'rule_content'):
            violation_messages = self.rule.rule_content.get('violation_messages', {})
            if message_key in violation_messages:
                template = violation_messages[message_key]
                return template.format(line=line_number, **format_args)
        
        defaults = {
            'hasattr_guard': f'Line {line_number}: hasattr() guard clause detected. Assume attributes exist - let AttributeError propagate if missing.',
            'file_existence_guard': f'Line {line_number}: File existence check detected. Let file operations fail if file missing - handle errors centrally.',
            'none_check_guard': f'Line {line_number}: None check guard clause detected. Assume variables are initialized - let code fail fast if None.',
            'truthiness_check_guard': f'Line {line_number}: Variable truthiness check detected (if {format_args.get("var", "variable")}:). Assume variable exists - let code fail fast if missing.',
            'truthiness_check_guard_not': f'Line {line_number}: Variable truthiness check detected (if not {format_args.get("var", "variable")}:). Assume variable exists - let code fail fast if missing.'
        }
        return defaults.get(message_key, f'Line {line_number}: Guard clause detected.')

    def _is_optional_config_check(self, guard_node: ast.If, source_lines: List[str]) -> bool:
        test = guard_node.test
        
        if self._is_file_exists_check_with_creation(test, guard_node, source_lines):
            return True
        
        if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == 'hasattr':
            return True
        
        if self._returns_empty_value(guard_node):
            return True
        
        if self._test_checks_optional_variable(test):
            return True
        
        return False
    
    def _is_file_exists_check_with_creation(self, test: ast.expr, guard_node: ast.If, source_lines: List[str]) -> bool:
        """Check if test is file.exists() followed by creation."""
        if not isinstance(test, ast.Call):
            return False
        if not isinstance(test.func, ast.Attribute):
            return False
        if test.func.attr != 'exists':
            return False
        return self._is_followed_by_creation_logic(guard_node, source_lines)
    
    def _returns_empty_value(self, guard_node: ast.If) -> bool:
        """Check if guard returns empty value."""
        if not guard_node.body:
            return False
        
        first_stmt = guard_node.body[0]
        if not isinstance(first_stmt, ast.Return):
            return False
        
        if first_stmt.value is None:
            return True
        if isinstance(first_stmt.value, ast.Constant) and first_stmt.value.value in ([], {}, None, ''):
            return True
        if isinstance(first_stmt.value, (ast.List, ast.Dict)):
            return True
        
        return False
    
    def _test_checks_optional_variable(self, test: ast.expr) -> bool:
        """Check if test checks an optional variable pattern."""
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if isinstance(test.operand, ast.Name):
                return self._check_optional_pattern(test.operand.id.lower())
        
        if isinstance(test, ast.Name):
            return self._check_optional_pattern(test.id.lower())
        
        if isinstance(test, ast.Compare):
            return self._compare_checks_optional_variable(test)
        
        return False
    
    def _compare_checks_optional_variable(self, test: ast.Compare) -> bool:
        """Check if comparison checks optional variable."""
        for op in test.ops:
            if not isinstance(op, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
                continue
            
            for comparator in test.comparators:
                if self._comparator_is_none(comparator) and isinstance(test.left, ast.Name):
                    if self._check_optional_pattern(test.left.id.lower()):
                        return True
        return False
    
    def _comparator_is_none(self, comparator: ast.expr) -> bool:
        """Check if comparator is None."""
        if isinstance(comparator, ast.Constant) and comparator.value is None:
            return True
        if isinstance(comparator, ast.NameConstant) and comparator.value is None:
            return True
        return False
    
    def _check_optional_pattern(self, var_name: str) -> bool:
        optional_patterns = ['config', 'template', 'option', 'setting', 'file', 'dir', 'path',
                            'pattern', 'spec', 'rule', 'violation', 'action', 'behavior',
                            'trigger', 'command', 'desc', 'instruction', 'error', 'info',
                            'name', 'obj', 'instance', 'module', 'class', 'background',
                            'parsed', 'result', 'content', 'tree', 'lines', 'data', 'value',
                            'item', 'entry', 'record', 'element', 'node', 'entity',
                            'response', 'output', 'input', 'param', 'arg', 'var',
                            'list', 'dict', 'set', 'collection', 'items', 'entries',
                            'scenario', 'step', 'answer', 'evidence', 'decision', 'assumption',
                            'workspace', 'directory']
        return any(pattern in var_name for pattern in optional_patterns)
    
    def _is_followed_by_creation_logic(self, guard_node: ast.If, source_lines: List[str]) -> bool:
        if guard_node.orelse:
            for stmt in guard_node.orelse:
                if self._contains_creation_call(stmt):
                    return True
        
        start_line = guard_node.lineno - 1
        end_line = guard_node.end_lineno if hasattr(guard_node, 'end_lineno') else start_line + len(guard_node.body) + 1
        
        if guard_node.orelse:
            for stmt in guard_node.orelse:
                if hasattr(stmt, 'lineno'):
                    stmt_start = stmt.lineno - 1
                    stmt_end = stmt.end_lineno if hasattr(stmt, 'end_lineno') else stmt_start + 1
                    for i in range(stmt_start, min(stmt_end + 1, len(source_lines))):
                        line = source_lines[i].strip()
                        creation_patterns = ['.write_text', '.write_bytes', '.mkdir', '.touch', 'open(']
                        if any(pattern in line for pattern in creation_patterns):
                            return True
        
        for i in range(end_line, min(end_line + 5, len(source_lines))):
            line = source_lines[i].strip()
            if not line or line.startswith('#'):
                continue
            creation_patterns = ['.write_text', '.write_bytes', '.mkdir', '.touch', 'open(']
            if any(pattern in line for pattern in creation_patterns):
                return True
        
        return False
    
    def _contains_creation_call(self, node: ast.AST) -> bool:
        creation_methods = ['write_text', 'write_bytes', 'mkdir', 'touch']
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and self._call_is_creation_method(child, creation_methods):
                return True
        return False
    
    def _call_is_creation_method(self, call: ast.Call, creation_methods: List[str]) -> bool:
        """Check if call is a creation method."""
        if isinstance(call.func, ast.Attribute):
            return call.func.attr in creation_methods
        return False

    def _get_optional_parameters(self, func_node: ast.FunctionDef) -> set:
        optional_params = set()
        
        args = func_node.args
        num_defaults = len(args.defaults)
        num_args = len(args.args)
        
        # Match defaults to their corresponding arguments
        for i, default in enumerate(args.defaults):
            # defaults are aligned to the right, so we need to offset
            arg_index = num_args - num_defaults + i
            arg = args.args[arg_index]
            
            # Check if default is None
            is_none_default = False
            if isinstance(default, ast.Constant) and default.value is None:
                is_none_default = True
            elif isinstance(default, ast.NameConstant) and default.value is None:
                is_none_default = True
            
            if is_none_default:
                optional_params.add(arg.arg)
        
        return optional_params
    
    def _is_lazy_initialization(self, guard_node: ast.If, func_node: ast.FunctionDef) -> bool:
        if not self._is_property_function(func_node):
            return False
        
        if not self._is_none_comparison(guard_node.test):
            return False
        
        return self._body_has_private_self_assignment(guard_node.body)
    
    def _is_property_function(self, func_node: ast.FunctionDef) -> bool:
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'property':
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr in ('getter', 'setter'):
                return True
        return False
    
    def _is_none_comparison(self, test: ast.expr) -> bool:
        if not isinstance(test, ast.Compare):
            return False
        for op in test.ops:
            if not isinstance(op, (ast.Is, ast.IsNot)):
                continue
            for comparator in test.comparators:
                if self._is_none_constant(comparator):
                    return True
        return False
    
    def _is_none_constant(self, node: ast.expr) -> bool:
        if isinstance(node, ast.Constant) and node.value is None:
            return True
        if isinstance(node, ast.NameConstant) and node.value is None:
            return True
        return False
    
    def _body_has_private_self_assignment(self, body: List[ast.stmt]) -> bool:
        for stmt in body:
            if not isinstance(stmt, ast.Assign):
                continue
            for target in stmt.targets:
                if self._is_private_self_attribute(target):
                    return True
        return False
    
    def _is_private_self_attribute(self, target: ast.expr) -> bool:
        if not isinstance(target, ast.Attribute):
            return False
        if not isinstance(target.value, ast.Name) or target.value.id != 'self':
            return False
        return target.attr.startswith('_')
    
    def _check_guard_pattern(self, guard_node: ast.If, file_path: Path, source_lines: List[str], content: str, func_node: ast.FunctionDef = None, optional_params: set = None) -> Optional[Dict[str, Any]]:
        test = guard_node.test
        
        if optional_params is None:
            optional_params = set()
        
        # Check if this is lazy initialization in a property
        if func_node and self._is_lazy_initialization(guard_node, func_node):
            return None
        
        # Check if this is a None check for a parameter with default None
        if isinstance(test, ast.Compare):
            for op in test.ops:
                if isinstance(op, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)):
                    for comparator in test.comparators:
                        if (isinstance(comparator, ast.Constant) and comparator.value is None) or \
                           (isinstance(comparator, ast.NameConstant) and comparator.value is None):
                            # Check if the variable being checked is an optional parameter
                            if isinstance(test.left, ast.Name) and test.left.id in optional_params:
                                return None
        
        if self._is_optional_config_check(guard_node, source_lines):
            return None
        
        # Check if this is a guard for raising an exception - explicitly allowed
        if self._is_exception_guard(guard_node):
            return None
        
        # Check if this is conditional append pattern for optional parameters
        if self._is_conditional_append_pattern(guard_node, func_node, optional_params):
            return None
        
        if isinstance(test, ast.Compare):
            for op in test.ops:
                if isinstance(op, (ast.Is, ast.IsNot)):
                    for comparator in test.comparators:
                        if isinstance(comparator, ast.Constant) and comparator.value is None:
                            return self._create_violation_with_snippet(
                                violation_message=self._get_violation_message('none_check_guard', guard_node.lineno),
                                file_path=file_path,
                                line_number=guard_node.lineno,
                                severity='warning',
                                content=content,
                                ast_node=guard_node
                            )
                        if isinstance(comparator, ast.NameConstant) and comparator.value is None:
                            return self._create_violation_with_snippet(
                                violation_message=self._get_violation_message('none_check_guard', guard_node.lineno),
                                file_path=file_path,
                                line_number=guard_node.lineno,
                                severity='warning',
                                content=content,
                                ast_node=guard_node
                            )
        
        # For simple truthiness checks, verify the variable could be guaranteed truthy
        if isinstance(test, ast.Name):
            var_name = self._get_variable_name(test)
            # Check if variable is from an optional parameter
            if var_name in optional_params:
                return None
            # Check if variable could be None/empty from its source
            if func_node and self._variable_could_be_empty(var_name, func_node, guard_node):
                return None
            return self._create_violation_with_snippet(
                violation_message=self._get_violation_message('truthiness_check_guard', guard_node.lineno, var=var_name),
                file_path=file_path,
                line_number=guard_node.lineno,
                severity='warning',
                content=content,
                ast_node=guard_node
            )
        
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if isinstance(test.operand, ast.Name):
                var_name = self._get_variable_name(test.operand)
                # Check if variable is from an optional parameter
                if var_name in optional_params:
                    return None
                # Check if variable could be None/empty from its source
                if func_node and self._variable_could_be_empty(var_name, func_node, guard_node):
                    return None
                return self._create_violation_with_snippet(
                    violation_message=self._get_violation_message('truthiness_check_guard_not', guard_node.lineno, var=var_name),
                    file_path=file_path,
                    line_number=guard_node.lineno,
                    severity='warning',
                    content=content,
                    ast_node=guard_node
                )
        
        return None
    
    def _get_variable_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        return 'variable'
    
    def _is_exception_guard(self, guard_node: ast.If) -> bool:
        for stmt in guard_node.body:
            if isinstance(stmt, ast.Raise):
                return True
            # Also check nested blocks
            for child in ast.walk(stmt):
                if isinstance(child, ast.Raise):
                    return True
        return False
    
    def _is_conditional_append_pattern(self, guard_node: ast.If, func_node: ast.FunctionDef, optional_params: set) -> bool:
        test_var = self._extract_test_variable(guard_node.test)
        
        if not test_var:
            return False
        
        if test_var in optional_params and self._body_has_append_operations(guard_node):
            return True
        
        if func_node and self._variable_could_be_empty(test_var, func_node, guard_node):
            if self._body_has_append_operations(guard_node):
                return True
        
        return False
    
    def _extract_test_variable(self, test: ast.expr) -> Optional[str]:
        """Extract variable being tested in guard."""
        if isinstance(test, ast.Name):
            return test.id
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
            if isinstance(test.operand, ast.Name):
                return test.operand.id
        return None
    
    def _body_has_append_operations(self, guard_node: ast.If) -> bool:
        """Check if guard body contains append/extend/add/update operations."""
        for stmt in guard_node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                if isinstance(stmt.value.func, ast.Attribute):
                    if stmt.value.func.attr in ('append', 'extend', 'add', 'update'):
                        return True
        return False
    
    def _variable_could_be_empty(self, var_name: str, func_node: ast.FunctionDef, guard_node: ast.If) -> bool:
        if self._check_optional_pattern(var_name):
            return True
        
        if self._variable_assigned_from_optional_source(var_name, func_node):
            return True
        
        # If we can't prove it's always truthy, assume it could be empty (safe default)
        return True
    
    def _variable_assigned_from_optional_source(self, var_name: str, func_node: ast.FunctionDef) -> bool:
        """Check if variable is assigned from a source that could return None/empty."""
        for node in ast.walk(func_node):
            if not isinstance(node, ast.Assign):
                continue
            
            if self._assignment_targets_variable(node, var_name):
                if self._assignment_value_could_be_empty(node):
                    return True
        
        return False
    
    def _assignment_targets_variable(self, assign_node: ast.Assign, var_name: str) -> bool:
        """Check if assignment targets the given variable."""
        for target in assign_node.targets:
            if isinstance(target, ast.Name) and target.id == var_name:
                return True
            if isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name) and elt.id == var_name:
                        return True
        return False
    
    def _assignment_value_could_be_empty(self, assign_node: ast.Assign) -> bool:
        """Check if assignment value could be None or empty."""
        value = assign_node.value
        
        if isinstance(value, ast.Call):
            if isinstance(value.func, ast.Attribute):
                if value.func.attr in ('get', 'pop', 'setdefault'):
                    return True
                method_name = value.func.attr
                optional_methods = ['find', 'find_by', 'get', 'fetch', 'load', 'read', 
                                  'parse', 'extract', 'search', 'lookup', 'query',
                                  'discover', 'locate', 'retrieve']
                if any(opt in method_name.lower() for opt in optional_methods):
                    return True
            return True  # Function calls can return None
        
        if isinstance(value, ast.IfExp):
            return True
        
        return False
    
