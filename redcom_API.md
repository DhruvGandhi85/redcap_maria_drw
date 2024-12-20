<!-- markdownlint-disable -->

# <kbd>module</kbd> `redcom_API`




**Global Variables**
---------------
- **rootdir**
- **logdir**
- **logfile**

---

## <kbd>function</kbd> `read_log_file`

```python
read_log_file(logfile: 'str') → str
```

For use in the Flask app, reads the last 10 lines of the log file and returns them as HTML. 



**Args:**
 
 - <b>`logfile`</b> (str):  The path to the log file. 



**Returns:**
 
 - <b>`str`</b>:  The last 10 lines of the log file as HTML. 


---

## <kbd>function</kbd> `send_email`

```python
send_email(
    message: 'str' = '',
    recipient_emails: 'list' = ['marcus.lehr@tufts.edu']
) → str
```

Sends an email alert to the specified recipient(s) with the specified message. 



**Args:**
 
 - <b>`message`</b> (str):  The message to include in the email. 
 - <b>`recipient_emails`</b> (list):  A list of email addresses to send the email to. 



**Returns:**
 
 - <b>`str`</b>:  A message indicating that the email was sent. 


---

## <kbd>function</kbd> `send_error_email`

```python
send_error_email(
    message: 'str' = '',
    recipient_emails: 'list' = ['marcus.lehr@tufts.edu']
) → str
```

Sends an error email alert to the specified recipient(s) with the specified message. 



**Args:**
 
 - <b>`message`</b> (str):  The message to include in the email. 
 - <b>`recipient_emails`</b> (list):  A list of email addresses to send the email to. 



**Returns:**
 
 - <b>`str`</b>:  A message indicating that the email was sent. 


---

## <kbd>function</kbd> `check_last_run`

```python
check_last_run(hours: 'int' = 9) → None
```

Checks the last time the outlier and missing data routine was run. If it was more than n hours ago, sends an email to the administrator. 



**Args:**
 
 - <b>`hours`</b> (int, optional):  The number of hours to check against. 



**Returns:**
 None 


---

## <kbd>function</kbd> `connect_to_maria`

```python
connect_to_maria(
    maria_user: 'str' = 'redcap_user',
    maria_pass: 'str' = '',
    maria_host: 'str' = 'redcap.hnrc.tufts.edu',
    maria_database: 'str' = 'redcap'
) → mariadb.connections.Connection
```

Establishes a connection to the mariaDB server. 

If the arguments `maria_user`, `maria_pass`, `maria_host`, `maria_database` are not provided, the default credentials from the `.env` file are loaded in.  



**Args:**
 
 - <b>`maria_user`</b> (str, optional):  The username of the mariaDB account (default is `mariaUser` from `.env`) 
 - <b>`maria_pass`</b> (str, optional):  The password of the mariaDB account (default is `mariaPass` from `.env`) 
 - <b>`maria_host`</b> (str, optional):  The host of the mariaDB server (default is `mariaHost` from `.env`) 
 - <b>`maria_database`</b> (str, optional):  The name of the mariaDB database (default is `mariaDatabase` from `.env`) 



**Returns:**
 
 - <b>`mariadb.connections.Connection`</b>:  A connection to the mariaDB server. 

Raises:     
 - <b>`mariadb.Error`</b>:  Raised if the connection fails (e.g. incorrect credentials or server is at max capacity) 


---

## <kbd>function</kbd> `execute_maria_cmd`

```python
execute_maria_cmd(
    conn: 'mariadb.connections.Connection',
    sql_comm: 'str',
    data_input: 'tuple' = None
) → list | None
```

Utilizes a cursor to execute a given SQL command in the mariaDB database.  If additional data is passed in, this is executed alongside the command as necessary 

If the argument `data_input` is not provided, it is assumed this is not a data input operation. 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server. 
 - <b>`sql_comm`</b> (str):  The SQL command to be executed in the database. 
 - <b>`data_input`</b> (tuple, optional):  The potential data values to be inputted into a mariaDB table, formatted as follows: `(val_col1, val_col2, val_col3, val_col...)`. Default value is None. 



**Returns:**
 
 - <b>`list | None`</b>:  If query returns a table, returns table values in the form of a list. Otherwise does not return anything. 



**Raises:**
 
 - <b>`mariadb.Error`</b>:  Raised if the operation fails (e.g., key-error, incorrect data values/types, etc.) 


---

## <kbd>function</kbd> `get_colnames`

```python
get_colnames(conn: 'mariadb.connections.Connection', table_names: 'list') → dict
```

Retrieves column names of given tables to use in data manipulation 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server. 
 - <b>`table_names`</b> (list):  The names of the redcap tables to retrieve. 



**Returns:**
 
 - <b>`dict`</b>:  A dictionary of type `string: list_of_strings` representing redcap tables and their list of column names, formatted as follows: `{'table_1': ['t1_col1', 't1_c2'], 'table_2': ['t2_col1'], ...}`. 


---

## <kbd>function</kbd> `get_table_data`

```python
get_table_data(
    conn: 'mariadb.connections.Connection',
    table_cols: 'dict'
) → dict
```

Retrieves column names of given tables to use in data manipulation 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server. 
 - <b>`table_cols`</b> (dict):  A dictionary of type `string: list_of_strings` representing redcap tables and their list of column names 



