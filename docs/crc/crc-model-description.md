# Domain Model Description: Agile Bots

**File Name**: `agile-bots-domain-model-description.md`
**Location**: `agile_bots/docs/stories/agile-bots-domain-model-description.md`

## Solution Purpose
Domain model for Agile Bots

---

## Domain Model Descriptions

### Module: actions


#### ActionDataSubSection

**Key Responsibilities:**
- **Wraps action JSON**: This responsibility involves collaboration with Action JSON.
- **Displays action properties**: This responsibility involves collaboration with Object, Action JSON.

#### ActionStateManager

**Key Responsibilities:**
- **Get state file path**: This responsibility involves collaboration with Path.
- **Load or create state**: This responsibility involves collaboration with State File, Dict.
- **Save state**: This responsibility involves collaboration with Action, State File.
- **Load state**: This responsibility involves collaboration with Actions List, Current Index.
- **Find action index**: This responsibility involves collaboration with Actions List, Action Name, Integer.
- **Filter completed actions**: This responsibility involves collaboration with Completed Actions, Target Index, Actions List, List.

#### ActionsView

**Key Responsibilities:**
- **Wraps actions JSON**: This responsibility involves collaboration with Actions JSON.
- **Displays action names list**: This responsibility involves collaboration with List, Action JSON.
- **Navigates to action**: This responsibility involves collaboration with CLI, Action.
- **Displays status indicators**: This responsibility involves collaboration with Status, Action JSON.
- **Executes action**: This responsibility involves collaboration with CLI, Action.
- **Displays completion progress**: This responsibility involves collaboration with Progress, Action JSON.

#### Base Action

**Key Responsibilities:**
- **Inject Instructions**: This responsibility involves collaboration with Behavior.
- **Load Relevant Content + Inject Into Instructions**: This responsibility involves collaboration with Content.
- **Save content changes**: This responsibility involves collaboration with Content.

#### JSONAction

**Key Responsibilities:**
- **Serialize action to JSON dict**: This responsibility involves collaboration with Action, Dict.
- **Include action metadata**: This responsibility involves collaboration with Name, Description, Status.
- **Wraps domain action**: This responsibility involves collaboration with Action.

#### MarkdownAction

**Key Responsibilities:**
- **Serialize action to Markdown**: This responsibility involves collaboration with Action, String.
- **Format action documentation**: This responsibility involves collaboration with Action Name, Description, Subsection.
- **Wraps domain action**: This responsibility involves collaboration with Action.

#### TTYAction

**Key Responsibilities:**
- **Serialize action to TTY**: This responsibility involves collaboration with Action, String.
- **Format action line**: This responsibility involves collaboration with Action Name, Marker, Indent.
- **Wraps domain action**: This responsibility involves collaboration with Action.

### Module: actions.build


#### BuildDataSubSection

**Key Responsibilities:**
- **Wraps build JSON**: This responsibility involves collaboration with Build JSON.
- **Displays knowledge graph spec**: This responsibility involves collaboration with Object, KnowledgeGraphSpec JSON.
- **Displays graph structure**: This responsibility involves collaboration with Object, KnowledgeGraphSpec JSON.
- **Displays builder instructions**: This responsibility involves collaboration with String, BuilderInstructions JSON.
- **Opens graph file**: This responsibility involves collaboration with CLI, Path JSON.

#### BuildInstructionsSection

**Key Responsibilities:**
- **Wraps build subsection**: This responsibility involves collaboration with BuildDataSubSection.

#### BuildKnowledgeAction

**Key Responsibilities:**
- **Inject knowledge graph template**: This responsibility involves collaboration with Behavior, Content, Knowledge Graph Spec, Knowledge Graph.
- **Inject builder instructions**: This responsibility involves collaboration with Behavior, Content, Build Instructions.
- **Save Knowledge graph**: This responsibility involves collaboration with Behavior, Content, Knowledge Graph.

#### JSONBuildKnowledge

**Key Responsibilities:**
- **Serialize build action to JSON**: This responsibility involves collaboration with BuildKnowledgeAction, JSON String.
- **Include build metadata**: This responsibility involves collaboration with Knowledge Graph Spec, JSON.
- **Wraps domain action**: This responsibility involves collaboration with BuildKnowledgeAction.

#### MarkdownBuildKnowledge

**Key Responsibilities:**
- **Serialize build action to Markdown**: This responsibility involves collaboration with BuildKnowledgeAction, Markdown String.
- **Format build documentation**: This responsibility involves collaboration with Knowledge Graph Spec, Markdown.
- **Wraps domain action**: This responsibility involves collaboration with BuildKnowledgeAction.

#### TTYBuildKnowledge

**Key Responsibilities:**
- **Serialize build action to TTY**: This responsibility involves collaboration with BuildKnowledgeAction, String.
- **Format build status**: This responsibility involves collaboration with Status, TTY String.
- **Wraps domain action**: This responsibility involves collaboration with BuildKnowledgeAction.

### Module: actions.clarify


#### ClarifyDataSubSection

**Key Responsibilities:**
- **Wraps key questions JSON**: This responsibility involves collaboration with KeyQuestions JSON.
- **Displays key questions**: This responsibility involves collaboration with List, KeyQuestion JSON.
- **Updates evidence**: This responsibility involves collaboration with CLI, Evidence JSON.
- **Edits answer**: This responsibility involves collaboration with CLI, KeyQuestion JSON.

#### ClarifyInstructionsSection

**Key Responsibilities:**
- **Wraps clarify subsection**: This responsibility involves collaboration with ClarifyDataSubSection.

#### GatherContextAction

**Key Responsibilities:**
- **Inject gather context instructions**: This responsibility involves collaboration with Behavior, Guardrails, Required Clarifications.
- **Inject questions and evidence**: This responsibility involves collaboration with Behavior, Guardrails, Key Questions, Evidence.

#### JSONGatherContext

**Key Responsibilities:**
- **Serialize clarify action to JSON**: This responsibility involves collaboration with GatherContextAction, JSON String.
- **Include questions and evidence**: This responsibility involves collaboration with Questions, Evidence, JSON.
- **Wraps domain action**: This responsibility involves collaboration with GatherContextAction.

#### MarkdownGatherContext

**Key Responsibilities:**
- **Serialize clarify action to Markdown**: This responsibility involves collaboration with GatherContextAction, Markdown String.
- **Format questions list**: This responsibility involves collaboration with Questions, Evidence, Markdown.
- **Wraps domain action**: This responsibility involves collaboration with GatherContextAction.

#### TTYGatherContext

**Key Responsibilities:**
- **Serialize clarify action to TTY**: This responsibility involves collaboration with GatherContextAction, TTY String.
- **Format key questions**: This responsibility involves collaboration with Questions, Evidence, TTY String.
- **Wraps domain action**: This responsibility involves collaboration with GatherContextAction.

### Module: actions.render


#### Content

**Key Responsibilities:**
- **Render outputs**: This responsibility involves collaboration with Template, Renderer, Render Spec.
- **Synchronize formats**: This responsibility involves collaboration with Synchronizer, Extractor, Synchronizer Spec.
- **Save knowledge graph**: This responsibility involves collaboration with Knowledge Graph.
- **Load rendered content**: This responsibility involves collaboration with na.
- **Present rendered content**: This responsibility involves collaboration with na.

#### JSONRenderOutput

**Key Responsibilities:**
- **Serialize render action to JSON**: This responsibility involves collaboration with RenderOutputAction, JSON String.
- **Include render spec**: This responsibility involves collaboration with Render Spec, Templates, JSON.
- **Wraps domain action**: This responsibility involves collaboration with RenderOutputAction.

#### MarkdownRenderOutput

**Key Responsibilities:**
- **Serialize render action to Markdown**: This responsibility involves collaboration with RenderOutputAction, Markdown String.
- **Format render documentation**: This responsibility involves collaboration with Render Spec, Templates, Markdown.
- **Wraps domain action**: This responsibility involves collaboration with RenderOutputAction.

#### RenderDataSubSection

**Key Responsibilities:**
- **Wraps render JSON**: This responsibility involves collaboration with Render JSON.
- **Displays render spec**: This responsibility involves collaboration with Object, RenderSpec JSON.
- **Displays templates**: This responsibility involves collaboration with List, Template JSON.
- **Displays render instructions**: This responsibility involves collaboration with String, RenderInstructions JSON.
- **Opens template file**: This responsibility involves collaboration with CLI, Path JSON.

#### RenderInstructionsSection

**Key Responsibilities:**
- **Wraps render subsection**: This responsibility involves collaboration with RenderDataSubSection.

