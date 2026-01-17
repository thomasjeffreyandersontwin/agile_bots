
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation

class BackgroundCommonSetupScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            background = story_data.get('background', [])
            
            if background:
                violation = self._check_background_has_when_then(background, node)
                if violation:
                    violations.append(violation)
                
                violation = self._check_background_scenario_specific(background, scenarios, node)
                if violation:
                    violations.append(violation)
            
            if len(scenarios) >= 3 and not background:
                violation = self._check_missing_background(scenarios, node)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_background_has_when_then(self, background: List[str], node: StoryNode) -> Optional[Dict[str, Any]]:
        for step in background:
            step_lower = step.lower().strip()
            if step_lower.startswith('when ') or step_lower.startswith('then '):
                location = f"{node.map_location()}.background"
                return Violation(
                    rule=self.rule,
                    violation_message=f'Background contains "{step}" - Background should only contain Given/And steps, not When/Then',
                    location=location,
                    severity='error'
                ).to_dict()
        return None
    
    def _check_background_scenario_specific(self, background: List[str], scenarios: List[Dict[str, Any]], node: StoryNode) -> Optional[Dict[str, Any]]:
        
        if len(scenarios) < 3 and background:
            location = f"{node.map_location()}.background"
            return Violation(
                rule=self.rule,
                violation_message=f'Background exists but story has only {len(scenarios)} scenario(s) - Background should only be used when 3+ scenarios share common setup',
                location=location,
                severity='warning'
            ).to_dict()
        
        return None
    
    def _check_missing_background(self, scenarios: List[Dict[str, Any]], node: StoryNode) -> Optional[Dict[str, Any]]:
        if len(scenarios) >= 3:
            first_scenario_steps = self._get_given_steps(scenarios[0])
            if first_scenario_steps:
                all_match = all(
                    self._get_given_steps(scenario)[:len(first_scenario_steps)] == first_scenario_steps
                    for scenario in scenarios[1:]
                )
                if all_match and len(first_scenario_steps) > 0:
                    location = f"{node.map_location()}"
                    return Violation(
                        rule=self.rule,
                        violation_message=f'Story has {len(scenarios)} scenarios that all start with same Given steps - consider moving common setup to Background section',
                        location=location,
                        severity='info'
                    ).to_dict()
        
        return None
    
    def _get_given_steps(self, scenario: Dict[str, Any]) -> List[str]:
        steps = []
        scenario_steps = self._get_scenario_steps(scenario)
        for step in scenario_steps:
            step_lower = step.lower().strip()
            if step_lower.startswith('given ') or step_lower.startswith('and '):
                steps.append(step)
            else:
                break
        return steps
    
    def _get_scenario_steps(self, scenario: Dict[str, Any]) -> List[str]:
        if isinstance(scenario, dict):
            if 'steps' in scenario:
                return scenario['steps']
            elif 'scenario' in scenario:
                scenario_text = scenario['scenario']
                if isinstance(scenario_text, str):
                    return [s.strip() for s in scenario_text.split('\n') if s.strip()]
        return []

