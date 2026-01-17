
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation
from .resources.ast_elements import Classes

logger = logging.getLogger(__name__)

class DomainLanguageCodeScanner(CodeScanner):
    
    GENERATE_PATTERNS = [r'^generate_', r'^calculate_']
    
    BUILDER_VERB_SUFFIXES = (
        'Generator', 'Calculator', 'Builder', 'Processor', 
        'Handler', 'Factory', 'Creator', 'Producer', 'Compiler'
    )
    
    def __init__(self):
        super().__init__()
        self.story_graph = None
    
    def _is_builder_class_with_domain_prefix(self, class_name: Optional[str]) -> bool:
        if not class_name:
            return False
        
        for suffix in self.BUILDER_VERB_SUFFIXES:
            if class_name.endswith(suffix):
                prefix = class_name[:-len(suffix)]
                if prefix:
                    return True
        return False
    
    def scan(self, story_graph: Dict[str, Any], rule_obj: Any = None, test_files: Optional[List['Path']] = None, code_files: Optional[List['Path']] = None, on_file_scanned: Optional[Any] = None) -> List[Dict[str, Any]]:
        self.story_graph = story_graph
        return super().scan(story_graph, rule_obj, test_files=test_files, code_files=code_files, on_file_scanned=on_file_scanned)
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        domain_terms = set()
        if self.story_graph:
            domain_terms = self._extract_domain_terms(self.story_graph)
        
        generic_names = {'self', 'result', 'value', 'data', 'item', 'obj', 'workspace', 'root', 'path', 'config'}
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        classes = Classes(tree)
        for cls in classes.get_many_classes:
            class_violations = self._check_domain_language(cls.node, file_path, rule_obj, domain_terms, generic_names)
            violations.extend(class_violations)
            
            for child in cls.node.body:
                if isinstance(child, ast.FunctionDef):
                    func_violations = self._check_function_domain_language(
                        child, file_path, rule_obj, domain_terms, generic_names,
                        enclosing_class=cls.node.name
                    )
                    violations.extend(func_violations)
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                func_violations = self._check_function_domain_language(
                    node, file_path, rule_obj, domain_terms, generic_names,
                    enclosing_class=None
                )
                violations.extend(func_violations)
        
        return violations
    
    def _check_domain_language(self, class_node: ast.ClassDef, file_path: Path, rule_obj: Any, 
                               domain_terms: set, generic_names: set) -> List[Dict[str, Any]]:
        violations = []
        class_name = class_node.name
        
        if class_name.lower() in generic_names:
            return violations
        
        if domain_terms and not self._matches_domain_term(class_name, domain_terms):
            sample_terms = sorted(list(domain_terms))[:10]
            violations.append(
                Violation(
                    rule=rule_obj,
                    violation_message=(
                        f'Class "{class_name}" doesn\'t match domain terms. '
                        f'Use domain-specific language from specification: {", ".join(sample_terms)}...'
                    ),
                    location=str(file_path),
                    line_number=class_node.lineno,
                    severity='info'
                ).to_dict()
            )
        
        return violations
    
    def _check_function_domain_language(self, func_node: ast.FunctionDef, file_path: Path, rule_obj: Any,
                                      domain_terms: set, generic_names: set, 
                                      enclosing_class: Optional[str] = None) -> List[Dict[str, Any]]:
        violations = []
        func_name_lower = func_node.name.lower()
        
        skip_generate_check = self._is_builder_class_with_domain_prefix(enclosing_class)
        
        if not skip_generate_check:
            for pattern in self.GENERATE_PATTERNS:
                if re.search(pattern, func_name_lower):
                    violations.append(
                        Violation(
                            rule=rule_obj,
                            violation_message=f'Function "{func_node.name}" uses generate/calculate. Use property instead (e.g., "recommended_trades" not "generate_recommendation").',
                            location=str(file_path),
                            line_number=func_node.lineno,
                            severity='warning'
                        ).to_dict()
                    )
        
        if domain_terms and not self._matches_domain_term(func_node.name, domain_terms):
            if func_node.name.lower() not in generic_names:
                sample_terms = sorted(list(domain_terms))[:10]
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=(
                            f'Function "{func_node.name}" doesn\'t match domain terms. '
                            f'Use domain-specific language from specification: {", ".join(sample_terms)}...'
                        ),
                        location=str(file_path),
                        line_number=func_node.lineno,
                        severity='info'
                    ).to_dict()
                )
        
        for arg in func_node.args.args:
            arg_name_lower = arg.arg.lower()
            if arg_name_lower in generic_names:
                continue
            
            if domain_terms and not self._matches_domain_term(arg.arg, domain_terms):
                sample_terms = sorted(list(domain_terms))[:10]
                violations.append(
                    Violation(
                        rule=rule_obj,
                        violation_message=(
                            f'Function "{func_node.name}" uses parameter name "{arg.arg}" that doesn\'t match domain terms. '
                            f'Use domain-specific language: {", ".join(sample_terms)}...'
                        ),
                        location=str(file_path),
                        line_number=func_node.lineno,
                        severity='info'
                    ).to_dict()
                )
        
        return violations

