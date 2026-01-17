
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from pathlib import Path
import ast
import re
import logging
from test_scanner import TestScanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import FileScanContext
from .resources.ast_elements import Functions

logger = logging.getLogger(__name__)

class BusinessReadableTestNamesScanner(TestScanner):
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        file_path = context.file_path
        story_graph = context.story_graph

        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        domain_language = self._extract_domain_language(story_graph)
        
        functions = Functions(tree)
        for function in functions.get_many_functions:
            self._check_test_function_node(function.node, file_path, self.rule, domain_language, violations)
        
        return violations
    
    def _check_test_function_node(self, node: Any, file_path: Path, domain_language: set, violations: list) -> None:
        if not isinstance(node, ast.FunctionDef):
            return
        
        if not node.name.startswith('test_'):
            return
        
        violation = self._check_business_readable(node.name, file_path, node, self.rule, domain_language)
        if violation:
            violations.append(violation)
    
    def _extract_domain_language(self, story_graph: Dict[str, Any]) -> set:
        domain_terms = set()
        
        common_domain_terms = {
            'json', 'data', 'param', 'params', 'parameter', 'parameters',
            'var', 'vars', 'variable', 'variables',
            'method', 'methods', 'class', 'classes', 'call', 'calls',
            'config', 'configuration', 'configurations',
            'agent', 'bot', 'workflow', 'story', 'epic', 'scenario', 'action',
            'behavior', 'rule', 'rules', 'validation', 'validate', 'scanner',
            'file', 'files', 'directory', 'directories', 'path', 'paths',
            'state', 'states', 'tool', 'tools', 'server', 'catalog', 'metadata'
        }
        domain_terms.update(common_domain_terms)
        
        if not story_graph:
            return domain_terms
        
        epics = story_graph.get('epics', [])
        for epic in epics:
            if isinstance(epic, dict):
                self._extract_domain_terms_from_epic(epic, domain_terms)
        
        return domain_terms
    
    def _extract_domain_terms_from_epic(self, epic: dict, domain_terms: set) -> None:
        epic_name = epic.get('name', '')
        if epic_name:
            domain_terms.update(self._extract_words_from_text(epic_name))
        
        sub_epics = epic.get('sub_epics', [])
        for sub_epic in sub_epics:
            if isinstance(sub_epic, dict):
                self._extract_domain_terms_from_sub_epic(sub_epic, domain_terms)
    
    def _extract_domain_terms_from_sub_epic(self, sub_epic: dict, domain_terms: set) -> None:
        sub_epic_name = sub_epic.get('name', '')
        if sub_epic_name:
            domain_terms.update(self._extract_words_from_text(sub_epic_name))
        
        story_groups = sub_epic.get('story_groups', [])
        for story_group in story_groups:
            if isinstance(story_group, dict):
                self._extract_domain_terms_from_story_group(story_group, domain_terms)
    
    def _extract_domain_terms_from_story_group(self, story_group: dict, domain_terms: set) -> None:
        stories = story_group.get('stories', [])
        for story in stories:
            if isinstance(story, dict):
                self._extract_domain_terms_from_story(story, domain_terms)
    
    def _extract_domain_terms_from_story(self, story: dict, domain_terms: set) -> None:
        story_name = story.get('name', '')
        if story_name:
            domain_terms.update(self._extract_words_from_text(story_name))
        
        acceptance_criteria = story.get('acceptance_criteria', [])
        for ac in acceptance_criteria:
            if isinstance(ac, dict):
                ac_text = ac.get('criterion', '')
                if ac_text:
                    domain_terms.update(self._extract_words_from_text(ac_text))
    
    def _extract_words_from_text(self, text: str) -> set:
        if not text:
            return set()
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)
    
    def _check_business_readable(self, test_name: str, file_path: Path, node: ast.FunctionDef, domain_language: set) -> Optional[Dict[str, Any]]:
        name_without_prefix = test_name[5:] if test_name.startswith('test_') else test_name
        
        test_words = self._extract_words_from_text(name_without_prefix)
        
        if domain_language and test_words:
            matching_domain_terms = test_words.intersection(domain_language)
            if len(matching_domain_terms) >= 1:
                return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            content = None
        
        technical_terms = [
            'constructor', 'init', 'parse', 'serialize', 'deserialize',
            'xml', 'http', 'api', 'endpoint', 'request', 'response',
            'schema', 'transform', 'convert', 'encode', 'decode',
            'execute', 'invoke', 'function', 'obj', 'cfg'
        ]
        
        name_lower = name_without_prefix.lower()
        for term in technical_terms:
            if term in name_lower:
                if term in domain_language:
                    continue
                
                if self._is_clearly_technical_jargon(term, name_lower, domain_language):
                    line_number = node.lineno if hasattr(node, 'lineno') else None
                    if content:
                        return self._create_violation_with_snippet(
                                                        violation_message=f'Test name "{test_name}" contains technical jargon "{term}" - use business-readable domain language instead',
                            file_path=file_path,
                            line_number=line_number,
                            severity='error',
                            content=content,
                            ast_node=node,
                            max_lines=3
                        )
                    else:
                        return Violation(
                            rule=self.rule,
                            violation_message=f'Test name "{test_name}" contains technical jargon "{term}" - use business-readable domain language instead',
                            location=str(file_path),
                            line_number=line_number,
                            severity='error'
                        ).to_dict()
        
        technical_abbrevs = r'\b(init|cfg|obj|req|resp|api|http|xml)\b'
        if re.search(technical_abbrevs, name_lower):
            abbrev_matches = re.findall(technical_abbrevs, name_lower)
            is_domain_abbrev = any(abbrev in domain_language for abbrev in abbrev_matches)
            
            if not is_domain_abbrev:
                line_number = node.lineno if hasattr(node, 'lineno') else None
                if content:
                    return self._create_violation_with_snippet(
                                                violation_message=f'Test name "{test_name}" contains abbreviations - use full business-readable words',
                        file_path=file_path,
                        line_number=line_number,
                        severity='warning',
                        content=content,
                        ast_node=node,
                        max_lines=3
                    )
                else:
                    return Violation(
                        rule=self.rule,
                        violation_message=f'Test name "{test_name}" contains abbreviations - use full business-readable words',
                        location=str(file_path),
                        line_number=line_number,
                        severity='warning'
                    ).to_dict()
        
        words = name_without_prefix.split('_')
        if len(words) < 3:
            line_number = node.lineno if hasattr(node, 'lineno') else None
            if content:
                return self._create_violation_with_snippet(
                                        violation_message=f'Test name "{test_name}" is too vague - add context about what happens and when',
                    file_path=file_path,
                    line_number=line_number,
                    severity='warning',
                    content=content,
                    ast_node=node,
                    max_lines=3
                )
            else:
                return Violation(
                    rule=self.rule,
                    violation_message=f'Test name "{test_name}" is too vague - add context about what happens and when',
                    location=str(file_path),
                    line_number=line_number,
                    severity='warning'
                ).to_dict()
        
        return None
    
    def _is_clearly_technical_jargon(self, term: str, test_name_lower: str, domain_language: set) -> bool:
        if term in domain_language:
            return False
        
        domain_prefixes = ['agent', 'bot', 'workflow', 'story', 'epic', 'scenario', 
                          'action', 'behavior', 'rule', 'validation', 'planning',
                          'config', 'state', 'tool', 'server', 'catalog']
        
        for prefix in domain_prefixes:
            if f'{prefix}_{term}' in test_name_lower:
                return False
            if f'{term}_{prefix}' in test_name_lower and prefix in domain_language:
                return False
        
        domain_compound_patterns = [
            r'agent[_\s]json', r'workflow[_\s]json', r'story[_\s]graph[_\s]json',
            r'planning[_\s]data', r'config[_\s]data', r'validation[_\s]data',
            r'environment[_\s]var', r'working[_\s]area', r'bot[_\s]config',
            r'action[_\s]method', r'behavior[_\s]action', r'close[_\s]current[_\s]action'
        ]
        
        for pattern in domain_compound_patterns:
            if re.search(pattern, test_name_lower):
                return False
        
        return True
    
    def _extract_code_snippet(self, content: str, ast_node: Optional[ast.AST] = None, 
                             start_line: Optional[int] = None, end_line: Optional[int] = None,
                             context_before: int = 2, max_lines: int = 50) -> str:
        lines = content.split('\n')
        
        if ast_node is not None:
            start_line_0 = ast_node.lineno - 1 if hasattr(ast_node, 'lineno') and ast_node.lineno else 0
            
            if hasattr(ast_node, 'end_lineno') and ast_node.end_lineno:
                end_line_0 = ast_node.end_lineno
            else:
                end_line_0 = start_line_0 + 1
                for node in ast.walk(ast_node):
                    if hasattr(node, 'lineno') and node.lineno:
                        end_line_0 = max(end_line_0, node.lineno)
        elif start_line is not None:
            start_line_0 = start_line - 1
            if end_line is not None:
                end_line_0 = end_line
            else:
                end_line_0 = start_line_0 + 1
        else:
            return ""
        
        snippet_start = max(0, start_line_0 - context_before)
        snippet_end = min(len(lines), end_line_0 + 1)
        code_snippet = '\n'.join(lines[snippet_start:snippet_end])
        
        code_lines = code_snippet.split('\n')
        if len(code_lines) > max_lines:
            code_snippet = '\n'.join(code_lines[:max_lines]) + '\n    # ... (truncated)'
        
        return code_snippet
    
    def _create_violation_with_snippet(
        self,
        violation_message: str,
        file_path: Path,
        line_number: Optional[int] = None,
        severity: str = 'warning',
        content: Optional[str] = None,
        ast_node: Optional[ast.AST] = None,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        context_before: int = 2,
        max_lines: int = 50
    ) -> Dict[str, Any]:
        code_snippet = ""
        if content is not None:
            if ast_node is not None or start_line is not None:
                code_snippet = self._extract_code_snippet(
                    content=content,
                    ast_node=ast_node,
                    start_line=start_line,
                    end_line=end_line,
                    context_before=context_before,
                    max_lines=max_lines
                )
        
        if code_snippet:
            final_message = f"{violation_message}\n\n```python\n{code_snippet}\n```"
        else:
            final_message = violation_message
        
        return Violation(
            rule=self.rule,
            violation_message=final_message,
            location=str(file_path),
            line_number=line_number,
            severity=severity
        ).to_dict()

