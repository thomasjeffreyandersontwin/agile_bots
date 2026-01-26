class DOMState {
    constructor(optimisticUpdates = [], rollbacks = []) {
        this._optimisticUpdates = [...optimisticUpdates];
        this._rollbacks = [...rollbacks];
    }

    get optimisticUpdates() {
        return [...this._optimisticUpdates];
    }

    get rollbacks() {
        return [...this._rollbacks];
    }

    addOptimisticUpdate(update) {
        this._optimisticUpdates.push({ ...update });
    }

    addRollback(rollback) {
        this._rollbacks.push({ ...rollback });
    }

    removeOptimisticUpdate(predicate) {
        const index = this._optimisticUpdates.findIndex(predicate);
        if (index > -1) {
            this._optimisticUpdates.splice(index, 1);
        }
    }
}

module.exports = DOMState;
