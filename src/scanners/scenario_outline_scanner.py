
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation
import re

class ScenarioOutlineScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            
            for scenario_idx, scenario in enumerate(scenarios):
                scenario_text = self._get_scenario_text(scenario)
                
                if 'Scenario Outline' in scenario_text:
                    has_examples = 'Examples:' in scenario_text or 'examples' in str(scenario).lower()
                    
                    if not has_examples:
                        location = f"{node.map_location()}.scenarios[{scenario_idx}]"
                        violation = Violation(
                            rule=self.rule,
                            violation_message='Scenario Outline used but no Examples table found - Scenario Outlines require Examples table',
                            location=location,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
        
        return violations
    
    def _get_scenario_text(self, scenario: Dict[str, Any]) -> str:
        if isinstance(scenario, dict):
            return scenario.get('scenario', '') or scenario.get('name', '') or str(scenario)
        return str(scenario)

