/**
 * BehaviorsView - Renders behavior hierarchy with actions.
 * 
 * Epic: Invoke Bot Through Panel
 * Sub-Epic: Navigate And Execute Behaviors Through Panel
 * Story: Display Hierarchy, Navigate Behavior Action, Execute Behavior Action
 */

const PanelView = require('./panel_view');

class BehaviorsView extends PanelView {
    /**
     * Behaviors view.
     * 
     * @param {string|PanelView} botPathOrCli - Bot path or CLI instance
     * @param {Object} webview - VS Code webview instance (optional)
     * @param {Object} extensionUri - Extension URI (optional)
     * @param {Object} parentView - Parent BotView (optional, for accessing cached botData)
     */
    constructor(botPathOrCli, webview, extensionUri, parentView = null) {
        super(botPathOrCli);
        this.expansionState = {};
        this.webview = webview || null;
        this.extensionUri = extensionUri || null;
        this.parentView = parentView;
    }
    
    /**
     * Get behaviors data from CLI
     */
    async getBehaviors() {
        const botData = await this.execute('status');
        // NO FALLBACKS - let it fail if data is missing
        if (!botData) throw new Error('[BehaviorsView] botData is null/undefined');
        if (!botData.behaviors) throw new Error('[BehaviorsView] No behaviors in response');
        if (!botData.behaviors.all_behaviors) throw new Error('[BehaviorsView] No all_behaviors in response');
        return botData.behaviors.all_behaviors;
    }
    
    /**
     * Escape HTML entities.
     * 
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    /**
     * Escape text for use in JavaScript strings.
     * 
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeForJs(text) {
        if (typeof text !== 'string') {
            text = String(text);
        }
        return text.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');
    }
    
    /**
     * Get status marker for behavior/action/operation.
     * 
     * @param {boolean} isCurrent - Is current item
     * @param {boolean} isCompleted - Is completed item
     * @param {string} tickIconPath - Tick icon path (optional)
     * @param {string} notTickedIconPath - Not ticked icon path (optional)
     * @returns {string} Marker HTML
     */
    getStatusMarker(isCurrent, isCompleted, tickIconPath, notTickedIconPath) {
        if (isCurrent) {
            return tickIconPath 
                ? `<img src="${tickIconPath}" alt="Current" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />`
                : '';
        } else if (isCompleted) {
            return tickIconPath 
                ? `<img src="${tickIconPath}" alt="Completed" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />`
                : '';
        } else {
            return notTickedIconPath 
                ? `<img src="${notTickedIconPath}" alt="Pending" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />`
                : '';
        }
    }
    
    /**
     * Render behaviors hierarchy HTML - gets own data from CLI.
     * 
     * @returns {Promise<string>} HTML string
     */
    async render() {
        // Use cached botData from parent if available, otherwise fetch it
        const botData = this.parentView?.botData || await this.execute('status');
        // NO FALLBACKS - let it fail if data is missing
        if (!botData) throw new Error('[BehaviorsView] botData is null/undefined');
        if (!botData.behaviors) throw new Error('[BehaviorsView] No behaviors in response');
        if (!botData.behaviors.all_behaviors) throw new Error('[BehaviorsView] No all_behaviors in response');
        
        // Log current state from status command
        console.log(`[BehaviorsView] Status returned - current_behavior: ${botData.current_behavior}, current_action: ${botData.current_action}`);
        
        const behaviorsData = botData.behaviors.all_behaviors;
        const vscode = require('vscode');
        
        // Get the proper webview URIs for icons
        let feedbackIconPath = '';
        let gearIconPath = '';
        let plusIconPath = '';
        let subtractIconPath = '';
        let tickIconPath = '';
        let notTickedIconPath = '';
        let leftIconPath = '';
        let pointerIconPath = '';
        let rightIconPath = '';
        let clipboardIconPath = '';
        if (this.webview && this.extensionUri) {
            try {
                const feedbackUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'feedback.png');
                feedbackIconPath = this.webview.asWebviewUri(feedbackUri).toString();
                
                const gearUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'gear.png');
                gearIconPath = this.webview.asWebviewUri(gearUri).toString();
                
                const plusUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'plus.png');
                plusIconPath = this.webview.asWebviewUri(plusUri).toString();
                
