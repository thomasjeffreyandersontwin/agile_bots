## Module: actions

ActionDataSubSection
    Wraps action JSON: Action JSON
    Displays action properties: Object,Action JSON

ActionStateManager
    Get state file path: Path
    Load or create state: State File,Dict
    Save state: Action,State File
    Load state: Actions List,Current Index
    Find action index: Actions List,Action Name,Integer
    Filter completed actions: Completed Actions,Target Index,Actions List,List

ActionsView
    Wraps actions JSON: Actions JSON
    Displays action names list: List,Action JSON
    Navigates to action: CLI,Action
    Displays status indicators: Status,Action JSON
    Executes action: CLI,Action
    Displays completion progress: Progress,Action JSON

Base Action
    Inject Instructions: Behavior
    Load Relevant Content + Inject Into Instructions: Content
    Save content changes: Content

JSONAction
    Serialize action to JSON dict: Action,Dict
    Include action metadata: Name,Description,Status
    Wraps domain action: Action

MarkdownAction
    Serialize action to Markdown: Action,String
    Format action documentation: Action Name,Description,Subsection
    Wraps domain action: Action

TTYAction
    Serialize action to TTY: Action,String
    Format action line: Action Name,Marker,Indent
    Wraps domain action: Action


## Module: actions.build

BuildDataSubSection
    Wraps build JSON: Build JSON
    Displays knowledge graph spec: Object,KnowledgeGraphSpec JSON
    Displays graph structure: Object,KnowledgeGraphSpec JSON
    Displays builder instructions: String,BuilderInstructions JSON
    Opens graph file: CLI,Path JSON

BuildInstructionsSection
    Wraps build subsection: BuildDataSubSection

BuildKnowledgeAction
    Inject knowledge graph template: Behavior,Content,Knowledge Graph Spec,Knowledge Graph
    Inject builder instructions: Behavior,Content,Build Instructions
    Save Knowledge graph: Behavior,Content,Knowledge Graph

JSONBuildKnowledge
    Serialize build action to JSON: BuildKnowledgeAction,JSON String
    Include build metadata: Knowledge Graph Spec,JSON
    Wraps domain action: BuildKnowledgeAction

MarkdownBuildKnowledge
    Serialize build action to Markdown: BuildKnowledgeAction,Markdown String
    Format build documentation: Knowledge Graph Spec,Markdown
    Wraps domain action: BuildKnowledgeAction

TTYBuildKnowledge
    Serialize build action to TTY: BuildKnowledgeAction,String
    Format build status: Status,TTY String
    Wraps domain action: BuildKnowledgeAction


## Module: actions.clarify

ClarifyDataSubSection
    Wraps key questions JSON: KeyQuestions JSON
    Displays key questions: List,KeyQuestion JSON
    Updates evidence: CLI,Evidence JSON
    Edits answer: CLI,KeyQuestion JSON

ClarifyInstructionsSection
    Wraps clarify subsection: ClarifyDataSubSection

GatherContextAction
    Inject gather context instructions: Behavior,Guardrails,Required Clarifications
    Inject questions and evidence: Behavior,Guardrails,Key Questions,Evidence

JSONGatherContext
    Serialize clarify action to JSON: GatherContextAction,JSON String
    Include questions and evidence: Questions,Evidence,JSON
    Wraps domain action: GatherContextAction

MarkdownGatherContext
    Serialize clarify action to Markdown: GatherContextAction,Markdown String
    Format questions list: Questions,Evidence,Markdown
    Wraps domain action: GatherContextAction

TTYGatherContext
    Serialize clarify action to TTY: GatherContextAction,TTY String
    Format key questions: Questions,Evidence,TTY String
    Wraps domain action: GatherContextAction


## Module: actions.render

Content
    Render outputs: Template,Renderer,Render Spec
    Synchronize formats: Synchronizer,Extractor,Synchronizer Spec
    Save knowledge graph: Knowledge Graph
    Load rendered content: na
    Present rendered content: na

JSONRenderOutput
    Serialize render action to JSON: RenderOutputAction,JSON String
    Include render spec: Render Spec,Templates,JSON
    Wraps domain action: RenderOutputAction

MarkdownRenderOutput
    Serialize render action to Markdown: RenderOutputAction,Markdown String
    Format render documentation: Render Spec,Templates,Markdown
    Wraps domain action: RenderOutputAction

RenderDataSubSection
    Wraps render JSON: Render JSON
    Displays render spec: Object,RenderSpec JSON
    Displays templates: List,Template JSON
    Displays render instructions: String,RenderInstructions JSON
    Opens template file: CLI,Path JSON

RenderInstructionsSection
    Wraps render subsection: RenderDataSubSection

