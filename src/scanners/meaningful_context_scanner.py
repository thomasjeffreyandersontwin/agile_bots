
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from scanners.violation import Violation

logger = logging.getLogger(__name__)

class MeaningfulContextScanner(CodeScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_magic_numbers(lines, file_path))
        
        violations.extend(self._check_numbered_variables(content, file_path))
        
        return violations
    
    def _check_magic_numbers(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        content = '\n'.join(lines)
        
        magic_number_patterns = [
            r'\b(200|404|500)\b',  # HTTP status codes
            r'\b(86400|3600)\b',  # Time constants (seconds in day/hour)
        ]
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Skip lines that are defining the patterns themselves (scanner definitions)
            if 'magic_number_patterns' in stripped or r'\b(' in stripped:
                continue
            
            # Skip lines that are defining named constants (already have meaningful names)
            if '=' in stripped and re.match(r'^\s*[A-Z_][A-Z0-9_]*\s*=', stripped):
                continue
            
            # Skip string multiplication for display purposes (e.g., "─" * 60)
            if re.search(r'["\'].*["\']\s*\*\s*\d+', stripped):
                continue
            
            for pattern in magic_number_patterns:
                match = re.search(pattern, stripped)
                if match:
                    # Skip if number is in a comment
                    if '#' in stripped:
                        comment_pos = stripped.index('#')
                        number_pos = match.start()
                        if comment_pos < number_pos:
                            continue
                    
                    violation = self._create_violation_with_snippet(
                                                violation_message=f'Line {line_num} contains magic number - replace with named constant',
                        file_path=file_path,
                        line_number=line_num,
                        severity='warning',
                        content=content,
                        start_line=line_num,
                        end_line=line_num,
                        context_before=1,
                        max_lines=3
                    )
                    violations.append(violation)
                    break
        
        return violations
    
    def _check_numbered_variables(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        try:
            tree = ast.parse(content, filename=str(file_path))
        except (SyntaxError, ValueError) as e:
            logger.debug(f'AST parsing failed for {file_path}, skipping numbered variable check: {type(e).__name__}: {e}')
            return []
        
        checker = NumberedVariableChecker(content, file_path, self.rule, self._create_violation_with_snippet)
        
        for node in ast.walk(tree):
            checker.check_node(node)
        
        return checker.violations


class NumberedVariableChecker:
    
    NUMBERED_VAR_PATTERN = re.compile(r'^\w+\d+$')
    MEANINGFUL_PATTERNS = [
        re.compile(r'^.+_(0|1)$'),
        re.compile(r'^[a-z_]+[12]$'),
        re.compile(r'^[a-z_]+[12]_[a-z_]+$'),
        re.compile(r'^[xy]\d+$'),
        re.compile(r'^(version|v)\d+$'),
    ]
    
    def __init__(self, content: str, file_path: Path, create_violation_fn):
        self.content = content
        self.file_path = file_path
        self.self.rule = self.rule
        self.create_violation_fn = create_violation_fn
        self.violations = []
    
    def check_node(self, node: ast.AST) -> None:
        if isinstance(node, ast.Assign):
            self._check_assign_targets(node.targets)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self._check_function_args(node)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            self._check_loop_target(node.target)
        elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            self._check_comprehension_targets(node.generators)
        elif isinstance(node, ast.ClassDef):
            self._check_class_assigns(node.body)
    
    def _check_assign_targets(self, targets: list) -> None:
        for target in targets:
            self._check_target(target)
    
    def _check_target(self, target: ast.AST) -> None:
        if isinstance(target, ast.Name):
            self._check_name(target.id, target.lineno)
        elif isinstance(target, ast.Tuple):
            for elt in target.elts:
                if isinstance(elt, ast.Name):
                    self._check_name(elt.id, elt.lineno)
        elif isinstance(target, ast.Attribute):
            if isinstance(target.attr, str) and self.NUMBERED_VAR_PATTERN.match(target.attr):
                self._check_name(target.attr, target.lineno)
    
    def _check_function_args(self, node) -> None:
        for arg in node.args.args:
            self._check_name(arg.arg, arg.lineno)
        for arg in node.args.kwonlyargs:
            self._check_name(arg.arg, arg.lineno)
    
    def _check_loop_target(self, target: ast.AST) -> None:
        self._check_target(target)
    
    def _check_comprehension_targets(self, generators: list) -> None:
        for generator in generators:
            self._check_target(generator.target)
    
    def _check_class_assigns(self, body: list) -> None:
        for item in body:
            if isinstance(item, ast.Assign):
                self._check_assign_targets(item.targets)
    
    def _check_name(self, var_name: str, lineno: int) -> None:
        if not self._is_violation(var_name):
            return
        
        self.violations.append(self.create_violation_fn(
            self.rule=self.self.rule,
            violation_message=f'Line {lineno} uses numbered variable "{var_name}" - use meaningful descriptive name',
            file_path=self.file_path,
            line_number=lineno,
            severity='warning',
            content=self.content,
            start_line=lineno,
            end_line=lineno,
            context_before=1,
            max_lines=3
        ))
    
    def _is_violation(self, var_name: str) -> bool:
        if not self.NUMBERED_VAR_PATTERN.match(var_name):
            return False
        if var_name.startswith('test') or var_name in ['test1', 'test2']:
            return False
        if len(var_name) <= 2:
            return False
        for pattern in self.MEANINGFUL_PATTERNS:
            if pattern.match(var_name):
                return False
        return True
