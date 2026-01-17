
from abc import abstractmethod
from typing import List, Dict, Any, Optional
from scanners.scanner import Scanner
from story_map import StoryMap
from domain_concept_node import DomainConceptNode

class DomainScanner(Scanner):
    
    def scan(
        self, 
        story_graph: Dict[str, Any] = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None,
        on_file_scanned: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.rule:
            raise ValueError("self.rule parameter is required for DomainScanner")
        
        violations = []
        story_graph_data = story_graph.get('story_graph', story_graph)
        story_map = StoryMap(story_graph_data)
        
        for epic in story_map.epics():
            epic_violations = self._scan_domain_concepts(
                epic.data.get('domain_concepts', []),
                epic.epic_idx,
                None,
                self.rule
            )
            violations.extend(epic_violations)
            
            for node in story_map.walk(epic):
                if hasattr(node, 'data') and 'domain_concepts' in node.data:
                    sub_epic_violations = self._scan_domain_concepts(
                        node.data.get('domain_concepts', []),
                        epic.epic_idx,
                        getattr(node, 'sub_epic_path', None),
                        self.rule
                    )
                    violations.extend(sub_epic_violations)
        
        return violations
    
    def _scan_domain_concepts(
        self,
        domain_concepts: List[Dict[str, Any]],
        epic_idx: int,
        sub_epic_path: Optional[List[int]]
    ) -> List[Dict[str, Any]]:
        violations = []
        
        for concept_idx, concept_data in enumerate(domain_concepts):
            domain_concept_node = DomainConceptNode(
                concept_data,
                epic_idx,
                sub_epic_path,
                concept_idx
            )
            
            concept_violations = self.scan_domain_concept(domain_concept_node)
            violations.extend(concept_violations)
        
        return violations
    
    @abstractmethod
    def scan_domain_concept(self, node: DomainConceptNode) -> List[Dict[str, Any]]:
        pass

