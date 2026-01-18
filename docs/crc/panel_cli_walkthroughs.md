# Domain Walkthrough Realizations: Panel

## Realization Scenarios

### Scenario 1: Open Panel

**Purpose**: User activates panel command, extension creates panel and displays bot information by calling Python CLI, wrapping JSON response, and rendering all sections
**Concepts Traced**: Panel

**Scope**: Invoke Bot Through Panel.Manage Bot Information.Open Panel


#### Walk Throughs

**Walk 1 - Covers**: Extension activation and panel creation

```
panelData: JSON = CLI.execute('status')
  -> cli:  = spawn('python', ['repl_main.py'])
  -> main()
     -> bot: Bot = load_bot()
     -> session: REPLSession = REPLSession(bot)
        -> this.bot = bot
        -> this.adapter: ChannelAdapter = this.determine_channel_adapter()
           return adapter: JSONBotAdapter
     -> session.run()
  -> stdin.write('status')
  -> REPLSession.read_and_execute_command('status')
     -> response: REPLCommandResponse = this.route_to_command_handler('status')
        -> handler: Method = this.get_handler_for_verb('status')
           return handler
        -> response: REPLCommandResponse = handler()
        -> jsonString: String = this.serialize()
           return jsonString: "{name: 'story_bot', workspace: 'base_bot', behaviors: [...], paths: {...}}"
        return output: "{...json...}"
     -> print(output)
  -> stdout: String = cli.stdout.read()
  -> panelData: JSON = JSON.parse(stdout)
  return panelData
panel: Panel = new Panel(panelData, cliClient)
return panel
```

**Walk 2 - Covers**: Panel constructor and section rendering

```
this.botJSON = panelData
this.cliClient = cliClient
headerView: BotHeaderView = new BotHeaderView(this.botJSON, this.cliClient)
pathsSection: PathsSection = new PathsSection(this.botJSON.paths, this.cliClient)
behaviorsSection: BehaviorsSection = new PathsSection(this.botJSON.behaviors, this.cliClient)
scopeSection: ScopeSection = new ScopeSection(this.botJSON.scope, this.cliClient)
instructionsSection: InstructionsSection = new InstructionsSection(this.botJSON.instructions, this.cliClient)
html: String = this.render()
  -> headerHTML: String = headerView.render()
     return `<div>${this.botJSON.name} v${this.botJSON.version}</div>`
  -> pathsHTML: String = pathsSection.render()
     return `<div>${this.botJSON.paths.workspace}</div>`
  -> behaviorsHTML: String = behaviorsSection.render()
  -> scopeHTML: String = scopeSection.render()
  -> instructionsHTML: String = instructionsSection.render()
  return html
webview.html = html
```

**Validation Result**: Model supports this scenario
**Gaps Found**: None
**Recommendations**: None

---

### Scenario 2: Refresh Panel

**Purpose**: User clicks refresh button, panel calls CLI to get updated status, wraps new JSON, and re-renders all sections
**Concepts Traced**: Panel

**Scope**: Invoke Bot Through Panel.Manage Bot Information.Refresh Panel


#### Walk Throughs

**Walk 1 - Covers**: User refresh action and CLI round-trip

```
BotHeaderView.onRefreshClick()
  -> newData: JSON = this.cliClient.execute('status')
     -> cli.stdin.write('status')
     -> REPLSession.handle_command('status')
        -> output: String = this.adapter.serialize()
           return jsonString: "{...}"
        -> print(output)
     -> stdout: String = cli.stdout.read()
     -> newData: JSON = JSON.parse(stdout)
     return newData
  -> this.botJSON = newData
  -> panel.update(newData)
     -> this.botJSON = newData
     -> html: String = this.render()
     -> webview.html = html
  return success
```

**Validation Result**: Model supports this scenario
**Gaps Found**: None
**Recommendations**: None

---

### Scenario 3: Display Hierarchy

**Purpose**: Panel displays behavior hierarchy with actions, user expands/collapses behaviors (instant), completion status from JSON
**Concepts Traced**: BehaviorsSection

**Scope**: Invoke Bot Through Panel.Navigate Behavior Action Status.Display Hierarchy


#### Walk Throughs

