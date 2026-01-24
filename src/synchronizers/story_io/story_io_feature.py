"""
Sub-Epic Domain Component

Represents a sub-epic in the story map hierarchy.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .story_io_component import StoryIOComponent
from .story_io_story import Story

if TYPE_CHECKING:
    from .story_io_feature import Feature


class Feature(StoryIOComponent):
    """Represents a sub-epic containing stories."""
    
    def __init__(self, name: str, sequential_order: Optional[float] = None,
                 position: Optional[Any] = None, boundary: Optional[Any] = None,
                 flag: bool = False, parent: Optional[StoryIOComponent] = None,
                 story_count: Optional[int] = None, test_file: Optional[str] = None):
        super().__init__(name, sequential_order, position, boundary, flag, parent)
        self._story_count = story_count
        self._test_file = test_file
    
    @property
    def stories(self) -> List[Story]:
        """Get all stories in this sub-epic."""
        return [child for child in self.children if isinstance(child, Story)]
    
    @property
    def story_count(self) -> Optional[int]:
        """Get estimated story count if stories are not fully enumerated."""
        return self._story_count
    
    @property
    def estimated_stories(self) -> Optional[int]:
        """Get estimated story count (alias for story_count)."""
        return self._story_count
    
    @property
    def total_stories(self) -> int:
        """Get total stories: actual stories + estimated stories."""
        actual_stories = len(self.stories)
        estimated = self._story_count or 0
        # If we have actual stories, use them; otherwise use estimate
        if actual_stories > 0:
            return actual_stories
        return estimated
    
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize sub-epic from external source."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'stories': [s.synchronize() for s in self.stories]
        }
        if self._story_count is not None:
            result['story_count'] = self._story_count
            result['estimated_stories'] = self._story_count
        return result
    
    def synchronize_as_sub_epic(self) -> Dict[str, Any]:
        """Synchronize sub-epic as sub_epic (new format: supports nested sub_epics)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'sub_epics': [f.synchronize_as_sub_epic() for f in self.sub_epics],
            'stories': [s.synchronize() for s in self.stories]
        }
        if self._story_count is not None:
            result['estimated_stories'] = self._story_count
        return result
    
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate synchronization report for this sub-epic."""
        return {
            'sub_epic': self.name,
            'stories_count': len(self.stories),
            'estimated_stories': self._story_count,
            'total_stories': self.total_stories,
            'status': 'synchronized'
        }
    
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this sub-epic with another component."""
        if not isinstance(other, Feature):
            return {'match': False, 'reason': 'Type mismatch'}
        
        return {
            'match': self.name == other.name,
            'name_match': self.name == other.name,
            'sequential_order_match': self.sequential_order == other.sequential_order,
            'stories_count_match': len(self.stories) == len(other.stories)
        }
    
    def render(self) -> Dict[str, Any]:
        """Render sub-epic to JSON representation."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'users': [],  # Sub-epic-level users from first story
        }
        # Only include stories if there are any (never empty array)
        if self.stories:
            result['stories'] = [s.render() for s in self.stories]
        if self._story_count is not None:
            result['story_count'] = self._story_count
            result['estimated_stories'] = self._story_count
        return result
    
    def render_as_sub_epic(self) -> Dict[str, Any]:
        """Render sub-epic as sub_epic (new format: supports nested sub_epics)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
        }
        
        # Include test_file if present (critical for test links in panel)
        if hasattr(self, '_test_file') and self._test_file is not None:
            result['test_file'] = self._test_file
        
        # Sub_epics have EITHER sub_epics OR story_groups, never both, never stories
        nested_sub_epics = [f.render_as_sub_epic() for f in self.sub_epics]
        
        # Priority: story_groups > nested sub_epics
        if hasattr(self, '_story_groups_data') and self._story_groups_data:
            # Has story_groups - don't include sub_epics
            result['story_groups'] = self._story_groups_data
        elif nested_sub_epics:
            # Has nested sub_epics - don't include story_groups
            result['sub_epics'] = nested_sub_epics
        # If no story_groups and no sub_epics, don't include any field
        
        if self._story_count is not None:
            result['estimated_stories'] = self._story_count
        return result
    
    @property
    def sub_epics(self) -> List['Feature']:
        """Get nested sub-epics."""
        return [child for child in self.children if isinstance(child, Feature)]
    
    @property
    def features(self) -> List['Feature']:
        """Deprecated: Use sub_epics instead."""
        return self.sub_epics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert sub-epic to dictionary."""
        result = super().to_dict()
        result['type'] = 'sub_epic'
        result['stories'] = [s.to_dict() for s in self.stories]
        if self._story_count is not None:
            result['story_count'] = self._story_count
            result['estimated_stories'] = self._story_count
        return result