#### RenderOutputAction

**Key Responsibilities:**
- **Inject render output instructions**: This responsibility involves collaboration with Behavior, Content, Render Spec, Renderer.
- **Inject templates**: This responsibility involves collaboration with Behavior, Content, Render Spec, Template.
- **Inject transformers**: This responsibility involves collaboration with Behavior, Content, Transformer.
- **Load + inject structured content**: This responsibility involves collaboration with Behavior, Content, Knowledge Graph.

#### Renderer

**Key Responsibilities:**
- **Render complex output**: This responsibility involves collaboration with Template, Knowledge Graph, Transformer.
- **Render outputs using components in context**: This responsibility involves collaboration with AI Chat, Template, Content.

#### TTYRenderOutput

**Key Responsibilities:**
- **Serialize render action to TTY**: This responsibility involves collaboration with RenderOutputAction, TTY String.
- **Format render status**: This responsibility involves collaboration with Render Spec, TTY String.
- **Wraps domain action**: This responsibility involves collaboration with RenderOutputAction.

#### Template

**Key Responsibilities:**
- **Define output structure**: This responsibility involves collaboration with Placeholder.
- **Transform content**: This responsibility involves collaboration with Transformer, Content.
- **Load template**: This responsibility involves collaboration with Behavior, Content.

### Module: actions.strategy


#### JSONStrategy

**Key Responsibilities:**
- **Serialize strategy action to JSON**: This responsibility involves collaboration with StrategyAction, JSON String.
- **Include criteria and assumptions**: This responsibility involves collaboration with Criteria, Assumptions, JSON.
- **Wraps domain action**: This responsibility involves collaboration with StrategyAction.

#### MarkdownStrategy

**Key Responsibilities:**
- **Serialize strategy action to Markdown**: This responsibility involves collaboration with StrategyAction, Markdown String.
- **Format strategy documentation**: This responsibility involves collaboration with Criteria, Assumptions, Markdown.
- **Wraps domain action**: This responsibility involves collaboration with StrategyAction.

#### StrategyAction

**Key Responsibilities:**
- **Inject Strategy instructions**: This responsibility involves collaboration with Behavior, Guardrails, Strategy.
- **Inject decision criteria and assumptions**: This responsibility involves collaboration with Behavior, Guardrails, Decision Criteria, Assumptions, Recommended Human Activity.

#### StrategyDataSubSection

**Key Responsibilities:**
- **Wraps strategy JSON**: This responsibility involves collaboration with Strategy JSON.
- **Displays decision criteria**: This responsibility involves collaboration with List, DecisionCriteria JSON.
- **Displays assumptions**: This responsibility involves collaboration with String, Assumptions JSON.
- **Edits decision criterion**: This responsibility involves collaboration with CLI, DecisionCriterion JSON.
- **Edits assumption**: This responsibility involves collaboration with CLI, Assumption JSON.

#### StrategyInstructionsSection

**Key Responsibilities:**
- **Wraps strategy subsection**: This responsibility involves collaboration with StrategyDataSubSection.

#### TTYStrategy

**Key Responsibilities:**
- **Serialize strategy action to TTY**: This responsibility involves collaboration with StrategyAction, TTY String.
- **Format decision criteria**: This responsibility involves collaboration with Criteria, Assumptions, TTY String.
- **Wraps domain action**: This responsibility involves collaboration with StrategyAction.

### Module: actions.validate


#### JSONValidateRules

**Key Responsibilities:**
- **Serialize validate action to JSON**: This responsibility involves collaboration with ValidateRulesAction, JSON String.
- **Include violations and fixes**: This responsibility involves collaboration with Violations, Suggestions, JSON.
- **Wraps domain action**: This responsibility involves collaboration with ValidateRulesAction.

#### MarkdownValidateRules

**Key Responsibilities:**
- **Serialize validate action to Markdown**: This responsibility involves collaboration with ValidateRulesAction, Markdown String.
- **Format validation report**: This responsibility involves collaboration with Violations, Suggestions, Markdown.
- **Wraps domain action**: This responsibility involves collaboration with ValidateRulesAction.

#### TTYValidateRules

**Key Responsibilities:**
- **Serialize validate action to TTY**: This responsibility involves collaboration with ValidateRulesAction, TTY String.
- **Format validation results**: This responsibility involves collaboration with Violations, TTY String.
- **Wraps domain action**: This responsibility involves collaboration with ValidateRulesAction.

#### ValidateDataSubSection

**Key Responsibilities:**
- **Wraps validate JSON**: This responsibility involves collaboration with Validate JSON.
- **Displays rules**: This responsibility involves collaboration with List, Rule JSON.
- **Displays rule descriptions**: This responsibility involves collaboration with String, Rule JSON.
- **Displays rule examples**: This responsibility involves collaboration with List, Rule JSON.
- **Opens rule file**: This responsibility involves collaboration with CLI, Path JSON.

#### ValidateInstructionsSection

**Key Responsibilities:**
- **Wraps validate subsection**: This responsibility involves collaboration with ValidateDataSubSection.

#### ValidateRulesAction

**Key Responsibilities:**
- **Inject common bot rules**: This responsibility involves collaboration with Base Bot, Rules, Common Rules.
- **Inject behavior specific rules**: This responsibility involves collaboration with Behavior, Rules, Behavior Rules.
- **Load + inject content for validation**: This responsibility involves collaboration with Behavior, Content, Knowledge Graph, Rendered Outputs.

### Module: behaviors


#### ---------------------------


#### Behavior

**Key Responsibilities:**
- **Name**: This responsibility involves collaboration with String.
- **Description**: This responsibility involves collaboration with String.
- **Goal**: This responsibility involves collaboration with String.
- **Folder**: This responsibility involves collaboration with Path.
- **Is completed**: This responsibility involves collaboration with Boolean.
- **Actions workflow**: This responsibility involves collaboration with List.
- **Action Names**: This responsibility involves collaboration with List.
- **Validation type**: This responsibility involves collaboration with ValidationType.
- **CurrentAction**: This responsibility involves collaboration with Action.
- **Guardrails**: This responsibility involves collaboration with Guardrails.
- **Content**: This responsibility involves collaboration with Content.
- **Rules**: This responsibility involves collaboration with Rules.
- **Actions**: This responsibility involves collaboration with Actions.

#### BehaviorsView

**Key Responsibilities:**
- **Wraps behaviors JSON**: This responsibility involves collaboration with Behaviors JSON.
- **Displays behavior names list**: This responsibility involves collaboration with List, Behavior JSON.
- **Navigates to behavior**: This responsibility involves collaboration with CLI, Behavior.
- **Toggles collapsed**: This responsibility involves collaboration with State, Behavior JSON.
- **Displays tooltip**: This responsibility involves collaboration with String, Behavior JSON.
- **Displays actions**: This responsibility involves collaboration with ActionsView.
- **Executes behavior**: This responsibility involves collaboration with CLI, Behavior.
- **Displays completion progress**: This responsibility involves collaboration with Status, Behavior JSON.
- **Displays navigation**: This responsibility involves collaboration with NavigationView.

#### Guardrails

**Key Responsibilities:**
- **Provide required context**: This responsibility involves collaboration with Key Questions, Evidence.
- **Guide Strategy decisions**: This responsibility involves collaboration with Decision Criteria, Assumptions.
- **Define recommended human activity**: This responsibility involves collaboration with Human, Instructions.

#### JSONBehavior

**Key Responsibilities:**
- **Serialize behavior to JSON dict**: This responsibility involves collaboration with Behavior, Dict.
- **Include behavior metadata**: This responsibility involves collaboration with Name, Description, Status.
- **Include actions**: This responsibility involves collaboration with Actions, Array.
- **Wraps domain behavior**: This responsibility involves collaboration with Behavior.

#### MarkdownBehavior

**Key Responsibilities:**
- **Serialize behavior to Markdown**: This responsibility involves collaboration with Behavior, String.
- **Format behavior documentation**: This responsibility involves collaboration with Behavior Name, Description, Section.
- **Format actions**: This responsibility involves collaboration with Actions, Markdown Subsections.
- **Wraps domain behavior**: This responsibility involves collaboration with Behavior.

#### NavigationView

**Key Responsibilities:**
- **Wraps current action JSON**: This responsibility involves collaboration with Action JSON.
- **Reruns action**: This responsibility involves collaboration with CLI, Action.
- **Navigates to next action**: This responsibility involves collaboration with CLI, Action.
- **Navigates to prev action**: This responsibility involves collaboration with CLI, Action.

#### Rule

