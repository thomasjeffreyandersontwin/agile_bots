
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation
import re

class ScenariosCoverAllCasesScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            
            if len(scenarios) > 0:
                has_happy_path = False
                has_edge_case = False
                has_error_case = False
                
                for scenario_idx, scenario in enumerate(scenarios):
                    scenario_text = self._get_scenario_text(scenario)
                    
                    if self._is_happy_path(scenario_text):
                        has_happy_path = True
                    if self._is_edge_case(scenario_text):
                        has_edge_case = True
                    if self._is_error_case(scenario_text):
                        has_error_case = True
                
                if not has_happy_path:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message='Story has no happy path scenario - add a scenario covering the normal success case',
                        location=node.map_location(),
                        severity='error'
                    ).to_dict()
                    violations.append(violation)
                
                if not has_edge_case and len(scenarios) > 1:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message='Story has no edge case scenario - add scenarios covering boundary values and edge conditions',
                        location=node.map_location(),
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
                
                if not has_error_case and len(scenarios) > 1:
                    violation = Violation(
                        rule=rule_obj,
                        violation_message='Story has no error case scenario - add scenarios covering invalid inputs and error conditions',
                        location=node.map_location(),
                        severity='warning'
                    ).to_dict()
                    violations.append(violation)
        
        return violations
    
    def _get_scenario_text(self, scenario: Dict[str, Any]) -> str:
        if isinstance(scenario, dict):
            return scenario.get('scenario', '') or scenario.get('name', '') or str(scenario)
        return str(scenario)
    
    def _is_happy_path(self, scenario_text: str) -> bool:
        text_lower = scenario_text.lower()
        happy_indicators = ['valid', 'success', 'saves', 'completes', 'accepts', 'processes']
        return any(indicator in text_lower for indicator in happy_indicators)
    
    def _is_edge_case(self, scenario_text: str) -> bool:
        text_lower = scenario_text.lower()
        # Edge case indicators: boundary, edge, limit, maximum, minimum, empty, null, zero
        edge_indicators = ['boundary', 'edge', 'limit', 'maximum', 'minimum', 'max', 'min', 'empty', 'null', 'zero', 'first', 'last']
        return any(indicator in text_lower for indicator in edge_indicators)
    
    def _is_error_case(self, scenario_text: str) -> bool:
        text_lower = scenario_text.lower()
        error_indicators = ['error', 'invalid', 'fails', 'rejects', 'exception', 'wrong', 'missing', 'not found']
        return any(indicator in text_lower for indicator in error_indicators)