**Returns:**
 
 - <b>`dict`</b>:  A dictionary of type `string: pandas.DataFrame` representing redcap tables and their data, formatted as follows: `{'table_1': pd.DataFrame, 'table_2': pd.DataFrame, ...}`. 


---

## <kbd>function</kbd> `retrieve_database_table`

```python
retrieve_database_table(table_names: 'list') → dict
```

Retrieves column names of given tables to use in data manipulation 



**Args:**
 
 - <b>`table_names`</b> (list):  The names of the redcap tables to retrieve. 



**Returns:**
 
 - <b>`dict`</b>:  A dictionary of type `string: pd.DataFrame` representing redcap tables and their data, formatted as follows: `{'table_1': pd.DataFrame(table_1), 'table_2': pd.DataFrame(table_2), ...}`. 


---

## <kbd>function</kbd> `get_data_dictionary`

```python
get_data_dictionary(filter: 'bool' = True) → pd.DataFrame
```

Retrieves the data dictionary from the redcap_metadata table in the mariaDB server. Filters the data dictionary to compare all ints and floats aside from ID number. 



**Args:**
 
 - <b>`filter`</b> (bool, optional):  If True, filters the data dictionary to compare all ints and floats aside from ID number. Default is True. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the filtered data dictionary. 


---

## <kbd>function</kbd> `store_data_dictionary`

```python
store_data_dictionary() → None
```

Stores the data dictionary locally as a CSV file. 



**Returns:**
  None 


---

## <kbd>function</kbd> `retrieve_data_dictionary`

```python
retrieve_data_dictionary() → pd.DataFrame
```

Retrieves the data dictionary from the local storage 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the filtered data dictionary 


---

## <kbd>function</kbd> `get_user_roles`

```python
get_user_roles() → pd.DataFrame
```

Retrieves the user roles from the redcap_user_roles table in the mariaDB server. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the user roles. 


---

## <kbd>function</kbd> `store_user_roles`

```python
store_user_roles() → None
```

Stores the user roles locally as a CSV file. 



**Returns:**
  None 


---

## <kbd>function</kbd> `retrieve_user_roles`

```python
retrieve_user_roles() → pd.DataFrame
```

Retrieves the user roles from the local storage 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the user roles 


---

## <kbd>function</kbd> `get_user_information`

```python
get_user_information() → pd.DataFrame
```

Retrieves the user_information from the redcap_user_information table in the mariaDB server. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the user information. 


---

## <kbd>function</kbd> `store_project_data`

```python
store_project_data() → pd.DataFrame
```

Retrieves redcap_projects table from the mariaDB server and stores it locally as a CSV file. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the redcap_projects table. 


---

## <kbd>function</kbd> `retrieve_project_data`

```python
retrieve_project_data() → pd.DataFrame
```

Retrieves redcap_projects table from the local storage. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the redcap_projects table 


---

## <kbd>function</kbd> `store_completed_users`

```python
store_completed_users() → None
```

Stores the list of users who have completed the study in the local storage.  Filters to see if study_complete is 0 or ss_status is 2 or 4. 



**Returns:**
  None 


---

## <kbd>function</kbd> `retrieve_completed_users`

```python
retrieve_completed_users() → pd.DataFrame
```

Retrieves the list of users who have completed the study from the local storage. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the list of users who have completed the study 


---

## <kbd>function</kbd> `refresh_all_stored_data`

```python
refresh_all_stored_data() → None
```

Refreshes all stored data in the stored_data folder. 



**Returns:**
  None 


---

## <kbd>function</kbd> `set_last_checked`

```python
set_last_checked(filename: 'str', message: 'str') → None
```

Sets the last checked data in the log file. 



**Args:**
 
 - <b>`filename`</b> (str):  The name of the file to write the message to. 
 - <b>`message`</b> (str):  The message to write to the log file. 



**Returns:**
 None 


---

## <kbd>function</kbd> `refresh_log_event_trigger`

```python
refresh_log_event_trigger(table_name: 'str') → str
```

Refreshes (creates or replaces) a trigger for the log_event table to send data to the Flask server when a new record is created or updated. 



**Args:**
 
 - <b>`table_name`</b> (str):  The name of the log_event table to create the trigger for. 



**Returns:**
 
 - <b>`str`</b>:  The SQL command to create the trigger for the log_event table. 


---

## <kbd>function</kbd> `refresh_data_table_trigger`

```python
refresh_data_table_trigger(table_name: 'str') → str
```

Refreshes (creates or replaces) a trigger for the data table to send data to the Flask server when a record has completed a study. 



**Args:**
 
 - <b>`table_name`</b> (str):  The name of the log_event table to create the trigger for. 



**Returns:**
 
 - <b>`str`</b>:  The SQL command to create the trigger for the log_event table. 


---

## <kbd>function</kbd> `refresh_necessary_log_event_triggers`

```python
refresh_necessary_log_event_triggers(
    conn: 'mariadb.connections.Connection'
) → str
```

Refreshes triggers for the log_event tables to send data to the Flask server when a new record is created or updated. 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server. 



**Returns:**
 
 - <b>`str`</b>:  A message indicating the completion of the trigger creation process. 


---

## <kbd>function</kbd> `refresh_necessary_data_table_triggers`

```python
refresh_necessary_data_table_triggers(
    conn: 'mariadb.connections.Connection'
) → str
```

Refreshes triggers for the log_event tables to send data to the Flask server when a new record is created or updated. 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server. 



