
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from scanners.code_scanner import CodeScanner
from scanners.violation import Violation

logger = logging.getLogger(__name__)

class MeaningfulContextScanner(CodeScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_magic_numbers(lines, file_path, rule_obj))
        
        violations.extend(self._check_numbered_variables(content, file_path, rule_obj))
        
        return violations
    
    def _check_magic_numbers(self, lines: List[str], file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
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
                        rule_obj=rule_obj,
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
    
    def _check_numbered_variables(self, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        try:
            tree = ast.parse(content, filename=str(file_path))
            
            numbered_var_pattern = re.compile(r'^\w+\d+$')
            
            # Meaningful patterns that should NOT be flagged as violations
            meaningful_patterns = [
                # Indexing schemes (0-indexed, 1-indexed)
                re.compile(r'^.+_(0|1)$'),  # e.g., start_line_0, end_line_1
                # ANY variable ending in 1 or 2 (comparison/pairing pattern)
                # This is a common idiom for comparing two similar things
                re.compile(r'^[a-z_]+[12]$'),  # e.g., func1, func2, preview1, preview2
                # Compound comparison variables (with underscores)
                re.compile(r'^[a-z_]+[12]_[a-z_]+$'),  # e.g., func1_lower, block1_nodes
                # Coordinate/dimension names
                re.compile(r'^[xy]\d+$'),  # e.g., x1, y2
                # Version numbers
                re.compile(r'^(version|v)\d+$'),
            ]
            
            def check_name(var_name: str, lineno: int):
                if not numbered_var_pattern.match(var_name):
                    return
                
                # Skip test-related variables
                if var_name.startswith('test') or var_name in ['test1', 'test2']:
                    return
                
                # Skip meaningful patterns
                for pattern in meaningful_patterns:
                    if pattern.match(var_name):
                        return
                
                # Skip very short numbered variables (likely loop counters)
                if len(var_name) <= 2:  # e.g., i1, j2, n1, n2
                    return
                
                violations.append(self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Line {lineno} uses numbered variable "{var_name}" - use meaningful descriptive name',
                    file_path=file_path,
                    line_number=lineno,
                    severity='warning',
                    content=content,
                    start_line=lineno,
                    end_line=lineno,
                    context_before=1,
                    max_lines=3
                ))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            check_name(target.id, target.lineno)
                        elif isinstance(target, ast.Tuple):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    check_name(elt.id, elt.lineno)
                        elif isinstance(target, ast.Attribute):
                            if isinstance(target.attr, str) and numbered_var_pattern.match(target.attr):
                                check_name(target.attr, target.lineno)
                
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for arg in node.args.args:
                        check_name(arg.arg, arg.lineno)
                    for arg in node.args.kwonlyargs:
                        check_name(arg.arg, arg.lineno)
                
                elif isinstance(node, (ast.For, ast.AsyncFor)):
                    if isinstance(node.target, ast.Name):
                        check_name(node.target.id, node.target.lineno)
                    elif isinstance(node.target, ast.Tuple):
                        for elt in node.target.elts:
                            if isinstance(elt, ast.Name):
                                check_name(elt.id, elt.lineno)
                
                elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                    for generator in node.generators:
                        if isinstance(generator.target, ast.Name):
                            check_name(generator.target.id, generator.target.lineno)
                        elif isinstance(generator.target, ast.Tuple):
                            for elt in generator.target.elts:
                                if isinstance(elt, ast.Name):
                                    check_name(elt.id, elt.lineno)
                
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    check_name(target.id, target.lineno)
                                elif isinstance(target, ast.Attribute):
                                    if isinstance(target.attr, str) and numbered_var_pattern.match(target.attr):
                                        check_name(target.attr, target.lineno)
        
        except (SyntaxError, ValueError) as e:
            logger.debug(f'AST parsing failed for {file_path}, skipping numbered variable check: {type(e).__name__}: {e}')
        
        return violations
