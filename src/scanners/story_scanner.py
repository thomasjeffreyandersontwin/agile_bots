from abc import abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from scanners.scanner import Scanner
from story_graph import StoryMap, StoryNode, StoryGroup
from domain_concept_node import DomainConceptNode

if TYPE_CHECKING:
    from scanners.resources.scan_context import ScanFilesContext
    from actions.rules.rule import Rule

class StoryScanner(Scanner):
    
    def __init__(self, rule: 'Rule'):
        super().__init__(rule)
    
    def scan_with_context(self, context: 'ScanFilesContext') -> List[Dict[str, Any]]:
        violations = []
        story_graph_data = context.story_graph.get('story_graph', context.story_graph)
        story_map = StoryMap(story_graph_data)
        
        for epic in story_map.epics():
            for node in story_map.walk(epic):
                if not isinstance(node, StoryGroup):
                    node_violations = self.scan_story_node(node)
                    violations.extend(node_violations)
        
        return violations
    
    def _scan_domain_concepts(
        self,
        domain_concepts: List[Dict[str, Any]],
        epic_idx: int,
        sub_epic_path: Optional[List[int]]
    ) -> List[Dict[str, Any]]:
        violations = []
        
        for concept_idx, concept_data in enumerate(domain_concepts):
            concept_name = concept_data.get('name', '')
            responsibilities = concept_data.get('responsibilities', [])
            
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
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        pass
    
    def scan_domain_concept(self, node: 'DomainConceptNode') -> List[Dict[str, Any]]:
        return []
