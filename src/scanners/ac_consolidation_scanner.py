
from typing import List, Dict, Any
from scanners.story_scanner import StoryScanner
from story_graph.nodes import StoryNode, Story
from scanners.violation import Violation
from collections import defaultdict

class ACConsolidationScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            acceptance_criteria = story_data.get('acceptance_criteria', [])
            
            violations.extend(self._check_duplicate_ac(acceptance_criteria, node))
        
        return violations
    
    def _check_duplicate_ac(self, acceptance_criteria: List[Any], node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        ac_texts = []
        for ac in acceptance_criteria:
            ac_text = self._get_ac_text(ac).lower().strip()
            ac_texts.append(ac_text)
        
        ac_counts = defaultdict(list)
        for idx, ac_text in enumerate(ac_texts):
            ac_counts[ac_text].append(idx)
        
        for ac_text, indices in ac_counts.items():
            if len(indices) > 1:
                location = f"{node.map_location()}.acceptance_criteria"
                violation = Violation(
                    rule=self.rule,
                    violation_message=f'Duplicate acceptance criteria found at indices {indices} - consolidate duplicate AC',
                    location=location,
                    severity='warning'
                ).to_dict()
                violations.append(violation)
        
        return violations
    
    def _get_ac_text(self, ac: Any) -> str:
        if isinstance(ac, dict):
            return ac.get('criterion', '') or ac.get('description', '') or str(ac)
        return str(ac)

