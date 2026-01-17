
from typing import List, Dict, Any, Optional, Set, TYPE_CHECKING
from pathlib import Path
import ast
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation
from .resources.ast_elements import Classes

logger = logging.getLogger(__name__)

class DependencyChainingCodeScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_violations = self._check_dependency_chaining(cls.node, file_path)
            violations.extend(class_violations)
        
        return violations
    
    def _check_dependency_chaining(self, class_node: ast.ClassDef, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        init_method = None
        init_params = []
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                init_method = node
                init_params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                break
        
        instance_attrs = self._collect_instance_attributes(class_node)
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef) and node.name != '__init__':
                is_classmethod = any(
                    (isinstance(decorator, ast.Name) and decorator.id == 'classmethod') or
                    (isinstance(decorator, ast.Attribute) and decorator.attr == 'classmethod')
                    for decorator in node.decorator_list
                )
                is_staticmethod = any(
                    (isinstance(decorator, ast.Name) and decorator.id == 'staticmethod') or
                    (isinstance(decorator, ast.Attribute) and decorator.attr == 'staticmethod')
                    for decorator in node.decorator_list
                )
                is_property_setter = any(
                    (isinstance(decorator, ast.Attribute) and decorator.attr == 'setter')
                    for decorator in node.decorator_list
                )
                
                # Skip classmethods, staticmethods, and property setters
                # Property setters need their parameters to set new values
                if is_classmethod or is_staticmethod or is_property_setter:
                    continue
                
                method_params = [arg.arg for arg in node.args.args if arg.arg != 'self']
                
                for param in method_params:
                    if param in init_params:
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            violations.append(
                                self._create_violation_with_snippet(
                                                                        violation_message=f'Method "{node.name}" in class "{class_node.name}" takes parameter "{param}" that is already injected in __init__. Use self.{param} instead.',
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    severity='warning',
                                    content=content,
                                    ast_node=node,
                                    max_lines=5
                                )
                            )
                        except Exception:
                            violations.append(
                                Violation(
                                    rule=self.rule,
                                    violation_message=f'Method "{node.name}" in class "{class_node.name}" takes parameter "{param}" that is already injected in __init__. Use self.{param} instead.',
                                    location=str(file_path),
                                    line_number=node.lineno,
                                    severity='warning'
                                ).to_dict()
                            )
                
                if node.name.startswith('_') and not (node.name.startswith('__') and node.name.endswith('__')):
                    violations.extend(self._check_method_calls_for_instance_attrs(
                        node, class_node.name, file_path, self.rule, instance_attrs
                    ))
        
        return violations
    
    def _collect_instance_attributes(self, class_node: ast.ClassDef) -> Set[str]:
        attrs = set()
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            attrs.add(target.attr)
            
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == 'self':
                    attrs.add(node.attr)
            
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'property':
                        attrs.add(node.name)
        
        return attrs
    
    def _check_method_calls_for_instance_attrs(
        self, func_node: ast.FunctionDef, class_name: str, file_path: Path, instance_attrs: Set[str]
    ) -> List[Dict[str, Any]]:
        violations = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'self':
                        for arg in node.args:
                            violation = self._check_argument(
                                arg, node.func.attr, class_name, file_path, self.rule, instance_attrs, func_node.lineno
                            )
                            if violation:
                                violations.append(violation)
        
        return violations
    
    def _check_argument(
        self, arg_node: ast.AST, method_name: str, class_name: str, file_path: Path, instance_attrs: Set[str], line_num: int
    ) -> Optional[Dict[str, Any]]:
        if isinstance(arg_node, ast.Attribute):
            if isinstance(arg_node.value, ast.Name) and arg_node.value.id == 'self':
                attr_name = arg_node.attr
                if attr_name in instance_attrs:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        return self._create_violation_with_snippet(
                                                        violation_message=f'Passing self.{attr_name} as parameter to {method_name}(). Access it directly in the method through self.{attr_name} instead.',
                            file_path=file_path,
                            line_number=line_num,
                            severity='warning',
                            content=content,
                            start_line=line_num,
                            end_line=line_num,
                            context_before=2,
                            max_lines=5
                        )
                    except Exception:
                        return Violation(
                            rule=self.rule,
                            violation_message=f'Line {line_num}: Passing self.{attr_name} as parameter to {method_name}(). Access it directly in the method through self.{attr_name} instead.',
                            location=str(file_path),
                            line_number=line_num,
                            severity='warning'
                        ).to_dict()
        
        return None

