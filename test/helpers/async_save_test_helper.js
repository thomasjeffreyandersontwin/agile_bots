const StoryGraphAsyncSaveController = require('../../src/panel/story_graph/async_save_controller');
const ParentNode = require('../../src/panel/story_graph/parent_node');

class TestStoryMapBuilder {
    constructor() {
        this._testStoryMap = {};
    }

    setupStoryMap(parentNode) {
        const key = `${parentNode.node_type}_${parentNode.node_name}`;
        if (!this._testStoryMap[key]) {
            this._testStoryMap[key] = {
                parent_node_type: parentNode.node_type,
                parent_node_name: parentNode.node_name,
                nodes: []
            };
        }
    }

    addNodeToParent(parentNode, nodeType, nodeName, position) {
        const key = `${parentNode.node_type}_${parentNode.node_name}`;
        if (!this._testStoryMap[key]) {
            this.setupStoryMap(parentNode);
        }
        this._testStoryMap[key].nodes.push({
            node_type: nodeType,
            node_name: nodeName,
            position: position
        });
    }

    getTestStoryMap() {
        return this._testStoryMap;
    }
}

class AsyncSaveTestHelper {
    constructor(backendPanel) {
        this._backendPanel = backendPanel;
        this._testMapBuilder = new TestStoryMapBuilder();
        this._parentNames = {};
    }

    createAsyncSaveController() {
        return new StoryGraphAsyncSaveController(this._backendPanel, this._testMapBuilder);
    }

    setupStoryMap(parentNodeType, parentNodeName) {
        const parentNode = new ParentNode(parentNodeType, parentNodeName);
        this._testMapBuilder.setupStoryMap(parentNode);
        this._parentNames[parentNodeType] = parentNodeName;
    }

    addNodeToParent(parentNodeType, nodeType, nodeName, position) {
        const parentNodeName = this._parentNames[parentNodeType];
        if (!parentNodeName) {
            throw new Error(`Parent ${parentNodeType} not set up. Call given_story_map_contains first.`);
        }
        const parentNode = new ParentNode(parentNodeType, parentNodeName);
        this._testMapBuilder.addNodeToParent(parentNode, nodeType, nodeName, position);
    }

    getTestStoryMap() {
        return this._testMapBuilder.getTestStoryMap();
    }
}

module.exports = AsyncSaveTestHelper;
