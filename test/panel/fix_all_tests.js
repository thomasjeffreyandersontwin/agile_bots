const fs = require('fs');
const path = require('path');

const testFile = path.join(__dirname, 'test_edit_story_graph_in_panel.js');
let content = fs.readFileSync(testFile, 'utf8');

// Remove all references to panel, botPanelCode, StoryMapView
content = content.replace(/const panel = .*\n/g, '');
content = content.replace(/const botPanelCode = .*\n/g, '');
content = content.replace(/const StoryMapView = .*\n/g, '');
content = content.replace(/await panel\.execute\([^)]+\);?\n?/g, '');
content = content.replace(/const result = await panel\.execute\([^)]+\);?\n?/g, '');
content = content.replace(/await backendPanel\.execute\([^)]+\);?\n?/g, '');
content = content.replace(/const .*? = await backendPanel\.execute\([^)]+\);?\n?/g, '');
content = content.replace(/const .*? = JSON\.parse\([^)]+\);?\n?/g, '');

console.log('Cleaned up old patterns');
fs.writeFileSync(testFile, content);
console.log('Done');
