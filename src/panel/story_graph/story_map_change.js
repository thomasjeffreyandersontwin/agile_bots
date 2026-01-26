class StoryMapChange {
    constructor(type, nodeType, options = {}) {
        this.type = type;
        this.node_type = nodeType;
        this.node_name = options.node_name !== undefined ? options.node_name : null;
        this.original_name = options.original_name !== undefined ? options.original_name : null;
        this.new_name = options.new_name !== undefined ? options.new_name : null;
        this.new_node_name = options.new_node_name !== undefined ? options.new_node_name : null;
        this.original_position = options.original_position !== undefined ? options.original_position : null;
        this.target_position = options.target_position !== undefined ? options.target_position : null;
        this.node_position = options.node_position !== undefined ? options.node_position : null;
        this.parent_node_type = options.parent_node_type !== undefined ? options.parent_node_type : null;
        this.parent_node_name = options.parent_node_name !== undefined ? options.parent_node_name : null;
    }

    static createMove(nodeType, nodeName, originalPosition, targetPosition) {
        return new StoryMapChange('move', nodeType, {
            node_name: nodeName,
            original_position: originalPosition,
            target_position: targetPosition
        });
    }

    static createRename(nodeType, originalName, newName) {
        return new StoryMapChange('rename', nodeType, {
            original_name: originalName,
            new_name: newName
        });
    }

    static createDelete(nodeType, nodeName, nodePosition) {
        return new StoryMapChange('delete', nodeType, {
            node_name: nodeName,
            node_position: nodePosition
        });
    }

    static createCreate(parentNodeType, parentNodeName, nodeType, newNodeName) {
        return new StoryMapChange('create', nodeType, {
            parent_node_type: parentNodeType,
            parent_node_name: parentNodeName,
            new_node_name: newNodeName
        });
    }
}

module.exports = StoryMapChange;
