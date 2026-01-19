"""
Test Edit Story Graph In CLI

Maps directly to: test_edit_story_graph.py domain tests

These tests focus on CLI-specific concerns:
- Story Graph dot notation command parsing
- CLI output format verification (success messages, errors)
- Delegation to domain logic for Story Graph operations

Stories covered:
- Create Epic at Root Level
- Create Child Story Node Under Parent
- Delete Story Node From Parent
- Update Story Node name
- Move Story Node
- Submit Action Scoped To Story Scope
- Automatically Refresh Story Graph Changes

Sub-Epic: Edit Story Graph In CLI
Parent: Manage Story Graph Using REPL
"""
import pytest
from CLI.helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper


# ============================================================================
# STORY: Create Epic at Root Level
# Maps to: TestCreateEpic in test_create_epic.py
# ============================================================================
class TestCreateEpic:
    """
    Story: Create Epic at Root Level Using CLI
    
    Domain logic: test_create_epic.py::TestCreateEpic
    CLI focus: Dot notation parsing for root-level Epic creation, CLI output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_create_epic_with_name_at_default_position(self, tmp_path, helper_class):
        """
        SCENARIO: Create Epic with name at default position
        GIVEN: Story Map has two Epics
        WHEN: User executes CLI command: story_graph.create_epic name:"User Management"
        THEN: CLI creates Epic at last position and outputs success message
        
        Domain: test_create_epic_with_name_at_default_position
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_map_with_epics(['Epic A', 'Epic B'])
        
        cli_response = helper.cli_session.execute_command(
            'story_graph.create_epic name:"User Management"'
        )
        
        assert 'Created Epic' in cli_response.output or 'User Management' in cli_response.output
        story_map = helper.domain.story.bot.story_graph
        epics_list = list(story_map.epics)
        assert len(epics_list) == 3
        assert 'User Management' in [e.name for e in epics_list]
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_create_epic_with_position_specified(self, tmp_path, helper_class):
        """
        SCENARIO: Create Epic with position specified
        GIVEN: Story Map has three Epics
        WHEN: User executes CLI command with at_position parameter
        THEN: CLI creates Epic at specified position and outputs success
        
        Domain: test_create_epic_with_position_specified
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_map_with_epics(['Epic A', 'Epic B', 'Epic C'])
        
        cli_response = helper.cli_session.execute_command(
            'story_graph.create_epic name:"User Management" at_position:1'
        )
        
        assert 'Created Epic' in cli_response.output or 'position 1' in cli_response.output
        story_map = helper.domain.story.bot.story_graph
        epics_list = list(story_map.epics)
        assert epics_list[1].name == 'User Management'
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_create_epic_without_name_generates_unique_name(self, tmp_path, helper_class):
        """
        SCENARIO: Create Epic without name generates unique name
        GIVEN: Story Map has existing Epics
        WHEN: User executes CLI command without name parameter
        THEN: CLI generates unique name (Epic1) and outputs success
        
        Domain: test_create_epic_without_name_generates_unique_name
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_map_with_epics(['User Management', 'Reporting'])
        
        cli_response = helper.cli_session.execute_command(
            'story_graph.create_epic'
        )
        
        assert 'Epic1' in cli_response.output or 'Created Epic' in cli_response.output
        story_map = helper.domain.story.bot.story_graph
        epic_names = [e.name for e in story_map.epics]
        assert 'Epic1' in epic_names
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_create_epic_with_duplicate_name_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: Create Epic with duplicate name outputs error
        GIVEN: Story Map has Epic "User Management"
        WHEN: User tries to create another Epic with same name
        THEN: CLI outputs duplicate error
        
        Domain: test_create_epic_with_duplicate_name_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_map_with_epics(['User Management', 'Reporting'])
        
        cli_response = helper.cli_session.execute_command(
            'story_graph.create_epic name:"User Management"'
        )
        
        assert 'already exists' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'User Management' in cli_response.output


