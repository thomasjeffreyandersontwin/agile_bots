"""
Story Domain Component

Represents a story in the story map hierarchy.
"""

from typing import List, Dict, Any, Optional, Set, TYPE_CHECKING
from .story_io_component import StoryIOComponent
from .story_io_position import Position

if TYPE_CHECKING:
    from .story_io_user import User


class Story(StoryIOComponent):
    """Represents a story with associated users."""
    
    def __init__(self, name: str, sequential_order: Optional[float] = None,
                 position: Optional[Position] = None, boundary: Optional[Any] = None,
                 flag: bool = False, parent: Optional[StoryIOComponent] = None,
                 users: Optional[List[str]] = None, steps: Optional[List[Dict[str, Any]]] = None,
                 vertical_order: Optional[int] = None, story_type: Optional[str] = None,
                 connector: Optional[str] = None):
        super().__init__(name, sequential_order, position, boundary, flag, parent)
        self._user_names = set(users or [])
        self._steps = steps or []
        self._vertical_order = vertical_order
        self._story_type = story_type  # 'user' (default), 'system', or 'technical'
        self._connector = connector  # 'and', 'or', 'opt', or None (default 'and')
        self._user_components: List['User'] = []
    
    @property
    def users(self) -> List[str]:
        """Get list of user names associated with this story."""
        return list(self._user_names)
    
    @property
    def user_components(self) -> List['User']:
        """Get user component objects associated with this story."""
        from .story_io_user import User
        return [c for c in self._user_components if isinstance(c, User)]
    
    @property
    def steps(self) -> List[Dict[str, Any]]:
        """Get acceptance criteria steps for this story."""
        return list(self._steps)
    
    @property
    def vertical_order(self) -> Optional[int]:
        """Get vertical ordering for stacked stories."""
        return self._vertical_order
    
    @property
    def story_type(self) -> str:
        """Get story type: 'user' (default), 'system', or 'technical'."""
        return self._story_type or 'user'
    
    def make_optional_to(self, target: 'Story') -> None:
        """
        Move this story below target story (for optional/alternative stories).
        Sets sequential_order to be a decimal of target's order.
        """
        if target.sequential_order is None:
            target.sequential_order = 1.0
        
        # Calculate decimal sequential order
        base_order = int(target.sequential_order)
        
        # Find all stories with same base order to determine next decimal
        parent = target.parent
        if parent:
            siblings = [s for s in parent.children if isinstance(s, Story)]
            same_base = [s for s in siblings 
                        if s.sequential_order and int(s.sequential_order) == base_order]
            
            if same_base:
                max_decimal = max([s.sequential_order - base_order 
                                  for s in same_base if s.sequential_order and s.sequential_order != base_order],
                                 default=0.0)
                self.sequential_order = base_order + max_decimal + 0.1
            else:
                self.sequential_order = base_order + 0.1
        
        # Move position below target
        if target.position and target.boundary:
            self.position = Position(
                target.position.x,
                target.boundary.bottom + 55  # STORY_SPACING_Y
            )
    
    def add_user(self, user: str) -> None:
        """
        Add a user to this story.
        Places user above story and pushes stories and users below down.
        """
        if user not in self._user_names:
            self._user_names.add(user)
            
            # Update position of story to make room for user above
            if self.position:
                self.position = Position(
                    self.position.x,
                    self.position.y + 60  # USER_LABEL_OFFSET
                )
    
    def remove_user(self, user: str) -> None:
        """Remove a user from this story."""
        if user in self._user_names:
            self._user_names.remove(user)
            
            # Update position if user was removed
            if self.position:
                self.position = Position(
                    self.position.x,
                    max(350, self.position.y - 60)  # STORY_START_Y minimum
                )
    
    def flag_story(self) -> None:
        """Flag this story (changes color in rendering)."""
        self.flag = True
    
    def unflag_story(self) -> None:
        """Unflag this story."""
        self.flag = False
    
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize story from external source (new format: acceptance_criteria, connector, nested stories)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'users': list(self._user_names),
            'story_type': self._story_type or 'user'
        }
        
        # Add connector (only include if not None - 'and' is the default)
        if self._connector is not None:
            result['connector'] = self._connector
        
        # Convert Steps to acceptance_criteria (new format)
        if self._steps:
            result['acceptance_criteria'] = [
                {
                    'description': step.get('description', ''),
                    'sequential_order': step.get('sequential_order', i + 1),
                    'connector': step.get('connector'),  # May be None
                    'user': step.get('user', '')
                }
                for i, step in enumerate(self._steps)
            ]
        else:
            result['acceptance_criteria'] = []
        
        # Handle nested stories (new format)
        nested_stories = [child for child in self.children if isinstance(child, Story)]
        if nested_stories:
            result['stories'] = [s.synchronize() for s in nested_stories]
        
        # Legacy format: steps (for backward compatibility)
        if self._steps:
            result['steps'] = self._steps
        if self._vertical_order is not None:
            result['vertical_order'] = self._vertical_order
        
        return result
    
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate synchronization report for this story."""
        return {
            'story': self.name,
            'users_count': len(self._user_names),
            'has_steps': len(self._steps) > 0,
            'status': 'synchronized'
        }
    
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this story with another component."""
        if not isinstance(other, Story):
            return {'match': False, 'reason': 'Type mismatch'}
        
        return {
            'match': self.name == other.name,
            'name_match': self.name == other.name,
            'users_match': self._user_names == other._user_names,
            'sequential_order_match': self.sequential_order == other.sequential_order
        }
    
    def render(self) -> Dict[str, Any]:
        """Render story to JSON representation (new format: acceptance_criteria, connector, nested stories)."""
        result = {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'users': list(self._user_names),
            'story_type': self._story_type or 'user'
        }
        
        # Add connector (only include if not None - 'and' is the default)
        if self._connector is not None:
            result['connector'] = self._connector
        
        # Convert Steps to acceptance_criteria (new format)
        if self._steps:
            result['acceptance_criteria'] = [
                {
                    'description': step.get('description', ''),
                    'sequential_order': step.get('sequential_order', i + 1),
                    'connector': step.get('connector'),  # May be None
                    'user': step.get('user', '')
                }
                for i, step in enumerate(self._steps)
            ]
        else:
            result['acceptance_criteria'] = []
        
        # Handle nested stories (new format)
        nested_stories = [child for child in self.children if isinstance(child, Story)]
        if nested_stories:
            result['stories'] = [s.render() for s in nested_stories]
        
        # Legacy format: Steps (for backward compatibility)
        if self._steps:
            result['Steps'] = self._steps
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert story to dictionary."""
        result = super().to_dict()
        result['type'] = 'story'
        result['users'] = list(self._user_names)
        if self._steps:
            result['Steps'] = self._steps
        if self._vertical_order:
            result['vertical_order'] = self._vertical_order
        if self._story_type and self._story_type != 'user':
            result['story_type'] = self._story_type
        return result

