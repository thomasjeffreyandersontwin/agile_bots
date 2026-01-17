"""
StoryIOComponent Base Class

Base class for all story map components with common properties and behaviors.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from dataclasses import dataclass, field
from .story_io_position import Position, Boundary


T = TypeVar('T', bound='StoryIOComponent')


@dataclass
class StoryIOComponent(ABC):
    """
    Base class for all story map components.
    
    Provides common functionality for hierarchy management, position tracking,
    synchronization, and rendering.
    """
    
    name: str
    sequential_order: Optional[float] = None
    position: Optional[Position] = None
    boundary: Optional[Boundary] = None
    flag: bool = False
    _parent: Optional['StoryIOComponent'] = field(default=None, repr=False)
    _children: List['StoryIOComponent'] = field(default_factory=list, repr=False)
    
    @property
    def parent(self) -> Optional['StoryIOComponent']:
        return self._parent
    
    @parent.setter
    def parent(self, value: Optional['StoryIOComponent']) -> None:
        """Set the parent component and update relationships."""
        # Remove from old parent if exists
        if self._parent is not None:
            self._parent._remove_child(self)
        
        # Set new parent
        self._parent = value
        
        # Add to new parent's children if exists
        if self._parent is not None:
            self._parent._add_child(self)
    
    def __post_init__(self):
        """Initialize component after dataclass initialization."""
        if self._parent:
            self._parent._add_child(self)
    
    def _add_child(self, child: 'StoryIOComponent') -> None:
        """Internal method to add a child component."""
        if child not in self._children:
            self._children.append(child)
            # Only set parent if it's not already set to avoid circular calls
            if child._parent != self:
                child._parent = self
    
    def _remove_child(self, child: 'StoryIOComponent') -> None:
        """Internal method to remove a child component."""
        if child in self._children:
            self._children.remove(child)
            if child._parent == self:
                child._parent = None
    
    @property
    def children(self) -> List['StoryIOComponent']:
        """Get all direct children of this component."""
        return list(self._children)
    
    def children_at_level(self, level: int) -> List['StoryIOComponent']:
        """Get all children at a specific depth level."""
        if level < 0:
            return []
        if level == 0:
            return [self]
        
        result = []
        for child in self._children:
            result.extend(child.children_at_level(level - 1))
        return result
    
    @property
    def leafs(self) -> List['StoryIOComponent']:
        """Get all leaf nodes (components with no children)."""
        if not self._children:
            return [self]
        
        result = []
        for child in self._children:
            result.extend(child.leafs)
        return result
    
    def determine_children(self, level: int) -> List['StoryIOComponent']:
        """Determine children at a specific level of the hierarchy."""
        return self.children_at_level(level)
    
    def search_for_all_children(self, query: str) -> List['StoryIOComponent']:
        """Search for all children matching a query string."""
        results = []
        query_lower = query.lower()
        
        if query_lower in self.name.lower():
            results.append(self)
        
        for child in self._children:
            results.extend(child.search_for_all_children(query))
        
        return results
    
    def move_before(self, target: 'StoryIOComponent') -> None:
        """
        Move this component before the target component.
        
        Both components must be at the same level in the hierarchy.
        Pushes other components at the same level to the right.
        """
        if not self._parent or self._parent != target._parent:
            raise ValueError("Components must have the same parent to reorder")
        
        if self == target:
            return
        
        parent = self._parent
        parent._remove_child(self)
        
        target_index = parent._children.index(target)
        parent._children.insert(target_index, self)
        
        # Update sequential orders
        self._reorder_siblings(parent._children)
    
    def change_parent(self, new_parent: 'StoryIOComponent', 
                     target: Optional['StoryIOComponent'] = None) -> None:
        """
        Change the parent of this component.
        
        Args:
            new_parent: The new parent component (must be one level higher)
            target: Optional target component to insert before
        """
        # Validate parent level (enforced by subclasses)
        if self._parent:
            self._parent._remove_child(self)
        
        self._parent = new_parent
        new_parent._add_child(self)
        
        if target:
            if target.parent != new_parent:
                raise ValueError("Target must be a child of new_parent")
            self.move_before(target)
        else:
            # Add to end and reorder
            self._reorder_siblings(new_parent._children)
    
    def _reorder_siblings(self, siblings: List['StoryIOComponent']) -> None:
        """Update sequential_order for sibling components."""
        for idx, sibling in enumerate(siblings, 1):
            sibling.sequential_order = float(idx)
    
    @abstractmethod
    def synchronize(self) -> Dict[str, Any]:
        """Synchronize component from external source (e.g., DrawIO file)."""
        pass
    
    @abstractmethod
    def synchronize_report(self) -> Dict[str, Any]:
        """Generate a synchronization report."""
        pass
    
    @abstractmethod
    def compare(self, other: 'StoryIOComponent') -> Dict[str, Any]:
        """Compare this component with another."""
        pass
    
    @abstractmethod
    def render(self) -> Any:
        """Render component to output format (XML, JSON, etc.)."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component to dictionary representation."""
        return {
            'name': self.name,
            'sequential_order': self.sequential_order,
            'position': {'x': self.position.x, 'y': self.position.y} if self.position else None,
            'boundary': {
                'x': self.boundary.x,
                'y': self.boundary.y,
                'width': self.boundary.width,
                'height': self.boundary.height
            } if self.boundary else None,
            'flag': self.flag,
            'children': [child.to_dict() for child in self._children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryIOComponent':
        """Create component from dictionary representation."""
        # Subclasses should override this
        raise NotImplementedError(f"{cls.__name__}.from_dict not implemented")

