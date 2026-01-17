"""Scanner for validating objects are preferred over primitives in method signatures."""

from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class PrimitiveVsObjectScanner(CodeScanner):
    
    # Primitive type names that suggest objects should be used instead
    PRIMITIVE_TYPES = {'str', 'int', 'float', 'bool', 'dict', 'Dict', 'list', 'List', 'tuple', 'Tuple'}
    
    # Presentation boundary method name patterns (primitives OK here)
    PRESENTATION_METHOD_PATTERNS = [
        r'render', r'format', r'to_string', r'to_dict', r'to_json', r'to_xml',
        r'display', r'print', r'show', r'cli', r'ui', r'html', r'json',
        r'str\(', r'__str__', r'__repr__', r'serialize', r'marshal'
    ]
    
    OBJECT_SUGGESTING_PATTERNS = [
        r'_id$',
        r'_ids$',
        r'_name$',
        r'_email$',
    ]
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            func_violations = self._check_function_parameters(function.node, content, file_path, rule_obj)
            violations.extend(func_violations)
            
            return_violation = self._check_return_type(function.node, content, file_path, rule_obj)
            if return_violation:
                violations.append(return_violation)
        
        return violations
    
    def _is_presentation_boundary(self, func_name: str, content: str, func_node: ast.FunctionDef) -> bool:
        func_name_lower = func_name.lower()
        
        for pattern in self.PRESENTATION_METHOD_PATTERNS:
            if re.search(pattern, func_name_lower):
                return True
        
        func_source = ast.get_source_segment(content, func_node) or ''
        presentation_keywords = ['print(', 'display', 'render', 'format', 'to_string', 'to_dict', 'cli', 'ui']
        if any(keyword in func_source.lower() for keyword in presentation_keywords):
            return True
        
        return False
    
    def _check_function_parameters(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if self._is_presentation_boundary(func_node.name, content, func_node):
            return violations
        
        # Skip __init__ methods - they often need primitives for construction
        if func_node.name == '__init__':
            return violations
        
        for arg in func_node.args.args:
            if arg.arg in ('self', 'cls'):
                continue
            
            if arg.annotation:
                type_name = self._extract_type_name(arg.annotation, content)
                
                if type_name and type_name in self.PRIMITIVE_TYPES:
                    if self._suggests_object_should_be_passed(arg.arg):
                        violations.append(self._create_primitive_violation(
                            rule_obj, file_path, func_node, arg, type_name,
                            f'Function "{func_node.name}" takes primitive "{arg.arg}: {type_name}" - consider passing domain object instead'
                        ))
            
            elif self._suggests_object_should_be_passed(arg.arg):
                violations.append(self._create_primitive_violation(
                    rule_obj, file_path, func_node, arg, None,
                    f'Function "{func_node.name}" takes "{arg.arg}" which suggests a primitive ID - consider passing domain object instead'
                ))
        
        return violations
    
    def _check_return_type(self, func_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        if self._is_presentation_boundary(func_node.name, content, func_node):
            return None
        
        if func_node.returns:
            return_type_name = self._extract_type_name(func_node.returns, content)
            
            if return_type_name in ('Dict', 'dict', 'List', 'list', 'tuple', 'Tuple'):
                func_name_lower = func_node.name.lower()
                object_return_patterns = ['create', 'build', 'make', 'get', 'find', 'load', 'process', 'generate']
                
                if any(pattern in func_name_lower for pattern in object_return_patterns):
                    return self._create_primitive_violation(
                        rule_obj, file_path, func_node, None, return_type_name,
                        f'Function "{func_node.name}" returns "{return_type_name}" - consider returning domain object instead'
                    )
        
        return None
    
    def _extract_type_name(self, annotation_node: ast.AST, content: str) -> Optional[str]:
        if isinstance(annotation_node, ast.Name):
            return annotation_node.id
        elif isinstance(annotation_node, ast.Subscript):
            if isinstance(annotation_node.value, ast.Name):
                return annotation_node.value.id
        elif isinstance(annotation_node, ast.Attribute):
            return annotation_node.attr
        
        return None
    
    def _suggests_object_should_be_passed(self, param_name: str) -> bool:
        param_name_lower = param_name.lower()
        
        for pattern in self.OBJECT_SUGGESTING_PATTERNS:
            if re.search(pattern, param_name_lower):
                return True
        
        return False
    
    def _create_primitive_violation(
        self,
        rule_obj: Any,
        file_path: Path,
        func_node: ast.FunctionDef,
        arg: Optional[ast.arg],
        type_name: Optional[str],
        message: str
    ) -> Dict[str, Any]:
        line_number = func_node.lineno if func_node else None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            return self._create_violation_with_snippet(
                rule_obj=rule_obj,
                violation_message=message,
                file_path=file_path,
                line_number=line_number,
                severity='warning',
                content=content,
                ast_node=func_node,
                max_lines=5
            )
        except Exception:
            return Violation(
                rule=rule_obj,
                violation_message=message,
                line_number=line_number,
                location=str(file_path),
                severity='warning'
            ).to_dict()

