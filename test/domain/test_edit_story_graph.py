"""
Test Edit Story Graph

Tests for editing story graph hierarchy including node creation, deletion, and validation.

Sub-Epic: Edit Story Graph
Stories: Create Epic, Create Child Story Node, Delete Story Node, Update Story Node Name, Move Story Node
"""
import re
import pytest
from domain.bot_test_helper import BotTestHelper
# SUB-EPIC: Edit Story Graph
# ================================================================================

class TestCreateEpic:
    """Tests for creating Epic nodes at root level of Story Map."""
    
    def test_create_epic_with_name_at_default_position(self, tmp_path):
        """
        SCENARIO: Create Epic with name at default position
        GIVEN: Story Map is initialized
        WHEN: Story Map creates Epic with name
        THEN: Epic is added at last position
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['Epic A', 'Epic B'])
        
        story_map = helper.story.bot.story_graph
        new_epic = story_map.create_epic(name='User Management')
        
        assert new_epic.name == 'User Management'
        epics_list = list(story_map.epics)
        assert len(epics_list) == 3
        assert story_map.epics['User Management'] == new_epic
    
    def test_create_epic_with_position_specified(self, tmp_path):
        """
        SCENARIO: Create Epic with position specified
        GIVEN: Story Map has existing Epics
        WHEN: Story Map creates Epic at specific position
        THEN: Epic is inserted at position and existing Epics shift
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['Epic A', 'Epic B', 'Epic C'])
        
        story_map = helper.story.bot.story_graph
        new_epic = story_map.create_epic(name='User Management', position=1)
        
        assert new_epic.name == 'User Management'
        epics_list = list(story_map.epics)
        assert len(epics_list) == 4
        assert epics_list[1].name == 'User Management'
        assert epics_list[0].name == 'Epic A'
        assert epics_list[2].name == 'Epic B'
        assert epics_list[3].name == 'Epic C'
    
    def test_create_epic_with_invalid_position_adjusts(self, tmp_path):
        """
        SCENARIO: Create Epic with invalid position adjusts to last
        GIVEN: Story Map has 2 Epics
        WHEN: Story Map creates Epic at position 99
        THEN: Position is adjusted to last (position 2)
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['Epic A', 'Epic B'])
        
        story_map = helper.story.bot.story_graph
        new_epic = story_map.create_epic(name='User Management', position=99)
        
        assert new_epic.name == 'User Management'
        epics_list = list(story_map.epics)
        assert len(epics_list) == 3
        assert epics_list[2].name == 'User Management'
    
    def test_create_epic_without_name_generates_unique_name(self, tmp_path):
        """
        SCENARIO: Create Epic without name generates unique name
        GIVEN: Story Map has existing Epics
        WHEN: Story Map creates Epic without name
        THEN: System generates unique name (Epic1, Epic2, etc.)
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['User Management', 'Reporting'])
        
        story_map = helper.story.bot.story_graph
        
        # Create first Epic with auto-generated name
        epic1 = story_map.create_epic()
        assert epic1.name == 'Epic1'
        
        # Create second Epic with auto-generated name
        epic2 = story_map.create_epic()
        assert epic2.name == 'Epic2'
        
        # Create third Epic with auto-generated name
        epic3 = story_map.create_epic()
        assert epic3.name == 'Epic3'
    
    def test_create_epic_with_duplicate_name_returns_error(self, tmp_path):
        """
        SCENARIO: Create Epic with duplicate name returns error
        GIVEN: Story Map has Epic "User Management"
        WHEN: Story Map attempts to create Epic with duplicate name
        THEN: System identifies duplicate and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['User Management', 'Reporting'])
        
        story_map = helper.story.bot.story_graph
        
        with pytest.raises(ValueError, match="Epic with name 'User Management' already exists"):
            story_map.create_epic(name='User Management')
    
    def test_create_epic_updates_epics_collection(self, tmp_path):
        """
        SCENARIO: Create Epic updates epics collection
        GIVEN: Story Map has existing Epics
        WHEN: Story Map creates new Epic
        THEN: Epics collection is updated and new Epic is accessible
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['Epic A'])
        
        story_map = helper.story.bot.story_graph
        new_epic = story_map.create_epic(name='User Management')
        
        # Verify accessible through epics collection
        assert story_map.epics['User Management'] == new_epic
        assert len(list(story_map.epics)) == 2
    
    def test_create_epic_updates_story_graph_dict(self, tmp_path):
        """
        SCENARIO: Create Epic updates underlying story_graph dict
        GIVEN: Story Map has existing Epics
        WHEN: Story Map creates new Epic
        THEN: story_graph dict is updated with new Epic
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['Epic A'])
        
        story_map = helper.story.bot.story_graph
        story_map.create_epic(name='User Management')
        
        # Verify story_graph dict updated (public property)
        assert len(story_map.story_graph['epics']) == 2
        assert story_map.story_graph['epics'][1]['name'] == 'User Management'
    
    def test_create_multiple_epics_in_sequence(self, tmp_path):
        """
        SCENARIO: Create multiple Epics in sequence
        GIVEN: Story Map is initialized
        WHEN: Story Map creates multiple Epics
        THEN: All Epics are added in correct order
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_empty()
        
        story_map = helper.story.bot.story_graph
        
        epic1 = story_map.create_epic(name='Invoke Bot')
        epic2 = story_map.create_epic(name='User Management')
        epic3 = story_map.create_epic(name='Reporting')
        
        epics_list = list(story_map.epics)
        assert len(epics_list) == 3
        assert epics_list[0].name == 'Invoke Bot'
        assert epics_list[1].name == 'User Management'
        assert epics_list[2].name == 'Reporting'
    
    def test_create_epic_at_beginning_position(self, tmp_path):
        """
        SCENARIO: Create Epic at beginning (position 0)
        GIVEN: Story Map has existing Epics
        WHEN: Story Map creates Epic at position 0
        THEN: Epic is inserted at beginning
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_map_with_epics(['Epic A', 'Epic B'])
        
        story_map = helper.story.bot.story_graph
        new_epic = story_map.create_epic(name='User Management', position=0)
        
        epics_list = list(story_map.epics)
        assert epics_list[0].name == 'User Management'
        assert epics_list[1].name == 'Epic A'
        assert epics_list[2].name == 'Epic B'


class TestCreateChildStoryNode:
    """Tests for creating child story nodes at all hierarchy levels."""
    # Scenario: Create child node at any hierarchy level with default position
    
    @pytest.mark.parametrize('parent_type,parent_name,existing_count,child_type,child_name,expected_position,total_children', [
        ('Epic', 'User Management', 0, 'SubEpic', 'Authentication', 0, 1),
        ('Epic', 'User Management', 2, 'SubEpic', 'Authorization', 2, 3),
        ('SubEpic', 'Authentication', 0, 'SubEpic', 'Login Flow', 0, 1),
        ('SubEpic', 'Login Flow', 1, 'Story', 'Validate Password', 1, 2),
        ('Story', 'Validate Password', 0, 'Scenario', 'Valid Password Entered', 0, 1),
        ('Story', 'Validate Password', 2, 'Scenario', 'Invalid Password Entered', 2, 3),
    ])
    def test_create_child_node_at_hierarchy_level(self, tmp_path, parent_type, parent_name, existing_count, child_type, child_name, expected_position, total_children):
        """
        SCENARIO: Create child node at any hierarchy level with default position
        GIVEN: Story Graph has parent node with existing children
        WHEN: Parent creates child node of specified type
        THEN: Child is added at last position with correct total count
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_parent_and_children(
            parent_type, parent_name, existing_count, child_type
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        elif parent_type == 'SubEpic':
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        else:
            parent = helper.story.find_story_in_story_graph(parent_name)
        
        new_child = parent.create_child(name=child_name, child_type=child_type)
        
        assert new_child.name == child_name
        helper.story.assert_child_created_at_position(parent, child_name, expected_position, total_children)
    # Scenario: Create child node with specified position
    
    @pytest.mark.parametrize('parent_type,parent_name,existing_children,new_child_name,target_position,final_order', [
        ('Epic', 'User Management', 'SubEpic A, SubEpic B', 'SubEpic C', 0, 'SubEpic C, SubEpic A, SubEpic B'),
        ('Epic', 'User Management', 'SubEpic A, SubEpic B', 'SubEpic C', 1, 'SubEpic A, SubEpic C, SubEpic B'),
        ('SubEpic', 'Authentication', 'Story A, Story B, Story C', 'Story D', 2, 'Story A, Story B, Story D, Story C'),
    ])
    def test_create_child_node_with_position(self, tmp_path, parent_type, parent_name, existing_children, new_child_name, target_position, final_order):
        """
        SCENARIO: Create child node with specified position
        GIVEN: Story Graph has parent node with existing children
        WHEN: Parent creates child node at specific position
        THEN: Child is inserted at position and existing children shift
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_named_children(
            parent_type, parent_name, existing_children
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        elif parent_type == 'SubEpic':
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        else:
            parent = helper.story.find_story_in_story_graph(parent_name)
        
        new_child = parent.create_child(name=new_child_name, position=target_position)
        
        helper.story.assert_children_in_order(parent, final_order)
        helper.story.assert_child_at_position(parent, new_child_name, target_position)
    # Scenario: Create child node with invalid position adjusts to last position
    
    @pytest.mark.parametrize('parent_type,parent_name,child_count,child_name,invalid_position,adjusted_position,total_children', [
        ('Epic', 'User Management', 3, 'New SubEpic', 99, 3, 4),
        ('Epic', 'User Management', 0, 'First SubEpic', 5, 0, 1),
        ('SubEpic', 'Authentication', 2, 'New Story', 10, 2, 3),
    ])
    def test_create_child_invalid_position_adjusts(self, tmp_path, parent_type, parent_name, child_count, child_name, invalid_position, adjusted_position, total_children):
        """
        SCENARIO: Create child node with invalid position adjusts to last position
        GIVEN: Story Graph has parent node with existing children
        WHEN: Parent creates child node at invalid position (exceeds child count)
        THEN: System adjusts position to last valid position
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_parent_and_children(
            parent_type, parent_name, child_count, 'SubEpic'
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        elif parent_type == 'SubEpic':
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        else:
            parent = helper.story.find_story_in_story_graph(parent_name)
        
        new_child = parent.create_child(name=child_name, position=invalid_position)
        
        helper.story.assert_child_at_position(parent, child_name, adjusted_position)
        helper.story.assert_parent_child_count(parent, total_children)
    # Scenario: Create child node with duplicate name returns error
    
    @pytest.mark.parametrize('parent_type,parent_name,child_type,existing_child_name,duplicate_name', [
        ('Epic', 'User Management', 'SubEpic', 'Authentication', 'Authentication'),
        ('SubEpic', 'Authentication', 'Story', 'Login Form', 'Login Form'),
        ('Story', 'Validate Password', 'Scenario', 'Valid Password', 'Valid Password'),
    ])
    def test_create_child_with_duplicate_name_returns_error(self, tmp_path, parent_type, parent_name, child_type, existing_child_name, duplicate_name):
        """
        SCENARIO: Create child node with duplicate name returns error
        GIVEN: Story Graph has parent node with existing child
        WHEN: Parent attempts to create child with duplicate name
        THEN: System identifies duplicate and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_existing_child(
            parent_type, parent_name, existing_child_name, child_type
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        elif parent_type == 'SubEpic':
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        else:
            parent = helper.story.find_story_in_story_graph(parent_name)
        
        with pytest.raises(ValueError, match=f"Child with name '{duplicate_name}' already exists"):
            parent.create_child(name=duplicate_name, child_type=child_type)
    # Scenario: Create child node without name generates unique name
    
    @pytest.mark.parametrize('parent_type,parent_name,existing_children,expected_generated_name', [
        ('Epic', 'User Management', '', 'Child1'),
        ('Epic', 'User Management', 'Child1', 'Child2'),
        ('Epic', 'User Management', 'Child1, Child2', 'Child3'),
        ('SubEpic', 'Authentication', 'Story1, Story2', 'Story3'),
    ])
    def test_create_child_without_name_generates_unique_name(self, tmp_path, parent_type, parent_name, existing_children, expected_generated_name):
        """
        SCENARIO: Create child node without name generates unique name
        GIVEN: Story Graph has parent node with existing children
        WHEN: Parent creates child without providing name
        THEN: System generates unique name (Child1, Child2, etc.)
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_named_children(
            parent_type, parent_name, existing_children
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        elif parent_type == 'SubEpic':
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        else:
            parent = helper.story.find_story_in_story_graph(parent_name)
        
        new_child = parent.create_child()
        
        helper.story.assert_node_added_to_parent(parent, expected_generated_name)
    # Scenario: SubEpic creates Story and auto-creates StoryGroup on first Story
    
    @pytest.mark.parametrize('subepic_name,existing_story_count,story_name,story_position', [
        ('Authentication', 0, 'Login Form', 0),
        ('Authentication', 1, 'Password Reset', 1),
        ('Authentication', 3, 'Two-Factor Auth', 3),
    ])
    def test_subepic_creates_story_and_storygroup(self, tmp_path, subepic_name, existing_story_count, story_name, story_position):
        """
        SCENARIO: SubEpic creates Story and auto-creates StoryGroup on first Story
        GIVEN: SubEpic has existing Story count (0 or more)
        WHEN: SubEpic creates new Story
        THEN: StoryGroup is created (if first) or existing StoryGroup is used
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_subepic_with_existing_stories(
            subepic_name, existing_story_count
        )
        
        subepic = helper.story.find_subepic_in_story_graph(subepic_name)
        new_story = subepic.create_child(name=story_name, child_type='Story')
        helper.story.assert_story_is_in_storygroup_at_position(
            subepic_name, story_name, story_position
        )
        helper.story.assert_storygroup_exists(subepic_name)
    # Scenario: SubEpic with Stories cannot create SubEpic child
    
    @pytest.mark.parametrize('subepic_name,existing_story,new_subepic_name', [
        ('Authentication', 'Login Form', 'OAuth Flow'),
        ('User Profile', 'Edit Profile', 'Profile Settings'),
    ])
    def test_subepic_with_stories_cannot_create_subepic_child(self, tmp_path, subepic_name, existing_story, new_subepic_name):
        """
        SCENARIO: SubEpic with Stories cannot create SubEpic child
        GIVEN: SubEpic has existing Story children
        WHEN: SubEpic attempts to create SubEpic child
        THEN: System identifies hierarchy violation and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_subepic_with_existing_story(
            subepic_name, existing_story
        )
        
        subepic = helper.story.find_subepic_in_story_graph(subepic_name)
        
        with pytest.raises(ValueError, match="Cannot create SubEpic under SubEpic with Stories"):
            subepic.create_child(name=new_subepic_name, child_type='SubEpic')
    # Scenario: SubEpic with SubEpics cannot create Story child
    
    @pytest.mark.parametrize('subepic_name,existing_subepic,story_name', [
        ('User Management', 'Authentication', 'Login Form'),
        ('User Management', 'Authorization', 'Check Permissions'),
    ])
    def test_subepic_with_subepics_cannot_create_story_child(self, tmp_path, subepic_name, existing_subepic, story_name):
        """
        SCENARIO: SubEpic with SubEpics cannot create Story child
        GIVEN: SubEpic has existing SubEpic children
        WHEN: SubEpic attempts to create Story child
        THEN: System identifies hierarchy violation and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_subepic_with_existing_subepic(
            subepic_name, existing_subepic
        )
        
        subepic = helper.story.find_subepic_in_story_graph(subepic_name)
        
        with pytest.raises(ValueError, match="Cannot create Story under SubEpic with SubEpics"):
            subepic.create_child(name=story_name, child_type='Story')
    # Scenario: Story creates child and adds to correct collection
    
    @pytest.mark.parametrize('story_name,child_type,child_name,target_collection,excluded_collection', [
        ('Validate Password', 'Scenario', 'Valid Password Entered', 'scenarios', 'acceptance_criteria'),
        ('Validate Password', 'ScenarioOutline', 'Invalid Password Formats', 'scenario_outlines', 'acceptance_criteria'),
        ('Validate Password', 'AcceptanceCriteria', 'Password Must Not Be Empty', 'acceptance_criteria', 'scenarios'),
    ])
    def test_story_creates_child_in_correct_collection(self, tmp_path, story_name, child_type, child_name, target_collection, excluded_collection):
        """
        SCENARIO: Story creates child and adds to correct collection
        GIVEN: Story exists in story graph
        WHEN: Story creates child of specific type (Scenario, ScenarioOutline, AcceptanceCriteria)
        THEN: Child is added to correct collection and not to others
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_in_graph(story_name)
        
        story = helper.story.find_story_in_story_graph(story_name)
        new_child = story.create_child(name=child_name, child_type=child_type)
        helper.story.assert_child_is_in_collection(story_name, child_name, target_collection)
        helper.story.assert_child_is_not_in_collection(story_name, child_name, excluded_collection)


class TestDeleteStoryNode:
    """Tests for deleting story nodes from hierarchy."""
    # Scenario: Delete node without children
    
    @pytest.mark.parametrize('parent_type,parent_name,initial_children,node_name,node_position,child_count,remaining_children,final_count', [
        ('Epic', 'User Management', 'SubEpic A, SubEpic B, SubEpic C', 'SubEpic B', 1, 0, 'SubEpic A, SubEpic C', 2),
        ('SubEpic', 'Authentication', 'Story A, Story B', 'Story A', 0, 0, 'Story B', 1),
        ('Story', 'Login Form', 'Scenario A, Scenario B, Scenario C', 'Scenario C', 2, 0, 'Scenario A, Scenario B', 2),
    ])
    def test_delete_node_without_children(self, tmp_path, parent_type, parent_name, initial_children, node_name, node_position, child_count, remaining_children, final_count):
        """
        SCENARIO: Delete node without children
        GIVEN: Story Graph has parent node with children
        WHEN: Node with no children is deleted
        THEN: Node is removed and siblings are resequenced
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_named_children(
            parent_type, parent_name, initial_children
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        elif parent_type == 'SubEpic':
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        else:
            parent = helper.story.find_story_in_story_graph(parent_name)
        
        node = next(child for child in parent.children if child.name == node_name)
        node.delete()
        
        helper.story.assert_children_in_order(parent, remaining_children)
        helper.story.assert_parent_child_count(parent, final_count)
    # Scenario: Delete node with children promotes children to grandparent
    
    @pytest.mark.parametrize('grandparent_type,grandparent,node_name,node_children,initial_child_count,final_child_count', [
        ('Epic', 'User Management', 'Authentication', 'Login Flow, Password Reset', 3, 4),
        ('SubEpic', 'Authentication', 'OAuth Flow', 'Google Auth, GitHub Auth', 2, 3),
    ])
    def test_delete_node_with_children_promotes_children_to_grandparent(self, tmp_path, grandparent_type, grandparent, node_name, node_children, initial_child_count, final_child_count):
        """
        SCENARIO: Delete node with children promotes children to grandparent
        GIVEN: Node has children
        WHEN: Node is deleted
        THEN: Children are moved to grandparent as last children
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node_and_children(
            grandparent_type, grandparent, node_name, node_children, initial_child_count
        )
        
        if grandparent_type == 'Epic':
            grandparent_node = helper.story.bot.story_graph.epics[grandparent]
        else:
            grandparent_node = helper.story.find_subepic_in_story_graph(grandparent)
        
        node = next(child for child in grandparent_node.children if child.name == node_name)
        node.delete()
        
        helper.story.assert_children_promoted_to_grandparent(grandparent_node, node_children, final_child_count)
    # Scenario: Delete node including children (cascade delete)
    
    @pytest.mark.parametrize('parent_type,parent_name,initial_children,node_name,child_count,total_descendants,remaining_children,final_count', [
        ('Epic', 'User Management', 'SubEpic A, SubEpic B, SubEpic C, SubEpic D', 'SubEpic B', 2, 5, 'SubEpic A, SubEpic C, SubEpic D', 3),
        ('SubEpic', 'Authentication', 'SubEpic A, SubEpic B', 'SubEpic A', 3, 8, 'SubEpic B', 1),
    ])
    def test_delete_node_including_children_cascade_delete(self, tmp_path, parent_type, parent_name, initial_children, node_name, child_count, total_descendants, remaining_children, final_count):
        """
        SCENARIO: Delete node including children (cascade delete)
        GIVEN: Node has descendants
        WHEN: Node is deleted with cascade option
        THEN: Node and all descendants are deleted
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_descendants(
            parent_type, parent_name, initial_children, node_name, child_count, total_descendants
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        else:
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        
        node = next(child for child in parent.children if child.name == node_name)
        node.delete(cascade=True)
        
        helper.story.assert_children_in_order(parent, remaining_children)
        helper.story.assert_parent_child_count(parent, final_count)
    # Scenario: Delete node at different positions verifies resequencing
    
    @pytest.mark.parametrize('parent_type,parent_name,initial_order,node_name,delete_position,final_order', [
        ('Epic', 'User Management', 'SubEpic A, SubEpic B, SubEpic C, SubEpic D', 'SubEpic A', 0, 'SubEpic B, SubEpic C, SubEpic D'),
        ('Epic', 'User Management', 'SubEpic A, SubEpic B, SubEpic C, SubEpic D', 'SubEpic C', 2, 'SubEpic A, SubEpic B, SubEpic D'),
        ('Epic', 'User Management', 'SubEpic A, SubEpic B, SubEpic C, SubEpic D', 'SubEpic D', 3, 'SubEpic A, SubEpic B, SubEpic C'),
    ])
    def test_delete_node_at_different_positions_verifies_resequencing(self, tmp_path, parent_type, parent_name, initial_order, node_name, delete_position, final_order):
        """
        SCENARIO: Delete node at different positions verifies resequencing
        GIVEN: Parent has children in order
        WHEN: Node at specific position is deleted
        THEN: Remaining children are resequenced properly
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_named_children(
            parent_type, parent_name, initial_order
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        else:
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        
        node = next(child for child in parent.children if child.name == node_name)
        node.delete()
        
        helper.story.assert_children_in_order(parent, final_order)
        helper.story.assert_children_have_sequential_positions(parent_name)


class TestUpdateStoryNodeName:
    """Tests for updating story node names."""
    # Scenario: Rename node with valid name across hierarchy levels
    
    @pytest.mark.parametrize('node_type,parent_name,old_name,new_name', [
        ('Epic', 'root', 'User Management', 'User Administration'),
        ('SubEpic', 'User Management', 'Authentication', 'User Authentication'),
        ('Story', 'Authentication', 'Login Form', 'User Login Form'),
        ('Scenario', 'Login Form', 'Valid Login', 'Successful User Login'),
    ])
    def test_rename_node_with_valid_name_across_hierarchy_levels(self, tmp_path, node_type, parent_name, old_name, new_name):
        """
        SCENARIO: Rename node with valid name across hierarchy levels
        GIVEN: Node exists with old name
        WHEN: Node is renamed to new valid name
        THEN: Node name is updated and accessible by new name
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node(
            node_type, parent_name, old_name
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[old_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(old_name)
        elif node_type == 'Story':
            node = helper.story.find_story_in_story_graph(old_name)
        else:
            node = helper.story.find_scenario_in_story_graph(old_name)
        
        node.rename(new_name)
        
        assert node.name == new_name
    # Scenario: Rename node with empty or whitespace name returns error
    
    @pytest.mark.parametrize('node_type,current_name,invalid_name,error_message', [
        ('Epic', 'User Management', '', 'Node name cannot be empty'),
        ('SubEpic', 'Authentication', '   ', 'Node name cannot be whitespace-only'),
        ('Story', 'Login Form', '  ', 'Node name cannot be whitespace-only'),
    ])
    def test_rename_node_with_empty_or_whitespace_name_returns_error(self, tmp_path, node_type, current_name, invalid_name, error_message):
        """
        SCENARIO: Rename node with empty or whitespace name returns error
        GIVEN: Node exists with current name
        WHEN: Attempting to rename to empty or whitespace name
        THEN: System identifies invalid name and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node(
            node_type, 'parent', current_name
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[current_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(current_name)
        else:
            node = helper.story.find_story_in_story_graph(current_name)
        
        with pytest.raises(ValueError, match=error_message):
            node.rename(invalid_name)
        
        assert node.name == current_name
    # Scenario: Rename node with duplicate sibling name returns error
    
    @pytest.mark.parametrize('parent_type,parent_name,existing_children,node_name,duplicate_name', [
        ('Epic', 'User Management', 'Authentication, Authorization, Audit', 'Audit', 'Authentication'),
        ('SubEpic', 'Authentication', 'Login Flow, Password Reset, OAuth', 'OAuth', 'Login Flow'),
        ('Story', 'Login Form', 'Valid Login, Invalid Password, Account Locked', 'Account Locked', 'Valid Login'),
    ])
    def test_rename_node_with_duplicate_sibling_name_returns_error(self, tmp_path, parent_type, parent_name, existing_children, node_name, duplicate_name):
        """
        SCENARIO: Rename node with duplicate sibling name returns error
        GIVEN: Parent has multiple children including target node
        WHEN: Attempting to rename node to existing sibling name
        THEN: System identifies duplicate and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_named_children(
            parent_type, parent_name, existing_children
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        elif parent_type == 'SubEpic':
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        else:
            parent = helper.story.find_story_in_story_graph(parent_name)
        
        node = next(child for child in parent.children if child.name == node_name)
        
        with pytest.raises(ValueError, match=f"Name '{duplicate_name}' already exists among siblings"):
            node.rename(duplicate_name)
        
        assert node.name == node_name
    # Scenario: Rename node with valid special characters
    
    @pytest.mark.parametrize('node_type,old_name,new_name_with_special_chars', [
        ('Epic', 'User Management', 'User Management & Administration'),
        ('SubEpic', 'Authentication', 'Authentication (OAuth 2.0)'),
        ('Story', 'Login', 'Login - Username/Password'),
        ('Scenario', 'Valid Login', 'Valid Login: Success Response'),
    ])
    def test_rename_node_with_valid_special_characters(self, tmp_path, node_type, old_name, new_name_with_special_chars):
        """
        SCENARIO: Rename node with valid special characters
        GIVEN: Node exists with old name
        WHEN: Renaming to name with valid special characters
        THEN: Name is updated and special characters are preserved
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node(
            node_type, 'parent', old_name
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[old_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(old_name)
        elif node_type == 'Story':
            node = helper.story.find_story_in_story_graph(old_name)
        else:
            node = helper.story.find_scenario_in_story_graph(old_name)
        
        node.rename(new_name_with_special_chars)
        
        assert node.name == new_name_with_special_chars
    # Scenario: Rename node with invalid special characters returns error
    
    @pytest.mark.parametrize('node_type,current_name,invalid_name,invalid_chars', [
        ('Epic', 'User Management', 'User<Admin>', '<, >'),
        ('SubEpic', 'Authentication', 'Auth\\System', '\\'),
        ('Story', 'Login Form', 'Login|Form', '|'),
        ('Scenario', 'Valid Login', 'Valid*Login?', '*, ?'),
    ])
    def test_rename_node_with_invalid_special_characters_returns_error(self, tmp_path, node_type, current_name, invalid_name, invalid_chars):
        """
        SCENARIO: Rename node with invalid special characters returns error
        GIVEN: Node exists with current name
        WHEN: Attempting to rename with invalid special characters
        THEN: System identifies invalid characters and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node(
            node_type, 'parent', current_name
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[current_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(current_name)
        elif node_type == 'Story':
            node = helper.story.find_story_in_story_graph(current_name)
        else:
            node = helper.story.find_scenario_in_story_graph(current_name)
        
        with pytest.raises(ValueError, match=f"Name contains invalid characters: {re.escape(invalid_chars)}"):
            node.rename(invalid_name)
        
        assert node.name == current_name


class TestMoveStoryNodeToParent:
    """Tests for moving story nodes between parents."""
    # Scenario: Move node to new parent with default position
    
    @pytest.mark.parametrize('source_parent_type,source_parent,node_name,original_position,target_parent_type,target_parent,target_child_count,new_position,final_child_count', [
        ('Epic', 'User Management', 'Authentication', 1, 'Epic', 'System Admin', 2, 2, 3),
        ('SubEpic', 'Authentication', 'Login Flow', 0, 'SubEpic', 'Authorization', 1, 1, 2),
        ('SubEpic', 'Authentication', 'User Login', 1, 'SubEpic', 'Session Management', 0, 0, 1),
    ])
    def test_move_node_to_new_parent_with_default_position(self, tmp_path, source_parent_type, source_parent, node_name, original_position, target_parent_type, target_parent, target_child_count, new_position, final_child_count):
        """
        SCENARIO: Move node to new parent with default position
        GIVEN: Node exists under source parent
        WHEN: Node moves to target parent
        THEN: Node is removed from source and added to target at last position
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_for_move(
            source_parent_type, source_parent, node_name, target_parent_type, target_parent, target_child_count
        )
        
        if source_parent_type == 'Epic':
            source_node = helper.story.bot.story_graph.epics[source_parent]
        else:
            source_node = helper.story.find_subepic_in_story_graph(source_parent)
        
        if target_parent_type == 'Epic':
            target = helper.story.bot.story_graph.epics[target_parent]
        else:
            target = helper.story.find_subepic_in_story_graph(target_parent)
        
        node = next(child for child in source_node.children if child.name == node_name)
        node.move_to(target)
        
        helper.story.assert_node_removed_from_parent(source_node, node_name)
        helper.story.assert_node_added_to_parent(target, node_name, new_position)
        helper.story.assert_parent_child_count(target, final_child_count)
    # Scenario: Move node to new parent with specified position
    
    @pytest.mark.parametrize('source_parent,node_name,target_parent,target_children,target_position,final_order', [
        ('Epic A', 'SubEpic X', 'Epic B', 'SubEpic A, SubEpic B, SubEpic C', 1, 'SubEpic A, SubEpic X, SubEpic B, SubEpic C'),
        ('SubEpic A', 'Story X', 'SubEpic B', 'Story A, Story B', 0, 'Story X, Story A, Story B'),
        ('SubEpic A', 'Story X', 'SubEpic B', 'Story A, Story B', 2, 'Story A, Story B, Story X'),
    ])
    def test_move_node_to_new_parent_with_specified_position(self, tmp_path, source_parent, node_name, target_parent, target_children, target_position, final_order):
        """
        SCENARIO: Move node to new parent with specified position
        GIVEN: Node exists under source parent, target parent has children
        WHEN: Node moves to target parent at specific position
        THEN: Node is inserted at position and target children shift
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_for_move_with_children(
            source_parent, node_name, target_parent, target_children
        )
        
        source_node = helper.story.bot.story_graph.epics[source_parent]
        target = helper.story.bot.story_graph.epics[target_parent]
        node = next(child for child in source_node.children if child.name == node_name)
        node.move_to(target, position=target_position)
        
        helper.story.assert_children_in_order(target, final_order)
        helper.story.assert_child_at_position(target, node_name, target_position)
    # Scenario: Move node with invalid position adjusts to last
    
    @pytest.mark.parametrize('source_parent,node_name,target_parent,target_child_count,invalid_position,adjusted_position,final_count', [
        ('Epic A', 'SubEpic X', 'Epic B', 3, 99, 3, 4),
        ('SubEpic A', 'Story X', 'SubEpic B', 0, 5, 0, 1),
    ])
    def test_move_node_with_invalid_position_adjusts_to_last(self, tmp_path, source_parent, node_name, target_parent, target_child_count, invalid_position, adjusted_position, final_count):
        """
        SCENARIO: Move node with invalid position adjusts to last
        GIVEN: Node exists under source parent
        WHEN: Moving to target with invalid position
        THEN: Position is adjusted to last valid position
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_for_move(
            'Epic', source_parent, node_name, 'Epic', target_parent, target_child_count
        )
        
        source_node = helper.story.bot.story_graph.epics[source_parent]
        target = helper.story.bot.story_graph.epics[target_parent]
        node = next(child for child in source_node.children if child.name == node_name)
        node.move_to(target, position=invalid_position)
        
        helper.story.assert_child_at_position(target, node_name, adjusted_position)
        helper.story.assert_parent_child_count(target, final_count)
    # Scenario: Move node to same parent at different position
    
    @pytest.mark.parametrize('parent_type,parent_name,initial_order,node_name,current_position,new_position,final_order', [
        ('Epic', 'User Management', 'SubEpic A, SubEpic B, SubEpic C', 'SubEpic C', 2, 0, 'SubEpic C, SubEpic A, SubEpic B'),
        ('SubEpic', 'Authentication', 'Story A, Story B, Story C, Story D', 'Story B', 1, 3, 'Story A, Story C, Story D, Story B'),
    ])
    def test_move_node_to_same_parent_at_different_position(self, tmp_path, parent_type, parent_name, initial_order, node_name, current_position, new_position, final_order):
        """
        SCENARIO: Move node to same parent at different position
        GIVEN: Parent has children in order
        WHEN: Node moves to different position within same parent
        THEN: Children are reordered correctly
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_named_children(
            parent_type, parent_name, initial_order
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        else:
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        
        node = next(child for child in parent.children if child.name == node_name)
        node.move_to(parent, position=new_position)
        
        helper.story.assert_children_in_order(parent, final_order)
        helper.story.assert_child_at_position(parent, node_name, new_position)
    # Scenario: Move node to parent where it already exists returns error
    
    @pytest.mark.parametrize('parent_type,parent_name,node_name', [
        ('Epic', 'User Management', 'Authentication'),
        ('SubEpic', 'Authentication', 'Login Form'),
    ])
    def test_move_node_to_parent_where_it_already_exists_returns_error(self, tmp_path, parent_type, parent_name, node_name):
        """
        SCENARIO: Move node to parent where it already exists returns error
        GIVEN: Node is already child of parent
        WHEN: Attempting to move node to same parent
        THEN: System identifies duplicate and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_child(
            parent_type, parent_name, node_name
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
        else:
            parent = helper.story.find_subepic_in_story_graph(parent_name)
        
        node = next(child for child in parent.children if child.name == node_name)
        
        with pytest.raises(ValueError, match=f"Node '{node_name}' already exists under parent '{parent_name}'"):
            node.move_to(parent)
    # Scenario: Move SubEpic to SubEpic with Stories returns error
    
    @pytest.mark.parametrize('source_parent,node_name,target_parent,existing_story', [
        ('User Management', 'OAuth Flow', 'Authentication', 'Login Form'),
        ('Administration', 'Audit Logging', 'User Profile', 'Edit Profile'),
    ])
    def test_move_subepic_to_subepic_with_stories_returns_error(self, tmp_path, source_parent, node_name, target_parent, existing_story):
        """
        SCENARIO: Move SubEpic to SubEpic with Stories returns error
        GIVEN: Source has SubEpic, target has Stories
        WHEN: Attempting to move SubEpic to target with Stories
        THEN: System identifies hierarchy violation and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_for_hierarchy_move_test(
            source_parent, node_name, 'SubEpic', target_parent, existing_story, 'Story'
        )
        
        source_subepic = helper.story.find_subepic_in_story_graph(source_parent)
        target = helper.story.find_subepic_in_story_graph(target_parent)
        node = next(child for child in source_subepic.children if child.name == node_name)
        
        with pytest.raises(ValueError, match="Cannot move SubEpic to SubEpic with Stories"):
            node.move_to(target)
    # Scenario: Move Story to SubEpic with SubEpics returns error
    
    @pytest.mark.parametrize('source_parent,node_name,target_parent,existing_subepic', [
        ('Authentication', 'Login Form', 'User Management', 'Authorization'),
        ('User Profile', 'Edit Profile', 'Administration', 'Audit Logging'),
    ])
    def test_move_story_to_subepic_with_subepics_returns_error(self, tmp_path, source_parent, node_name, target_parent, existing_subepic):
        """
        SCENARIO: Move Story to SubEpic with SubEpics returns error
        GIVEN: Source has Story, target has SubEpics
        WHEN: Attempting to move Story to target with SubEpics
        THEN: System identifies hierarchy violation and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_for_hierarchy_move_test(
            source_parent, node_name, 'Story', target_parent, existing_subepic, 'SubEpic'
        )
        
        source_subepic = helper.story.find_subepic_in_story_graph(source_parent)
        target = helper.story.find_subepic_in_story_graph(target_parent)
        node = helper.story.find_story_in_story_graph(node_name)
        
        with pytest.raises(ValueError, match="Cannot move Story to SubEpic with SubEpics"):
            node.move_to(target)
    # Scenario: Move node to create circular reference returns error
    
    @pytest.mark.parametrize('parent_type,parent_name,child_name', [
        ('Epic', 'User Management', 'Authentication'),
        ('SubEpic', 'Authentication', 'Login Flow'),
    ])
    def test_move_node_to_create_circular_reference_returns_error(self, tmp_path, parent_type, parent_name, child_name):
        """
        SCENARIO: Move node to create circular reference returns error
        GIVEN: Parent has descendant
        WHEN: Attempting to move parent to its descendant
        THEN: System identifies circular reference and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_descendant(
            parent_type, parent_name, child_name
        )
        
        if parent_type == 'Epic':
            parent = helper.story.bot.story_graph.epics[parent_name]
            child = next(c for c in parent.children if c.name == child_name)
        else:
            parent = helper.story.find_subepic_in_story_graph(parent_name)
            child = next(c for c in parent.children if c.name == child_name)
        
        with pytest.raises(ValueError, match="Cannot move node to its own descendant - circular reference"):
            parent.move_to(child)


class TestExecuteActionScopedToStoryNode:
    """Tests for executing actions scoped to story nodes."""
    # Scenario: Execute action on node with valid parameters
    
    @pytest.mark.parametrize('node_type,node_name,action_name,parameters', [
        ('Epic', 'User Management', 'build', '{"output": "docs/stories"}'),
        ('SubEpic', 'Authentication', 'validate', '{"rules": "all"}'),
        ('Story', 'Login Form', 'render', '{"format": "markdown"}'),
    ])
    def test_execute_action_on_node_with_valid_parameters(self, tmp_path, node_type, node_name, action_name, parameters):
        """
        SCENARIO: Execute action on node with valid parameters
        GIVEN: Node exists and bot has registered actions
        WHEN: Node executes action with valid parameters
        THEN: Action completes successfully
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node_and_actions(
            node_type, node_name, ['clarify', 'strategy', 'build', 'validate', 'render']
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[node_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(node_name)
        else:
            node = helper.story.find_story_in_story_graph(node_name)
        
        result = node.execute_action(action_name, parameters)
        
        assert result.success is True
        helper.story.assert_story_graph_structure_valid()
    # Scenario: Execute action with invalid parameters returns error
    
    @pytest.mark.parametrize('node_type,node_name,action_name,invalid_parameters,invalid_params_list,error_message', [
        ('Epic', 'User Management', 'build', '{"invalid_key": "value"}', 'invalid_key', 'Invalid parameter: invalid_key. Expected: output'),
        ('SubEpic', 'Authentication', 'validate', '{}', 'rules', 'Missing required parameter: rules'),
        ('Story', 'Login Form', 'render', '{"format": "invalid_format"}', 'format', 'Invalid format value: invalid_format. Expected: markdown, json, html'),
    ])
    def test_execute_action_with_invalid_parameters_returns_error(self, tmp_path, node_type, node_name, action_name, invalid_parameters, invalid_params_list, error_message):
        """
        SCENARIO: Execute action with invalid parameters returns error
        GIVEN: Node exists and bot has registered actions
        WHEN: Node executes action with invalid parameters
        THEN: Bot validates parameters and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node_and_actions(
            node_type, node_name, ['clarify', 'strategy', 'build', 'validate', 'render']
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[node_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(node_name)
        else:
            node = helper.story.find_story_in_story_graph(node_name)
        
        with pytest.raises(ValueError, match=error_message):
            node.execute_action(action_name, invalid_parameters)
    # Scenario: Execute non-existent action returns error
    
    @pytest.mark.parametrize('node_type,node_name,non_existent_action', [
        ('Epic', 'User Management', 'deploy'),
        ('SubEpic', 'Authentication', 'test'),
        ('Story', 'Login Form', 'compile'),
    ])
    def test_execute_non_existent_action_returns_error(self, tmp_path, node_type, node_name, non_existent_action):
        """
        SCENARIO: Execute non-existent action returns error
        GIVEN: Node exists and bot has registered actions
        WHEN: Node attempts to execute non-existent action
        THEN: Bot validates action exists and returns error
        """
        helper = BotTestHelper(tmp_path)
        helper.story.create_story_graph_with_node_and_actions(
            node_type, node_name, ['clarify', 'strategy', 'build', 'validate', 'render']
        )
        
        if node_type == 'Epic':
            node = helper.story.bot.story_graph.epics[node_name]
        elif node_type == 'SubEpic':
            node = helper.story.find_subepic_in_story_graph(node_name)
        else:
            node = helper.story.find_story_in_story_graph(node_name)
        
        with pytest.raises(ValueError, match=f"Action '{non_existent_action}' not found. Available actions: clarify, strategy, build, validate, render"):
            node.execute_action(non_existent_action)
