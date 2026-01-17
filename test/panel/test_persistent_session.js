/**
 * Test Persistent CLI Session
 * 
 * Verifies that a single Python CLI process can handle multiple commands
 * without hanging or needing to restart.
 */

const { test, after } = require('node:test');
const assert = require('assert');
const path = require('path');
const fs = require('fs');
const os = require('os');
const BotView = require('../../src/bot/bot_view');

// Track all bot views to ensure cleanup
const activeBotViews = [];

// Force exit after all tests complete
after(() => {
    // Clean up any remaining bot views
    for (const botView of activeBotViews) {
        try {
            botView.cleanup();
        } catch (e) {
            // Ignore cleanup errors
        }
    }
    // Force exit to prevent hanging
    setTimeout(() => process.exit(0), 100);
});

function setupTestWorkspace() {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'panel-test-'));
    return tmpDir;
}

function getBotDirectory() {
    const repoRoot = path.join(__dirname, '../..');
    return path.join(repoRoot, 'bots', 'story_bot');
}

test('TestPersistentSession', { concurrency: false }, async (t) => {
    let botView;
    let tmpPath;

    t.beforeEach(() => {
        tmpPath = setupTestWorkspace();
    });

    t.afterEach(() => {
        if (botView) {
            botView.cleanup();
            const index = activeBotViews.indexOf(botView);
            if (index > -1) activeBotViews.splice(index, 1);
        }
        if (tmpPath) {
            try {
                fs.rmSync(tmpPath, { recursive: true, force: true });
            } catch (e) {
                // Ignore cleanup errors
            }
        }
    });

    await t.test('test_multiple_commands_on_same_session', async () => {
        /**
         * Test that we can call multiple commands on the same Python session
         * without hanging or needing to restart the process.
         */
        const botDir = getBotDirectory();
        botView = new BotView({}, null, tmpPath, botDir);
        activeBotViews.push(botView);
        
        // Call 'current' command multiple times
        const result1 = await botView.execute('current');
        assert(result1, 'First command should return a result');
        
        const result2 = await botView.execute('current');
        assert(result2, 'Second command should return a result');
        
        const result3 = await botView.execute('current');
        assert(result3, 'Third command should return a result');
        
        // Verify all results are similar (same structure)
        assert(typeof result1 === 'object', 'Result 1 should be an object');
        assert(typeof result2 === 'object', 'Result 2 should be an object');
        assert(typeof result3 === 'object', 'Result 3 should be an object');
        
        // Test with different commands
        const status1 = await botView.execute('status');
        assert(status1, 'Status command should return a result');
        assert(typeof status1 === 'object', 'Status should be an object');
        
        const current2 = await botView.execute('current');
        assert(current2, 'Current command after status should still work');
        
        // Verify Python process is still alive
        assert(botView.pythonProcess, 'Python process should still exist');
        assert(botView.pythonProcess.exitCode === null, 'Python process should still be running');
        assert(!botView.pythonProcess.killed, 'Python process should not be killed');
        
        // Explicitly cleanup to ensure process is killed
        botView.cleanup();
        assert(!botView.pythonProcess, 'Python process should be null after cleanup');
    });
});
