/**
 * InstructionsSection - Renders action instructions with action-specific subsections.
 * 
 * Epic: Invoke Bot Through Panel
 * Sub-Epic: Display Action Instructions Through Panel
 * Story: Display Base Instructions, Display Clarify Instructions, Display Strategy Instructions, etc.
 */

const PanelView = require('./panel_view');
const vscode = require('vscode');
const path = require('path');

class InstructionsSection extends PanelView {
    /**
     * Instructions section view.
     * 
     * @param {string|PanelView} botPathOrCli - Bot path or CLI instance
     * @param {Object} webview - VS Code webview instance (optional)
     * @param {Object} extensionUri - Extension URI (optional)
     * @param {Object} parentView - Parent BotView (optional, for accessing cached botData)
     */
    constructor(botPathOrCli, webview, extensionUri, parentView = null) {
        super(botPathOrCli);
        this.promptContent = '';
        this.webview = webview || null;
        this.extensionUri = extensionUri || null;
        this.parentView = parentView;
    }
    
    /**
     * Escape HTML entities.
     * 
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }
    
    /**
     * Escape string for JavaScript context (inside single quotes)
     */
    escapeForJs(text) {
        if (!text) return '';
        return String(text).replace(/\\/g, '\\\\').replace(/'/g, "\\'");
    }
    
    escapeForAttribute(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }
    
    /**
     * Render instructions section HTML.
     * Always renders the section structure, even if empty (for consistent UI).
     * 
     * @returns {string} HTML string
     */
    async render() {
        // Prefer the most recent CLI response (navigation returns unified {bot,instructions})
        const lastResponse = PanelView._lastResponse || {};
        let instructionsData = lastResponse.instructions || {};
        let currentActionFromResponse = lastResponse.bot?.current_action || lastResponse.current_action;

        // Fallback to status if no cached instructions
        if (!instructionsData || Object.keys(instructionsData).length === 0) {
            // Use cached botData from parent if available, otherwise fetch it
            const botData = this.parentView?.botData || await this.execute('status');
            
            // Check if there's a current behavior and action
            const currentBehavior = botData?.behaviors?.current_behavior || botData?.current_behavior;
            const currentAction = botData?.behaviors?.current_action || botData?.current_action;
            
            // If we have a current behavior/action, execute it to get instructions
            if (currentBehavior && currentAction) {
                try {
                    const actionResponse = await this.execute('current');
                    instructionsData = actionResponse?.instructions || {};
                    currentActionFromResponse = currentAction;
                } catch (error) {
                    console.error('[InstructionsSection] Failed to load current action instructions:', error);
                    instructionsData = botData?.instructions || botData?.bot?.instructions || {};
                }
            } else {
                // No current action - auto-navigate to first behavior's first action
                console.log('[InstructionsSection] No current action, auto-navigating to first action');
                const behaviors = botData?.behaviors?.behaviors || botData?.bot?.behaviors?.behaviors || [];
                if (behaviors.length > 0) {
                    const firstBehavior = behaviors[0];
                    const firstBehaviorName = firstBehavior.name || firstBehavior.behavior_name;
                    const firstAction = firstBehavior.actions?.[0]?.name || firstBehavior.actions?.[0];
                    
                    if (firstBehaviorName && firstAction) {
                        try {
                            console.log(`[InstructionsSection] Auto-navigating to ${firstBehaviorName}.${firstAction}`);
                            const actionResponse = await this.execute(`${firstBehaviorName}.${firstAction}`);
                            instructionsData = actionResponse?.instructions || {};
                            currentActionFromResponse = firstAction;
                        } catch (error) {
                            console.error('[InstructionsSection] Failed to auto-navigate to first action:', error);
                            instructionsData = botData?.instructions || botData?.bot?.instructions || {};
                        }
                    } else {
                        instructionsData = botData?.instructions || botData?.bot?.instructions || {};
                    }
                } else {
                    instructionsData = botData?.instructions || botData?.bot?.instructions || {};
                }
            }
            
            currentActionFromResponse = currentActionFromResponse ||
                botData?.current_action ||
                botData?.behaviors?.current_action ||
                botData?.bot?.current_action;
        }

        // Persist prompt content for submit button state
        if (instructionsData?.display_content) {
            this.promptContent = Array.isArray(instructionsData.display_content)
                ? instructionsData.display_content.join('\n')
                : instructionsData.display_content;
        }
        
        if (!instructionsData || Object.keys(instructionsData).length === 0) {
            return `
    <div class="section card-primary">
        <div class="collapsible-section expanded">
            <div class="collapsible-header" onclick="toggleSection('instructions-content')" style="
                cursor: pointer;
                padding: 4px 5px;
                background-color: transparent;
                border-left: none;
                border-radius: 2px;
                display: flex;
                align-items: center;
                user-select: none;
            ">
                <span class="expand-icon">▸</span>
                <span style="font-weight: 600; font-size: 20px;">Instructions</span>
            </div>
            <div id="instructions-content" class="collapsible-content" style="max-height: 600px; overflow-y: auto; overflow-x: hidden; transition: max-height 0.3s ease;">
                <div class="card-secondary" style="padding: 8px 10px; color: var(--vscode-descriptionForeground);">
                    <div style="margin-bottom: 4px;">No instructions available yet.</div>
                    <div>Navigate to a behavior/action to load instructions.</div>
                </div>
            </div>
        </div>
    </div>`;
        }

        // Merge behavior instructions into base_instructions at the top
        let instructions = { ...instructionsData };
        if (instructions.behavior && instructions.base_instructions) {
            // Combine behavior at the top of base_instructions
            if (Array.isArray(instructions.behavior) && Array.isArray(instructions.base_instructions)) {
                instructions = { ...instructions, base_instructions: [...instructions.behavior, ...instructions.base_instructions] };
            } else if (typeof instructions.behavior === 'string' && Array.isArray(instructions.base_instructions)) {
                instructions = { ...instructions, base_instructions: [instructions.behavior, ...instructions.base_instructions] };
            } else if (Array.isArray(instructions.behavior) && typeof instructions.base_instructions === 'string') {
                instructions = { ...instructions, base_instructions: [...instructions.behavior, instructions.base_instructions] };
            } else if (typeof instructions.behavior === 'string' && typeof instructions.base_instructions === 'string') {
                instructions = { ...instructions, base_instructions: instructions.behavior + '\n\n' + instructions.base_instructions };
            }
            // Remove the separate behavior key after merging
            delete instructions.behavior;
        } else if (instructions.behavior && !instructions.base_instructions) {
            // If there's only behavior, rename it to base_instructions
            instructions = { ...instructions, base_instructions: instructions.behavior };
            delete instructions.behavior;
        }

        // Load icon images
        let clipboardIconPath = '';
        let documentIconPath = '';
        let lightbulbIconPath = '';
        let lightbulbHeadIconPath = '';
        let bullseyeIconPath = '';
        let storyIconPath = '';
        let botSubmitIconPath = '';
        if (this.webview && this.extensionUri) {
            try {
                const clipboardUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'clipboard.png');
                clipboardIconPath = this.webview.asWebviewUri(clipboardUri).toString();
                
                const documentUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'document.png');
                documentIconPath = this.webview.asWebviewUri(documentUri).toString();
                
                const lightbulbUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'lightbulb.png');
                lightbulbIconPath = this.webview.asWebviewUri(lightbulbUri).toString();
                
                const lightbulbHeadUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'light_bulb_head.png');
                lightbulbHeadIconPath = this.webview.asWebviewUri(lightbulbHeadUri).toString();
                
