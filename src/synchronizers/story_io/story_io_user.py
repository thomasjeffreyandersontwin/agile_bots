"""
User Domain Component

Represents a user in the story map hierarchy.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .story_io_component import StoryIOComponent

if TYPE_CHECKING:
    from .story_io_story import Story


class User(StoryIOComponent):
    """Represents a user associated with stories."""
    
    def __init__(self, name: str, position: Optional[Any] = None,
                 boundary: Optional[Any] = None, flag: bool = False,
                 parent: Optional[StoryIOComponent] = None):
        super().__init__(name, None, position, boundary, flag, parent)
        self._story_refs: List['Story'] = []
    
    @property
    def stories(self) -> List['Story']:
        """Get all stories associated with this user."""
        from .story_io_story import Story
        return [s for s in self._story_refs if isinstance(s, Story)]
    
    def add_story(self, story: 'Story') -> None:
        """
        Add a story to this user.
        Same as story.add_user(user) - creates bidirectional relationship.
        """
        if story not in self._story_refs:
            self._story_refs.append(story)
            story.add_user(self.name)
    
    def remove_story(self, story: 'Story') -> None:
        """Remove a story from this user."""
        if story in self._story_refs:
            self._story_refs.remove(story)
            story.remove_user(self.name)
    
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize user from external source."""
        return {
            'name': self.name,
            'stories': [s.name for s in self._story_refs]
        }
    
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate synchronization report for this user."""
        return {
            'user': self.name,
            'stories_count': len(self._story_refs),
            'status': 'synchronized'
        }
    
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this user with another component."""
        if not isinstance(other, User):
            return {'match': False, 'reason': 'Type mismatch'}
        
        return {
            'match': self.name == other.name,
            'name_match': self.name == other.name,
            'stories_count_match': len(self._story_refs) == len(other._story_refs)
        }
    
    def render(self) -> Dict[str, Any]:
        """Render user to JSON representation."""
        return {
            'name': self.name,
            'stories': [s.name for s in self._story_refs]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        result = super().to_dict()
        result['type'] = 'user'
        result['stories'] = [s.name for s in self._story_refs]
        return result

