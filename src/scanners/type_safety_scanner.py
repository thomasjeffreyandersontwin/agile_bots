
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class TypeSafetyScanner(CodeScanner):
    
    ALLOWED_DICT_ANY_METHODS = {
        'to_dict', 'from_dict', 'to_json', 'from_json', 'serialize', 'deserialize',
        'read_json_file', 'write_json_file', 'load_json', 'save_json',
        'create_test_data', 'mock_response',
        'scan', 'scan_file', 'scan_cross_file',
        '_load_config', 'load_config',
    }
    
    ALLOWED_DICT_ANY_PARAMS = {
        'kwargs', 'options', 'metadata', 'extra', 'attrs', 'attributes',
        'story_graph', 'rule_content', 'config',
    }
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        if file_path.name.startswith('test_'):
            return violations
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            func_violations = self._check_function_type_safety(function.node, file_path, rule_obj, content)
            violations.extend(func_violations)
        
        return violations
    
    def _check_function_type_safety(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, content: str) -> List[Dict[str, Any]]:
        violations = []
        
        func_name = func_node.name
        
        if func_name in self.ALLOWED_DICT_ANY_METHODS:
            return violations
        
        if func_name.startswith('_') and not func_name.startswith('__'):
            if func_name not in ('do_execute', '_execute', '_process', '_handle'):
                return violations
        
        param_violations = self._check_parameter_types(func_node, file_path, rule_obj, content)
        violations.extend(param_violations)
        
        return_violations = self._check_return_type(func_node, file_path, rule_obj, content)
        violations.extend(return_violations)
        
        get_violations = self._check_parameters_get_pattern(func_node, file_path, rule_obj, content)
        violations.extend(get_violations)
        
        return violations
    
    def _check_parameter_types(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, content: str) -> List[Dict[str, Any]]:
        violations = []
        
        for arg in func_node.args.args:
            param_name = arg.arg
            
            if param_name in ('self', 'cls'):
                continue
            
            if param_name in self.ALLOWED_DICT_ANY_PARAMS:
                continue
            
            annotation = arg.annotation
            if annotation and self._is_dict_any_annotation(annotation):
                message = self._get_violation_message(
                    rule_obj, 'dict_any_parameter', func_node.lineno,
                    method=func_node.name, param=param_name
                )
                violations.append(
                    self._create_violation_with_snippet(
                        rule_obj=rule_obj,
                        violation_message=message,
                        file_path=file_path,
                        line_number=func_node.lineno,
                        severity='warning',
                        content=content,
                        ast_node=func_node,
                        max_lines=10
                    )
                )
                break
        
        return violations
    
    def _check_return_type(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, content: str) -> List[Dict[str, Any]]:
        violations = []
        
        returns = func_node.returns
        if returns and self._is_dict_any_annotation(returns):
            if any(pattern in func_node.name.lower() for pattern in ['to_dict', 'as_dict', 'to_json', 'serialize']):
                return violations
            
            message = self._get_violation_message(
                rule_obj, 'dict_any_return', func_node.lineno,
                method=func_node.name
            )
            violations.append(
                self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=message,
                    file_path=file_path,
                    line_number=func_node.lineno,
                    severity='warning',
                    content=content,
                    ast_node=func_node,
                    max_lines=10
                )
            )
        
        return violations
    
    def _check_parameters_get_pattern(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any, content: str) -> List[Dict[str, Any]]:
        violations = []
        found_lines = set()
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'get':
                        if isinstance(node.func.value, ast.Name):
                            var_name = node.func.value.id
                            if var_name in ('parameters', 'params', 'kwargs'):
                                line_no = node.lineno
                                if line_no not in found_lines:
                                    found_lines.add(line_no)
                                    message = self._get_violation_message(
                                        rule_obj, 'parameters_get_pattern', line_no
                                    )
                                    violations.append(
                                        Violation(
                                            rule=rule_obj,
                                            violation_message=message,
                                            location=str(file_path),
                                            line_number=line_no,
                                            severity='warning'
                                        ).to_dict()
                                    )
        
        # Limit to first 3 violations per function to avoid noise
        return violations[:3]
    
    def _is_dict_any_annotation(self, annotation: ast.AST) -> bool:
        if isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id == 'Dict':
                    if isinstance(annotation.slice, ast.Tuple):
                        if len(annotation.slice.elts) >= 2:
                            second_arg = annotation.slice.elts[1]
                            if isinstance(second_arg, ast.Name) and second_arg.id == 'Any':
                                return True
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id == 'dict':
                    if isinstance(annotation.slice, ast.Tuple):
                        if len(annotation.slice.elts) >= 2:
                            second_arg = annotation.slice.elts[1]
                            if isinstance(second_arg, ast.Name) and second_arg.id == 'Any':
                                return True
        
        if isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Attribute):
                if annotation.value.attr == 'Dict':
                    if isinstance(annotation.slice, ast.Tuple):
                        if len(annotation.slice.elts) >= 2:
                            second_arg = annotation.slice.elts[1]
                            if isinstance(second_arg, ast.Name) and second_arg.id == 'Any':
                                return True
        
        return False
    
    def _get_violation_message(self, rule_obj: Any, message_key: str, line_number: int, **format_args) -> str:
        if rule_obj and hasattr(rule_obj, 'rule_content'):
            violation_messages = rule_obj.rule_content.get('violation_messages', {})
            if message_key in violation_messages:
                template = violation_messages[message_key]
                return template.format(line=line_number, **format_args)
        
        defaults = {
            'dict_any_parameter': f"Line {line_number}: Method '{format_args.get('method', 'unknown')}' uses Dict[str, Any] parameter '{format_args.get('param', 'unknown')}'. Define a typed dataclass/class instead.",
            'dict_any_return': f"Line {line_number}: Method '{format_args.get('method', 'unknown')}' returns Dict[str, Any]. Define a typed result class instead.",
            'parameters_get_pattern': f"Line {line_number}: Found 'parameters.get()' pattern. Use typed context object with direct attribute access.",
            'kwargs_abuse': f"Line {line_number}: Method '{format_args.get('method', 'unknown')}' uses **kwargs when parameter set is known. Define explicit typed parameters.",
            'list_any_type': f"Line {line_number}: Found List[Any] type hint. Specify the element type."
        }
        return defaults.get(message_key, f'Line {line_number}: Type safety violation detected.')

