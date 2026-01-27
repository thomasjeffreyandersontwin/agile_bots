"""
Test Submit Scoped Action

SubEpic: Submit Scoped Action
Parent Epic: Invoke Bot > Edit Story Map

Domain tests verify core scope management logic.
CLI tests verify command parsing and output formatting across TTY, Pipe, and JSON channels.
"""
import pytest
from pathlib import Path
import json
import os
from helpers.bot_test_helper import BotTestHelper
from helpers import TTYBotTestHelper, PipeBotTestHelper, JsonBotTestHelper
from story_graph.nodes import Scenario

# ============================================================================
# DOMAIN TESTS - Core Scope Logic
# ============================================================================

class TestSetScopeToSelectedStoryNodeAndSubmit:
    """
    Story: Set scope to selected story node and submit
    
    Tests the bot's ability to determine what behavior is needed for a story
    based on its completeness state (acceptance criteria, scenarios, tests).
    """
    
    @pytest.mark.parametrize("epic_name,story_name,test_class,acceptance_criteria,scenarios,test_methods,expected_behavior,action,expected_instructions_contain", [
        # All scenarios have tests -> code behavior
        (
            "File Management",
            "Upload File",
            "test_file_upload.py",
            "File size validated; File type checked; Upload progress tracked",
            [
                "User uploads valid file and sees success confirmation",
                "User uploads oversized file and sees size limit error",
                "User uploads invalid file type and sees type error",
                "User cancels upload mid-transfer and sees cancellation confirmation",
                "Upload fails with network error and user sees retry option"
            ],
            [
                "test_user_uploads_valid_file_and_sees_success_confirmation",
                "test_user_uploads_oversized_file_and_sees_size_limit_error",
                "test_user_uploads_invalid_file_type_and_sees_type_error",
                "test_user_cancels_upload_mid_transfer_and_sees_cancellation_confirmation",
                "test_upload_fails_with_network_error_and_user_sees_retry_option"
            ],
            "code",
            "build",
            "code behavior; build action; upload file functionality"
        ),
        # Some scenarios tested -> test behavior
        (
            "File Management",
            "Download File",
            "test_file_download.py",
            "Download initiated; Progress displayed",
            [
                "User downloads file successfully and sees progress",
                "User cancels download mid-transfer",
                "Download fails due to network error and user sees error message"
            ],
            [
                "test_user_downloads_file_successfully_and_sees_progress",
                "test_user_cancels_download_mid_transfer",
                None  # Third scenario has no test
            ],
            "tests",
            "build",
            "tests behavior; build action; download file functionality"
        ),
        # Scenarios exist but no tests -> tests behavior
        (
            "File Management",
            "Delete File",
            "test_file_delete.py",
            "Confirmation required; File removed from storage",
            [
                "User confirms delete and file is removed from system",
                "User cancels delete and file remains",
                "Delete operation fails due to permissions and user sees error"
            ],
            [],
            "tests",
            "validate",
            "tests behavior; validate action; delete file functionality"
        ),
        # Has AC but no scenarios -> scenarios behavior
        (
            "User Management",
            "Create User",
            "",
            "Email validated; Password meets requirements",
            [],
            [],
            "scenarios",
            "build",
            "scenarios behavior; build action; create user functionality"
        ),
        # No AC and no scenarios -> exploration behavior
        (
            "Reporting",
            "View Report",
            "",
            "",
            [],
            [],
            "exploration",
            "clarify",
            "exploration behavior; clarify action; view report functionality"
        ),
        # No AC but scenarios all tested -> code behavior
        (
            "Authentication",
            "Reset Password",
            "test_reset_password.py",
            "",  # No AC
            [
                "User requests password reset and receives reset email",
                "User submits new password meeting requirements and password is updated",
                "User submits invalid password not meeting requirements and sees validation error"
            ],
            [
                "test_user_requests_password_reset_and_receives_reset_email",
                "test_user_submits_new_password_meeting_requirements_and_password_is_updated",
                "test_user_submits_invalid_password_not_meeting_requirements_and_sees_validation_error"
            ],
            "code",
            "validate",
            "code behavior; validate action; reset password functionality"
        ),
        # No AC but some scenarios tested -> tests behavior
        (
            "Data Export",
            "Export CSV",
            "test_export_csv.py",
            "",
            [
                "User exports data to CSV and file downloads successfully",
                "Export handles empty data set and generates valid empty CSV",
                "Export handles large dataset and shows progress indicator",
                "Export with special characters in data and properly escapes them in CSV"
            ],
            [
                "test_user_exports_data_to_csv_and_file_downloads_successfully",
                "test_export_handles_empty_data_set_and_generates_valid_empty_csv",
                None,
                None
            ],
            "tests",
            "clarify",
            "tests behavior; clarify action; export csv functionality"
        ),
        # No AC but scenarios without tests -> tests behavior
        (
            "Payment",
            "Process Payment",
            "test_process_payment.py",
            "",
            [
                "Payment processed with valid card and transaction completes successfully",
                "Payment attempted with expired card and user sees card expired error"
            ],
            [],
            "tests",
            "build",
            "tests behavior; build action; payment processing test coverage; implement test methods"
        ),
    ])
    def test_determine_behavior_for_story_and_get_instructions(
        self,
        tmp_path,
        epic_name,
        story_name,
        test_class,
        acceptance_criteria,
        scenarios,
        test_methods,
        expected_behavior,
        action,
        expected_instructions_contain
    ):
        """
        SCENARIO: Determine Behavior For Story And Get Instructions
        GIVEN: Bot has story map loaded with epic <epic_name>
        AND: Epic contains story <story_name>
        AND: Story has acceptance criteria <acceptance_criteria>
        AND: Story has scenarios <scenarios>
        AND: Story has test class <test_class>
        AND: Story has test methods <test_methods>
        WHEN: Bot determines behavior for the story
        THEN: Bot returns behavior <expected_behavior>
        WHEN: User calls story.get_required_behavior_instructions with action <action>
        THEN: Bot is set to behavior <expected_behavior>
        AND: Bot is set to action <action>
        AND: Instructions for <expected_behavior> behavior and <action> action are returned
        AND: Instructions contain required sections for <expected_behavior> behavior
        
        This test validates the hierarchical logic:
        - If all scenarios have tests -> code behavior
        - If some/no scenarios tested -> test behavior
        - If no scenarios exist -> scenario behavior
        - If no acceptance criteria -> explore behavior
        - Lower level artifacts take precedence (tests > scenarios > AC)
        """
        # Given - Create a test story with the specified state
        helper = BotTestHelper(tmp_path)
        story = helper.story.create_story_with_state_for_behavior_test(
            epic_name,
            story_name,
            test_class,
            acceptance_criteria,
            scenarios,
            test_methods
        )
        
        # When - Bot determines behavior for the story
        actual_behavior = story.behavior_needed
        
        # Then - Bot returns expected behavior
        assert actual_behavior == expected_behavior, (
            f"Expected behavior '{expected_behavior}' but got '{actual_behavior}'"
        )
        
        # When - User calls story.get_required_behavior_instructions with action
        instructions = story.get_required_behavior_instructions(action)
        
        # Then - Bot is set to behavior and action
        assert helper.bot.behaviors.current.name == expected_behavior
        assert helper.bot.behaviors.current.actions.current.action_name == action
        
        # And - Scope is restored to 'all' after getting instructions
        helper.scope.assert_scope_is_cleared()
        
        # And - Instructions object is returned
        from instructions.instructions import Instructions
        assert isinstance(instructions, Instructions), "Should return Instructions object"
        assert instructions.get('behavior_metadata') is not None, "Instructions should have behavior metadata"
        assert instructions.get('action_metadata') is not None, "Instructions should have action metadata"
        assert instructions.get('behavior_metadata')['name'] == expected_behavior
        assert instructions.get('action_metadata')['name'] == action
        
        # And - Instructions contain the scope that was set
        assert instructions.scope is not None, "Instructions should contain scope"
        assert instructions.scope.type.value == 'story', f"Expected scope type 'story', got '{instructions.scope.type.value}'"
        assert story.name in instructions.scope.value, f"Expected story '{story.name}' in scope value {instructions.scope.value}"

    @pytest.mark.parametrize("sub_epic_name,stories_data,expected_behavior,action,expected_instructions_contain", [
        # Example 1: All stories have tests -> code behavior
        (
            "User Authentication",
            [
                {
                    "story_name": "Login User",
                    "test_class": "test_login_user.py",
                    "acceptance_criteria": "Valid credentials accepted; Invalid credentials rejected; Account locked after 3 failures",
                    "scenarios": [
                        "User enters valid username and password and sees dashboard",
                        "User enters invalid password and sees error message",
                        "User fails login 3 times and account is locked"
                    ],
                    "test_methods": [
                        "test_user_enters_valid_username_and_password_and_sees_dashboard",
                        "test_user_enters_invalid_password_and_sees_error_message",
                        "test_user_fails_login_3_times_and_account_is_locked"
                    ]
                },
                {
                    "story_name": "Logout User",
                    "test_class": "test_logout_user.py",
                    "acceptance_criteria": "Session terminated on logout; User redirected to login page; Auth token invalidated",
                    "scenarios": [
                        "User clicks logout button and session ends",
                        "User clicks logout and is redirected to login",
                        "Logged out user cannot access protected pages"
                    ],
                    "test_methods": [
                        "test_user_clicks_logout_button_and_session_ends",
                        "test_user_clicks_logout_and_is_redirected_to_login",
                        "test_logged_out_user_cannot_access_protected_pages"
                    ]
                },
                {
                    "story_name": "Refresh Token",
                    "test_class": "test_refresh_token.py",
                    "acceptance_criteria": "Token refreshed before expiry; Expired token triggers re-login; Refresh token rotated after use",
                    "scenarios": [
                        "User with expiring token gets new token automatically",
                        "User with expired token is prompted to login",
                        "Used refresh token becomes invalid"
                    ],
                    "test_methods": [
                        "test_user_with_expiring_token_gets_new_token_automatically",
                        "test_user_with_expired_token_is_prompted_to_login",
                        "test_used_refresh_token_becomes_invalid"
                    ]
                }
            ],
            "code",
            "build",
            "code behavior; build action; authentication functionality; implement production code for feature"
        ),
        # Example 2: One story needs scenarios, sub-epic follows lowest -> scenarios behavior
        (
            "Payment Processing",
            [
                {
                    "story_name": "Process Payment",
                    "test_class": "test_process_payment.py",
                    "acceptance_criteria": "Card details validated; Payment amount verified; Transaction receipt generated",
                    "scenarios": [
                        "User enters valid card and payment succeeds",
                        "User enters invalid card number and sees validation error",
                        "Payment succeeds and receipt is emailed to user"
                    ],
                    "test_methods": []
                },
                {
                    "story_name": "Refund Payment",
                    "test_class": "",
                    "acceptance_criteria": "Original payment verified; Refund amount calculated; Customer notified of refund",
                    "scenarios": [],
                    "test_methods": []
                }
            ],
            "scenarios",
            "validate",
            "scenarios behavior; validate action; payment processing domain language; verify scenarios are complete"
        ),
        # Example 3: One story at exploration level makes entire sub-epic exploration -> exploration behavior
        (
            "Data Management",
            [
                {
                    "story_name": "Import Data",
                    "test_class": "test_import_data.py",
                    "acceptance_criteria": "CSV file format validated; Data schema verified; Import progress tracked",
                    "scenarios": [
                        "User uploads valid CSV and data is imported",
                        "User uploads invalid CSV and sees format error",
                        "User sees progress bar during import"
                    ],
                    "test_methods": []
                },
                {
                    "story_name": "Export Data",
                    "test_class": "",
                    "acceptance_criteria": "Export format selected; Data filtered before export; Download link generated",
                    "scenarios": [],
                    "test_methods": []
                },
                {
                    "story_name": "Validate Data",
                    "test_class": "",
                    "acceptance_criteria": "Data types checked; Required fields verified; Business rules applied",
                    "scenarios": [],
                    "test_methods": []
                },
                {
                    "story_name": "Archive Data",
                    "test_class": "",
                    "acceptance_criteria": "",
                    "scenarios": [],
                    "test_methods": []
                }
            ],
            "exploration",
            "build",
            "exploration behavior; build action; data management domain concepts; add stories with acceptance criteria"
        ),
        # Example 4: Two stories need tests, sub-epic follows lowest -> tests behavior
        (
            "File Operations",
            [
                {
                    "story_name": "Upload File",
                    "test_class": "test_file_upload.py",
                    "acceptance_criteria": "File size validated; File type checked; Upload progress tracked",
                    "scenarios": [
                        "User uploads valid file and sees success confirmation",
                        "User uploads oversized file and sees size limit error",
                        "User uploads invalid file type and sees type error",
                        "User cancels upload mid-transfer and sees cancellation confirmation",
                        "Upload fails with network error and user sees retry option"
                    ],
                    "test_methods": [
                        "test_user_uploads_valid_file_and_sees_success_confirmation",
                        "test_user_uploads_oversized_file_and_sees_size_limit_error",
                        "test_user_uploads_invalid_file_type_and_sees_type_error",
                        "test_user_cancels_upload_mid_transfer_and_sees_cancellation_confirmation",
                        "test_upload_fails_with_network_error_and_user_sees_retry_option"
                    ]
                },
                {
                    "story_name": "Download File",
                    "test_class": "test_file_download.py",
                    "acceptance_criteria": "Download initiated; Progress displayed",
                    "scenarios": [
                        "User clicks download and file transfer starts",
                        "User sees download progress bar",
                        "Download completes and file appears in downloads folder"
                    ],
                    "test_methods": []
                },
                {
                    "story_name": "Delete File",
                    "test_class": "test_file_delete.py",
                    "acceptance_criteria": "Confirmation required; File removed from storage",
                    "scenarios": [
                        "User clicks delete and sees confirmation dialog",
                        "User confirms deletion and file is removed",
                        "User sees success message after deletion"
                    ],
                    "test_methods": []
                }
            ],
            "tests",
            "clarify",
            "tests behavior; clarify action; file operations test requirements; clarify test coverage expectations"
        ),
        # Example 5: Single story at scenarios level -> scenarios behavior
        (
            "Search",
            [
                {
                    "story_name": "Basic Search",
                    "test_class": "",
                    "acceptance_criteria": "Search term entered; Results displayed; No results message shown when empty",
                    "scenarios": [],
                    "test_methods": []
                }
            ],
            "scenarios",
            "build",
            "scenarios behavior; build action; search domain language; write detailed scenarios"
        ),
    ])
    def test_determine_behavior_for_sub_epic_and_get_instructions(self, tmp_path, sub_epic_name, stories_data, expected_behavior, action, expected_instructions_contain):
        """
        SCENARIO: Determine Behavior For Sub Epic And Get Instructions
        GIVEN: Bot has story map loaded with sub-epic <sub_epic_name>
        AND: Sub-epic contains stories shown in table
        WHEN: Bot determines behavior for the sub-epic
        THEN: Bot returns behavior <expected_behavior>
        WHEN: User calls sub_epic.get_required_behavior_instructions with action <action>
        THEN: Bot is set to behavior <expected_behavior>
        AND: Bot is set to action <action>
        AND: Instructions for <expected_behavior> behavior and <action> action are returned
        AND: Instructions contain required sections for <expected_behavior> behavior
        
        This test validates the hierarchical degradation logic:
        - Sub-epic checks first story for its behavior
        - For each subsequent story, checks at degraded level
        - Returns the lowest behavior needed across all stories
        """
        # Given - Create a test sub-epic with multiple stories
        helper = BotTestHelper(tmp_path)
        sub_epic = helper.story.create_sub_epic_with_stories_for_behavior_test(sub_epic_name, stories_data)
        
        # When - Bot determines behavior for the sub-epic
        actual_behavior = sub_epic.behavior_needed
        
        # Then - Bot returns expected behavior
        assert actual_behavior == expected_behavior, (
            f"Expected behavior '{expected_behavior}' but got '{actual_behavior}' "
            f"for sub-epic '{sub_epic_name}' with {len(stories_data)} stories"
        )
        
        # When - User calls sub_epic.get_required_behavior_instructions with action
        instructions = sub_epic.get_required_behavior_instructions(action)
        
        # Then - Bot is set to behavior and action
        assert helper.bot.behaviors.current.name == expected_behavior
        assert helper.bot.behaviors.current.actions.current.action_name == action
        
        # And - Scope is restored to 'all' after getting instructions
        helper.scope.assert_scope_is_cleared()
        
        # And - Instructions object is returned
        from instructions.instructions import Instructions
        assert isinstance(instructions, Instructions), "Should return Instructions object"
        assert instructions.get('behavior_metadata') is not None, "Instructions should have behavior metadata"
        assert instructions.get('action_metadata') is not None, "Instructions should have action metadata"
        assert instructions.get('behavior_metadata')['name'] == expected_behavior
        assert instructions.get('action_metadata')['name'] == action

    @pytest.mark.parametrize("scenario_name,test_method,expected_behavior", [
        # Scenario with test method -> code behavior
        (
            "User uploads valid file and sees success confirmation",
            "test_user_uploads_valid_file_and_sees_success_confirmation",
            "code"
        ),
        # Scenario without test method -> tests behavior
        (
            "User downloads file successfully and sees progress",
            None,
            "tests"
        ),
        # Scenario with empty test method -> tests behavior
        (
            "User deletes file and sees confirmation",
            None,
            "tests"
        ),
    ])
    def test_determine_behavior_for_scenario(
        self,
        scenario_name,
        test_method,
        expected_behavior
    ):
        """
        SCENARIO: Determine Behavior For Scenario
        GIVEN: Scenario <scenario_name> with test method <test_method>
        WHEN: Bot determines behavior for the scenario
        THEN: Bot returns behavior <expected_behavior>
        
        This test validates the scenario-level logic:
        - If scenario has test_method -> code behavior
        - If scenario has no test_method -> test behavior
        """
        # Given - Create a scenario with the specified state
        scenario = Scenario(
            name=scenario_name,
            sequential_order=1.0,
            type="happy_path",
            background=[],
            test_method=test_method,
            _parent=None
        )
        
        # When - Bot determines behavior for the scenario
        actual_behavior = scenario.behavior_needed
        
        # Then - Bot returns expected behavior
        assert actual_behavior == expected_behavior, (
            f"Expected behavior '{expected_behavior}' but got '{actual_behavior}'"
        )

    @pytest.mark.parametrize("epic_name,sub_epics_data,expected_behavior,action,expected_instructions_contain", [
        # Example 1: All sub-epics have code behavior -> code behavior
        (
            "File Management",
            [
                {
                    "name": "File Operations",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Upload File",
                            "test_class": "test_file_upload.py",
                            "acceptance_criteria": "File size validated; File type checked; Upload progress tracked",
                            "scenarios": [
                                "User uploads valid file and sees success confirmation",
                                "User uploads oversized file and sees size limit error",
                                "User uploads invalid file type and sees type error"
                            ],
                            "test_methods": [
                                "test_user_uploads_valid_file_and_sees_success_confirmation",
                                "test_user_uploads_oversized_file_and_sees_size_limit_error",
                                "test_user_uploads_invalid_file_type_and_sees_type_error"
                            ]
                        },
                        {
                            "story_name": "Download File",
                            "test_class": "test_file_download.py",
                            "acceptance_criteria": "Download initiated; Progress displayed",
                            "scenarios": [
                                "User downloads file successfully and sees progress",
                                "User cancels download mid-transfer",
                                "Download fails due to network error and user sees error message"
                            ],
                            "test_methods": [
                                "test_user_downloads_file_successfully_and_sees_progress",
                                "test_user_cancels_download_mid_transfer",
                                "test_download_fails_due_to_network_error_and_user_sees_error_message"
                            ]
                        }
                    ]
                },
                {
                    "name": "File Search",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Search by Name",
                            "test_class": "test_search_by_name.py",
                            "acceptance_criteria": "Search term validated; Results sorted by relevance; Partial matches included",
                            "scenarios": [
                                "User searches for file name and sees matching results",
                                "User searches with partial name and sees partial matches",
                                "User searches nonexistent file and sees no results message"
                            ],
                            "test_methods": [
                                "test_user_searches_for_file_name_and_sees_matching_results",
                                "test_user_searches_with_partial_name_and_sees_partial_matches",
                                "test_user_searches_nonexistent_file_and_sees_no_results_message"
                            ]
                        }
                    ]
                }
            ],
            "code",
            "validate",
            "code behavior; validate action; file management functionality; verify implementation is complete"
        ),
        # Example 2: One sub-epic at exploration level -> exploration behavior (highest wins)
        (
            "Reporting",
            [
                {
                    "name": "Report Generation",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Generate Sales Report",
                            "test_class": "test_generate_sales_report.py",
                            "acceptance_criteria": "Date range validated; Data aggregated; Report formatted",
                            "scenarios": [
                                "User generates report for valid date range and sees report",
                                "User generates report with invalid date range and sees error"
                            ],
                            "test_methods": []
                        }
                    ]
                },
                {
                    "name": "Report Scheduling",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Schedule Report",
                            "test_class": None,
                            "acceptance_criteria": "Schedule time validated; Recipients specified; Report sent at scheduled time",
                            "scenarios": [],
                            "test_methods": []
                        }
                    ]
                },
                {
                    "name": "Report Export",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Export to PDF",
                            "test_class": None,
                            "acceptance_criteria": "",
                            "scenarios": [],
                            "test_methods": []
                        }
                    ]
                }
            ],
            "exploration",
            "clarify",
            "exploration behavior; clarify action; reporting domain concepts; clarify feature requirements"
        ),
        # Example 3: One sub-epic at scenarios level with others at code -> scenarios behavior
        (
            "User Management",
            [
                {
                    "name": "Authentication",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Login User",
                            "test_class": "test_login_user.py",
                            "acceptance_criteria": "Valid credentials accepted; Invalid credentials rejected; Account locked after 3 failures",
                            "scenarios": [
                                "User enters valid username and password and sees dashboard",
                                "User enters invalid password and sees error message",
                                "User fails login 3 times and account is locked"
                            ],
                            "test_methods": [
                                "test_user_enters_valid_username_and_password_and_sees_dashboard",
                                "test_user_enters_invalid_password_and_sees_error_message",
                                "test_user_fails_login_3_times_and_account_is_locked"
                            ]
                        }
                    ]
                },
                {
                    "name": "User Profile",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Update Profile",
                            "test_class": None,
                            "acceptance_criteria": "Profile fields validated; Changes saved to database; Confirmation displayed",
                            "scenarios": [],
                            "test_methods": []
                        }
                    ]
                }
            ],
            "scenarios",
            "build",
            "scenarios behavior; build action; user management domain language; write detailed scenarios"
        ),
        # Example 4: Multiple sub-epics at tests level -> tests behavior
        (
            "Payment Processing",
            [
                {
                    "name": "Process Payment",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Validate Card",
                            "test_class": "test_validate_card.py",
                            "acceptance_criteria": "Card number validated; Expiry date checked; CVV verified",
                            "scenarios": [
                                "User enters valid card and validation passes",
                                "User enters invalid card number and sees error",
                                "User enters expired card and sees expiry error"
                            ],
                            "test_methods": []
                        }
                    ]
                },
                {
                    "name": "Refund Payment",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Issue Refund",
                            "test_class": "test_issue_refund.py",
                            "acceptance_criteria": "Original payment verified; Refund amount calculated; Customer notified",
                            "scenarios": [
                                "Admin issues full refund and customer receives confirmation",
                                "Admin issues partial refund and amount is calculated correctly"
                            ],
                            "test_methods": []
                        }
                    ]
                }
            ],
            "tests",
            "build",
            "tests behavior; build action; payment processing test coverage; implement test methods"
        ),
        # Example 5: Empty epic with no sub-epics -> shape behavior
        (
            "Product Catalog",
            [],  # No sub-epics
            "shape",
            "build",
            "shape behavior; build action; product catalog domain concepts; add sub-epics and stories"
        ),
        # Example 6: Epic with nested sub-epics - parent sub-epic follows highest of nested children
        (
            "Product Management",
            [
                {
                    "name": "Product Catalog",
                    "nested_sub_epics": [
                        {
                            "name": "Category Management",
                            "nested_sub_epics": [],
                            "stories": [
                                {
                                    "story_name": "Create Category",
                                    "test_class": "test_create_category.py",
                                    "acceptance_criteria": "Category name validated; Parent category selected; Category saved",
                                    "scenarios": [
                                        "User creates new category with valid name",
                                        "User creates subcategory under parent category"
                                    ],
                                    "test_methods": [
                                        "test_user_creates_new_category_with_valid_name",
                                        "test_user_creates_subcategory_under_parent_category"
                                    ]
                                }
                            ]
                        },
                        {
                            "name": "Product Search",
                            "nested_sub_epics": [],
                            "stories": [
                                {
                                    "story_name": "Search Products",
                                    "test_class": None,
                                    "acceptance_criteria": "Search term entered; Filters applied; Results displayed",
                                    "scenarios": [],
                                    "test_methods": []
                                }
                            ]
                        }
                    ],
                    "stories": []
                },
                {
                    "name": "Inventory Management",
                    "nested_sub_epics": [],
                    "stories": [
                        {
                            "story_name": "Update Stock",
                            "test_class": "test_update_stock.py",
                            "acceptance_criteria": "Stock quantity validated; Inventory updated; Notification sent",
                            "scenarios": [
                                "Admin updates stock quantity and inventory reflects change"
                            ],
                            "test_methods": [
                                "test_admin_updates_stock_quantity_and_inventory_reflects_change"
                            ]
                        }
                    ]
                }
            ],
            "scenarios",
            "validate",
            "scenarios behavior; validate action; product management domain language; verify scenarios are complete"
        ),
        # Example 7: Parent sub-epic with nested sub-epics -> exploration behavior (highest of nested)
        (
            "Data Management Epic",
            [
                {
                    "name": "Data Management",
                    "nested_sub_epics": [
                        {
                            "name": "Data Import",
                            "nested_sub_epics": [],
                            "stories": [
                                {
                                    "story_name": "Import CSV",
                                    "test_class": "test_import_csv.py",
                                    "acceptance_criteria": "File format validated; Data parsed; Import completed",
                                    "scenarios": [
                                        "User imports valid CSV and data is loaded",
                                        "User imports invalid CSV and sees error"
                                    ],
                                    "test_methods": []
                                }
                            ]
                        },
                        {
                            "name": "Data Validation",
                            "nested_sub_epics": [],
                            "stories": [
                                {
                                    "story_name": "Validate Records",
                                    "test_class": None,
                                    "acceptance_criteria": "Data types checked; Required fields verified; Business rules applied",
                                    "scenarios": [],
                                    "test_methods": []
                                }
                            ]
                        },
                        {
                            "name": "Data Archive",
                            "nested_sub_epics": [],
                            "stories": [
                                {
                                    "story_name": "Archive Old Data",
                                    "test_class": None,
                                    "acceptance_criteria": "",
                                    "scenarios": [],
                                    "test_methods": []
                                }
                            ]
                        }
                    ],
                    "stories": []
                }
            ],
            "exploration",
            "clarify",
            "exploration behavior; clarify action; data management domain concepts; clarify feature requirements"
        ),
    ])
    def test_determine_behavior_for_epic_and_get_instructions(self, tmp_path, epic_name, sub_epics_data, expected_behavior, action, expected_instructions_contain):
        """
        SCENARIO: Determine Behavior For Epic And Get Instructions
        GIVEN: Bot has story map loaded with epic <epic_name>
        AND: Epic contains sub-epics shown in table
        WHEN: Bot determines behavior for the epic
        THEN: Bot returns behavior <expected_behavior>
        WHEN: User calls epic.get_required_behavior_instructions with action <action>
        THEN: Bot is set to behavior <expected_behavior>
        AND: Bot is set to action <action>
        AND: Instructions for <expected_behavior> behavior and <action> action are returned
        AND: Instructions contain required sections for <expected_behavior> behavior
        
        This test validates the hierarchical behavior determination:
        - Epic examines all sub-epics (including nested ones)
        - Returns the HIGHEST behavior found (shape > explore > scenario > test > code)
        - Can stop examining a sub-epic once a behavior at or above current highest is found
        """
        # Given - Create an epic with sub-epics (including nested if specified)
        helper = BotTestHelper(tmp_path)
        epic = helper.story.create_epic_with_sub_epics_for_behavior_test(epic_name, sub_epics_data)
        
        # When - Bot determines behavior for the epic
        actual_behavior = epic.behavior_needed
        
        # Then - Bot returns expected behavior (follows highest across all sub-epics)
        assert actual_behavior == expected_behavior, (
            f"Expected behavior '{expected_behavior}' but got '{actual_behavior}' "
            f"for epic '{epic_name}' with {len(sub_epics_data)} sub-epics"
        )
        
        # When - User calls epic.get_required_behavior_instructions with action
        instructions = epic.get_required_behavior_instructions(action)
        
        # Then - Bot is set to behavior and action
        assert helper.bot.behaviors.current.name == expected_behavior
        assert helper.bot.behaviors.current.actions.current.action_name == action
        
        # And - Scope is restored to 'all' after getting instructions
        helper.scope.assert_scope_is_cleared()
        
        # And - Instructions object is returned
        from instructions.instructions import Instructions
        assert isinstance(instructions, Instructions), "Should return Instructions object"
        assert instructions.get('behavior_metadata') is not None, "Instructions should have behavior metadata"
        assert instructions.get('action_metadata') is not None, "Instructions should have action metadata"
        assert instructions.get('behavior_metadata')['name'] == expected_behavior
        assert instructions.get('action_metadata')['name'] == action

    def test_display_behavior_needed_via_cli_and_get_instructions(self, tmp_path):
        """
        SCENARIO: Display behavior needed via CLI and get instructions
        GIVEN: CLI has story graph with stories at different behavior states
        WHEN: User executes 'scope' command
        THEN: CLI returns JSON with behavior field for each epic, sub-epic, and story
        AND: Behavior values match domain logic (explore/scenario/test/code)
        WHEN: User calls CLI submit command for epic with action "build"
        AND: Node calls get_required_behavior_instructions with action "build"
        THEN: Bot is set to behavior <expected_behavior>
        AND: Bot is set to action "build"
        AND: Instructions for behavior and action are returned
        
        This test validates that behavior_needed is included in CLI JSON output
        and can be used to submit with correct behavior.
        """
        # Given - Create story graph with stories at different behavior states
        helper = JsonBotTestHelper(tmp_path)
        helper.domain.state.set_state('shape', 'clarify')
        
        # Create epic with sub-epic containing stories with different behaviors
        epic_data = {
            "name": "Test Epic",
            "nested_sub_epics": [],
            "stories": [
                # Story with all scenarios tested -> code
                {
                    "story_name": "Story With Tests",
                    "test_class": "test_story.py",
                    "acceptance_criteria": "AC exists",
                    "scenarios": ["Scenario 1"],
                    "test_methods": ["test_scenario_1"]
                },
                # Story with scenarios but no tests -> test
                {
                    "story_name": "Story Needs Tests",
                    "test_class": "test_story.py",
                    "acceptance_criteria": "AC exists",
                    "scenarios": ["Scenario 1"],
                    "test_methods": []
                },
                # Story with AC but no scenarios -> scenario
                {
                    "story_name": "Story Needs Scenarios",
                    "test_class": "",
                    "acceptance_criteria": "AC exists",
                    "scenarios": [],
                    "test_methods": []
                },
                # Story with no AC -> explore
                {
                    "story_name": "Story Needs Exploration",
                    "test_class": "",
                    "acceptance_criteria": "",
                    "scenarios": [],
                    "test_methods": []
                }
            ]
        }
        
        epic = helper.domain.story.create_epic_with_sub_epics_for_behavior_test("Test Epic", [epic_data])
        
        # When - Execute scope command via CLI
        cli_response = helper.cli_session.execute_command('scope showall')
        response_data = json.loads(cli_response.output)
        
        # Then - JSON includes behavior field for all nodes
        assert 'scope' in response_data
        scope_data = response_data['scope']
        assert 'content' in scope_data
        assert 'epics' in scope_data['content']
        
        test_epic = next((e for e in scope_data['content']['epics'] if e['name'] == 'Test Epic'), None)
        assert test_epic is not None, "Test Epic not found in scope output"
        assert 'behavior_needed' in test_epic, "Epic missing 'behavior_needed' field"
        
        # Check sub-epic has behavior_needed
        assert 'sub_epics' in test_epic
        assert len(test_epic['sub_epics']) > 0
        sub_epic = test_epic['sub_epics'][0]
        assert 'behavior_needed' in sub_epic, "Sub-epic missing 'behavior_needed' field"
        
        # Check each story has correct behavior_needed
        stories = sub_epic['story_groups'][0]['stories']
        
        story_with_tests = next(s for s in stories if s['name'] == 'Story With Tests')
        assert 'behavior_needed' in story_with_tests, "Story missing 'behavior_needed' field"
        assert story_with_tests['behavior_needed'] == 'code', f"Expected 'code' but got '{story_with_tests['behavior_needed']}'"
        
        story_needs_tests = next(s for s in stories if s['name'] == 'Story Needs Tests')
        assert 'behavior_needed' in story_needs_tests, "Story missing 'behavior_needed' field"
        assert story_needs_tests['behavior_needed'] == 'tests', f"Expected 'tests' but got '{story_needs_tests['behavior_needed']}'"
        
        story_needs_scenarios = next(s for s in stories if s['name'] == 'Story Needs Scenarios')
        assert 'behavior_needed' in story_needs_scenarios, "Story missing 'behavior_needed' field"
        assert story_needs_scenarios['behavior_needed'] == 'scenarios', f"Expected 'scenarios' but got '{story_needs_scenarios['behavior_needed']}'"
        
        story_needs_exploration = next(s for s in stories if s['name'] == 'Story Needs Exploration')
        assert 'behavior_needed' in story_needs_exploration, "Story missing 'behavior_needed' field"
        assert story_needs_exploration['behavior_needed'] == 'exploration', f"Expected 'exploration' but got '{story_needs_exploration['behavior_needed']}'"
        
        # When - User calls CLI submit command for epic with action "build"
        # (Using the epic's behavior_needed which should be 'explore' based on highest behavior)
        expected_behavior = test_epic['behavior_needed']
        action = 'build'
        
        # Get instructions using the domain method
        instructions = epic.get_required_behavior_instructions(action)
        
        # Then - Bot is set to behavior and action
        assert helper.domain.bot.behaviors.current.name == expected_behavior
        assert helper.domain.bot.behaviors.current.actions.current.action_name == action
        
        # And - Instructions object is returned
        from instructions.instructions import Instructions
        assert isinstance(instructions, Instructions), "Should return Instructions object"
        
        # Format instructions using JSON formatter for CLI
        from instructions.json_instructions import JSONInstructions
        formatter = JSONInstructions(instructions)
        instructions_dict = formatter.to_dict()
        
        assert instructions_dict is not None, "Instructions dict should not be None"
        assert 'behavior_metadata' in instructions_dict
        assert 'action_metadata' in instructions_dict
        assert instructions_dict['behavior_metadata']['name'] == expected_behavior
        assert instructions_dict['action_metadata']['name'] == action

