
from abc import abstractmethod
from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from pathlib import Path
import ast
from scanners.scanner import Scanner
from scanners.violation import Violation

if TYPE_CHECKING:
    from scanners.resources.scan_context import ScanFilesContext, FileScanContext, CrossFileScanContext
    from actions.rules.rule import Rule

class CodeScanner(Scanner):
    
    def __init__(self, rule: 'Rule'):
        super().__init__(rule)
        self.story_graph = None
    
    def scan_with_context(self, context: 'ScanFilesContext') -> List[Dict[str, Any]]:
        self.story_graph = context.story_graph
        return super().scan_with_context(context)
    
    def scan_file_with_context(self, context: 'FileScanContext') -> List[Dict[str, Any]]:
        self.story_graph = context.story_graph
        return self._empty_violation_list()
    
    def _extract_domain_terms(self, story_graph: Dict[str, Any]) -> set:
        domain_terms = self._get_common_domain_terms()
        
        if not story_graph:
            return domain_terms
        
        for epic in story_graph.get('epics', []):
            if isinstance(epic, dict):
                self._extract_terms_from_epic(epic, domain_terms)
        
        return domain_terms
    
    def _get_common_domain_terms(self) -> set:
        return {
            'json', 'data', 'param', 'params', 'parameter', 'parameters',
            'var', 'vars', 'variable', 'variables',
            'method', 'methods', 'class', 'classes', 'call', 'calls',
            'config', 'configuration', 'configurations',
            'agent', 'bot', 'workflow', 'story', 'epic', 'scenario', 'action',
            'behavior', 'rule', 'rules', 'validation', 'validate', 'scanner',
            'file', 'files', 'directory', 'directories', 'path', 'paths',
            'state', 'states', 'tool', 'tools', 'server', 'catalog', 'metadata'
        }
    
    def _extract_terms_from_epic(self, epic: dict, domain_terms: set) -> None:
        self._add_name_terms(epic.get('name', ''), domain_terms)
        self._extract_terms_from_concepts(epic.get('domain_concepts', []), domain_terms)
        
        for sub_epic in epic.get('sub_epics', []):
            if isinstance(sub_epic, dict):
                self._extract_terms_from_sub_epic(sub_epic, domain_terms)
    
    def _extract_terms_from_sub_epic(self, sub_epic: dict, domain_terms: set) -> None:
        self._add_name_terms(sub_epic.get('name', ''), domain_terms)
        self._extract_terms_from_concepts(sub_epic.get('domain_concepts', []), domain_terms)
        
        for story_group in sub_epic.get('story_groups', []):
            if isinstance(story_group, dict):
                for story in story_group.get('stories', []):
                    if isinstance(story, dict):
                        self._extract_terms_from_story(story, domain_terms)
    
    def _extract_terms_from_concepts(self, concepts: list, domain_terms: set) -> None:
        for concept in concepts:
            if not isinstance(concept, dict):
                continue
            
            concept_name = concept.get('name', '')
            if concept_name:
                domain_terms.add(concept_name.lower())
                domain_terms.add(concept_name.lower().replace(' ', '_'))
                domain_terms.update(self._extract_words_from_text(concept_name))
            
            self._extract_responsibility_terms(concept.get('responsibilities', []), domain_terms)
            self._extract_collaborator_terms(concept.get('collaborators', []), domain_terms)
    
    def _extract_responsibility_terms(self, responsibilities: list, domain_terms: set) -> None:
        for resp in responsibilities:
            if isinstance(resp, dict) and resp.get('name'):
                domain_terms.update(self._extract_words_from_text(resp['name']))
    
    def _extract_collaborator_terms(self, collaborators: list, domain_terms: set) -> None:
        for collab in collaborators:
            if isinstance(collab, str):
                domain_terms.add(collab.lower())
                domain_terms.update(self._extract_words_from_text(collab))
    
    def _extract_terms_from_story(self, story: dict, domain_terms: set) -> None:
        self._add_name_terms(story.get('name', ''), domain_terms)
        self._extract_acceptance_criteria_terms(story.get('acceptance_criteria', []), domain_terms)
        self._extract_scenario_terms(story.get('scenarios', []), domain_terms)
    
    def _extract_acceptance_criteria_terms(self, criteria: list, domain_terms: set) -> None:
        for ac in criteria:
            if isinstance(ac, dict) and ac.get('criterion'):
                domain_terms.update(self._extract_words_from_text(ac['criterion']))
            elif isinstance(ac, str):
                domain_terms.update(self._extract_words_from_text(ac))
    
    def _extract_scenario_terms(self, scenarios: list, domain_terms: set) -> None:
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                continue
            for step in scenario.get('steps', []):
                if isinstance(step, str):
                    domain_terms.update(self._extract_words_from_text(step))
    
    def _add_name_terms(self, name: str, domain_terms: set) -> None:
        if name:
            domain_terms.update(self._extract_words_from_text(name))
    
    def _extract_words_from_text(self, text: str) -> set:
        if not text:
            return set()
        
        import re
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return set(words)
    
    def _matches_domain_term(self, name: str, domain_terms: set) -> bool:
        if not name or not domain_terms:
            return False
        
        name_lower = name.lower()
        name_words = self._extract_words_from_text(name)
        
        for domain_term in domain_terms:
            if domain_term in name_words:
                return True
            if domain_term in name_lower or name_lower in domain_term:
                return True
        
        return False
    
    def _read_and_parse_file(self, file_path: Path) -> Optional[Tuple[str, List[str], ast.AST]]:
        import logging
        logger = logging.getLogger(__name__)
        
        if not file_path.exists():
            return None
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            tree = ast.parse(content, filename=str(file_path))
            return (content, lines, tree)
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.debug(f'Skipping file {file_path} due to {type(e).__name__}: {e}')
            return None
    
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
