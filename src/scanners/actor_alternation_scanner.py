from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story
from scanners.violation import Violation

class ActorAlternationScanner(StoryScanner):
    
    def scan_story_node(self, node: StoryNode, rule_obj: Any) -> List[Dict[str, Any]]:
        violations = []
        
        if isinstance(node, Story):
            acceptance_criteria = node.data.get('acceptance_criteria', [])
            
            for idx, ac in enumerate(acceptance_criteria):
                if not isinstance(ac, str):
                    continue
                
                violation = self._check_actor_alternation(ac, node, idx, rule_obj)
                if violation:
                    violations.append(violation)
        
        return violations
    
    def _check_actor_alternation(self, ac: str, story: Story, ac_index: int, rule_obj: Any) -> Optional[Dict[str, Any]]:
        lines = ac.split('\n')
        
        actors = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            actor = self._extract_actor(line)
            if actor:
                actors.append(actor)
        
        if len(actors) < 3:
            return None
        
        consecutive_count = 1
        prev_actor = actors[0]
        
        for i in range(1, len(actors)):
            current_actor = actors[i]
            
            if current_actor == prev_actor:
                consecutive_count += 1
                
                if consecutive_count > 2:
                    location = story.map_location(f'acceptance_criteria[{ac_index}]')
                    return Violation(
                        rule=rule_obj,
                        violation_message=f'Story "{story.name}" AC #{ac_index + 1} has {consecutive_count} consecutive {prev_actor} steps without alternating',
                        location=location,
                        severity='warning'
                    ).to_dict()
            else:
                consecutive_count = 1
                prev_actor = current_actor
        
        return None
    
    def _extract_actor(self, line: str) -> Optional[str]:
        line_lower = line.lower()
        
        for keyword in ['when ', 'then ', 'and ', 'given ']:
            if line_lower.startswith(keyword):
                line_lower = line_lower[len(keyword):].strip()
                break
        
        if any(word in line_lower for word in ['user ', 'actor ', 'customer ', 'developer ', 'human ', 'cli ', 'repl ']):
            return 'user'
        elif any(word in line_lower for word in ['system ', 'bot ', 'application ', 'server ', 'workflow ']):
            return 'system'
        
        return 'system'
