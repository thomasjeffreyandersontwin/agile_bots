/**
 * StoryMapView Test Helper
 * Provides factory methods for testing StoryMapView
 * This helper is ALLOWED to import production code (it wraps it)
 * Follows rule: object_oriented_test_helpers
 */

const path = require('path');

class StoryMapViewTestHelper {
    constructor(cli) {
        // This helper is ALLOWED to import production code - it wraps it for tests
        const StoryMapView = require('../../src/panel/story_map_view');
        this._cli = cli;
        this._view = new StoryMapView(cli);
    }
    
    /**
     * Render story map HTML
     * @returns {Promise<string>} - Rendered HTML
     */
    async render() {
        return await this._view.render();
    }
    
    /**
     * Get the view instance (for tests that need direct access)
     * @returns {StoryMapView}
     */
    getView() {
        return this._view;
    }
    
    /**
     * Create a new StoryMapView instance
     * @param {Object} cli - PanelView CLI instance
     * @returns {StoryMapView} - New StoryMapView instance
     */
    static create(cli) {
        const StoryMapView = require('../../src/panel/story_map_view');
        return new StoryMapView(cli);
    }
}

module.exports = StoryMapViewTestHelper;
