# 📄 Set scope to selected story node and submit

**Navigation:** [📄‹ Story Map](../../../../story-map.drawio) | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L203)

**User:** System
**Path:** [🎯 Invoke Bot](../..) / [⚙️ Edit Story Map](..) / [⚙️ Filter Scope](../..) / [⚙️ Scope Stories](..) / [⚙️ Manage Story Scope](.)  
**Sequential Order:** 8.0
**Story Type:** user

## Story Description

Set scope to selected story node and submit functionality for the mob minion system.

## Acceptance Criteria

### Behavioral Acceptance Criteria

- **When** action executes, **then** action completes successfully

## Scenarios

<a id="scenario-determine-behavior-for-story"></a>
### Scenario: [Determine Behavior For Story](#scenario-determine-behavior-for-story) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L338)

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
```

**Example 1: Story with all scenarios tested → code behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| File Management | Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User uploads valid file and sees success confirmation | test_user_uploads_valid_file_and_sees_success_confirmation |
| User uploads oversized file and sees size limit error | test_user_uploads_oversized_file_and_sees_size_limit_error |
| User uploads invalid file type and sees type error | test_user_uploads_invalid_file_type_and_sees_type_error |
| User cancels upload mid-transfer and sees cancellation confirmation | test_user_cancels_upload_mid_transfer_and_sees_cancellation_confirmation |
| Upload fails with network error and user sees retry option | test_upload_fails_with_network_error_and_user_sees_retry_option |

---

**Example 2: Story with some scenarios tested → test behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| File Management | Download File | test_file_download.py | Download initiated; Progress displayed | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User downloads file successfully and sees progress | test_user_downloads_file_successfully_and_sees_progress |
| User cancels download mid-transfer | test_user_cancels_download_mid_transfer |
| Download fails due to network error and user sees error message |  |

---

**Example 3: Story with scenarios but no tests → test behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| File Management | Delete File | test_file_delete.py | Confirmation required; File removed from storage | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User confirms delete and file is removed from system |  |
| User cancels delete and file remains |  |
| Delete operation fails due to permissions and user sees error |  |

---

**Example 4: Story with AC but no scenarios → scenario behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| User Management | Create User |  | Email validated; Password meets requirements | scenario |

---

**Example 5: Story with no AC and no scenarios → explore behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| Reporting | View Report |  |  | explore |

---

**Example 6: Story with no AC but scenarios all tested → code behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| Authentication | Reset Password | test_reset_password.py |  | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User requests password reset and receives reset email | test_user_requests_password_reset_and_receives_reset_email |
| User submits new password meeting requirements and password is updated | test_user_submits_new_password_meeting_requirements_and_password_is_updated |
| User submits invalid password not meeting requirements and sees validation error | test_user_submits_invalid_password_not_meeting_requirements_and_sees_validation_error |

---

**Example 7: Story with no AC but some scenarios tested → test behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| Data Export | Export CSV | test_export_csv.py |  | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User exports data to CSV and file downloads successfully | test_user_exports_data_to_csv_and_file_downloads_successfully |
| Export handles empty data set and generates valid empty CSV | test_export_handles_empty_data_set_and_generates_valid_empty_csv |
| Export handles large dataset and shows progress indicator |  |
| Export with special characters in data and properly escapes them in CSV |  |

---

**Example 8: Story with no AC but scenarios with no tests → test behavior**

| epic_name | story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- | --- |
| Payment | Process Payment | test_process_payment.py |  | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| Payment processed with valid card and transaction completes successfully |  |
| Payment attempted with expired card and user sees card expired error |  |


<a id="scenario-determine-behavior-for-sub-epic"></a>
### Scenario: [Determine Behavior For Sub Epic](#scenario-determine-behavior-for-sub-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L566)

**Steps:**
```gherkin
Given Bot has story map loaded with sub-epic <sub_epic_name>
And Sub-epic contains stories shown in table
When Bot determines behavior for the sub-epic
Then Bot returns behavior <expected_behavior>
```

**Example 1: All stories have tests → code behavior**

| sub_epic_name | expected_behavior |
| --- | --- |
| User Authentication | code |

**Story: Login User**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Login User | test_login_user.py | Valid credentials accepted; Invalid credentials rejected; Account locked after 3 failures | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User enters valid username and password and sees dashboard | test_user_enters_valid_username_and_password_and_sees_dashboard |
| User enters invalid password and sees error message | test_user_enters_invalid_password_and_sees_error_message |
| User fails login 3 times and account is locked | test_user_fails_login_3_times_and_account_is_locked |

**Story: Logout User**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Logout User | test_logout_user.py | Session terminated on logout; User redirected to login page; Auth token invalidated | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User clicks logout button and session ends | test_user_clicks_logout_button_and_session_ends |
| User clicks logout and is redirected to login | test_user_clicks_logout_and_is_redirected_to_login |
| Logged out user cannot access protected pages | test_logged_out_user_cannot_access_protected_pages |

**Story: Refresh Token**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Refresh Token | test_refresh_token.py | Token refreshed before expiry; Expired token triggers re-login; Refresh token rotated after use | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User with expiring token gets new token automatically | test_user_with_expiring_token_gets_new_token_automatically |
| User with expired token is prompted to login | test_user_with_expired_token_is_prompted_to_login |
| Used refresh token becomes invalid | test_used_refresh_token_becomes_invalid |

---

**Example 2: One story needs scenario, sub-epic follows lowest → scenario behavior**

| sub_epic_name | expected_behavior |
| --- | --- |
| Payment Processing | scenario |

**Story: Process Payment**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Process Payment | test_process_payment.py | Card details validated; Payment amount verified; Transaction receipt generated | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User enters valid card and payment succeeds |  |
| User enters invalid card number and sees validation error |  |
| Payment succeeds and receipt is emailed to user |  |

**Story: Refund Payment**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Refund Payment |  | Original payment verified; Refund amount calculated; Customer notified of refund | scenario |

---

**Example 3: One story at explore level makes entire sub-epic explore → explore behavior**

| sub_epic_name | expected_behavior |
| --- | --- |
| Data Management | explore |

**Story: Import Data**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Import Data | test_import_data.py | CSV file format validated; Data schema verified; Import progress tracked | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User uploads valid CSV and data is imported |  |
| User uploads invalid CSV and sees format error |  |
| User sees progress bar during import |  |

**Story: Export Data**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Export Data |  | Export format selected; Data filtered before export; Download link generated | scenario |

**Story: Validate Data**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Validate Data |  | Data types checked; Required fields verified; Business rules applied | scenario |

**Story: Archive Data**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Archive Data |  |  | explore |

---

**Example 4: Two stories need tests, sub-epic follows lowest → test behavior**

| sub_epic_name | expected_behavior |
| --- | --- |
| File Operations | test |

**Story: Upload File**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User uploads valid file and sees success confirmation | test_user_uploads_valid_file_and_sees_success_confirmation |
| User uploads oversized file and sees size limit error | test_user_uploads_oversized_file_and_sees_size_limit_error |
| User uploads invalid file type and sees type error | test_user_uploads_invalid_file_type_and_sees_type_error |
| User cancels upload mid-transfer and sees cancellation confirmation | test_user_cancels_upload_mid_transfer_and_sees_cancellation_confirmation |
| Upload fails with network error and user sees retry option | test_upload_fails_with_network_error_and_user_sees_retry_option |

**Story: Download File**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Download File | test_file_download.py | Download initiated; Progress displayed | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User clicks download and file transfer starts |  |
| User sees download progress bar |  |
| Download completes and file appears in downloads folder |  |

**Story: Delete File**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Delete File | test_file_delete.py | Confirmation required; File removed from storage | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User clicks delete and sees confirmation dialog |  |
| User confirms deletion and file is removed |  |
| User sees success message after deletion |  |

---

**Example 5: Single story at scenario level → scenario behavior**

| sub_epic_name | expected_behavior |
| --- | --- |
| Search | scenario |

**Story: Basic Search**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Basic Search |  | Search term entered; Results displayed; No results message shown when empty | scenario |


<a id="scenario-determine-behavior-for-epic"></a>
### Scenario: [Determine Behavior For Epic](#scenario-determine-behavior-for-epic) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L998)

**Steps:**
```gherkin
Given Bot has story map loaded with epic <epic_name>
And Epic contains sub-epics shown in table
When Bot determines behavior for the epic
Then Bot returns behavior <expected_behavior>
```

**Example 1: All sub-epics have code behavior → code behavior**

| epic_name | expected_behavior |
| --- | --- |
| File Management | code |

**Sub-Epic: File Operations**
| sub_epic_name | expected_behavior |
| --- | --- |
| File Operations | code |

**Story: Upload File**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Upload File | test_file_upload.py | File size validated; File type checked; Upload progress tracked | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User uploads valid file and sees success confirmation | test_user_uploads_valid_file_and_sees_success_confirmation |
| User uploads oversized file and sees size limit error | test_user_uploads_oversized_file_and_sees_size_limit_error |
| User uploads invalid file type and sees type error | test_user_uploads_invalid_file_type_and_sees_type_error |

**Story: Download File**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Download File | test_file_download.py | Download initiated; Progress displayed | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User downloads file successfully and sees progress | test_user_downloads_file_successfully_and_sees_progress |
| User cancels download mid-transfer | test_user_cancels_download_mid_transfer |
| Download fails due to network error and user sees error message | test_download_fails_due_to_network_error_and_user_sees_error_message |

**Sub-Epic: File Search**
| sub_epic_name | expected_behavior |
| --- | --- |
| File Search | code |

**Story: Search by Name**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Search by Name | test_search_by_name.py | Search term validated; Results sorted by relevance; Partial matches included | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User searches for file name and sees matching results | test_user_searches_for_file_name_and_sees_matching_results |
| User searches with partial name and sees partial matches | test_user_searches_with_partial_name_and_sees_partial_matches |
| User searches nonexistent file and sees no results message | test_user_searches_nonexistent_file_and_sees_no_results_message |

---

**Example 2: One sub-epic at explore level, epic follows highest → explore behavior**

| epic_name | expected_behavior |
| --- | --- |
| Reporting | explore |

**Sub-Epic: Report Generation**
| sub_epic_name | expected_behavior |
| --- | --- |
| Report Generation | test |

**Story: Generate Sales Report**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Generate Sales Report | test_generate_sales_report.py | Date range validated; Data aggregated; Report formatted | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User generates report for valid date range and sees report |  |
| User generates report with invalid date range and sees error |  |

**Sub-Epic: Report Scheduling**
| sub_epic_name | expected_behavior |
| --- | --- |
| Report Scheduling | scenario |

**Story: Schedule Report**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Schedule Report |  | Schedule time validated; Recipients specified; Report sent at scheduled time | scenario |

**Sub-Epic: Report Export**
| sub_epic_name | expected_behavior |
| --- | --- |
| Report Export | explore |

**Story: Export to PDF**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Export to PDF |  |  | explore |

---

**Example 3: One sub-epic at scenario level with others at code, epic follows highest → scenario behavior**

| epic_name | expected_behavior |
| --- | --- |
| User Management | scenario |

**Sub-Epic: Authentication**
| sub_epic_name | expected_behavior |
| --- | --- |
| Authentication | code |

**Story: Login User**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Login User | test_login_user.py | Valid credentials accepted; Invalid credentials rejected; Account locked after 3 failures | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User enters valid username and password and sees dashboard | test_user_enters_valid_username_and_password_and_sees_dashboard |
| User enters invalid password and sees error message | test_user_enters_invalid_password_and_sees_error_message |
| User fails login 3 times and account is locked | test_user_fails_login_3_times_and_account_is_locked |

**Sub-Epic: User Profile**
| sub_epic_name | expected_behavior |
| --- | --- |
| User Profile | scenario |

**Story: Update Profile**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Update Profile |  | Profile fields validated; Changes saved to database; Confirmation displayed | scenario |

---

**Example 4: Multiple sub-epics at test level → test behavior**

| epic_name | expected_behavior |
| --- | --- |
| Payment Processing | test |

**Sub-Epic: Process Payment**
| sub_epic_name | expected_behavior |
| --- | --- |
| Process Payment | test |

**Story: Validate Card**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Validate Card | test_validate_card.py | Card number validated; Expiry date checked; CVV verified | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User enters valid card and validation passes |  |
| User enters invalid card number and sees error |  |
| User enters expired card and sees expiry error |  |

**Sub-Epic: Refund Payment**
| sub_epic_name | expected_behavior |
| --- | --- |
| Refund Payment | test |

**Story: Issue Refund**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Issue Refund | test_issue_refund.py | Original payment verified; Refund amount calculated; Customer notified | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| Admin issues full refund and customer receives confirmation |  |
| Admin issues partial refund and amount is calculated correctly |  |

---

**Example 5: Empty epic with no sub-epics → shape behavior**

| epic_name | expected_behavior |
| --- | --- |
| Product Catalog | shape |

*(No sub-epics defined)*

---

**Example 6: Epic with nested sub-epics - parent sub-epic follows highest of nested children → scenario behavior**

| epic_name | expected_behavior |
| --- | --- |
| Product Management | scenario |

**Sub-Epic: Product Catalog** (contains nested sub-epics)
| sub_epic_name | expected_behavior |
| --- | --- |
| Product Catalog | scenario |

**Nested Sub-Epic: Category Management**
| sub_epic_name | expected_behavior |
| --- | --- |
| Category Management | code |

**Story: Create Category**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Create Category | test_create_category.py | Category name validated; Parent category selected; Category saved | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User creates new category with valid name | test_user_creates_new_category_with_valid_name |
| User creates subcategory under parent category | test_user_creates_subcategory_under_parent_category |

**Nested Sub-Epic: Product Search**
| sub_epic_name | expected_behavior |
| --- | --- |
| Product Search | scenario |

**Story: Search Products**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Search Products |  | Search term entered; Filters applied; Results displayed | scenario |

**Sub-Epic: Inventory Management** (direct child of epic, not nested)
| sub_epic_name | expected_behavior |
| --- | --- |
| Inventory Management | code |

**Story: Update Stock**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Update Stock | test_update_stock.py | Stock quantity validated; Inventory updated; Notification sent | code |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| Admin updates stock quantity and inventory reflects change | test_admin_updates_stock_quantity_and_inventory_reflects_change |

---

**Example 7: Parent sub-epic with nested sub-epics (no epic context) → explore behavior**

| sub_epic_name | expected_behavior |
| --- | --- |
| Data Management | explore |

**Nested Sub-Epic: Data Import**
| sub_epic_name | expected_behavior |
| --- | --- |
| Data Import | test |

**Story: Import CSV**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Import CSV | test_import_csv.py | File format validated; Data parsed; Import completed | test |

**Scenario to Test Method Mapping:**
| scenario | test_method |
| --- | --- |
| User imports valid CSV and data is loaded |  |
| User imports invalid CSV and sees error |  |

**Nested Sub-Epic: Data Validation**
| sub_epic_name | expected_behavior |
| --- | --- |
| Data Validation | scenario |

**Story: Validate Records**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Validate Records |  | Data types checked; Required fields verified; Business rules applied | scenario |

**Nested Sub-Epic: Data Archive**
| sub_epic_name | expected_behavior |
| --- | --- |
| Data Archive | explore |

**Story: Archive Old Data**
| story_name | test_class | acceptance_criteria | expected_behavior |
| --- | --- | --- | --- |
| Archive Old Data |  |  | explore |


<a id="scenario-panel-submit-button-displays-behavior-specific-icon-with-hover-tooltip"></a>
### Scenario: [Panel submit button displays behavior-specific icon with hover tooltip](#scenario-panel-submit-button-displays-behavior-specific-icon-with-hover-tooltip) (happy_path)

**Steps:**
```gherkin
Given User has selected a <node_type> <node_name> in the panel
And Node has behavior <behavior> needed
When Panel renders the submit button
Then Submit button displays <icon_file> icon indicating <behavior> behavior
When User hovers over the submit button
Then Submit button shows tooltip <tooltip_text>
```

**Examples:**
| node_type | node_name | behavior | icon_file | tooltip_text |
| --- | --- | --- | --- | --- |
| epic | Product Catalog | shape | submit_subepic.png | Submit shape instructions for epic |
| sub-epic | Report Export | explore | submit_story.png | Submit explore instructions for sub-epic |
| story | Create User | scenario | submit_ac.png | Submit scenario instructions for story |
| story | Delete File | test | submit_tests.png | Submit test instructions for story |
| story | Upload File | code | submit_code.png | Submit code instructions for story |


<a id="scenario-display-behavior-needed-via-cli-with-json-format"></a>
### Scenario: [Display behavior needed via CLI with JSON format](#scenario-display-behavior-needed-via-cli-with-json-format) (happy_path)  | [Test](/test/invoke_bot/edit_story_map/test_manage_story_scope.py#L1003)

**Steps:**
```gherkin
Given CLI has story map loaded with <node_type> <epic_name>
When User requests behavior for <epic_name> using JSON format
Then CLI returns JSON with behavior <expected_behavior>
```

**Examples:**
| node_type | epic_name | expected_behavior |
| --- | --- | --- |
| epic | Product Catalog | shape |

**Note:** This scenario validates that `behavior_needed` is accessible for JSON formatting. Full behavior determination logic is comprehensively tested in previous scenarios: [Determine Behavior For Story](#scenario-determine-behavior-for-story), [Determine Behavior For Sub Epic](#scenario-determine-behavior-for-sub-epic), and [Determine Behavior For Epic](#scenario-determine-behavior-for-epic).