RenderOutputAction
    Inject render output instructions: Behavior,Content,Render Spec,Renderer
    Inject templates: Behavior,Content,Render Spec,Template
    Inject transformers: Behavior,Content,Transformer
    Load + inject structured content: Behavior,Content,Knowledge Graph

Renderer
    Render complex output: Template,Knowledge Graph,Transformer
    Render outputs using components in context: AI Chat,Template,Content

TTYRenderOutput
    Serialize render action to TTY: RenderOutputAction,TTY String
    Format render status: Render Spec,TTY String
    Wraps domain action: RenderOutputAction

Template
    Define output structure: Placeholder
    Transform content: Transformer,Content
    Load template: Behavior,Content


## Module: actions.strategy

JSONStrategy
    Serialize strategy action to JSON: StrategyAction,JSON String
    Include criteria and assumptions: Criteria,Assumptions,JSON
    Wraps domain action: StrategyAction

MarkdownStrategy
    Serialize strategy action to Markdown: StrategyAction,Markdown String
    Format strategy documentation: Criteria,Assumptions,Markdown
    Wraps domain action: StrategyAction

StrategyAction
    Inject Strategy instructions: Behavior,Guardrails,Strategy
    Inject decision criteria and assumptions: Behavior,Guardrails,Decision Criteria,Assumptions,Recommended Human Activity

StrategyDataSubSection
    Wraps strategy JSON: Strategy JSON
    Displays decision criteria: List,DecisionCriteria JSON
    Displays assumptions: String,Assumptions JSON
    Edits decision criterion: CLI,DecisionCriterion JSON
    Edits assumption: CLI,Assumption JSON

StrategyInstructionsSection
    Wraps strategy subsection: StrategyDataSubSection

TTYStrategy
    Serialize strategy action to TTY: StrategyAction,TTY String
    Format decision criteria: Criteria,Assumptions,TTY String
    Wraps domain action: StrategyAction


## Module: actions.validate

JSONValidateRules
    Serialize validate action to JSON: ValidateRulesAction,JSON String
    Include violations and fixes: Violations,Suggestions,JSON
    Wraps domain action: ValidateRulesAction

MarkdownValidateRules
    Serialize validate action to Markdown: ValidateRulesAction,Markdown String
    Format validation report: Violations,Suggestions,Markdown
    Wraps domain action: ValidateRulesAction

TTYValidateRules
    Serialize validate action to TTY: ValidateRulesAction,TTY String
    Format validation results: Violations,TTY String
    Wraps domain action: ValidateRulesAction

ValidateDataSubSection
    Wraps validate JSON: Validate JSON
    Displays rules: List,Rule JSON
    Displays rule descriptions: String,Rule JSON
    Displays rule examples: List,Rule JSON
    Opens rule file: CLI,Path JSON

ValidateInstructionsSection
    Wraps validate subsection: ValidateDataSubSection

ValidateRulesAction
    Inject common bot rules: Base Bot,Rules,Common Rules
    Inject behavior specific rules: Behavior,Rules,Behavior Rules
    Load + inject content for validation: Behavior,Content,Knowledge Graph,Rendered Outputs


## Module: behaviors

---------------------------

Behavior
    Name: String
    Description: String
    Goal: String
    Folder: Path
    Is completed: Boolean
    Actions workflow: List
    Action Names: List
    Validation type: ValidationType
    CurrentAction: Action
    Guardrails: Guardrails
    Content: Content
    Rules: Rules
    Actions: Actions

BehaviorsView
    Wraps behaviors JSON: Behaviors JSON
    Displays behavior names list: List,Behavior JSON
    Navigates to behavior: CLI,Behavior
    Toggles collapsed: State,Behavior JSON
    Displays tooltip: String,Behavior JSON
    Displays actions: ActionsView
    Executes behavior: CLI,Behavior
    Displays completion progress: Status,Behavior JSON
    Displays navigation: NavigationView

Guardrails
    Provide required context: Key Questions,Evidence
    Guide Strategy decisions: Decision Criteria,Assumptions
    Define recommended human activity: Human,Instructions

JSONBehavior
    Serialize behavior to JSON dict: Behavior,Dict
    Include behavior metadata: Name,Description,Status
    Include actions: Actions,Array
    Wraps domain behavior: Behavior

MarkdownBehavior
    Serialize behavior to Markdown: Behavior,String
    Format behavior documentation: Behavior Name,Description,Section
    Format actions: Actions,Markdown Subsections
    Wraps domain behavior: Behavior

NavigationView
    Wraps current action JSON: Action JSON
    Reruns action: CLI,Action
    Navigates to next action: CLI,Action
    Navigates to prev action: CLI,Action