                const bullseyeUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'bullseye.png');
                bullseyeIconPath = this.webview.asWebviewUri(bullseyeUri).toString();
                
                const storyUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'story.png');
                storyIconPath = this.webview.asWebviewUri(storyUri).toString();
                
                const submitUri = vscode.Uri.joinPath(this.extensionUri, 'img', 'submit.png');
                botSubmitIconPath = this.webview.asWebviewUri(submitUri).toString();
            } catch (err) {
                console.error('Failed to create icon URIs:', err);
            }
        }

        // RESTRUCTURE: Consolidate into EXACTLY 4 sections: Base, Clarify, Strategy, Build
        const restructured = {};

        // 1. BASE INSTRUCTIONS - combine behavior + action + base
        if (instructions.behavior_instructions || instructions.action_instructions || instructions.base_instructions) {
            let baseContent = '';
            
            // Format behavior instructions
            if (instructions.behavior_instructions) {
                baseContent += '**Behavior Instructions**\n\n';
                if (typeof instructions.behavior_instructions === 'string') {
                    baseContent += instructions.behavior_instructions;
                } else if (typeof instructions.behavior_instructions === 'object') {
                    if (instructions.behavior_instructions.name) {
                        baseContent += `**${instructions.behavior_instructions.name}**`;
                    }
                    if (instructions.behavior_instructions.description) {
                        baseContent += `\n\n${instructions.behavior_instructions.description}`;
                    }
                    if (instructions.behavior_instructions.instructions) {
                        baseContent += '\n\n';
                        if (Array.isArray(instructions.behavior_instructions.instructions)) {
                            baseContent += instructions.behavior_instructions.instructions.map(i => `- ${i}`).join('\n');
                        } else {
                            baseContent += instructions.behavior_instructions.instructions;
                        }
                    }
                }
                baseContent += '\n\n';
            }
            
            // Format action instructions
            if (instructions.action_instructions) {
                baseContent += '**Action Instructions**\n\n';
                if (typeof instructions.action_instructions === 'string') {
                    baseContent += instructions.action_instructions;
                } else if (typeof instructions.action_instructions === 'object') {
                    if (instructions.action_instructions.name) {
                        baseContent += `**${instructions.action_instructions.name}**`;
                    }
                    if (instructions.action_instructions.description) {
                        baseContent += `\n\n${instructions.action_instructions.description}`;
                    }
                    if (instructions.action_instructions.instructions) {
                        baseContent += '\n\n';
                        if (Array.isArray(instructions.action_instructions.instructions)) {
                            baseContent += instructions.action_instructions.instructions.map(i => `- ${i}`).join('\n');
                        } else {
                            baseContent += instructions.action_instructions.instructions;
                        }
                    }
                }
                baseContent += '\n\n';
            }
            
            // Add base instructions
            if (instructions.base_instructions) {
                if (Array.isArray(instructions.base_instructions)) {
                    baseContent += instructions.base_instructions.map(i => `- ${i}`).join('\n');
                } else if (typeof instructions.base_instructions === 'string') {
                    baseContent += instructions.base_instructions;
                }
            }
            
            restructured.base_instructions = baseContent.trim();
        }

        // 2. CLARIFY - Q&A + Evidence
        // ALWAYS show when there's saved clarification data (visible on all pages as context)
        // ALSO show when in clarify action even if no saved data yet (for editing)
        const currentAction = instructions.action_instructions?.name || currentActionFromResponse || '';
        const savedClarification = instructions.clarification;
        const isInClarifyAction = currentAction === 'clarify';
        
        // Check if we have saved answers or if we're in clarify action
        const hasSavedAnswers = savedClarification && 
                               savedClarification.key_questions && 
                               savedClarification.key_questions.answers &&
                               Object.keys(savedClarification.key_questions.answers).length > 0;
        
        const showClarifySection = hasSavedAnswers || isInClarifyAction;
        
        if (showClarifySection) {
            // Transform clarification.json structure to array format for rendering
            let clarificationDataArray = [];
            
            // Check if we have saved clarification data (from clarification.json)
            if (hasSavedAnswers) {
                // Convert answers object to array of {question, answer} objects
                const answers = savedClarification.key_questions.answers;
                clarificationDataArray = Object.keys(answers).map(question => ({
                    question: question,
                    answer: answers[question]
                }));
            }
            
            // If no saved data but we're in clarify action, create empty entries for guardrail questions
            if (clarificationDataArray.length === 0 && isInClarifyAction && instructions.guardrails?.required_context?.key_questions) {
                const questions = instructions.guardrails.required_context.key_questions;
                clarificationDataArray = questions.map(q => ({
                    question: q,
                    answer: ''
                }));
            }
            
            // Get evidence - pass full evidence object with both required and provided
            let evidenceData = {};
            if (savedClarification && savedClarification.evidence) {
                // Use saved evidence structure (has both required and provided)
                evidenceData = savedClarification.evidence;
            } else {
                // Create structure from guardrails only (no provided yet)
                evidenceData = {
                    required: instructions.guardrails?.required_context?.evidence || [],
                    provided: {}
                };
            }
            
            restructured.clarify_instructions = {
                clarification_data: clarificationDataArray,
                evidence: evidenceData,
                guardrails: instructions.guardrails || instructions.clarify_instructions?.guardrails
            };
        }

        // 3. STRATEGY - Decision Criteria + Assumptions
        // ALWAYS show when there's saved strategy data (visible on all pages as context)
        // ALSO show when in strategy action even if no saved data yet (for editing)
        const savedStrategy = instructions.strategy;
        const isInStrategyAction = currentAction === 'strategy';
        
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/8c521aea-7def-453b-baa0-70f06cfd0592',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'instructions_view.js:346',message:'strategy data received',data:{has_savedStrategy:!!savedStrategy,savedStrategy_keys:savedStrategy?Object.keys(savedStrategy):null,isInStrategyAction:isInStrategyAction,full_instructions_keys:Object.keys(instructions)},timestamp:Date.now(),sessionId:'debug-session',runId:'initial',hypothesisId:'H5'})}).catch(()=>{});
        // #endregion
        
        // Check if we have saved decisions or assumptions
        const hasSavedDecisions = savedStrategy && 
                                 savedStrategy.strategy_criteria && 
                                 savedStrategy.strategy_criteria.decisions_made &&
                                 Object.keys(savedStrategy.strategy_criteria.decisions_made).length > 0;
        
        const hasSavedAssumptions = savedStrategy && 
                                   savedStrategy.assumptions && 
                                   savedStrategy.assumptions.assumptions_made &&
                                   savedStrategy.assumptions.assumptions_made.length > 0;
        
        const showStrategySection = hasSavedDecisions || hasSavedAssumptions || isInStrategyAction;
        
        if (showStrategySection) {
            // Extract saved strategy data from strategy.json
            let strategyCriteriaData = {};
            let decisionsMade = {};
            let assumptionsMade = [];
            
            if (savedStrategy && savedStrategy.strategy_criteria) {
                // #region agent log
                fetch('http://127.0.0.1:7242/ingest/8c521aea-7def-453b-baa0-70f06cfd0592',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'instructions_view.js:372',message:'savedStrategy.strategy_criteria details',data:{strategy_criteria_keys:Object.keys(savedStrategy.strategy_criteria),has_criteria:!!savedStrategy.strategy_criteria.criteria,has_decisions_made:!!savedStrategy.strategy_criteria.decisions_made},timestamp:Date.now(),sessionId:'debug-session',runId:'initial',hypothesisId:'H8'})}).catch(()=>{});
                // #endregion
                
                // Get criteria (questions and options) - always load if available to show decisions with context
                // Previously only loaded in strategy action, but we need it everywhere to display decisions properly
                strategyCriteriaData = savedStrategy.strategy_criteria.criteria || {};
                // Get decisions made - always show if available
                decisionsMade = savedStrategy.strategy_criteria.decisions_made || {};
            }
            
            if (savedStrategy && savedStrategy.assumptions) {
                // Get assumptions made - always show if available
                assumptionsMade = savedStrategy.assumptions.assumptions_made || [];
            }
            
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/8c521aea-7def-453b-baa0-70f06cfd0592',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'instructions_view.js:380',message:'extracted strategy data',data:{strategyCriteriaData_keys:Object.keys(strategyCriteriaData),decisionsMade_keys:Object.keys(decisionsMade),assumptionsMade_length:assumptionsMade.length,showStrategySection:showStrategySection},timestamp:Date.now(),sessionId:'debug-session',runId:'initial',hypothesisId:'H5'})}).catch(()=>{});
            // #endregion
            
            // Fallback to guardrails if no saved data and we're in strategy action
            if (Object.keys(strategyCriteriaData).length === 0 && isInStrategyAction) {
                const fallbackData = instructions.strategy_criteria || instructions.guardrails?.decision_criteria || {};
                
                // If fallbackData has nested 'criteria' key, extract it; otherwise use as-is
                if (fallbackData.criteria) {
                    strategyCriteriaData = fallbackData.criteria;
                } else {
                    strategyCriteriaData = fallbackData;
                }
                
                // #region agent log
                fetch('http://127.0.0.1:7242/ingest/8c521aea-7def-453b-baa0-70f06cfd0592',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'instructions_view.js:391',message:'fallback criteria from instructions',data:{from_strategy_criteria:!!instructions.strategy_criteria,from_guardrails:!!instructions.guardrails?.decision_criteria,had_nested_criteria:!!fallbackData.criteria,strategyCriteriaData_keys:Object.keys(strategyCriteriaData)},timestamp:Date.now(),sessionId:'debug-session',runId:'initial',hypothesisId:'H8'})}).catch(()=>{});
                // #endregion
            }
            
            restructured.strategy_instructions = {
                strategy_criteria: strategyCriteriaData,
                decisions_made: decisionsMade,
                assumptions_made: assumptionsMade,
                action_instructions: instructions.action_instructions
            };
        }

        // 4. BUILD - Story Graph + Rules (ONLY show during build action)
        const buildRelatedKeys = ['schema', 'story_graph_template', 'story_graph_config', 'rules', 'build_instructions'];
        const hasBuildData = buildRelatedKeys.some(key => instructions[key]);
        if (hasBuildData && currentAction === 'build') {
            // Merge story_graph_template and story_graph_config into a single schema object
            let schemaData = instructions.schema || instructions.build_instructions?.schema || {};
        
            // Merge story_graph_template fields
            if (instructions.story_graph_template) {
                schemaData = { ...schemaData, ...instructions.story_graph_template };
            }
            
            // Merge story_graph_config fields
            if (instructions.story_graph_config) {
                schemaData = { ...schemaData, ...instructions.story_graph_config };
            }
            
            restructured.build_instructions = {
                schema: Object.keys(schemaData).length > 0 ? schemaData : null,
                rules: instructions.rules || instructions.build_instructions?.rules || []
            };
        }

        // 5. RENDER - Render Configs (ONLY show during render action)
        if (currentAction === 'render') {
            restructured.render_instructions = {
                render_config: instructions.render_config || null,
                render_config_paths: instructions.render_config_paths || [],
                render_template_paths: instructions.render_template_paths || [],
                render_output_paths: instructions.render_output_paths || []
            };
        }

        // 6. VALIDATE - Rules (ONLY show during validate action)
        if (currentAction === 'validate' && (instructions.rules || instructions.validation_rules)) {
            restructured.validate_instructions = {
                rules: instructions.rules || [],
                validation_rules: instructions.validation_rules || []
            };
        }

        // Replace instructions with restructured version
        instructions = restructured;

        // Define colors and display order/names - 6 sections (base + 5 action-specific)
        const propertyConfig = {
            'base_instructions': { name: 'Base Instructions', color: '#ff8c00', icon: '', iconPath: documentIconPath, defaultExpanded: false },
            'clarify_instructions': { name: 'Clarify', color: '#569cd6', icon: '', iconPath: lightbulbHeadIconPath, defaultExpanded: false },
            'strategy_instructions': { name: 'Strategy', color: '#c586c0', icon: '', iconPath: lightbulbIconPath, defaultExpanded: false },
            'build_instructions': { name: 'Build', color: '#4ec9b0', icon: '', iconPath: bullseyeIconPath, defaultExpanded: false },
            'render_instructions': { name: 'Render', color: '#ce9178', icon: '', iconPath: documentIconPath, defaultExpanded: false },
            'validate_instructions': { name: 'Validate', color: '#dcdcaa', icon: '', iconPath: lightbulbHeadIconPath, defaultExpanded: false }
        };

        // Get only the 4 main sections in order
        const validKeys = Object.keys(propertyConfig).filter(key => {
            const value = instructions[key];
            if (value === null || value === undefined) return false;
            if (typeof value === 'string' && value.trim() === '') return false;
            if (Array.isArray(value) && value.length === 0) return false;
            if (typeof value === 'object' && Object.keys(value).length === 0) return false;
            return true;
        });

        if (validKeys.length === 0) {
            return '';
        }

        // Generate collapsible sections for each property
        const sections = validKeys.map((key, index) => {
            const value = instructions[key];
            const config = propertyConfig[key] || { 
                name: this._formatPropertyName(key), 
                color: '#4ec9b0', 
                icon: '',
                iconPath: storyIconPath,
                defaultExpanded: false 
            };
            
            const sectionId = `instr-section-${index}`;
            const expanded = config.defaultExpanded ? 'true' : 'false';
            const expandedClass = config.defaultExpanded ? 'expanded' : '';
            
            // Format the content based on type
            let contentHtml;
            if (key === 'clarify_instructions') {
                contentHtml = this._formatClarifyInstructions(value);
            } else if (key === 'strategy_instructions') {
                contentHtml = this._formatStrategyInstructions(value);
            } else if (key === 'build_instructions') {
                contentHtml = this._formatBuildInstructions(value);
            } else if (key === 'render_instructions') {
                contentHtml = this._formatRenderInstructions(value);
            } else if (key === 'validate_instructions') {
                contentHtml = this._formatValidateInstructions(value);
            } else {
                contentHtml = this._formatInstructionValue(value, config.color);
            }
            
            // Determine icon display - use image if available
            const iconHtml = config.iconPath 
                ? `<img src="${config.iconPath}" style="margin-right: 8px; width: 20px; height: 20px; object-fit: contain; vertical-align: middle;" alt="${config.name}" />`
                : '';
            
            return `
        <div class="collapsible-section ${expandedClass}" style="margin-bottom: 8px;">
          <div class="collapsible-header" onclick="toggleSection('${sectionId}')" style="
            cursor: pointer;
            padding: 4px 5px;
            background-color: transparent;
            border-left: none;
            border-radius: 2px;
            display: flex;
            align-items: center;
            user-select: none;
          ">
            <span class="expand-icon">▸</span>
            ${iconHtml}
            <span style="font-weight: 600; color: var(--vscode-foreground); font-size: 14px;">${config.name}</span>
          </div>
          <div id="${sectionId}" class="collapsible-content" style="
            max-height: ${config.defaultExpanded ? 'none' : '0'};
            overflow: ${config.defaultExpanded ? 'visible' : 'hidden'};
            display: ${config.defaultExpanded ? 'block' : 'none'};
            transition: max-height 0.3s ease;
          ">
            <div style="padding: 5px; background-color: transparent; margin-top: 2px;">
              ${contentHtml}
            </div>
          </div>
        </div>`;
        }).join('');

        // Escape prompt content for safe embedding in HTML attribute
        const promptContentStr = typeof this.promptContent === 'string' ? this.promptContent : (this.promptContent ? String(this.promptContent) : '');
        const escapedPromptContent = promptContentStr.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n').replace(/\r/g, '\\r');
        
        return `
    <div class="section card-primary">
        <div class="collapsible-section expanded">
            <div class="collapsible-header" style="
                cursor: pointer;
                padding: 4px 5px;
                background-color: transparent;
                border-left: none;
                border-radius: 2px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                user-select: none;
            ">
                <div style="display: flex; align-items: center;" onclick="toggleSection('instructions-content')">
                    <span class="expand-icon">▸</span>
                    ${clipboardIconPath ? `<img src="${clipboardIconPath}" style="margin-right: 8px; width: 28px; height: 28px; object-fit: contain;" alt="Instructions Icon" />` : ''}
                    <span style="font-weight: 600; font-size: 20px;">Instructions</span>
                </div>
                <button id="submit-to-chat-btn" onclick="sendInstructionsToChat(event)" style="
                    background: rgba(255, 140, 0, 0.15);
                    border: none;
                    border-radius: 8px;
                    padding: 6px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.15s ease;
                    width: 48px;
                    height: 48px;
                " 
                onmouseover="this.style.backgroundColor='rgba(255, 140, 0, 0.3)'" 
                onmouseout="this.style.backgroundColor='rgba(255, 140, 0, 0.15)'"
                title="Submit instructions to chat">
                    ${botSubmitIconPath ? `<img src="${botSubmitIconPath}" style="width: 100%; height: 100%; object-fit: contain;" alt="Submit to Chat" />` : ''}
                </button>
                <script>
                    window._promptContent = ${JSON.stringify(promptContentStr)};
                </script>
            </div>
            <div id="instructions-content" class="collapsible-content" style="max-height: 600px; overflow-y: auto; overflow-x: hidden; transition: max-height 0.3s ease;">
                <div class="card-secondary" style="padding: 5px 10px;">
                    ${sections}
                    
                    <!-- Raw Instructions Subsection -->
                    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <div class="collapsible-section">
                            <div class="collapsible-header" style="
                                cursor: pointer;
                                padding: 8px 0;
                                display: flex;
                                align-items: center;
                                user-select: none;
                            " onclick="toggleSection('raw-instructions-content')">
                                <span class="expand-icon">▸</span>
                                <img src="${this.webview && this.extensionUri ? this.webview.asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'img', 'copy.png')).toString() : ''}" 
                                     style="margin-right: 8px; width: 20px; height: 20px; object-fit: contain; opacity: 0.9;" 
                                     alt="Raw" 
                                     onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';" />
                                <span style="font-weight: 600; font-size: 14px;">Raw Instructions (Test)</span>
                            </div>
                            <div id="raw-instructions-content" class="collapsible-content" style="max-height: 0; overflow: hidden; display: none; transition: max-height 0.3s ease;">
                                <div style="padding: 5px 0; margin-top: 8px;">
                                    <pre style="
                                        white-space: pre-wrap;
                                        word-wrap: break-word;
                                        font-family: 'Courier New', monospace;
                                        font-size: 11px;
                                        line-height: 1.4;
                                        color: rgba(255,255,255,0.8);
                                        background: rgba(0,0,0,0.3);
                                        padding: 6px;
                                        border-radius: 4px;
                                        margin: 0;
                                        max-height: 400px;
                                        overflow-y: auto;
                                    ">${promptContentStr ? promptContentStr.replace(/</g, '&lt;').replace(/>/g, '&gt;') : 'Click Submit button or run an instructions command to populate'}</pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`;
    }
    
    _formatPropertyName(key) {
        // Convert snake_case or camelCase to Title Case
        return key
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ')
            .trim();
    }
    
    _formatClarifyInstructions(value) {
        // Format clarify-specific instructions - Q&A and evidence
        if (typeof value !== 'object' || !value) {
            return this.escapeHtml(String(value));
        }
        
        let html = '';
        let questions = [];
        let evidence = [];
        
        // Determine source of questions and answers
        if (value.clarification_data && Array.isArray(value.clarification_data) && value.clarification_data.length > 0) {
            // Use clarification.json if present
            questions = value.clarification_data;
        } else if (value.guardrails && value.guardrails.required_context && Array.isArray(value.guardrails.required_context.key_questions)) {
            // Use guardrails questions if clarification.json not present
            questions = value.guardrails.required_context.key_questions.map(q => ({
                question: q,
                answer: ''
            }));
        }

        // Get required evidence and provided evidence from evidence object
        let requiredEvidence = [];
        let providedEvidence = {};
        
        if (value.evidence && typeof value.evidence === 'object') {
            // Evidence object should have 'required' and 'provided' keys
            requiredEvidence = value.evidence.required || [];
            providedEvidence = value.evidence.provided || {};
        }
        
        // Fallback to guardrails if no evidence structure
        if (requiredEvidence.length === 0 && value.guardrails && value.guardrails.required_context && Array.isArray(value.guardrails.required_context.evidence)) {
            requiredEvidence = value.guardrails.required_context.evidence;
        }

        // Render Q&A Section - questions with editable answer textboxes
        if (questions.length > 0) {
            questions.forEach((item, idx) => {
                const questionText = typeof item === 'string' ? item : item.question;
                const answerText = typeof item === 'object' ? (item.answer || '') : '';
                
                if (questionText) {
                    html += `<div class="input-container" style="margin-top: ${idx > 0 ? '12px' : '0'};">`;
                    html += `<div class="input-header">${this.escapeHtml(questionText)}</div>`;
                    html += `<textarea id="clarify-answer-${idx}" data-question="${this.escapeForAttribute(questionText)}" rows="3" onblur="saveClarifyAnswers()" style="width: 100%; padding: var(--input-padding); background-color: var(--input-bg); border: none; color: var(--vscode-foreground); resize: vertical; font-family: inherit; font-size: var(--font-size-base);">${this.escapeHtml(answerText)}</textarea>`;
                    html += `</div>`;
                }
            });
        }
        
        // Render Evidence Section - Required evidence as list + editable "Evidence Provided" box
        if (requiredEvidence.length > 0 || Object.keys(providedEvidence).length > 0) {
            html += '<div style="margin-top: 16px;">';
            html += '<div class="input-header">Evidence</div>';
            
            // Show required evidence as bullet list
            if (requiredEvidence.length > 0) {
                html += '<div style="margin-top: 8px;">';
                requiredEvidence.forEach(item => {
                    html += `<div style="margin-bottom: 4px;">• ${this.escapeHtml(String(item))}</div>`;
                });
                html += '</div>';
            }
            
            // Show editable "Evidence Provided" textarea
            html += '<div style="margin-top: 12px;">';
            html += '<div class="input-header" style="font-size: 13px; margin-bottom: 4px;">Evidence Provided</div>';
            
            // Convert providedEvidence object to text for textarea
            let providedText = '';
            if (Object.keys(providedEvidence).length > 0) {
                providedText = Object.entries(providedEvidence)
                    .map(([key, val]) => `${key}: ${val}`)
                    .join('\n');
            }
            
            html += `<textarea id="clarify-evidence" rows="3" onblur="saveClarifyEvidence()" placeholder="Enter evidence sources provided (e.g., Requirements doc: project-spec.md)" style="width: 100%; padding: var(--input-padding); background-color: var(--input-bg); border: none; color: var(--vscode-foreground); resize: vertical; font-family: inherit; font-size: var(--font-size-base);">${this.escapeHtml(providedText)}</textarea>`;
            html += '</div>';
            html += '</div>';
        }
        
        return html;
    }
    
    _formatStrategyInstructions(value) {
        // Format strategy-specific instructions - decision criteria and assumptions
        if (typeof value !== 'object' || !value) {
            return this.escapeHtml(String(value));
        }

        console.log('[DEBUG] Strategy Instructions value:', JSON.stringify(value, null, 2));
        
        let html = '';
        const strategyCriteriaObj = value.strategy_criteria || {};
        const decisionsMade = value.decisions_made || {};
        const assumptionsMade = value.assumptions_made || [];

        // Render Decision Criteria - radio buttons with saved decisions highlighted
        // strategyCriteriaObj format: { 'key1': {question: '...', options: [...]}, ... }
        // decisionsMade format: { 'key1': 'selected option text', ... }
        const criteriaKeys = Object.keys(strategyCriteriaObj);
        if (criteriaKeys.length > 0) {
            criteriaKeys.forEach((criteriaKey, criteriaIdx) => {
                const criteria = strategyCriteriaObj[criteriaKey];
                if (typeof criteria === 'object' && criteria !== null) {
                    html += '<div style="margin-bottom: 16px;">';
                    
                    // Render the question as header
                    const question = criteria.question || criteriaKey;
                    html += `<div class="input-header">${this.escapeHtml(question)}</div>`;
                    
                    // Get the saved decision for this criteria
                    const savedDecision = decisionsMade[criteriaKey];
                    
                    // Render options as radio buttons
                    const options = criteria.options || [];
                    if (options.length > 0) {
                        html += '<div style="margin-top: 8px;">';
                        options.forEach((option, optionIdx) => {
                            const radioName = `decision-criteria-${criteriaIdx}`;
                            
                            // Extract option text (could be string or object with 'name' field)
                            let optionText = '';
                            if (typeof option === 'string') {
                                optionText = option;
                            } else if (typeof option === 'object' && option !== null) {
                                optionText = option.name || option.id || JSON.stringify(option);
                            }
                            
                            // Check if this option matches the saved decision
                            const isSelected = savedDecision && optionText === savedDecision;
                            
                            // Escape for use in onclick attribute
                            const escapedCriteriaKey = this.escapeHtml(criteriaKey).replace(/'/g, "\\'");
                            const escapedOptionText = this.escapeHtml(optionText).replace(/'/g, "\\'");
                            
                            html += `<div style="margin-bottom: 8px;">`;
                            html += `<label style="display: flex; align-items: flex-start; cursor: pointer;">`;
                            html += `<input type="radio" name="${radioName}" value="${optionIdx}" ${isSelected ? 'checked' : ''} onchange="saveStrategyDecision('${escapedCriteriaKey}', '${escapedOptionText}')" style="margin-right: 8px; margin-top: 4px; cursor: pointer;" />`;
                            html += `<span style="flex: 1; ${isSelected ? 'font-weight: 600; color: var(--vscode-textLink-foreground);' : ''}">${this.escapeHtml(optionText)}</span>`;
                            html += `</label>`;
                            html += `</div>`;
                        });
                        html += '</div>';
                    }
                    
                    html += '</div>';
                }
            });
        }

        // Render Assumptions - always show as editable textarea with saved values pre-filled
        html += '<div class="input-container" style="margin-top: 6px;">';
        html += '<div class="input-header">Assumptions</div>';

        // Pre-fill textarea with saved assumptions (one per line) or empty
        const assumptionsText = assumptionsMade.length > 0
            ? assumptionsMade.join('\n')
            : '';
        html += `<textarea id="strategy-assumptions" rows="5" onblur="saveStrategyAssumptions()" placeholder="Enter assumptions (one per line)" style="width: 100%; padding: var(--input-padding); background-color: var(--input-bg); border: none; color: var(--vscode-foreground); resize: vertical; font-family: inherit; font-size: var(--font-size-base);">${this.escapeHtml(assumptionsText)}</textarea>`;
        html += '</div>';

        return html;
    }

    _formatBuildInstructions(value) {
        // Format build-specific instructions - Story Graph and Rules only
        if (typeof value !== 'object' || !value) {
            return this.escapeHtml(String(value));
        }
        
        let html = '';
        
        // Story Graph Section - collapsible
        if (value.schema) {
            html += '<div class="collapsible-section" style="margin-bottom: 8px;">';
            html += '<div class="collapsible-header" style="margin-bottom: 8px; cursor: pointer; display: flex; align-items: center;" onclick="toggleSection(\'build-kg-section\')">';
            html += '<span class="expand-icon">▸</span>';
            html += '<strong style="font-size: 14px;">Story Graph</strong>';
            html += '</div>';
            html += '<div id="build-kg-section" class="collapsible-content" style="max-height: 0; overflow: hidden; display: none; transition: max-height 0.3s ease;">';
            html += '<div style="padding-left: 14px;">';
            html += this._formatBuildStoryGraph(value.schema);
            html += '</div>';
            html += '</div>';
            html += '</div>';
        }
        
        // Rules Section - collapsible
        if (value.rules && Array.isArray(value.rules) && value.rules.length > 0) {
            html += '<div class="collapsible-section" style="margin-bottom: 8px;">';
            html += '<div class="collapsible-header" style="margin-bottom: 8px; cursor: pointer; display: flex; align-items: center;" onclick="toggleSection(\'build-rules-section\')">';
            html += '<span class="expand-icon">▸</span>';
            html += '<strong style="font-size: 14px;">Rules</strong>';
            html += '</div>';
            html += '<div id="build-rules-section" class="collapsible-content" style="max-height: 0; overflow: hidden; display: none; transition: max-height 0.3s ease;">';
            html += '<div style="padding-left: 14px;">';
            html += this._formatBuildRules(value.rules);
            html += '</div>';
            html += '</div>';
            html += '</div>';
        }

        return html;
    }

    _formatBuildStoryGraph(data) {
        if (!data) return '';

        // Merge all items into one - get template, output filename, path directory, and exists
        let mergedItem = {
            template_path: null,
            output_file: null,
            path_dir: null,
            exists: null
        };

        if (Array.isArray(data)) {
            data.forEach(item => {
                if (typeof item === 'object' && item !== null) {
                    if (item.template_path && !mergedItem.template_path) {
                        mergedItem.template_path = item.template_path;
                    }
                    // Only use item.template as fallback if it looks like a full path (contains path separators)
                    if (item.template && !mergedItem.template_path && (item.template.includes('/') || item.template.includes('\\'))) {
                        mergedItem.template_path = item.template;
                    }
                    if (item.output && !mergedItem.output_file) {
                        mergedItem.output_file = item.output;
                    }
                    if (item.path && !mergedItem.path_dir) {
                        mergedItem.path_dir = item.path;
                    }
                    if (item.exists !== undefined && mergedItem.exists === null) {
                        mergedItem.exists = item.exists;
                    }
                }
            });
        } else if (typeof data === 'object' && data !== null) {
            if (data.template_path) mergedItem.template_path = data.template_path;
            // Only use data.template as fallback if it looks like a full path (contains path separators)
            if (data.template && !mergedItem.template_path && (data.template.includes('/') || data.template.includes('\\'))) {
                mergedItem.template_path = data.template;
            }
            if (data.output) mergedItem.output_file = data.output;
            if (data.path) mergedItem.path_dir = data.path;
            if (data.exists !== undefined) mergedItem.exists = data.exists;
        }

        // Remove nulls
        Object.keys(mergedItem).forEach(key => {
            if (mergedItem[key] === null) delete mergedItem[key];
        });

        let html = '';
        // Template - show filename, link to full path
        if (mergedItem.template_path) {
            html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(mergedItem.template_path)}">`;
            html += `<span class="label">Template:</span>`;
            html += `<span class="value">${this.renderFileLink(mergedItem.template_path)}</span>`;
            html += '</div>';
        }
        // Output - show filename, link to full path (path_dir + output_file)
        if (mergedItem.output_file) {
            const fullOutputPath = mergedItem.path_dir ? path.join(mergedItem.path_dir, mergedItem.output_file) : mergedItem.output_file;
            html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(fullOutputPath)}">`;
            html += `<span class="label">Output:</span>`;
            html += `<span class="value">${this.renderFileLink(fullOutputPath)}</span>`;
            html += '</div>';
        }
        // Path - show directory path as clickable link
        if (mergedItem.path_dir) {
            html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(mergedItem.path_dir)}">`;
            html += `<span class="label">Path:</span>`;
            const jsEscapedPath = mergedItem.path_dir.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
            html += `<span class="value"><a href="#" onclick="openFile('${jsEscapedPath}'); return false;" style="color: var(--vscode-textLink-foreground); text-decoration: none; cursor: pointer;">${this.escapeHtml(mergedItem.path_dir)}</a></span>`;
            html += '</div>';
        }
        // Existing - Yes/No
        if (mergedItem.exists !== undefined) {
            html += `<div class="info-display" style="margin-top: 4px;">`;
            html += `<span class="label">Existing:</span>`;
            html += `<span class="value">${mergedItem.exists ? 'Yes' : 'No'}</span>`;
            html += '</div>';
    }
        return html;
    }

    _formatBuildRules(rules) {
        if (!Array.isArray(rules) || rules.length === 0) return '';

        let html = '';
        rules.forEach((rule, idx) => {
            const rulePath = typeof rule === 'string' ? rule : rule.rule_file || '';
            if (rulePath) {
                html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(rulePath)}">`;
                html += `<span class="label">Rule ${idx + 1}:</span>`;
                html += `<span class="value">${this.renderFileLink(rulePath)}</span>`;
                html += '</div>';
            }
        });
        return html;
    }

    renderFileLink(fullPath) {
        if (!fullPath) return '';
        const fileName = fullPath.split(/[\/\\]/).pop();
        const jsEscapedPath = fullPath.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
        return `<a href="#" onclick="openFile('${jsEscapedPath}'); return false;" style="color: var(--vscode-textLink-foreground); text-decoration: none; cursor: pointer;">${this.escapeHtml(fileName)}</a>`;
    }

    _formatRenderInstructions(value) {
        // Format render-specific instructions - Render Configs
        if (typeof value !== 'object' || !value) {
            return this.escapeHtml(String(value));
        }
        
        let html = '';
        
        // Render Config Paths (similar to Build rules)
        if (Array.isArray(value.render_config_paths) && value.render_config_paths.length > 0) {
            value.render_config_paths.forEach((configPath, idx) => {
                html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(configPath)}">`;
                html += `<span class="label">Config ${idx + 1}:</span>`;
                html += `<span class="value">${this.renderFileLink(configPath)}</span>`;
                html += '</div>';
            });
        }

        // Render Template Paths (similar to Build template_path)
        if (Array.isArray(value.render_template_paths) && value.render_template_paths.length > 0) {
            value.render_template_paths.forEach((templatePath, idx) => {
                html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(templatePath)}">`;
                html += `<span class="label">Template ${idx + 1}:</span>`;
                html += `<span class="value">${this.renderFileLink(templatePath)}</span>`;
                html += '</div>';
            });
        }

        // Render Output Paths (drawio, md, txt files)
        if (Array.isArray(value.render_output_paths) && value.render_output_paths.length > 0) {
            value.render_output_paths.forEach((outputPath, idx) => {
                html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(outputPath)}">`;
                html += `<span class="label">Output ${idx + 1}:</span>`;
                html += `<span class="value">${this.renderFileLink(outputPath)}</span>`;
                html += '</div>';
            });
        }

        // Render Config Section - similar to Story Graph
        if (value.render_config) {
            const configs = Array.isArray(value.render_config) ? value.render_config : [value.render_config];
            
            configs.forEach((config, idx) => {
                html += '<div class="collapsible-section" style="margin-bottom: 8px;">';
                html += `<div class="collapsible-header" style="margin-bottom: 8px; cursor: pointer; display: flex; align-items: center;" onclick="toggleSection('render-config-section-${idx}')">`;
                html += '<span class="expand-icon">▸</span>';
                html += `<strong style="font-size: 14px;">Render Config ${configs.length > 1 ? idx + 1 : ''}</strong>`;
                html += '</div>';
                html += `<div id="render-config-section-${idx}" class="collapsible-content" style="max-height: 0; overflow: hidden; display: none; transition: max-height 0.3s ease;">`;
                html += '<div style="padding-left: 14px;">';
                html += this._formatRenderConfig(config);
                html += '</div>';
                html += '</div>';
                html += '</div>';
            });
        }

        return html;
    }

    _formatRenderConfig(config) {
        if (!config) return '';

        let html = '';
        
        // Template
        if (config.template_path || config.template) {
            const templatePath = config.template_path || config.template;
            html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(templatePath)}">`;
            html += `<span class="label">Template:</span>`;
            html += `<span class="value">${this.renderFileLink(templatePath)}</span>`;
            html += '</div>';
        }
        
        // Output
        if (config.output || config.output_file) {
            const outputFile = config.output || config.output_file;
            const fullOutputPath = config.path ? path.join(config.path, outputFile) : outputFile;
            html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(fullOutputPath)}">`;
            html += `<span class="label">Output:</span>`;
            html += `<span class="value">${this.renderFileLink(fullOutputPath)}</span>`;
            html += '</div>';
        }
        
        // Path
        if (config.path || config.path_dir) {
            const dirPath = config.path || config.path_dir;
            html += `<div class="info-display" style="margin-top: 4px;" title="${this.escapeHtml(dirPath)}">`;
            html += `<span class="label">Path:</span>`;
            const jsEscapedPath = dirPath.replace(/\\/g, '\\\\').replace(/'/g, "\\'");
            html += `<span class="value"><a href="#" onclick="openFile('${jsEscapedPath}'); return false;" style="color: var(--vscode-textLink-foreground); text-decoration: none; cursor: pointer;">${this.escapeHtml(dirPath)}</a></span>`;
            html += '</div>';
    }
    
        // Existing
        if (config.exists !== undefined) {
            html += `<div class="info-display" style="margin-top: 4px;">`;
            html += `<span class="label">Existing:</span>`;
            html += `<span class="value">${config.exists ? 'Yes' : 'No'}</span>`;
            html += '</div>';
        }
        
        return html;
    }

    _formatValidateInstructions(value) {
        // Format validate-specific instructions - Rules + validation rule objects
        if (typeof value !== 'object' || !value) {
            return this.escapeHtml(String(value));
        }

        let html = '';

        // Rules paths Section - collapsible
        if (value.rules && Array.isArray(value.rules) && value.rules.length > 0) {
            html += '<div class="collapsible-section" style="margin-bottom: 8px;">';
            html += '<div class="collapsible-header" style="margin-bottom: 8px; cursor: pointer; display: flex; align-items: center;" onclick="toggleSection(\'validate-rules-section\')">';
            html += '<span class="expand-icon">▸</span>';
            html += '<strong style="font-size: 14px;">Rule Files</strong>';
            html += '</div>';
            html += '<div id="validate-rules-section" class="collapsible-content" style="max-height: 0; overflow: hidden; display: none; transition: max-height 0.3s ease;">';
            html += '<div style="padding-left: 14px;">';
            html += this._formatBuildRules(value.rules);
            html += '</div>';
            html += '</div>';
            html += '</div>';
        }

        // Validation rule objects (with scanner status, descriptions)
        if (value.validation_rules && Array.isArray(value.validation_rules) && value.validation_rules.length > 0) {
            html += '<div class="collapsible-section" style="margin-bottom: 8px;">';
            html += '<div class="collapsible-header" style="margin-bottom: 8px; cursor: pointer; display: flex; align-items: center;" onclick="toggleSection(\'validate-rules-objects-section\')">';
            html += '<span class="expand-icon">▸</span>';
            html += '<strong style="font-size: 14px;">Validation Rules</strong>';
            html += '</div>';
            html += '<div id="validate-rules-objects-section" class="collapsible-content" style="max-height: 0; overflow: hidden; display: none; transition: max-height 0.3s ease;">';
            html += '<div style="padding-left: 14px;">';
            html += '<ul style="padding-left: 16px; margin: 0;">';
            for (const rule of value.validation_rules) {
                const rule_file = rule.rule_file || 'unknown';
                const rc = rule.rule_content || {};
                const name = rc.name || rule_file.split('/').pop().replace('.json', '').replace(/_/g, ' ');
                const desc = rc.description || '';
                const priority = rc.priority !== undefined ? rc.priority : 'N/A';
                const hasScanner = (rc.scanner || rc.scanners) ? '[Scanner]' : '[Manual]';
                html += `<li style="margin-bottom: 6px;">`;
                html += `<div><strong>${this.escapeHtml(name)}</strong> (Priority ${this.escapeHtml(priority)}, ${hasScanner})</div>`;
                html += `<div style="font-size: 12px; color: var(--vscode-descriptionForeground);">File: <code>${this.escapeHtml(rule_file)}</code></div>`;
                if (desc) {
                    html += `<div style="margin-top: 2px;">${this.escapeHtml(desc)}</div>`;
                }
                html += `</li>`;
            }
            html += '</ul>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
        }

        return html;
    }

    _formatInstructionValue(value, borderColor) {
        if (Array.isArray(value)) {
            // Array: join with newlines and format
            const text = value.join('\n');
            return this.escapeHtml(text)
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        } else if (typeof value === 'object' && value !== null) {
            // Check if this is clarification data with phase-based structure (e.g., shape.key_questions.answers)
            const phaseKeys = Object.keys(value);
            for (const phaseKey of phaseKeys) {
                const phaseData = value[phaseKey];
                if (phaseData && typeof phaseData === 'object' && phaseData.key_questions && phaseData.key_questions.answers) {
                    return this._formatClarificationData(value, borderColor);
                }
            }
            
            // Check if this is direct key_questions.answers structure
            if (value.key_questions && value.key_questions.answers) {
                return this._formatQuestionsAndAnswers(value.key_questions.answers, borderColor);
            }
            
            // Check if this is strategy data with assumptions structure
            if (value.assumptions && (value.assumptions.assumptions || value.assumptions.review_status)) {
                return this._formatStrategyData(value, borderColor);
            }
            
            // Object: pretty print JSON
            return `<pre style="margin: 0; white-space: pre-wrap; font-family: monospace; font-size: 11px; line-height: 1.4;">${this.escapeHtml(JSON.stringify(value, null, 2))}</pre>`;
        } else {
            // String or other: escape and format
            return this.escapeHtml(String(value))
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        }
    }

    _formatClarificationData(clarificationData, borderColor) {
        if (!clarificationData || typeof clarificationData !== 'object') {
            return '<div style="color: var(--vscode-descriptionForeground); font-style: italic;">No clarification data available</div>';
        }

        let html = '';

        // Process each phase (e.g., "shape", "discovery", etc.)
        const phases = Object.keys(clarificationData);
        phases.forEach((phaseName, phaseIndex) => {
            const phaseData = clarificationData[phaseName];
            
            if (!phaseData || typeof phaseData !== 'object') return;

            // Phase header
            html += `
        <div style="
          margin-bottom: 6px;
          padding: 8px 0;
          background-color: transparent;
          border-radius: 0;
          border-left: none;
        ">
          <span style="font-weight: 600; color: var(--vscode-foreground); font-size: 13px; text-transform: capitalize;">
            ${this.escapeHtml(phaseName)} Phase
          </span>
        </div>`;

            // Key Questions & Answers
            if (phaseData.key_questions && phaseData.key_questions.answers) {
                html += this._formatQuestionsAndAnswers(phaseData.key_questions.answers, borderColor);
            }

            // Evidence sources
            if (phaseData.evidence && phaseData.evidence.sources && Array.isArray(phaseData.evidence.sources)) {
                html += `
          <div style="
            margin-top: 6px;
            padding: 8px 0;
            background-color: transparent;
            border-radius: 0;
            border-left: none;
          ">
            <div style="font-weight: 600; color: var(--vscode-foreground); margin-bottom: 6px; font-size: 11px;">
              Evidence Sources
            </div>
            <ul style="margin: 0; padding-left: 0; list-style-type: none; font-size: 10px; line-height: 1.6;">
              ${phaseData.evidence.sources.map(source => 
                `<li style="color: var(--vscode-foreground); margin-bottom: 4px;">• ${this.escapeHtml(source)}</li>`
              ).join('')}
            </ul>
          </div>`;
            }

            // Context items
            if (phaseData.context && Array.isArray(phaseData.context)) {
                html += `
          <div style="
            margin-top: 6px;
            padding: 8px 0;
            background-color: transparent;
            border-radius: 0;
            border-left: none;
          ">
            <div style="font-weight: 600; color: var(--vscode-foreground); margin-bottom: 6px; font-size: 11px;">
              Context
            </div>
            <ul style="margin: 0; padding-left: 0; list-style-type: none; font-size: 10px; line-height: 1.6;">
              ${phaseData.context.map(item => 
                `<li style="color: var(--vscode-foreground); margin-bottom: 4px;">• ${this.escapeHtml(item)}</li>`
              ).join('')}
            </ul>
          </div>`;
            }

            // Add spacing between phases
            if (phaseIndex < phases.length - 1) {
                html += '<div style="margin-bottom: 10px;"></div>';
            }
        });

        return html || '<div style="color: var(--vscode-descriptionForeground); font-style: italic;">No clarification details available</div>';
    }

    _formatQuestionsAndAnswers(answers, borderColor) {
        if (!answers || typeof answers !== 'object') {
            return '<div style="color: var(--vscode-descriptionForeground); font-style: italic;">No questions answered yet</div>';
        }

        const entries = Object.entries(answers);
        if (entries.length === 0) {
            return '<div style="color: var(--vscode-descriptionForeground); font-style: italic;">No questions answered yet</div>';
        }

        const qaBlocks = entries.map(([question, answer], index) => {
            const questionId = `question-${index}`;
            const answerId = `answer-${index}`;
            return `<div class="input-container" style="margin-bottom: ${index < entries.length - 1 ? '20px' : '0'};">
        <div class="input-header">${this.escapeHtml(question)}</div>
        <textarea id="${answerId}" placeholder="Enter answer..." oninput="autoResizeTextarea(this)" onchange="updateQuestionAnswer('${this.escapeForJs(question)}', this.value)">${this.escapeHtml(answer || '')}</textarea>
      </div>`;
        }).join('');

        return qaBlocks;
    }

    _formatStrategyData(strategy, borderColor) {
        if (!strategy || typeof strategy !== 'object') {
            return '<div style="color: var(--vscode-descriptionForeground); font-style: italic;">No strategy data available</div>';
        }
        
        let html = '';
        
        // Format assumptions section
        if (strategy.assumptions) {
            const assumptions = strategy.assumptions;
            
            // Review status
            if (assumptions.review_status) {
                html += `
          <div style="
            margin-bottom: 6px;
            padding: 8px 0;
            background-color: transparent;
            border-radius: 0;
            border-left: none;
          ">
            <span style="font-weight: 400; color: var(--vscode-foreground);">Review Status:</span>
            <span style="margin-left: 8px; color: var(--vscode-foreground);">${this.escapeHtml(assumptions.review_status)}</span>
          </div>`;
            }

            // Individual assumptions
            if (assumptions.assumptions && Array.isArray(assumptions.assumptions)) {
                assumptions.assumptions.forEach((item, index) => {
                    const statusIcon = ''; // No emoji fallbacks - use images only
                    
                    html += `
            <div style="
              margin-bottom: ${index < assumptions.assumptions.length - 1 ? '12px' : '0'};
              padding: 8px 0;
              background-color: transparent;
              border-radius: 0;
              border-left: none;
            ">
              <div style="
                display: flex;
                align-items: flex-start;
                margin-bottom: 8px;
              ">
                <span style="
                  font-weight: 600;
                  color: var(--vscode-foreground);
                  font-size: 12px;
                  line-height: 1.4;
                  flex: 1;
                ">
                  ${this.escapeHtml(item.assumption)}
                </span>
                <span style="
                  padding: 2px 8px;
                  border-radius: 3px;
                  font-size: 10px;
                  font-weight: 400;
                  color: var(--vscode-foreground);
                  border: 1px solid rgba(255, 255, 255, 0.2);
                ">
                  ${statusIcon} ${this.escapeHtml(item.status || 'UNKNOWN')}
                </span>
              </div>
              ${item.justification ? `
                <div style="
                  color: var(--vscode-foreground);
                  font-size: 11px;
                  line-height: 1.5;
                  padding-left: 0;
                  white-space: pre-wrap;
                  word-wrap: break-word;
                  border-left: none;
                  padding: 8px 0;
                  margin-top: 8px;
                ">
                  ${this.escapeHtml(item.justification)}
                </div>` : ''}
            </div>`;
                });
            }
        }
        
        return html || '<div style="color: var(--vscode-descriptionForeground); font-style: italic;">No strategy details available</div>';
    }
}

module.exports = InstructionsSection;
