
from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Epic
from scanners.violation import Violation

class VerticalSliceScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        return violations
    
    def scan(
        self, 
        story_graph: Dict[str, Any], 
        rule_obj: Any = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None,
        on_file_scanned: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        violations = []
        
        if not rule_obj:
            raise ValueError("rule_obj parameter is required")
        
        increments = story_graph.get('increments', [])
        
        for increment_idx, increment in enumerate(increments):
            increment_epics = increment.get('epics', [])
            
            if len(increment_epics) == 1:
                location = f"increments[{increment_idx}]"
                violation = Violation(
                    rule=rule_obj,
                    violation_message=f'Increment "{increment.get("name", f"Increment {increment_idx+1}")}" spans only 1 epic - increments should be vertical slices spanning multiple epics',
                    location=location,
                    severity='error'
                ).to_dict()
                violations.append(violation)
        
        return violations