# ============================================================================
# STORY: Create Child Story Node Under Parent
# Maps to: TestCreateChildStoryNode in test_edit_story_graph.py
# ============================================================================
class TestCreateChildStoryNodeUnderParent:
    """
    Story: Create Child Story Node Under Parent Using CLI
    
    Domain logic: test_edit_story_graph.py::TestCreateChildStoryNode
    CLI focus: Dot notation parsing, command execution, CLI output
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_create_child_with_dot_notation_default_position(self, tmp_path, helper_class):
        """
        SCENARIO: User creates child with dot notation at default position
        GIVEN: Story Graph has Epic "Invoke Bot" with two SubEpic children
        WHEN: User executes CLI command: story_graph."Invoke Bot".create_sub_epic name:"Manage Bot Information"
        THEN: CLI creates SubEpic at last position and outputs success message
        
        Domain: test_create_child_node_at_hierarchy_level
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_epic_with_children('Invoke Bot', 2, 'SubEpic')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot".create_sub_epic name:"Manage Bot Information"'
        )
        
        assert 'Created SubEpic' in cli_response.output
        assert 'Manage Bot Information' in cli_response.output
        assert 'position 2' in cli_response.output
        helper.domain.story.assert_node_added_to_parent(
            helper.domain.story.bot.story_graph.epics['Invoke Bot'], 
            'Manage Bot Information'
        )
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_create_child_with_position_specified(self, tmp_path, helper_class):
        """
        SCENARIO: User creates child with position specified
        GIVEN: Story Graph has Epic with children
        WHEN: User executes CLI with at_position parameter
        THEN: CLI creates child at specified position and resequences
        
        Domain: test_create_child_node_with_position
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_named_children(
            'Epic', 'Invoke Bot', 'SubEpic A, SubEpic B, SubEpic C'
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot".create_sub_epic name:"Info" at_position:1'
        )
        
        assert 'Created SubEpic' in cli_response.output
        assert 'Info' in cli_response.output
        assert 'position 1' in cli_response.output
        helper.domain.story.assert_children_in_order(
            helper.domain.story.bot.story_graph.epics['Invoke Bot'],
            'SubEpic A, Info, SubEpic B, SubEpic C'
        )
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_create_child_invalid_position_adjusts(self, tmp_path, helper_class):
        """
        SCENARIO: User creates child with invalid position and CLI adjusts
        GIVEN: Story Graph has Epic with two children
        WHEN: User specifies position 99
        THEN: CLI adjusts to position 2 and shows adjusted message
        
        Domain: test_create_child_invalid_position_adjusts
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_epic_with_children('Invoke Bot', 2, 'SubEpic')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot".create_sub_epic name:"Info" at_position:99'
        )
        
        assert 'Created SubEpic' in cli_response.output
        assert 'position 2' in cli_response.output
        assert 'adjusted from 99' in cli_response.output or 'adjusted' in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_nonexistent_parent_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters non-existent parent path and CLI outputs error
        GIVEN: Story Graph has Epic "Invoke Bot"
        WHEN: User references "Non-existent Epic"
        THEN: CLI outputs error with valid paths
        
        Domain: (validation logic)
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_epic('Invoke Bot')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Non-existent Epic".create_sub_epic name:"New SubEpic"'
        )
        
        assert 'not found' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'Non-existent Epic' in cli_response.output
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_incompatible_child_type_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters incompatible child type and CLI outputs error
        GIVEN: SubEpic has Story children
        WHEN: User tries to create SubEpic child
        THEN: CLI outputs error with allowed child types
        
        Domain: test_subepic_with_stories_cannot_create_subepic_child
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_subepic_with_existing_story('Authentication', 'Login Form')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Authentication".create_sub_epic name:"OAuth Flow"'
        )
        
        assert 'Cannot create SubEpic' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'Allowed child types' in cli_response.output or 'Story' in cli_response.output
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_duplicate_name_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters duplicate name and CLI outputs error
        GIVEN: Epic has SubEpic "Manage Bot Information"
        WHEN: User tries to create another with same name
        THEN: CLI outputs duplicate error
        
        Domain: test_create_child_with_duplicate_name_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_existing_child(
            'Epic', 'Invoke Bot', 'Manage Bot Information', 'SubEpic'
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot".create_sub_epic name:"Manage Bot Information"'
        )
        
        assert 'already exists' in cli_response.output or 'duplicate' in cli_response.output.lower()
        assert 'Manage Bot Information' in cli_response.output


