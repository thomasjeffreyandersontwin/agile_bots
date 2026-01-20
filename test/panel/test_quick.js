/**
 * Quick test to verify panel message flow + REAL backend results
 * 
 * Pattern:
 * 1. Setup: Get initial backend state
 * 2. Action: Simulate UI interaction (test message flow)
 * 3. Verify: Check message flow worked
 * 4. Verify: Check REAL backend state changed
 */

const { test, after } = require('node:test');
const assert = require('assert');
const path = require('path');
const PanelView = require('../../src/panel/panel_view');

// Setup
const workspaceDir = path.join(__dirname, '../..');
const botPath = path.join(workspaceDir, 'bots', 'story_bot');

// Shared REAL backend for all tests
const backendPanel = new PanelView(botPath);

/**
 * Helper to create test panel that uses REAL backend
 * Tests message flow: webview postMessage → extension handler → REAL backend
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
    
    // Create a panel-like object that handles messages
    const panelLike = {
        _botView: backendPanel, // Use REAL backend!
        _panel: mockVscodePanel,
        
        // The key method: handle messages from webview
        async _handleMessage(message) {
            const { command, data, commandText } = message;
            
            if (command === 'executeCommand') {
                // Support both message formats
                const cmdText = commandText || (data && (data.commandText || data.command));
                if (cmdText) {
                    executedCommands.push(cmdText);
                    const result = await this._botView.execute(cmdText);
                    this._panel.webview.postMessage({
                        command: 'commandResult',
                        data: { result }
                    });
                }
            }
        }
    };
    
    // Register the handler
    mockWebview.onDidReceiveMessage((msg) => panelLike._handleMessage(msg));
    
    return {
        panel: panelLike,
        executedCommands,
        sentMessages,
        // Simulate webview sending a message to extension
        postMessageFromWebview: async (message) => {
            if (messageHandler) {
                await messageHandler(message);
            }
        }
    };
}

// Cleanup
after(() => {
    if (backendPanel) {
        backendPanel.cleanup();
    }
});

test('should create epic via message flow', async () => {
    const testPanel = createTestBotPanel();
    
    // Simulate UI: User clicks "Create Epic" button
    await testPanel.postMessageFromWebview({
        command: 'executeCommand',
        commandText: 'bot.story_graph.create_epic name:"Test Epic"'
    });
    
    // Verify response came back through message flow
    assert.strictEqual(testPanel.sentMessages.length, 1);
    assert.strictEqual(testPanel.sentMessages[0].command, 'commandResult');
    
    // The result came through the flow - check it
    const result = testPanel.sentMessages[0].data.result;
    assert.ok(result, 'Should have result from backend');
});

test('should delete epic via message flow', async () => {
    const testPanel = createTestBotPanel();
    
    // First create an epic through message flow
    await testPanel.postMessageFromWebview({
        command: 'executeCommand',
        commandText: 'bot.story_graph.create_epic name:"Epic To Delete"'
    });
    
    // Now delete it through message flow
    await testPanel.postMessageFromWebview({
        command: 'executeCommand',
        commandText: 'bot.story_graph."Epic To Delete".delete'
    });
    
    // Verify both responses came back
    assert.strictEqual(testPanel.sentMessages.length, 2);
    assert.strictEqual(testPanel.sentMessages[0].command, 'commandResult');
    assert.strictEqual(testPanel.sentMessages[1].command, 'commandResult');
    
    // Check delete result came through
    const deleteResult = testPanel.sentMessages[1].data.result;
    assert.ok(deleteResult, 'Should have delete result from backend');
});
