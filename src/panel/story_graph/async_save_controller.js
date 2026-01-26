const StoryGraphAsyncSaveQueue = require('./async_save_queue');
const StoryGraphUpdater = require('./story_graph_updater');
const StoryMapChange = require('./story_map_change');

class StoryGraphAsyncSaveController {
    constructor(backendPanel, storyMapProvider = null) {
        this._saveQueue = new StoryGraphAsyncSaveQueue(backendPanel);
        this._graphUpdater = new StoryGraphUpdater();
        this._storyMapProvider = storyMapProvider;
        this._storyGraphLoaded = false;
        this._errorDialog = null;
    }

    enqueue(operation) {
        const storyMapChange = this._convertToStoryMapChange(operation);
        this._saveQueue.enqueue(storyMapChange);
    }

    _convertToStoryMapChange(operation) {
        return new StoryMapChange(
            operation.type,
            operation.node_type,
            {
                node_name: operation.node_name,
                original_name: operation.original_name,
                new_name: operation.new_name,
                new_node_name: operation.new_node_name,
                original_position: operation.original_position,
                target_position: operation.target_position,
                node_position: operation.node_position,
                parent_node_type: operation.parent_node_type,
                parent_node_name: operation.parent_node_name
            }
        );
    }

    completeSaveSuccessfully() {
        this._saveQueue.completeSaveSuccessfully();
    }

    returnError(errorType, errorMessage) {
        const executedCommands = this._saveQueue.getExecutedCommands();
        const operation = executedCommands[executedCommands.length - 1] || {};
        const parentNodeName = this._getParentNodeNameForOperation(operation);
        this._errorDialog = this._buildErrorDialog(errorType, errorMessage, operation, parentNodeName);
        this._saveQueue.returnError(errorType, errorMessage);
    }

    _getParentNodeNameForOperation(operation) {
        if (operation.parent_node_name) {
            return operation.parent_node_name;
        }
        if (this._storyMapProvider) {
            const storyMap = this._storyMapProvider.getTestStoryMap();
            for (const parent of Object.values(storyMap)) {
                for (const node of parent.nodes || []) {
                    if (node.node_name === operation.original_name || node.node_name === operation.node_name) {
                        return parent.parent_node_name;
                    }
                }
            }
        }
        return 'Edit Story Map';
    }

    _buildErrorDialog(errorType, errorMessage, operation, parentNodeName) {
        const invalidName = operation.new_name || operation.invalid_name || '';
        const message = errorType === 'validation' 
            ? `ValidationError: Story name is required and cannot be empty string`
            : `HierarchyError: Story '${invalidName}' already exists in SubEpic '${parentNodeName}'`;
        return {
            message: message,
            stack: `Error: ${errorMessage}\n    at StoryGraphAsyncSaveController.returnError\n    at backend.saveOperation`
        };
    }

    getDOMState() {
        return this._saveQueue.getDOMState();
    }

    getStatusIndicator() {
        return this._saveQueue.getStatusIndicator();
    }

    getQueueLength() {
        return this._saveQueue.getQueueLength();
    }

    getExecutedCommands() {
        return this._saveQueue.getExecutedCommands();
    }

    async waitForDebounce(milliseconds) {
        await this._saveQueue.waitForDebounce(milliseconds);
    }

    displayStoryMap() {
        this._storyGraphLoaded = true;
    }

    reloadPanel() {
        this._storyGraphLoaded = true;
        this._loadStoryGraph();
    }

    _loadStoryGraph() {
        if (!this._storyMapProvider) {
            return;
        }
        const storyMap = this._storyMapProvider.getTestStoryMap();
        const executedCommands = this._saveQueue.getExecutedCommands();
        this._graphUpdater.loadStoryGraph(storyMap, executedCommands);
    }

    isStoryGraphLoaded() {
        return this._storyGraphLoaded;
    }

    getStoryGraph() {
        if (!this._graphUpdater.getStoryGraph()) {
            this._loadStoryGraph();
        }
        return this._graphUpdater.getStoryGraph();
    }

    findNodeInGraph(nodeType, nodeName) {
        if (!this._graphUpdater.getStoryGraph()) {
            this._loadStoryGraph();
        }
        return this._graphUpdater.findNodeInGraph(nodeType, nodeName);
    }

    clickErrorIndicator() {
        const statusIndicator = this._saveQueue.getStatusIndicator();
        if (statusIndicator.isError && !this._errorDialog) {
            this._errorDialog = {
                message: statusIndicator.message,
                stack: `Error stack trace for: ${statusIndicator.message}`
            };
        }
    }

    isErrorDialogDisplayed() {
        return this._errorDialog !== null;
    }

    getErrorDialog() {
        return this._errorDialog;
    }
}

module.exports = StoryGraphAsyncSaveController;