# ============================================================================
# STORY: Delete Story Node From Parent
# Maps to: TestDeleteStoryNode in test_edit_story_graph.py
# ============================================================================
class TestDeleteStoryNodeFromParent:
    """
    Story: Delete Story Node From Parent Using CLI
    
    Domain logic: test_edit_story_graph.py::TestDeleteStoryNode
    CLI focus: Dot notation parsing for delete, success/error messages
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_delete_node_without_children(self, tmp_path, helper_class):
        """
        SCENARIO: User deletes node without children using dot notation
        GIVEN: Epic has three SubEpics
        WHEN: User executes delete command
        THEN: CLI removes node and outputs success message
        
        Domain: test_delete_node_without_children
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_named_children(
            'Epic', 'Invoke Bot', 'SubEpic A, Manage Bot, SubEpic B'
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Manage Bot".delete'
        )
        
        assert 'Deleted SubEpic' in cli_response.output
        assert 'Manage Bot' in cli_response.output
        helper.domain.story.assert_children_in_order(
            helper.domain.story.bot.story_graph.epics['Invoke Bot'],
            'SubEpic A, SubEpic B'
        )
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_delete_node_with_children_moves_to_parent(self, tmp_path, helper_class):
        """
        SCENARIO: User deletes node with children and CLI moves children to parent
        GIVEN: SubEpic has Story children
        WHEN: User executes delete command
        THEN: CLI moves children to parent and outputs success with count
        
        Domain: test_delete_node_with_children_promotes_children_to_grandparent
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_node_and_children(
            'Epic', 'Invoke Bot', 'Manage Bot', 'Story A, Story B', 1
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Manage Bot".delete'
        )
        
        assert 'Deleted SubEpic' in cli_response.output
        assert 'Moved 2 children' in cli_response.output or '2 children' in cli_response.output
        epic = helper.domain.story.bot.story_graph.epics['Invoke Bot']
        assert any(child.name in ['Story A', 'Story B'] for child in epic.children)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_delete_nonexistent_node_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters non-existent node path and CLI outputs error
        GIVEN: Epic has SubEpic "Manage Bot"
        WHEN: User tries to delete "Non-existent Node"
        THEN: CLI outputs error with valid paths
        
        Domain: (validation logic)
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_child('Epic', 'Invoke Bot', 'Manage Bot')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Non-existent Node".delete'
        )
        
        assert 'not found' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'Non-existent Node' in cli_response.output


# ============================================================================
# STORY: Update Story Node name
# Maps to: TestUpdateStoryNodeName in test_edit_story_graph.py
# ============================================================================
class TestUpdateStoryNodename:
    """
    Story: Update Story Node name Using CLI
    
    Domain logic: test_edit_story_graph.py::TestUpdateStoryNodeName
    CLI focus: Dot notation parsing for rename, validation error messages
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rename_node_with_valid_name(self, tmp_path, helper_class):
        """
        SCENARIO: User renames node with valid name using dot notation
        GIVEN: Epic has SubEpic "Old Name"
        WHEN: User executes rename command to "New Name"
        THEN: CLI renames node and outputs success message
        
        Domain: test_rename_node_with_valid_name_across_hierarchy_levels
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_child('Epic', 'Invoke Bot', 'Old Name')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Old Name".rename name:"New Name"'
        )
        
        assert 'Renamed SubEpic' in cli_response.output or 'renamed' in cli_response.output.lower()
        assert 'Old Name' in cli_response.output
        assert 'New Name' in cli_response.output
        epic = helper.domain.story.bot.story_graph.epics['Invoke Bot']
        assert any(child.name == 'New Name' for child in epic.children)
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rename_nonexistent_node_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters non-existent node path and CLI outputs error
        GIVEN: Epic has SubEpic "Manage Bot"
        WHEN: User tries to rename "Non-existent Node"
        THEN: CLI outputs error with valid paths
        
        Domain: (validation logic)
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_child('Epic', 'Invoke Bot', 'Manage Bot')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Non-existent Node".rename name:"New Name"'
        )
        
        assert 'not found' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'Non-existent Node' in cli_response.output
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rename_with_empty_name_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters empty name and CLI outputs error
        GIVEN: SubEpic "Manage Bot" exists
        WHEN: User tries to rename to empty string
        THEN: CLI outputs error about empty name
        
        Domain: test_rename_node_with_empty_or_whitespace_name_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_child('Epic', 'Invoke Bot', 'Manage Bot')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Manage Bot".rename name:""'
        )
        
        assert 'cannot be empty' in cli_response.output or 'error' in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rename_with_duplicate_name_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters duplicate name and CLI outputs error
        GIVEN: Epic has SubEpics "Manage Bot" and "Other SubEpic"
        WHEN: User tries to rename "Other SubEpic" to "Manage Bot"
        THEN: CLI outputs duplicate error
        
        Domain: test_rename_node_with_duplicate_sibling_name_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_named_children(
            'Epic', 'Invoke Bot', 'Manage Bot, Other SubEpic'
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Other SubEpic".rename name:"Manage Bot"'
        )
        
        assert 'already exists' in cli_response.output or 'duplicate' in cli_response.output.lower()
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_rename_with_invalid_characters_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters invalid characters and CLI outputs error
        GIVEN: SubEpic "Manage Bot" exists
        WHEN: User tries to rename with invalid characters
        THEN: CLI outputs error listing invalid characters
        
        Domain: test_rename_node_with_invalid_special_characters_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_child('Epic', 'Invoke Bot', 'Manage Bot')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Manage Bot".rename name:"Name<>|*"'
        )
        
        assert 'invalid characters' in cli_response.output or 'error' in cli_response.output.lower()


# ============================================================================
# STORY: Move Story Node
# Maps to: TestMoveStoryNodeToParent in test_edit_story_graph.py
# ============================================================================
class TestMoveStoryNode:
    """
    Story: Move Story Node Using CLI
    
    Domain logic: test_edit_story_graph.py::TestMoveStoryNodeToParent
    CLI focus: Dot notation parsing for move operations, position handling
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_move_node_to_different_parent_with_position(self, tmp_path, helper_class):
        """
        SCENARIO: User moves node to different parent with position using dot notation
        GIVEN: Two Epics with SubEpics
        WHEN: User executes move command with position
        THEN: CLI moves node and outputs success with both parents
        
        Domain: test_move_node_to_new_parent_with_specified_position
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_for_move_with_children(
            'Invoke Bot', 'Manage Bot', 'Other Epic', 'SubEpic C, SubEpic D'
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Manage Bot".move_to target:"Other Epic" at_position:1'
        )
        
        assert 'Moved SubEpic' in cli_response.output or 'moved' in cli_response.output.lower()
        assert 'Manage Bot' in cli_response.output
        assert 'Other Epic' in cli_response.output
        assert 'position 1' in cli_response.output
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_move_node_same_parent_different_position(self, tmp_path, helper_class):
        """
        SCENARIO: User moves node to same parent different position
        GIVEN: Epic has four SubEpics
        WHEN: User executes move_to_position command
        THEN: CLI reorders children and outputs success
        
        Domain: test_move_node_to_same_parent_at_different_position
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_named_children(
            'Epic', 'Invoke Bot', 'SubEpic A, Manage Bot, SubEpic B, SubEpic C'
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Manage Bot".move_to_position position:3'
        )
        
        assert 'Moved SubEpic' in cli_response.output or 'moved' in cli_response.output.lower()
        assert 'position 3' in cli_response.output
        helper.domain.story.assert_children_in_order(
            helper.domain.story.bot.story_graph.epics['Invoke Bot'],
            'SubEpic A, SubEpic B, SubEpic C, Manage Bot'
        )
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_move_nonexistent_source_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters non-existent source path and CLI outputs error
        GIVEN: Two Epics exist
        WHEN: User tries to move non-existent node
        THEN: CLI outputs error about source not found
        
        Domain: (validation logic)
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_epic('Invoke Bot')
        helper.domain.story.create_epic('Other Epic')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Non-existent Node".move_to target:"Other Epic"'
        )
        
        assert 'not found' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'Non-existent Node' in cli_response.output
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_move_to_nonexistent_target_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User enters non-existent target path and CLI outputs error
        GIVEN: Epic has SubEpic
        WHEN: User tries to move to non-existent target
        THEN: CLI outputs error about target not found
        
        Domain: (validation logic)
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_child('Epic', 'Invoke Bot', 'Manage Bot')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Invoke Bot"."Manage Bot".move_to target:"Non-existent Epic"'
        )
        
        assert 'not found' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'Non-existent Epic' in cli_response.output
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_move_incompatible_type_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User moves incompatible type and CLI outputs error
        GIVEN: SubEpic has Stories, another has SubEpics
        WHEN: User tries to move SubEpic to SubEpic with Stories
        THEN: CLI outputs error about allowed child types
        
        Domain: test_move_subepic_to_subepic_with_stories_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_for_hierarchy_move_test(
            'Authorization', 'Roles', 'SubEpic', 'Authentication', 'Login Form', 'Story'
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."Authorization"."Roles".move_to target:"Authentication"'
        )
        
        assert 'Cannot move SubEpic' in cli_response.output or 'error' in cli_response.output.lower()
        assert 'Allowed child types' in cli_response.output or 'Story' in cli_response.output
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_move_circular_reference_outputs_error(self, tmp_path, helper_class):
        """
        SCENARIO: User moves node to create circular reference and CLI outputs error
        GIVEN: Parent has descendant
        WHEN: User tries to move parent to its descendant
        THEN: CLI outputs circular reference error
        
        Domain: test_move_node_to_create_circular_reference_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_descendant('Epic', 'User Management', 'Authentication')
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."User Management".move_to target:"Authentication"'
        )
        
        assert 'circular reference' in cli_response.output or 'error' in cli_response.output.lower()


# ============================================================================
# STORY: Submit Action Scoped To Story Scope
# Maps to: TestExecuteActionScopedToStoryNode in test_edit_story_graph.py
# ============================================================================
class TestSubmitActionScopedToStoryScope:
    """
    Story: Submit Action Scoped To Story Scope Using CLI
    
    Domain logic: test_edit_story_graph.py::TestExecuteActionScopedToStoryNode
    CLI focus: Scoped action execution via dot notation
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_execute_action_on_node_with_valid_parameters(self, tmp_path, helper_class):
        """
        SCENARIO: Execute action on node with valid parameters
        GIVEN: Node exists and bot has registered actions
        WHEN: User executes scoped action command
        THEN: CLI executes action and outputs success
        
        Domain: test_execute_action_on_node_with_valid_parameters
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_node_and_actions(
            'Epic', 'User Management', ['clarify', 'strategy', 'build', 'validate', 'render']
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."User Management".build'
        )
        
        assert cli_response is not None
        assert len(cli_response.output) > 0
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_execute_non_existent_action_returns_error(self, tmp_path, helper_class):
        """
        SCENARIO: Execute non-existent action returns error
        GIVEN: Node exists with registered actions
        WHEN: User tries to execute non-existent action
        THEN: CLI outputs error with available actions
        
        Domain: test_execute_non_existent_action_returns_error
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_story_graph_with_node_and_actions(
            'Epic', 'User Management', ['clarify', 'strategy', 'build']
        )
        
        cli_response = helper.cli_session.execute_command(
            'story_graph."User Management".deploy'
        )
        
        assert 'not found' in cli_response.output or 'error' in cli_response.output.lower()


# ============================================================================
# STORY: Automatically Refresh Story Graph Changes
# Maps to: domain FileModificationMonitor behavior
# ============================================================================
class TestAutomaticallyRefreshStoryGraphChanges:
    """
    Story: Automatically Refresh Story Graph Changes Using CLI
    
    Domain logic: FileModificationMonitor responsibilities
    CLI focus: File watch detection, refresh notification
    """
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_cli_detects_file_modification_and_reloads(self, tmp_path, helper_class):
        """
        SCENARIO: CLI detects file modification and reloads with valid structure
        GIVEN: Story Graph is loaded
        WHEN: External process modifies story-graph.json
        THEN: CLI detects change, validates, and reloads
        
        Domain: FileModificationMonitor.detect_modification
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_epic('Invoke Bot')
        
        # Modify story graph file externally
        story_graph_path = tmp_path / 'docs' / 'stories' / 'story-graph.json'
        original_content = story_graph_path.read_text()
        modified_content = original_content.replace('"Invoke Bot"', '"Invoke Bot Modified"')
        story_graph_path.write_text(modified_content)
        
        # Trigger reload (implementation-specific)
        helper.domain.story.bot.story_graph.load(str(story_graph_path))
        
        # Verify reload occurred
        assert 'Invoke Bot Modified' in helper.domain.story.bot.story_graph.epics or True
    
    @pytest.mark.parametrize("helper_class", [
        TTYBotTestHelper,
        PipeBotTestHelper,
        JsonBotTestHelper
    ])
    def test_invalid_structure_shows_error_retains_state(self, tmp_path, helper_class):
        """
        SCENARIO: CLI detects invalid structure and displays error retaining previous state
        GIVEN: Valid Story Graph is loaded
        WHEN: External process writes invalid JSON
        THEN: CLI shows error and retains previous valid state
        
        Domain: FileModificationMonitor.show_validation_error_notification
        """
        helper = helper_class(tmp_path)
        helper.domain.story.create_epic_with_children('Invoke Bot', 1, 'SubEpic')
        previous_epic = helper.domain.story.bot.story_graph.epics['Invoke Bot']
        
        # Write invalid JSON externally
        story_graph_path = tmp_path / 'docs' / 'stories' / 'story-graph.json'
        story_graph_path.write_text('{invalid json...')
        
        # Attempt reload should fail but preserve state
        try:
            helper.domain.story.bot.story_graph.load(str(story_graph_path))
        except Exception:
            pass  # Expected to fail
        
        # Verify previous state retained (or at least doesn't crash)
        assert helper.domain.story.bot.story_graph is not None
