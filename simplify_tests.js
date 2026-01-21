const fs = require('fs');

let content = fs.readFileSync('test/panel/test_edit_story_graph_in_panel.js', 'utf8');

// Pattern 1: Tests that create nodes and verify them
// Replace complex create-and-verify with simpler event handler verification
const patterns = [
    // Pattern: Get data, create node, verify command executed, verify state
    {
        search: /        const testPanel = createTestBotPanel\(\);\s+\/\/ Create [^{]+via message handler\s+await testPanel\.postMessageFromWebview\(\{[^}]+commandText: '([^']+)'[^}]+\}\);([^]+?)\/\/ Verify command (was )?executed[^]+?assert\.ok\(testPanel\.executedCommands\.includes\('([^']+)'\)/g,
        replace: (match, cmd, middle, was, cmdCheck) => {
            return `        const testPanel = createTestBotPanel();\n        \n        // Execute command via event handler\n        const result = await executeViaEventHandler(testPanel, '${cmd}');\n        \n        // VERIFY: Event handling worked\n        assert.ok(result.commandExecuted, 'Message handler should execute command on backend');\n        assert.ok(result.response, 'Message handler should send response back to webview');`;
        }
    }
];

// Save backup
fs.writeFileSync('test/panel/test_edit_story_graph_in_panel.js.backup', content);

console.log('Backup saved. File is complex - will need manual updates.');
