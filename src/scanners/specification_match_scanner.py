
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
import logging
from test_scanner import TestScanner
from scanners.violation import Violation
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class SpecificationMatchScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        violations.extend(self._check_test_method_names(tree, file_path, rule_obj))
        
        violations.extend(self._check_variable_names(tree, content, file_path, rule_obj))
        
        violations.extend(self._check_assertions(tree, content, file_path, rule_obj))
        
        if story_graph:
            violations.extend(self._check_specification_matches(tree, content, file_path, rule_obj, story_graph))
        
        return violations
    
    def _check_test_method_names(self, tree: ast.AST, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        vague_patterns = [
            r'^test_(init|setup|create|new|get|set|run|execute|do|handle|process|check|verify|test)$',
            r'^test_\w+_(init|setup|create|new|get|set|run|execute|do|handle|process|check|verify)$',
        ]
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            if function.node.name.startswith('test_'):
                is_vague = False
                for pattern in vague_patterns:
                    if re.match(pattern, function.node.name, re.IGNORECASE):
                        is_vague = True
                        break
                
                is_thin_wrapper = self._is_thin_wrapper(function.node)
                
                if is_vague and not is_thin_wrapper:
                    violations.append(self._create_violation_with_line_number(
                        rule_obj, file_path, function.node,
                        f'Test method "{function.node.name}" has vague name - should clearly describe behavior from specification scenario'
                    ))
        
        return violations
    
    def _is_thin_wrapper(self, test_node: ast.FunctionDef) -> bool:
        if len(test_node.body) == 1:
            stmt = test_node.body[0]
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                return True
            if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):
                return True
        return False
    
    def _create_violation_with_line_number(
        self,
        rule_obj: Any,
        file_path: Path,
        node: ast.AST,
        message: str,
        severity: str = 'warning'
    ) -> Dict[str, Any]:
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            content = None
        
        line_number = node.lineno if hasattr(node, 'lineno') else None
        
        violation_dict = Violation(
            rule=rule_obj,
            violation_message=message,
            location=str(file_path),
            line_number=line_number,
            severity=severity
        ).to_dict()
        
        if content and line_number:
            lines = content.split('\n')
            start_line = max(0, line_number - 2)
            end_line = min(len(lines), line_number + 3)
            snippet_lines = lines[start_line:end_line]
            violation_dict['snippet'] = '\n'.join(snippet_lines)
        
        return violation_dict
    
    def _check_variable_names(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        generic_names = ['data', 'result', 'value', 'item', 'obj', 'thing', 'name', 'root', 'path', 'config']
        
        test_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_methods.append(node)
        
        for test_method in test_methods:
            for child in ast.walk(test_method):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            if var_name.lower() in generic_names:
                                if not self._is_in_helper_call(child, test_method):
                                    violations.append(self._create_violation_with_line_number(
                                        rule_obj, file_path, child,
                                        f'Line {child.lineno if hasattr(child, "lineno") else "?"} uses generic variable name "{var_name}" - use exact variable names from specification'
                                    ))
        
        return violations
    
    def _is_in_helper_call(self, assign_node: ast.Assign, test_method: ast.FunctionDef) -> bool:
        if isinstance(assign_node.value, ast.Call):
            func = assign_node.value.func
            if isinstance(func, ast.Name):
                func_name = func.id
                if func_name.startswith(('verify_', 'given_', 'when_', 'then_', 'create_', 'setup_')):
                    return True
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
                if func_name.startswith(('verify_', 'given_', 'when_', 'then_', 'create_', 'setup_')):
                    return True
        return False
    
    def _check_assertions(self, tree: ast.AST, content: str, file_path: Path, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        implementation_patterns = [
            r'\._(private|internal|_flag|_state|_cache)',
            r'\.called\b',
            r'\.assert_called',
            r'\._validate',
        ]
        
        test_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_methods.append(node)
        
        for test_method in test_methods:
            for child in ast.walk(test_method):
                if isinstance(child, ast.Assert):
                    assertion_line = self._get_assertion_line(child, content, child.lineno)
                    
                    for pattern in implementation_patterns:
                        if re.search(pattern, assertion_line, re.IGNORECASE):
                            violations.append(self._create_violation_with_line_number(
                                rule_obj, file_path, child,
                                f'Line {child.lineno if hasattr(child, "lineno") else "?"} assertion checks implementation detail - verify exactly what specification states, no more, no less'
                            ))
                            break
        
        return violations
    
    def _get_assertion_line(self, assert_node: ast.Assert, content: str, line_num: int) -> str:
        lines = content.split('\n')
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""
    
    def _check_specification_matches(self, tree: ast.AST, content: str, file_path: Path, 
                                    rule_obj: Any, story_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        
        test_methods = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_methods.append(node)
        
        domain_terms = self._extract_domain_terms(story_graph)
        
        for test_method in test_methods:
            scenario = self._extract_scenario_from_docstring(test_method)
            
            matching_story = self._find_matching_story(scenario, test_method.name, story_graph)
            
            if matching_story:
                variable_matches = self._check_variable_matches(test_method, matching_story, domain_terms, rule_obj, file_path)
                violations.extend(variable_matches)
                
                assertion_matches = self._check_assertion_matches(test_method, matching_story, rule_obj, file_path)
                violations.extend(assertion_matches)
            elif scenario:
                violations.append(self._create_violation_with_line_number(
                    rule_obj, file_path, test_method,
                    f'Test "{test_method.name}" has scenario but no matching story found in specification. '
                    f'Scenario: {scenario[:100]}...'
                ))
        
        return violations
    
    def _extract_domain_terms(self, story_graph: Dict[str, Any]) -> set:
        domain_terms = set()
        
        if not story_graph:
            return domain_terms
        
        epics = story_graph.get('epics', [])
        for epic in epics:
            if isinstance(epic, dict):
                epic_name = epic.get('name', '')
                if epic_name:
                    domain_terms.update(self._extract_words_from_text(epic_name))
                
                domain_concepts = epic.get('domain_concepts', [])
                for concept in domain_concepts:
                    if isinstance(concept, dict):
                        concept_name = concept.get('name', '')
                        if concept_name:
                            domain_terms.add(concept_name.lower())
                            domain_terms.add(concept_name.lower().replace(' ', '_'))
                            domain_terms.update(self._extract_words_from_text(concept_name))
                            
                            responsibilities = concept.get('responsibilities', [])
                            for resp in responsibilities:
                                if isinstance(resp, dict):
                                    resp_name = resp.get('name', '')
                                    if resp_name:
                                        domain_terms.update(self._extract_words_from_text(resp_name))
                            
                            collaborators = concept.get('collaborators', [])
                            for collab in collaborators:
                                if isinstance(collab, str):
                                    domain_terms.add(collab.lower())
                                    domain_terms.update(self._extract_words_from_text(collab))
                
                sub_epics = epic.get('sub_epics', [])
                for sub_epic in sub_epics:
                    if isinstance(sub_epic, dict):
                        sub_epic_name = sub_epic.get('name', '')
                        if sub_epic_name:
                            domain_terms.update(self._extract_words_from_text(sub_epic_name))
                        
                        sub_epic_concepts = sub_epic.get('domain_concepts', [])
                        for concept in sub_epic_concepts:
                            if isinstance(concept, dict):
                                concept_name = concept.get('name', '')
                                if concept_name:
                                    domain_terms.add(concept_name.lower())
                                    domain_terms.add(concept_name.lower().replace(' ', '_'))
                                    domain_terms.update(self._extract_words_from_text(concept_name))
                                    
                                    responsibilities = concept.get('responsibilities', [])
                                    for resp in responsibilities:
                                        if isinstance(resp, dict):
                                            resp_name = resp.get('name', '')
                                            if resp_name:
                                                domain_terms.update(self._extract_words_from_text(resp_name))
                                    
                                    collaborators = concept.get('collaborators', [])
                                    for collab in collaborators:
                                        if isinstance(collab, str):
                                            domain_terms.add(collab.lower())
                                            domain_terms.update(self._extract_words_from_text(collab))
                        
                        story_groups = sub_epic.get('story_groups', [])
                        for story_group in story_groups:
                            if isinstance(story_group, dict):
                                stories = story_group.get('stories', [])
                                for story in stories:
                                    if isinstance(story, dict):
                                        story_name = story.get('name', '')
                                        if story_name:
                                            domain_terms.update(self._extract_words_from_text(story_name))
                                        
                                        acceptance_criteria = story.get('acceptance_criteria', [])
                                        for ac in acceptance_criteria:
                                            if isinstance(ac, dict):
                                                ac_text = ac.get('criterion', '')
                                                if ac_text:
                                                    domain_terms.update(self._extract_words_from_text(ac_text))
                                            elif isinstance(ac, str):
                                                domain_terms.update(self._extract_words_from_text(ac))
                                        
                                        scenarios = story.get('scenarios', [])
                                        for scenario in scenarios:
                                            if isinstance(scenario, dict):
                                                steps = scenario.get('steps', [])
                                                for step in steps:
                                                    if isinstance(step, str):
                                                        domain_terms.update(self._extract_words_from_text(step))
        
        return domain_terms
    
    def _extract_words_from_text(self, text: str) -> set:
        import re
        if not text:
            return set()
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)
    
    def _extract_scenario_from_docstring(self, test_method: ast.FunctionDef) -> Optional[str]:
        if not test_method.body:
            return None
        
        first_stmt = test_method.body[0]
        if isinstance(first_stmt, ast.Expr):
            if isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
                return first_stmt.value.value
            elif hasattr(ast, 'Str') and isinstance(first_stmt.value, ast.Str):
                return first_stmt.value.s
        
        return None
    
    def _find_matching_story(self, scenario: Optional[str], test_name: str, story_graph: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not story_graph:
            return None
        
        scenario_name = None
        if scenario:
            scenario_match = re.search(r'SCENARIO:\s*(.+?)(?:\n|$)', scenario, re.IGNORECASE)
            if scenario_match:
                scenario_name = scenario_match.group(1).strip()
        
        test_keywords = set(self._extract_words_from_text(test_name))
        
        epics = story_graph.get('epics', [])
        for epic in epics:
            if isinstance(epic, dict):
                sub_epics = epic.get('sub_epics', [])
                for sub_epic in sub_epics:
                    if isinstance(sub_epic, dict):
                        story_groups = sub_epic.get('story_groups', [])
                        for story_group in story_groups:
                            if isinstance(story_group, dict):
                                stories = story_group.get('stories', [])
                                for story in stories:
                                    if isinstance(story, dict):
                                        if scenario_name:
                                            story_scenarios = story.get('scenarios', [])
                                            for story_scenario in story_scenarios:
                                                if isinstance(story_scenario, dict):
                                                    story_scenario_name = story_scenario.get('name', '')
                                                    normalized_test_scenario = re.sub(r'\s+', ' ', scenario_name.lower().strip())
                                                    normalized_story_scenario = re.sub(r'\s+', ' ', story_scenario_name.lower().strip())
                                                    if normalized_test_scenario == normalized_story_scenario:
                                                        return story
        
        return None
    
    def _check_variable_matches(self, test_method: ast.FunctionDef, story: Dict[str, Any], 
                                domain_terms: set, rule_obj: Any, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        variable_names = []
        for node in ast.walk(test_method):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        variable_names.append((target.id, node.lineno if hasattr(node, 'lineno') else None))
        
        for var_name, line_number in variable_names:
            var_name_lower = var_name.lower()
            
            generic_names = {'self', 'result', 'value', 'data', 'item', 'obj', 'workspace', 'root', 'path', 'config'}
            if var_name_lower in generic_names:
                continue
            
            var_words = set(self._extract_words_from_text(var_name))
            
            matches_domain_term = False
            for domain_term in domain_terms:
                if domain_term in var_words:
                    matches_domain_term = True
                    break
                if domain_term in var_name_lower or var_name_lower in domain_term:
                    matches_domain_term = True
                    break
            
            if not matches_domain_term:
                sample_terms = sorted(list(domain_terms))[:10]
                violations.append(self._create_violation_with_line_number(
                    rule_obj, file_path, test_method,
                    f'Variable "{var_name}" in test "{test_method.name}" doesn\'t match domain terms. '
                    f'Use terms from specification: {", ".join(sample_terms)}...',
                    'info'
                ))
        
        return violations
    
    def _check_assertion_matches(self, test_method: ast.FunctionDef, story: Dict[str, Any], 
                                 rule_obj: Any, file_path: Path) -> List[Dict[str, Any]]:
        violations = []
        
        acceptance_criteria = story.get('acceptance_criteria', [])
        if not acceptance_criteria:
            return violations
        
        assertions = []
        has_pytest_raises = False
        has_helper_assertions = False
        
        for node in ast.walk(test_method):
            if isinstance(node, ast.Assert):
                assertions.append(node)
            
            if isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        func = item.context_expr.func
                        if isinstance(func, ast.Attribute):
                            if func.attr == 'raises':
                                if isinstance(func.value, ast.Name) and func.value.id == 'pytest':
                                    has_pytest_raises = True
                        elif isinstance(func, ast.Name):
                            if func.id == 'raises':
                                has_pytest_raises = True
            
            if isinstance(node, ast.Call):
                func = node.func
                func_name = None
                if isinstance(func, ast.Name):
                    func_name = func.id
                elif isinstance(func, ast.Attribute):
                    func_name = func.attr
                
                if func_name:
                    if func_name.startswith(('then_', 'verify_', 'check_', 'assert_')):
                        has_helper_assertions = True
        
        total_assertions = len(assertions)
        if has_pytest_raises:
            total_assertions += 1
        if has_helper_assertions:
            total_assertions += 1
        
        if total_assertions == 0 and len(acceptance_criteria) > 0:
            violations.append(self._create_violation_with_line_number(
                rule_obj, file_path, test_method,
                f'Test "{test_method.name}" has no assertions but story has {len(acceptance_criteria)} acceptance criteria. '
                f'Add assertions to verify acceptance criteria.'
            ))
        
        return violations
    
    def scan_story_node(self, node: Any, rule_obj: Any) -> List[Dict[str, Any]]:
        return []

