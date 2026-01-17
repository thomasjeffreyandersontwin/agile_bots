/**
 * Run all panel tests with proper cleanup at the end.
 */

const { spawn } = require('child_process');
const path = require('path');

// Get all test files except this one
const testFiles = [
    'test_behaviors_view.js',
    'test_behaviors_view_example.js',
    'test_display_instructions.js',
    'test_get_help.js',
    'test_infrastructure_smoke.js',
    'test_instructions_view.js',
    'test_manage_panel_session.js',
    'test_manage_scope.js',
    'test_navigate_and_execute.js',
    'test_navigate_behaviors.js',
    'test_scope_view.js',
    'test_smoke.js'
].map(f => path.join(__dirname, f));

// Run node test with all files
const nodeProcess = spawn('node', ['--test', ...testFiles], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '../..')
});

nodeProcess.on('close', (code) => {
    // Force exit to ensure clean shutdown
    process.exit(code || 0);
});