                const subtractUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'subtract.png');
                subtractIconPath = this.webview.asWebviewUri(subtractUri).toString();
                
                const tickUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'tick.png');
                tickIconPath = this.webview.asWebviewUri(tickUri).toString();
                
                const notTickedUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'not_ticked.png');
                notTickedIconPath = this.webview.asWebviewUri(notTickedUri).toString();
                
                const leftUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'left.png');
                leftIconPath = this.webview.asWebviewUri(leftUri).toString();
                
                const pointerUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'pointer.png');
                pointerIconPath = this.webview.asWebviewUri(pointerUri).toString();
                
                const rightUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'right.png');
                rightIconPath = this.webview.asWebviewUri(rightUri).toString();
                
                const clipboardUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'rules.png');
                clipboardIconPath = this.webview.asWebviewUri(clipboardUri).toString();
            } catch (err) {
                console.error('Failed to create icon URIs:', err);
            }
        }
        
        if (!behaviorsData || behaviorsData.length === 0) {
            return this.renderEmpty(feedbackIconPath, gearIconPath, leftIconPath, pointerIconPath, rightIconPath);
        }
        
        const behaviorsHtml = behaviorsData.map((behavior, bIdx) => {
            return this.renderBehavior(behavior, bIdx, plusIconPath, subtractIconPath, tickIconPath, notTickedIconPath, clipboardIconPath);
        }).join('');
        
        return `
    <div class="section card-primary">
        <div class="collapsible-section expanded">
            <div class="collapsible-header" onclick="toggleSection('behaviors-content')" style="
                cursor: pointer;
                padding: 4px 5px;
                background-color: transparent;
                border-left: none;
                border-radius: 2px;
                display: flex;
                align-items: center;
                user-select: none;
            ">
                <span class="expand-icon" style="margin-right: 8px; font-size: 28px; transition: transform 0.15s;">▸</span>
                ${feedbackIconPath ? `<img src="${feedbackIconPath}" style="margin-right: 8px; width: 36px; height: 36px; object-fit: contain;" alt="Behavior Icon" />` : (gearIconPath ? `<img src="${gearIconPath}" style="margin-right: 8px; width: 36px; height: 36px; object-fit: contain;" alt="Behavior Icon" />` : '')}
                <span style="font-weight: 600; font-size: 20px;">Behavior Action Status</span>
            </div>
            <div id="behaviors-content" class="collapsible-content" style="max-height: 2000px; overflow: hidden; transition: max-height 0.3s ease;">
                <div class="card-secondary" style="padding: 5px;">
                    ${behaviorsHtml}
                    <div style="margin-top: 8px; padding-top: 5px; border-top: none; display: flex; gap: 4px; flex-wrap: wrap;">
                        <button onclick="executeNavigationCommand('back')" title="Back - Go to previous action" style="
                            background-color: var(--vscode-button-secondaryBackground);
                            color: var(--vscode-button-secondaryForeground);
                            border: none;
                            padding: 4px 6px;
                            cursor: pointer;
                            border-radius: 2px;
                            font-size: 16px;
                            font-family: inherit;
                            line-height: 1;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">${leftIconPath ? `<img src="${leftIconPath}" style="width: 20px; height: 20px; object-fit: contain;" alt="Back" />` : ''}</button>
                        <button onclick="executeNavigationCommand('current')" title="Current - Show current action details" style="
                            background-color: var(--vscode-button-secondaryBackground);
                            color: var(--vscode-button-secondaryForeground);
                            border: none;
                            padding: 4px 6px;
                            cursor: pointer;
                            border-radius: 2px;
                            font-size: 16px;
                            font-family: inherit;
                            line-height: 1;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">${pointerIconPath ? `<img src="${pointerIconPath}" style="width: 20px; height: 20px; object-fit: contain;" alt="Current" />` : ''}</button>
                        <button onclick="executeNavigationCommand('next')" title="Next - Advance to next action" style="
                            background-color: var(--vscode-button-secondaryBackground);
                            color: var(--vscode-button-secondaryForeground);
                            border: none;
                            padding: 4px 6px;
                            cursor: pointer;
                            border-radius: 2px;
                            font-size: 16px;
                            font-family: inherit;
                            line-height: 1;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">${rightIconPath ? `<img src="${rightIconPath}" style="width: 20px; height: 20px; object-fit: contain;" alt="Next" />` : ''}</button>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    }
    
    /**
     * Render empty state.
     * 
     * @param {string} feedbackIconPath - Feedback icon path
     * @param {string} gearIconPath - Gear icon path
     * @param {string} leftIconPath - Left icon path
     * @param {string} pointerIconPath - Pointer icon path
     * @param {string} rightIconPath - Right icon path
     * @returns {string} HTML string
     */
    renderEmpty(feedbackIconPath, gearIconPath, leftIconPath, pointerIconPath, rightIconPath) {
        return `
    <div class="section card-primary">
        <div class="collapsible-section expanded">
            <div class="collapsible-header" onclick="toggleSection('behaviors-content')" style="
                cursor: pointer;
                padding: 4px 5px;
                background-color: transparent;
                border-left: none;
                border-radius: 2px;
                display: flex;
                align-items: center;
                user-select: none;
            ">
                <span class="expand-icon" style="margin-right: 8px; font-size: 28px; transition: transform 0.15s;">▸</span>
                ${feedbackIconPath ? `<img src="${feedbackIconPath}" style="margin-right: 8px; width: 36px; height: 36px; object-fit: contain;" alt="Behavior Icon" />` : (gearIconPath ? `<img src="${gearIconPath}" style="margin-right: 8px; width: 36px; height: 36px; object-fit: contain;" alt="Behavior Icon" />` : '')}
                <span style="font-weight: 600; font-size: 20px;">Behavior Action Status</span>
            </div>
            <div id="behaviors-content" class="collapsible-content" style="max-height: 2000px; overflow: hidden; transition: max-height 0.3s ease;">
                <div class="card-secondary" style="padding: 5px;">
                    <div class="empty-state">No behaviors available</div>
                    <div style="margin-top: 8px; padding-top: 5px; border-top: none; display: flex; gap: 4px; flex-wrap: wrap;">
                        <button onclick="executeNavigationCommand('back')" title="Back - Go to previous action" style="
                            background-color: var(--vscode-button-secondaryBackground);
                            color: var(--vscode-button-secondaryForeground);
                            border: none;
                            padding: 4px 6px;
                            cursor: pointer;
                            border-radius: 2px;
                            font-size: 16px;
                            font-family: inherit;
                            line-height: 1;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">${leftIconPath ? `<img src="${leftIconPath}" style="width: 20px; height: 20px; object-fit: contain;" alt="Back" />` : ''}</button>
                        <button onclick="executeNavigationCommand('current')" title="Current - Show current action details" style="
                            background-color: var(--vscode-button-secondaryBackground);
                            color: var(--vscode-button-secondaryForeground);
                            border: none;
                            padding: 4px 6px;
                            cursor: pointer;
                            border-radius: 2px;
                            font-size: 16px;
                            font-family: inherit;
                            line-height: 1;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">${pointerIconPath ? `<img src="${pointerIconPath}" style="width: 20px; height: 20px; object-fit: contain;" alt="Current" />` : ''}</button>
                        <button onclick="executeNavigationCommand('next')" title="Next - Advance to next action" style="
                            background-color: var(--vscode-button-secondaryBackground);
                            color: var(--vscode-button-secondaryForeground);
                            border: none;
                            padding: 4px 6px;
                            cursor: pointer;
                            border-radius: 2px;
                            font-size: 16px;
                            font-family: inherit;
                            line-height: 1;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">${rightIconPath ? `<img src="${rightIconPath}" style="width: 20px; height: 20px; object-fit: contain;" alt="Next" />` : ''}</button>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    }
    
    /**
     * Render a single behavior.
     * 
     * @param {Object} behavior - Behavior object
     * @param {number} bIdx - Behavior index
     * @param {string} plusIconPath - Plus icon path
     * @param {string} subtractIconPath - Subtract icon path
     * @param {string} tickIconPath - Tick icon path
     * @param {string} notTickedIconPath - Not ticked icon path
     * @param {string} clipboardIconPath - Clipboard icon path
     * @returns {string} HTML string
     */
    renderBehavior(behavior, bIdx, plusIconPath, subtractIconPath, tickIconPath, notTickedIconPath, clipboardIconPath) {
        const isCurrent = behavior.isCurrent || behavior.is_current || false;
        const isCompleted = behavior.isCompleted || behavior.is_completed || false;
        const behaviorMarker = isCurrent 
            ? (tickIconPath ? `<img src="${tickIconPath}" alt="Current" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />` : '')
            : isCompleted
            ? (tickIconPath ? `<img src="${tickIconPath}" alt="Completed" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />` : '')
            : (notTickedIconPath ? `<img src="${notTickedIconPath}" alt="Pending" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />` : '');
        
        const behaviorTooltip = behavior.description ? this.escapeHtml(behavior.description) : '';
        const behaviorId = `behavior-${bIdx}`;
        const behaviorNameRaw = behavior.name || '';
        const behaviorName = this.escapeHtml(behaviorNameRaw);
        const behaviorNameJs = this.escapeForJs(behaviorNameRaw);
        
        // Expansion logic:
        // 1. If we have saved state for this item, use it (user's explicit choice)
        // 2. Otherwise, expand if current or completed (don't auto-collapse completed items)
        const hasExpansionState = this.expansionState && (behaviorId in this.expansionState);
        const behaviorExpanded = hasExpansionState ? this.expansionState[behaviorId] : (isCurrent || isCompleted);
        const behaviorIconSrc = behaviorExpanded ? subtractIconPath : plusIconPath;
        const behaviorIconAlt = behaviorExpanded ? 'Collapse' : 'Expand';
        const behaviorIconClass = behaviorExpanded ? 'expanded' : '';
        const behaviorDisplay = behaviorExpanded ? 'block' : 'none';
        
        const behaviorActiveClass = isCurrent ? ' active' : '';
        let html = `<div class="collapsible-header card-item${behaviorActiveClass}" data-behavior="${behaviorName}" title="${behaviorTooltip}"><span id="${behaviorId}-icon" class="${behaviorIconClass}" style="display: inline-block; min-width: 12px; cursor: pointer;" onclick="toggleCollapse('${behaviorId}')" data-plus="${plusIconPath}" data-subtract="${subtractIconPath}">${plusIconPath && subtractIconPath ? `<img src="${behaviorIconSrc}" alt="${behaviorIconAlt}" style="width: 12px; height: 12px; vertical-align: middle;" />` : ''}</span> <span style="cursor: pointer; text-decoration: underline;" onclick="navigateToBehavior('${behaviorNameJs}')">${behaviorMarker}${behaviorName}</span>${clipboardIconPath ? `<button onclick="event.stopPropagation(); getBehaviorRules('${behaviorNameJs}');" style="background: transparent; border: none; padding: 0 0 0 8px; margin: 0; cursor: pointer; vertical-align: middle; display: inline-flex; align-items: center; transition: opacity 0.15s ease;" onmouseover="this.style.opacity='0.7'" onmouseout="this.style.opacity='1'" title="Get rules for ${behaviorName} and send to chat"><img src="${clipboardIconPath}" style="width: 16px; height: 16px; object-fit: contain;" alt="Get Rules" /></button>` : ''}</div>`;
        
        // Always create collapsible content, even if empty
        const actionsArray = behavior.actions?.all_actions || behavior.actions || [];
        const hasActions = Array.isArray(actionsArray) && actionsArray.length > 0;
        const actionsHtml = hasActions ? actionsArray.map((action, aIdx) => {
            return this.renderAction(action, bIdx, aIdx, behaviorName, plusIconPath, subtractIconPath, tickIconPath, notTickedIconPath);
        }).join('') : '';
        
        html += `<div id="${behaviorId}" class="collapsible-content" style="display: ${behaviorDisplay};">${actionsHtml}</div>`;
        
        return html;
    }
    
    /**
     * Render a single action.
     * 
     * @param {Object} action - Action object
     * @param {number} bIdx - Behavior index
     * @param {number} aIdx - Action index
     * @param {string} behaviorName - Behavior name (escaped)
     * @param {string} plusIconPath - Plus icon path
     * @param {string} subtractIconPath - Subtract icon path
     * @param {string} tickIconPath - Tick icon path
     * @param {string} notTickedIconPath - Not ticked icon path
     * @returns {string} HTML string
     */
    renderAction(action, bIdx, aIdx, behaviorName, plusIconPath, subtractIconPath, tickIconPath, notTickedIconPath) {
        // Log inputs
        const fs = require('fs');
        const path = require('path');
        const logPath = 'c:\\dev\\agile_bots\\render-action-debug.log';
        const timestamp = new Date().toISOString();
        
        const logEntry = `\n${'='.repeat(80)}\n[${timestamp}] renderAction called\n` +
            `  bIdx: ${bIdx}, aIdx: ${aIdx}\n` +
            `  action raw: ${JSON.stringify(action)}\n` +
            `  behaviorName (passed in): "${behaviorName}"\n` +
            `  behaviorName type: ${typeof behaviorName}\n`;
        
        try {
            fs.appendFileSync(logPath, logEntry);
        } catch (err) {
            console.error('[BehaviorsView] Failed to write to log file:', err);
        }
        
        const isCurrent = action.isCurrent || action.is_current || false;
        const isCompleted = action.isCompleted || action.is_completed || false;
        const actionMarker = isCurrent
            ? (tickIconPath ? `<img src="${tickIconPath}" alt="Current" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />` : '')
            : isCompleted
            ? (tickIconPath ? `<img src="${tickIconPath}" alt="Completed" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />` : '')
            : (notTickedIconPath ? `<img src="${notTickedIconPath}" alt="Pending" style="width: 18px; height: 18px; vertical-align: middle; margin-right: 8px;" />` : '');
        
        const actionTooltip = action.description ? this.escapeHtml(action.description) : '';
        const actionName = this.escapeHtml(action.action_name || action.name || '');
        
        // Log escaped values
        const logEntry2 = `  actionName (escaped): "${actionName}"\n` +
            `  onclick will be: navigateToAction('${behaviorName}', '${actionName}')\n`;
        
        try {
            fs.appendFileSync(logPath, logEntry2);
        } catch (err) {
            console.error('[BehaviorsView] Failed to write to log file:', err);
        }
        
        const actionActiveClass = isCurrent ? ' active' : '';
        const actionHtml = `<div class="collapsible-header action-item card-item${actionActiveClass}" title="${actionTooltip}"><span style="cursor: pointer; text-decoration: underline;" onclick="navigateToAction('${behaviorName}', '${actionName}')">${actionMarker}${actionName}</span></div>`;
        
        // Log final HTML
        const logEntry3 = `  Generated HTML: ${actionHtml.substring(0, 200)}...\n`;
        try {
            fs.appendFileSync(logPath, logEntry3);
        } catch (err) {
            console.error('[BehaviorsView] Failed to write to log file:', err);
        }
        
        return actionHtml;
    }
    
    /**
     * Handle events.
     * 
     * @param {string} eventType - Event type
     * @param {Object} eventData - Event data
     * @returns {Promise<Object>} Result
     */
    async handleEvent(eventType, eventData) {
        if (eventType === 'execute') {
            // Execute behavior/action logic would go here
            return { success: true };
        }
        throw new Error(`Unknown event type: ${eventType}`);
    }
}

module.exports = BehaviorsView;
