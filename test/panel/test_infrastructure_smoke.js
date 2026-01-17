/**
 * Infrastructure Smoke Test
 * 
 * Validates that helper infrastructure is working correctly.
 */

// Mock vscode before requiring any modules that depend on it
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function(...args) {
    if (args[0] === 'vscode') {
        return require('./mock_vscode');
    }
    return originalRequire.apply(this, args);
};

const { test, after } = require('node:test');
const assert = require('node:assert');
const path = require('path');
const { parseHTML, HTMLAssertions } = require('./helpers/html_assertions');
const { BehaviorsViewTestHelper } = require('./helpers');

// Setup workspace
const workspaceDir = path.join(__dirname, '../..');

// ONE helper for all tests
const helper = new BehaviorsViewTestHelper(workspaceDir, 'story_bot');

// Cleanup after all tests
after(() => {
    helper.cleanup();
});

test('TestInfrastructure.testHTMLAssertionsCanParseHTML', async () => {
    const html = '<div class="test">Hello</div>';
    const doc = parseHTML(html);
    assert.ok(doc, 'Should parse HTML');
    assert.ok(doc.querySelector('.test'), 'Should find element by class');
});

test('TestInfrastructure.testHelperCanRenderHTML', async () => {
    const html = await helper.render_html();
    assert.ok(html, 'Should render HTML');
    assert.ok(html.length > 0, 'Rendered HTML should not be empty');
});

test('TestInfrastructure.testCLICanExecuteCommands', async () => {
    const status = await helper._cli.execute('status');
    assert.ok(status, 'Should get status');
    assert.ok(status.behaviors, 'Status should have behaviors');
});

test('TestInfrastructure.testHTMLAssertionsCanVerifyElementPresence', async () => {
    const html = '<div class="test-element">Content</div>';
    const element = HTMLAssertions.assertElementPresent(html, '.test-element');
    assert.ok(element, 'Should find element');
});