Rule
    Validate content: Knowledge Graph,Violations
    Find behavior specific rules from context: Behavior
    Find common bot rules from context: Base Bot
    Load + inject diagnostics results: AI Chat,Violations,Corrections
    Suggest corrections: Violations,Suggestions,Fixes
    Provide examples - Do: Example,Description
    Provide examples - Dont: Example,Description
    Specialized examples: Language,Framework,Pattern

TTYBehavior
    Serialize behavior to TTY: Behavior,String
    Format behavior line: Behavior Name,Marker,Color
    Format actions: Actions,String
    Wraps domain behavior: Behavior


## Module: bot

AvailableBotsView
    Wraps bot registry JSON: BotRegistry JSON
    Displays available bots: List,BotRegistry JSON
    Selects bot: CLI,Bot

Base Bot
    Executes Actions: Workflow,Behavior,Action
    Execute behavior: Behavior,BotResult
    Execute current action: BotResult
    Navigate and execute: Behavior,Action,ActionContext,BotResult
    Validate behavior exists: Behavior,Boolean
    Validate action exists: Behavior,Action,Boolean
    Track activity: Behavior,Action
    Route to behaviors and actions: Router,Trigger Words
    Persist content: Content
    Manage Project State: Project
    Render: 
    Get scope: Scope (read-only property)
    Get status: Status
    Navigate next: NavigationResult
    Navigate back: NavigationResult
    Get bot path: BotPath
    Get help: Help
    Exit: ExitResult

BotHeaderView
    Wraps bot JSON: Bot JSON
    Displays image: Image
    Displays title: String,Bot JSON
    Displays version number: String,Bot JSON
    Refreshes panel: CLI

BotView
    Wraps bot JSON: Bot JSON
    Displays BotHeaderView: BotHeaderView
    Displays PathsSection: PathsSection
    Displays BehaviorsView: BehaviorsView
    Displays ScopeSection: ScopeSection
    Displays InstructionsSection: InstructionsSection

JSONBot
    Execute behavior by name: Behavior Name String,JSON String
    Execute current action: JSON String
    Navigate and execute: Dot Notation String,JSON String
    Validate behavior exists: Behavior Name String,JSON String
    Validate action exists: Dot Notation String,JSON String
    Serialize bot to JSON: Bot,JSON String
    Include bot metadata: Name,Directory,Paths
    Behaviors: Bot,Behaviors,JSON Behaviors
    Get status: JSON String (delegates to JSONStatus)
    Get scope: JSON String (delegates to JSONScope)
    Navigate next: JSON String (delegates to JSONNavigation)
    Navigate back: JSON String (delegates to JSONNavigation)
    Get bot path: JSON String (delegates to JSONBotPath)
    Get help: JSON String (delegates to JSONHelp)
    Exit: JSON String (delegates to JSONExitResult)
    Wraps domain bot: Bot

MarkdownBot
    Execute behavior by name: Behavior Name String,Markdown String
    Execute current action: Markdown String
    Navigate and execute: Dot Notation String,Markdown String
    Validate behavior exists: Behavior Name String,Markdown String
    Validate action exists: Dot Notation String,Markdown String
    Serialize bot to Markdown: Bot,Markdown String
    Format bot documentation: Bot Name,Description,Markdown Header
    Behaviors: Bot,Behaviors,Markdown Behaviors
    Get status: Markdown String (delegates to MarkdownStatus)
    Get scope: Markdown String (delegates to MarkdownScope)
    Navigate next: Markdown String (delegates to MarkdownNavigation)
    Navigate back: Markdown String (delegates to MarkdownNavigation)
    Get bot path: Markdown String (delegates to MarkdownBotPath)
    Get help: Markdown String (delegates to MarkdownHelp)
    Exit: Markdown String (delegates to MarkdownExitResult)
    Wraps domain bot: Bot

PathsSection
    Wraps bot paths JSON: BotPaths JSON
    Displays bot directory: String,BotPaths JSON
    Edits workspace directory: CLI,BotPaths JSON
    Displays available bots: AvailableBotsView

Specific Bot
    Provide Behavior config: Bot Config,Behavior
    Provide MCP config: MCP Config
    Provide Renderers: 
    Provide Extractors: 
    Provide Synchronizer: 
    Provide Trigger Words: 

TTYBot
    Execute behavior by name: Behavior Name String,TTY String
    Execute current action: TTY String
    Navigate and execute: Dot Notation String,TTY String
    Validate behavior exists: Behavior Name String,TTY String (True/False)
    Validate action exists: Dot Notation String,TTY String (True/False)
    Serialize entire bot to TTY: Bot,TTY String
    Bot header: Bot Name,TTY String
    Behaviors: Bot,Behaviors,TTY Behaviors
    Get status: TTY String (delegates to TTYStatus)
    Get scope: TTY String (delegates to TTYScope)
    Navigate next: TTY String (delegates to TTYNavigation)
    Navigate back: TTY String (delegates to TTYNavigation)
    Get bot path: TTY String (delegates to TTYBotPath)
    Get help: TTY String (delegates to TTYHelp)
    Exit: TTY String (delegates to TTYExitResult)
    Wraps domain bot: Bot


