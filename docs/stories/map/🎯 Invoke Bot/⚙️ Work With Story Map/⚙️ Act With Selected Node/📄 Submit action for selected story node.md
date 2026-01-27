# 📄 Submit action for selected story node

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py#L22)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Work With Story Map](..) / [⚙️ Act With Selected Node](.)  
**Sequential Order:** 1.0
**Story Type:** user

## Story Description

Submit action for selected story node functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-determine-behavior-for-story-and-get-instructions"></a>
### Scenario: [Determine Behavior For Story And Get Instructions](#scenario-determine-behavior-for-story-and-get-instructions) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py#L173)

**Steps:**
```gherkin
Given Bot has story map loaded with epic <epic_name>
And Epic contains story <story_name>
And Story has acceptance criteria <acceptance_criteria>
And Story has scenarios <scenarios>
And Story has test class <test_class>
And Story has test methods <test_methods>
When Bot determines behavior for the story
Then Bot returns behavior <expected_behavior>
When User calls story.get_required_behavior_instructions with action <action>
Then Bot is set to behavior <expected_behavior>
And Bot is set to action <action>
And Instructions for <expected_behavior> behavior and <action> action are returned
And Instructions contain required sections for <expected_behavior> behavior
```

**Examples:**
| epic_name | story_name | test_class | acceptance_criteria | expected_behavior | action | expected_instructions_contain | scenario | test_method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| File Management | Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code | build | code behavior; build action; file upload functionality; implement production code | User uploads valid file and sees success confirmation | test_user_uploads_valid_file_and_sees_success_confirmation |
| File Management | Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code | build | code behavior; build action; file upload functionality; implement production code | User uploads oversized file and sees size limit error | test_user_uploads_oversized_file_and_sees_size_limit_error |
| File Management | Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code | build | code behavior; build action; file upload functionality; implement production code | User uploads invalid file type and sees type error | test_user_uploads_invalid_file_type_and_sees_type_error |
| File Management | Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code | build | code behavior; build action; file upload functionality; implement production code | User cancels upload mid-transfer and sees cancellation confirmation | test_user_cancels_upload_mid_transfer_and_sees_cancellation_confirmation |
| File Management | Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code | build | code behavior; build action; file upload functionality; implement production code | Upload fails with network error and user sees retry option | test_upload_fails_with_network_error_and_user_sees_retry_option |
| File Management | Download File | test_file_download.py | Download initiated; Progress displayed | test | build | test behavior; build action; file download test coverage; implement test methods for scenarios | User downloads file successfully and sees progress | test_user_downloads_file_successfully_and_sees_progress |
| File Management | Download File | test_file_download.py | Download initiated; Progress displayed | test | build | test behavior; build action; file download test coverage; implement test methods for scenarios | User cancels download mid-transfer | test_user_cancels_download_mid_transfer |
| File Management | Download File | test_file_download.py | Download initiated; Progress displayed | test | build | test behavior; build action; file download test coverage; implement test methods for scenarios | Download fails due to network error and user sees error message |  |
| File Management | Delete File | test_file_delete.py | Confirmation required; File removed from storage | test | validate | test behavior; validate action; file deletion test coverage; verify test implementation | User confirms delete and file is removed from system |  |
| File Management | Delete File | test_file_delete.py | Confirmation required; File removed from storage | test | validate | test behavior; validate action; file deletion test coverage; verify test implementation | User cancels delete and file remains |  |
| File Management | Delete File | test_file_delete.py | Confirmation required; File removed from storage | test | validate | test behavior; validate action; file deletion test coverage; verify test implementation | Delete operation fails due to permissions and user sees error |  |
| User Management | Create User |  | Email validated; Password meets requirements | scenario | build | scenario behavior; build action; user creation domain language; write detailed Given/When/Then scenarios |  |  |
| Reporting | View Report |  |  | explore | clarify | explore behavior; clarify action; report viewing concepts; add acceptance criteria and domain understanding |  |  |
| Authentication | Reset Password | test_reset_password.py |  | code | validate | code behavior; validate action; password reset functionality; verify implementation meets requirements | User requests password reset and receives reset email | test_user_requests_password_reset_and_receives_reset_email |
| Authentication | Reset Password | test_reset_password.py |  | code | validate | code behavior; validate action; password reset functionality; verify implementation meets requirements | User submits new password meeting requirements and password is updated | test_user_submits_new_password_meeting_requirements_and_password_is_updated |
| Authentication | Reset Password | test_reset_password.py |  | code | validate | code behavior; validate action; password reset functionality; verify implementation meets requirements | User submits invalid password not meeting requirements and sees validation error | test_user_submits_invalid_password_not_meeting_requirements_and_sees_validation_error |
| Data Export | Export CSV | test_export_csv.py |  | test | clarify | test behavior; clarify action; CSV export test requirements; clarify test expectations | User exports data to CSV and file downloads successfully | test_user_exports_data_to_csv_and_file_downloads_successfully |
| Data Export | Export CSV | test_export_csv.py |  | test | clarify | test behavior; clarify action; CSV export test requirements; clarify test expectations | Export handles empty data set and generates valid empty CSV | test_export_handles_empty_data_set_and_generates_valid_empty_csv |
| Data Export | Export CSV | test_export_csv.py |  | test | clarify | test behavior; clarify action; CSV export test requirements; clarify test expectations | Export handles large dataset and shows progress indicator |  |
| Data Export | Export CSV | test_export_csv.py |  | test | clarify | test behavior; clarify action; CSV export test requirements; clarify test expectations | Export with special characters in data and properly escapes them in CSV |  |
| Payment | Process Payment | test_process_payment.py |  | test | build | test behavior; build action; payment processing test coverage; implement test methods | Payment processed with valid card and transaction completes successfully |  |
| Payment | Process Payment | test_process_payment.py |  | test | build | test behavior; build action; payment processing test coverage; implement test methods | Payment attempted with expired card and user sees card expired error |  |


