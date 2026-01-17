
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation

class ScenarioSpecificGivenScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            background = story_data.get('background', [])
            
            for scenario_idx, scenario in enumerate(scenarios):
                scenario_steps = self._get_scenario_steps(scenario)
                
                if scenario_steps:
                    first_step = scenario_steps[0]
                    if not first_step.startswith('Given'):
                        location = f"{node.map_location()}.scenarios[{scenario_idx}]"
                        violation = Violation(
                            rule=rule_obj,
                            violation_message=f'Scenario does not start with Given step - scenario-specific setup should start with Given, not When',
                            location=location,
                            severity='error'
                        ).to_dict()
                        violations.append(violation)
        
        return violations
    
    def _get_scenario_steps(self, scenario: Dict[str, Any]) -> List[str]:
        steps = []
        if isinstance(scenario, dict):
            if 'steps' in scenario:
                steps = scenario['steps']
            elif 'scenario' in scenario:
                scenario_text = scenario['scenario']
                if isinstance(scenario_text, str):
                    steps = [s.strip() for s in scenario_text.split('\n') if s.strip()]
        return steps

