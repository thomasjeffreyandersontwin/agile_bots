"""Scanner for validating ubiquitous language consistency."""

from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import logging
import ast
import re
from test_scanner import TestScanner
from scanners.violation import Violation

logger = logging.getLogger(__name__)

class UbiquitousLanguageScanner(TestScanner):
    
    def scan_file(self, file_path: Path, rule_obj: Any = None, story_graph: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        violations = []
        
        parsed = self._read_and_parse_file(file_path)
        if not parsed:
            return violations
        
        content, lines, tree = parsed
        
        domain_entities = self._extract_domain_entities_from_story_graph(story_graph)
        
        classes_under_test = self._extract_classes_under_test(tree, content, lines)
        
        violations.extend(
            self._check_classes_against_domain_model(
                classes_under_test, 
                domain_entities, 
                file_path, 
                rule_obj
            )
        )
        
        return violations
    
    def _extract_domain_entities_from_story_graph(self, story_graph: Dict[str, Any]) -> Set[str]:
        """
        Extract domain entity names (nouns/classes) from story graph.
        Look in domain_concepts sections for entity names.
        """
        if not story_graph:
            return set()
        
        entities = set()
        
        epics = story_graph.get('epics', [])
        for epic in epics:
            self._extract_from_node(epic, entities)
        
        return entities
    
    def _extract_from_node(self, node: Dict[str, Any], entities: Set[str]):
        """Recursively extract domain concepts from any node."""
        domain_concepts = node.get('domain_concepts', [])
        for concept in domain_concepts:
            if isinstance(concept, dict):
                name = concept.get('name', '')
                if name:
                    entities.add(name)
                    entities.add(self._to_class_name(name))
            elif isinstance(concept, str):
                entities.add(concept)
                entities.add(self._to_class_name(concept))
        
        for sub_epic in node.get('sub_epics', []):
            self._extract_from_node(sub_epic, entities)
    
    def _to_class_name(self, concept_name: str) -> str:
        """
        Convert domain concept name to expected class name.
        'REPL Session' -> 'REPLSession'
        'Behavior Action State' -> 'BehaviorActionState'
        Preserves acronyms (all-caps words stay all-caps)
        """
        def convert_word(word: str) -> str:
            if word.isupper() and len(word) > 1:
                return word
            return word.capitalize()
        
        return ''.join(convert_word(word) for word in concept_name.split())
    
    def _extract_classes_under_test(self, tree: ast.AST, content: str, lines: List[str]) -> List[Tuple[str, int, str]]:
        """
        Extract all class instantiations and imports from test file.
        Returns list of (class_name, line_number, code_snippet)
        """
        classes_used = []
        
        class ClassVisitor(ast.NodeVisitor):
            def __init__(self):
                self.classes = []
            
            def visit_Call(self, node: ast.Call):
                if isinstance(node.func, ast.Name):
                    class_name = node.func.id
                    line_num = node.lineno
                    snippet = self._get_code_snippet(lines, line_num)
                    self.classes.append((class_name, line_num, snippet))
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node: ast.ImportFrom):
                for alias in node.names:
                    class_name = alias.name
                    line_num = node.lineno
                    snippet = self._get_code_snippet(lines, line_num)
                    self.classes.append((class_name, line_num, snippet))
                self.generic_visit(node)
            
            def _get_code_snippet(self, lines: List[str], line_num: int, context: int = 2) -> str:
                """Get code snippet around the line."""
                start = max(0, line_num - context - 1)
                end = min(len(lines), line_num + context)
                return '\n'.join(lines[start:end])
        
        try:
            visitor = ClassVisitor()
            visitor.visit(tree)
            classes_used = visitor.classes
        except Exception as e:
            logger.warning(f"Error extracting classes from AST: {e}")
        
        return classes_used
    
    def _check_classes_against_domain_model(
        self, 
        classes_under_test: List[Tuple[str, int, str]], 
        domain_entities: Set[str],
        file_path: Path,
        rule_obj: Any
    ) -> List[Dict[str, Any]]:
        """
        Check if classes being tested are in the domain model.
        Flag violations for:
        1. Classes not in domain model
        2. Agent nouns (Handler, Manager, Service, Processor) detected via NLTK
        """
        from vocabulary_helper import VocabularyHelper
        
        violations = []
        
        ignore_classes = {
            'Mock', 'MagicMock', 'patch', 'pytest', 'Path', 'Dict', 'List', 'Set', 
            'Any', 'Optional', 'Tuple', 'Union', 'Callable', 'Type',
            'json', 'logging', 'datetime', 'timedelta', 'date', 'time',
            'StringIO', 'BytesIO', 'TextIOWrapper', 'BufferedReader', 'BufferedWriter',
            'OrderedDict', 'defaultdict', 'Counter', 'deque',
            'Process', 'Thread', 'Lock', 'Queue', 'Event',
            'Bot'
        }
        
        for class_name, line_num, code_snippet in classes_under_test:
            if class_name.startswith('Test') or class_name in ignore_classes:
                continue
            
            if class_name and class_name[0].islower():
                continue
            
            if class_name not in domain_entities:
                is_agent, base_verb, suffix = VocabularyHelper.is_agent_noun(class_name)
                
                if is_agent:
                    message = f"Class '{class_name}' is an agent noun (doer of action from verb '{base_verb}') not in domain model. Use domain entity names from story graph."
                    if code_snippet:
                        message += f"\n\n```python\n{code_snippet}\n```"
                    
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=message,
                        location=f"{file_path}",
                        line_number=line_num,
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                elif len(class_name) > 3:
                    message = f"Class '{class_name}' not found in domain model. Base APIs on domain concepts or update domain model documentation."
                    if code_snippet:
                        message += f"\n\n```python\n{code_snippet}\n```"
                    
                    violation = Violation(
                        rule=rule_obj,
                        violation_message=message,
                        location=f"{file_path}",
                        line_number=line_num,
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations

