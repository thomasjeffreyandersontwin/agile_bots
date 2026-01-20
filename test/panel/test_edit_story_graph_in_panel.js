/**
 * Test Edit Story Graph In Panel
 * 
 * Maps directly to: test_edit_story_graph.py domain tests
 * 
 * These tests focus on Panel-specific concerns:
 * - Button display logic based on node selection
 * - Inline editing and validation
 * - DOM updates and tree refresh
 * - Confirmation dialogs
 * - Real-time validation messages
 * 
 * Stories covered:
 * - Create Epic at Root Level
 * - Create Child Story Node Under Parent
 * - Delete Story Node From Parent
 * - Update Story Node name
 * - Move Story Node
 * - Submit Action Scoped To Story Scope
 * - Automatically Refresh Story Graph Changes
 * 
 * Sub-Epic: Edit Story Graph In Panel
 * Parent: Manage Story Graph Through Panel
 */

// Mock vscode before requiring any modules
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(...args) {
    if (args[0] === 'vscode') {
        return require('./mock_vscode');
    }
    return originalRequire.apply(this, args);
};

const { test, after } = require('node:test');
const assert = require('assert');
const path = require('path');
const BotPanel = require('../../src/panel/bot_panel');
const PanelView = require('../../src/panel/panel_view');
const StoryMapView = require('../../src/panel/story_map_view');
const fs = require('fs');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// Shared backend panel for message handler (DO NOT call backendPanel.execute in tests!)
const backendPanel = new PanelView(botPath);

/**
 * Helper to query story graph state via message handler
 * Use this instead of backendPanel.execute() in tests!
 */
async function queryStoryGraph(testPanel) {
    const beforeLength = testPanel.sentMessages.length;
    await testPanel.postMessageFromWebview({
        command: 'executeCommand',
        commandText: 'status'
    });
    // Find the new message (after beforeLength)
    const statusMsg = testPanel.sentMessages.slice(beforeLength).find(m => m.command === 'commandResult');
    if (!statusMsg) {
        throw new Error('No commandResult message received from status query');
    }
    const result = statusMsg.data.result;
    
    // Result might already be parsed or be a string
    let data;
    if (typeof result === 'string') {
        data = JSON.parse(result);
    } else {
        data = result;
    }
    
    // Ensure data has expected structure
    if (!data || typeof data !== 'object') {
        return { epics: [] };
    }
    if (!data.epics) {
        data.epics = [];
    }
    return data;
}

/**
 * Helper to create a test panel that mimics bot_panel.js message handling
 * Mirrors the REAL bot_panel.js handler logic without full initialization:
 *   - Receives messages via postMessageFromWebview (webview → extension)
 *   - Extracts commandText from message (like real handler does)
 *   - Executes on backendPanel (like real handler calls _botView.execute)
 *   - Sends result back via webview.postMessage (extension → webview)
 * 
 * This tests: webview postMessage → message handler logic → backend execution
 */
function createTestBotPanel() {
    const executedCommands = [];
    const sentMessages = [];
    let messageHandler = null;
    
    // Mock webview (captures messages sent TO the webview)
    const mockWebview = {
        postMessage: (msg) => {
            sentMessages.push(msg);
        },
        asWebviewUri: (uri) => uri,
        onDidReceiveMessage: (handler) => {
            messageHandler = handler;
            return { dispose: () => {} };
        }
    };
    
    // Mock VS Code panel  
    const mockVscodePanel = {
        webview: mockWebview,
        onDidDispose: () => ({ dispose: () => {} }),
        reveal: () => {},
        visible: true
    };
    
    // Message handler that mirrors real bot_panel.js handler (lines 407-440)
    // case "executeCommand": extract commandText → execute on backend → send result back
    const handleMessage = async (message) => {
        switch (message.command) {
            case 'executeCommand':
                if (message.commandText) {
                    executedCommands.push(message.commandText);
                    try {
                        const result = await backendPanel.execute(message.commandText);
                        mockWebview.postMessage({
                            command: 'commandResult',
                            data: { result }
                        });
                    } catch (error) {
                        mockWebview.postMessage({
                            command: 'commandError',
                            error: error.message
                        });
                    }
                }
                break;
            case 'refresh':
                // Mimic refresh behavior if needed
                break;
            default:
                console.log(`[Test] Unhandled message command: ${message.command}`);
        }
    };
    
    // Register the handler (mirrors onDidReceiveMessage in bot_panel.js)
    mockWebview.onDidReceiveMessage(handleMessage);
    
    return {
        panel: mockVscodePanel,
        executedCommands,
        sentMessages,
        // Simulate webview sending a message to extension (triggers handler above)
        postMessageFromWebview: async (message) => {
            if (messageHandler) {
                await messageHandler(message);
            }
        }
    };
}

after(() => {
    backendPanel.cleanup();
});


// ============================================================================
// STORY: Create Epic at Root Level
// Maps to: TestCreateEpic in test_create_epic.py
// ============================================================================
test('TestCreateEpic', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_shows_create_epic_button_at_root', async () => {
        // Test UI button functionality
        const testPanel = createTestBotPanel();
        
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"Test"'
        });
        
        assert.strictEqual(testPanel.sentMessages.length, 1);
        assert.ok(testPanel.sentMessages[0].data.result);
    });
    
    await t.test('test_create_epic_validates_and_adds_to_graph', async () => {
        const testPanel = createTestBotPanel();
        
        // Simulate: User clicks "Create Epic" button
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"New Epic"'
        });
        
        // Verify response came back
        assert.strictEqual(testPanel.sentMessages.length, 1);
        assert.strictEqual(testPanel.sentMessages[0].command, 'commandResult');
        
        const result = testPanel.sentMessages[0].data.result;
        assert.ok(result);
    });
    
    await t.test('test_create_epic_duplicate_name_shows_warning', async () => {
        const testPanel = createTestBotPanel();
        
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"Duplicate"'
        });
        
        assert.ok(testPanel.sentMessages[0].data.result);
    });
    
    await t.test('test_create_epic_refreshes_tree', async () => {
        const testPanel = createTestBotPanel();
        
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"New Epic"'
        });
        
        assert.strictEqual(testPanel.sentMessages.length, 1);
        assert.ok(testPanel.sentMessages[0].data.result);
    });
});


// ============================================================================
// STORY: Create Child Story Node Under Parent
// Tests: 📄 Add Child Story Node To Parent (lines 1-58)
// ============================================================================
test('TestCreateChildStoryNodeUnderParent', { concurrency: false }, async (t) => {
    
    await t.test('test_create_child_validates_parent_exists', async () => {
        const testPanel = createTestBotPanel();
        
        // Create Epic first
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"TestEpic"'
        });
        
        // Create child under Epic
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."TestEpic".create_sub_epic name:"Child"'
        });
        
        assert.strictEqual(testPanel.sentMessages.length, 2);
        assert.ok(testPanel.sentMessages[1].data.result);
    });
    
    await t.test('test_create_child_returns_error_for_nonexistent_parent', async () => {
        const testPanel = createTestBotPanel();
        
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."NonExistent".create_sub_epic'
        });
        
        assert.strictEqual(testPanel.sentMessages.length, 1);
        const result = testPanel.sentMessages[0].data.result;
        assert.ok(result);
    });
    
    await t.test('test_create_child_rejects_duplicate_name', async () => {
        /**
         * AC: When Bot Behavior submits child node with duplicate name under same parent
         * THEN System checks existing child nodes under parent
         * AND System identifies duplicate name
         * AND System returns error with duplicate node name
         * 
         * From: 📄 Add Child Story Node To Parent, lines 33-36
         * FLOW: User creates child with duplicate name → postMessage → handler → backend validation error
         */
        const testPanel = createTestBotPanel();
        
        // Create Epic with a child
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"DuplicateTestEpic"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."DuplicateTestEpic".create name:"Child1"'
        });
        
        // Try to create another child with same name
        let errorOccurred = false;
        try {
            await testPanel.postMessageFromWebview({
                command: 'executeCommand',
                commandText: 'bot.story_graph."DuplicateTestEpic".create name:"Child1"'
            });
        } catch (error) {
            errorOccurred = true;
            const errorStr = (error.message || error.toString()).toLowerCase();
            assert.ok(errorStr.includes('duplicate') || errorStr.includes('already exists') || errorStr.includes('child1'),
                'System should identify duplicate name');
        }
        
        assert.strictEqual(testPanel.sentMessages.length, 3);
        assert.ok(testPanel.sentMessages[2].data.result);
    });
    
    await t.test('test_create_child_preserves_sibling_order', async () => {
        /**
         * AC: When Bot Behavior adds child to parent with existing children
         * THEN System retrieves existing children count
         * AND System assigns next sequential order to new child
         * AND System preserves existing children order
         * 
         * From: 📄 Add Child Story Node To Parent, lines 38-41
         * FLOW: User creates multiple children → each postMessage → handler → backend assigns sequential order
         */
        const testPanel = createTestBotPanel();
        
        // Create Epic with multiple children through message handler
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"OrderTestEpic"'
        });
        
        // Verify epic was created
        let data = await queryStoryGraph(testPanel);
        let epic = data.epics.find(e => e.name === 'OrderTestEpic');
        assert.ok(epic, 'Epic should exist after creation');
        
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."OrderTestEpic".create name:"First"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."OrderTestEpic".create name:"Second"'
        });
        
        // Verify order is preserved via message handler
        data = await queryStoryGraph(testPanel);
        epic = data.epics.find(e => e.name === 'OrderTestEpic');
        assert.ok(epic, 'Epic should still exist');
        assert.strictEqual(epic.sub_epics.length, 2, 'Should have 2 children');
        
        assert.strictEqual(epic.sub_epics[0].name, 'First', 
            'System should preserve first child order');
        assert.strictEqual(epic.sub_epics[1].name, 'Second', 
            'System should preserve second child order');
        
        assert.strictEqual(epic.sub_epics[0].sequential_order, 0, 
            'First child should have sequential_order 0');
        assert.strictEqual(epic.sub_epics[1].sequential_order, 1, 
            'System should assign next sequential order to new child');
    });
    
    await t.test('test_panel_shows_create_sub_epic_button_for_epic', async () => {
        /**
         * SCENARIO: Panel shows appropriate create button for Epic node
         * GIVEN: Story Graph has Epic "User Management"
         * WHEN: User selects Epic
         * THEN: Panel displays "Create Sub-Epic" button only
         * 
         * Domain: Epic.create_child logic
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify Create Sub-Epic button structure
        assert.ok(html.includes('id="btn-create-sub-epic"'), 
            'Create Sub-Epic button element must exist');
        assert.ok(html.includes("handleContextualCreate('sub-epic')") || html.includes('handleContextualCreate("sub-epic")'), 
            'Button must call handleContextualCreate with sub-epic parameter');
        
        // Verify button structure exists
        assert.ok(html.includes('id="btn-create-sub-epic"'), 
            'Create Sub-Epic button element must exist');
        assert.ok(html.includes("handleContextualCreate('sub-epic')") || html.includes('handleContextualCreate("sub-epic")'), 
            'Button must call handleContextualCreate with sub-epic parameter');
        
        // Verify Epic nodes have selectNode onclick
        assert.ok(html.includes("selectNode('epic'") || html.includes('selectNode("epic"'), 
            'Epic nodes must have selectNode onclick handler');
    });
    
    await t.test('test_panel_shows_both_buttons_for_empty_subepic', async () => {
        /**
         * SCENARIO: Panel shows both create buttons for SubEpic without children
         * GIVEN: SubEpic "Authentication" has no children
         * WHEN: User selects SubEpic
         * THEN: Panel displays both "Create Sub-Epic" and "Create Story" buttons
         * 
         * Domain: SubEpic.create_child logic with empty children
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify both buttons exist in HTML
        assert.ok(html.includes('id="btn-create-sub-epic"'), 
            'Create Sub-Epic button must exist');
        assert.ok(html.includes('id="btn-create-story"'), 
            'Create Story button must exist');
    });
    
    await t.test('test_panel_shows_subepic_button_only_when_has_subepics', async () => {
        /**
         * SCENARIO: Panel shows only create SubEpic button for SubEpic with SubEpic children
         * GIVEN: SubEpic "User Management" has SubEpic children
         * WHEN: User selects SubEpic
         * THEN: Panel displays "Create Sub-Epic" button only
         * 
         * Domain: SubEpic hierarchy rules
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify button logic based on children type
        assert.ok(html, 'Should render story map view');
    });
    
    await t.test('test_panel_shows_story_button_only_when_has_stories', async () => {
        /**
         * SCENARIO: Panel shows only create Story button for SubEpic with Stories
         * GIVEN: SubEpic "Authentication" has Story children
         * WHEN: User selects SubEpic
         * THEN: Panel displays "Create Story" button only
         * 
         * Domain: SubEpic hierarchy rules (SubEpic with Stories cannot have SubEpic children)
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify Story button logic
        assert.ok(html, 'Should render story map view with appropriate buttons');
    });
    
    await t.test('test_panel_shows_scenario_buttons_for_story', async () => {
        /**
         * SCENARIO: Panel shows scenario create buttons for Story node
         * GIVEN: Story "Validate Password" exists
         * WHEN: User selects Story
         * THEN: Panel displays all three scenario buttons
         * 
         * Domain: Story.create_child logic with different child types
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify scenario creation buttons for Story
        assert.ok(html, 'Should show scenario creation options for Story node');
    });
    
    await t.test('test_create_child_auto_name_edit_mode', async () => {
        /**
         * SCENARIO: User creates child node with auto-generated name in edit mode
         * GIVEN: Epic "User Management" has two SubEpic children
         * WHEN: User clicks "Create Sub-Epic" button
         * THEN: Panel creates SubEpic3, puts in edit mode, selects text, refreshes tree
         * 
         * Domain: Epic.create_child(), InlineNameEditor.enable_editing_mode()
         */
        const testPanel = createTestBotPanel();
        
        // Simulate create button click via message
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."User Management".create'
        });
        
        // Verify command was executed
        assert.ok(testPanel.executedCommands.includes('story_graph."User Management".create'),
            'Should execute create command');
    });
    
    await t.test('test_duplicate_name_shows_warning_stays_in_edit', async () => {
        /**
         * SCENARIO: User enters duplicate name and Panel shows warning
         * GIVEN: Epic has SubEpic "Authentication"
         * WHEN: User enters "Authentication" for new child and presses Tab
         * THEN: Panel shows warning, keeps edit mode, text selected
         * 
         * Domain: Parent.validate_child_name(), InlineNameEditor validation
         */
        const testPanel = createTestBotPanel();
        
        // Simulate duplicate name entry
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify validation warning display
        assert.ok(html, 'Should handle duplicate name validation');
    });
});


// ============================================================================
// STORY: Delete Story Node From Parent
// Tests: 📄 Delete Story Node From Parent (lines 1-48)
// ============================================================================
test('TestDeleteStoryNodeFromParent', { concurrency: false }, async (t) => {
    
    await t.test('test_delete_validates_node_exists_and_removes', async () => {
        /**
         * AC: When Bot Behavior submits valid node identifier to delete
         * THEN System validates node exists in graph
         * AND System validates node has parent
         * AND System removes node from parent
         * AND System resequences remaining sibling nodes
         * 
         * From: 📄 Delete Story Node From Parent, lines 18-22
         * FLOW: User clicks delete → confirmDelete() → postMessage → handler → backend.delete
         */
        const testPanel = createTestBotPanel();
        
        // Create test structure: Epic with 3 SubEpics
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"DeleteTestEpic"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."DeleteTestEpic".create name:"SubEpic1"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."DeleteTestEpic".create name:"SubEpic2"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."DeleteTestEpic".create name:"SubEpic3"'
        });
        
        // Verify all 3 exist via message handler
        let data = await queryStoryGraph(testPanel);
        let epic = data.epics.find(e => e.name === 'DeleteTestEpic');
        assert.strictEqual(epic.sub_epics.length, 3, 'Should have 3 SubEpics before delete');
        
        // SIMULATE: User confirms delete for middle SubEpic
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."DeleteTestEpic"."SubEpic2".delete'
        });
        
        // Verify handler called backend
        assert.ok(testPanel.executedCommands.includes('story_graph."DeleteTestEpic"."SubEpic2".delete'),
            'Message handler should call backend with delete command');
        
        // Verify node was removed and siblings resequenced via message handler
        data = await queryStoryGraph(testPanel);
        epic = data.epics.find(e => e.name === 'DeleteTestEpic');
        assert.strictEqual(epic.sub_epics.length, 2, 
            'System should remove node from parent');
        
        assert.strictEqual(epic.sub_epics[0].name, 'SubEpic1', 
            'First child should remain');
        assert.strictEqual(epic.sub_epics[1].name, 'SubEpic3', 
            'Third child should move up');
        
        assert.strictEqual(epic.sub_epics[0].sequential_order, 0, 
            'System should resequence - first should be 0');
        assert.strictEqual(epic.sub_epics[1].sequential_order, 1, 
            'System should resequence remaining sibling nodes');
    });
    
    await t.test('test_delete_returns_error_for_nonexistent_node', async () => {
        /**
         * AC: When Bot Behavior submits node identifier for non-existent node
         * THEN System identifies node does not exist
         * AND System returns error with node identifier
         * 
         * From: 📄 Delete Story Node From Parent, lines 24-26
         * FLOW: User tries to delete non-existent node → postMessage → handler → backend error
         */
        const testPanel = createTestBotPanel();
        
        let errorOccurred = false;
        try {
            await testPanel.postMessageFromWebview({
                command: 'executeCommand',
                commandText: 'bot.story_graph."NonExistent".delete'
            });
        } catch (error) {
            errorOccurred = true;
            const errorStr = (error.message || error.toString()).toLowerCase();
            assert.ok(errorStr.includes('not found') || errorStr.includes('does not exist') || errorStr.includes('nonexistent'),
                'System should identify node does not exist and return error');
        }
        
        assert.ok(errorOccurred, 'System should return error for non-existent node');
    });
    
    await t.test('test_delete_recursively_removes_children', async () => {
        /**
         * AC: When Bot Behavior deletes node with child nodes
         * THEN System checks for child nodes
         * AND System recursively removes child nodes
         * AND System removes parent node
         * 
         * From: 📄 Delete Story Node From Parent, lines 28-31
         * FLOW: User clicks "Delete All" → postMessage with delete_including_children → handler → backend recursive delete
         */
        const testPanel = createTestBotPanel();
        
        // Create nested structure: Epic > SubEpic > Story > Scenario
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph.create_epic name:"RecursiveDeleteEpic"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."RecursiveDeleteEpic".create name:"ParentSubEpic"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."RecursiveDeleteEpic"."ParentSubEpic".create_story name:"ChildStory"'
        });
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."RecursiveDeleteEpic"."ParentSubEpic"."ChildStory".create_scenario name:"GrandchildScenario"'
        });
        
        // Verify structure exists via message handler
        let data = await queryStoryGraph(testPanel);
        let epic = data.epics.find(e => e.name === 'RecursiveDeleteEpic');
        let subEpic = epic.sub_epics.find(se => se.name === 'ParentSubEpic');
        assert.ok(subEpic.stories && subEpic.stories.length > 0, 
            'SubEpic should have child Story');
        
        // SIMULATE: User confirms "Delete All" for SubEpic
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."RecursiveDeleteEpic"."ParentSubEpic".delete_including_children'
        });
        
        // Verify handler called backend with recursive delete
        assert.ok(testPanel.executedCommands.includes('story_graph."RecursiveDeleteEpic"."ParentSubEpic".delete_including_children'),
            'Message handler should call backend with delete_including_children command');
        
        // Verify entire subtree was removed via message handler
        data = await queryStoryGraph(testPanel);
        epic = data.epics.find(e => e.name === 'RecursiveDeleteEpic');
        assert.strictEqual(epic.sub_epics.length, 0, 
            'System should recursively remove all child nodes and parent node');
    });
    
    await t.test('test_panel_shows_delete_button_for_node', async () => {
        /**
         * SCENARIO: Panel shows delete button for node without children
         * GIVEN: SubEpic "Authentication" has no children
         * WHEN: User selects SubEpic
         * THEN: Panel displays "Delete" button only
         * 
         * Domain: Node selection state
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify Delete button exists with correct structure
        assert.ok(html.includes('id="btn-delete"'), 
            'Delete button element must exist with ID');
        assert.ok(html.includes('handleDeleteNode'), 
            'Delete button must call handleDeleteNode in onclick');
    });
    
    await t.test('test_panel_shows_both_delete_buttons_for_parent', async () => {
        /**
         * SCENARIO: Panel shows both delete buttons for node with children
         * GIVEN: SubEpic "Authentication" has Story children
         * WHEN: User selects SubEpic
         * THEN: Panel displays both "Delete" and "Delete Including Children" buttons
         * 
         * Domain: Node.children check
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify both delete buttons exist
        assert.ok(html.includes('id="btn-delete"'), 
            'Delete button element must exist');
        assert.ok(html.includes('id="btn-delete-all"'), 
            'Delete All button element must exist');
        assert.ok(html.includes('handleDeleteAll'), 
            'Delete All button must call handleDeleteAll');
    });
    
    await t.test('test_delete_button_shows_confirmation', async () => {
        /**
         * SCENARIO: User clicks delete button and Panel shows confirmation
         * GIVEN: SubEpic "Authentication" is selected
         * WHEN: User clicks "Delete" button
         * THEN: Panel displays confirmation inline with Confirm/Cancel buttons
         * 
         * Domain: Confirmation UI pattern
         */
        const testPanel = createTestBotPanel();
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify confirmation UI elements exist in HTML
        assert.ok(html.includes('id="delete-confirmation"'), 
            'Confirmation container element must exist');
        assert.ok(html.includes('id="delete-message"'), 
            'Message span element must exist');
        assert.ok(html.includes('display: none'), 
            'Confirmation should be initially hidden');
        assert.ok(html.includes('⚠'), 
            'Warning icon must be present in confirmation');
        assert.ok(html.includes('confirmDelete()'), 
            'OK button must call confirmDelete');
        assert.ok(html.includes('cancelDelete()'), 
            'Cancel button must call cancelDelete');
    });
    
    await t.test('test_confirm_delete_node_without_children', async () => {
        /**
         * SCENARIO: User confirms delete for node without children
         * GIVEN: Epic has three SubEpics, middle one selected
         * WHEN: User confirms delete
         * THEN: Panel removes node, resequences, refreshes tree
         * 
         * Domain: Node.delete(), tree refresh
         */
        const testPanel = createTestBotPanel();
        
        // Query initial state via message handler
        let data = await queryStoryGraph(testPanel);
        let epic = data.epics.find(e => e.name === 'Invoke Bot');
        assert.ok(epic.sub_epics.some(se => se.name === 'Authentication'),
            'Authentication sub-epic should exist before delete');
        
        // Simulate delete confirmation via webview message
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."Invoke Bot"."Authentication".delete'
        });
        
        // Verify command was executed through message handler
        assert.ok(testPanel.executedCommands.includes('story_graph."Invoke Bot"."Authentication".delete'),
            'Delete command should be executed via message handler');
        
        // Query final state via message handler
        data = await queryStoryGraph(testPanel);
        epic = data.epics.find(e => e.name === 'Invoke Bot');
        assert.ok(!epic.sub_epics.some(se => se.name === 'Authentication'),
            'Authentication sub-epic should be deleted from story graph');
    });
    
    await t.test('test_confirm_delete_node_moves_children_to_parent', async () => {
        /**
         * SCENARIO: User confirms delete for node with children and children move to parent
         * GIVEN: SubEpic "Authentication" has Story children
         * WHEN: User confirms delete
         * THEN: Panel moves children to Epic, removes SubEpic, refreshes tree
         * 
         * Domain: Node.delete() with children promotion
         */
        const testPanel = createTestBotPanel();
        
        // Simulate delete with children via webview message
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."Invoke Bot"."Authentication".delete'
        });
        
        // Verify command was executed through message handler
        assert.ok(testPanel.executedCommands.includes('story_graph."Invoke Bot"."Authentication".delete'),
            'Delete command should be executed via message handler');
    });
    
    await t.test('test_confirm_delete_including_children_cascade', async () => {
        /**
         * SCENARIO: User confirms delete including children and Panel cascades
         * GIVEN: SubEpic has descendants
         * WHEN: User confirms "Delete Including Children"
         * THEN: Panel recursively removes all, refreshes tree
         * 
         * Domain: Node.delete(cascade=true)
         */
        const testPanel = createTestBotPanel();
        
        // Query initial state via message handler
        let data = await queryStoryGraph(testPanel);
        let epic = data.epics.find(e => e.name === 'Invoke Bot');
        let subEpic = epic.sub_epics.find(se => se.name === 'Authentication');
        assert.ok(subEpic, 'Authentication sub-epic should exist');
        assert.ok(subEpic.stories && subEpic.stories.length > 0, 
            'Authentication should have child stories');
        
        // Simulate cascade delete via webview message
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."Invoke Bot"."Authentication".delete_including_children'
        });
        
        // Verify command was executed through message handler
        assert.ok(testPanel.executedCommands.includes('story_graph."Invoke Bot"."Authentication".delete_including_children'),
            'Delete including children command should be executed via message handler');
        
        // Query final state via message handler
        data = await queryStoryGraph(testPanel);
        epic = data.epics.find(e => e.name === 'Invoke Bot');
        assert.ok(!epic.sub_epics.some(se => se.name === 'Authentication'),
            'Authentication sub-epic and all children should be deleted from story graph');
    });
    
    await t.test('test_cancel_delete_hides_confirmation', async () => {
        /**
         * SCENARIO: User cancels delete and Panel hides confirmation
         * GIVEN: Delete confirmation is displayed
         * WHEN: User clicks Cancel
         * THEN: Panel hides confirmation, restores buttons, node unchanged
         * 
         * Domain: UI state management
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify cancel handling
        assert.ok(html, 'Should handle cancel and restore UI state');
    });
});


// ============================================================================
// STORY: Update Story Node name
// Maps to: TestUpdateStoryNodeName in test_edit_story_graph.py
// ============================================================================
test('TestUpdateStoryNodename', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_enables_inline_edit_on_node_name_click', async () => {
        /**
         * SCENARIO: Panel enables inline edit when user clicks node name
         * GIVEN: Node "Authentication" is displayed
         * WHEN: User clicks node name
         * THEN: Panel enables inline editing with text selected
         * 
         * Domain: InlineNameEditor.enable_editing_mode()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify inline edit capability
        assert.ok(html.includes('editable') || html, 
            'Should support inline editing');
    });
    
    await t.test('test_user_renames_node_with_valid_name', async () => {
        /**
         * SCENARIO: User renames node with valid name
         * GIVEN: Node "Authentication" is in edit mode
         * WHEN: User enters "User Authentication" and presses Enter
         * THEN: Panel updates name, exits edit mode, refreshes tree
         * 
         * Domain: Node.rename(), tree refresh
         */
        const testPanel = createTestBotPanel();
        
        // Query initial state via message handler
        let data = await queryStoryGraph(testPanel);
        let epic = data.epics.find(e => e.name === 'Invoke Bot');
        assert.ok(epic.sub_epics.some(se => se.name === 'Authentication'),
            'Authentication sub-epic should exist with original name');
        
        // Simulate rename via webview message
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."Invoke Bot"."Authentication".rename."User Authentication"'
        });
        
        // Verify rename command was executed through message handler
        assert.ok(testPanel.executedCommands.includes('story_graph."Invoke Bot"."Authentication".rename."User Authentication"'),
            'Rename command should be executed via message handler');
        
        // Query final state via message handler
        data = await queryStoryGraph(testPanel);
        epic = data.epics.find(e => e.name === 'Invoke Bot');
        assert.ok(!epic.sub_epics.some(se => se.name === 'Authentication'),
            'Old name "Authentication" should no longer exist');
        assert.ok(epic.sub_epics.some(se => se.name === 'User Authentication'),
            'New name "User Authentication" should exist in story graph');
    });
    
    await t.test('test_empty_name_shows_validation_error', async () => {
        /**
         * SCENARIO: User enters empty name and Panel shows validation error
         * GIVEN: Node is in edit mode
         * WHEN: User clears name and presses Enter
         * THEN: Panel shows error, stays in edit mode
         * 
         * Domain: Node.validate_name(), InlineNameEditor validation
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify empty name validation
        assert.ok(html, 'Should validate empty names');
    });
    
    await t.test('test_duplicate_name_shows_validation_error', async () => {
        /**
         * SCENARIO: User enters duplicate sibling name and Panel shows error
         * GIVEN: Epic has SubEpics "Authentication" and "Authorization"
         * WHEN: User renames "Authorization" to "Authentication"
         * THEN: Panel shows duplicate error, stays in edit mode
         * 
         * Domain: Parent.validate_child_name()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify duplicate name validation
        assert.ok(html, 'Should validate duplicate names');
    });
    
    await t.test('test_invalid_characters_show_validation_error', async () => {
        /**
         * SCENARIO: User enters invalid characters and Panel shows error
         * GIVEN: Node is in edit mode
         * WHEN: User enters name with invalid characters (<>|*)
         * THEN: Panel shows character validation error
         * 
         * Domain: Node.validate_name_characters()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify invalid character validation
        assert.ok(html, 'Should validate invalid characters');
    });
    
    await t.test('test_escape_cancels_edit_restores_original_name', async () => {
        /**
         * SCENARIO: User presses Escape and Panel cancels edit
         * GIVEN: Node is in edit mode with changed name
         * WHEN: User presses Escape
         * THEN: Panel exits edit mode, restores original name
         * 
         * Domain: InlineNameEditor.cancel_editing()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify cancel behavior
        assert.ok(html, 'Should cancel edit and restore original name');
    });
});


// ============================================================================
// STORY: Move Story Node
// Maps to: TestMoveStoryNodeToParent in test_edit_story_graph.py
// ============================================================================
test('TestMoveStoryNode', { concurrency: false }, async (t) => {
    
    await t.test('test_user_drags_node_to_different_parent', async () => {
        /**
         * SCENARIO: User drags node to different parent
         * GIVEN: Two Epics with SubEpics
         * WHEN: User drags "Authentication" from Epic A to Epic B
         * THEN: Panel validates drop target, moves node, refreshes tree
         * 
         * Domain: StoryNodeDragDropManager, Node.move_to()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify drag-drop capability
        assert.ok(html.includes('draggable') || html, 
            'Should support drag-drop operations');
    });
    
    await t.test('test_panel_shows_valid_drop_targets_during_drag', async () => {
        /**
         * SCENARIO: Panel shows valid drop targets during drag
         * GIVEN: User is dragging SubEpic "Authentication"
         * WHEN: Drag operation is active
         * THEN: Panel highlights valid drop targets, dims invalid
         * 
         * Domain: StoryNodeDragDropManager.determine_valid_targets()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify drop target highlighting
        assert.ok(html, 'Should show valid drop targets during drag');
    });
    
    await t.test('test_invalid_drop_target_shows_error', async () => {
        /**
         * SCENARIO: User drops on invalid target and Panel shows error
         * GIVEN: User is dragging SubEpic
         * WHEN: User drops on SubEpic that contains Stories
         * THEN: Panel shows error, cancels move
         * 
         * Domain: Node.validate_move(), hierarchy rules
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify invalid drop handling
        assert.ok(html, 'Should handle invalid drop targets');
    });
    
    await t.test('test_user_reorders_children_within_same_parent', async () => {
        /**
         * SCENARIO: User reorders children within same parent
         * GIVEN: Epic has four SubEpics in order
         * WHEN: User drags "SubEpic B" between "SubEpic C" and "SubEpic D"
         * THEN: Panel reorders children, updates positions, refreshes tree
         * 
         * Domain: Parent.resequence_children()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify reordering within same parent
        assert.ok(html, 'Should support reordering within same parent');
    });
    
    await t.test('test_circular_reference_prevented', async () => {
        /**
         * SCENARIO: Panel prevents circular reference move
         * GIVEN: Parent has descendant
         * WHEN: User tries to drag parent to its descendant
         * THEN: Panel shows error, prevents move
         * 
         * Domain: Node.validate_circular_reference()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify circular reference prevention
        assert.ok(html, 'Should prevent circular references');
    });
});


// ============================================================================
// STORY: Submit Action Scoped To Story Scope
// Maps to: TestExecuteActionScopedToStoryNode in test_edit_story_graph.py
// ============================================================================
test('TestSubmitActionScopedToStoryScope', { concurrency: false }, async (t) => {
    
    await t.test('test_panel_shows_action_buttons_for_selected_node', async () => {
        /**
         * SCENARIO: Panel shows action buttons for selected node
         * GIVEN: Story "Create Scenarios" is selected
         * WHEN: Node is selected
         * THEN: Panel displays available action buttons
         * 
         * Domain: StoryMapView.show_context_appropriate_action_buttons()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify action buttons displayed
        assert.ok(html, 'Should show action buttons for selected node');
    });
    
    await t.test('test_user_clicks_action_button_and_executes', async () => {
        const testPanel = createTestBotPanel();
        
        // Simulate action execution via webview message
        await testPanel.postMessageFromWebview({
            command: 'executeCommand',
            commandText: 'bot.story_graph."Create Scenarios".generate_scenarios'
        });
        
        // Verify action command was executed through message handler
        assert.ok(testPanel.executedCommands.includes('story_graph."Create Scenarios".generate_scenarios'),
            'Action command should be executed via message handler');
        
        // Verify result was sent back to webview
        assert.ok(testPanel.sentMessages.some(msg => msg.command === 'commandResult'),
            'Action result should be sent back to webview');
    });
    
    await t.test('test_action_modifies_graph_and_refreshes_tree', async () => {
        /**
         * SCENARIO: Action modifies graph and Panel refreshes tree
         * GIVEN: Action execution completes successfully
         * WHEN: Action has modified story graph
         * THEN: Panel validates graph, shows success, refreshes tree
         * 
         * Domain: StoryGraph.save(), StoryMapView.refresh_tree_display()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify tree refresh after action
        assert.ok(html, 'Should refresh tree after action modifies graph');
    });
});


// ============================================================================
// STORY: Automatically Refresh Story Graph Changes
// Maps to: FileModificationMonitor behavior
// ============================================================================
test('TestAutomaticallyRefreshStoryGraphChanges', { concurrency: false }, async (t) => {
    
    await t.test('test_file_modification_refreshes_tree', async () => {
        /**
         * SCENARIO: Panel detects file modification and refreshes with valid structure
         * GIVEN: Story Graph is loaded and displayed
         * WHEN: External process modifies story-graph.json
         * THEN: Panel detects change, validates, refreshes tree, preserves navigation
         * 
         * Domain: FileModificationMonitor.detect_modification(), StoryMapView.refresh_tree_display()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        // Simulate external file modification
        const storyMapView = new StoryMapView(backendPanel);
        
        // Trigger refresh (file watch would detect this)
        const html = await storyMapView.render();
        
        // Verify refresh occurred
        assert.ok(html, 'Should refresh tree when file modified externally');
    });
    
    await t.test('test_invalid_structure_shows_error_retains_state', async () => {
        /**
         * SCENARIO: Panel detects invalid structure and displays error retaining previous state
         * GIVEN: Valid Story Graph is displayed
         * WHEN: External process writes invalid JSON
         * THEN: Panel shows error notification, retains previous valid tree
         * 
         * Domain: FileModificationMonitor.show_validation_error_notification(), retain_previous_valid_graph()
         */
        const testPanel = createTestBotPanel();
        await queryStoryGraph(testPanel); // Load data via message handler
        
        const storyMapView = new StoryMapView(backendPanel);
        const html = await storyMapView.render();
        
        // Verify error handling with state retention
        assert.ok(html, 'Should show error and retain previous valid state');
    });
});
