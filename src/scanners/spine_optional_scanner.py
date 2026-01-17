from typing import List, Dict, Any, Optional
from story_scanner import StoryScanner
from story_map import StoryNode, Story, StoryGroup
from scanners.violation import Violation

class SpineOptionalScanner(StoryScanner):
    
    def scan(
        self, 
        story_graph: Dict[str, Any] = None,
        test_files: Optional[List['Path']] = None,
        code_files: Optional[List['Path']] = None,
        on_file_scanned: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        if not self.rule:
            raise ValueError("self.rule parameter is required for SpineOptionalScanner")
        
        violations = []
        from story_map import StoryMap
        story_map = StoryMap(story_graph)
        
        for epic in story_map.epics():
            for node in story_map.walk(epic):
                if isinstance(node, StoryGroup):
                    group_violations = self._scan_story_group(node)
                    violations.extend(group_violations)
        
        return violations
    
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        return []
    
    def _scan_story_group(self, story_group: StoryGroup) -> List[Dict[str, Any]]:
        violations = []
        stories = story_group.children
        
        if len(stories) < 2:
            return violations
        
        sequential_stories = [s for s in stories if isinstance(s, Story) and s.sequential_order > 0]
        optional_stories = [s for s in stories if isinstance(s, Story) and s.data.get('optional', False)]
        
        violation = self._check_sequential_order_gaps(sequential_stories, story_group)
        if violation:
            violations.append(violation)
        
        violation = self._check_missing_optional_markers(stories, sequential_stories)
        if violation:
            violations.extend(violation)
        
        violation = self._check_all_stories_mandatory(stories, sequential_stories, optional_stories, story_group)
        if violation:
            violations.append(violation)
        
        return violations
    
    def _check_sequential_order_gaps(self, sequential_stories: List[Story], story_group: StoryGroup) -> Optional[Dict[str, Any]]:
        if len(sequential_stories) < 2:
            return None
        
        sequential_stories.sort(key=lambda s: s.sequential_order)
        expected_order = 1
        
        for seq_story in sequential_stories:
            if seq_story.sequential_order != expected_order:
                location = seq_story.map_location('sequential_order')
                return Violation(
                    rule=self.rule,
                    violation_message=f'Story "{seq_story.name}" has sequential_order {seq_story.sequential_order}, but expected {expected_order} (gap in sequence)',
                    location=location,
                    severity='error'
                ).to_dict()
            expected_order += 1
        
        return None
    
    def _check_missing_optional_markers(self, all_stories: List[Story], sequential_stories: List[Story]) -> List[Dict[str, Any]]:
        violations = []
        
        if len(sequential_stories) == 0:
            return violations
        
        for story in all_stories:
            if not isinstance(story, Story):
                continue
            
            is_optional = story.data.get('optional', False)
            sequential_order = story.sequential_order
            
            if sequential_order == 0 and not is_optional:
                location = story.map_location('optional')
                violations.append(Violation(
                    rule=self.rule,
                    violation_message=f'Story "{story.name}" has no sequential_order and is not marked as optional - should be marked optional: true if not part of spine',
                    location=location,
                    severity='warning'
                ).to_dict())
        
        return violations
    
    def _check_all_stories_mandatory(self, all_stories: List[Story], sequential_stories: List[Story], optional_stories: List[Story], story_group: StoryGroup) -> Optional[Dict[str, Any]]:
        if len(all_stories) < 2:
            return None
        
        if len(sequential_stories) == len(all_stories) and len(optional_stories) == 0:
            location = story_group.map_location()
            return Violation(
                rule=self.rule,
                violation_message=f'All stories in story group have sequential_order - consider marking some as optional if they are alternatives or enhancements',
                location=location,
                severity='warning'
            ).to_dict()
        
        return None

