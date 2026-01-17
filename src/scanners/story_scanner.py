from abc import abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from scanners.scanner import Scanner
from story_map import StoryMap, StoryNode, StoryGroup
from domain_concept_node import DomainConceptNode

if TYPE_CHECKING:
    from scanners.resources.scan_context import ScanFilesContext

class StoryScanner(Scanner):
    
    def scan_with_context(self, context: 'ScanFilesContext') -> List[Dict[str, Any]]:
        if not context.rule_obj:
            raise ValueError("rule_obj is required in context for StoryScanner")
        
        violations = []
        story_graph_data = context.story_graph.get('story_graph', context.story_graph)
        story_map = StoryMap(story_graph_data)
        
        for epic in story_map.epics():
            for node in story_map.walk(epic):
                if not isinstance(node, StoryGroup):
                    node_violations = self.scan_story_node(node, context.rule_obj)
                    violations.extend(node_violations)
        
        return violations
    
    def _scan_domain_concepts(
        self,
        domain_concepts: List[Dict[str, Any]],
        epic_idx: int,
        sub_epic_path: Optional[List[int]],
        rule_obj: Any
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
            
            concept_violations = self.scan_domain_concept(domain_concept_node, rule_obj)
            violations.extend(concept_violations)
        
        return violations
    
    @abstractmethod
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        pass
    
    def scan_domain_concept(self, node: 'DomainConceptNode', rule_obj: Any) -> List[Dict[str, Any]]:
        return []
