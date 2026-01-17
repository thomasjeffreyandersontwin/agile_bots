
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import logging
from test_scanner import TestScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class ArrangeActAssertScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if function.node.name.startswith('test_'):
                violation = self._check_aaa_structure(function.node, content, file_path, rule_obj)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_aaa_structure(self, test_node: ast.FunctionDef, content: str, file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        violations = []
        
        sections = self._detect_aaa_sections_ast(test_node, content)
        
        has_actual_code = self._has_actual_code(test_node)
        
        structure_violation = self._validate_aaa_structure(sections, test_node, file_path, rule_obj)
        if structure_violation:
            violations.append(structure_violation)
        
        order_violation = self._validate_aaa_order(sections, test_node, file_path, rule_obj)
        if order_violation:
            violations.append(order_violation)
        
        if not has_actual_code:
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            try:
                violations.append(self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Test "{test_node.name}" has AAA structure but no actual code - tests must call production code, not just contain comments and pass statements',
                    file_path=file_path,
                    line_number=line_number,
                    severity='error',
                    content=content,
                    ast_node=test_node,
                    max_lines=10
                ))
            except Exception:
                violations.append(Violation(
                    rule=rule_obj,
                    violation_message=f'Test "{test_node.name}" has AAA structure but no actual code - tests must call production code, not just contain comments and pass statements',
                    location=str(file_path),
                    line_number=line_number,
                    severity='error'
                ).to_dict())
        
        return violations[0] if violations else None
    
    def _detect_aaa_sections_ast(self, test_node: ast.FunctionDef, content: str) -> Dict[str, List[ast.stmt]]:
        sections = {'arrange': [], 'act': [], 'assert': []}
        test_lines = content.split('\n')
        
        current_section = None
        
        for i, stmt in enumerate(test_node.body):
            if isinstance(stmt, (ast.Pass, ast.Expr)):
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                    continue
            
            if hasattr(stmt, 'lineno'):
                line_num = stmt.lineno - 1
                if line_num < len(test_lines):
                    line = test_lines[line_num].strip()
                    if '# Given' in line or '# Arrange' in line:
                        current_section = 'arrange'
                    elif '# When' in line or '# Act' in line:
                        current_section = 'act'
                    elif '# Then' in line or '# Assert' in line:
                        current_section = 'assert'
            
            if current_section:
                sections[current_section].append(stmt)
            else:
                section = self._classify_statement(stmt)
                if section:
                    sections[section].append(stmt)
        
        return sections
    
    def _classify_statement(self, stmt: ast.stmt) -> Optional[str]:
        if isinstance(stmt, ast.Assert):
            return 'assert'
        
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name and ('assert' in func_name.lower() or 'verify' in func_name.lower()):
                    return 'assert'
        
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name:
                    if func_name.startswith('given_'):
                        return 'arrange'
                    elif func_name.startswith('when_'):
                        return 'act'
                    elif func_name.startswith('then_'):
                        return 'assert'
        
        if isinstance(stmt, ast.Assign):
            return 'arrange'
        
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            return 'act'
        
        return None
    
    def _get_call_name(self, call_node: ast.Call) -> Optional[str]:
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None
    
    def _validate_aaa_structure(self, sections: Dict[str, List[ast.stmt]], test_node: ast.FunctionDef, 
                                file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        has_arrange = len(sections['arrange']) > 0
        has_act = len(sections['act']) > 0
        has_assert = len(sections['assert']) > 0
        
        test_lines = file_path.read_text(encoding='utf-8').split('\n')
        start_line = test_node.lineno - 1
        end_line = test_node.end_lineno if hasattr(test_node, 'end_lineno') else start_line + 50
        test_body_lines = test_lines[start_line:end_line]
        
        has_given_comment = any('# Given' in line or '# Arrange' in line for line in test_body_lines)
        has_when_comment = any('# When' in line or '# Act' in line for line in test_body_lines)
        has_then_comment = any('# Then' in line or '# Assert' in line for line in test_body_lines)
        
        has_given_method = False
        has_when_method = False
        has_then_method = False
        
        for node in ast.walk(test_node):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name:
                    if func_name.startswith('given_'):
                        has_given_method = True
                    elif func_name.startswith('when_'):
                        has_when_method = True
                    elif func_name.startswith('then_'):
                        has_then_method = True
        
        has_given = has_arrange or has_given_comment or has_given_method
        has_when = has_act or has_when_comment or has_when_method
        has_then = has_assert or has_then_comment or has_then_method
        
        if not (has_given and has_when and has_then):
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            try:
                content = file_path.read_text(encoding='utf-8')
                return self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Test "{test_node.name}" does not follow Arrange-Act-Assert structure - add # Given/When/Then comments or use given_*/when_*/then_* method names',
                    file_path=file_path,
                    line_number=line_number,
                    severity='error',
                    content=content,
                    ast_node=test_node,
                    max_lines=10
                )
            except Exception:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test "{test_node.name}" does not follow Arrange-Act-Assert structure - add # Given/When/Then comments or use given_*/when_*/then_* method names',
                    location=str(file_path),
                    line_number=line_number,
                    severity='error'
                ).to_dict()
        
        return None
    
    def _validate_aaa_order(self, sections: Dict[str, List[ast.stmt]], test_node: ast.FunctionDef,
                           file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        arrange_lines = [stmt.lineno for stmt in sections['arrange'] if hasattr(stmt, 'lineno')]
        act_lines = [stmt.lineno for stmt in sections['act'] if hasattr(stmt, 'lineno')]
        assert_lines = [stmt.lineno for stmt in sections['assert'] if hasattr(stmt, 'lineno')]
        
        if not arrange_lines or not act_lines or not assert_lines:
            return None
        
        max_arrange = max(arrange_lines) if arrange_lines else 0
        min_act = min(act_lines) if act_lines else float('inf')
        max_act = max(act_lines) if act_lines else 0
        min_assert = min(assert_lines) if assert_lines else float('inf')
        
        if max_arrange > min_act:
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            try:
                content = file_path.read_text(encoding='utf-8')
                return self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Test "{test_node.name}" has Arrange section mixed with Act section - Arrange should come before Act',
                    file_path=file_path,
                    line_number=line_number,
                    severity='warning',
                    content=content,
                    ast_node=test_node,
                    max_lines=10
                )
            except Exception:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test "{test_node.name}" has Arrange section mixed with Act section - Arrange should come before Act',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        if max_act > min_assert:
            line_number = test_node.lineno if hasattr(test_node, 'lineno') else None
            try:
                content = file_path.read_text(encoding='utf-8')
                return self._create_violation_with_snippet(
                    rule_obj=rule_obj,
                    violation_message=f'Test "{test_node.name}" has Act section mixed with Assert section - Act should come before Assert',
                    file_path=file_path,
                    line_number=line_number,
                    severity='warning',
                    content=content,
                    ast_node=test_node,
                    max_lines=10
                )
            except Exception:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test "{test_node.name}" has Act section mixed with Assert section - Act should come before Assert',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        return None
    
    def _has_actual_code(self, test_node: ast.FunctionDef) -> bool:
        if not test_node.body:
            return False
        
        for stmt in test_node.body:
            if isinstance(stmt, ast.Pass):
                continue
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
                continue
            else:
                for node in ast.walk(stmt):
                    if isinstance(node, (ast.Call, ast.Assign, ast.Assert, ast.Return, ast.Raise)):
                        return True
        
        return False