<a id="scenario-determine-behavior-for-sub-epic"></a>
### Scenario: [Determine Behavior For Sub Epic](#scenario-determine-behavior-for-sub-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py#L441)

**Steps:**
```gherkin
Given Bot has story map loaded with sub-epic <sub_epic_name>
And Sub-epic contains stories shown in table
When Bot determines behavior for the sub-epic
Then Bot returns behavior <expected_behavior>
```

**Examples:**
| example_name | sub_epic | stories |
| --- | --- | --- |
| Example 1: All stories have tests - code behavior | {'columns': ['sub_epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['User Authentication', 'code', 'build', 'code behavior; build action; authentication functionality; implement production code for feature']} | [{'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Login User', 'test_login_user.py', 'Valid credentials accepted; Invalid credentials rejected; Account locked after 3 failures', 'code']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User enters valid username and password and sees dashboard', 'test_user_enters_valid_username_and_password_and_sees_dashboard'], ['User enters invalid password and sees error message', 'test_user_enters_invalid_password_and_sees_error_message'], ['User fails login 3 times and account is locked', 'test_user_fails_login_3_times_and_account_is_locked']]}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Logout User', 'test_logout_user.py', 'Session terminated on logout; User redirected to login page; Auth token invalidated', 'code']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User clicks logout button and session ends', 'test_user_clicks_logout_button_and_session_ends'], ['User clicks logout and is redirected to login', 'test_user_clicks_logout_and_is_redirected_to_login'], ['Logged out user cannot access protected pages', 'test_logged_out_user_cannot_access_protected_pages']]}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Refresh Token', 'test_refresh_token.py', 'Token refreshed before expiry; Expired token triggers re-login; Refresh token rotated after use', 'code']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User with expiring token gets new token automatically', 'test_user_with_expiring_token_gets_new_token_automatically'], ['User with expired token is prompted to login', 'test_user_with_expired_token_is_prompted_to_login'], ['Used refresh token becomes invalid', 'test_used_refresh_token_becomes_invalid']]}}] |
| Example 2: One story needs scenario, sub-epic follows lowest - scenario behavior | {'columns': ['sub_epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Payment Processing', 'scenario', 'validate', 'scenario behavior; validate action; payment processing domain language; verify scenarios are complete']} | [{'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Process Payment', 'test_process_payment.py', 'Card details validated; Payment amount verified; Transaction receipt generated', 'test']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User enters valid card and payment succeeds', ''], ['User enters invalid card number and sees validation error', ''], ['Payment succeeds and receipt is emailed to user', '']]}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Refund Payment', '', 'Original payment verified; Refund amount calculated; Customer notified of refund', 'scenario']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': []}}] |
| Example 3: One story at explore level makes entire sub-epic explore - explore behavior | {'columns': ['sub_epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Data Management', 'explore', 'build', 'explore behavior; build action; data management domain concepts; add stories with acceptance criteria']} | [{'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Import Data', 'test_import_data.py', 'CSV file format validated; Data schema verified; Import progress tracked', 'test']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User uploads valid CSV and data is imported', ''], ['User uploads invalid CSV and sees format error', ''], ['User sees progress bar during import', '']]}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Export Data', '', 'Export format selected; Data filtered before export; Download link generated', 'scenario']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': []}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Validate Data', '', 'Data types checked; Required fields verified; Business rules applied', 'scenario']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': []}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Archive Data', '', '', 'explore']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': []}}] |
| Example 4: Two stories need tests, sub-epic follows lowest - test behavior | {'columns': ['sub_epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['File Operations', 'test', 'clarify', 'test behavior; clarify action; file operations test requirements; clarify test coverage expectations']} | [{'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Upload File', 'test_file_upload.py', 'File size validated; File type checked; Upload progress tracked', 'code']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User uploads valid file and sees success confirmation', 'test_user_uploads_valid_file_and_sees_success_confirmation'], ['User uploads oversized file and sees size limit error', 'test_user_uploads_oversized_file_and_sees_size_limit_error'], ['User uploads invalid file type and sees type error', 'test_user_uploads_invalid_file_type_and_sees_type_error'], ['User cancels upload mid-transfer and sees cancellation confirmation', 'test_user_cancels_upload_mid_transfer_and_sees_cancellation_confirmation'], ['Upload fails with network error and user sees retry option', 'test_upload_fails_with_network_error_and_user_sees_retry_option']]}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Download File', 'test_file_download.py', 'Download initiated; Progress displayed', 'test']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User clicks download and file transfer starts', ''], ['User sees download progress bar', ''], ['Download completes and file appears in downloads folder', '']]}}, {'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Delete File', 'test_file_delete.py', 'Confirmation required; File removed from storage', 'test']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': [['User clicks delete and sees confirmation dialog', ''], ['User confirms deletion and file is removed', ''], ['User sees success message after deletion', '']]}}] |
| Example 5: Single story at scenario level - scenario behavior | {'columns': ['sub_epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Search', 'scenario', 'build', 'scenario behavior; build action; search domain language; write detailed scenarios']} | [{'story': {'columns': ['story_name', 'test_class', 'acceptance_criteria', 'expected_behavior'], 'row': ['Basic Search', '', 'Search term entered; Results displayed; No results message shown when empty', 'scenario']}, 'scenarios': {'columns': ['scenario', 'test_method'], 'rows': []}}] |


