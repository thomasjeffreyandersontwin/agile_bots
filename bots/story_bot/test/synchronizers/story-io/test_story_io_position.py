"""
BDD Tests for Position and Boundary

Tests for geometric position and boundary domain types.
"""

from mamba import description, context, it, before
from expects import expect, equal, be_true, be_false

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_position import Position, Boundary


def create_position(x=0.0, y=0.0):
    """Helper factory for creating positions."""
    return Position(x=x, y=y)


def create_boundary(x=0.0, y=0.0, width=100.0, height=50.0):
    """Helper factory for creating boundaries."""
    return Boundary(x=x, y=y, width=width, height=height)


with description('a Position'):
    with context('that is created'):
        with it('should have x and y coordinates'):
            pos = create_position(x=10.0, y=20.0)
            expect(pos.x).to(equal(10.0))
            expect(pos.y).to(equal(20.0))
        
        with it('should be immutable'):
            pos = create_position(x=5.0, y=10.0)
            expect(pos.x).to(equal(5.0))
    
    with context('that calculates distance'):
        with before.each:
            self.pos1 = create_position(x=0.0, y=0.0)
            self.pos2 = create_position(x=3.0, y=4.0)
        
        with it('should calculate Euclidean distance correctly'):
            distance = self.pos1.distance_to(self.pos2)
            expect(distance).to(equal(5.0))
        
        with it('should return zero distance to itself'):
            distance = self.pos1.distance_to(self.pos1)
            expect(distance).to(equal(0.0))
    
    with context('that checks tolerance'):
        with before.each:
            self.pos1 = create_position(x=10.0, y=10.0)
            self.pos2 = create_position(x=12.0, y=10.0)
        
        with it('should return true when within tolerance'):
            result = self.pos1.is_within_tolerance(self.pos2, tolerance=3.0)
            expect(result).to(be_true)
        
        with it('should return false when outside tolerance'):
            result = self.pos1.is_within_tolerance(self.pos2, tolerance=1.0)
            expect(result).to(be_false)
    
    with context('that performs arithmetic'):
        with before.each:
            self.pos1 = create_position(x=5.0, y=10.0)
            self.pos2 = create_position(x=2.0, y=3.0)
        
        with it('should add positions component-wise'):
            result = self.pos1 + self.pos2
            expect(result.x).to(equal(7.0))
            expect(result.y).to(equal(13.0))
        
        with it('should subtract positions component-wise'):
            result = self.pos1 - self.pos2
            expect(result.x).to(equal(3.0))
            expect(result.y).to(equal(7.0))


with description('a Boundary'):
    with context('that is created'):
        with it('should have position and dimensions'):
            boundary = create_boundary(x=10.0, y=20.0, width=100.0, height=50.0)
            expect(boundary.x).to(equal(10.0))
            expect(boundary.y).to(equal(20.0))
            expect(boundary.width).to(equal(100.0))
            expect(boundary.height).to(equal(50.0))
        
        with it('should be immutable'):
            boundary = create_boundary()
            expect(boundary.width).to(equal(100.0))
    
    with context('that calculates properties'):
        with before.each:
            self.boundary = create_boundary(x=10.0, y=20.0, width=100.0, height=50.0)
        
        with it('should return top-left position'):
            pos = self.boundary.position
            expect(pos.x).to(equal(10.0))
            expect(pos.y).to(equal(20.0))
        
        with it('should calculate center position'):
            center = self.boundary.center
            expect(center.x).to(equal(60.0))
            expect(center.y).to(equal(45.0))
        
        with it('should return right edge x coordinate'):
            expect(self.boundary.right).to(equal(110.0))
        
        with it('should return bottom edge y coordinate'):
            expect(self.boundary.bottom).to(equal(70.0))
    
    with context('that checks containment'):
        with before.each:
            self.boundary = create_boundary(x=10.0, y=20.0, width=100.0, height=50.0)
        
        with it('should contain position inside'):
            pos = create_position(x=50.0, y=40.0)
            expect(self.boundary.contains_position(pos)).to(be_true)
        
        with it('should not contain position outside'):
            pos = create_position(x=150.0, y=100.0)
            expect(self.boundary.contains_position(pos)).to(be_false)
        
        with it('should contain position on edge'):
            pos = create_position(x=10.0, y=20.0)
            expect(self.boundary.contains_position(pos)).to(be_true)
    
    with context('that checks boundary containment'):
        with before.each:
            self.outer = create_boundary(x=0.0, y=0.0, width=200.0, height=200.0)
            self.inner = create_boundary(x=50.0, y=50.0, width=50.0, height=50.0)
            self.overlapping = create_boundary(x=150.0, y=150.0, width=100.0, height=100.0)
        
        with it('should contain smaller boundary inside'):
            expect(self.outer.contains_boundary(self.inner)).to(be_true)
        
        with it('should not contain overlapping boundary'):
            expect(self.outer.contains_boundary(self.overlapping)).to(be_false)
    
    with context('that checks overlap'):
        with before.each:
            self.boundary1 = create_boundary(x=0.0, y=0.0, width=100.0, height=100.0)
            self.boundary2 = create_boundary(x=50.0, y=50.0, width=100.0, height=100.0)
            self.boundary3 = create_boundary(x=200.0, y=200.0, width=100.0, height=100.0)
        
        with it('should detect overlapping boundaries'):
            expect(self.boundary1.overlaps(self.boundary2)).to(be_true)
        
        with it('should detect non-overlapping boundaries'):
            expect(self.boundary1.overlaps(self.boundary3)).to(be_false)
    
    with context('that expands'):
        with before.each:
            self.boundary = create_boundary(x=10.0, y=20.0, width=100.0, height=50.0)
        
        with it('should expand by padding on all sides'):
            expanded = self.boundary.expand(padding=5.0)
            expect(expanded.x).to(equal(5.0))
            expect(expanded.y).to(equal(15.0))
            expect(expanded.width).to(equal(110.0))
            expect(expanded.height).to(equal(60.0))
    
    with context('that creates union'):
        with before.each:
            self.boundary1 = create_boundary(x=0.0, y=0.0, width=100.0, height=100.0)
            self.boundary2 = create_boundary(x=50.0, y=50.0, width=100.0, height=100.0)
        
        with it('should create boundary containing both'):
            union = self.boundary1.union(self.boundary2)
            expect(union.x).to(equal(0.0))
            expect(union.y).to(equal(0.0))
            expect(union.width).to(equal(150.0))
            expect(union.height).to(equal(150.0))

