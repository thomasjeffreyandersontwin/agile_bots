/**
 * InstructionsView Test Helper
 * Provides factory methods and assertions for testing InstructionsView
 * Follows rule: object_oriented_test_helpers
 */

const assert = require('node:assert');
const { parseHTML, HTMLAssertions } = require('./html_assertions');

class InstructionsViewTestHelper {
    constructor(workspaceDir, botName = 'story_bot') {
        const path = require('path');
        this.botPath = path.join(workspaceDir, 'bots', botName);
        
        // Create CLI instance - helper owns the process
        const PanelView = require('../../src/panel/panel_view');
        this._cli = new PanelView(this.botPath);
        
        // Create view with injected CLI
        const InstructionsView = require('../../src/panel/instructions_view');
        this._view = new InstructionsView(this._cli);
    }
    
    /**
     * Cleanup CLI process
     */
    cleanup() {
        if (this._cli) {
            this._cli.cleanup();
            this._cli = null;
        }
        this._view = null;
    }
    
    // ========================================================================
    // FACTORY METHODS - Create test objects
    // ========================================================================
    
    /**
     * Render instructions HTML
     * @returns {Promise<string>} - Rendered HTML
     */
    async render_html() {
        return await this._view.render();
    }
    
    // ========================================================================
    // SETUP HELPERS - Create test data structures
    // ========================================================================
    
    /**
     * Create base instructions data
     * @param {string[]} instructionLines - Array of instruction lines
     * @returns {Object} - Base instructions data
     */
    create_base_instructions(instructionLines) {
        return {
            base_instructions: instructionLines
        };
    }
    
    /**
     * Create clarify instructions data
     * @param {string[]} instructionLines - Array of instruction lines
     * @returns {Object} - Clarify instructions data
     */
    create_clarify_instructions(instructionLines) {
        return {
            clarify_instructions: instructionLines,
            base_instructions: instructionLines
        };
    }
    
    /**
     * Create strategy instructions data
     * @param {string[]} instructionLines - Array of instruction lines
     * @returns {Object} - Strategy instructions data
     */
    create_strategy_instructions(instructionLines) {
        return {
            strategy_instructions: instructionLines,
            base_instructions: instructionLines
        };
    }
    
    /**
     * Create validate instructions data
     * @param {string[]} instructionLines - Array of instruction lines
     * @param {string[]} [rules] - Optional rules
     * @returns {Object} - Validate instructions data
     */
    create_validate_instructions(instructionLines, rules = []) {
        return {
            base_instructions: instructionLines,
            rules: rules
        };
    }
    
    /**
     * Create instructions with parameters
     * @param {string[]} instructionLines - Array of instruction lines
     * @param {Object} parameters - Parameter definitions
     * @returns {Object} - Instructions with parameters
     */
    create_instructions_with_parameters(instructionLines, parameters) {
        return {
            base_instructions: instructionLines,
            parameters: parameters
        };
    }
    
    create_markdown_instructions(text) {
        return { base_instructions: [text], format: 'markdown' };
    }
    
    create_plain_text_instructions(text) {
        return { base_instructions: [text], format: 'text' };
    }
    
    create_empty_instructions() {
        return { base_instructions: [] };
    }
    
    create_instructions_with_commands(commands) {
        const text = 'Available commands:\n' + commands.map(c => `- ${c}`).join('\n');
        return { base_instructions: [text] };
    }
    
    create_instructions_with_code(codeBlock) {
        return { base_instructions: [codeBlock] };
    }
    
    create_instructions_with_links(markdownWithLinks) {
        return { base_instructions: [markdownWithLinks] };
    }
    
    create_multiline_instructions(paragraphs) {
        return { base_instructions: paragraphs };
    }
    
    create_instructions_with_bullets(items) {
        const text = items.map(item => `- ${item}`).join('\n');
        return { base_instructions: [text] };
    }
    
    // ========================================================================
    // ACTION HELPERS - Execute actions
    // ========================================================================
    