## Module: bot_path

BotPath
    Get bot directory: Path
    Get workspace directory: Path
    Get behaviors directory: Path
    Get config path: Path
    Get all paths: Dict

JSONBotPath
    Serialize bot path to JSON: BotPath,JSON String
    Include all paths: Dict,JSON
    Wraps domain bot path: BotPath

MarkdownBotPath
    Serialize bot path to Markdown: BotPath,Markdown String
    Format paths section: BotPath,Markdown String
    Wraps domain bot path: BotPath

TTYBotPath
    Serialize bot path to TTY: BotPath,TTY String
    Format path display: Path Name,Path Value,TTY String
    Format all paths: BotPath,TTY String
    Wraps domain bot path: BotPath


## Module: cli

CLISession
    Runs CLI loop: 
    Reads input from stdin or terminal: 
    Determine channel adapter: ChannelAdapter
    Read and execute command: Command String,CLICommandResponse
    Parse command: Command String,Command Verb,Params
    Route to bot domain methods: Bot,Command Verb,Params,BotResult
    Serializes via channel adapter: ChannelAdapter,String
    Displays serialized output: Stdout

ChannelAdapter (Abstract)
    Serialize domain object to format: Domain Object,Format
    Deserialize format to domain object: Format,Domain Object

JSONAdapter
    Serialize to JSON dict: Dict
    Deserialize JSON dict: Dict,Domain Object
    Convert to JSON string: Dict,String
    Parse JSON string: String,Dict
    Validate JSON structure: Dict,Schema

JSONProgressAdapter
    Include progress fields: Is Completed,Is Current
    Include completion markers: Progress String

MarkdownAdapter
    Serialize to Markdown: String
    Deserialize Markdown: String,Domain Object
    Parse markdown sections: Markdown,Sections
    Format header: Level,Text
    Format list item: Marker,Text,Indent
    Format code block: Language,Content

MarkdownProgressAdapter
    Render progress marker: Is Completed,Is Current,Marker String
    Format progress line: Name,Is Completed,Is Current,String

TTYAdapter
    Serialize to TTY text: Domain Object,String
    Deserialize TTY text: String,Domain Object
    Add color: Text,Color
    Format indentation: Indent Level,Spaces

TTYProgressAdapter
    Format line with marker: Marker,Text,Indent
    Render marker: Is Completed,Is Current

TextAdapter
    Parse command text: Text String,Command,Params


## Module: exit_result

ExitResult
    Get exit code: Integer
    Get exit message: String
    Get should cleanup: Boolean

JSONExitResult
    Serialize exit result to JSON: ExitResult,JSON String
    Include exit code: Integer,JSON
    Include exit message: String,JSON
    Wraps domain exit result: ExitResult

MarkdownExitResult
    Serialize exit result to Markdown: ExitResult,Markdown String
    Format exit documentation: ExitResult,Markdown String
    Wraps domain exit result: ExitResult

TTYExitResult
    Serialize exit result to TTY: ExitResult,TTY String
    Format exit message: Message,TTY String
    Wraps domain exit result: ExitResult


## Module: help

### status

JSONHelp
    Serialize help to JSON: Help,Dict
    Include help sections: Sections,Array
    Wraps domain help: Help

JSONStatus
    Serialize status to JSON: Status,JSON String
    Include progress path: Progress Path,String
    Include stage name: Stage Name,String
    Include current behavior: Behavior Name,String
    Include current action: Action Name,String
    Wraps domain status: Status

MarkdownHelp
    Serialize help to Markdown: Help,String
    Format help sections: Sections,Markdown
    Wraps domain help: Help

MarkdownStatus
    Serialize status to Markdown: Status,Markdown String
    Format progress section: Progress Path,Stage Name,Markdown String
    Format workflow state: Status,Markdown String
    Wraps domain status: Status

Status
    Get progress path: String
    Get stage name: String
    Get current behavior name: String
    Get current action name: String
    Get has current behavior: Boolean
    Get has current action: Boolean

TTYHelp
    Serialize help to TTY: Help,String
    Format help sections: Sections,String
    Wraps domain help: Help

TTYStatus
    Serialize status to TTY: Status,TTY String
    Format progress line: Progress Path,Stage Name,TTY String
    Format hierarchical status: Bot,Status,TTY String
    Wraps domain status: Status


## Module: instructions

BaseInstructionsSubSection
    Wraps instructions JSON: Instructions JSON
    Displays behavior name: String,Instructions JSON
    Displays action name: String,Instructions JSON
    Displays  Instructions: Instructions JSON

