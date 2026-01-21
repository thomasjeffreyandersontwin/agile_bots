const fs = require('fs');

const testFile = 'test/panel/test_edit_story_graph_in_panel.js';
let content = fs.readFileSync(testFile, 'utf8');

// Pattern 1: Simple postMessage without state validation
// await testPanel.postMessageFromWebview({ command: 'executeCommand', commandText: 'X' });
// → const result = await executeViaEventHandler(testPanel, 'X');

const pattern1 = /await testPanel\.postMessageFromWebview\(\{\s*command: 'executeCommand',\s*commandText: '([^']+)'\s*\}\);/g;

let count = 0;
content = content.replace(pattern1, (match, commandText) => {
    count++;
    return `const r${count} = await executeViaEventHandler(testPanel, '${commandText}');`;
});

console.log(`Replaced ${count} postMessageFromWebview calls with executeViaEventHandler`);

// Pattern 2: Replace response checks
// const response = testPanel.sentMessages[testPanel.sentMessages.length - 1];
// This should already be handled by using result.response

content = content.replace(
    /const response = testPanel\.sentMessages\[testPanel\.sentMessages\.length - 1\];/g,
    '// Response already available in result.response'
);

console.log('Replaced response checks');

// Write back
fs.writeFileSync(testFile, content, 'utf8');
console.log('File updated!');