**Returns:**
 
 - <b>`str`</b>:  A message indicating the completion of the trigger creation process. 


---

## <kbd>function</kbd> `drop_log_event_triggers`

```python
drop_log_event_triggers(conn: 'mariadb.connections.Connection') → str
```

Drops triggers for the log_event tables to stop sending data to the Flask server when a new record is created or updated. 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server. 



**Returns:**
 
 - <b>`str`</b>:  A message indicating the completion of the trigger drop process. 


---

## <kbd>function</kbd> `drop_data_table_triggers`

```python
drop_data_table_triggers(conn: 'mariadb.connections.Connection') → str
```

Drops triggers for the log_event tables to stop sending data to the Flask server when a new record is created or updated. 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server. 



**Returns:**
 
 - <b>`str`</b>:  A message indicating the completion of the trigger drop process. 


---

## <kbd>function</kbd> `refresh_background_trigger`

```python
refresh_background_trigger() → None
```

Official process to refresh triggers for the log_event and data tables (used in multithreading). 



**Returns:**
  None 


---

## <kbd>function</kbd> `retrieve_default_reviewer`

```python
retrieve_default_reviewer(project_id: 'int', form_name: 'str') → pd.DataFrame
```

Retrieves the default assignees for a project from the redcap_user_rights table. 



**Args:**
 
 - <b>`project_id`</b> (int):  The project_id of the project to retrieve the default assignees for. 
 - <b>`form_name`</b> (str):  The form_name of the form to retrieve the default assignees for. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the default assignees for the project 


---

## <kbd>function</kbd> `filter_data_table`

```python
filter_data_table(data_table: 'pd.DataFrame') → pd.DataFrame
```

Prepares the redcap_data table for operations such as joining with log table 



**Args:**
 
 - <b>`data_table`</b> (pd.DataFrame):  A pandas DataFrame containing the redcap_data table 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the filtered redcap_data table 


---

## <kbd>function</kbd> `retrieve_all_data`

```python
retrieve_all_data(pid_list: 'list') → pd.DataFrame
```

Retrieves all data from the redcap_data tables for a list of project_ids. 



**Args:**
 
 - <b>`pid_list`</b> (list):  A list of project_ids to retrieve the data for. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing all data for the projects in the list 


---

## <kbd>function</kbd> `get_log_event_and_data_tables`

```python
get_log_event_and_data_tables(project_id: 'int') → tuple[list, list]
```

Retrieves the log_event and data table from the redcap_projects table. 



**Args:**
 
 - <b>`project_id`</b> (int):  The project_id of the project to retrieve the tables for. 



**Returns:**
 
 - <b>`tuple[list, list]`</b>:  A tuple containing lists of strings representing the log_event and data table names for the project. 


---

## <kbd>function</kbd> `check_for_confirmed_correct_fields`

```python
check_for_confirmed_correct_fields(
    data_dictionary: 'pd.DataFrame'
) → pd.DataFrame
```

Checks the data dictionary for fields that have been confirmed correct in the redcap_data_quality_status and redcap_data_quality_resolutions tables. Removes these fields from the data dictionary so they cannot be flagged as missing data.  



**Args:**
 
 - <b>`data_dictionary`</b> (pd.DataFrame):  A pandas DataFrame containing the data dictionary 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the data dictionary with fields that have been confirmed correct removed 


---

## <kbd>function</kbd> `get_drw_table`

```python
get_drw_table() → pd.DataFrame
```

Retrieves redcap_data_quality_resolutions and redcap_data_quality_status tables and joins them 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the merged redcap_data_quality_resolutions and redcap_data_quality_status tables 


---

## <kbd>function</kbd> `get_current_drw_count`

```python
get_current_drw_count() → int
```

Retrieves the current number of entries in the redcap_data_quality_status table for use in alerting 



**Returns:**
 
 - <b>`int`</b>:  The current number of entries in the redcap_data_quality 


---

## <kbd>function</kbd> `filter_log_event_table`

```python
filter_log_event_table(log_event_table: 'pd.DataFrame') → pd.DataFrame
```

Filters the log_event table to only hold Data Entry pages rather than administrative logging. 



**Args:**
 
 - <b>`log_event_table`</b> (pd.DataFrame):  A pandas DataFrame containing the log_event table 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the filtered log_event table 


---

## <kbd>function</kbd> `get_unioned_super_table`

```python
get_unioned_super_table(pid_list: 'list') → pd.DataFrame
```






---

## <kbd>function</kbd> `resolve_open_queries`

```python
resolve_open_queries(pid_list: 'list', production_mode: 'bool' = False) → None
```

Resolves open queries for missing data in the redcap_data_quality_resolutions and redcap_data_quality_status tables by   merging with existing data and seeing what has been added. 



**Args:**
 
 - <b>`pid_list`</b> (list):  A list of project_ids to resolve open queries for 
 - <b>`production_mode`</b> (bool, optional):  If True, resolves the open queries in production mode. Default is False. 



**Returns:**
 None 


---

## <kbd>function</kbd> `get_thread_id`

```python
get_thread_id(
    mess_tables: 'dict',
    channel_name: 'str',
    user_id: 'int',
    assigned_user_id: 'int',
    project_id: 'int'
) → int
```

Retrieves the thread_id of the new thread to be created in the redcap_messages_threads table. 