**Key Responsibilities:**
- **Validate content**: This responsibility involves collaboration with Knowledge Graph, Violations.
- **Find behavior specific rules from context**: This responsibility involves collaboration with Behavior.
- **Find common bot rules from context**: This responsibility involves collaboration with Base Bot.
- **Load + inject diagnostics results**: This responsibility involves collaboration with AI Chat, Violations, Corrections.
- **Suggest corrections**: This responsibility involves collaboration with Violations, Suggestions, Fixes.
- **Provide examples - Do**: This responsibility involves collaboration with Example, Description.
- **Provide examples - Dont**: This responsibility involves collaboration with Example, Description.
- **Specialized examples**: This responsibility involves collaboration with Language, Framework, Pattern.

#### TTYBehavior

**Key Responsibilities:**
- **Serialize behavior to TTY**: This responsibility involves collaboration with Behavior, String.
- **Format behavior line**: This responsibility involves collaboration with Behavior Name, Marker, Color.
- **Format actions**: This responsibility involves collaboration with Actions, String.
- **Wraps domain behavior**: This responsibility involves collaboration with Behavior.

### Module: bot


#### AvailableBotsView

**Key Responsibilities:**
- **Wraps bot registry JSON**: This responsibility involves collaboration with BotRegistry JSON.
- **Displays available bots**: This responsibility involves collaboration with List, BotRegistry JSON.
- **Selects bot**: This responsibility involves collaboration with CLI, Bot.

#### Base Bot

**Key Responsibilities:**
- **Executes Actions**: This responsibility involves collaboration with Workflow, Behavior, Action.
- **Execute behavior**: This responsibility involves collaboration with Behavior, BotResult.
- **Execute current action**: This responsibility involves collaboration with BotResult.
- **Navigate and execute**: This responsibility involves collaboration with Behavior, Action, ActionContext, BotResult.
- **Validate behavior exists**: This responsibility involves collaboration with Behavior, Boolean.
- **Validate action exists**: This responsibility involves collaboration with Behavior, Action, Boolean.
- **Track activity**: This responsibility involves collaboration with Behavior, Action.
- **Route to behaviors and actions**: This responsibility involves collaboration with Router, Trigger Words.
- **Persist content**: This responsibility involves collaboration with Content.
- **Manage Project State**: This responsibility involves collaboration with Project.
- **Render**: Render
- **Get scope**: This responsibility involves collaboration with Scope (read-only property).
- **Get status**: This responsibility involves collaboration with Status.
- **Navigate next**: This responsibility involves collaboration with NavigationResult.
- **Navigate back**: This responsibility involves collaboration with NavigationResult.
- **Get bot path**: This responsibility involves collaboration with BotPath.
- **Get help**: This responsibility involves collaboration with Help.
- **Exit**: This responsibility involves collaboration with ExitResult.

#### BotHeaderView

**Key Responsibilities:**
- **Wraps bot JSON**: This responsibility involves collaboration with Bot JSON.
- **Displays image**: This responsibility involves collaboration with Image.
- **Displays title**: This responsibility involves collaboration with String, Bot JSON.
- **Displays version number**: This responsibility involves collaboration with String, Bot JSON.
- **Refreshes panel**: This responsibility involves collaboration with CLI.

#### BotView

**Key Responsibilities:**
- **Wraps bot JSON**: This responsibility involves collaboration with Bot JSON.
- **Displays BotHeaderView**: This responsibility involves collaboration with BotHeaderView.
- **Displays PathsSection**: This responsibility involves collaboration with PathsSection.
- **Displays BehaviorsView**: This responsibility involves collaboration with BehaviorsView.
- **Displays ScopeSection**: This responsibility involves collaboration with ScopeSection.
- **Displays InstructionsSection**: This responsibility involves collaboration with InstructionsSection.

#### JSONBot

**Key Responsibilities:**
- **Execute behavior by name**: This responsibility involves collaboration with Behavior Name String, JSON String.
- **Execute current action**: This responsibility involves collaboration with JSON String.
- **Navigate and execute**: This responsibility involves collaboration with Dot Notation String, JSON String.
- **Validate behavior exists**: This responsibility involves collaboration with Behavior Name String, JSON String.
- **Validate action exists**: This responsibility involves collaboration with Dot Notation String, JSON String.
- **Serialize bot to JSON**: This responsibility involves collaboration with Bot, JSON String.
- **Include bot metadata**: This responsibility involves collaboration with Name, Directory, Paths.
- **Behaviors**: This responsibility involves collaboration with Bot, Behaviors, JSON Behaviors.
- **Get status**: This responsibility involves collaboration with JSON String (delegates to JSONStatus).
- **Get scope**: This responsibility involves collaboration with JSON String (delegates to JSONScope).
- **Navigate next**: This responsibility involves collaboration with JSON String (delegates to JSONNavigation).
- **Navigate back**: This responsibility involves collaboration with JSON String (delegates to JSONNavigation).
- **Get bot path**: This responsibility involves collaboration with JSON String (delegates to JSONBotPath).
- **Get help**: This responsibility involves collaboration with JSON String (delegates to JSONHelp).
- **Exit**: This responsibility involves collaboration with JSON String (delegates to JSONExitResult).
- **Wraps domain bot**: This responsibility involves collaboration with Bot.

#### MarkdownBot

**Key Responsibilities:**
- **Execute behavior by name**: This responsibility involves collaboration with Behavior Name String, Markdown String.
- **Execute current action**: This responsibility involves collaboration with Markdown String.
- **Navigate and execute**: This responsibility involves collaboration with Dot Notation String, Markdown String.
- **Validate behavior exists**: This responsibility involves collaboration with Behavior Name String, Markdown String.
- **Validate action exists**: This responsibility involves collaboration with Dot Notation String, Markdown String.
- **Serialize bot to Markdown**: This responsibility involves collaboration with Bot, Markdown String.
- **Format bot documentation**: This responsibility involves collaboration with Bot Name, Description, Markdown Header.
- **Behaviors**: This responsibility involves collaboration with Bot, Behaviors, Markdown Behaviors.
- **Get status**: This responsibility involves collaboration with Markdown String (delegates to MarkdownStatus).
- **Get scope**: This responsibility involves collaboration with Markdown String (delegates to MarkdownScope).
- **Navigate next**: This responsibility involves collaboration with Markdown String (delegates to MarkdownNavigation).
- **Navigate back**: This responsibility involves collaboration with Markdown String (delegates to MarkdownNavigation).
- **Get bot path**: This responsibility involves collaboration with Markdown String (delegates to MarkdownBotPath).
- **Get help**: This responsibility involves collaboration with Markdown String (delegates to MarkdownHelp).
- **Exit**: This responsibility involves collaboration with Markdown String (delegates to MarkdownExitResult).
- **Wraps domain bot**: This responsibility involves collaboration with Bot.

#### PathsSection

**Key Responsibilities:**
- **Wraps bot paths JSON**: This responsibility involves collaboration with BotPaths JSON.
- **Displays bot directory**: This responsibility involves collaboration with String, BotPaths JSON.
- **Edits workspace directory**: This responsibility involves collaboration with CLI, BotPaths JSON.
- **Displays available bots**: This responsibility involves collaboration with AvailableBotsView.

#### Specific Bot

**Key Responsibilities:**
- **Provide Behavior config**: This responsibility involves collaboration with Bot Config, Behavior.
- **Provide MCP config**: This responsibility involves collaboration with MCP Config.
- **Provide Renderers**: Provide Renderers
- **Provide Extractors**: Provide Extractors
- **Provide Synchronizer**: Provide Synchronizer
- **Provide Trigger Words**: Provide Trigger Words

#### TTYBot

**Key Responsibilities:**
- **Execute behavior by name**: This responsibility involves collaboration with Behavior Name String, TTY String.
- **Execute current action**: This responsibility involves collaboration with TTY String.
- **Navigate and execute**: This responsibility involves collaboration with Dot Notation String, TTY String.
- **Validate behavior exists**: This responsibility involves collaboration with Behavior Name String, TTY String (True/False).
- **Validate action exists**: This responsibility involves collaboration with Dot Notation String, TTY String (True/False).
- **Serialize entire bot to TTY**: This responsibility involves collaboration with Bot, TTY String.
- **Bot header**: This responsibility involves collaboration with Bot Name, TTY String.
- **Behaviors**: This responsibility involves collaboration with Bot, Behaviors, TTY Behaviors.
- **Get status**: This responsibility involves collaboration with TTY String (delegates to TTYStatus).
- **Get scope**: This responsibility involves collaboration with TTY String (delegates to TTYScope).
- **Navigate next**: This responsibility involves collaboration with TTY String (delegates to TTYNavigation).
- **Navigate back**: This responsibility involves collaboration with TTY String (delegates to TTYNavigation).
- **Get bot path**: This responsibility involves collaboration with TTY String (delegates to TTYBotPath).
- **Get help**: This responsibility involves collaboration with TTY String (delegates to TTYHelp).
- **Exit**: This responsibility involves collaboration with TTY String (delegates to TTYExitResult).
- **Wraps domain bot**: This responsibility involves collaboration with Bot.

