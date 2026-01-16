"""
Tests for StoryIOComponent

Tests for the base StoryIOComponent class.
"""

import pytest
from pathlib import Path

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_component import StoryIOComponent
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_position import Position, Boundary


class TestComponent(StoryIOComponent):
    """Test implementation of StoryIOComponent for testing."""
    
    def synchronize(self):
        return {'name': self.name}
    
    def synchronize_report(self):
        return {'status': 'test'}
    
    def compare(self, other):
        return {'match': self.name == other.name}
    
    def render(self):
        return {'name': self.name}


class TestStoryIOComponent:
    """Tests for StoryIOComponent."""
    
    class TestNewlyCreated:
        """Tests for newly created components."""
        
        def test_should_have_the_specified_name(self):
            component = TestComponent(name='Test Component')
            assert component.name == 'Test Component'
        
        def test_should_have_no_parent(self):
            component = TestComponent(name='Test Component')
            assert component.parent is None
        
        def test_should_have_no_children(self):
            component = TestComponent(name='Test Component')
            assert component.children == []
        
        def test_should_not_be_flagged(self):
            component = TestComponent(name='Test Component')
            assert component.flag is False
    
    class TestWithPosition:
        """Tests for components with position."""
        
        def test_should_store_the_position(self):
            position = Position(x=10.0, y=20.0)
            component = TestComponent(name='Test', position=position)
            assert component.position.x == 10.0
            assert component.position.y == 20.0
    
    class TestWithChildren:
        """Tests for components with children."""
        
        def test_should_add_child_when_child_parent_is_set(self):
            parent = TestComponent(name='Parent')
            child1 = TestComponent(name='Child 1')
            child1.parent = parent
            assert parent.children == [child1]
        
        def test_should_have_multiple_children(self):
            parent = TestComponent(name='Parent')
            child1 = TestComponent(name='Child 1')
            child2 = TestComponent(name='Child 2')
            child1.parent = parent
            child2.parent = parent
            assert len(parent.children) == 2
        
        def test_should_set_child_parent_when_adding_child(self):
            parent = TestComponent(name='Parent')
            child1 = TestComponent(name='Child 1')
            child1.parent = parent
            assert child1.parent == parent
    
    class TestSearchingForChildren:
        """Tests for searching children."""
        
        def test_should_find_children_matching_query(self):
            parent = TestComponent(name='Parent Component')
            child1 = TestComponent(name='Child Alpha')
            child2 = TestComponent(name='Child Beta')
            child1.parent = parent
            child2.parent = parent
            results = parent.search_for_all_children('Alpha')
            assert len(results) == 1
            assert results[0].name == 'Child Alpha'
        
        def test_should_find_parent_when_query_matches(self):
            parent = TestComponent(name='Parent Component')
            child1 = TestComponent(name='Child Alpha')
            child2 = TestComponent(name='Child Beta')
            child1.parent = parent
            child2.parent = parent
            results = parent.search_for_all_children('Parent')
            assert len(results) == 1
            assert results[0].name == 'Parent Component'
        
        def test_should_perform_case_insensitive_search(self):
            parent = TestComponent(name='Parent Component')
            child1 = TestComponent(name='Child Alpha')
            child2 = TestComponent(name='Child Beta')
            child1.parent = parent
            child2.parent = parent
            results = parent.search_for_all_children('beta')
            assert len(results) == 1
            assert results[0].name == 'Child Beta'
    
    class TestLeafComponents:
        """Tests for leaf components."""
        
        def test_should_return_only_leaf_nodes(self):
            root = TestComponent(name='Root')
            child1 = TestComponent(name='Child 1')
            child2 = TestComponent(name='Child 2')
            grandchild = TestComponent(name='Grandchild')
            child1.parent = root
            child2.parent = root
            grandchild.parent = child1
            leafs = root.leafs
            assert len(leafs) == 2
            assert leafs[0].name == 'Grandchild'
            assert leafs[1].name == 'Child 2'
    
    class TestReorderingSiblings:
        """Tests for reordering siblings."""
        
        def test_should_move_component_before_target(self):
            parent = TestComponent(name='Parent')
            child1 = TestComponent(name='Child 1')
            child2 = TestComponent(name='Child 2')
            child3 = TestComponent(name='Child 3')
            child1.parent = parent
            child2.parent = parent
            child3.parent = parent
            child3.move_before(child2)
            children = parent.children
            assert children[0].name == 'Child 1'
            assert children[1].name == 'Child 3'
            assert children[2].name == 'Child 2'
        
        def test_should_raise_error_when_moving_components_with_different_parents(self):
            parent = TestComponent(name='Parent')
            child1 = TestComponent(name='Child 1')
            child1.parent = parent
            other_parent = TestComponent(name='Other Parent')
            other_child = TestComponent(name='Other Child')
            other_child.parent = other_parent
            with pytest.raises(ValueError):
                child1.move_before(other_child)
    
    class TestChangingParent:
        """Tests for changing parent."""
        
        def test_should_move_child_to_new_parent(self):
            old_parent = TestComponent(name='Old Parent')
            new_parent = TestComponent(name='New Parent')
            child = TestComponent(name='Child')
            child.parent = old_parent
            child.change_parent(new_parent)
            assert child.parent == new_parent
            assert len(new_parent.children) == 1
        
        def test_should_remove_child_from_old_parent(self):
            old_parent = TestComponent(name='Old Parent')
            new_parent = TestComponent(name='New Parent')
            child = TestComponent(name='Child')
            child.parent = old_parent
            child.change_parent(new_parent)
            assert len(old_parent.children) == 0
    
    class TestConvertingToDictionary:
        """Tests for converting to dictionary."""
        
        def test_should_include_name_in_dictionary(self):
            component = TestComponent(name='Test Component', sequential_order=1.0)
            result = component.to_dict()
            assert result['name'] == 'Test Component'
        
        def test_should_include_sequential_order_in_dictionary(self):
            component = TestComponent(name='Test Component', sequential_order=1.0)
            result = component.to_dict()
            assert result['sequential_order'] == 1.0
        
        def test_should_include_children_in_dictionary(self):
            component = TestComponent(name='Test Component', sequential_order=1.0)
            child = TestComponent(name='Child')
            child.parent = component
            result = component.to_dict()
            assert len(result['children']) == 1
    
    class TestDeterminingChildrenAtLevel:
        """Tests for determining children at level."""
        
        def test_should_return_self_at_level_0(self):
            root = TestComponent(name='Root')
            results = root.children_at_level(0)
            assert len(results) == 1
            assert results[0].name == 'Root'
        
        def test_should_return_direct_children_at_level_1(self):
            root = TestComponent(name='Root')
            child1 = TestComponent(name='Child 1')
            child2 = TestComponent(name='Child 2')
            child1.parent = root
            child2.parent = root
            results = root.children_at_level(1)
            assert len(results) == 2
        
        def test_should_return_grandchildren_at_level_2(self):
            root = TestComponent(name='Root')
            child1 = TestComponent(name='Child 1')
            child2 = TestComponent(name='Child 2')
            grandchild = TestComponent(name='Grandchild')
            child1.parent = root
            child2.parent = root
            grandchild.parent = child1
            results = root.children_at_level(2)
            assert len(results) == 1
            assert results[0].name == 'Grandchild'
    
    class TestDeterminingChildren:
        """Tests for determining children."""
        
        def test_should_return_children_at_specified_level(self):
            root = TestComponent(name='Root')
            child = TestComponent(name='Child')
            child.parent = root
            results = root.determine_children(1)
            assert len(results) == 1
            assert results[0].name == 'Child'