**Args:**
 
 - <b>`mess_tables`</b> (dict):  A dictionary containing the tables necessary for the messaging system 
 - <b>`channel_name`</b> (str):  The name of the channel the message is being sent in 
 - <b>`user_id`</b> (int):  The user_id of the author of the message 
 - <b>`assigned_user_id`</b> (int):  The user_id of the recipient of the message 
 - <b>`project_id`</b> (int):  The project_id of the project the message is being sent in 



**Returns:**
 
 - <b>`int`</b>:  The thread_id of the new thread to be created 


---

## <kbd>function</kbd> `get_username`

```python
get_username(mess_tables: 'dict', recipient_user_id: 'int') → str
```

Retrieves the username of the recipient of the message from the redcap_user_information table. 



**Args:**
 
 - <b>`mess_tables`</b> (dict):  A dictionary containing the tables necessary for the messaging system 
 - <b>`recipient_user_id`</b> (int):  The user_id of the recipient of the message 



**Returns:**
 
 - <b>`str`</b>:  The username of the recipient of the message 


---

## <kbd>function</kbd> `get_app_title`

```python
get_app_title(mess_tables: 'dict', project_id: 'int') → str
```

Retrieves the official title of the project from the redcap_projects table. 



**Args:**
 
 - <b>`mess_tables`</b> (dict):  A dictionary containing the tables necessary for the messaging system 
 - <b>`project_id`</b> (int):  The project_id of the project to retrieve the title of 



**Returns:**
 
 - <b>`str`</b>:  The official title of the project 


---

## <kbd>function</kbd> `find_version_history`

```python
find_version_history() → str
```

Retrieves the build of the latest updated redcap version from the redcap_history_version table. 



**Returns:**
 
 - <b>`str`</b>:  The build of the latest updated redcap version 


---

## <kbd>function</kbd> `create_msg_body`

```python
create_msg_body(
    app_title: 'str',
    redcap_version: 'str',
    project_id: 'int',
    status: 'str',
    recipient_user_id: 'int',
    status_id: 'int',
    username: 'str',
    sent_time: 'datetime.datetime'
) → str
```

Creates the message body to be sent to the recipient via the REDCap messenger, including a link to the workflow table. 



**Args:**
 
 - <b>`app_title`</b> (str):  The official title of the project 
 - <b>`redcap_version`</b> (str):  The current version of the redcap server 
 - <b>`project_id`</b> (int):  The project_id of the project the message is being sent in 
 - <b>`status`</b> (str):  The status of the data query 
 - <b>`recipient_user_id`</b> (int):  The user_id of the recipient of the message 
 - <b>`status_id`</b> (int):  The status_id of the data query 
 - <b>`username`</b> (str):  The username of the author of the message 
 - <b>`sent_time`</b> (datetime.datetime):  The time the message was sent 



**Returns:**
 
 - <b>`str`</b>:  The message body to be sent to the recipient via the REDCap messenger, including a link to the workflow table 


---

## <kbd>function</kbd> `get_arm_data`

```python
get_arm_data() → pd.DataFrame
```

Retrieves and merges redcap_events_metadata and redcap_events_arms tables to match event_id and event names 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A pandas DataFrame containing the merged redcap_events_metadata and redcap_events_arms tables 


---

## <kbd>function</kbd> `send_periodic_email`

```python
send_periodic_email() → None
```

Sends an email to all users who have unresolved data quality queries in the system. The email is sent once every 24 hours once the interval is triggered. 



**Returns:**
  None 


---

## <kbd>function</kbd> `check_drw_enabled`

```python
check_drw_enabled(pid_list: 'list') → None
```

Checks if the data resolution workflow parameter is enabled for the projects in the list. 



**Args:**
 
 - <b>`pid_list`</b> (list):  A list of project_ids to check the data resolution workflow for 



**Returns:**
 None 


---

## <kbd>function</kbd> `prepare_mess_data`

```python
prepare_mess_data(
    mess_tables: 'dict',
    author_user_id: 'int',
    recipient_user_id: 'int',
    sent_time: 'datetime.datetime',
    project_id: 'int',
    status: 'str',
    status_id: 'int'
) → list
```

Prepares the necessary data to be entered into the redcap_messages, redcap_messages_recipients, and redcap_messages_threads tables. 



**Args:**
 
 - <b>`mess_tables`</b> (dict):  A dictionary containing the tables necessary for the messaging system 
 - <b>`author_user_id`</b> (int):  The user_id of the author of the message 
 - <b>`recipient_user_id`</b> (int):  The user_id of the recipient of the message 
 - <b>`sent_time`</b> (datetime.datetime):  The time the message was sent 
 - <b>`project_id`</b> (int):  The project_id of the project the message is being sent in 
 - <b>`status`</b> (str):  The status of the data query 
 - <b>`status_id`</b> (int):  The status_id of the data query 



**Returns:**
 
 - <b>`list`</b>:  A list of tuples containing the necessary data to be entered into the redcap_messages, redcap_messages_recipients, and redcap_messages_threads tables 


---

## <kbd>function</kbd> `prepare_drw_data`

```python
prepare_drw_data(
    dq_tables: 'dict',
    ts: 'datetime.datetime',
    project_id: 'int',
    event_id: 'int',
    hnrcid: 'int',
    field_name: 'str',
    value: 'str',
    repeat_instance: 'int',
    assigned_user_id: 'int',
    user_id: 'int',
    comment: 'str'
) → list
```

Prepares the necessary data to be entered into the redcap_data_quality_status and redcap_data_quality_resolutions tables. 



