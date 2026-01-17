
from typing import List, Dict, Any
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation

class InvestPrinciplesScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if not isinstance(node, Story):
            return violations
        
        if not hasattr(node, 'name') or not node.name:
            return violations
        
        story_data = node.data if hasattr(node, 'data') else {}
        scenarios = story_data.get('scenarios', [])
        scenario_outlines = story_data.get('scenario_outlines', [])
        acceptance_criteria = story_data.get('acceptance_criteria', [])
        
        has_scenarios = (scenarios and len(scenarios) > 0) or (scenario_outlines and len(scenario_outlines) > 0)
        has_acceptance_criteria = acceptance_criteria and len(acceptance_criteria) > 0
        
        if not has_scenarios and not has_acceptance_criteria:
            violation = Violation(
                rule=rule_obj,
                violation_message=f'Story "{node.name}" lacks scenarios/scenario_outlines or acceptance criteria in story-graph.json - INVEST principle "Testable" requires clear testable outcomes',
                location=node.name,
                severity='warning'
            ).to_dict()
            violations.append(violation)
        
        
        return violations

