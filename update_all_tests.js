const fs = require('fs');

// Read the test file
let content = fs.readFileSync('test/panel/test_edit_story_graph_in_panel.js', 'utf8');

// Save backup
fs.writeFileSync('test/panel/test_edit_story_graph_in_panel.js.before_batch_update', content);

// Replace pattern: Simple postMessageFromWebview + executedCommands check -> executeViaEventHandler
// Find all instances where we have:
//   await testPanel.postMessageFromWebview({ ... commandText: 'COMMAND' });
//   ...
//   assert.ok(testPanel.executedCommands.includes('COMMAND'));
// And replace with:
//   const result = await executeViaEventHandler(testPanel, 'COMMAND');
//   assert.ok(result.commandExecuted, ...);

// Pattern 1: Single command with executedCommands check right after
content = content.replace(
    /await testPanel\.postMessageFromWebview\(\{\s+command: 'executeCommand',\s+commandText: '([^']+)'\s+\}\);\s+\/\/ Verify command( was)? executed( through message handler)?\s+assert\.ok\(testPanel\.executedCommands\.includes\('([^']+)'\),\s+'([^']+)'\);/g,
    `const result = await executeViaEventHandler(testPanel, '$1');\n        \n        // VERIFY: Event handling worked\n        assert.ok(result.commandExecuted, '$5');`
);

// Pattern 2: Command without immediate executedCommands check
content = content.replace(
    /\/\/ SIMULATE: ([^\n]+)\s+await testPanel\.postMessageFromWebview\(\{\s+command: 'executeCommand',\s+commandText: '([^']+)'\s+\}\);/g,
    `// SIMULATE: $1\n        const result = await executeViaEventHandler(testPanel, '$2');`
);

fs.writeFileSync('test/panel/test_edit_story_graph_in_panel.js', content);
console.log('Updated all tests to use executeViaEventHandler pattern');
