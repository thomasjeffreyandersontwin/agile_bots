class StatusIndicator {
    constructor() {
        this._icon = null;
        this._message = null;
        this._isError = false;
        this._isClickable = false;
        this._autoHideScheduled = false;
        this._autoHideTimeout = null;
    }

    get icon() {
        return this._icon;
    }

    get message() {
        return this._message;
    }

    get isError() {
        return this._isError;
    }

    get isClickable() {
        return this._isClickable;
    }

    get autoHideScheduled() {
        return this._autoHideScheduled;
    }

    get autoHideTimeout() {
        return this._autoHideTimeout;
    }

    update(icon, message, isError = false) {
        this._icon = icon;
        this._message = message;
        this._isError = isError;
        this._isClickable = isError;
        if (isError) {
            this._autoHideScheduled = false;
            this._autoHideTimeout = null;
        }
    }

    scheduleAutoHide(milliseconds) {
        this._autoHideScheduled = true;
        this._autoHideTimeout = milliseconds;
    }

    clear() {
        this._icon = null;
        this._message = null;
        this._autoHideScheduled = false;
        this._autoHideTimeout = null;
    }
}

module.exports = StatusIndicator;
