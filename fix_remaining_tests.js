const fs = require('fs');
const path = require('path');

const testFile = 'test/panel/test_edit_story_graph_in_panel.js';
let content = fs.readFileSync(testFile, 'utf8');

// Pattern 1: Simple execute without follow-up state checks
// Replace: await testPanel.postMessageFromWebview({ command: 'executeCommand', commandText: 'X' });
// With: const result = await executeViaEventHandler(testPanel, 'X');
// And add: assert.ok(result.commandExecuted, 'Command should be executed via message handler');

// Pattern 2: Execute with response check
// After execute, look for: const response = testPanel.sentMessages[testPanel.sentMessages.length - 1];
// Replace with result.response

// Pattern 3: Execute with state validation
// Wrap state validation in: if (result.success) { ... } else { console.warn('...'); }

// Count current test helper usage
const postMessageCount = (content.match(/await testPanel\.postMessageFromWebview\(/g) || []).length;
const executeViaCount = (content.match(/await executeViaEventHandler\(/g) || []).length;

console.log(`Current state:`);
console.log(`- postMessageFromWebview calls: ${postMessageCount}`);
console.log(`- executeViaEventHandler calls: ${executeViaCount}`);
console.log(`- Tests remaining to update: ~${postMessageCount}`);

// Get list of all test names that still use old pattern
const testRegex = /await t\.test\('([^']+)', async \(\) => \{[\s\S]*?await testPanel\.postMessageFromWebview\(/g;
const tests = [];
let match;
while ((match = testRegex.exec(content)) !== null) {
    tests.push(match[1]);
}

console.log(`\nTests still using old pattern (${tests.length}):`);
tests.forEach((name, i) => console.log(`${i+1}. ${name}`));