### Module: bot_path


#### BotPath

**Key Responsibilities:**
- **Get bot directory**: This responsibility involves collaboration with Path.
- **Get workspace directory**: This responsibility involves collaboration with Path.
- **Get behaviors directory**: This responsibility involves collaboration with Path.
- **Get config path**: This responsibility involves collaboration with Path.
- **Get all paths**: This responsibility involves collaboration with Dict.

#### JSONBotPath

**Key Responsibilities:**
- **Serialize bot path to JSON**: This responsibility involves collaboration with BotPath, JSON String.
- **Include all paths**: This responsibility involves collaboration with Dict, JSON.
- **Wraps domain bot path**: This responsibility involves collaboration with BotPath.

#### MarkdownBotPath

**Key Responsibilities:**
- **Serialize bot path to Markdown**: This responsibility involves collaboration with BotPath, Markdown String.
- **Format paths section**: This responsibility involves collaboration with BotPath, Markdown String.
- **Wraps domain bot path**: This responsibility involves collaboration with BotPath.

#### TTYBotPath

**Key Responsibilities:**
- **Serialize bot path to TTY**: This responsibility involves collaboration with BotPath, TTY String.
- **Format path display**: This responsibility involves collaboration with Path Name, Path Value, TTY String.
- **Format all paths**: This responsibility involves collaboration with BotPath, TTY String.
- **Wraps domain bot path**: This responsibility involves collaboration with BotPath.

### Module: cli


#### CLISession

**Key Responsibilities:**
- **Runs CLI loop**: Runs CLI loop
- **Reads input from stdin or terminal**: Reads input from stdin or terminal
- **Determine channel adapter**: This responsibility involves collaboration with ChannelAdapter.
- **Read and execute command**: This responsibility involves collaboration with Command String, CLICommandResponse.
- **Parse command**: This responsibility involves collaboration with Command String, Command Verb, Params.
- **Route to bot domain methods**: This responsibility involves collaboration with Bot, Command Verb, Params, BotResult.
- **Serializes via channel adapter**: This responsibility involves collaboration with ChannelAdapter, String.
- **Displays serialized output**: This responsibility involves collaboration with Stdout.

#### ChannelAdapter (Abstract)

**Key Responsibilities:**
- **Serialize domain object to format**: This responsibility involves collaboration with Domain Object, Format.
- **Deserialize format to domain object**: This responsibility involves collaboration with Format, Domain Object.

#### JSONAdapter

**Key Responsibilities:**
- **Serialize to JSON dict**: This responsibility involves collaboration with Dict.
- **Deserialize JSON dict**: This responsibility involves collaboration with Dict, Domain Object.
- **Convert to JSON string**: This responsibility involves collaboration with Dict, String.
- **Parse JSON string**: This responsibility involves collaboration with String, Dict.
- **Validate JSON structure**: This responsibility involves collaboration with Dict, Schema.

#### JSONProgressAdapter

**Key Responsibilities:**
- **Include progress fields**: This responsibility involves collaboration with Is Completed, Is Current.
- **Include completion markers**: This responsibility involves collaboration with Progress String.

#### MarkdownAdapter

**Key Responsibilities:**
- **Serialize to Markdown**: This responsibility involves collaboration with String.
- **Deserialize Markdown**: This responsibility involves collaboration with String, Domain Object.
- **Parse markdown sections**: This responsibility involves collaboration with Markdown, Sections.
- **Format header**: This responsibility involves collaboration with Level, Text.
- **Format list item**: This responsibility involves collaboration with Marker, Text, Indent.
- **Format code block**: This responsibility involves collaboration with Language, Content.

#### MarkdownProgressAdapter

**Key Responsibilities:**
- **Render progress marker**: This responsibility involves collaboration with Is Completed, Is Current, Marker String.
- **Format progress line**: This responsibility involves collaboration with Name, Is Completed, Is Current, String.

#### TTYAdapter

**Key Responsibilities:**
- **Serialize to TTY text**: This responsibility involves collaboration with Domain Object, String.
- **Deserialize TTY text**: This responsibility involves collaboration with String, Domain Object.
- **Add color**: This responsibility involves collaboration with Text, Color.
- **Format indentation**: This responsibility involves collaboration with Indent Level, Spaces.

#### TTYProgressAdapter

**Key Responsibilities:**
- **Format line with marker**: This responsibility involves collaboration with Marker, Text, Indent.
- **Render marker**: This responsibility involves collaboration with Is Completed, Is Current.

#### TextAdapter

**Key Responsibilities:**
- **Parse command text**: This responsibility involves collaboration with Text String, Command, Params.

### Module: exit_result


#### ExitResult

**Key Responsibilities:**
- **Get exit code**: This responsibility involves collaboration with Integer.
- **Get exit message**: This responsibility involves collaboration with String.
- **Get should cleanup**: This responsibility involves collaboration with Boolean.

#### JSONExitResult

**Key Responsibilities:**
- **Serialize exit result to JSON**: This responsibility involves collaboration with ExitResult, JSON String.
- **Include exit code**: This responsibility involves collaboration with Integer, JSON.
- **Include exit message**: This responsibility involves collaboration with String, JSON.
- **Wraps domain exit result**: This responsibility involves collaboration with ExitResult.

#### MarkdownExitResult

**Key Responsibilities:**
- **Serialize exit result to Markdown**: This responsibility involves collaboration with ExitResult, Markdown String.
- **Format exit documentation**: This responsibility involves collaboration with ExitResult, Markdown String.
- **Wraps domain exit result**: This responsibility involves collaboration with ExitResult.

#### TTYExitResult

**Key Responsibilities:**
- **Serialize exit result to TTY**: This responsibility involves collaboration with ExitResult, TTY String.
- **Format exit message**: This responsibility involves collaboration with Message, TTY String.
- **Wraps domain exit result**: This responsibility involves collaboration with ExitResult.

### Module: help


#### ### status


#### JSONHelp

**Key Responsibilities:**
- **Serialize help to JSON**: This responsibility involves collaboration with Help, Dict.
- **Include help sections**: This responsibility involves collaboration with Sections, Array.
- **Wraps domain help**: This responsibility involves collaboration with Help.

#### JSONStatus

**Key Responsibilities:**
- **Serialize status to JSON**: This responsibility involves collaboration with Status, JSON String.
- **Include progress path**: This responsibility involves collaboration with Progress Path, String.
- **Include stage name**: This responsibility involves collaboration with Stage Name, String.
- **Include current behavior**: This responsibility involves collaboration with Behavior Name, String.
- **Include current action**: This responsibility involves collaboration with Action Name, String.
- **Wraps domain status**: This responsibility involves collaboration with Status.

#### MarkdownHelp

**Key Responsibilities:**
- **Serialize help to Markdown**: This responsibility involves collaboration with Help, String.
- **Format help sections**: This responsibility involves collaboration with Sections, Markdown.
- **Wraps domain help**: This responsibility involves collaboration with Help.

#### MarkdownStatus

**Key Responsibilities:**
- **Serialize status to Markdown**: This responsibility involves collaboration with Status, Markdown String.
- **Format progress section**: This responsibility involves collaboration with Progress Path, Stage Name, Markdown String.
- **Format workflow state**: This responsibility involves collaboration with Status, Markdown String.
- **Wraps domain status**: This responsibility involves collaboration with Status.

#### Status

**Key Responsibilities:**
- **Get progress path**: This responsibility involves collaboration with String.
- **Get stage name**: This responsibility involves collaboration with String.
- **Get current behavior name**: This responsibility involves collaboration with String.
- **Get current action name**: This responsibility involves collaboration with String.
- **Get has current behavior**: This responsibility involves collaboration with Boolean.
- **Get has current action**: This responsibility involves collaboration with Boolean.

#### TTYHelp

**Key Responsibilities:**
- **Serialize help to TTY**: This responsibility involves collaboration with Help, String.
- **Format help sections**: This responsibility involves collaboration with Sections, String.
- **Wraps domain help**: This responsibility involves collaboration with Help.