**Args:**
 
 - <b>`dq_tables`</b> (dict):  A dictionary containing the tables necessary for the data resolution workflow 
 - <b>`ts`</b> (datetime.datetime):  The time the data query was entered 
 - <b>`project_id`</b> (int):  The project_id of the data entry 
 - <b>`event_id`</b> (int):  The event_id of the data entry 
 - <b>`hnrcid`</b> (int):  The hnrcid of the data entry 
 - <b>`field_name`</b> (str):  The field_name of the data entry 
 - <b>`value`</b> (str):  The value of the data entry 
 - <b>`repeat_instance`</b> (int):  The repeat_instance of the data entry 
 - <b>`assigned_user_id`</b> (int):  The user_id of the recipient of the data query 
 - <b>`user_id`</b> (int):  The user_id of the author of the data query 
 - <b>`comment`</b> (str):  The comment of the data query 



**Returns:**
 
 - <b>`list`</b>:  A list of tuples containing the necessary data to be entered into the redcap_data_quality_status and redcap_data_quality_resolutions tables 


---

## <kbd>function</kbd> `find_outliers_chauvenet`

```python
find_outliers_chauvenet(df: 'pd.DataFrame') → pd.DataFrame
```

Finds outliers in a DataFrame using Chauvenet's criterion. Pseudocode (chau_peirce_thomson.pdf): 1. Calculate mean and std 2. If n · erfc(|value - mean|/ std) < 1/2 then reject value 3. Repeat steps 1 and 2 4. Report final mean, std, and n 



**Args:**
 
 - <b>`df`</b> (pd.DataFrame):  The DataFrame to find outliers in 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A DataFrame containing only the outliers 


---

## <kbd>function</kbd> `get_entry_of_outlier`

```python
get_entry_of_outlier(
    unioned_super_table: 'pd.DataFrame',
    project_id: 'int',
    event_id: 'int',
    hnrcid: 'int',
    form_name: 'str',
    field_name: 'str',
    value: 'str',
    repeat_instance: 'int'
) → tuple[int, str, str]
```

Retrieves the user_id, username, and email of the data entrist by filtering on the hnrcid, event_id, field_name, and instance attributes. 



**Args:**
 
 - <b>`unioned_super_table`</b> (pd.DataFrame):  A pandas DataFrame containing the unioned super table 
 - <b>`project_id`</b> (int):  The project_id of the data entry 
 - <b>`event_id`</b> (int):  The event_id of the data entry 
 - <b>`hnrcid`</b> (int):  The hnrcid of the data entry 
 - <b>`form_name`</b> (str):  The form_name of the data entry 
 - <b>`field_name`</b> (str):  The field_name of the data entry 
 - <b>`value`</b> (str):  The value of the data entry 
 - <b>`repeat_instance`</b> (int):  The repeat_instance of the data entry 



**Returns:**
 
 - <b>`tuple[int,str,str]`</b>:  A tuple containing the user_id, username, and email of the data entry 


---

## <kbd>function</kbd> `pierce_critical_value`

```python
pierce_critical_value(N) → float
```

Approximate critical value based on dataset size N. Pierce's criterion uses lookup tables to get the exact critical value. Here, we use a rough approximation based on the dataset size. 



**Args:**
 
 - <b>`N`</b> (int):  The number of data points in the dataset 



**Returns:**
 
 - <b>`float`</b>:  The critical value for Pierce's criterion 


---

## <kbd>function</kbd> `find_outliers_pierce`

```python
find_outliers_pierce(df: 'pd.DataFrame') → pd.DataFrame
```

Finds outliers in a DataFrame using Pierce's criterion. Pseudocode (chau_peirce_thomson.pdf): 1. Calculate mean and std 2. Calculate Z-scores for each data point 3. Find the most extreme outlier (highest Z-score) 4. If the Z-score is greater than the critical value, remove the outlier 5. Repeat steps 1-4 until no more outliers are found 



**Args:**
 
 - <b>`df`</b> (pd.DataFrame):  The DataFrame to find outliers in 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A DataFrame containing only the outliers 


---

## <kbd>function</kbd> `qq_calc_cooks_dist`

```python
qq_calc_cooks_dist(df_group: 'pd.DataFrame') → pd.DataFrame
```

Calculate Cook's distance for a group of data points. 



**Args:**
 
 - <b>`df_group`</b> (pd.DataFrame):  A group of data points to calculate Cook's distance for 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  The original DataFrame with Cook's distance added as a new column 


---

## <kbd>function</kbd> `find_outliers_qq`

```python
find_outliers_qq(df: 'pd.DataFrame') → pd.DataFrame
```

Finds outliers in a DataFrame using QQ plots and Cook's distance. 



**Args:**
 
 - <b>`df`</b> (pd.DataFrame):  The DataFrame to find outliers in. 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A DataFrame containing only the outliers. 


---

## <kbd>function</kbd> `create_data_res_workflow_entry`

```python
create_data_res_workflow_entry(
    conn: 'mariadb.connections.Connection',
    project_id: 'int',
    event_id: 'int',
    hnrcid: 'int',
    field_name: 'str',
    value: 'str',
    repeat_instance: 'int',
    assigned_user_id: 'int',
    user_id: 'int',
    ping: 'bool',
    comment: 'str',
    ts: 'datetime.datetime' = datetime.datetime(2024, 12, 20, 17, 26, 55, 216096, tzinfo=datetime.timezone.utc)
) → None
```