**Walk 1 - Covers**: Rendering behavior hierarchy from JSON

```
this.behaviorsJSON = behaviorsJSON
this.cliClient = cliClient
html: String = this.render()
  -> behaviorsHTML: String = this.render_all_behaviors()
     -> behaviorView: BehaviorView = new BehaviorView(behavior, this.cliClient)
     -> behaviorHTML: String = behaviorView.render()
        -> name: String = this.behaviorJSON.name
        -> status: String = this.behaviorJSON.status
        -> actionsHTML: String = actionsView.render_all_actions()
           return actionsHTML: "<div>gather_context [completed]</div>..."
        return `<div class='behavior ${status}'>${name}${actionsHTML}</div>`
     return behaviorsHTML: "<div class='behavior current'>discover...</div>"
  return behaviorsHTML
```

**Walk 2 - Covers**: User expands behavior (client-side toggle)

```
BehaviorView.onToggleClick()
  -> this.expanded = !this.expanded
  -> elementHTML: String = this.render()
  -> document.getElementById(this.elementId).innerHTML = elementHTML
  return
```

**Validation Result**: Model supports this scenario
**Gaps Found**: None
**Recommendations**: None

---

### Scenario 4: Execute Behavior Action

**Purpose**: User clicks behavior to execute, system navigates to behavior and executes first action via CLI
**Concepts Traced**: BehaviorsSection

**Scope**: Invoke Bot Through Panel.Navigate Behavior Action Status.Execute Behavior Action


#### Walk Throughs

**Walk 1 - Covers**: User executes behavior via CLI

```
BehaviorView.onExecuteClick()
  -> behaviorName: String = this.behaviorJSON.name
  -> result: JSON = this.cliClient.execute(behaviorName)
     -> cli:  = spawn('python', ['repl_main.py'])
     -> stdin.write(behaviorName)
     -> REPLSession.handle_command(behaviorName)
        -> botResult: BotResult = this.bot.execute_behavior(behaviorName)
           -> isValid: Boolean = this.validate_behavior_exists(behaviorName)
              return True
           -> behavior: Behavior = this.behaviors.get(behaviorName)
           -> action: Action = behavior.get_current_action()
           -> result: ActionResult = action.execute()
           -> this.track_activity(behavior, action)
           return botResult: {behavior: behaviorName, action: action.name, status: 'in_progress'}
        -> output: String = this.adapter.serialize(botResult)
        -> print(output)
     return statusJSON
  -> panel.update(result)
     -> this.behaviorsJSON = result.behaviors
     -> html: String = behaviorsSection.render()
     -> webview.postMessage({update: 'behaviors', html: html})
  return
```

**Validation Result**: Model supports this scenario
**Gaps Found**: None
**Recommendations**: None

---

### Scenario 5: Display Story Scope Hierarchy

**Purpose**: Panel displays nested epic/sub-epic/story/scenario hierarchy from story graph JSON, user can expand/collapse and navigate
**Concepts Traced**: StoryGraphTabView

**Scope**: Invoke Bot Through Panel.Filter And Navigate Scope.Display Story Scope Hierarchy


#### Walk Throughs

**Walk 1 - Covers**: Rendering 4-level nested hierarchy from JSON

```
this.storyMapJSON = storyMapJSON
this.cliClient = cliClient
html: String = this.render()
  -> epicsHTML: String = this.render_all_epics()
     epicView: EpicView = new EpicView(epic, this.cliClient)
     epicHTML: String = epicView.render()
       -> name: String = this.epicJSON.name
       -> icon: String = this.epicJSON.icon
       -> subEpicsHTML: String = this.render_sub_epics()
          subEpicView: SubEpicView = new SubEpicView(subEpic, this.cliClient)
          subEpicHTML: String = subEpicView.render()
            -> storiesHTML: String = this.render_stories()
               storyView: StoryView = new StoryView(story, this.cliClient)
               storyHTML: String = storyView.render()
                 -> scenariosHTML: String = this.render_scenarios()
                    return scenariosHTML: "<div>Scenario 1</div>..."
                 return `<div>${this.storyJSON.name}${scenariosHTML}</div>`
               return storiesHTML: "<div>Story 1...</div>"
            return `<div>${this.subEpicJSON.name}${storiesHTML}</div>`
          return subEpicsHTML: "<div>Sub-Epic 1...</div>"
       return `<div>${name}${subEpicsHTML}</div>`
     return epicsHTML: "<div>Epic 1...</div>"
  return epicsHTML
```