InstructionsSection
    Wraps instructions JSON: Instructions JSON
    Wraps action JSON: Action JSON
    Displays base instructions subsection: BaseInstructionsSubSection
    Displays raw format subsection: RawFormatSubSection
    Submits to AI chat: CLI,Instructions JSON

JSONInstructions
    Serialize instructions to JSON: Instructions,Dict
    Include instruction sections: Sections,Array
    Wraps domain instructions: Instructions

MarkdownInstructions
    Serialize instructions to Markdown: Instructions,String
    Format instruction sections: Sections,Markdown
    Wraps domain instructions: Instructions

RawFormatSubSection
    Wraps instructions JSON: Instructions JSON
    Displays raw instructions: String,Instructions JSON

TTYInstructions
    Serialize instructions to TTY: Instructions,String
    Format instruction sections: Sections,String
    Wraps domain instructions: Instructions


## Module: navigation

JSONNavigation
    Serialize navigation to JSON: NavigationResult,JSON String
    Include previous action: Action,JSON
    Include next action: Action,JSON
    Include navigation state: Can Back,Can Next,JSON
    Wraps domain navigation: NavigationResult

MarkdownNavigation
    Serialize navigation to Markdown: NavigationResult,Markdown String
    Format navigation section: NavigationResult,Markdown String
    Wraps domain navigation: NavigationResult

NavigationResult
    Get previous action: Action
    Get next action: Action
    Get can navigate back: Boolean
    Get can navigate next: Boolean
    Get navigation path: String

TTYNavigation
    Serialize navigation to TTY: NavigationResult,TTY String
    Format navigation options: Can Back,Can Next,TTY String
    Format navigation path: Path String,TTY String
    Wraps domain navigation: NavigationResult


## Module: panel

ConfirmationDialog
    Shows confirmation inline: Message,DOM Element
    Shows confirm and cancel buttons: Button Set
    Invokes callback on confirm: Callback Function
    Hides confirmation on cancel: DOM Element

PanelHeader
    Displays header image: Image
    Displays title: String

PanelView (Base)
    Wraps JSON data: JSON
    Spawns subprocess: CLI,Python Process
    Sends command to CLI: Command,Stdin
    Receives JSON from CLI: Stdout
    Parses JSON: String,Dict
    Provides element ID: String
    Renders to HTML: HTML,JSON

SectionView
    Renders section header: PanelHeader
    Toggles collapsed state: State
    May contain subsections: SubSectionView

SubSectionView
    Toggles collapsed state: State


## Module: scope

JSONScope
    Serialize scope to JSON: Scope,JSON String
    Include filter: Filter String,String
    Include results: Results List,Array
    Include filter metadata: Is Active,Count,JSON
    Wraps domain scope: Scope

MarkdownScope
    Serialize scope to Markdown: Scope,Markdown String
    Format filter section: Filter String,Markdown String
    Format results list: Results,Markdown List
    Format filter documentation: Scope,Markdown String
    Wraps domain scope: Scope

Scope
    Get filter: String (read/write property)
    Set filter: String
    Get results: List (read-only property)
    Apply filter to behaviors: Behaviors,Filtered Behaviors
    Apply filter to stories: Stories,Filtered Stories
    Clear filter: 
    Get filter count: Integer
    Get is active: Boolean

ScopeView
    Wraps scope JSON: Scope JSON
    Displays current filter: String,Scope JSON
    Edits filter: CLI,Scope JSON
    Displays filtered results: List,Scope JSON
    Clears filter: CLI,Scope JSON
    Displays filter status: Is Active,Count,Scope JSON

TTYScope
    Serialize scope to TTY: Scope,TTY String
    Format filter display: Filter String,TTY String
    Format results list: Results,TTY String
    Format filter status: Is Active,Count,TTY String
    Wraps domain scope: Scope


## Module: story_graph.acceptance_criteria

AcceptanceCriteria
    Get steps: List[Step]

AcceptanceCriteriaView
    Wraps acceptance criteria JSON: AcceptanceCriteria JSON
    Displays criteria name: String,AcceptanceCriteria JSON
    Displays criteria icon: Image
    Displays steps as checklist: List[Step],HTML

JSONAcceptanceCriteria
    Include steps: List[Step],JSON Array
    Wraps domain acceptance criteria: AcceptanceCriteria

MarkdownAcceptanceCriteria
    Format criteria as checklist: List[Step],Markdown
    Format steps list: List[Step],Markdown
    Wraps domain acceptance criteria: AcceptanceCriteria

TTYAcceptanceCriteria
    Format steps: List[Step],TTY String
    Format criteria list: List[Step],TTY String
    Wraps domain acceptance criteria: AcceptanceCriteria


## Module: story_graph.domain