#### TTYStatus

**Key Responsibilities:**
- **Serialize status to TTY**: This responsibility involves collaboration with Status, TTY String.
- **Format progress line**: This responsibility involves collaboration with Progress Path, Stage Name, TTY String.
- **Format hierarchical status**: This responsibility involves collaboration with Bot, Status, TTY String.
- **Wraps domain status**: This responsibility involves collaboration with Status.

### Module: instructions


#### BaseInstructionsSubSection

**Key Responsibilities:**
- **Wraps instructions JSON**: This responsibility involves collaboration with Instructions JSON.
- **Displays behavior name**: This responsibility involves collaboration with String, Instructions JSON.
- **Displays action name**: This responsibility involves collaboration with String, Instructions JSON.
- **Displays  Instructions**: This responsibility involves collaboration with Instructions JSON.

#### InstructionsSection

**Key Responsibilities:**
- **Wraps instructions JSON**: This responsibility involves collaboration with Instructions JSON.
- **Wraps action JSON**: This responsibility involves collaboration with Action JSON.
- **Displays base instructions subsection**: This responsibility involves collaboration with BaseInstructionsSubSection.
- **Displays raw format subsection**: This responsibility involves collaboration with RawFormatSubSection.
- **Submits to AI chat**: This responsibility involves collaboration with CLI, Instructions JSON.

#### JSONInstructions

**Key Responsibilities:**
- **Serialize instructions to JSON**: This responsibility involves collaboration with Instructions, Dict.
- **Include instruction sections**: This responsibility involves collaboration with Sections, Array.
- **Wraps domain instructions**: This responsibility involves collaboration with Instructions.

#### MarkdownInstructions

**Key Responsibilities:**
- **Serialize instructions to Markdown**: This responsibility involves collaboration with Instructions, String.
- **Format instruction sections**: This responsibility involves collaboration with Sections, Markdown.
- **Wraps domain instructions**: This responsibility involves collaboration with Instructions.

#### RawFormatSubSection

**Key Responsibilities:**
- **Wraps instructions JSON**: This responsibility involves collaboration with Instructions JSON.
- **Displays raw instructions**: This responsibility involves collaboration with String, Instructions JSON.

#### TTYInstructions

**Key Responsibilities:**
- **Serialize instructions to TTY**: This responsibility involves collaboration with Instructions, String.
- **Format instruction sections**: This responsibility involves collaboration with Sections, String.
- **Wraps domain instructions**: This responsibility involves collaboration with Instructions.

### Module: navigation


#### JSONNavigation

**Key Responsibilities:**
- **Serialize navigation to JSON**: This responsibility involves collaboration with NavigationResult, JSON String.
- **Include previous action**: This responsibility involves collaboration with Action, JSON.
- **Include next action**: This responsibility involves collaboration with Action, JSON.
- **Include navigation state**: This responsibility involves collaboration with Can Back, Can Next, JSON.
- **Wraps domain navigation**: This responsibility involves collaboration with NavigationResult.

#### MarkdownNavigation

**Key Responsibilities:**
- **Serialize navigation to Markdown**: This responsibility involves collaboration with NavigationResult, Markdown String.
- **Format navigation section**: This responsibility involves collaboration with NavigationResult, Markdown String.
- **Wraps domain navigation**: This responsibility involves collaboration with NavigationResult.

#### NavigationResult

**Key Responsibilities:**
- **Get previous action**: This responsibility involves collaboration with Action.
- **Get next action**: This responsibility involves collaboration with Action.
- **Get can navigate back**: This responsibility involves collaboration with Boolean.
- **Get can navigate next**: This responsibility involves collaboration with Boolean.
- **Get navigation path**: This responsibility involves collaboration with String.

#### TTYNavigation

**Key Responsibilities:**
- **Serialize navigation to TTY**: This responsibility involves collaboration with NavigationResult, TTY String.
- **Format navigation options**: This responsibility involves collaboration with Can Back, Can Next, TTY String.
- **Format navigation path**: This responsibility involves collaboration with Path String, TTY String.
- **Wraps domain navigation**: This responsibility involves collaboration with NavigationResult.

### Module: panel


#### PanelHeader

**Key Responsibilities:**
- **Displays header image**: This responsibility involves collaboration with Image.
- **Displays title**: This responsibility involves collaboration with String.

#### PanelView (Base)

**Key Responsibilities:**
- **Wraps JSON data**: This responsibility involves collaboration with JSON.
- **Spawns subprocess**: This responsibility involves collaboration with CLI, Python Process.
- **Sends command to CLI**: This responsibility involves collaboration with Command, Stdin.
- **Receives JSON from CLI**: This responsibility involves collaboration with Stdout.
- **Parses JSON**: This responsibility involves collaboration with String, Dict.
- **Provides element ID**: This responsibility involves collaboration with String.
- **Renders to HTML**: This responsibility involves collaboration with HTML, JSON.

#### SectionView

**Key Responsibilities:**
- **Renders section header**: This responsibility involves collaboration with PanelHeader.
- **Toggles collapsed state**: This responsibility involves collaboration with State.
- **May contain subsections**: This responsibility involves collaboration with SubSectionView.

#### SubSectionView

**Key Responsibilities:**
- **Toggles collapsed state**: This responsibility involves collaboration with State.

### Module: scope


#### JSONScope

**Key Responsibilities:**
- **Serialize scope to JSON**: This responsibility involves collaboration with Scope, JSON String.
- **Include filter**: This responsibility involves collaboration with Filter String, String.
- **Include results**: This responsibility involves collaboration with Results List, Array.
- **Include filter metadata**: This responsibility involves collaboration with Is Active, Count, JSON.
- **Wraps domain scope**: This responsibility involves collaboration with Scope.

#### MarkdownScope

**Key Responsibilities:**
- **Serialize scope to Markdown**: This responsibility involves collaboration with Scope, Markdown String.
- **Format filter section**: This responsibility involves collaboration with Filter String, Markdown String.
- **Format results list**: This responsibility involves collaboration with Results, Markdown List.
- **Format filter documentation**: This responsibility involves collaboration with Scope, Markdown String.
- **Wraps domain scope**: This responsibility involves collaboration with Scope.

#### Scope

**Key Responsibilities:**
- **Get filter**: This responsibility involves collaboration with String (read/write property).
- **Set filter**: This responsibility involves collaboration with String.
- **Get results**: This responsibility involves collaboration with List (read-only property).
- **Apply filter to behaviors**: This responsibility involves collaboration with Behaviors, Filtered Behaviors.
- **Apply filter to stories**: This responsibility involves collaboration with Stories, Filtered Stories.
- **Clear filter**: Clear filter
- **Get filter count**: This responsibility involves collaboration with Integer.
- **Get is active**: This responsibility involves collaboration with Boolean.

#### ScopeView

**Key Responsibilities:**
- **Wraps scope JSON**: This responsibility involves collaboration with Scope JSON.
- **Displays current filter**: This responsibility involves collaboration with String, Scope JSON.
- **Edits filter**: This responsibility involves collaboration with CLI, Scope JSON.
- **Displays filtered results**: This responsibility involves collaboration with List, Scope JSON.
- **Clears filter**: This responsibility involves collaboration with CLI, Scope JSON.
- **Displays filter status**: This responsibility involves collaboration with Is Active, Count, Scope JSON.

#### TTYScope

**Key Responsibilities:**
- **Serialize scope to TTY**: This responsibility involves collaboration with Scope, TTY String.
- **Format filter display**: This responsibility involves collaboration with Filter String, TTY String.
- **Format results list**: This responsibility involves collaboration with Results, TTY String.
- **Format filter status**: This responsibility involves collaboration with Is Active, Count, TTY String.
- **Wraps domain scope**: This responsibility involves collaboration with Scope.

### Module: story_graph.acceptance_criteria


#### AcceptanceCriteria

**Key Responsibilities:**
- **Get steps**: This responsibility involves collaboration with List[Step].

#### AcceptanceCriteriaView

**Key Responsibilities:**
- **Wraps acceptance criteria JSON**: This responsibility involves collaboration with AcceptanceCriteria JSON.
- **Displays criteria name**: This responsibility involves collaboration with String, AcceptanceCriteria JSON.
- **Displays criteria icon**: This responsibility involves collaboration with Image.
- **Displays steps as checklist**: This responsibility involves collaboration with List[Step], HTML.

#### JSONAcceptanceCriteria

**Key Responsibilities:**
- **Include steps**: This responsibility involves collaboration with List[Step], JSON Array.
- **Wraps domain acceptance criteria**: This responsibility involves collaboration with AcceptanceCriteria.