Creates a new data entry in the redcap_data_quality_status and redcap_data_quality_resolutions tables. 



**Args:**
 
 - <b>`conn`</b> (mariadb.connections.Connection):  The active connection to the mariaDB server 
 - <b>`project_id`</b> (int):  The project_id of the data entry 
 - <b>`event_id`</b> (int):  The event_id of the data entry 
 - <b>`hnrcid`</b> (int):  The hnrcid of the data entry 
 - <b>`field_name`</b> (str):  The field_name of the data entry 
 - <b>`value`</b> (str):  The value of the data entry 
 - <b>`repeat_instance`</b> (int):  The repeat_instance of the data entry 
 - <b>`assigned_user_id`</b> (int):  The user_id of the recipient of the data query 
 - <b>`user_id`</b> (int):  The user_id of the author of the data query 
 - <b>`ping`</b> (bool):  A boolean indicating whether to send a message to the recipient 
 - <b>`comment`</b> (str):  The comment of the data query 
 - <b>`ts`</b> (datetime.datetime, optional):  The time the data query was entered (default is the current time) 



**Returns:**
 None 


---

## <kbd>function</kbd> `check_existing_drw_entry`

```python
check_existing_drw_entry(
    project_id: 'int',
    event_id: 'int',
    hnrcid: 'int',
    field_name: 'str',
    official_user_id: 'int',
    repeat_instance: 'int'
) → pd.DataFrame
```

Searches redcap_data_quality_status table to see if a DRW entry exists for that record already.  Prevents key-errors as duplicate entries cannot be added to DRW.   



**Args:**
 
 - <b>`project_id`</b> (int):  The project_id of the data entry 
 - <b>`event_id`</b> (int):  The event_id of the data entry 
 - <b>`hnrcid`</b> (int):  The hnrcid of the data entry 
 - <b>`field_name`</b> (str):  The field_name of the data entry 
 - <b>`official_user_id`</b> (int):  The user_id of the recipient of the data query 
 - <b>`repeat_instance`</b> (int):  The repeat_instance of the data entry 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A DataFrame containing the existing DRW entry 


---

## <kbd>function</kbd> `outlier_data_submission`

```python
outlier_data_submission(
    project_id: 'int',
    event_id: 'int',
    hnrcid: 'int',
    form_name: 'str',
    field_name: 'str',
    value: 'str',
    repeat_instance: 'int',
    official_user_id: 'int',
    username: 'str',
    email: 'str',
    ping: 'bool' = True
) → None
```

Submits a new data entry to the redcap_data_quality_status and redcap_data_quality_resolutions tables after checking for duplicates. 



**Args:**
 
 - <b>`project_id`</b> (int):  The project_id of the data entry 
 - <b>`event_id`</b> (int):  The event_id of the data entry 
 - <b>`hnrcid`</b> (int):  The hnrcid of the data entry 
 - <b>`form_name`</b> (str):  The form_name of the data entry 
 - <b>`field_name`</b> (str):  The field_name of the data entry 
 - <b>`value`</b> (str):  The value of the data entry 
 - <b>`repeat_instance`</b> (int):  The repeat_instance of the data entry 
 - <b>`official_user_id`</b> (int):  The user_id of the recipient of the data query 
 - <b>`username`</b> (str):  The username of the recipient of the data query 
 - <b>`email`</b> (str):  The email of the recipient of the data query 
 - <b>`ping`</b> (bool, optional):  A boolean indicating whether to send a message to the recipient (default is True) 



**Returns:**
 None 


---

## <kbd>function</kbd> `operate_outlier_qc`

```python
operate_outlier_qc(
    merged_data_table: 'pd.DataFrame',
    data_entry_table: 'pd.DataFrame',
    unioned_super_table: 'pd.DataFrame',
    outlier_method: 'str' = 'Chauvanet',
    production_mode: 'bool' = False
) → None
```

Operates the outlier detection and submission process for a given DataFrame. 



**Args:**
 
 - <b>`merged_data_table`</b> (pd.DataFrame):  The DataFrame containing all the data for the relevant project 
 - <b>`data_entry_table`</b> (pd.DataFrame):  The DataFrame containing the data that has been submitted 
 - <b>`unioned_super_table`</b> (pd.DataFrame):  The DataFrame containing the unioned super table 
 - <b>`outlier_method`</b> (str, optional):  The method to use for outlier detection (default is 'Chauvanet') 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `get_entry_of_missing`

```python
get_entry_of_missing(
    unioned_super_table: 'pd.DataFrame',
    project_id: 'int',
    event_id: 'int',
    hnrcid: 'int',
    form_name: 'str',
    field_name: 'str',
    value: 'str',
    repeat_instance: 'int'
) → tuple[int, str, str]
```

Retrieves the user_id and username of the data entrist by filtering on the hnrcid, event_id, field_name, and instance attributes. 



**Args:**
 
 - <b>`unioned_super_table`</b> (pd.DataFrame):  The DataFrame containing all the data for the relevant project 
 - <b>`project_id`</b> (int):  The project_id of the data entry 
 - <b>`event_id`</b> (int):  The event_id of the data entry 
 - <b>`hnrcid`</b> (int):  The hnrcid of the data entry 
 - <b>`form_name`</b> (str):  The form_name of the data entry 
 - <b>`field_name`</b> (str):  The field_name of the data entry 
 - <b>`value`</b> (str):  The value of the data entry 
 - <b>`repeat_instance`</b> (int):  The repeat_instance of the data entry 