Collaborator
    Get name: String
    From string: String,Collaborator
    To string: String

DomainConcept
    Get name: String
    Get responsibilities: List[Responsibility]
    From dict: Dict,DomainConcept
    To dict: Dict

DomainModule
    Contains domain objects: List[DomainConcept]
    Get submodules: List[Module]
    Get parent module: Module

JSONDomainConcept
    Serialize domain concept to JSON: DomainConcept,JSON String
    Include responsibilities: List[Responsibility],JSON Array
    Wraps domain concept: DomainConcept

MarkdownDomainConcept
    Serialize domain concept to Markdown: DomainConcept,Markdown String
    Format CRC table: DomainConcept,Markdown
    Format responsibilities section: List[Responsibility],Markdown
    Wraps domain concept: DomainConcept

Responsibility
    Get name: String
    Get collaborators: List[Collaborator]
    From dict: Dict,Responsibility
    To dict: Dict

TTYDomainConcept
    Serialize domain concept to TTY: DomainConcept,TTY String
    Format responsibilities: List[Responsibility],TTY String
    Format CRC card: DomainConcept,TTY String
    Wraps domain concept: DomainConcept


## Module: story_graph.epic

Epic
    Test file property: String
    Get all stories: List[Story]
    Get domain concepts: List[DomainConcept]

EpicView
    Wraps epic JSON: Epic JSON
    Displays epic name: String,Epic JSON
    Displays epic icon: Image
    Displays sub epics: SubEpicView,SubEpic JSON
    Opens epic folder: CLI,Epic JSON
    Opens epic test file: CLI,Epic JSON

JSONEpic
    Include domain concepts: List[DomainConcept],JSON Array
    Wraps domain epic: Epic

MarkdownEpic
    Format domain concepts table: List[DomainConcept],Markdown
    Wraps domain epic: Epic

TTYEpic
    Format domain concepts: List[DomainConcept],TTY String
    Wraps domain epic: Epic


## Module: story_graph.nodes

InlineNameEditor
    Enables inline editing mode: DOM Element,Input Field
    Validates name in real-time: StoryNode,Siblings Collection
    Saves name on blur or Enter: StoryNode,Event
    Cancels on Escape: Event,Original Value
    Shows validation messages: ValidationMessageDisplay,Message

JSONStoryNode
    Serialize node to JSON: StoryNode,JSON String
    Include name: String,JSON
    Include sequential order: Float,JSON
    Include children: List[StoryNode],JSON Array
    Add child: StoryNode,JSON Result
    Add child at position: StoryNode,Position,JSON Result
    Delete child: StoryNode,JSON Result
    Delete this node: JSON Result
    Delete with children: JSON Result
    Update name: String,JSON Result
    Move to parent: New Parent,Position,JSON Result
    Move after target: Target StoryNode,JSON Result
    Move before target: Target StoryNode,JSON Result
    Reorder children: Start Pos,End Pos,JSON Result
    Automatically refresh story graph: JSON Result
    Wraps domain story node: StoryNode

MarkdownStoryNode
    Serialize node to Markdown: StoryNode,Markdown String
    Format node header: String,Sequential Order,Markdown
    Format children list: List[StoryNode],Markdown
    Wraps domain story node: StoryNode

StoryNode (Base)
    Serializes: StoryNodeSerializer
    Get/Update name: String
    Get node type: String
    Get node ID: String,StoryNode,StoryNodeNavigator
    Get parent: StoryNode
    Get sequential order: StoryNodeNavigator,Float
    Contains Children: StoryNodeChildren
    Delete self: StoryNodeSerializer
    Delete with children: StoryNodeSerializer,StoryNodeChildren
    Get/Update test: Test

StoryNodeChildren
    Get children: List[StoryNode]
    Find child by name: String,StoryNode
    Delete child: StoryNode

StoryNodeNavigator
    Build node ID from hierarchy path: String,StoryNode
    Get parent: StoryNode
    Move to parent: New Parent,Position
    Move after: StoryNode,sequential order
    Move before: StoryNode,sequential order
    DetermineOrder: FLoat,StoryNode

StoryNodeSerializer
    File: File
    Create Node: File,StoryNode
    Load Node: File,StoryNode
    Update Node: File,StoryNode
    Delete Node: File,StoryNode
    From JSON: JSON,StoryNode
    To JSON: JSON,StoryNode

StoryNodeView
    Wraps story node JSON: StoryNode JSON
    Toggles collapsed: State
    Add child node: StoryNode,Panel Result
    Add child at position: StoryNode,Position,Panel Result
    Delete this node: Panel Result
    Delete with children: Panel Result
    Update node name: String,Panel Result
    Move to parent: New Parent,Position,Panel Result
    Move after target: Target StoryNode,Panel Result
    Move before target: Target StoryNode,Panel Result
    Drag and drop: Drop Target,Position,Panel Result
    Reorder children: Start Pos,End Pos,Panel Result
    Automatically refresh story graph: Panel Result