**Walk 2 - Covers**: User opens epic folder via CLI

```
EpicView.onFolderClick()
  -> folderPath: String = this.epicJSON.folder_path
  -> this.cliClient.sendMessage({command: 'openScope', filePath: folderPath})
     -> vscode.commands.executeCommand('vscode.open', fileUri)
  return
```

**Validation Result**: Model supports this scenario
**Gaps Found**: None
**Recommendations**: None

---

### Scenario 6: Filter Story Scope

**Purpose**: User types story name in filter, system calls CLI to update scope filter, returns filtered JSON, view re-renders with filtered hierarchy
**Concepts Traced**: StoryGraphTabView

**Scope**: Invoke Bot Through Panel.Filter And Navigate Scope.Filter Story Scope


#### Walk Throughs

**Walk 1 - Covers**: User filters scope via CLI

```
ScopeSection.onFilterInput('Open Panel')
  -> filteredData: JSON = this.cliClient.execute('scope "Open Panel"')
     -> cli:  = spawn('python', ['repl_main.py'])
     -> stdin.write('scope "Open Panel"')
     -> Bot.update_scope_filter('Open Panel')
        -> scope: Scope = Scope.filter_by_story('Open Panel')
        -> filteredStoryMap: JSON = scope.get_filtered_story_map()
        return {scope: {filter: 'Open Panel', storyMap: filteredStoryMap}}
     return scopeJSON
  -> this.scopeJSON = filteredData.scope
  -> storyGraphView: StoryGraphTabView = new StoryGraphTabView(filteredData.scope.storyMap, this.cliClient)
  -> html: String = storyGraphView.render()
  -> document.getElementById('scope-display').innerHTML = html
  return
```

**Validation Result**: Model supports this scenario
**Gaps Found**: None
**Recommendations**: None

---

### Scenario 7: Display Clarify Instructions

**Purpose**: When current action is clarify, panel displays ClarifyInstructionsSection with key questions in editable textareas, user edits answer, system saves via CLI
**Concepts Traced**: ClarifyInstructionsSection

**Scope**: Invoke Bot Through Panel.Display Instructions.Display Clarify Instructions


#### Walk Throughs

**Walk 1 - Covers**: Rendering clarify-specific instructions from JSON

```
InstructionsSection.create(instructionsJSON, actionJSON, cliClient)
  -> actionType: String = actionJSON.type
  -> section: InstructionsSection = this.create_section_for_type(actionType, instructionsJSON, actionJSON, cliClient)
     -> section: ClarifyInstructionsSection = new ClarifyInstructionsSection(instructionsJSON, actionJSON, cliClient)
        -> this.keyQuestionsJSON = instructionsJSON.clarify.key_questions
        -> this.cliClient = cliClient
     return section
html: String = section.render()
  -> baseHTML: String = this.renderBase()
     return `<div>${this.instructionsJSON.behavior_name}.${this.actionJSON.name}</div>`
  -> questionsHTML: String = this.render_all_questions()
     return questionsHTML: "<div class='question'>...</div>..."
  return `${baseHTML}${questionsHTML}`
```

**Walk 2 - Covers**: User edits answer and saves via CLI

```
ClarifyInstructionsSection.onAnswerChange(questionId, newAnswer)
  -> question: Object = this.get_question_by_id(questionId)
  -> result: JSON = this.cliClient.execute(`update_answer "${question.question}" "${newAnswer}"`)
     -> cli:  = spawn('python', ['repl_main.py'])
     -> stdin.write('update_answer ...')
     -> Bot.update_question_answer(question, newAnswer)
        -> clarificationFile: Path = behavior.get_clarification_file()
        -> this.persist_clarification_answer(clarificationFile, question, newAnswer)
        return {status: 'saved', question: question, answer: newAnswer}
     return resultJSON
  -> question.answer = newAnswer
  return
```

**Validation Result**: Model supports this scenario
**Gaps Found**: None
**Recommendations**: None

---

