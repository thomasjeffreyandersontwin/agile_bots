"""
Position and Boundary Domain Types

Represent geometric positions and boundaries for story map components.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Position:
    """Represents a 2D position with x and y coordinates."""
    
    x: float
    y: float
    
    def __add__(self, other: 'Position') -> 'Position':
        """Add two positions component-wise."""
        return Position(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Position') -> 'Position':
        """Subtract two positions component-wise."""
        return Position(self.x - other.x, self.y - other.y)
    
    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5
    
    def is_within_tolerance(self, other: 'Position', tolerance: float) -> bool:
        """Check if this position is within tolerance of another."""
        return self.distance_to(other) <= tolerance


@dataclass(frozen=True)
class Boundary:
    """Represents a rectangular boundary with position and dimensions."""
    
    x: float
    y: float
    width: float
    height: float
    
    @property
    def position(self) -> Position:
        """Get the top-left position of this boundary."""
        return Position(self.x, self.y)
    
    @property
    def center(self) -> Position:
        """Get the center position of this boundary."""
        return Position(self.x + self.width / 2, self.y + self.height / 2)
    
    @property
    def right(self) -> float:
        """Get the right edge x coordinate."""
        return self.x + self.width
    
    @property
    def bottom(self) -> float:
        """Get the bottom edge y coordinate."""
        return self.y + self.height
    
    def contains_position(self, pos: Position) -> bool:
        """Check if a position is within this boundary."""
        return (self.x <= pos.x <= self.right and
                self.y <= pos.y <= self.bottom)
    
    def contains_boundary(self, other: 'Boundary') -> bool:
        """Check if another boundary is fully contained within this one."""
        return (self.x <= other.x and
                self.y <= other.y and
                self.right >= other.right and
                self.bottom >= other.bottom)
    
    def overlaps(self, other: 'Boundary') -> bool:
        """Check if this boundary overlaps with another."""
        return not (self.right < other.x or
                   other.right < self.x or
                   self.bottom < other.y or
                   other.bottom < self.y)
    
    def expand(self, padding: float) -> 'Boundary':
        """Create a new boundary expanded by padding on all sides."""
        return Boundary(
            x=self.x - padding,
            y=self.y - padding,
            width=self.width + 2 * padding,
            height=self.height + 2 * padding
        )
    
    def union(self, other: 'Boundary') -> 'Boundary':
        """Create a boundary that contains both this and another boundary."""
        min_x = min(self.x, other.x)
        min_y = min(self.y, other.y)
        max_right = max(self.right, other.right)
        max_bottom = max(self.bottom, other.bottom)
        
        return Boundary(
            x=min_x,
            y=min_y,
            width=max_right - min_x,
            height=max_bottom - min_y
        )

