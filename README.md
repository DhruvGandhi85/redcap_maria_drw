<!-- markdownlint-disable -->

# API Overview

## Modules

- [`redcom_API`](./redcom_API.md#module-redcom_api)
- [`app`](./app.md#module-app)

## Classes

- No classes

## Functions

- [`redcom_API.check_drw_enabled`](./redcom_API.md#function-check_drw_enabled): Checks if the data resolution workflow parameter is enabled for the projects in the list.
- [`redcom_API.check_existing_drw_entry`](./redcom_API.md#function-check_existing_drw_entry): Searches redcap_data_quality_status table to see if a DRW entry exists for that record already. 
- [`redcom_API.check_for_all_missing`](./redcom_API.md#function-check_for_all_missing): Checks for all missing data entries in the data dictionary and sends an email if the number of entries exceeds the alert threshold.
- [`redcom_API.check_for_all_outlier_and_missing`](./redcom_API.md#function-check_for_all_outlier_and_missing): Checks for all missing data entries and outlier data in the data dictionary and sends an email if the number of entries exceeds the alert threshold.
- [`redcom_API.check_for_all_outliers`](./redcom_API.md#function-check_for_all_outliers): Checks for all missing data entries in the data dictionary and sends an email if the number of entries exceeds the alert threshold.
- [`redcom_API.check_for_confirmed_correct_fields`](./redcom_API.md#function-check_for_confirmed_correct_fields): Checks the data dictionary for fields that have been confirmed correct in the redcap_data_quality_status and redcap_data_quality_resolutions tables.
- [`redcom_API.check_last_run`](./redcom_API.md#function-check_last_run): Checks the last time the outlier and missing data routine was run. If it was more than n hours ago, sends an email to the administrator.
- [`redcom_API.connect_to_maria`](./redcom_API.md#function-connect_to_maria): Establishes a connection to the mariaDB server.
- [`redcom_API.create_data_res_workflow_entry`](./redcom_API.md#function-create_data_res_workflow_entry): Creates a new data entry in the redcap_data_quality_status and redcap_data_quality_resolutions tables.
- [`redcom_API.create_msg_body`](./redcom_API.md#function-create_msg_body): Creates the message body to be sent to the recipient via the REDCap messenger, including a link to the workflow table.
- [`redcom_API.drop_data_table_triggers`](./redcom_API.md#function-drop_data_table_triggers): Drops triggers for the log_event tables to stop sending data to the Flask server when a new record is created or updated.
- [`redcom_API.drop_log_event_triggers`](./redcom_API.md#function-drop_log_event_triggers): Drops triggers for the log_event tables to stop sending data to the Flask server when a new record is created or updated.
- [`redcom_API.execute_maria_cmd`](./redcom_API.md#function-execute_maria_cmd): Utilizes a cursor to execute a given SQL command in the mariaDB database. 
- [`redcom_API.filter_data_table`](./redcom_API.md#function-filter_data_table): Prepares the redcap_data table for operations such as joining with log table
- [`redcom_API.filter_log_event_table`](./redcom_API.md#function-filter_log_event_table): Filters the log_event table to only hold Data Entry pages rather than administrative logging.
- [`redcom_API.filter_missing_forms`](./redcom_API.md#function-filter_missing_forms): Filters out missing forms from the data dictionary and sends a message to the user to fill out the missing forms.
- [`redcom_API.find_empty_forms`](./redcom_API.md#function-find_empty_forms): Finds all empty forms in a given project.
- [`redcom_API.find_missing_data`](./redcom_API.md#function-find_missing_data): Finds missing data entries in a DataFrame using the data dictionary and the merged data table.
- [`redcom_API.find_outliers_chauvenet`](./redcom_API.md#function-find_outliers_chauvenet): Finds outliers in a DataFrame using Chauvenet's criterion.
- [`redcom_API.find_outliers_pierce`](./redcom_API.md#function-find_outliers_pierce): Finds outliers in a DataFrame using Pierce's criterion.
- [`redcom_API.find_outliers_qq`](./redcom_API.md#function-find_outliers_qq): Finds outliers in a DataFrame using QQ plots and Cook's distance.
- [`redcom_API.find_version_history`](./redcom_API.md#function-find_version_history): Retrieves the build of the latest updated redcap version from the redcap_history_version table.
- [`redcom_API.get_app_title`](./redcom_API.md#function-get_app_title): Retrieves the official title of the project from the redcap_projects table.
- [`redcom_API.get_arm_data`](./redcom_API.md#function-get_arm_data): Retrieves and merges redcap_events_metadata and redcap_events_arms tables to match event_id and event names
- [`redcom_API.get_colnames`](./redcom_API.md#function-get_colnames): Retrieves column names of given tables to use in data manipulation
- [`redcom_API.get_current_drw_count`](./redcom_API.md#function-get_current_drw_count): Retrieves the current number of entries in the redcap_data_quality_status table for use in alerting
- [`redcom_API.get_data_dictionary`](./redcom_API.md#function-get_data_dictionary): Retrieves the data dictionary from the redcap_metadata table in the mariaDB server.
- [`redcom_API.get_drw_table`](./redcom_API.md#function-get_drw_table): Retrieves redcap_data_quality_resolutions and redcap_data_quality_status tables and joins them
- [`redcom_API.get_entry_of_missing`](./redcom_API.md#function-get_entry_of_missing): Retrieves the user_id and username of the data entrist by filtering on the hnrcid, event_id, field_name, and instance attributes.
- [`redcom_API.get_entry_of_outlier`](./redcom_API.md#function-get_entry_of_outlier): Retrieves the user_id, username, and email of the data entrist by filtering on the hnrcid, event_id, field_name, and instance attributes.
- [`redcom_API.get_log_event_and_data_tables`](./redcom_API.md#function-get_log_event_and_data_tables): Retrieves the log_event and data table from the redcap_projects table.
- [`redcom_API.get_table_data`](./redcom_API.md#function-get_table_data): Retrieves column names of given tables to use in data manipulation
- [`redcom_API.get_thread_id`](./redcom_API.md#function-get_thread_id): Retrieves the thread_id of the new thread to be created in the redcap_messages_threads table.
- [`redcom_API.get_unioned_super_table`](./redcom_API.md#function-get_unioned_super_table)
- [`redcom_API.get_user_information`](./redcom_API.md#function-get_user_information): Retrieves the user_information from the redcap_user_information table in the mariaDB server.
- [`redcom_API.get_user_roles`](./redcom_API.md#function-get_user_roles): Retrieves the user roles from the redcap_user_roles table in the mariaDB server.
- [`redcom_API.get_username`](./redcom_API.md#function-get_username): Retrieves the username of the recipient of the message from the redcap_user_information table.
- [`redcom_API.missing_data_submission`](./redcom_API.md#function-missing_data_submission): Submits a new data entry to the redcap_data_quality_status and redcap_data_quality_resolutions tables after checking for duplicates.
- [`redcom_API.navigate_branching_logic`](./redcom_API.md#function-navigate_branching_logic): This function navigates the branching logic of the personalized data dictionary to remove rows that do not meet the criteria of the branching logic.
- [`redcom_API.operate_missing_qc`](./redcom_API.md#function-operate_missing_qc): Args:
- [`redcom_API.operate_outlier_qc`](./redcom_API.md#function-operate_outlier_qc): Operates the outlier detection and submission process for a given DataFrame.
- [`redcom_API.operate_quality_control_individual`](./redcom_API.md#function-operate_quality_control_individual): Operates the quality control process on a data entry.
- [`redcom_API.operate_quality_control_routine`](./redcom_API.md#function-operate_quality_control_routine): Operates the quality control process on a data entry.
- [`redcom_API.outlier_data_submission`](./redcom_API.md#function-outlier_data_submission): Submits a new data entry to the redcap_data_quality_status and redcap_data_quality_resolutions tables after checking for duplicates.
- [`redcom_API.pierce_critical_value`](./redcom_API.md#function-pierce_critical_value): Approximate critical value based on dataset size N.
- [`redcom_API.prepare_drw_data`](./redcom_API.md#function-prepare_drw_data): Prepares the necessary data to be entered into the redcap_data_quality_status and redcap_data_quality_resolutions tables.
- [`redcom_API.prepare_mess_data`](./redcom_API.md#function-prepare_mess_data): Prepares the necessary data to be entered into the redcap_messages, redcap_messages_recipients, and redcap_messages_threads tables.
- [`redcom_API.qq_calc_cooks_dist`](./redcom_API.md#function-qq_calc_cooks_dist): Calculate Cook's distance for a group of data points.
- [`redcom_API.read_log_file`](./redcom_API.md#function-read_log_file): For use in the Flask app, reads the last 10 lines of the log file and returns them as HTML.
- [`redcom_API.refresh_all_stored_data`](./redcom_API.md#function-refresh_all_stored_data): Refreshes all stored data in the stored_data folder.
- [`redcom_API.refresh_background_trigger`](./redcom_API.md#function-refresh_background_trigger): Official process to refresh triggers for the log_event and data tables (used in multithreading).
- [`redcom_API.refresh_data_table_trigger`](./redcom_API.md#function-refresh_data_table_trigger): Refreshes (creates or replaces) a trigger for the data table to send data to the Flask server when a record has completed a study.
- [`redcom_API.refresh_log_event_trigger`](./redcom_API.md#function-refresh_log_event_trigger): Refreshes (creates or replaces) a trigger for the log_event table to send data to the Flask server when a new record is created or updated.
- [`redcom_API.refresh_necessary_data_table_triggers`](./redcom_API.md#function-refresh_necessary_data_table_triggers): Refreshes triggers for the log_event tables to send data to the Flask server when a new record is created or updated.
- [`redcom_API.refresh_necessary_log_event_triggers`](./redcom_API.md#function-refresh_necessary_log_event_triggers): Refreshes triggers for the log_event tables to send data to the Flask server when a new record is created or updated.
- [`redcom_API.resolve_open_queries`](./redcom_API.md#function-resolve_open_queries): Resolves open queries for missing data in the redcap_data_quality_resolutions and redcap_data_quality_status tables by 
- [`redcom_API.retrieve_all_data`](./redcom_API.md#function-retrieve_all_data): Retrieves all data from the redcap_data tables for a list of project_ids.
- [`redcom_API.retrieve_completed_users`](./redcom_API.md#function-retrieve_completed_users): Retrieves the list of users who have completed the study from the local storage.
- [`redcom_API.retrieve_data_dictionary`](./redcom_API.md#function-retrieve_data_dictionary): Retrieves the data dictionary from the local storage
- [`redcom_API.retrieve_database_table`](./redcom_API.md#function-retrieve_database_table): Retrieves column names of given tables to use in data manipulation
- [`redcom_API.retrieve_default_reviewer`](./redcom_API.md#function-retrieve_default_reviewer): Retrieves the default assignees for a project from the redcap_user_rights table.
- [`redcom_API.retrieve_project_data`](./redcom_API.md#function-retrieve_project_data): Retrieves redcap_projects table from the local storage.
- [`redcom_API.retrieve_user_roles`](./redcom_API.md#function-retrieve_user_roles): Retrieves the user roles from the local storage
- [`redcom_API.send_email`](./redcom_API.md#function-send_email): Sends an email alert to the specified recipient(s) with the specified message.
- [`redcom_API.send_error_email`](./redcom_API.md#function-send_error_email): Sends an error email alert to the specified recipient(s) with the specified message.
- [`redcom_API.send_periodic_email`](./redcom_API.md#function-send_periodic_email): Sends an email to all users who have unresolved data quality queries in the system. The email is sent once every 24 hours once the interval is triggered.
- [`redcom_API.set_last_checked`](./redcom_API.md#function-set_last_checked): Sets the last checked data in the log file.
- [`redcom_API.store_completed_users`](./redcom_API.md#function-store_completed_users): Stores the list of users who have completed the study in the local storage. 
- [`redcom_API.store_data_dictionary`](./redcom_API.md#function-store_data_dictionary): Stores the data dictionary locally as a CSV file.
- [`redcom_API.store_project_data`](./redcom_API.md#function-store_project_data): Retrieves redcap_projects table from the mariaDB server and stores it locally as a CSV file.
- [`redcom_API.store_user_roles`](./redcom_API.md#function-store_user_roles): Stores the user roles locally as a CSV file.
- [`redcom_API.submit_stored_drw_entries`](./redcom_API.md#function-submit_stored_drw_entries): Retrieves csv file with stored DRW entries and submits any entries that do not exist in the DRW to REDCap
- [`app.common_troubleshooting`](./app.md#function-common_troubleshooting): Returns common troubleshooting fixes.
- [`app.default_page`](./app.md#function-default_page): Returns the default webpage structure with routing, troubleshooting, and log file.
- [`app.home`](./app.md#function-home): Routed from / and /flaskApp/.
- [`app.logfile_tail`](./app.md#function-logfile_tail): Returns the last 10 lines of the log file.
- [`app.outlier_and_missing_routine`](./app.md#function-outlier_and_missing_routine): Runs when triggered by POST request from MariaDB.
- [`app.receive_from_maria`](./app.md#function-receive_from_maria): Runs when triggered by POST request from MariaDB. 
- [`app.routing_links`](./app.md#function-routing_links): Returns the webpage routes.
- [`app.update_triggers`](./app.md#function-update_triggers): Routed from /flaskApp/update-triggers/ and when triggered by POST request from MariaDB.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
