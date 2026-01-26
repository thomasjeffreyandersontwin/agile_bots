class StoryGraphUpdater {
    constructor() {
        this._storyGraph = null;
    }

    loadStoryGraph(testStoryMap, executedCommands) {
        const epicMap = this._buildEpicMap(testStoryMap);
        this._storyGraph = {
            epics: Array.from(epicMap.values())
        };
        this._applyExecutedCommands(executedCommands);
    }

    _buildEpicMap(testStoryMap) {
        const epicMap = new Map();
        const epic = this._getOrCreateEpic(epicMap);
        
        for (const parent of Object.values(testStoryMap)) {
            if (parent.parent_node_type === 'SubEpic') {
                this._addSubEpicToEpic(epic, parent);
            } else if (parent.parent_node_type === 'Epic') {
                this._addSubEpicsToEpic(epic, parent);
            }
        }
        
        for (const parent of Object.values(testStoryMap)) {
            if (parent.parent_node_type === 'Story') {
                this._addScenariosToStory(epic, parent);
            } else if (parent.parent_node_type === 'Scenario') {
                this._addChildrenToScenario(epic, parent);
            }
        }
        
        return epicMap;
    }

    _getOrCreateEpic(epicMap) {
        let epic = epicMap.get('Invoke Bot');
        if (!epic) {
            epic = {
                name: 'Invoke Bot',
                type: 'Epic',
                children: []
            };
            epicMap.set('Invoke Bot', epic);
        }
        return epic;
    }

    _addSubEpicToEpic(epic, parent) {
        let subEpic = epic.children.find(child => child.name === parent.parent_node_name);
        if (!subEpic) {
            subEpic = {
                name: parent.parent_node_name,
                type: 'SubEpic',
                children: []
            };
            epic.children.push(subEpic);
        }
        this._addStoriesToSubEpic(subEpic, parent);
    }

    _addStoriesToSubEpic(subEpic, parent) {
        for (const node of parent.nodes) {
            if (node.node_type === 'Story') {
                subEpic.children.push({
                    name: node.node_name,
                    type: 'Story',
                    sequential_order: node.position,
                    children: []
                });
            }
        }
    }

    _addScenariosToStory(epic, parent) {
        const story = this._findNodeRecursive(epic, 'Story', parent.parent_node_name);
        if (story) {
            if (!story.children) {
                story.children = [];
            }
            for (const node of parent.nodes) {
                if (node.node_type === 'Scenario') {
                    story.children.push({
                        name: node.node_name,
                        type: 'Scenario',
                        sequential_order: node.position
                    });
                }
            }
        }
    }

    _addChildrenToScenario(epic, parent) {
        const scenario = this._findNodeRecursive(epic, 'Scenario', parent.parent_node_name);
        if (scenario) {
            if (!scenario.children) {
                scenario.children = [];
            }
            for (const node of parent.nodes) {
                scenario.children.push({
                    name: node.node_name,
                    type: node.node_type,
                    sequential_order: node.position
                });
            }
        }
    }

    _addSubEpicsToEpic(epic, parent) {
        for (const node of parent.nodes) {
            if (node.node_type === 'SubEpic') {
                epic.children.push({
                    name: node.node_name,
                    type: 'SubEpic',
                    sequential_order: node.position,
                    children: []
                });
            }
        }
    }

    _applyExecutedCommands(executedCommands) {
        for (const command of executedCommands) {
            if (command.persisted) {
                this._applyCommandToStoryGraph(command);
            }
        }
    }

    _applyCommandToStoryGraph(command) {
        if (!this._storyGraph) {
            return;
        }
        
        if (command.type === 'move') {
            this._applyMoveCommand(command);
        } else if (command.type === 'rename') {
            this._applyRenameCommand(command);
        } else if (command.type === 'delete') {
            this._applyDeleteCommand(command);
        } else if (command.type === 'create') {
            this._applyCreateCommand(command);
        }
    }

    _applyMoveCommand(command) {
        const node = this.findNodeInGraph(command.node_type, command.node_name);
        if (node) {
            node.sequential_order = command.target_position;
        }
    }

    _applyRenameCommand(command) {
        const node = this.findNodeInGraph(command.node_type, command.original_name);
        if (node) {
            node.name = command.new_name;
        }
    }

    _applyDeleteCommand(command) {
        this._removeNodeFromGraph(command.node_type, command.node_name);
    }

    _applyCreateCommand(command) {
        const parent = this.findNodeInGraph(command.parent_node_type, command.parent_node_name);
        if (parent) {
            if (!parent.children) {
                parent.children = [];
            }
            parent.children.push({
                name: command.new_node_name,
                type: command.node_type,
                sequential_order: parent.children.length
            });
        }
    }
    
    _removeNodeFromGraph(nodeType, nodeName) {
        if (!this._storyGraph || !this._storyGraph.epics) {
            return;
        }
        for (const epic of this._storyGraph.epics) {
            if (this._removeNodeRecursive(epic, nodeType, nodeName)) {
                return;
            }
        }
    }

    _removeNodeRecursive(node, nodeType, nodeName) {
        if (node.children) {
            const index = node.children.findIndex(child => 
                child.type === nodeType && child.name === nodeName
            );
            if (index > -1) {
                node.children.splice(index, 1);
                return true;
            }
            for (const child of node.children) {
                if (this._removeNodeRecursive(child, nodeType, nodeName)) {
                    return true;
                }
            }
        }
        return false;
    }

    getStoryGraph() {
        return this._storyGraph;
    }

    findNodeInGraph(nodeType, nodeName) {
        if (!this._storyGraph || !this._storyGraph.epics) {
            return null;
        }
        for (const epic of this._storyGraph.epics) {
            const found = this._findNodeRecursive(epic, nodeType, nodeName);
            if (found) {
                return found;
            }
        }
        return null;
    }

    _findNodeRecursive(node, nodeType, nodeName) {
        if (node.type === nodeType && node.name === nodeName) {
            return node;
        }
        if (node.children) {
            for (const child of node.children) {
                const found = this._findNodeRecursive(child, nodeType, nodeName);
                if (found) {
                    return found;
                }
            }
        }
        return null;
    }
}

module.exports = StoryGraphUpdater;
