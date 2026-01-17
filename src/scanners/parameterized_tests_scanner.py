from typing import List, Dict, Any, Optional
from scanners.scanner import Scanner
from scanners.violation import Violation
from story_map import StoryMap, StoryNode, Story

class ParameterizedTestsScanner(Scanner):
    
    def scan(
        self, 
        story_graph: Dict[str, Any] = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None,
        on_file_scanned: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.rule:
            raise ValueError("self.rule parameter is required for ParameterizedTestsScanner")
        
        violations = []
        story_map = StoryMap(story_graph)
        
        for epic in story_map.epics():
            for node in story_map.walk(epic):
                if isinstance(node, Story):
                    for scenario_outline in node.scenario_outlines:
                        if scenario_outline.examples_rows and len(scenario_outline.examples_rows) > 1:
                            location = scenario_outline.map_location()
                            violations.append(Violation(
                                rule=self.rule,
                                violation_message=f"Scenario outline '{scenario_outline.name}' has {len(scenario_outline.examples_rows)} examples but may not use @pytest.mark.parametrize",
                                location=location,
                                severity='warning'
                            ).to_dict())
        
        return violations