TTYStoryNode
    Serialize node to TTY: StoryNode,TTY String
    Format name: String,TTY String
    Format sequential order: Float,TTY String
    Format children: List[StoryNode],TTY String
    Add child: StoryNode,CLI Result
    Add child at position: StoryNode,Position,CLI Result
    Delete child: StoryNode,CLI Result
    Delete this node: CLI Result
    Delete with children: CLI Result
    Update name: String,CLI Result
    Move to parent: New Parent,Position,CLI Result
    Move after target: Target StoryNode,CLI Result
    Move before target: Target StoryNode,CLI Result
    Reorder children: Start Pos,End Pos,CLI Result
    Automatically refresh story graph: CLI Result
    Wraps domain story node: StoryNode

ValidationMessageDisplay
    Shows warning message: Message Text,DOM Element
    Hides message: DOM Element
    Applies message styling: CSS Class,Message Type


## Module: story_graph.scenario

JSONScenario
    Include steps: List[Step],JSON Array
    Include test method: Test Method,JSON
    Wraps domain scenario: Scenario

MarkdownScenario
    Format Gherkin scenario: Scenario,Markdown
    Format steps as Given/When/Then: List[Step],Markdown
    Wraps domain scenario: Scenario

Scenario
    Test method property: String
    Get test method: String
    Get default test method: String
    Get steps: List[Step]

ScenarioView
    Wraps scenario JSON: Scenario JSON
    Displays scenario name: String,Scenario JSON
    Displays scenario icon: Image
    Opens test at scenario: CLI,Scenario JSON

TTYScenario
    Format steps: List[Step],TTY String
    Format test method: Test Method,TTY String
    Wraps domain scenario: Scenario


## Module: story_graph.scenario_outline

JSONScenarioOutline
    Include steps: List[Step],JSON Array
    Include examples: List[Dict],JSON Array
    Include test method: Test Method,JSON
    Wraps domain scenario outline: ScenarioOutline

MarkdownScenarioOutline
    Format Gherkin scenario outline: ScenarioOutline,Markdown
    Format steps as Given/When/Then: List[Step],Markdown
    Format examples table: List[Dict],Markdown
    Wraps domain scenario outline: ScenarioOutline

ScenarioOutline
    Test method property: String
    Get test method: String
    Get default test method: String
    Get examples: List[Dict]
    Get steps: List[Step]

ScenarioOutlineView
    Wraps scenario outline JSON: ScenarioOutline JSON
    Displays scenario outline name: String,ScenarioOutline JSON
    Displays scenario outline icon: Image
    Displays examples table: List[Dict],Table HTML
    Opens test at scenario outline: CLI,ScenarioOutline JSON

TTYScenarioOutline
    Format steps: List[Step],TTY String
    Format examples: List[Dict],TTY String
    Format test method: Test Method,TTY String
    Wraps domain scenario outline: ScenarioOutline


## Module: story_graph.step

JSONStep
    Include step text: String,JSON
    Wraps domain step: Step

MarkdownStep
    Format step as Gherkin: Step,Markdown
    Wraps domain step: Step

Step
    Get text: String

StepView
    Wraps step JSON: Step JSON
    Displays step text: String,Step JSON
    Displays step icon: Image

TTYStep
    Format step text: String,TTY String
    Format step keyword: String,TTY String
    Wraps domain step: Step


## Module: story_graph.story

JSONStory
    Include users: List[StoryUser],JSON Array
    Include test metadata: Test File,Test Class,JSON
    Wraps domain story: Story

MarkdownStory
    Format story card: Story,Markdown
    Format users section: List[StoryUser],Markdown
    Wraps domain story: Story

Story
    Test class property: String
    Get test class: String
    Get default test class: String
    Get story type: String
    Get users: List[StoryUser]
    Get scenarios: List[Scenario]
    Get scenario outlines: List[ScenarioOutline]
    Get acceptance criteria: List[AcceptanceCriteria]

StoryView
    Wraps story JSON: Story JSON
    Displays story name: String,Story JSON
    Displays story icon: Image
    Displays scenarios: ScenarioView,Scenario JSON
    Opens test at class: CLI,Story JSON

TTYStory
    Format users: List[StoryUser],TTY String
    Format test metadata: Test File,Test Class,TTY String
    Wraps domain story: Story


## Module: story_graph.story_group

StoryGroup


## Module: story_graph.story_map

DotNotationParser
    Parses dot notation to node path: Dot Notation String,Path Segments
    Resolves node from path: StoryGraph,Path Segments,StoryNode
    Formats navigation error with valid paths: Error Message,Valid Paths List

