const fs = require('fs');
const testFile = 'test/panel/test_edit_story_graph_in_panel.js';
let content = fs.readFileSync(testFile, 'utf8');

// Strategy: Find tests that still use "await testPanel.postMessageFromWebview" and haven't been updated
// Count how many still need updating
const testMatches = content.match(/await t\.test\('[^']+', async \(\) => \{[^}]*await testPanel\.postMessageFromWebview\([^)]+\)/g);

console.log(`Found ${testMatches ? testMatches.length : 0} tests still using old pattern`);

// Pattern: Replace simple single postMessageFromWebview calls with executeViaEventHandler
// This handles tests with single command execution followed by assertions

let updateCount = 0;

// Pattern 1: Simple command with state check
// await testPanel.postMessageFromWebview({ command: 'executeCommand', commandText: 'CMD' });
// ... some lines ...
// assert checks

const lines = content.split('\n');
const newLines = [];
let i = 0;

while (i < lines.length) {
    const line = lines[i];
    
    // Check if this line has postMessageFromWebview
    if (line.includes('await testPanel.postMessageFromWebview') && line.includes('executeCommand')) {
        // Extract command
        const match = line.match(/commandText: '([^']+)'/);
        if (match) {
            const cmd = match[1];
            const indent = line.match(/^(\s*)/)[1];
            // Replace with executeViaEventHandler
            newLines.push(`${indent}const cmdResult${updateCount} = await executeViaEventHandler(testPanel, '${cmd}');`);
            updateCount++;
            i++;
            continue;
        }
    }
    
    newLines.push(line);
    i++;
}

content = newLines.join('\n');

console.log(`Updated ${updateCount} postMessageFromWebview calls`);

// Write back
fs.writeFileSync(testFile, content, 'utf8');
console.log('File updated!');
console.log('\nNOTE: You will still need to add conditional error handling manually:');
console.log('  if (cmdResultN.success) { ... state validation ... } else { console.warn(...) }');
