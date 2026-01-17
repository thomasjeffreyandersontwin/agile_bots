
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation
import re

class PlainEnglishScenariosScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            story_data = node.data
            scenarios = story_data.get('scenarios', [])
            
            for scenario_idx, scenario in enumerate(scenarios):
                scenario_text = self._get_scenario_text(scenario)
                
                violation = self._check_variables(scenario_text, node, scenario_idx, rule_obj)
                if violation:
                    violations.append(violation)
                
                violation = self._check_scenario_outline(scenario_text, node, scenario_idx, rule_obj)
                if violation:
                    violations.append(violation)
                
                violation = self._check_examples_table(scenario, node, scenario_idx, rule_obj)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _get_scenario_text(self, scenario: Dict[str, Any]) -> str:
        if isinstance(scenario, dict):
            return scenario.get('scenario', '') or scenario.get('name', '') or str(scenario)
        return str(scenario)
    
    def _check_variables(self, scenario_text: str, node: StoryNode, scenario_idx: int, rule_obj: Any) -> Optional[Dict[str, Any]]:
        if re.search(r'<[^>]+>', scenario_text):
            location = f"{node.map_location()}.scenarios[{scenario_idx}]"
            return Violation(
                rule=rule_obj,
                violation_message=f'Scenario contains variable placeholder (e.g., "<variable>") - use plain English instead',
                location=location,
                severity='error'
            ).to_dict()
        
        if re.search(r'"[<][^>]+[>]"', scenario_text):
            location = f"{node.map_location()}.scenarios[{scenario_idx}]"
            return Violation(
                rule=rule_obj,
                violation_message=f'Scenario contains quoted placeholder (e.g., "<variable>") - use plain English instead',
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def _check_scenario_outline(self, scenario_text: str, node: StoryNode, scenario_idx: int, rule_obj: Any) -> Optional[Dict[str, Any]]:
        if 'Scenario Outline:' in scenario_text or 'Scenario Outline' in scenario_text:
            location = f"{node.map_location()}.scenarios[{scenario_idx}]"
            return Violation(
                rule=rule_obj,
                violation_message='Scenario uses Scenario Outline - use plain English scenarios instead',
                location=location,
                severity='error'
            ).to_dict()
        
        return None
    
    def _check_examples_table(self, scenario: Dict[str, Any], node: StoryNode, scenario_idx: int, rule_obj: Any) -> Optional[Dict[str, Any]]:
        if isinstance(scenario, dict):
            if 'examples' in scenario or 'Examples:' in str(scenario):
                location = f"{node.map_location()}.scenarios[{scenario_idx}]"
                return Violation(
                    rule=rule_obj,
                    violation_message='Scenario contains Examples table - use plain English scenarios instead',
                    location=location,
                    severity='error'
                ).to_dict()
        
        return None