<a id="scenario-determine-behavior-for-epic-and-get-instructions"></a>
### Scenario: [Determine Behavior For Epic And Get Instructions](#scenario-determine-behavior-for-epic-and-get-instructions) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py#L877)

**Steps:**
```gherkin
Given Bot has story map loaded with epic <epic_name>
And Epic contains sub-epics shown in table
When Bot determines behavior for the epic
Then Bot returns behavior <expected_behavior>
When User calls epic.get_required_behavior_instructions with action <action>
Then Bot is set to behavior <expected_behavior>
And Bot is set to action <action>
And Instructions for <expected_behavior> behavior and <action> action are returned
And Instructions contain required sections for <expected_behavior> behavior
```

**Examples:**
| example_name | parent | children |
| --- | --- | --- |
| Example 1: All sub-epics at code level - code behavior | {'columns': ['epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['File Management', 'code', 'validate', 'code behavior; validate action; file management functionality; verify implementation is complete']} | {'columns': ['sub_epic_name', 'sub_epic_expected_behavior'], 'rows': [['File Operations', 'code'], ['File Search', 'code']]} |
| Example 2: One sub-epic at explore level makes entire epic explore - explore behavior | {'columns': ['epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Reporting', 'explore', 'clarify', 'explore behavior; clarify action; reporting domain concepts; clarify feature requirements']} | {'columns': ['sub_epic_name', 'sub_epic_expected_behavior'], 'rows': [['Report Generation', 'test'], ['Report Scheduling', 'scenario'], ['Report Export', 'explore']]} |
| Example 3: One sub-epic at scenario level with others at code - scenario behavior | {'columns': ['epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['User Management', 'scenario', 'build', 'scenario behavior; build action; user management domain language; write detailed scenarios']} | {'columns': ['sub_epic_name', 'sub_epic_expected_behavior'], 'rows': [['Authentication', 'code'], ['User Profile', 'scenario']]} |
| Example 4: Multiple sub-epics at test level - test behavior | {'columns': ['epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Payment Processing', 'test', 'build', 'test behavior; build action; payment processing test coverage; implement test methods']} | {'columns': ['sub_epic_name', 'sub_epic_expected_behavior'], 'rows': [['Process Payment', 'test'], ['Refund Payment', 'test']]} |
| Example 5: Empty epic with no sub-epics - shape behavior | {'columns': ['epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Product Catalog', 'shape', 'build', 'shape behavior; build action; product catalog domain concepts; add sub-epics and stories']} | {'columns': ['sub_epic_name', 'sub_epic_expected_behavior'], 'rows': []} |
| Example 6: Epic with nested sub-epics - scenario behavior | {'columns': ['epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Product Management', 'scenario', 'validate', 'scenario behavior; validate action; product management domain language; verify scenarios are complete']} | {'columns': ['sub_epic_name', 'sub_epic_expected_behavior'], 'rows': [['Product Catalog (nested)', 'scenario'], ['Inventory Management', 'code']]} |
| Example 7: Parent sub-epic with nested sub-epics at explore - explore behavior | {'columns': ['epic_name', 'expected_behavior', 'action', 'expected_instructions_contain'], 'row': ['Data Management Epic', 'explore', 'clarify', 'explore behavior; clarify action; data management domain concepts; clarify feature requirements']} | {'columns': ['sub_epic_name', 'sub_epic_expected_behavior'], 'rows': [['Data Management (nested)', 'explore']]} |


<a id="scenario-display-behavior-needed-via-cli-with-json-format"></a>
### Scenario: [Display behavior needed via CLI with JSON format](#scenario-display-behavior-needed-via-cli-with-json-format) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_submit_scoped_action.py#L926)

**Steps:**
```gherkin
Given CLI has story map loaded with <node_type> <epic_name>
When User requests behavior for <epic_name> using JSON format
Then CLI returns JSON with behavior <expected_behavior>
```

**Examples:**
| node_type | epic_name | expected_behavior | action | expected_instructions_contain |
| --- | --- | --- | --- | --- |
| epic | Product Catalog | shape | build | shape behavior; build action; product catalog domain concepts; add sub-epics and stories |


<a id="scenario-panel-submit-button-displays-behavior-specific-icon-and-submits-instructions"></a>
### Scenario: [Panel submit button displays behavior-specific icon and submits instructions](#scenario-panel-submit-button-displays-behavior-specific-icon-and-submits-instructions) (happy_path)

**Steps:**
```gherkin
Given User has selected a <node_type> <node_name> in the panel
And Node has behavior <behavior> needed
When Panel renders the submit button
Then Submit button displays <icon_file> icon indicating <behavior> behavior
When User hovers over the submit button
Then Submit button shows tooltip <tooltip_text>
When User clicks the submit button
Then Panel submits node with action "build"
And Node calls get_required_behavior_instructions with action "build"
And Bot is set to behavior <behavior>
And Bot is set to action "build"
And Instructions for <behavior> behavior and "build" action are returned
```

**Examples:**
| node_type | node_name | behavior | icon_file | tooltip_text |
| --- | --- | --- | --- | --- |
| epic | Product Catalog | shape | submit_subepic.png | Submit shape instructions for epic |
| sub-epic | Report Export | exploration | submit_story.png | Submit exploration instructions for sub-epic |
| story | Create User | scenario | submit_ac.png | Submit scenario instructions for story |
| story | Delete File | test | submit_tests.png | Submit test instructions for story |
| story | Upload File | code | submit_code.png | Submit code instructions for story |