#### MarkdownAcceptanceCriteria

**Key Responsibilities:**
- **Format criteria as checklist**: This responsibility involves collaboration with List[Step], Markdown.
- **Format steps list**: This responsibility involves collaboration with List[Step], Markdown.
- **Wraps domain acceptance criteria**: This responsibility involves collaboration with AcceptanceCriteria.

#### TTYAcceptanceCriteria

**Key Responsibilities:**
- **Format steps**: This responsibility involves collaboration with List[Step], TTY String.
- **Format criteria list**: This responsibility involves collaboration with List[Step], TTY String.
- **Wraps domain acceptance criteria**: This responsibility involves collaboration with AcceptanceCriteria.

### Module: story_graph.domain


#### Collaborator

**Key Responsibilities:**
- **Get name**: This responsibility involves collaboration with String.
- **From string**: This responsibility involves collaboration with String, Collaborator.
- **To string**: This responsibility involves collaboration with String.

#### DomainConcept

**Key Responsibilities:**
- **Get name**: This responsibility involves collaboration with String.
- **Get responsibilities**: This responsibility involves collaboration with List[Responsibility].
- **From dict**: This responsibility involves collaboration with Dict, DomainConcept.
- **To dict**: This responsibility involves collaboration with Dict.

#### DomainModule

**Key Responsibilities:**
- **Contains domain objects**: This responsibility involves collaboration with List[DomainConcept].
- **Get submodules**: This responsibility involves collaboration with List[Module].
- **Get parent module**: This responsibility involves collaboration with Module.

#### JSONDomainConcept

**Key Responsibilities:**
- **Serialize domain concept to JSON**: This responsibility involves collaboration with DomainConcept, JSON String.
- **Include responsibilities**: This responsibility involves collaboration with List[Responsibility], JSON Array.
- **Wraps domain concept**: This responsibility involves collaboration with DomainConcept.

#### MarkdownDomainConcept

**Key Responsibilities:**
- **Serialize domain concept to Markdown**: This responsibility involves collaboration with DomainConcept, Markdown String.
- **Format CRC table**: This responsibility involves collaboration with DomainConcept, Markdown.
- **Format responsibilities section**: This responsibility involves collaboration with List[Responsibility], Markdown.
- **Wraps domain concept**: This responsibility involves collaboration with DomainConcept.

#### Responsibility

**Key Responsibilities:**
- **Get name**: This responsibility involves collaboration with String.
- **Get collaborators**: This responsibility involves collaboration with List[Collaborator].
- **From dict**: This responsibility involves collaboration with Dict, Responsibility.
- **To dict**: This responsibility involves collaboration with Dict.

#### TTYDomainConcept

**Key Responsibilities:**
- **Serialize domain concept to TTY**: This responsibility involves collaboration with DomainConcept, TTY String.
- **Format responsibilities**: This responsibility involves collaboration with List[Responsibility], TTY String.
- **Format CRC card**: This responsibility involves collaboration with DomainConcept, TTY String.
- **Wraps domain concept**: This responsibility involves collaboration with DomainConcept.

### Module: story_graph.epic


#### Epic

**Key Responsibilities:**
- **Test file property**: This responsibility involves collaboration with String.
- **Get all stories**: This responsibility involves collaboration with List[Story].
- **Get domain concepts**: This responsibility involves collaboration with List[DomainConcept].

#### EpicView

**Key Responsibilities:**
- **Wraps epic JSON**: This responsibility involves collaboration with Epic JSON.
- **Displays epic name**: This responsibility involves collaboration with String, Epic JSON.
- **Displays epic icon**: This responsibility involves collaboration with Image.
- **Displays sub epics**: This responsibility involves collaboration with SubEpicView, SubEpic JSON.
- **Opens epic folder**: This responsibility involves collaboration with CLI, Epic JSON.
- **Opens epic test file**: This responsibility involves collaboration with CLI, Epic JSON.

#### JSONEpic

**Key Responsibilities:**
- **Include domain concepts**: This responsibility involves collaboration with List[DomainConcept], JSON Array.
- **Wraps domain epic**: This responsibility involves collaboration with Epic.

#### MarkdownEpic

**Key Responsibilities:**
- **Format domain concepts table**: This responsibility involves collaboration with List[DomainConcept], Markdown.
- **Wraps domain epic**: This responsibility involves collaboration with Epic.

#### TTYEpic

**Key Responsibilities:**
- **Format domain concepts**: This responsibility involves collaboration with List[DomainConcept], TTY String.
- **Wraps domain epic**: This responsibility involves collaboration with Epic.

### Module: story_graph.nodes


#### JSONStoryNode

**Key Responsibilities:**
- **Serialize node to JSON**: This responsibility involves collaboration with StoryNode, JSON String.
- **Include name**: This responsibility involves collaboration with String, JSON.
- **Include sequential order**: This responsibility involves collaboration with Float, JSON.
- **Include children**: This responsibility involves collaboration with List[StoryNode], JSON Array.
- **Add child**: This responsibility involves collaboration with StoryNode, JSON Result.
- **Add child at position**: This responsibility involves collaboration with StoryNode, Position, JSON Result.
- **Delete child**: This responsibility involves collaboration with StoryNode, JSON Result.
- **Delete this node**: This responsibility involves collaboration with JSON Result.
- **Delete with children**: This responsibility involves collaboration with JSON Result.
- **Update name**: This responsibility involves collaboration with String, JSON Result.
- **Move to parent**: This responsibility involves collaboration with New Parent, Position, JSON Result.
- **Move after target**: This responsibility involves collaboration with Target StoryNode, JSON Result.
- **Move before target**: This responsibility involves collaboration with Target StoryNode, JSON Result.
- **Reorder children**: This responsibility involves collaboration with Start Pos, End Pos, JSON Result.
- **Automatically refresh story graph**: This responsibility involves collaboration with JSON Result.
- **Wraps domain story node**: This responsibility involves collaboration with StoryNode.

#### MarkdownStoryNode

**Key Responsibilities:**
- **Serialize node to Markdown**: This responsibility involves collaboration with StoryNode, Markdown String.
- **Format node header**: This responsibility involves collaboration with String, Sequential Order, Markdown.
- **Format children list**: This responsibility involves collaboration with List[StoryNode], Markdown.
- **Wraps domain story node**: This responsibility involves collaboration with StoryNode.

#### StoryNode (Base)

**Key Responsibilities:**
- **Serializes**: This responsibility involves collaboration with StoryNodeSerializer.
- **Get/Update name**: This responsibility involves collaboration with String.
- **Get node type**: This responsibility involves collaboration with String.
- **Get node ID**: This responsibility involves collaboration with String, StoryNode, StoryNodeNavigator.
- **Get parent**: This responsibility involves collaboration with StoryNode.
- **Get sequential order**: This responsibility involves collaboration with StoryNodeNavigator, Float.
- **Contains Children**: This responsibility involves collaboration with StoryNodeChildren.
- **Delete self**: This responsibility involves collaboration with StoryNodeSerializer.
- **Delete with children**: This responsibility involves collaboration with StoryNodeSerializer, StoryNodeChildren.
- **Get/Update test**: This responsibility involves collaboration with Test.

#### StoryNodeChildren

**Key Responsibilities:**
- **Get children**: This responsibility involves collaboration with List[StoryNode].
- **Find child by name**: This responsibility involves collaboration with String, StoryNode.
- **Delete child**: This responsibility involves collaboration with StoryNode.

#### StoryNodeNavigator

**Key Responsibilities:**
- **Build node ID from hierarchy path**: This responsibility involves collaboration with String, StoryNode.
- **Get parent**: This responsibility involves collaboration with StoryNode.
- **Move to parent**: This responsibility involves collaboration with New Parent, Position.
- **Move after**: This responsibility involves collaboration with StoryNode, sequential order.
- **Move before**: This responsibility involves collaboration with StoryNode, sequential order.
- **DetermineOrder**: This responsibility involves collaboration with FLoat, StoryNode.

#### StoryNodeSerializer

**Key Responsibilities:**
- **File**: This responsibility involves collaboration with File.
- **Create Node**: This responsibility involves collaboration with File, StoryNode.
- **Load Node**: This responsibility involves collaboration with File, StoryNode.
- **Update Node**: This responsibility involves collaboration with File, StoryNode.
- **Delete Node**: This responsibility involves collaboration with File, StoryNode.
- **From JSON**: This responsibility involves collaboration with JSON, StoryNode.
- **To JSON**: This responsibility involves collaboration with JSON, StoryNode.

#### StoryNodeView

