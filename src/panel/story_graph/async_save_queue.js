const StoryMapChange = require('./story_map_change');
const DOMState = require('./dom_state');
const StatusIndicator = require('./status_indicator');

const DEBOUNCE_DELAY_MS = 500;
const AUTO_HIDE_DELAY_MS = 2000;

class StoryGraphAsyncSaveQueue {
    constructor(backendPanel) {
        this._backendPanel = backendPanel;
        this._storyMapChangeQueue = [];
        this._debounceTimer = null;
        this._domState = new DOMState();
        this._statusIndicator = new StatusIndicator();
        this._executedCommands = [];
    }

    enqueue(storyMapChange) {
        this._storyMapChangeQueue.push(storyMapChange);
        this._applyOptimisticUpdate(storyMapChange);
        const message = this._storyMapChangeQueue.length > 1 
            ? `Saving ${this._storyMapChangeQueue.length} changes...`
            : `Saving ${this._storyMapChangeQueue.length} change...`;
        this._statusIndicator.update('spinner icon', message);
        this._resetDebounce();
    }

    _applyOptimisticUpdate(storyMapChange) {
        const update = {
            type: storyMapChange.type,
            node_type: storyMapChange.node_type,
            node_name: storyMapChange.node_name || storyMapChange.original_name || storyMapChange.new_node_name,
            target_position: storyMapChange.target_position,
            original_position: storyMapChange.original_position,
            original_name: storyMapChange.original_name,
            new_name: storyMapChange.new_name,
            new_node_name: storyMapChange.new_node_name,
            parent_node_type: storyMapChange.parent_node_type,
            parent_node_name: storyMapChange.parent_node_name
        };
        this._domState.addOptimisticUpdate(update);
        this._captureRollbackState(storyMapChange);
    }

    _captureRollbackState(storyMapChange) {
        const rollback = {
            operationType: storyMapChange.type,
            restoredValue: storyMapChange.original_name || storyMapChange.node_name,
            originalPosition: storyMapChange.original_position,
            originalParent: storyMapChange.parent_node_type
        };
        this._domState.addRollback(rollback);
    }

    _resetDebounce() {
        if (this._debounceTimer) {
            clearTimeout(this._debounceTimer);
        }
        this._debounceTimer = setTimeout(() => {
            this._processQueue();
        }, DEBOUNCE_DELAY_MS);
    }

    async _processQueue() {
        if (this._storyMapChangeQueue.length === 0) {
            return;
        }

        const storyMapChanges = [...this._storyMapChangeQueue];
        this._storyMapChangeQueue = [];

        for (const storyMapChange of storyMapChanges) {
            await this._executeStoryMapChange(storyMapChange);
        }
    }

    async _executeStoryMapChange(storyMapChange) {
        const command = {
            type: storyMapChange.type,
            node_type: storyMapChange.node_type,
            node_name: storyMapChange.node_name,
            original_position: storyMapChange.original_position,
            target_position: storyMapChange.target_position,
            original_name: storyMapChange.original_name,
            new_name: storyMapChange.new_name,
            new_node_name: storyMapChange.new_node_name,
            parent_node_type: storyMapChange.parent_node_type,
            parent_node_name: storyMapChange.parent_node_name,
            persisted: false
        };

        try {
            await this._sendCommandToBackend(command);
            command.persisted = true;
            this._executedCommands.push(command);
        } catch (error) {
            this._handleStoryMapChangeError(storyMapChange, error);
        }
    }

    async _sendCommandToBackend(command) {
        const commandString = this._buildCommandString(command);
        await this._backendPanel.execute(commandString);
    }

    _buildCommandString(command) {
        if (command.type === 'move') {
            return `move "${command.node_name}" to position ${command.target_position}`;
        } else if (command.type === 'rename') {
            return `rename "${command.original_name}" to "${command.new_name}"`;
        } else if (command.type === 'delete') {
            return `delete "${command.node_name}"`;
        } else if (command.type === 'create') {
            return `create ${command.node_type.toLowerCase()} "${command.new_node_name}" under ${command.parent_node_type} "${command.parent_node_name}"`;
        }
        return '';
    }

    _handleStoryMapChangeError(storyMapChange, error) {
        const rollback = this._domState.rollbacks.find(r => 
            r.restoredValue === (storyMapChange.original_name || storyMapChange.node_name)
        );
        if (rollback) {
            this._executeRollback(rollback);
        }
        this._statusIndicator.update('red X icon', 'Save failed', true);
    }

    _executeRollback(rollback) {
        this._domState.removeOptimisticUpdate(u => 
            u.node_name === rollback.restoredValue || u.original_name === rollback.restoredValue
        );
    }

    completeSaveSuccessfully() {
        if (!this._statusIndicator.isError) {
            this._statusIndicator.update('green checkmark', 'Saved', false);
            this._scheduleAutoHide();
        }
    }

    returnError(errorType, errorMessage) {
        const storyMapChange = this._executedCommands[this._executedCommands.length - 1] || this._storyMapChangeQueue[0] || {};
        const error = {
            type: errorType,
            message: errorMessage,
            stack: `Error: ${errorMessage}\n    at StoryGraphAsyncSaveQueue.returnError`
        };
        this._handleStoryMapChangeError(storyMapChange, error);
    }

    _scheduleAutoHide() {
        this._statusIndicator.scheduleAutoHide(AUTO_HIDE_DELAY_MS);
        setTimeout(() => {
            this._statusIndicator.clear();
        }, AUTO_HIDE_DELAY_MS);
    }

    getDOMState() {
        return this._domState;
    }

    getStatusIndicator() {
        return this._statusIndicator;
    }

    getQueueLength() {
        return this._storyMapChangeQueue.length;
    }

    getExecutedCommands() {
        return [...this._executedCommands];
    }

    async waitForDebounce(milliseconds) {
        if (this._debounceTimer) {
            await new Promise(resolve => {
                clearTimeout(this._debounceTimer);
                this._debounceTimer = setTimeout(resolve, milliseconds);
            });
            await this._processQueue();
        } else {
            await new Promise(resolve => setTimeout(resolve, milliseconds));
        }
    }
}

module.exports = StoryGraphAsyncSaveQueue;
