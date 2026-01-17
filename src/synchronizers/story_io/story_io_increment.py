"""
Increment Domain Component

Represents an increment (marketable release) in the story map.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import field
from .story_io_component import StoryIOComponent
from .story_io_epic import Epic
from .story_io_feature import Feature
from .story_io_story import Story
from .story_io_position import Boundary


class Increment(StoryIOComponent):
    """Represents an increment containing epics, sub-epics, and stories."""
    
    def __init__(self, name: str, priority: Union[int, str] = 1,
                 position: Optional[Any] = None, boundary: Optional[Boundary] = None,
                 flag: bool = False, parent: Optional[StoryIOComponent] = None):
        # Convert priority to int for ordering, but preserve original
        priority_int = self._priority_to_int(priority)
        super().__init__(name, float(priority_int), position, boundary, flag, parent)
        self._priority_value = priority  # Store original (can be int or string like "NOW")
        self._priority_int = priority_int  # Store numeric value for ordering
    
    @staticmethod
    def _priority_to_int(priority: Union[int, str]) -> int:
        """Convert priority to integer for ordering."""
        if isinstance(priority, str):
            priority_map = {'NOW': 1, 'LATER': 2, 'SOON': 1, 'NEXT': 2}
            return priority_map.get(priority.upper(), 1)
        elif isinstance(priority, (int, float)):
            return int(priority)
        else:
            return 1
    
    @property
    def priority(self) -> Union[int, str]:
        """Get the priority of this increment (original value, can be int or string like 'NOW')."""
        return self._priority_value
    
    @property
    def priority_int(self) -> int:
        """Get the numeric priority value for ordering."""
        return self._priority_int
    
    @property
    def epics(self) -> List[Epic]:
        """Get all epics in this increment."""
        return [child for child in self.children if isinstance(child, Epic)]
    
    @property
    def sub_epics(self) -> List[Feature]:
        """Get all sub-epics directly in this increment (not through epics)."""
        return [child for child in self.children if isinstance(child, Feature)]
    
    @property
    def features(self) -> List[Feature]:
        """Deprecated: Use sub_epics instead."""
        return self.sub_epics
    
    @property
    def stories(self) -> List[Story]:
        """Get all stories directly in this increment (not through epics/sub-epics)."""
        return [child for child in self.children if isinstance(child, Story)]
    
    @property
    def story_names(self) -> List[str]:
        """Get story names referenced by this increment (for JSON format)."""
        return self._story_names if hasattr(self, '_story_names') else []
    
    @story_names.setter
    def story_names(self, names: List[str]) -> None:
        """Set story names referenced by this increment (for JSON format)."""
        self._story_names = names
    
    def add_story(self, story: Story) -> None:
        """
        Add a story to this increment.
        Pushes down other stories and increases increment height if needed.
        Handles user placement if story has different users than previous stories.
        """
        # Calculate position below existing stories
        if self.stories:
            last_story = max(self.stories, key=lambda s: s.position.y if s.position else 0)
            if last_story.position and last_story.boundary:
                base_y = last_story.boundary.bottom
            else:
                base_y = 450  # Default starting Y
        else:
            base_y = 450  # Default starting Y
        
        # Check if story has different users than previous story
        if self.stories and self.stories[-1].users:
            last_users = set(self.stories[-1].users)
            story_users = set(story.users)
            has_different_users = story_users != last_users
        else:
            has_different_users = bool(story.users)
        
        # Add extra spacing if different users
        spacing = 60 if has_different_users else 55  # USER_LABEL_OFFSET or STORY_SPACING_Y
        
        from .story_io_position import Position
        story.position = Position(
            self.boundary.x + 10 if self.boundary else 10,
            base_y + spacing
        )
        
        # Add story to increment
        story.change_parent(self)
        
        # Update increment height if needed
        if story.position and story.boundary:
            story_bottom = story.boundary.bottom
            if self.boundary and story_bottom > self.boundary.bottom:
                self.boundary = Boundary(
                    self.boundary.x,
                    self.boundary.y,
                    self.boundary.width,
                    story_bottom - self.boundary.y + 20  # Add padding
                )
    
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize increment from external source."""
        result = {
            'name': self.name,
            'priority': self._priority_value,  # Preserve original format
            'epics': [e.synchronize() for e in self.epics],
            'sub_epics': [f.synchronize() for f in self.sub_epics]
        }
        # Include stories as names if available, otherwise as objects
        if hasattr(self, '_story_names') and self._story_names:
            result['stories'] = self._story_names
        else:
            result['stories'] = [s.synchronize() for s in self.stories]
        return result
    
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate synchronization report for this increment."""
        return {
            'increment': self.name,
            'priority': self._priority_value,  # Preserve original format
            'epics_count': len(self.epics),
            'sub_epics_count': len(self.sub_epics),
            'stories_count': len(self.story_names) if hasattr(self, '_story_names') else len(self.stories),
            'status': 'synchronized'
        }
    
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this increment with another component."""
        if not isinstance(other, Increment):
            return {'match': False, 'reason': 'Type mismatch'}
        
        return {
            'match': self.name == other.name and self._priority_int == other._priority_int,
            'name_match': self.name == other.name,
            'priority_match': self._priority_int == other._priority_int,
            'stories_count_match': len(self.story_names) == len(other.story_names) if hasattr(self, '_story_names') and hasattr(other, '_story_names') else len(self.stories) == len(other.stories)
        }
    
    def render(self) -> Dict[str, Any]:
        """Render increment to JSON representation."""
        result = {
            'name': self.name,
            'priority': self._priority_value,  # Preserve original format (string or int)
        }
        
        # Include additional metadata if present
        if hasattr(self, '_relative_size'):
            result['relative_size'] = self._relative_size
        if hasattr(self, '_approach'):
            result['approach'] = self._approach
        if hasattr(self, '_focus'):
            result['focus'] = self._focus
        
        # Include epics and features if present
        if self.epics:
            result['epics'] = [e.render() for e in self.epics]
        if self.sub_epics:
            result['sub_epics'] = [f.render() for f in self.sub_epics]
        
        # Include stories as names if available, otherwise as objects
        if hasattr(self, '_story_names') and self._story_names:
            result['stories'] = self._story_names
        elif self.stories:
            result['stories'] = [s.render() for s in self.stories]
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert increment to dictionary."""
        result = super().to_dict()
        result['type'] = 'increment'
        result['priority'] = self._priority_value  # Preserve original format
        result['epics'] = [e.to_dict() for e in self.epics]
        result['sub_epics'] = [f.to_dict() for f in self.sub_epics]
        # Include stories as names if available
        if hasattr(self, '_story_names') and self._story_names:
            result['stories'] = self._story_names
        else:
            result['stories'] = [s.to_dict() for s in self.stories]
        return result

