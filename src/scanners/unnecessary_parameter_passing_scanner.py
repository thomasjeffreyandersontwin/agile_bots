"""Scanner for detecting unnecessary parameter passing in code."""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

logger = logging.getLogger(__name__)


class UnnecessaryParameterPassingScanner(CodeScanner):

    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        if self._is_test_file(file_path):
            return violations
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        # Find classes and check their methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                violations.extend(self._check_class_methods(node, content, file_path))
        
        return violations
    
    def _check_class_methods(self, class_node: ast.ClassDef, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for unnecessary parameter passing within a class."""
        violations = []
        
        # Get all instance variable accesses in __init__
        instance_vars = self._get_instance_variables(class_node)
        if not instance_vars:
            return violations
        
        # Check each method for unnecessary parameter passing
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_') and node.name != '__init__':
                    # This is a private/internal method
                    violations.extend(self._check_method_parameters(
                        node, instance_vars, content, file_path, class_node.name
                    ))
        
        return violations
    
    def _get_instance_variables(self, class_node: ast.ClassDef) -> set:
        instance_vars = set()
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == 'self':
                    instance_vars.add(node.attr)
        
        return instance_vars
    
    def _check_method_parameters(
        self, 
        method_node: ast.FunctionDef, 
        instance_vars: set,
        content: str,
        file_path: Path,
        class_name: str
    ) -> List[Dict[str, Any]]:
        """Check if method parameters match instance variables."""
        violations = []
        
        # Skip magic methods - they have special parameter semantics
        if method_node.name.startswith('__') and method_node.name.endswith('__'):
            return violations
        
        # Get parameter names (excluding self, cls, args, kwargs)
        param_names = []
        for arg in method_node.args.args:
            if arg.arg not in ('self', 'cls', 'args', 'kwargs'):
                param_names.append(arg.arg)
        
        # Check if any parameters match instance variable names
        for param_name in param_names:
            # Skip generic common parameter names that often have different semantics
            if param_name in ('name', 'instructions', 'rule', 'rules', 'story_graph', 'context', 'data'):
                continue
            
            # Check for exact match or close match with instance vars
            for inst_var in instance_vars:
                if self._names_match(param_name, inst_var):
                    # Skip if the instance var has a suffix suggesting different semantic meaning
                    # e.g., behavior_name (string) vs behavior (object)
                    if self._has_semantic_difference(param_name, inst_var):
                        continue
                    
                    # This parameter name matches an instance variable
                    violation = self._create_violation_with_snippet(
                        violation_message=f'Method "{method_node.name}" in class "{class_name}" receives parameter "{param_name}" that matches instance variable "self.{inst_var}". Access self.{inst_var} directly instead of passing as parameter.',
                        file_path=file_path,
                        line_number=method_node.lineno,
                        severity='warning',
                        content=content,
                        ast_node=method_node,
                        max_lines=10
                    )
                    violations.append(violation)
                    break  # Only report once per parameter
        
        return violations
    
    def _has_semantic_difference(self, param_name: str, inst_var_name: str) -> bool:
        """Check if names suggest semantically different things."""
        # If one has '_name' suffix and the other doesn't, they're likely different
        # (e.g., behavior_name vs behavior)
        param_has_name = param_name.endswith('_name')
        inst_has_name = inst_var_name.endswith('_name')
        if param_has_name != inst_has_name:
            return True
        
        return False
    
    def _names_match(self, param_name: str, inst_var_name: str) -> bool:
        # Exact match
        if param_name == inst_var_name:
            return True
        
        # Match with underscore prefix stripped
        if param_name == inst_var_name.lstrip('_'):
            return True
        if inst_var_name == param_name.lstrip('_'):
            return True
        
        # Match with common suffixes/prefixes
        common_variations = [
            f'{param_name}_path',
            f'{param_name}_file',
            f'{param_name}_folder',
            f'{param_name}_dir',
            f'{param_name}_name',
            f'{inst_var_name}_path',
            f'{inst_var_name}_file',
            f'{inst_var_name}_folder',
            f'{inst_var_name}_dir',
            f'{inst_var_name}_name',
        ]
        
        if inst_var_name in common_variations or param_name in common_variations:
            return True
        
        return False