**Returns:**
 
 - <b>`tuple[int,str,str]`</b>:  A tuple containing the user_id, username, and email of the data entry 


---

## <kbd>function</kbd> `navigate_branching_logic`

```python
navigate_branching_logic(
    personalized_data_dic: 'pd.DataFrame',
    missing_check_dict: 'dict'
) → pd.DataFrame
```

This function navigates the branching logic of the personalized data dictionary to remove rows that do not meet the criteria of the branching logic. 

Steps: 1. Iterate through each row in the personalized data dictionary.  1a. Check if the branching logic is not null.  1b. Iterate through the other rows in the personalized data dictionary to check if the branching logic is met.  1c. Drop rows if the branching logic is confirmed to be not met. 

2. Iterate through each row in the personalized data dictionary.  2a. Drop rows if field_name is not vital or misc HIDDEN logic criteria are met. 

3. Iterate through each row in the personalized data dictionary.  3a. If a row is missing, check if the row references another field in the branching logic.  3b. Drop the row if the referenced field is not present. 





**Args:**
 
 - <b>`personalized_data_dic`</b> (pd.DataFrame):  The data dictionary to navigate the branching logic of for that exact event/form 
 - <b>`missing_check_dict`</b> (dict):  A dictionary containing the event_name, event_id, and form_name of the missing data entry 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  The updated personalized data dictionary after navigating the branching logic 


---

## <kbd>function</kbd> `find_missing_data`

```python
find_missing_data(
    merged_data_table: 'pd.DataFrame',
    data_dictionary: 'pd.DataFrame',
    missing_check_dict: 'dict'
) → pd.DataFrame
```

Finds missing data entries in a DataFrame using the data dictionary and the merged data table. 



**Args:**
 
 - <b>`merged_data_table`</b> (pd.DataFrame):  The DataFrame containing all the data for the relevant project 
 - <b>`data_dictionary`</b> (pd.DataFrame):  The DataFrame containing the data dictionary for the relevant project 
 - <b>`missing_check_dict`</b> (dict):  A dictionary containing the project_id, event_id, form_name, and event_name of the missing data entry 



**Returns:**
 
 - <b>`pd.DataFrame`</b>:  A DataFrame containing the missing data entries 


---

## <kbd>function</kbd> `missing_data_submission`

```python
missing_data_submission(
    project_id: 'int',
    event_id: 'int',
    hnrcid: 'int',
    form_name: 'str',
    field_name: 'str',
    value: 'str',
    repeat_instance: 'int',
    missing_fields: 'list',
    official_user_id: 'int',
    username: 'str',
    email: 'str',
    ping: 'bool' = True
) → None
```

Submits a new data entry to the redcap_data_quality_status and redcap_data_quality_resolutions tables after checking for duplicates. 



**Args:**
 
 - <b>`project_id`</b> (int):  The project_id of the data entry 
 - <b>`event_id`</b> (int):  The event_id of the data entry 
 - <b>`hnrcid`</b> (int):  The hnrcid of the data entry 
 - <b>`form_name`</b> (str):  The form_name of the data entry 
 - <b>`field_name`</b> (str):  The field_name of the data entry 
 - <b>`value`</b> (str):  The value of the data entry 
 - <b>`repeat_instance`</b> (int):  The repeat_instance of the data entry 
 - <b>`missing_fields`</b> (list):  A list of the missing fields in the data entry 
 - <b>`ping`</b> (bool, optional):  A boolean indicating whether to send a message to the recipient (default is True) 



**Returns:**
 None 


---

## <kbd>function</kbd> `submit_stored_drw_entries`

```python
submit_stored_drw_entries(
    alert_threshold: 'int' = 100,
    production_mode: 'bool' = False
) → None
```

Retrieves csv file with stored DRW entries and submits any entries that do not exist in the DRW to REDCap 



**Args:**
 
 - <b>`alert_threshold`</b> (int, optional):  The threshold for the number of entries to submit (default is 100) 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `operate_missing_qc`

```python
operate_missing_qc(
    merged_data_table: 'pd.DataFrame',
    data_entry_table: 'pd.DataFrame',
    unioned_super_table: 'pd.DataFrame',
    production_mode: 'bool' = False
) → None
```



**Args:**
 
 - <b>`merged_data_table`</b> (pd.DataFrame):  The merged data table containing all data entries for a given project 
 - <b>`data_entry_table`</b> (pd.DataFrame):  The data entry table containing the inputted data  
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run the function in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `operate_quality_control_individual`

```python
operate_quality_control_individual(
    data_entry: 'dict',
    outlier_method: 'str' = 'Chauvanet',
    outlier_qc: 'bool' = True,
    missing_qc: 'bool' = True,
    routine: 'bool' = False,
    production_mode: 'bool' = False
) → None
```

Operates the quality control process on a data entry. 



**Args:**
 
 - <b>`data_entry`</b> (dict):  The data entry to operate the quality control process on 
 - <b>`outlier_method`</b> (str, optional):  The method to use for outlier detection (default is 'Chauvanet') 
 - <b>`outlier_qc`</b> (bool, optional):  A boolean indicating whether to perform outlier quality control (default is True) 
 - <b>`missing_qc`</b> (bool, optional):  A boolean indicating whether to perform missing data quality control (default is True) 
 - <b>`routine`</b> (bool, optional):  A boolean indicating whether to perform the quality control routine (default is False) 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run the process in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `operate_quality_control_routine`