**Key Responsibilities:**
- **Wraps story node JSON**: This responsibility involves collaboration with StoryNode JSON.
- **Toggles collapsed**: This responsibility involves collaboration with State.
- **Add child node**: This responsibility involves collaboration with StoryNode, Panel Result.
- **Add child at position**: This responsibility involves collaboration with StoryNode, Position, Panel Result.
- **Delete this node**: This responsibility involves collaboration with Panel Result.
- **Delete with children**: This responsibility involves collaboration with Panel Result.
- **Update node name**: This responsibility involves collaboration with String, Panel Result.
- **Move to parent**: This responsibility involves collaboration with New Parent, Position, Panel Result.
- **Move after target**: This responsibility involves collaboration with Target StoryNode, Panel Result.
- **Move before target**: This responsibility involves collaboration with Target StoryNode, Panel Result.
- **Drag and drop**: This responsibility involves collaboration with Drop Target, Position, Panel Result.
- **Reorder children**: This responsibility involves collaboration with Start Pos, End Pos, Panel Result.
- **Automatically refresh story graph**: This responsibility involves collaboration with Panel Result.

#### TTYStoryNode

**Key Responsibilities:**
- **Serialize node to TTY**: This responsibility involves collaboration with StoryNode, TTY String.
- **Format name**: This responsibility involves collaboration with String, TTY String.
- **Format sequential order**: This responsibility involves collaboration with Float, TTY String.
- **Format children**: This responsibility involves collaboration with List[StoryNode], TTY String.
- **Add child**: This responsibility involves collaboration with StoryNode, CLI Result.
- **Add child at position**: This responsibility involves collaboration with StoryNode, Position, CLI Result.
- **Delete child**: This responsibility involves collaboration with StoryNode, CLI Result.
- **Delete this node**: This responsibility involves collaboration with CLI Result.
- **Delete with children**: This responsibility involves collaboration with CLI Result.
- **Update name**: This responsibility involves collaboration with String, CLI Result.
- **Move to parent**: This responsibility involves collaboration with New Parent, Position, CLI Result.
- **Move after target**: This responsibility involves collaboration with Target StoryNode, CLI Result.
- **Move before target**: This responsibility involves collaboration with Target StoryNode, CLI Result.
- **Reorder children**: This responsibility involves collaboration with Start Pos, End Pos, CLI Result.
- **Automatically refresh story graph**: This responsibility involves collaboration with CLI Result.
- **Wraps domain story node**: This responsibility involves collaboration with StoryNode.

### Module: story_graph.scenario


#### JSONScenario

**Key Responsibilities:**
- **Include steps**: This responsibility involves collaboration with List[Step], JSON Array.
- **Include test method**: This responsibility involves collaboration with Test Method, JSON.
- **Wraps domain scenario**: This responsibility involves collaboration with Scenario.

#### MarkdownScenario

**Key Responsibilities:**
- **Format Gherkin scenario**: This responsibility involves collaboration with Scenario, Markdown.
- **Format steps as Given/When/Then**: This responsibility involves collaboration with List[Step], Markdown.
- **Wraps domain scenario**: This responsibility involves collaboration with Scenario.

#### Scenario

**Key Responsibilities:**
- **Test method property**: This responsibility involves collaboration with String.
- **Get test method**: This responsibility involves collaboration with String.
- **Get default test method**: This responsibility involves collaboration with String.
- **Get steps**: This responsibility involves collaboration with List[Step].

#### ScenarioView

**Key Responsibilities:**
- **Wraps scenario JSON**: This responsibility involves collaboration with Scenario JSON.
- **Displays scenario name**: This responsibility involves collaboration with String, Scenario JSON.
- **Displays scenario icon**: This responsibility involves collaboration with Image.
- **Opens test at scenario**: This responsibility involves collaboration with CLI, Scenario JSON.

#### TTYScenario

**Key Responsibilities:**
- **Format steps**: This responsibility involves collaboration with List[Step], TTY String.
- **Format test method**: This responsibility involves collaboration with Test Method, TTY String.
- **Wraps domain scenario**: This responsibility involves collaboration with Scenario.

### Module: story_graph.scenario_outline


#### JSONScenarioOutline

**Key Responsibilities:**
- **Include steps**: This responsibility involves collaboration with List[Step], JSON Array.
- **Include examples**: This responsibility involves collaboration with List[Dict], JSON Array.
- **Include test method**: This responsibility involves collaboration with Test Method, JSON.
- **Wraps domain scenario outline**: This responsibility involves collaboration with ScenarioOutline.

#### MarkdownScenarioOutline

**Key Responsibilities:**
- **Format Gherkin scenario outline**: This responsibility involves collaboration with ScenarioOutline, Markdown.
- **Format steps as Given/When/Then**: This responsibility involves collaboration with List[Step], Markdown.
- **Format examples table**: This responsibility involves collaboration with List[Dict], Markdown.
- **Wraps domain scenario outline**: This responsibility involves collaboration with ScenarioOutline.

#### ScenarioOutline

**Key Responsibilities:**
- **Test method property**: This responsibility involves collaboration with String.
- **Get test method**: This responsibility involves collaboration with String.
- **Get default test method**: This responsibility involves collaboration with String.
- **Get examples**: This responsibility involves collaboration with List[Dict].
- **Get steps**: This responsibility involves collaboration with List[Step].

#### ScenarioOutlineView

**Key Responsibilities:**
- **Wraps scenario outline JSON**: This responsibility involves collaboration with ScenarioOutline JSON.
- **Displays scenario outline name**: This responsibility involves collaboration with String, ScenarioOutline JSON.
- **Displays scenario outline icon**: This responsibility involves collaboration with Image.
- **Displays examples table**: This responsibility involves collaboration with List[Dict], Table HTML.
- **Opens test at scenario outline**: This responsibility involves collaboration with CLI, ScenarioOutline JSON.

#### TTYScenarioOutline

**Key Responsibilities:**
- **Format steps**: This responsibility involves collaboration with List[Step], TTY String.
- **Format examples**: This responsibility involves collaboration with List[Dict], TTY String.
- **Format test method**: This responsibility involves collaboration with Test Method, TTY String.
- **Wraps domain scenario outline**: This responsibility involves collaboration with ScenarioOutline.

### Module: story_graph.step


#### JSONStep

**Key Responsibilities:**
- **Include step text**: This responsibility involves collaboration with String, JSON.
- **Wraps domain step**: This responsibility involves collaboration with Step.

#### MarkdownStep

**Key Responsibilities:**
- **Format step as Gherkin**: This responsibility involves collaboration with Step, Markdown.
- **Wraps domain step**: This responsibility involves collaboration with Step.

#### Step

**Key Responsibilities:**
- **Get text**: This responsibility involves collaboration with String.

#### StepView

**Key Responsibilities:**
- **Wraps step JSON**: This responsibility involves collaboration with Step JSON.
- **Displays step text**: This responsibility involves collaboration with String, Step JSON.
- **Displays step icon**: This responsibility involves collaboration with Image.

#### TTYStep

**Key Responsibilities:**
- **Format step text**: This responsibility involves collaboration with String, TTY String.
- **Format step keyword**: This responsibility involves collaboration with String, TTY String.
- **Wraps domain step**: This responsibility involves collaboration with Step.

### Module: story_graph.story


#### JSONStory

**Key Responsibilities:**
- **Include users**: This responsibility involves collaboration with List[StoryUser], JSON Array.
- **Include test metadata**: This responsibility involves collaboration with Test File, Test Class, JSON.
- **Wraps domain story**: This responsibility involves collaboration with Story.

#### MarkdownStory

**Key Responsibilities:**
- **Format story card**: This responsibility involves collaboration with Story, Markdown.
- **Format users section**: This responsibility involves collaboration with List[StoryUser], Markdown.
- **Wraps domain story**: This responsibility involves collaboration with Story.

#### Story

**Key Responsibilities:**
- **Test class property**: This responsibility involves collaboration with String.
- **Get test class**: This responsibility involves collaboration with String.
- **Get default test class**: This responsibility involves collaboration with String.
- **Get story type**: This responsibility involves collaboration with String.
- **Get users**: This responsibility involves collaboration with List[StoryUser].
- **Get scenarios**: This responsibility involves collaboration with List[Scenario].
- **Get scenario outlines**: This responsibility involves collaboration with List[ScenarioOutline].
- **Get acceptance criteria**: This responsibility involves collaboration with List[AcceptanceCriteria].

#### StoryView

