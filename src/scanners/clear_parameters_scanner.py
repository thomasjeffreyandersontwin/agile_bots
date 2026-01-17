
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext

logger = logging.getLogger(__name__)


class ClearParametersScanner(CodeScanner):
    """Scanner for detecting unclear or excessive function parameters."""
    
    ACCEPTABLE_PARAMETER_NAMES = {
        'data',
        'value',
        'item',
        'obj',
        'param',
        'arg',
        'kwargs', 'args',
        'self', 'cls',
    }
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        if not file_path.exists():
            return violations
        
        if self._is_test_file(file_path):
            return violations
        
        domain_terms = set()
        if self.story_graph:
            domain_terms = self._extract_domain_terms(self.story_graph)
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            violation = self._check_parameters(function.node, file_path, self.rule, domain_terms, content)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _is_test_file(self, file_path: Path) -> bool:
        path_str = str(file_path).lower()
        file_name = file_path.name.lower()
        
        if '/test' in path_str or '/tests' in path_str or '\\test' in path_str or '\\tests' in path_str:
            return True
        
        if file_name.startswith('test_'):
            return True
        
        if file_name == 'conftest.py':
            return True
        
        return False
    
    def _check_parameters(self, func_node: ast.FunctionDef, file_path: Path, domain_terms: set = None, content: str = None) -> Optional[Dict[str, Any]]:
        if domain_terms is None:
            domain_terms = set()
        
        max_params = 7 if func_node.name == '__init__' else 5
        if len(func_node.args.args) > max_params:
            line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
            return self._create_violation_with_snippet(
                                violation_message=f'Function "{func_node.name}" has {len(func_node.args.args)} parameters - consider using existing domain objects with properties instead of passing primitives. Extend domain objects (Behaviors, Behavior, Actions, RenderSpec, etc.) with properties that encapsulate the needed data rather than creating new parameter objects.',
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node,
                max_lines=5
            )
        
        vague_names = ['thing', 'stuff', 'info']
        for arg in func_node.args.args:
            if arg.arg in ['self', 'cls', 'args', 'kwargs']:
                continue
            
            arg_name_lower = arg.arg.lower()
            
            if arg_name_lower in domain_terms:
                continue
            
            if domain_terms:
                arg_words = arg_name_lower.split('_')
                if any(word in domain_terms for word in arg_words):
                    continue
            
            if arg_name_lower in self.ACCEPTABLE_PARAMETER_NAMES:
                if not self._function_name_provides_context(func_node.name, arg.arg):
                    continue
            
            if arg_name_lower in vague_names:
                line_number = func_node.lineno if hasattr(func_node, 'lineno') else None
                return self._create_violation_with_snippet(
                                        violation_message=f'Function "{func_node.name}" has vague parameter name "{arg.arg}" - use descriptive name',
                    file_path=file_path,
                    line_number=line_number,
                    severity='warning',
                    content=content,
                    ast_node=func_node,
                    max_lines=5
                )
        
        return None
    
    def _function_name_provides_context(self, func_name: str, param_name: str) -> bool:
        func_name_lower = func_name.lower()
        param_name_lower = param_name.lower()
        
        if param_name_lower in func_name_lower:
            return True
        
        context_map = {
            'data': ['data', 'datum', 'content', 'payload'],
            'value': ['value', 'val', 'result', 'output'],
            'item': ['item', 'element', 'entry', 'record'],
            'obj': ['obj', 'object', 'instance', 'entity'],
        }
        
        if param_name_lower in context_map:
            for related_term in context_map[param_name_lower]:
                if related_term in func_name_lower:
                    return True
        
        return False

