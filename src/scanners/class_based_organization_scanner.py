
from typing import List, Dict, Any, Optional
from pathlib import Path
import ast
import re
from test_scanner import TestScanner
from story_map import StoryNode
from scanners.violation import Violation

class ClassBasedOrganizationScanner(TestScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        return []
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        if not file_path.exists():
            return violations
        
        sub_epic_names = self._extract_sub_epic_names(story_graph)
        file_name = file_path.stem
        violation = self._check_file_name_matches_sub_epic(file_name, sub_epic_names, file_path, rule_obj, story_graph)
        if violation:
            violations.append(violation)
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        story_names = self._extract_story_names(story_graph)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name.startswith('Test'):
                    violation = self._check_class_name_matches_story(node.name, story_names, file_path, rule_obj)
                    if violation:
                        violations.append(violation)
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith('test_'):
                                violation = self._check_method_name_matches_scenario(
                                    item.name, node.name, story_names, story_graph, file_path, rule_obj
                                )
                                if violation:
                                    violations.append(violation)
        
        return violations
    
    def _extract_story_names(self, story_graph: Dict[str, Any]) -> List[str]:
        story_names = []
        epics = story_graph.get('epics', [])
        for epic in epics:
            self._extract_story_names_recursive(epic, story_names)
        return story_names
    
    def _extract_story_names_recursive(self, node: Dict[str, Any], result: List[str]) -> None:
        sub_epics = node.get('sub_epics', [])
        for sub_epic in sub_epics:
            self._extract_story_names_recursive(sub_epic, result)
        
        story_groups = node.get('story_groups', [])
        for story_group in story_groups:
            stories = story_group.get('stories', [])
            for story in stories:
                story_name = story.get('name', '')
                if story_name:
                    result.append(story_name)
    
    def _check_class_name_matches_story(self, class_name: str, story_names: List[str], file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        
        expected_story_name = self._pascal_to_story_name(story_name_from_class)
        
        matches = [s for s in story_names if self._names_match(s, expected_story_name)]
        
        if not matches:
            if self._is_abbreviated(class_name, story_names):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test class "{class_name}" appears abbreviated - should match story name exactly (Test<ExactStoryName>)',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
            
            if self._is_generic(class_name):
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test class "{class_name}" uses generic name - should match story name exactly',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
        
        return None
    
    def _check_method_name_matches_scenario(self, method_name: str, class_name: str, story_names: List[str], 
                                           story_graph: Dict[str, Any], file_path: Path, rule_obj: Any) -> Optional[Dict[str, Any]]:
        scenario_name_from_method = method_name[5:] if method_name.startswith('test_') else method_name
        
        if len(scenario_name_from_method) < 20:
            expected_name = self._find_expected_scenario_name(scenario_name_from_method, story_graph, class_name)
            
            if expected_name:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test method "{method_name}" appears abbreviated - should match scenario name exactly. Expected name based on epic/story: "{expected_name}"',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
            else:
                return Violation(
                    rule=rule_obj,
                    violation_message=f'Test method "{method_name}" appears abbreviated - should match scenario name exactly',
                    location=str(file_path),
                    severity='error'
                ).to_dict()
        
        return None
    
    def _find_expected_scenario_name(self, method_name: str, story_graph: Dict[str, Any], class_name: str) -> Optional[str]:
        full_method_name = f"test_{method_name}" if not method_name.startswith('test_') else method_name
        method_name_norm = self._normalize_name(method_name)
        
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        story_name_normalized = self._normalize_name(story_name_from_class)
        
        epics = story_graph.get('epics', [])
        
        best_match = None
        best_match_type = None
        
        for epic in epics:
            epic_name = epic.get('name', '')
            epic_name_norm = self._normalize_name(epic_name) if epic_name else ''
            
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                sub_epic_name_norm = self._normalize_name(sub_epic_name) if sub_epic_name else ''
                
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        story_name_norm = self._normalize_name(story_name) if story_name else ''
                        
                        story_matches_class = (story_name_norm == story_name_normalized or 
                                             story_name_norm.startswith(story_name_normalized) or
                                             story_name_normalized.startswith(story_name_norm))
                        
                        scenarios = story.get('scenarios', [])
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', '')
                            test_method = scenario.get('test_method', '')
                            
                            if test_method and full_method_name == test_method:
                                if epic_name:
                                    return f"{epic_name} - {scenario_name}"
                                return scenario_name
                            
                            if not scenario_name:
                                continue
                            scenario_name_norm = self._normalize_name(scenario_name)
                            
                            if (method_name_norm in scenario_name_norm or 
                                scenario_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(scenario_name_norm)):
                                if epic_name:
                                    return f"{epic_name} - {scenario_name}"
                                return scenario_name
                        
                        if story_matches_class:
                            if (method_name_norm in story_name_norm or 
                                story_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(story_name_norm)):
                                if not best_match or best_match_type in ['epic', 'sub_epic']:
                                    best_match = f"{epic_name} - {story_name}" if epic_name else story_name
                                    best_match_type = 'story'
                        
                        acceptance_criteria = story.get('acceptance_criteria', [])
                        for ac in acceptance_criteria:
                            ac_text = ac.get('text', '') if isinstance(ac, dict) else str(ac)
                            if not ac_text:
                                continue
                            ac_norm = self._normalize_name(ac_text)
                            
                            if (method_name_norm in ac_norm or 
                                ac_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(ac_norm)):
                                if not best_match or best_match_type in ['epic', 'sub_epic']:
                                    best_match = f"{epic_name} - {story_name}" if epic_name else story_name
                                    best_match_type = 'story'
                        
                        if (method_name_norm in sub_epic_name_norm or 
                            sub_epic_name_norm.startswith(method_name_norm) or
                            method_name_norm.startswith(sub_epic_name_norm)):
                            if not best_match or best_match_type == 'epic':
                                best_match = f"{epic_name} - {sub_epic_name}" if epic_name else sub_epic_name
                                best_match_type = 'sub_epic'
                        
                        if epic_name_norm and (method_name_norm in epic_name_norm or 
                                             epic_name_norm.startswith(method_name_norm) or
                                             method_name_norm.startswith(epic_name_norm)):
                            if not best_match:
                                best_match = epic_name
                                best_match_type = 'epic'
        
        if 'epic' in method_name_norm.lower():
            for epic in epics:
                epic_name = epic.get('name', '')
                if not epic_name:
                    continue
                
                if 'sub' in method_name_norm.lower():
                    sub_epics = epic.get('sub_epics', [])
                    for sub_epic in sub_epics:
                        sub_epic_name = sub_epic.get('name', '')
                        if sub_epic_name:
                            if not best_match or best_match_type == 'epic':
                                best_match = f"{epic_name} - {sub_epic_name}" if epic_name else sub_epic_name
                                best_match_type = 'sub_epic'
                else:
                    if not best_match:
                        best_match = epic_name
                        best_match_type = 'epic'
        
        return best_match
    
    def _normalize_name(self, name: str) -> str:
        return re.sub(r'[^\w]', '', name.lower())
    
    def _pascal_to_story_name(self, pascal_name: str) -> str:
        return re.sub(r'([A-Z])', r' \1', pascal_name).strip()
    
    def _names_match(self, name1: str, name2: str) -> bool:
        n1 = re.sub(r'[^\w]', '', name1.lower())
        n2 = re.sub(r'[^\w]', '', name2.lower())
        return n1 == n2
    
    def _is_abbreviated(self, class_name: str, story_names: List[str]) -> bool:
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        if len(story_name_from_class) < 10:
            return True
        
        abbrev_patterns = [r'\bGen\b', r'\bMgr\b', r'\bCfg\b', r'\bSvc\b', r'\bUtil\b', r'\bHelper\b']
        for pattern in abbrev_patterns:
            if re.search(pattern, class_name):
                return True
        
        return False
    
    def _is_generic(self, class_name: str) -> bool:
        generic_names = ['TestToolGeneration', 'TestValidation', 'TestHelpers', 'TestUtils']
        return class_name in generic_names
    
    def _extract_epic_names(self, story_graph: Dict[str, Any]) -> List[str]:
        epic_names = []
        epics = story_graph.get('epics', [])
        for epic in epics:
            epic_name = epic.get('name', '')
            if epic_name:
                snake_case = self._to_snake_case(epic_name)
                epic_names.append(snake_case)
        return epic_names
    
    def _extract_sub_epic_names(self, story_graph: Dict[str, Any]) -> List[str]:
        sub_epic_names = []
        epics = story_graph.get('epics', [])
        for epic in epics:
            self._extract_sub_epic_names_recursive(epic.get('sub_epics', []), sub_epic_names)
        return sub_epic_names
    
    def _extract_sub_epic_names_recursive(self, sub_epics: List[Dict[str, Any]], result: List[str]) -> None:
        for sub_epic in sub_epics:
            sub_epic_name = sub_epic.get('name', '')
            if sub_epic_name:
                snake_case = self._to_snake_case(sub_epic_name)
                result.append(snake_case)
            nested_sub_epics = sub_epic.get('sub_epics', [])
            if nested_sub_epics:
                self._extract_sub_epic_names_recursive(nested_sub_epics, result)
    
    def _to_snake_case(self, name: str) -> str:
        name = name.replace('&amp;', 'and')
        name = name.replace('&', 'and')
        name = re.sub(r'\band\s+', 'and', name)
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
        name = name.replace(' ', '_')
        name = re.sub(r'[^a-zA-Z0-9_]', '', name)
        return name.lower()
    
    def _check_file_name_matches_sub_epic(self, file_name: str, sub_epic_names: List[str], file_path: Path, rule_obj: Any, story_graph: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        name_without_prefix = file_name[5:] if file_name.startswith('test_') else file_name
        
        name_normalized = self._to_snake_case(name_without_prefix)
        
        matches = [name for name in sub_epic_names if name_normalized == name or name_normalized in name or name in name_normalized]
        
        if matches:
            return None
        
        epic_names = self._extract_epic_names(story_graph)
        epic_matches = [name for name in epic_names if name_normalized == name or name_normalized in name or name in name_normalized]
        
        if epic_matches:
            if self._is_helper_file_only(file_path):
                return None
            
            sub_epics_spanned = self._get_sub_epics_spanned_by_test_methods(file_path, story_graph)
            if len(sub_epics_spanned) > 1:
                return None
        
        sub_epics_spanned = self._get_sub_epics_spanned_by_test_methods(file_path, story_graph)
        
        if len(sub_epics_spanned) > 1:
            return None
        
        suggestions = self._find_closest_sub_epic_names(name_normalized, sub_epic_names)
        suggestion_text = ""
        if suggestions:
            suggestion_list = ", ".join([f"test_{s}.py" for s in suggestions[:5]])  # Limit to top 5
            suggestion_text = f" Suggested names: {suggestion_list}"
        
        return Violation(
            rule=rule_obj,
            violation_message=f'Test file name "{file_name}" does not match any sub-epic name and test methods do not span multiple sub-epics - file should be named test_<sub_epic_name>.py.{suggestion_text}',
            location=str(file_path),
            severity='error'
        ).to_dict()
    
    def _get_sub_epics_spanned_by_test_methods(self, file_path: Path, story_graph: Dict[str, Any]) -> set:
        sub_epics = set()
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        class_name = node.name
                        
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                if item.name.startswith('test_'):
                                    sub_epic = self._find_sub_epic_for_method(item.name, class_name, story_graph)
                                    if sub_epic:
                                        sub_epics.add(self._to_snake_case(sub_epic))
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.debug(f"Skipping file {file_path} due to parse error: {e}")
            return set()
        
        return sub_epics
    
    def _find_sub_epic_for_method(self, method_name: str, class_name: str, story_graph: Dict[str, Any]) -> Optional[str]:
        method_name_norm = self._normalize_name(method_name)
        story_name_from_class = class_name[4:] if class_name.startswith('Test') else class_name
        story_name_normalized = self._normalize_name(story_name_from_class)
        
        epics = story_graph.get('epics', [])
        
        for epic in epics:
            sub_epics = epic.get('sub_epics', [])
            for sub_epic in sub_epics:
                sub_epic_name = sub_epic.get('name', '')
                sub_epic_name_norm = self._normalize_name(sub_epic_name) if sub_epic_name else ''
                
                story_groups = sub_epic.get('story_groups', [])
                for story_group in story_groups:
                    stories = story_group.get('stories', [])
                    for story in stories:
                        story_name = story.get('name', '')
                        story_name_norm = self._normalize_name(story_name) if story_name else ''
                        
                        story_matches_class = (story_name_norm == story_name_normalized or 
                                             story_name_norm.startswith(story_name_normalized) or
                                             story_name_normalized.startswith(story_name_norm))
                        
                        scenarios = story.get('scenarios', [])
                        for scenario in scenarios:
                            scenario_name = scenario.get('name', '')
                            if not scenario_name:
                                continue
                            scenario_name_norm = self._normalize_name(scenario_name)
                            
                            if (method_name_norm in scenario_name_norm or 
                                scenario_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(scenario_name_norm)):
                                return sub_epic_name
                        
                        if story_matches_class:
                            if (method_name_norm in story_name_norm or 
                                story_name_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(story_name_norm)):
                                return sub_epic_name
                        
                        acceptance_criteria = story.get('acceptance_criteria', [])
                        for ac in acceptance_criteria:
                            ac_text = ac.get('text', '') if isinstance(ac, dict) else str(ac)
                            if not ac_text:
                                continue
                            ac_norm = self._normalize_name(ac_text)
                            
                            if (method_name_norm in ac_norm or 
                                ac_norm.startswith(method_name_norm) or
                                method_name_norm.startswith(ac_norm)):
                                return sub_epic_name
                        
                        if (method_name_norm in sub_epic_name_norm or 
                            sub_epic_name_norm.startswith(method_name_norm) or
                            method_name_norm.startswith(sub_epic_name_norm)):
                            return sub_epic_name
        
        return None
    
    def _find_closest_sub_epic_names(self, file_name: str, sub_epic_names: List[str], max_suggestions: int = 5) -> List[str]:
        if not sub_epic_names:
            return []
        
        scored_names = []
        file_name_lower = file_name.lower()
        
        for sub_epic_name in sub_epic_names:
            sub_epic_lower = sub_epic_name.lower()
            
            score = 0
            
            if file_name_lower == sub_epic_lower:
                score = 1000
            elif file_name_lower in sub_epic_lower:
                score = 50 + len(file_name_lower)
            elif sub_epic_lower in file_name_lower:
                score = 30 + len(sub_epic_lower)
            else:
                file_parts = set(file_name_lower.split('_'))
                sub_epic_parts = set(sub_epic_lower.split('_'))
                common_parts = file_parts.intersection(sub_epic_parts)
                if common_parts:
                    score = len(common_parts) * 10
            
            if score > 0:
                scored_names.append((score, sub_epic_name))
        
        scored_names.sort(key=lambda x: x[0], reverse=True)
        return [name for _, name in scored_names[:max_suggestions]]
    
    def _is_helper_file_only(self, file_path: Path) -> bool:
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test'):
                        return False
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        return False
            
            return True
        except (SyntaxError, UnicodeDecodeError):
            return False
    

