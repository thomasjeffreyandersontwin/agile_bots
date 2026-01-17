(E) Build Agile Bots
    (E) Generate MCP Tools
        (S) MCP Server Generator --> Generate Bot Tools
        and (S) MCP Server Generator --> Generate Behavior Tools
        and (S) MCP Server Generator --> Generate MCP Bot Server
        and (S) MCP Server Generator --> Generate Behavior Action Tools
        and (S) Deploy MCP BOT Server
        and (S) MCP Server Generator --> Restart MCP Server To Load Code Changes
    and (E) Generate CLI
        (S) Generator --> Generate Command Definitions
        and (S) Generator --> Generate CLI Entry Point
        and (S) Generator --> Generate Cursor Commands
        and (S) Generator --> Generate Help Documentation
and (E) Invoke Bot
    (E) Invoke MCP
        (S) AI Chat --> Invoke Bot Tool
        and (S) Bot Behavior --> Load And Merge Behavior Action Instructions
        and (S) AI Chat --> Forward To Current Behavior and Current Action
        and (S) AI Chat --> Forward To Current Action
        and (S) Bot Behavior --> Track Activity For Workspace
    and (E) Invoke Bot Directly
        (E) Navigate And Execute Behaviors
            (S) Bot Behavior --> Manage Behaviors
            and (S) Bot Behavior --> Manage Behavior Action State
            and (S) Bot Behavior --> Navigate To Behavior Action And Execute
            and (S) Bot Behavior --> Navigate Sequentially
            and (S) Bot Behavior --> Inject Context Into Instructions
            and (S) Bot Behavior --> Track Activity For Workspace
            and (S) Bot Behavior --> Execute End To End Workflow
        and (E) Manage Story Graph
            (E) Manage Story Scope
                (S) Bot Behavior --> Create Scope
                and (S) Bot Behavior --> Filter Scope By Stories
                and (S) Bot Behavior --> Filter Scope By Files
                and (S) Bot Behavior --> Persist Scope
                and (S) Bot Behavior --> Clear Scope
                and (S) Bot Behavior --> Execute Actions With Scope
                and (S) Bot Behavior --> Navigate Story Graph
            and (E) Manage File Scope
                (S) Bot Behavior --> Filter File Scope
                and (S) Bot Behavior --> Get All Files For Behavior
                and (S) Bot Behavior --> Add Filter Part To File Scope
                and (S) Bot Behavior --> Remove Filter Part From File Scope
            and (E) Edit Story Graph
                (S) Bot Behavior --> Add Child Story Node To Parent
                and (S) Bot Behavior --> Delete Story Node From Parent
                and (S) Bot Behavior --> Update Story Node name
                and (S) Bot Behavior --> Move Story Node
                and (S) Bot Behavior --> Submit Action Scoped To Story Scope
                and (S) Bot Behavior --> Update Story Graph Changes
            and (E) Edit Increments
                (S) Bot Behavior --> Add Increment
                and (S) Bot Behavior --> Delete Increment
                and (S) Bot Behavior --> Move Story to Increment
                and (S) Bot Behavior --> Show All Increment Scope
                and (S) Bot Behavior --> Submit Action Scoped To Increment
        and (E) Perform Action
            (S) Bot Behavior --> Build Story Graph
            and (S) Bot Behavior --> Clarify Requirements
            and (S) Bot Behavior --> Validate Rules
            and (S) Bot Behavior --> Display Rules
            and (S) Bot Behavior --> Decide Strategy
            and (S) Bot Behavior --> Render Output
            and (S) System --> Save Guardrails
        and (E) Track Activity
            (S) Bot Behavior --> Track Action Start
            and (S) Bot Behavior --> Track Action Completion
            and (S) Bot Behavior --> Record Activity Metrics And Paths
    and (E) Get Help
        (S) Bot Behavior --> Get Help
    and (E) Invoke Bot Through Panel
        (E) Manage Panel Session
            (S) User --> Open Panel
            and (S) User --> Display Session Status
            and (S) User --> Change Workspace Path
            and (S) User --> Switch Bot
            and (S) User --> Toggle Panel Section
        and (E) Navigate And Execute Behaviors Through Panel
            (S) User --> Display Hierarchy
            and (S) User --> Navigate Behavior Action
            and (S) User --> Execute Behavior Action
        and (E) Manage Story Graph Through Panel
            (E) Manage Story Scope Through Panel
                (S) User --> Filter Story Scope
                and (S) User --> Show All Scope Through Panel
                and (S) User --> Display Story Scope Hierarchy
                and (S) User --> Filter File Scope
                and (S) User --> Open Story Files
            and (E) Manage File Scope Through Panel
                (S) Bot Behavior --> Filter File Scope
                and (S) Bot Behavior --> Display All Files For Behavior
                and (S) Bot Behavior --> Add Filter Part To File Scope
                and (S) Bot Behavior --> Remove Filter Part From File Scope
            and (E) Edit Story Graph In Panel
                (S) Bot Behavior --> Add Child Story Node To Parent
                and (S) Bot Behavior --> Delete Story Node From Parent
                and (S) Bot Behavior --> Update Story Node name
                and (S) Bot Behavior --> Move Story Node
                and (S) Bot Behavior --> Submit Action Scoped To Story Scope
                and (S) Bot Behavior --> Automatically Refresh Story Graph Changes
            and (E) Edit Increments In Panel
                (S) Bot Behavior --> Add Increment
                and (S) Bot Behavior --> Delete Increment
                and (S) Bot Behavior --> Move Story to Increment
                and (S) Bot Behavior --> Show All Increment Scope Through Panel
                and (S) Bot Behavior --> Submit Action Scoped To Increment
        and (E) Display Action Instructions Through Panel
            (S) User --> Display Base Instructions
            and (S) User --> Display Clarify Instructions
            and (S) User --> Display Strategy Instructions
            and (S) User --> Display Build Instructions
            and (S) User --> Display Validate Instructions
            and (S) User --> Display Render Instructions
            and (S) User --> Submit Behavior Rules Through Panel
            and (S) User --> Display Instructions In Raw Format
            and (S) User --> Submit Instructions To AI Agent
            and (S) User --> Save Guardrails Through Panel
    and (E) Invoke Bot Through REPL
        (E) Initialize CLI Session
            (S) User --> Launch CLI in Interactive Mode
            and (S) AI Agent, Automation --> Launch CLI in Pipe Mode
            and (S) Web View, API Client --> Launch CLI in JSON Mode
            and (S) CLI --> Display Piped Mode Instructions for AI Agents
            and (S) TTYDetector --> Detect and Configure TTY/Non-TTY Input
            and (S) CLI --> Load and Display Workspace Context in CLI
            and (S) CLI --> Switch Registered Bots
        and (E) Navigate Behaviors Using REPL Commands
            (S) User --> Navigate Using CLI Dot Notation
            and (S) User --> Navigate Sequentially Using CLI Commands
            and (S) User --> Exit CLI REPL
        and (E) Navigate Behaviors Using Domain Model
            (S) System --> Navigate To First Behavior Action
            and (S) System --> Advance Action And Persist State
            and (S) System --> Show Remaining Actions After Completion
        and (E) Display Action Instructions Using REPL
            (E) Display Common Instructions Through REPL
                (S) User --> Get Action Instructions Through CLI
                and (S) User --> Confirm Action Completion Through CLI
                and (S) User --> Re-execute Current Operation Using CLI
                and (S) User --> Handle Operation Errors and Validation in CLI
                and (S) User --> Submit Instructions Through CLI
            and (E) Display Clarify Instructions Through REPL
                (S) User --> Display Clarification Data Through CLI
                and (S) User --> Display Guardrails Through CLI
                and (S) User --> Get Clarify Instructions Through CLI
                and (S) User --> Confirm Clarify With Answers Through CLI
            and (E) Display Strategy Instructions Through REPL
                (S) User --> Display Strategy Data Through CLI
                and (S) User --> Get Strategy Instructions Through CLI
            and (E) Execute Actions Through REPL
                (S) User --> Save Guardrails Through CLI
            and (E) Display Build Instructions Through REPL
                (S) User --> Display Story Graph Through CLI
                and (S) User --> Display Build Scope Through CLI
                and (S) User --> Display Filtered Knowledge Graph Through CLI
                and (S) User --> Get Build Instructions Through CLI
            and (E) Display Validate Instructions Through REPL
                (S) User --> Display Validation Scanners Through CLI
                and (S) User --> Display Validation Results Through CLI
                and (S) User --> Get Validate Instructions Through CLI
            and (E) Display Render Instructions Through REPL
                (S) User --> Display Render Configurations Through CLI
                and (S) User --> Display Synchronizer Output Through CLI
                and (S) User --> Get Render Instructions Through CLI
            and (E) Display Rules Through REPL
                (S) User --> Get Rules Instructions Through CLI
        and (E) Manage Story Graph Using REPL
            (E) Manage Story Scope Using REPL
                (S) User --> Filter Work Using Knowledge Graph Scope in CLI
                and (S) User --> Filter Work Using Files Scope in CLI
                and (S) CLI --> Enforce Mutually Exclusive Scope Types
                and (S) User --> View Current Scope in CLI
                and (S) User --> Clear Scope Through CLI
            and (E) Manage File Scope Using REPL
                (S) Bot Behavior --> Filter File Scope
                and (S) Bot Behavior --> Display All Files For Behavior
                and (S) Bot Behavior --> Add Filter Part To File Scope
                and (S) Bot Behavior --> Remove Filter Part From File Scope
            and (E) Edit Story Graph In CLI
                (S) Bot Behavior --> Add Child Story Node To Parent
                and (S) Bot Behavior --> Delete Story Node From Parent
                and (S) Bot Behavior --> Update Story Node name
                and (S) Bot Behavior --> Move Story Node
                and (S) Bot Behavior --> Submit Action Scoped To Story Scope
                and (S) Bot Behavior --> Automatically Refresh Story Graph Changes
            and (E) Edit Increments In CLI
                (S) Bot Behavior --> Add Increment
                and (S) Bot Behavior --> Delete Increment
                and (S) Bot Behavior --> Move Story to Increment
                and (S) Bot Behavior --> Show All Increment Scope Through CLI
                and (S) Bot Behavior --> Submit Action Scoped To Increment
        and (E) Display State Using REPL
            (S) CLI --> Display CLI Header
            and (S) CLI --> Display Bot Hierarchy Tree with Progress Indicators
            and (S) CLI --> Display Current Position in CLI
            and (S) CLI --> Display Active Scope in CLI Status
            and (S) CLI --> Display CLI Navigation Menu Footer
            and (S) CLI --> Display Headless Mode Status in CLI
            and (S) CLI --> Display Available Bot in Tree Hierarchy
            and (S) CLI --> Display CLI Bot Command in Navigation Menu Footer
        and (E) Get Help Using REPL
            (S) User --> Display Action Help Using CLI
            and (S) User --> Display Parameter Help Using CLI
            and (S) User --> Display Command Examples Using CLI
    and (E) Initialize Bot
        (S) Bot Behavior --> Load Bot
        and (S) Bot Behavior --> Load Bot Behaviors
        and (S) Bot Behavior --> Resolve Bot Path
        and (S) Bot Behavior --> Load Actions
        and (S) Bot Behavior --> Manage Bot Registry