FileModificationMonitor
    Detects file modification: File System,Last Modified Timestamp
    Delegates reload to StoryGraph: StoryGraph,File Path
    Triggers panel refresh: StoryMapView,DOM
    Shows validation error notification: Error Message,Panel Display
    Retains previous valid graph on error: Previous Graph,StoryGraph

JSONStoryMap
    Serialize story map to JSON: StoryMap,JSON String
    Include story graph: Dict,JSON
    Include all epics: List[Epic],JSON Array
    Wraps domain story map: StoryMap

MarkdownStoryMap
    Serialize story map to Markdown: StoryMap,Markdown String
    Format epic hierarchy: List[Epic],Markdown
    Format story index: List[Story],Markdown
    Wraps domain story map: StoryMap

StoryMap
    Load from bot directory: Bot,StoryMap
    Load from story graph: File Path,StoryMap
    Creates Epic at root level: Epic,Name,Position
    Walk nodes: StoryNode,Iterator[StoryNode]
    Get all stories: List[Story]
    Get all scenarios: List[Scenario]
    Get all domain concepts: List[DomainConcept]
    Find by name: Name,StoryNode
    Find node by path: Path String,StoryNode
    Get story graph dict: Dict
    Get epics: List[Epic]
    Save to story graph: File Path
    Reload from story graph: File Path,StoryMap
    Validate graph structure: Validation Result

StoryMapView
    Wraps story map JSON: StoryMap JSON
    Renders story graph as tree hierarchy: StoryNode,HTML
    Displays epic hierarchy: EpicView,Epic JSON
    Shows context-appropriate action buttons: StoryNode,ButtonSet
    Refreshes tree display: StoryGraph,DOM
    Searches stories: Filter,StoryGraph JSON
    Opens story graph file: CLI,File JSON
    Opens story map file: CLI,File JSON
    Delegates to InlineNameEditor: InlineNameEditor,StoryNode
    Delegates to DragDropManager: DragDropManager,StoryNode

TTYStoryMap
    Serialize story map to TTY: StoryMap,TTY String
    Format epics list: List[Epic],TTY String
    Format story hierarchy: StoryMap,TTY String
    Walk and format nodes: StoryNode,TTY String
    Wraps domain story map: StoryMap


## Module: story_graph.story_user

JSONStoryUser
    Serialize user to JSON: StoryUser,JSON String
    Include user name: String,JSON
    Include user list: List[StoryUser],JSON Array
    Wraps domain story user: StoryUser

MarkdownStoryUser
    Serialize user to Markdown: StoryUser,Markdown String
    Format user badge: StoryUser,Markdown
    Format user list: List[StoryUser],Markdown
    Wraps domain story user: StoryUser

StoryUser
    Get name: String
    From string: String,StoryUser
    From list: List[String],List[StoryUser]
    To string: String

StoryUserView
    Wraps story user JSON: StoryUser JSON
    Displays user name: String,StoryUser JSON
    Displays user icon: Image
    Filters stories by user: StoryUser,Panel Result

TTYStoryUser
    Serialize user to TTY: StoryUser,TTY String
    Format user name: String,TTY String
    Format user list: List[StoryUser],TTY String
    Wraps domain story user: StoryUser


## Module: story_graph.sub_epic

SubEpic
    Test file property: String

SubEpicView
    Wraps sub epic JSON: SubEpic JSON
    Displays sub epic name: String,SubEpic JSON
    Displays sub epic icon: Image
    Displays nested sub epics: SubEpicView,SubEpic JSON
    Displays stories: StoryView,Story JSON
    Opens sub epic folder: CLI,SubEpic JSON
    Opens sub epic test file: CLI,SubEpic JSON


## Module: story_graph.test

JSONTest
    Serialize test to JSON: Test,JSON String
    Include test file: String,JSON
    Include test class: String,JSON
    Include test method: String,JSON
    Wraps domain test: Test

MarkdownTest
    Serialize test to Markdown: Test,Markdown String
    Format test link: Test File,Test Class,Test Method,Markdown
    Wraps domain test: Test

TTYTest
    Serialize test to TTY: Test,TTY String
    Format test file: String,TTY String
    Format test class: String,TTY String
    Format test method: String,TTY String
    Wraps domain test: Test

Test
    Get test file: String
    Get test class: String
    Get test method: String
    Get default test class: String
    Get default test method: String
    Build from story node: StoryNode,TestMetadata

TestView
    Wraps test JSON: Test JSON
    Displays test file: String,Test JSON
    Displays test class: String,Test JSON
    Displays test method: String,Test JSON
    Opens test file: CLI,Test JSON
    Opens test at class: CLI,Test JSON
    Opens test at method: CLI,Test JSON

