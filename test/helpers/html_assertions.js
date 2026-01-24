/**
 * HTML Assertion Helpers
 * Provides utilities for parsing HTML and making assertions about DOM structure
 */

const assert = require('node:assert');
const { JSDOM } = require('jsdom');

/**
 * Parse HTML string into a DOM document
 * @param {string} htmlString - HTML string to parse
 * @returns {Document} - DOM document
 */
function parseHTML(htmlString) {
    const dom = new JSDOM(htmlString);
    return dom.window.document;
}

/**
 * HTML assertion utilities
 */
class HTMLAssertions {
    /**
     * Assert element is present in HTML
     * @param {string} html - HTML string
     * @param {string} selector - CSS selector
     * @returns {Element} - Found element
     */
    static assertElementPresent(html, selector) {
        const doc = parseHTML(html);
        const element = doc.querySelector(selector);
        assert.ok(element, `Element not found: ${selector}`);
        return element;
    }
    
    /**
     * Assert element has specific class
     * @param {string} html - HTML string
     * @param {string} selector - CSS selector
     * @param {string} className - Expected class name
     */
    static assertElementHasClass(html, selector, className) {
        const element = this.assertElementPresent(html, selector);
        assert.ok(element.classList.contains(className), 
            `Element ${selector} should have class "${className}"`);
    }
    
    /**
     * Assert element contains specific text
     * @param {string} html - HTML string
     * @param {string} selector - CSS selector
     * @param {string} expectedText - Expected text content
     */
    static assertElementHasText(html, selector, expectedText) {
        const element = this.assertElementPresent(html, selector);
        assert.ok(element.textContent.includes(expectedText), 
            `Element ${selector} should contain text "${expectedText}"`);
    }
    
    /**
     * Assert element has specific attribute
     * @param {string} html - HTML string
     * @param {string} selector - CSS selector
     * @param {string} attributeName - Attribute name
     * @param {string} [expectedValue] - Optional expected value
     */
    static assertElementHasAttribute(html, selector, attributeName, expectedValue) {
        const element = this.assertElementPresent(html, selector);
        if (expectedValue !== undefined) {
            assert.strictEqual(element.getAttribute(attributeName), expectedValue,
                `Element ${selector} attribute "${attributeName}" should be "${expectedValue}"`);
        } else {
            assert.ok(element.hasAttribute(attributeName),
                `Element ${selector} should have attribute "${attributeName}"`);
        }
    }
    
    /**
     * Assert specific count of elements matching selector
     * @param {string} html - HTML string
     * @param {string} selector - CSS selector
     * @param {number} expectedCount - Expected number of elements
     */
    static assertElementCount(html, selector, expectedCount) {
        const doc = parseHTML(html);
        const elements = doc.querySelectorAll(selector);
        assert.strictEqual(elements.length, expectedCount,
            `Expected ${expectedCount} elements matching "${selector}", found ${elements.length}`);
    }
    
    /**
     * Assert HTML contains text (simple string match)
     * @param {string} html - HTML string
     * @param {string} expectedText - Expected text
     */
    static assertContainsText(html, expectedText) {
        assert.ok(html.includes(expectedText),
            `HTML should contain text "${expectedText}"`);
    }
    
    /**
     * Assert HTML does not contain text
     * @param {string} html - HTML string
     * @param {string} unexpectedText - Text that should not be present
     */
    static assertDoesNotContainText(html, unexpectedText) {
        assert.ok(!html.includes(unexpectedText),
            `HTML should not contain text "${unexpectedText}"`);
    }
}

module.exports = { parseHTML, HTMLAssertions };
