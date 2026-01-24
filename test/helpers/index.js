/**
 * Panel Test Helpers Index
 * Central export for all test helper classes
 */

const BotViewTestHelper = require('./bot_view_test_helper');
const BehaviorsViewTestHelper = require('./behaviors_view_test_helper');
const ScopeViewTestHelper = require('./scope_view_test_helper');
const InstructionsViewTestHelper = require('./instructions_view_test_helper');
const { parseHTML, HTMLAssertions } = require('./html_assertions');

module.exports = {
    BotViewTestHelper,
    BehaviorsViewTestHelper,
    ScopeViewTestHelper,
    InstructionsViewTestHelper,
    parseHTML,
    HTMLAssertions
};
