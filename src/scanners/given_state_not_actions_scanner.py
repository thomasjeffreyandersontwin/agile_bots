
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation
import re

class GivenStateNotActionsScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            
            for scenario_idx, scenario in enumerate(scenarios):
                scenario_steps = self._get_scenario_steps(scenario)
                
                for step_idx, step in enumerate(scenario_steps):
                    if step.startswith('Given') or step.startswith('And'):
                        violation = self._check_given_is_action(step, node, scenario_idx, step_idx, rule_obj)
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
            elif 'given' in scenario or 'when' in scenario or 'then' in scenario:
                if 'given' in scenario:
                    given = scenario['given']
                    if isinstance(given, list):
                        steps.extend([f"Given {g}" if not g.startswith('Given') else g for g in given])
                    elif isinstance(given, str):
                        steps.append(f"Given {given}" if not given.startswith('Given') else given)
                if 'when' in scenario:
                    when = scenario['when']
                    if isinstance(when, str):
                        steps.append(f"When {when}" if not when.startswith('When') else when)
                if 'then' in scenario:
                    then = scenario['then']
                    if isinstance(then, list):
                        steps.extend([f"Then {t}" if not t.startswith('Then') else t for t in then])
                    elif isinstance(then, str):
                        steps.append(f"Then {then}" if not then.startswith('Then') else then)
        
        return steps
    
    def _check_given_is_action(self, step: str, node: StoryNode, scenario_idx: int, step_idx: int, rule_obj: Any) -> Optional[Dict[str, Any]]:
        action_verbs = [
            'invokes', 'invoked', 'calls', 'called', 'executes', 'executed',
            'clicks', 'clicked', 'sends', 'sent', 'triggers', 'triggered',
            'submits', 'submitted', 'creates', 'created', 'deletes', 'deleted',
            'updates', 'updated', 'modifies', 'modified', 'processes', 'processed',
            'runs', 'ran', 'starts', 'started', 'stops', 'stopped',
            'opens', 'opened', 'closes', 'closed', 'loads', 'loaded',
            'saves', 'saved', 'writes', 'wrote', 'reads', 'read'
        ]
        
        step_lower = step.lower()
        
        for verb in action_verbs:
            if verb in step_lower:
                if re.search(rf'\b{verb}\b', step_lower):
                    location = f"{node.map_location()}.scenarios[{scenario_idx}].steps[{step_idx}]"
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Given step "{step}" contains action verb "{verb}" - Given should describe state, not actions. Use When for actions.',
                        location=location,
                        severity='error'
                    ).to_dict()
        
        return None

