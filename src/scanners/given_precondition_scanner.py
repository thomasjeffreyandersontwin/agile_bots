
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation
import re

class GivenPreconditionScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            
            for scenario_idx, scenario in enumerate(scenarios):
                scenario_steps = self._get_scenario_steps(scenario)
                
                for step_idx, step in enumerate(scenario_steps):
                    if step.startswith('Given') or step.startswith('And'):
                        violation = self._check_given_is_functionality(step, node, scenario_idx, step_idx)
                        if violation:
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
    
    def _check_given_is_functionality(self, step: str, node: StoryNode, scenario_idx: int, step_idx: int) -> Optional[Dict[str, Any]]:
        step_lower = step.lower()
        
        functionality_patterns = [
            r'\b(processes|validates|calculates|saves|loads|displays|sends|receives)\b',
            r'\b(handles|manages|controls|orchestrates|coordinates)\b',
            r'\b(implements|executes|performs|runs|triggers)\b'
        ]
        
        for pattern in functionality_patterns:
            if re.search(pattern, step_lower):
                location = f"{node.map_location()}.scenarios[{scenario_idx}].steps[{step_idx}]"
                return Violation(
                    rule=self.rule,
                    violation_message=f'Given step "{step}" describes functionality - Given should describe preconditions/state, not functionality',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None