```python
operate_quality_control_routine(
    data_entry: 'dict',
    merged_data_table: 'pd.DataFrame',
    unioned_super_table: 'pd.DataFrame',
    outlier_method: 'str' = 'Chauvanet',
    outlier_qc: 'bool' = True,
    missing_qc: 'bool' = True,
    routine: 'bool' = False,
    production_mode: 'bool' = False
) → None
```

Operates the quality control process on a data entry. 



**Args:**
 
 - <b>`data_entry`</b> (dict):  The data entry to operate the quality control process on 
 - <b>`merged_data_table`</b> (pd.DataFrame):  The merged data table containing all data entries for a given project 
 - <b>`unioned_super_table`</b> (pd.DataFrame):  The unioned super table containing all data entries for a given project 
 - <b>`outlier_method`</b> (str, optional):  The method to use for outlier detection (default is 'Chauvanet') 
 - <b>`outlier_qc`</b> (bool, optional):  A boolean indicating whether to perform outlier quality control (default is True) 
 - <b>`missing_qc`</b> (bool, optional):  A boolean indicating whether to perform missing data quality control (default is True) 
 - <b>`routine`</b> (bool, optional):  A boolean indicating whether to perform the quality control routine (default is False) 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run the process in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `find_empty_forms`

```python
find_empty_forms(
    data_dictionary: 'pd.DataFrame',
    project_form_event_combos: 'pd.DataFrame',
    pid_list: 'list'
) → list
```

Finds all empty forms in a given project. 

one df (project_form_event_combos) has all the possible field_name and event_id combos.  The other (unioned_data_table) has all the pk, field_name and event_id combos that have been used.  If a pk has a field_name and event_id combo that is not in the used df, then it is missing. 



**Args:**
 
 - <b>`data_dictionary`</b> (pd.DataFrame):  The data dictionary to use for the process 
 - <b>`project_form_event_combos`</b> (pd.DataFrame):  The project form event combos that need to be checked 
 - <b>`pid_list`</b> (list):  The list of project ids 



**Returns:**
 
 - <b>`list`</b>:  A list of dataframes containing the missing forms separated by project id 


---

## <kbd>function</kbd> `filter_missing_forms`

```python
filter_missing_forms(
    pid_list: 'list',
    ping: 'bool' = True,
    production_mode: 'bool' = False
) → None
```

Filters out missing forms from the data dictionary and sends a message to the user to fill out the missing forms. 



**Args:**
 
 - <b>`pid_list`</b> (list):  A list of project_ids to filter missing forms for 
 - <b>`ping`</b> (bool, optional):  A boolean indicating whether to send a message to the recipient (default is True) 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run the function in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `check_for_all_outliers`

```python
check_for_all_outliers(
    pid_list: 'list',
    outlier_method='Chauvanet',
    alert_threshold: 'int' = 100,
    ping: 'bool' = True,
    production_mode: 'bool' = False
) → None
```

Checks for all missing data entries in the data dictionary and sends an email if the number of entries exceeds the alert threshold. 



**Args:**
 
 - <b>`pid_list`</b> (list):  A list of project_ids to check for missing data entries 
 - <b>`outlier_method`</b> (str, optional):  The method to use for outlier detection (default is 'Chauvanet') 
 - <b>`alert_threshold`</b> (int, optional):  The threshold for the number of missing data entries to send an alert (default is 100) 
 - <b>`ping`</b> (bool, optional):  A boolean indicating whether to send a message to the recipient (default is True) 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run the function in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `check_for_all_missing`

```python
check_for_all_missing(
    pid_list: 'list',
    alert_threshold: 'int' = 100,
    ping: 'bool' = True,
    production_mode: 'bool' = False
) → None
```

Checks for all missing data entries in the data dictionary and sends an email if the number of entries exceeds the alert threshold. 



**Args:**
 
 - <b>`pid_list`</b> (list):  A list of project_ids to check for missing data entries 
 - <b>`alert_threshold`</b> (int, optional):  The threshold for the number of missing data entries to send an alert (default is 100) 
 - <b>`ping`</b> (bool, optional):  A boolean indicating whether to send a message to the recipient (default is True) 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run the function in production mode (default is False) 



**Returns:**
 None 


---

## <kbd>function</kbd> `check_for_all_outlier_and_missing`

```python
check_for_all_outlier_and_missing(
    pid_list: 'list',
    outlier_method: 'str' = 'Chauvanet',
    alert_threshold: 'int' = 100,
    ping: 'bool' = True,
    production_mode: 'bool' = False
) → None
```

Checks for all missing data entries and outlier data in the data dictionary and sends an email if the number of entries exceeds the alert threshold. 



**Args:**
 
 - <b>`pid_list`</b> (list):  A list of project_ids to check for missing data entries 
 - <b>`outlier_method`</b> (str, optional):  The method to use for outlier detection (default is 'Chauvanet') 
 - <b>`alert_threshold`</b> (int, optional):  The threshold for the number of missing data entries to send an alert (default is 100) 
 - <b>`ping`</b> (bool, optional):  A boolean indicating whether to send a message to the recipient (default is True) 
 - <b>`production_mode`</b> (bool, optional):  A boolean indicating whether to run the function in production mode (default is False) 



**Returns:**
 None 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