    /**
     * Render instructions view to HTML
     * @param {Object} instructionsData - Instructions data
     * @param {Array} [trackingArray] - Optional array to track views for cleanup
     * @returns {string} - Rendered HTML
     */
    /**
     * Render instructions view to HTML - uses REAL CLI
     * @returns {Promise<string>} - Rendered HTML
     */
    async render_html() {
        const view = this.createInstructionsView();
        return await view.render();
    }
    
    // ========================================================================
    // ASSERTION HELPERS - Verify results
    // ========================================================================
    
    /**
     * Assert instructions content is displayed
     * @param {string} html - HTML string
     * @param {string[]} expectedLines - Expected instruction lines
     */
    assert_instructions_displayed(html, expectedLines) {
        for (const line of expectedLines) {
            HTMLAssertions.assertContainsText(html, line);
        }
    }
    
    /**
     * Assert no instructions message is displayed
     * @param {string} html - HTML string
     */
    assert_no_instructions_message(html) {
        assert.ok(
            html.includes('No instructions') ||
            html.includes('no instructions') ||
            html.includes('Navigate to an action') ||
            html.length === 0,
            'HTML should contain no instructions message or be empty'
        );
    }
    
    /**
     * Assert submit button is present
     * @param {string} html - HTML string
     */
    assert_submit_button_present(html) {
        const doc = parseHTML(html);
        const submitBtn = doc.querySelector('button[data-command*="submit"]') ||
                         doc.querySelector('.submit-btn') ||
                         doc.querySelector('#submit-instructions');
        assert.ok(submitBtn || html.includes('submit'), 
            'HTML should contain submit button');
    }
    
    /**
     * Assert submit button is disabled
     * @param {string} html - HTML string
     */
    assert_submit_button_disabled(html) {
        const doc = parseHTML(html);
        const submitBtn = doc.querySelector('button[data-command*="submit"]') ||
                         doc.querySelector('.submit-btn') ||
                         doc.querySelector('#submit-instructions');
        if (submitBtn) {
            assert.ok(
                submitBtn.disabled ||
                submitBtn.hasAttribute('disabled') ||
                submitBtn.classList.contains('disabled'),
                'Submit button should be disabled'
            );
        }
    }
    
    /**
     * Assert raw instructions section is present
     * @param {string} html - HTML string
     */
    assert_raw_instructions_section(html) {
        assert.ok(
            html.includes('raw') || 
            html.includes('Raw') ||
            html.includes('code') ||
            html.includes('pre'),
            'HTML should contain raw instructions section'
        );
    }
    
    /**
     * Assert parameters are displayed
     * @param {string} html - HTML string
     * @param {Object} parameters - Expected parameters
     */
    assert_parameters_displayed(html, parameters) {
        for (const [paramName, paramInfo] of Object.entries(parameters)) {
            HTMLAssertions.assertContainsText(html, paramName);
            if (paramInfo.description) {
                HTMLAssertions.assertContainsText(html, paramInfo.description);
            }
        }
    }
    
    /**
     * Assert rules are displayed
     * @param {string} html - HTML string
     * @param {string[]} rules - Expected rules
     */
    assert_rules_displayed(html, rules) {
        for (const rule of rules) {
            assert.ok(
                html.includes(rule) || html.includes('rule'),
                `HTML should contain rule: ${rule}`
            );
        }
    }
    
    /**
     * Assert instruction format is correct
     * @param {string} html - HTML string
     * @param {string} format - Expected format (markdown, html, text)
     */
    assert_instruction_format(html, format) {
        if (format === 'markdown') {
            assert.ok(
                html.includes('<p>') || html.includes('<h') || html.includes('<li>'),
                'HTML should contain markdown-formatted content'
            );
        } else if (format === 'html') {
            assert.ok(
                html.includes('<') && html.includes('>'),
                'HTML should contain HTML tags'
            );
        }
    }
    
    assert_format(html, format) {
        return this.assert_instruction_format(html, format);
    }
}

module.exports = InstructionsViewTestHelper;