**Key Responsibilities:**
- **Wraps story JSON**: This responsibility involves collaboration with Story JSON.
- **Displays story name**: This responsibility involves collaboration with String, Story JSON.
- **Displays story icon**: This responsibility involves collaboration with Image.
- **Displays scenarios**: This responsibility involves collaboration with ScenarioView, Scenario JSON.
- **Opens test at class**: This responsibility involves collaboration with CLI, Story JSON.

#### TTYStory

**Key Responsibilities:**
- **Format users**: This responsibility involves collaboration with List[StoryUser], TTY String.
- **Format test metadata**: This responsibility involves collaboration with Test File, Test Class, TTY String.
- **Wraps domain story**: This responsibility involves collaboration with Story.

### Module: story_graph.story_group


#### StoryGroup


### Module: story_graph.story_map


#### JSONStoryMap

**Key Responsibilities:**
- **Serialize story map to JSON**: This responsibility involves collaboration with StoryMap, JSON String.
- **Include story graph**: This responsibility involves collaboration with Dict, JSON.
- **Include all epics**: This responsibility involves collaboration with List[Epic], JSON Array.
- **Wraps domain story map**: This responsibility involves collaboration with StoryMap.

#### MarkdownStoryMap

**Key Responsibilities:**
- **Serialize story map to Markdown**: This responsibility involves collaboration with StoryMap, Markdown String.
- **Format epic hierarchy**: This responsibility involves collaboration with List[Epic], Markdown.
- **Format story index**: This responsibility involves collaboration with List[Story], Markdown.
- **Wraps domain story map**: This responsibility involves collaboration with StoryMap.

#### StoryMap

**Key Responsibilities:**
- **Load from bot directory**: This responsibility involves collaboration with Bot, StoryMap.
- **Load from story graph**: This responsibility involves collaboration with File Path, StoryMap.
- **Walk nodes**: This responsibility involves collaboration with StoryNode, Iterator[StoryNode].
- **Get all stories**: This responsibility involves collaboration with List[Story].
- **Get all scenarios**: This responsibility involves collaboration with List[Scenario].
- **Get all domain concepts**: This responsibility involves collaboration with List[DomainConcept].
- **Find by name**: This responsibility involves collaboration with Name, StoryNode.
- **Find node by path**: This responsibility involves collaboration with Path String, StoryNode.
- **Get story graph dict**: This responsibility involves collaboration with Dict.
- **Get epics**: This responsibility involves collaboration with List[Epic].
- **Save to story graph**: This responsibility involves collaboration with File Path.
- **Reload from story graph**: This responsibility involves collaboration with File Path, StoryMap.
- **Validate graph structure**: This responsibility involves collaboration with Validation Result.

#### StoryMapView

**Key Responsibilities:**
- **Wraps story map JSON**: This responsibility involves collaboration with StoryMap JSON.
- **Displays epic hierarchy**: This responsibility involves collaboration with EpicView, Epic JSON.
- **Searches stories**: This responsibility involves collaboration with Filter, StoryGraph JSON.
- **Opens story graph file**: This responsibility involves collaboration with CLI, File JSON.
- **Opens story map file**: This responsibility involves collaboration with CLI, File JSON.

#### TTYStoryMap

**Key Responsibilities:**
- **Serialize story map to TTY**: This responsibility involves collaboration with StoryMap, TTY String.
- **Format epics list**: This responsibility involves collaboration with List[Epic], TTY String.
- **Format story hierarchy**: This responsibility involves collaboration with StoryMap, TTY String.
- **Walk and format nodes**: This responsibility involves collaboration with StoryNode, TTY String.
- **Wraps domain story map**: This responsibility involves collaboration with StoryMap.

### Module: story_graph.story_user


#### JSONStoryUser

**Key Responsibilities:**
- **Serialize user to JSON**: This responsibility involves collaboration with StoryUser, JSON String.
- **Include user name**: This responsibility involves collaboration with String, JSON.
- **Include user list**: This responsibility involves collaboration with List[StoryUser], JSON Array.
- **Wraps domain story user**: This responsibility involves collaboration with StoryUser.

#### MarkdownStoryUser

**Key Responsibilities:**
- **Serialize user to Markdown**: This responsibility involves collaboration with StoryUser, Markdown String.
- **Format user badge**: This responsibility involves collaboration with StoryUser, Markdown.
- **Format user list**: This responsibility involves collaboration with List[StoryUser], Markdown.
- **Wraps domain story user**: This responsibility involves collaboration with StoryUser.

#### StoryUser

**Key Responsibilities:**
- **Get name**: This responsibility involves collaboration with String.
- **From string**: This responsibility involves collaboration with String, StoryUser.
- **From list**: This responsibility involves collaboration with List[String], List[StoryUser].
- **To string**: This responsibility involves collaboration with String.

#### StoryUserView

**Key Responsibilities:**
- **Wraps story user JSON**: This responsibility involves collaboration with StoryUser JSON.
- **Displays user name**: This responsibility involves collaboration with String, StoryUser JSON.
- **Displays user icon**: This responsibility involves collaboration with Image.
- **Filters stories by user**: This responsibility involves collaboration with StoryUser, Panel Result.

#### TTYStoryUser

**Key Responsibilities:**
- **Serialize user to TTY**: This responsibility involves collaboration with StoryUser, TTY String.
- **Format user name**: This responsibility involves collaboration with String, TTY String.
- **Format user list**: This responsibility involves collaboration with List[StoryUser], TTY String.
- **Wraps domain story user**: This responsibility involves collaboration with StoryUser.

### Module: story_graph.sub_epic


#### SubEpic

**Key Responsibilities:**
- **Test file property**: This responsibility involves collaboration with String.

#### SubEpicView

**Key Responsibilities:**
- **Wraps sub epic JSON**: This responsibility involves collaboration with SubEpic JSON.
- **Displays sub epic name**: This responsibility involves collaboration with String, SubEpic JSON.
- **Displays sub epic icon**: This responsibility involves collaboration with Image.
- **Displays nested sub epics**: This responsibility involves collaboration with SubEpicView, SubEpic JSON.
- **Displays stories**: This responsibility involves collaboration with StoryView, Story JSON.
- **Opens sub epic folder**: This responsibility involves collaboration with CLI, SubEpic JSON.
- **Opens sub epic test file**: This responsibility involves collaboration with CLI, SubEpic JSON.

### Module: story_graph.test


#### JSONTest

**Key Responsibilities:**
- **Serialize test to JSON**: This responsibility involves collaboration with Test, JSON String.
- **Include test file**: This responsibility involves collaboration with String, JSON.
- **Include test class**: This responsibility involves collaboration with String, JSON.
- **Include test method**: This responsibility involves collaboration with String, JSON.
- **Wraps domain test**: This responsibility involves collaboration with Test.

#### MarkdownTest

**Key Responsibilities:**
- **Serialize test to Markdown**: This responsibility involves collaboration with Test, Markdown String.
- **Format test link**: This responsibility involves collaboration with Test File, Test Class, Test Method, Markdown.
- **Wraps domain test**: This responsibility involves collaboration with Test.

#### TTYTest

**Key Responsibilities:**
- **Serialize test to TTY**: This responsibility involves collaboration with Test, TTY String.
- **Format test file**: This responsibility involves collaboration with String, TTY String.
- **Format test class**: This responsibility involves collaboration with String, TTY String.
- **Format test method**: This responsibility involves collaboration with String, TTY String.
- **Wraps domain test**: This responsibility involves collaboration with Test.

#### Test

**Key Responsibilities:**
- **Get test file**: This responsibility involves collaboration with String.
- **Get test class**: This responsibility involves collaboration with String.
- **Get test method**: This responsibility involves collaboration with String.
- **Get default test class**: This responsibility involves collaboration with String.
- **Get default test method**: This responsibility involves collaboration with String.
- **Build from story node**: This responsibility involves collaboration with StoryNode, TestMetadata.

#### TestView

**Key Responsibilities:**
- **Wraps test JSON**: This responsibility involves collaboration with Test JSON.
- **Displays test file**: This responsibility involves collaboration with String, Test JSON.
- **Displays test class**: This responsibility involves collaboration with String, Test JSON.
- **Displays test method**: This responsibility involves collaboration with String, Test JSON.
- **Opens test file**: This responsibility involves collaboration with CLI, Test JSON.
- **Opens test at class**: This responsibility involves collaboration with CLI, Test JSON.
- **Opens test at method**: This responsibility involves collaboration with CLI, Test JSON.

---

## Source Material

**Primary Source:** `input.txt`
**Date Generated:** 2025-01-27
**Context:** Shape phase - Domain model extracted from story-graph.json
