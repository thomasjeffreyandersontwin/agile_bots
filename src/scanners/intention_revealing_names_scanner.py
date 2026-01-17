
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions, Classes

logger = logging.getLogger(__name__)


class IntentionRevealingNamesScanner(CodeScanner):
    """Scanner for detecting names that don't reveal intention."""
    
    ACCEPTABLE_DOMAIN_TERMS = {
        'scan', 'scan_test_file', 'scan_code_file', 'scan_cross_file',
        'parse', 'render', 'build', 'load', 'save', 'read', 'write',
        'get', 'set', 'has', 'is', 'can',
        'init', '__init__', '__str__', '__repr__', '__eq__',
    }
    
    ACCEPTABLE_CONTEXT_NAMES = {
        'data',
        'value',
        'item',
        'result',
    }
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        domain_terms = set()
        if self.story_graph:
            domain_terms = self._extract_domain_terms(self.story_graph)
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        docstring_ranges = self._get_docstring_ranges(tree)
        
        violations.extend(self._check_variable_names(tree, file_path, rule_obj, content, domain_terms, docstring_ranges))
        
        violations.extend(self._check_function_names(tree, file_path, rule_obj, domain_terms))
        
        violations.extend(self._check_class_names(tree, file_path, rule_obj, domain_terms))
        
        return violations
    
    def _check_variable_names(self, tree: ast.AST, file_path: Path, rule_obj: Any, content: str, domain_terms: set = None, docstring_ranges: List[tuple] = None) -> List[Dict[str, Any]]:
        violations = []
        
        if domain_terms is None:
            domain_terms = set()
        if docstring_ranges is None:
            docstring_ranges = []
        
        generic_names = ['info', 'thing', 'stuff', 'temp']
        
        acceptable_single_letter_names = self._collect_loop_and_comprehension_var_names(tree)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                var_name = node.id
                
                if self._is_in_docstring_or_comment(node, content, docstring_ranges):
                    continue
                
                if isinstance(node.ctx, ast.Store):
                    if self._is_acceptable_in_context(node, tree, content):
                        continue
                
                always_allowed = {'i', 'j', 'k', '_'}
                if len(var_name) == 1:
                    if var_name in always_allowed:
                        continue
                    if var_name in acceptable_single_letter_names:
                        continue
                    violations.append(self._create_generic_name_violation(
                        rule_obj, file_path, node, var_name, 'variable', 'single-letter'
                    ))
                    continue
                
                var_name_lower = var_name.lower()
                if var_name_lower in generic_names:
                    if var_name_lower in domain_terms:
                        continue
                    if not self._is_acceptable_in_context(node, tree, content):
                        violations.append(self._create_generic_name_violation(
                            rule_obj, file_path, node, var_name, 'variable', 'generic'
                        ))
                elif domain_terms:
                    if self._matches_domain_term(var_name, domain_terms):
                        continue
        
        return violations
    
    def _create_generic_name_violation(
        self, 
        rule_obj: Any, 
        file_path: Path, 
        node: ast.AST, 
        name: str, 
        name_type: str, 
        issue_type: str,
        severity: str = 'error'
    ) -> Dict[str, Any]:
        line_number = node.lineno if hasattr(node, 'lineno') else None
        
        if issue_type == 'single-letter':
            message = f'{name_type.capitalize()} "{name}" uses single-letter name - use intention-revealing name'
        elif name_type == 'function':
            message = f'Function "{name}" uses generic name - use intention-revealing name that explains purpose'
        elif name_type == 'class':
            message = f'Class "{name}" uses generic name - use intention-revealing name that explains purpose'
        else:
            message = f'Variable "{name}" uses generic name - use intention-revealing name'
        
        try:
            content = file_path.read_text(encoding='utf-8')
            return self._create_violation_with_snippet(
                rule_obj=rule_obj,
                violation_message=message,
                file_path=file_path,
                line_number=line_number,
                severity=severity,
                content=content,
                ast_node=node,
                max_lines=3
            )
        except Exception:
            return Violation(
                rule=rule_obj,
                violation_message=message,
                location=str(file_path),
                line_number=line_number,
                severity=severity
            ).to_dict()
    
    def _collect_loop_and_comprehension_var_names(self, tree: ast.AST) -> set:
        acceptable_names = set()
        
        for node in ast.walk(tree):
            self._collect_var_names_from_node(node, acceptable_names)
        
        return acceptable_names
    
    def _collect_var_names_from_node(self, node: ast.AST, acceptable_names: set) -> None:
        if isinstance(node, ast.For):
            self._add_target_var_names(node.target, acceptable_names)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            acceptable_names.add(node.name)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for generator in node.generators:
                self._add_target_var_names(generator.target, acceptable_names)
        elif isinstance(node, ast.Lambda):
            for arg in node.args.args:
                acceptable_names.add(arg.arg)
        elif isinstance(node, ast.With):
            self._collect_with_var_names(node, acceptable_names)
    
    def _collect_with_var_names(self, node: ast.With, acceptable_names: set) -> None:
        for item in node.items:
            if item.optional_vars:
                self._add_target_var_names(item.optional_vars, acceptable_names)
    
    def _add_target_var_names(self, target: ast.AST, acceptable_names: set):
        if isinstance(target, ast.Name):
            acceptable_names.add(target.id)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                self._add_target_var_names(elt, acceptable_names)
    
    def _is_acceptable_in_context(self, node: ast.Name, tree: ast.AST, content: str) -> bool:
        
        return False
    
    def _check_function_names(self, tree: ast.AST, file_path: Path, rule_obj: Any, domain_terms: set = None) -> List[Dict[str, Any]]:
        violations = []
        
        if domain_terms is None:
            domain_terms = set()
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            func_name = function.node.name
            func_name_lower = func_name.lower()
            
            if func_name.startswith('_') and func_name != '__init__':
                continue
            
            if func_name_lower in self.ACCEPTABLE_DOMAIN_TERMS:
                continue
            
            if domain_terms:
                if self._matches_domain_term(func_name, domain_terms):
                    continue
            
            generic_names = ['process', 'handle', 'do', 'execute', 'run', 'main']
            if func_name_lower in generic_names and len(func_name.split('_')) == 1:
                violations.append(self._create_generic_name_violation(
                    rule_obj, file_path, function.node, func_name, 'function', 'generic'
                ))
        
        return violations
    
    def _check_class_names(self, tree: ast.AST, file_path: Path, rule_obj: Any, domain_terms: set = None) -> List[Dict[str, Any]]:
        violations = []
        
        if domain_terms is None:
            domain_terms = set()
        
        acceptable_class_patterns = ['Scanner', 'CodeScanner', 'TestScanner', 'StoryScanner']
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_name = cls.node.name
            class_name_lower = class_name.lower()
            
            if any(pattern in class_name for pattern in acceptable_class_patterns):
                continue
            
            if domain_terms:
                if self._matches_domain_term(class_name, domain_terms):
                    continue
            
            generic_names = ['Manager', 'Handler', 'Processor', 'Util', 'Helper', 'Service']
            if class_name in generic_names:
                violations.append(self._create_generic_name_violation(
                    rule_obj, file_path, cls.node, class_name, 'class', 'generic', 'error'
                ))
            elif any(class_name.endswith(g) and len(class_name) <= len(g) + 2 for g in generic_names):
                violations.append(self._create_generic_name_violation(
                    rule_obj, file_path, cls.node, class_name, 'class', 'generic', 'warning'
                ))
        
        return violations
    
    def _get_docstring_ranges(self, tree: ast.AST) -> List[tuple]:
        docstring_ranges = []
        
        def visit_node(node):
            if hasattr(node, 'body') and isinstance(node.body, list) and len(node.body) > 0:
                first_stmt = node.body[0]
                if isinstance(first_stmt, ast.Expr):
                    if isinstance(first_stmt.value, (ast.Constant, ast.Str)):
                        if isinstance(first_stmt.value, ast.Constant):
                            docstring_value = first_stmt.value.value
                        else:
                            docstring_value = first_stmt.value.s
                        
                        if isinstance(docstring_value, str):
                            start_line = first_stmt.lineno if hasattr(first_stmt, 'lineno') else None
                            if start_line:
                                docstring_lines = docstring_value.count('\n')
                                end_line = start_line + docstring_lines + 2
                                docstring_ranges.append((start_line, end_line))
            
            for child in ast.iter_child_nodes(node):
                visit_node(child)
        
        visit_node(tree)
        return docstring_ranges
    
    def _is_in_docstring_or_comment(self, node: ast.AST, content: str, docstring_ranges: List[tuple]) -> bool:
        if not hasattr(node, 'lineno'):
            return False
        
        line_number = node.lineno
        
        for start_line, end_line in docstring_ranges:
            if start_line <= line_number <= end_line:
                return True
        
        lines = content.split('\n')
        if line_number <= len(lines):
            line = lines[line_number - 1].strip()
            if line.startswith('#'):
                return True
            if line.startswith('"""') or line.startswith("'''"):
                return True
        
        return False

