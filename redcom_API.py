from __future__ import annotations          # allows for more strict type hinting (documentation)
import dotenv           # loads system environment
import os               # accesses system environment for stored private variables
import mariadb          # create connection to mdb server
import sys              # kills process if necessary
import re               # regex for data manipulation 
import socket           # retrieves IP for log entry
import datetime         # for timestamp field 
import time             # allows sleep intervals between polling
import pandas as pd     # data manipulation
import numpy as np      # converting numeric types for comparison
import warnings         # suppresses deprecation warnings
import logging          # logs events
import smtplib          # sends email alerts

from logging.config import dictConfig               # allows for logging configuration
from email.mime.text import MIMEText                # formats email alerts
from email.mime.multipart import MIMEMultipart      # formats email alerts

from scipy.special import erfc                      # provides mathematical operations for outlier filtering (Chauvenet’s)
from scipy.stats import norm                        # provides mathematical operations for outlier filtering (QQ)
from sklearn.preprocessing import StandardScaler    # provides mathematical operations for outlier filtering (QQ)
from statsmodels.formula.api import ols             # provides mathematical operations for outlier filtering (QQ)
import statsmodels.api as sm                        # provides mathematical operations for outlier filtering (QQ)

dotenv.load_dotenv()                                # loads system environment variables from .env file
warnings.filterwarnings('ignore')                   # suppresses deprecation warnings 

pd.set_option('display.max_columns', None)          # sets pandas output view settings (for development)
pd.set_option('display.expand_frame_repr', False)   # sets pandas output view settings (for development)
pd.set_option('max_colwidth', -1)                   # sets pandas output view settings (for development)

rootdir = f"C:\\inetpub\\flaskApp"            # sets root directory
logdir = fr"{rootdir}\\output_logs\\{datetime.datetime.now().strftime('%Y-%m')}"                # sets log directory
logfile = fr"{logdir}\\redcom_log_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"           # sets log file

if not os.path.exists(logdir):
    os.makedirs(logdir)

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s]: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': logfile,
            'encoding': 'utf-8',
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file'],
    }
})

def read_log_file(logfile: str) -> str:
    """
    For use in the Flask app, reads the last 10 lines of the log file and returns them as HTML.

    Args:
        logfile (str): The path to the log file.

    Returns:
        str: The last 10 lines of the log file as HTML.
    """
    try:
        with open(logfile, 'r') as file:
            lines = file.readlines()[-10:]
        styled_lines = [
            f"<span style='background-color: { '#f0f0f0' if i % 2 == 0 else '#ffffff' }; display: block;'>{line.strip()}</span>"
            for i, line in enumerate(lines)
        ]
        return "".join(styled_lines)
    except Exception as e:
        logging.error(f"Error reading log file: {e}")
        return "Could not read log file."

def send_email(message: str = '', recipient_emails: list = [os.environ.get("adminEmail")]) -> str:
    """
    Sends an email alert to the specified recipient(s) with the specified message.

    Args:
        message (str): The message to include in the email.
        recipient_emails (list): A list of email addresses to send the email to.

    Returns:
        str: A message indicating that the email was sent.
    """
    sender_email = "donotreply@redcap.hnrc.tufts.edu"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_emails) if isinstance(recipient_emails, list) else recipient_emails
    msg['Subject'] = "Redcap Alert"
    body = (
        "This is an automated message. Please do not reply to this email.\n\n"
        f"{message}\n\n"
    )
    msg.attach(MIMEText(body, 'plain'))

    # Tufts email server and port
    with smtplib.SMTP("130.64.49.7", 25) as server:
        server.ehlo()
        server.sendmail(sender_email, recipient_emails, msg.as_string())

    return 'Email sent \n'

def send_error_email(message: str = '', recipient_emails: list = [os.environ.get("adminEmail")]) -> str:
    """
    Sends an error email alert to the specified recipient(s) with the specified message.

    Args:
        message (str): The message to include in the email.
        recipient_emails (list): A list of email addresses to send the email to.

    Returns:
        str: A message indicating that the email was sent.
    """
    sender_email = "donotreply@redcap.hnrc.tufts.edu"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(recipient_emails) if isinstance(recipient_emails, list) else recipient_emails
    msg['Subject'] = "Automation Process Failed"
    body = (
        "We encountered an issue while attempting to execute the automation process. "
        "Please review the system logs or contact the support team to address the issue.\n\n"
        "This is an automated message. Please do not reply to this email.\n\n"
        f"{message}\n\n"
    )
    msg.attach(MIMEText(body, 'plain'))

    # Tufts email server and port
    with smtplib.SMTP("130.64.49.7", 25) as server:
        server.ehlo()
        server.sendmail(sender_email, recipient_emails, msg.as_string())

    return 'Email sent \n'

def check_last_run(hours: int = 9) -> None:
    """
    Checks the last time the outlier and missing data routine was run. If it was more than n hours ago, sends an email to the administrator.

    Args:
        hours (int, optional): The number of hours to check against.

    Returns:
        None
    """
    with open('stored_data/last_routine.log', 'r') as file:
        file_contents = file.read()
    
    timestamp = datetime.datetime.strptime(file_contents, '%Y-%m-%d %H:%M:%S')
    time_diff = datetime.datetime.now() - timestamp

    if time_diff > datetime.timedelta(hours=hours):
        send_error_email(message=f'Last run was more than {hours} hours ago. Please check the server.')
    logging.info("Time since last run: " + str(time_diff))
    return None

def connect_to_maria(maria_user: str = os.environ.get("mariaUser"), maria_pass: str = os.environ.get("mariaPass"), maria_host: str = os.environ.get("mariaHost"), maria_database: str = os.environ.get("mariaDatabase")) -> mariadb.connections.Connection:
    """
    Establishes a connection to the mariaDB server.

    If the arguments `maria_user`, `maria_pass`, `maria_host`, `maria_database` are not provided,
    the default credentials from the `.env` file are loaded in. 

    Args:
        maria_user (str, optional): The username of the mariaDB account (default is `mariaUser` from `.env`)
        maria_pass (str, optional): The password of the mariaDB account (default is `mariaPass` from `.env`)
        maria_host (str, optional): The host of the mariaDB server (default is `mariaHost` from `.env`)
        maria_database (str, optional): The name of the mariaDB database (default is `mariaDatabase` from `.env`)

    Returns:
        mariadb.connections.Connection: A connection to the mariaDB server.

    Raises:    
        mariadb.Error: Raised if the connection fails (e.g. incorrect credentials or server is at max capacity)
    """

    # sourced from mariaDB website - creates a connection to the mariaDB linux server 
    try:                              
        conn = mariadb.connect(
            user=maria_user,
            password=maria_pass,
            host=maria_host,
            database=maria_database
        )
        
        # Disable auto-commit, changes must be committed manually
        conn.autocommit = False       
    except mariadb.Error as e:
        logging.info(f"Error connecting to MariaDB Platform: {e}")

        # terminate the process if there is a connection error
        sys.exit(1)                 
    
    return conn

def execute_maria_cmd(conn: mariadb.connections.Connection, sql_comm: str, data_input: tuple = None) -> list | None:
    """
    Utilizes a cursor to execute a given SQL command in the mariaDB database. 
    If additional data is passed in, this is executed alongside the command as necessary

    If the argument `data_input` is not provided, it is assumed this is not a data input operation.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server.
        sql_comm (str): The SQL command to be executed in the database.
        data_input (tuple, optional): The potential data values to be inputted into a mariaDB table, formatted as follows: `(val_col1, val_col2, val_col3, val_col...)`. Default value is None.

    Returns:
        list | None: If query returns a table, returns table values in the form of a list. Otherwise does not return anything.

    Raises:
        mariadb.Error: Raised if the operation fails (e.g., key-error, incorrect data values/types, etc.)
    """

    # initializes a cursor to navigate mariaDB
    cur = conn.cursor()
    try: 
        # if data_input exists, submit the data alongside the execution of the command  
        if data_input is not None:
            cur.execute(sql_comm, data_input)
        else:
            cur.execute(sql_comm)
        
        # if query returns a table, returns table values in the form of a list
        try:
            results = cur.fetchall()
            return results
        except: 
            return None
    
    except mariadb.Error as e: 
        if "Duplicate entry" in str(e):
            with open(fr'{rootdir}\\output_logs\\key_errors.csv', 'a') as f:
                f.write(f"{e}|{data_input}|{sql_comm}\n")  
        else:
           logging.info(f"Error: {e} with data: {data_input} in command: {sql_comm}")  
           send_error_email(message=f"Error: {e} with data: {data_input} in command: {sql_comm}")  

    # cursor MUST be closed at end of process so it is not infinitely hanging
    finally:
        cur.close() 

def get_colnames(conn: mariadb.connections.Connection, table_names: list) -> dict:
    """
    Retrieves column names of given tables to use in data manipulation

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server.
        table_names (list): The names of the redcap tables to retrieve.

    Returns:
        dict: A dictionary of type `string: list_of_strings` representing redcap tables and their list of column names, formatted as follows: `{'table_1': ['t1_col1', 't1_c2'], 'table_2': ['t2_col1'], ...}`.
    """
    table_cols = {}
    for table_name in table_names:
        sql_comm = f"SHOW columns FROM {table_name}"
        results = execute_maria_cmd(conn, sql_comm)
        table_attributes = pd.DataFrame(results)

        # 0th element of returned table_attributes is colnames, so convert entire 0th column to a list
        colnames = list(table_attributes[0])
        table_cols[table_name] = colnames
    return table_cols

def get_table_data(conn: mariadb.connections.Connection, table_cols: dict) -> dict:
    """
    Retrieves column names of given tables to use in data manipulation

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server.
        table_cols (dict): A dictionary of type `string: list_of_strings` representing redcap tables and their list of column names

    Returns:
        dict: A dictionary of type `string: pandas.DataFrame` representing redcap tables and their data, formatted as follows: `{'table_1': pd.DataFrame, 'table_2': pd.DataFrame, ...}`.
    """
    tables = {}
    table_names = list(table_cols.keys())
    col_names = list(table_cols.values())
    for table in range(len(table_names)):
        sql_comm = f"SELECT * FROM {table_names[table]}"
        results = execute_maria_cmd(conn, sql_comm)

        df = pd.DataFrame(results, columns = col_names[table])
        tables[table_names[table]] = df
    return tables

def retrieve_database_table(table_names: list) -> dict:
    """
    Retrieves column names of given tables to use in data manipulation

    Args:
        table_names (list): The names of the redcap tables to retrieve.

    Returns:
        dict: A dictionary of type `string: pd.DataFrame` representing redcap tables and their data, formatted as follows: `{'table_1': pd.DataFrame(table_1), 'table_2': pd.DataFrame(table_2), ...}`.
    """
    conn = connect_to_maria()
    table_cols = get_colnames(conn, table_names)
    tables = get_table_data(conn, table_cols)
    conn.close()
    return tables

def get_data_dictionary(filter: bool = True) -> pd.DataFrame:
    """
    Retrieves the data dictionary from the redcap_metadata table in the mariaDB server.
    Filters the data dictionary to compare all ints and floats aside from ID number.

    Args:
        filter (bool, optional): If True, filters the data dictionary to compare all ints and floats aside from ID number. Default is True.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the filtered data dictionary.
    """
    table_data = retrieve_database_table(['redcap_metadata'])
    data_dic = table_data['redcap_metadata']

    data_dic = data_dic[~(data_dic['field_name'] == 'hnrcid')]
    if filter:
        data_dic = data_dic[(data_dic['element_validation_type'].str.contains('int', case=False, na=False)) | 
                            (data_dic['element_validation_type'].str.contains('float', case=False, na=False))]
    
    return data_dic

def store_data_dictionary() -> None:
    """
    Stores the data dictionary locally as a CSV file.

    Returns:
        None
    """
    path = f'{rootdir}\\stored_data'

    if not os.path.exists(path):
        os.makedirs(path)

    data_dictionary = get_data_dictionary(filter=False)
    data_dictionary['branching_logic'] = data_dictionary['branching_logic'].str.replace('\n', ' ')

    data_dictionary.to_csv(f'{path}\\data_dic.csv', index = False)

    return None

def retrieve_data_dictionary() -> pd.DataFrame:
    """
    Retrieves the data dictionary from the local storage

    Returns:
        pd.DataFrame: A pandas DataFrame containing the filtered data dictionary
    """
    path = f'{rootdir}\\stored_data'
    data_dic = pd.read_csv(f'{path}\\data_dic.csv')

    return data_dic

def get_user_roles() -> pd.DataFrame:
    """
    Retrieves the user roles from the redcap_user_roles table in the mariaDB server.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the user roles.
    """
    table_data = retrieve_database_table(['redcap_user_roles'])
    user_roles = table_data['redcap_user_roles']
    
    return user_roles
def store_user_roles() -> None:
    """
    Stores the user roles locally as a CSV file.
    
    Returns:
        None
    """
    path = f'{rootdir}\\stored_data'

    if not os.path.exists(path):
        os.makedirs(path)

    user_roles = get_user_roles()

    user_roles["data_entry"] = user_roles["data_entry"].str.findall(r"\[(.*?)\]") 
    df_exploded = user_roles.explode("data_entry", ignore_index=True)  
    df_exploded[["form_name", "permission"]] = df_exploded["data_entry"].str.split(",", expand=True) 

    df_exploded.to_csv(f'{path}\\user_roles.csv', index = False)

    return None

def retrieve_user_roles() -> pd.DataFrame:
    """
    Retrieves the user roles from the local storage
    
    Returns:
        pd.DataFrame: A pandas DataFrame containing the user roles
    """

    path = f'{rootdir}\\stored_data'
    user_roles = pd.read_csv(f'{path}\\user_roles.csv')

    return user_roles

def get_user_information() -> pd.DataFrame:
    """
    Retrieves the user_information from the redcap_user_information table in the mariaDB server.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the user information.
    """
    table_data = retrieve_database_table(['redcap_user_information'])
    user_information = table_data['redcap_user_information']
    
    return user_information

def store_project_data() -> pd.DataFrame:
    """
    Retrieves redcap_projects table from the mariaDB server and stores it locally as a CSV file.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the redcap_projects table.
    """
    table_data = retrieve_database_table(['redcap_projects'])
    projects = table_data['redcap_projects']

    projects.to_csv('stored_data/redcap_projects.csv', index = False)
    return projects

def retrieve_project_data() -> pd.DataFrame:
    """
    Retrieves redcap_projects table from the local storage.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the redcap_projects table
    """
    projects = pd.read_csv('stored_data/redcap_projects.csv')

    return projects

def store_completed_users() -> None:
    """
    Stores the list of users who have completed the study in the local storage. 
    Filters to see if study_complete is 0 or ss_status is 2 or 4.

    Returns:
        None
    """
    projects = retrieve_project_data()
    data_table_list = list(set(projects['data_table']))

    table_data = retrieve_database_table(data_table_list)
    merged_table_data = pd.concat(table_data.values())

    merged_table_data = merged_table_data[((merged_table_data['field_name'] == 'study_complete') & (merged_table_data['value'] == '0')) | ((merged_table_data['field_name'] == 'ss_status') & ((merged_table_data['value'] == '2') | (merged_table_data['value'] == '4')))].reset_index(drop=True)

    merged_table_data = merged_table_data[['project_id', 'record']]

    with open(fr'{rootdir}\\stored_data\\completed_users.csv', 'w', newline='') as f:
        merged_table_data.to_csv(f, index = False)
        
    return None

def retrieve_completed_users() -> pd.DataFrame:
    """
    Retrieves the list of users who have completed the study from the local storage.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the list of users who have completed the study
    """
    completed_users = pd.read_csv(fr'{rootdir}\\stored_data\\completed_users.csv')
    return completed_users

def refresh_all_stored_data() -> None:
    """
    Refreshes all stored data in the stored_data folder.

    Returns:
        None
    """
    path = f'{rootdir}\\stored_data'
    if not os.path.exists(path):
        os.makedirs(path)
    store_data_dictionary()
    store_project_data()
    store_completed_users()
    store_user_roles()
    logging.info("Stored data refreshed.")
    return None

def set_last_checked(filename: str, message: str) -> None:
    """
    Sets the last checked data in the log file.

    Args:
        filename (str): The name of the file to write the message to.
        message (str): The message to write to the log file.

    Returns:
        None
    """

    with open(filename, 'w') as f:
        f.write(message)
    return None

def refresh_log_event_trigger(table_name: str) -> str:
    """
    Refreshes (creates or replaces) a trigger for the log_event table to send data to the Flask server when a new record is created or updated.

    Args:
        table_name (str): The name of the log_event table to create the trigger for.

    Returns:
        str: The SQL command to create the trigger for the log_event table.
    """
    trigger_name = table_name + "_update"
    trigger_comm = f'''CREATE OR REPLACE TRIGGER {trigger_name} AFTER INSERT ON {table_name} FOR EACH ROW BEGIN DECLARE rtn_value text DEFAULT ''; '''
    trigger_comm += f'''SET @json = JSON_OBJECT( 'log_event_id', NEW.log_event_id, 'project_id', NEW.project_id, 'ts', NEW.ts, 'user', NEW.user, 'ip', NEW.ip, 'page', NEW.page, 'event', NEW.event, 'object_type', NEW.object_type, 'sql_log', NEW.sql_log, 'pk', NEW.pk, 'event_id', NEW.event_id, 'data_values', NEW.data_values, 'description', NEW.description, 'legacy', NEW.legacy, 'change_reason', NEW.change_reason); '''
    trigger_comm += f'''IF (NEW.event IN ('UPDATE', 'INSERT') AND NEW.page IN ('DataEntry/index.php') AND NEW.description not in ('Assign record to Data Access Group')) THEN SELECT http_post('https://redcom.hnrc.tufts.edu/flaskApp/receive-from-maria', 'application/json', @json) INTO @rtn_value;  END IF; END; '''
    return trigger_comm

def refresh_data_table_trigger(table_name: str) -> str:
    """
    Refreshes (creates or replaces) a trigger for the data table to send data to the Flask server when a record has completed a study.

    Args:
        table_name (str): The name of the log_event table to create the trigger for.

    Returns:
        str: The SQL command to create the trigger for the log_event table.
    """
    trigger_name = table_name + "_update"
    trigger_comm = f'''CREATE OR REPLACE TRIGGER {trigger_name} AFTER INSERT ON {table_name} FOR EACH ROW BEGIN DECLARE rtn_value text DEFAULT ''; '''
    trigger_comm += f'''SET @json = JSON_OBJECT( 'project_id', NEW.project_id, 'event_id', NEW.event_id, 'record', NEW.record, 'field_name', NEW.field_name, 'value', NEW.value, 'instance', NEW.instance); '''
    trigger_comm += f'''IF (NEW.field_name IN ('study_complete')) THEN SELECT http_post('https://redcom.hnrc.tufts.edu/flaskApp/study-complete', 'application/json', @json) INTO @rtn_value;  END IF; END; '''
    return trigger_comm
					
def refresh_necessary_log_event_triggers(conn: mariadb.connections.Connection) -> str:
    """
    Refreshes triggers for the log_event tables to send data to the Flask server when a new record is created or updated.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server.

    Returns:
        str: A message indicating the completion of the trigger creation process.
    """
    cmd = 'SELECT DISTINCT log_event_table FROM redcap_projects;'
    res = execute_maria_cmd(conn, cmd)
    tables = []
    for table_name in range(len(res)):
        name = list(res[table_name])
        tables.append(''.join(name))
    
    for table in tables:
        trigger_comm = refresh_log_event_trigger(table)
        execute_maria_cmd(conn, trigger_comm)

    timestamp = datetime.datetime.now(datetime.timezone.utc)
    return f"Last complete at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

def refresh_necessary_data_table_triggers(conn: mariadb.connections.Connection) -> str:
    """
    Refreshes triggers for the log_event tables to send data to the Flask server when a new record is created or updated.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server.

    Returns:
        str: A message indicating the completion of the trigger creation process.
    """
    cmd = 'SELECT DISTINCT data_table FROM redcap_projects;'
    res = execute_maria_cmd(conn, cmd)
    tables = []
    for table_name in range(len(res)):
        name = list(res[table_name])
        tables.append(''.join(name))
    
    for table in tables:
        trigger_comm = refresh_data_table_trigger(table)
        execute_maria_cmd(conn, trigger_comm)

    timestamp = datetime.datetime.now(datetime.timezone.utc)
    return f"Last complete at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

def drop_log_event_triggers(conn: mariadb.connections.Connection) -> str:
    """
    Drops triggers for the log_event tables to stop sending data to the Flask server when a new record is created or updated.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server.

    Returns:
        str: A message indicating the completion of the trigger drop process.
    """
    cmd = 'SELECT DISTINCT log_event_table FROM redcap_projects;'
    res = execute_maria_cmd(conn, cmd)
    tables = []
    for table_name in range(len(res)):
        name = list(res[table_name])
        tables.append(''.join(name))

    for table in tables:
        trigger_comm = f'drop trigger if exists {table}_update;'
        execute_maria_cmd(conn, trigger_comm)
    
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    return f"Last complete at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

def drop_data_table_triggers(conn: mariadb.connections.Connection) -> str:
    """
    Drops triggers for the log_event tables to stop sending data to the Flask server when a new record is created or updated.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server.

    Returns:
        str: A message indicating the completion of the trigger drop process.
    """
    cmd = 'SELECT DISTINCT data_table FROM redcap_projects;'
    res = execute_maria_cmd(conn, cmd)
    tables = []
    for table_name in range(len(res)):
        name = list(res[table_name])
        tables.append(''.join(name))

    for table in tables:
        trigger_comm = f'drop trigger if exists {table}_update;'
        execute_maria_cmd(conn, trigger_comm)
    
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    return f"Last complete at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

def refresh_background_trigger() -> None:
    """
    Official process to refresh triggers for the log_event and data tables (used in multithreading).

    Returns:
        None
    """
    conn = connect_to_maria()
    refresh_necessary_log_event_triggers(conn)
    refresh_necessary_data_table_triggers(conn)
    conn.close()
    return None

def retrieve_default_reviewer(project_id: int, form_name: str) -> pd.DataFrame:
    """
    Retrieves the default assignees for a project from the redcap_user_rights table.

    Args:
        project_id (int): The project_id of the project to retrieve the default assignees for.
        form_name (str): The form_name of the form to retrieve the default assignees for.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the default assignees for the project
    """
    default_reviewers = pd.read_csv('stored_data/default_reviewers.csv')
    user_roles = retrieve_user_roles()

    default_reviewers = default_reviewers[default_reviewers['project_id'] == project_id]
    user_roles = user_roles[(user_roles['project_id'] == project_id) & (user_roles['form_name'] == form_name) & (user_roles['permission'] == 2)]
    default_reviewers = default_reviewers.merge(user_roles, on = ['project_id', 'role_name'])

    return default_reviewers

def filter_data_table(data_table: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares the redcap_data table for operations such as joining with log table

    Args:
        data_table (pd.DataFrame): A pandas DataFrame containing the redcap_data table

    Returns:
        pd.DataFrame: A pandas DataFrame containing the filtered redcap_data table
    """        
    data_table['instance'] = data_table['instance'].fillna(1).astype(int)
    data_table['value'] = "'" + data_table['value'].astype(str) + "'"
    data_table = data_table.rename(columns={'record': 'pk'})
    data_table = data_table[['project_id', 'event_id', 'pk', 'instance', 'field_name', 'value']]
    data_table = data_table[data_table['pk'].str.isnumeric()]

    data_table = data_table.astype({'project_id': int, 'event_id': int, 'pk': int, 'instance': int, 'field_name': str, 'value': str})

    return data_table

def retrieve_all_data(pid_list: list) -> pd.DataFrame:
    """
    Retrieves all data from the redcap_data tables for a list of project_ids.

    Args:
        pid_list (list): A list of project_ids to retrieve the data for.

    Returns:
        pd.DataFrame: A pandas DataFrame containing all data for the projects in the list
    """
    project_table = retrieve_project_data()
    project_table = project_table[project_table['project_id'].isin(pid_list)]
    data_tables = project_table['data_table'].unique().tolist()

    table_data = retrieve_database_table(data_tables)

    unioned_data_table = pd.DataFrame(columns=['project_id', 'event_id', 'pk', 'instance', 'field_name', 'value'])
    for data_table in range(len(data_tables)):
        # loads relevant data table

        table = filter_data_table(table_data[data_tables[data_table]])
        unioned_data_table = unioned_data_table.append(table, ignore_index=True)

    return unioned_data_table

def get_log_event_and_data_tables(project_id: int) -> tuple[list, list]:
    """
    Retrieves the log_event and data table from the redcap_projects table.

    Args:
        project_id (int): The project_id of the project to retrieve the tables for.
    
    Returns:
        tuple[list, list]: A tuple containing lists of strings representing the log_event and data table names for the project.
    """
    projects = retrieve_project_data()
    projects = projects[projects['project_id'] == project_id]
    projects = projects[['log_event_table', 'data_table']]

    log_list = list(projects['log_event_table'].unique())
    data_list = list(projects['data_table'].unique())

    return log_list, data_list

def check_for_confirmed_correct_fields(data_dictionary: pd.DataFrame) -> pd.DataFrame:
    """
    Checks the data dictionary for fields that have been confirmed correct in the redcap_data_quality_status and redcap_data_quality_resolutions tables.
    Removes these fields from the data dictionary so they cannot be flagged as missing data. 

    Args:
        data_dictionary (pd.DataFrame): A pandas DataFrame containing the data dictionary

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data dictionary with fields that have been confirmed correct removed
    """
    table_data = retrieve_database_table(['redcap_data_quality_status', 'redcap_data_quality_resolutions'])

    dq_status = table_data['redcap_data_quality_status']
    dq_resolutions = table_data['redcap_data_quality_resolutions']
    dq_status[['record', 'event_id', 'assigned_user_id']] = dq_status[['record', 'event_id', 'assigned_user_id']].apply(pd.to_numeric, errors='coerce')
    dq_resolutions[['res_id', 'status_id', 'user_id']] = dq_resolutions[['res_id', 'status_id', 'user_id']].apply(pd.to_numeric, errors='coerce')

    dq_total = dq_status.merge(dq_resolutions, on = 'status_id')
    dq_total = dq_total[dq_total['response'] == 'CONFIRMED_CORRECT']

    dq_total = dq_total[['project_id', 'event_id', 'field_name']].drop_duplicates()

    data_dictionary = data_dictionary.merge(dq_total, on=['project_id', 'event_id', 'field_name'], how='left', indicator=True)
    data_dictionary = data_dictionary[data_dictionary['_merge'] == 'left_only'].drop('_merge', axis=1)

    return data_dictionary

def get_drw_table() -> pd.DataFrame:
    """
    Retrieves redcap_data_quality_resolutions and redcap_data_quality_status tables and joins them

    Returns:
        pd.DataFrame: A pandas DataFrame containing the merged redcap_data_quality_resolutions and redcap_data_quality_status tables
    """
    table_data = retrieve_database_table(['redcap_data_quality_status', 'redcap_data_quality_resolutions'])

    dq_status = table_data['redcap_data_quality_status']
    dq_resolutions = table_data['redcap_data_quality_resolutions']
    dq_status[['record', 'event_id', 'assigned_user_id']] = dq_status[['record', 'event_id', 'assigned_user_id']].apply(pd.to_numeric, errors='coerce')
    dq_resolutions[['res_id', 'status_id', 'user_id']] = dq_resolutions[['res_id', 'status_id', 'user_id']].apply(pd.to_numeric, errors='coerce')

    dq_total = dq_status.merge(dq_resolutions, on = 'status_id')
    dq_total = dq_total[dq_total[['project_id', 'event_id', 'record', 'instance']].applymap(np.isfinite).all(axis=1)]
    dq_total = dq_total.astype({'project_id': int, 'event_id': int, 'record': int, 'instance': int, 'field_name': str})
    return dq_total

def get_current_drw_count() -> int:
    """
    Retrieves the current number of entries in the redcap_data_quality_status table for use in alerting

    Returns: 
        int: The current number of entries in the redcap_data_quality
    """
    table_data = retrieve_database_table(['redcap_data_quality_status'])

    dq_status = table_data['redcap_data_quality_status']
    status_id_count = len(dq_status.index)

    return status_id_count

def resolve_open_queries(pid_list: list, production_mode: bool = False) -> None:
    """
    Resolves open queries for missing data in the redcap_data_quality_resolutions and redcap_data_quality_status tables by 
        merging with existing data and seeing what has been added.

    Args:
        pid_list (list): A list of project_ids to resolve open queries for
        production_mode (bool, optional): If True, resolves the open queries in production mode. Default is False.

    Returns:
        None
    """
    logging.info("Resolving Open Queries.")
    dq_total = get_drw_table()

    unioned_data_table = retrieve_all_data(pid_list)

    dq_total = dq_total.merge(unioned_data_table, left_on=['project_id', 'record', 'event_id', 'field_name', 'instance'], right_on=['project_id', 'pk', 'event_id', 'field_name', 'instance'], how='left')

    # find fields that have been confirmed correct or have had missing filled in, and close the query 
    confirmed_correct_list = dq_total[dq_total['response'] == 'CONFIRMED_CORRECT'][['project_id', 'event_id', 'field_name']].drop_duplicates()
    confirmed_correct = confirmed_correct_list.merge(dq_total, on=['project_id', 'event_id', 'field_name'], how='left')

    filled_in = dq_total[(dq_total['value'].notnull() & (dq_total['comment'] == "Missing data") & (dq_total['current_query_status'] == "OPEN"))].reset_index(drop=True)
    filled_in = pd.concat([filled_in, confirmed_correct], ignore_index=True)
    
    conn = connect_to_maria()
    for index, row in filled_in.iterrows():
        if production_mode:
            if row['query_status'] == 'OPEN':
                sql_comm = f"UPDATE redcap_data_quality_resolutions SET current_query_status = 'CLOSED' WHERE res_id = {row['res_id']}"
                execute_maria_cmd(conn, sql_comm)
                sql_comm = f"UPDATE redcap_data_quality_status SET query_status = 'CLOSED' WHERE status_id = {row['status_id']}"
                execute_maria_cmd(conn, sql_comm)

                logging.info(f"Resolved query for project_id: {row['project_id']}, record: {row['record']}, event_id: {row['event_id']}, field_name: {row['field_name']}, instance: {row['instance']}")

    conn.commit()
    conn.close()

    return None

def get_thread_id(mess_tables: dict, channel_name: str, user_id: int, assigned_user_id: int, project_id: int) -> int:
    """
    Retrieves the thread_id of the new thread to be created in the redcap_messages_threads table.
    
    Args:
        mess_tables (dict): A dictionary containing the tables necessary for the messaging system
        channel_name (str): The name of the channel the message is being sent in
        user_id (int): The user_id of the author of the message
        assigned_user_id (int): The user_id of the recipient of the message
        project_id (int): The project_id of the project the message is being sent in

    Returns:
        int: The thread_id of the new thread to be created
    """
    messages_table = mess_tables['redcap_messages']
    recipients_table = mess_tables['redcap_messages_recipients']
    threads_table = mess_tables['redcap_messages_threads']
    thread_id = 0

    # checks if the recipient is involved in a workflow thread
    if (np.float64(assigned_user_id) in recipients_table['recipient_user_id'].to_list()):
        recipient_threads = list(recipients_table[recipients_table['recipient_user_id'] == assigned_user_id]['thread_id'])
        workflow_threads = list(threads_table[(threads_table['channel_name'].isin([channel_name])) & (threads_table['project_id'] == project_id)]['thread_id'])
        recipient_workflow_threads = list(set(recipient_threads) & set(workflow_threads))

        if (len(recipient_workflow_threads) > 0):

            # then checks if the author is involved in one of the same workflow threads
            if ((np.float64(user_id) in messages_table['author_user_id'].to_list())):
                author_threads = list(messages_table[(messages_table['author_user_id'] == user_id)]['thread_id'])
                workflow_threads = list(threads_table[(threads_table['channel_name'].isin([channel_name])) & (threads_table['project_id'] == project_id)]['thread_id'])
                author_workflow_threads = list(set(author_threads) & set(workflow_threads))

                if (len(author_workflow_threads) > 0):
                    thread_id = list(set(recipient_workflow_threads) & set(author_workflow_threads))[0]
                else:
                    thread_id = max(threads_table['thread_id']) + 1
            
            # if not, creates a new thread
            else:
                thread_id = max(threads_table['thread_id']) + 1
        
        # if not, creates a new thread
        else:
            thread_id = max(threads_table['thread_id']) + 1

    # if not, creates a new thread
    else:
        thread_id = max(threads_table['thread_id']) + 1

    return thread_id

def get_username(mess_tables: dict, recipient_user_id: int) -> str:
    """
    Retrieves the username of the recipient of the message from the redcap_user_information table.
    
    Args:
        mess_tables (dict): A dictionary containing the tables necessary for the messaging system
        recipient_user_id (int): The user_id of the recipient of the message

    Returns:
        str: The username of the recipient of the message
    """
    user_info = mess_tables['redcap_user_information']
    username = user_info[user_info['ui_id'] == recipient_user_id]['username']
    return username.iloc[0]

def get_app_title(mess_tables: dict, project_id: int) -> str:
    """
    Retrieves the official title of the project from the redcap_projects table.

    Args:
        mess_tables (dict): A dictionary containing the tables necessary for the messaging system
        project_id (int): The project_id of the project to retrieve the title of

    Returns:
        str: The official title of the project
    """
    project_info = mess_tables['redcap_projects']
    app_title = project_info[project_info['project_id'] == project_id]['app_title']
    return app_title.iloc[0]

def find_version_history() -> str:
    """
    Retrieves the build of the latest updated redcap version from the redcap_history_version table.

    Returns:
        str: The build of the latest updated redcap version
    """
    version_table = retrieve_database_table(['redcap_history_version'])
    redcap_version = version_table['redcap_version'].iloc[-1]
    return redcap_version

def create_msg_body(app_title: str, redcap_version:str, project_id: int, status: str, recipient_user_id: int, status_id: int, username: str, sent_time: datetime.datetime) -> str:
    """
    Creates the message body to be sent to the recipient via the REDCap messenger, including a link to the workflow table.

    Args:
        app_title (str): The official title of the project
        redcap_version (str): The current version of the redcap server
        project_id (int): The project_id of the project the message is being sent in
        status (str): The status of the data query
        recipient_user_id (int): The user_id of the recipient of the message
        status_id (int): The status_id of the data query
        username (str): The username of the author of the message
        sent_time (datetime.datetime): The time the message was sent
    
    Returns:
        str: The message body to be sent to the recipient via the REDCap messenger, including a link to the workflow table
    """
    if (status is None):
        status = ''
    message_body = '''[{"msg_body":'''
    message_body += fr'''"You have been assigned to a data query that was just opened in the REDCap project \"<b>{app_title}<\/b>\".<br><br>Open the data query assigned to you: '''
    message_body += fr'''https:\/\/rctest.hnrc.tufts.edu\/redcap_v{redcap_version}\/DataQuality\/resolve.php?pid={project_id}&status_type=OPEN&field_rule_filter=&assigned_user_id={recipient_user_id}"'''
    # message_body += fr'''https:\/\/rctest.hnrc.tufts.edu\/redcap_v{redcap_version}\/DataQuality\/resolve.php?pid={project_id}&status_type={status}&assigned_user_id={recipient_user_id}&status_id={status_id}"'''
    message_body += fr''',"msg_end":"","important":"0","action":"post","user":"{username}","ts":"{sent_time.strftime('%m-%d-%Y %H:%M')}"'''
    message_body += """}]"""
    return message_body

def get_arm_data() -> pd.DataFrame:
    """
    Retrieves and merges redcap_events_metadata and redcap_events_arms tables to match event_id and event names

    Returns:
        pd.DataFrame: A pandas DataFrame containing the merged redcap_events_metadata and redcap_events_arms tables
    """
    table_data = retrieve_database_table(['redcap_events_metadata', 'redcap_events_arms', 'redcap_events_forms', 'redcap_events_repeat'])

    metadata = table_data['redcap_events_metadata']
    arms = table_data['redcap_events_arms']
    forms = table_data['redcap_events_forms']
    repeat = table_data['redcap_events_repeat']
    
    event_arms_table = (metadata.merge(arms, how='left', on='arm_id')) 
    event_arms_table = event_arms_table.merge(forms, how='left', on='event_id')
    event_arms_table = event_arms_table.merge(repeat, how='left', on=['event_id', 'form_name'])
    event_arms_table['event_name'] = (event_arms_table['descrip'].str.lower().str.replace(':','').str.replace(' ', '_').str.replace('-', '')) +"_"+ (event_arms_table['arm_name'].str.lower().str.replace(' ', '_').str.replace('-', ''))

    return event_arms_table

def send_periodic_email() -> None:
    """
    Sends an email to all users who have unresolved data quality queries in the system. The email is sent once every 24 hours once the interval is triggered.

    Returns:
        None
    """
    with open('stored_data/last_email_blast.log', 'r') as file:
        file_contents = file.read()
    
    timestamp = datetime.datetime.strptime(file_contents, '%Y-%m-%d %H:%M:%S')
    time_diff = datetime.datetime.now() - timestamp

    logging.info(f"Time since last email blast: {time_diff}")

    if time_diff > datetime.timedelta(hours=24):
        drw_table = get_drw_table()
        user_info = get_user_information()
        redcap_version = find_version_history()

        user_info = user_info[['ui_id', 'username', 'user_email']]
        drw_table = drw_table.merge(user_info, left_on='assigned_user_id', right_on='ui_id', how='left')
        drw_table = drw_table[drw_table['current_query_status'] != 'CLOSED']

        drw_table['ts'] = pd.to_datetime(drw_table['ts']).dt.tz_localize('UTC')
        current_time = datetime.datetime.now(datetime.timezone.utc)
        drw_table['time_since'] = current_time - drw_table['ts']
        drw_table = drw_table[drw_table['time_since'] > datetime.timedelta(hours=24)]
        
        drw_table = drw_table.groupby(['project_id', 'assigned_user_id', 'username', 'user_email']).size().reset_index(name='count')

        for index, row in drw_table.iterrows():
            link = f"""https://rctest.hnrc.tufts.edu/redcap_v{redcap_version}/DataQuality/resolve.php?pid={row['project_id']}&status_type=OPEN&field_rule_filter=&assigned_user_id={row['assigned_user_id']} \n\n"""
            message = f"Hello {row['username']},\n\nYou have {row['count']} unresolved data quality queries in project {row['project_id']}. Please log in to the system to resolve them.\n\n {link}Thank you,\n\nThe REDCap Data Quality Team"
            send_email(message, [row['user_email']])
        
        with open('stored_data/last_email_blast.log', 'w') as file:
            file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return None

def check_drw_enabled(pid_list: list) -> None:
    """
    Checks if the data resolution workflow parameter is enabled for the projects in the list.

    Args:
        pid_list (list): A list of project_ids to check the data resolution workflow for

    Returns:
        None
    """
    project_table = retrieve_project_data()
    project_table = project_table[['project_id', 'data_resolution_enabled']]
    project_table = project_table[project_table['project_id'].isin(pid_list)]
    
    for index, row in project_table.iterrows():
        if row['data_resolution_enabled'] == 2:
            pass
        else:
            send_error_email(message=f"Data resolution workflow is not enabled for project {row['project_id']}.")
            logging.info(f"Data resolution workflow is not enabled for project {row['project_id']}.")

    return None

def filter_log_event_table(log_event_table: pd.DataFrame) -> pd.DataFrame:
    """
    Filters the log_event table to only hold Data Entry pages rather than administrative logging.

    Args:
        log_event_table (pd.DataFrame): A pandas DataFrame containing the log_event table

    Returns:
        pd.DataFrame: A pandas DataFrame containing the filtered log_event table
    """
    data_entry_table = log_event_table[
        (log_event_table['description'].isin(["Update record", "Create record"])) &
        (log_event_table['page'].isin(["DataEntry/index.php", "ProjectGeneral/create_project.php"])) &
        (log_event_table['object_type'] == "redcap_data") &
        (log_event_table['data_values'].notna() &
        log_event_table['sql_log'].notna())
    ]


    # data_values and sql_log are all grouped up in one row per form submission as a string. Splits these strings into lists for easier manipulation
    data_entry_table['data_values'] = data_entry_table['data_values'].str.split(',\n')
    data_entry_table['sql_log'] = data_entry_table['sql_log'].str.split(';\n')
    
    # sets default instance to 1 rather than None
    data_entry_table['instance'] = 1

    # if the data_values is of an instance greater than 1, seperates the instance into a seperate column and removes it from data_values so data_values and sql_log have the same length
    for index, row in data_entry_table.iterrows():
        if isinstance(row['data_values'], list) and len(row['data_values']) > 0:
            first_item = row['data_values'][0]
            if first_item.startswith('[instance = '):
                instance_value = int(first_item.split('=')[1].strip(']'))
                data_entry_table.at[index, 'instance'] = instance_value
                
                data_value_without_instance = row['data_values'][1:]
                data_entry_table.at[index, 'data_values'] = data_value_without_instance

    # mismatched_rows = data_entry_table[data_entry_table['data_values'].apply(len) != data_entry_table['sql_log'].apply(len)]
    # mismatched_rows['len_data_values'] = mismatched_rows['data_values'].apply(len)
    # mismatched_rows['len_sql_log'] = mismatched_rows['sql_log'].apply(len)

    # display(mismatched_rows)

    data_entry_table = data_entry_table.explode(['data_values', 'sql_log']).reset_index(drop=True)

    # splits field_name and value into individual columns and sets type for relevant columns
    # print(data_entry_table)
    if not data_entry_table.empty:
        data_entry_table[['field_name', 'value']] = data_entry_table['data_values'].str.split(' = ',expand=True)
        data_entry_table = data_entry_table.astype({'project_id': int, 'event_id': int, 'pk': int, 'instance': int, 'field_name': str, 'value': str})


    return data_entry_table

def prepare_mess_data(mess_tables: dict, author_user_id: int, recipient_user_id: int, sent_time: datetime.datetime, project_id: int, status: str, status_id: int) -> list:
    """
    Prepares the necessary data to be entered into the redcap_messages, redcap_messages_recipients, and redcap_messages_threads tables.

    Args:
        mess_tables (dict): A dictionary containing the tables necessary for the messaging system
        author_user_id (int): The user_id of the author of the message
        recipient_user_id (int): The user_id of the recipient of the message
        sent_time (datetime.datetime): The time the message was sent
        project_id (int): The project_id of the project the message is being sent in
        status (str): The status of the data query
        status_id (int): The status_id of the data query
    
    Returns:
        list: A list of tuples containing the necessary data to be entered into the redcap_messages, redcap_messages_recipients, and redcap_messages_threads tables

    """
    # sets necessary field values for messages table
    if (len(mess_tables['redcap_messages']) == 0):
        message_id = 1
    else:
        message_id = max(mess_tables['redcap_messages']['message_id']) + 1
    attachment_doc_id = None
    stored_url = None

    app_title = get_app_title(mess_tables, project_id)
    channel_name = f'Assigned to a data query in project {project_id}: {app_title}'
    redcap_version = find_version_history()

    # sets necessary field values for threads table
    thread_id = get_thread_id(mess_tables, channel_name, author_user_id, recipient_user_id, project_id)
    type = 'CHANNEL'
    invisible = 0
    archived = 0

    update_thread = False
    # checks if a new thread is created. 
    if (thread_id == (max(mess_tables['redcap_messages_threads']['thread_id']) + 1)):
        update_thread = True
    
    # sets necessary field values for recipients table
    if (thread_id > max(mess_tables['redcap_messages_recipients']['thread_id'])):
        recipient_id = max(mess_tables['redcap_messages_recipients']['recipient_id']) + 1
    else:
        rec_index = list(mess_tables['redcap_messages_recipients']['thread_id']).index(thread_id)
        recipient_id = mess_tables['redcap_messages_recipients']['recipient_id'][rec_index]
    all_users = 0
    prioritize = 0
    conv_leader = 1

    # message sent in messenger
    username = get_username(mess_tables, recipient_user_id)
    message_body = create_msg_body(app_title, redcap_version, project_id, status, recipient_user_id, status_id, username, sent_time)
    
    # organizes full row of data for input in respective tables
    threads_tuple = (thread_id, type, channel_name, invisible, archived, project_id)
    messages_tuple = (message_id, thread_id, sent_time.strftime('%Y-%m-%d %H:%M:%S'), author_user_id, message_body, attachment_doc_id, stored_url)
    recipients_tuple = (recipient_id, thread_id, recipient_user_id, all_users, prioritize, conv_leader)

    data_rows = [update_thread, threads_tuple, messages_tuple, recipients_tuple]

    return data_rows

def prepare_drw_data(dq_tables: dict, ts: datetime.datetime, project_id: int, event_id: int, hnrcid: int, field_name: str, value: str, repeat_instance: int, assigned_user_id: int, user_id: int, comment: str) -> list:
    """
    Prepares the necessary data to be entered into the redcap_data_quality_status and redcap_data_quality_resolutions tables.

    Args:
        dq_tables (dict): A dictionary containing the tables necessary for the data resolution workflow
        ts (datetime.datetime): The time the data query was entered
        project_id (int): The project_id of the data entry
        event_id (int): The event_id of the data entry
        hnrcid (int): The hnrcid of the data entry
        field_name (str): The field_name of the data entry
        value (str): The value of the data entry
        repeat_instance (int): The repeat_instance of the data entry
        assigned_user_id (int): The user_id of the recipient of the data query
        user_id (int): The user_id of the author of the data query
        comment (str): The comment of the data query
    
    Returns:
        list: A list of tuples containing the necessary data to be entered into the redcap_data_quality_status and redcap_data_quality_resolutions tables
    """
    # DQ (data quality) tables: redcap_data_quality_status, redcap_data_quality_resolutions
    # DQ_status is where the individual flags are housed
    # DQ_resolutions is where the Data Resolution workflow is housed, using DQ_status entries

    # sets up fields for entry in DQ Status and Resolution tables
    # many fields are pre-set, while others can be passed in, such as the specific entries to modify
    # sets necessary field values for Status table
    if (len(dq_tables['redcap_data_quality_status']) == 0):
        status_id = 1
    else:
        status_id = max(dq_tables['redcap_data_quality_status']['status_id']) + 1
    rule_id = None
    pd_rule_id = None
    non_rule = 1
    status = None
    exclude = 0
    query_status = 'OPEN'
    repeat_instrument = None

    # sets necessary field values for Resolution table
    if (len(dq_tables['redcap_data_quality_resolutions']) == 0):
        res_id = 1
    else:
        res_id = max(dq_tables['redcap_data_quality_resolutions']['res_id']) + 1
    response_requested = 1
    response = None
    current_query_status = 'OPEN'
    upload_doc_id = None
    field_comment_edited = 0

    if pd.isna(repeat_instrument):
        repeat_instrument = None
    
    # organizes full row of data for input in respective tables
    status_tuple = (status_id, rule_id, pd_rule_id, non_rule, project_id, hnrcid, event_id, field_name, repeat_instrument, repeat_instance, status, exclude, query_status, assigned_user_id)
    resolution_tuple = (res_id, status_id, ts.strftime('%Y-%m-%d %H:%M:%S'), user_id, response_requested, response, comment, current_query_status, upload_doc_id, field_comment_edited)

    data_rows = [status_tuple, resolution_tuple]

    return data_rows

def get_entry_of_outlier(conn: mariadb.connections.Connection, project_id: int, event_id: int, hnrcid: int, form_name: str, field_name: str, value: str, repeat_instance: int) -> tuple[int,str,str]:
    """
    Retrieves the user_id and username of the data entrist by filtering on the hnrcid, event_id, field_name, and instance attributes.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server
        project_id (int): The project_id of the data entry
        event_id (int): The event_id of the data entry
        hnrcid (int): The hnrcid of the data entry
        form_name (str): The form_name of the data entry
        field_name (str): The field_name of the data entry
        value (str): The value of the data entry
        repeat_instance (int): The repeat_instance of the data entry

    Returns:
        tuple[int,str,str]: A tuple containing the user_id, username, and email of the data entry
    """
    # imported studies have multiple project_ids and therefore need to be joined before processing
    log_event_tables, data_tables = get_log_event_and_data_tables(conn, project_id)
    table_name = []
    for log_event_table in range(len(log_event_tables)):
        table_name.append(log_event_tables[log_event_table])
    table_name.append('redcap_user_information')
    for data_table in range(len(data_tables)):
        table_name.append(data_tables[data_table])
    col_names = get_colnames(conn, table_name)
    table_data = get_table_data(conn, col_names)

    unioned_log_table = pd.DataFrame(columns=col_names[table_name[0]])
    unioned_data_table = pd.DataFrame(columns=['project_id', 'event_id', 'pk', 'instance', 'field_name', 'value'])

    for log_event_table in range(len(log_event_tables)):
        # loads relevant log table and splits multi-entries into individual rows
        table = filter_log_event_table(table_data[log_event_tables[log_event_table]])
        unioned_log_table = unioned_log_table.append(table, ignore_index=True)
    
    for data_table in range(len(data_tables)):
        # loads relevant data table
        table = filter_data_table(table_data[data_tables[data_table]])
        unioned_data_table = unioned_data_table.append(table, ignore_index=True)
    
    # loads user info table and merges with log table to find user_id
    user_info = table_data['redcap_user_information'][['ui_id', 'username', 'user_email']]
    unioned_log_table = (unioned_log_table.merge(user_info, left_on = 'user', right_on = 'username')).drop(columns=['username'])

    data_dictionary = retrieve_data_dictionary()
    data_dictionary = data_dictionary[['project_id', 'field_name','form_name']]
    unioned_data_table = (unioned_data_table.merge(data_dictionary, on = ['project_id', 'field_name']))

    cols = ['project_id', 'event_id', 'pk', 'instance', 'field_name', 'value']
    
    unioned_super_table = unioned_data_table.merge(unioned_log_table, left_on=cols, right_on=cols)

    # display(unioned_super_table)

    # table with all of that patient's data entries for that project. requires a user to proceed. needs to be one entry. 
    # outlier['event_id'] needs to be equal to event_id
    # outlier['instance'] needs to be equal to repeat_instance if instance_value exists
    # outlier['pk'] needs to be equal to hnrcid
    # if there are more than one user for that hnrcid for that event, make outlier['user'] whoever has greater value_counts with that hnrcid
    # if the field_name exists for that event and pk, make outlier['field_name'] the field name. 

    # print(f"{project_id} {event_id} {hnrcid} {field_name} {value} {repeat_instance}")

    outlier = unioned_super_table.copy()
    if len(outlier[(outlier['form_name'] == form_name)]) > 0:
        outlier = outlier[(outlier['form_name'] == form_name)]
        
    if len(outlier[(outlier['event_id'].astype(int) == int(event_id))]) > 0:
        outlier = outlier[(outlier['event_id'].astype(int) == int(event_id))]

    if len(outlier[(outlier['field_name'] == field_name)]) > 0:
        outlier = outlier[(outlier['field_name'] == field_name)]

    if len(outlier[(outlier['pk'].astype(int) == int(hnrcid))]) > 0:
        outlier = outlier[(outlier['pk'].astype(int) == int(hnrcid))]

    if len(outlier[(outlier['instance'].astype(int) == int(repeat_instance))]) > 0:
        outlier = outlier[(outlier['instance'].astype(int) == int(repeat_instance))]

    # display(outlier)

    if len(outlier) == 0:
        outlier = retrieve_default_reviewer(project_id, form_name).reset_index(drop=True)
        first_entry = outlier.iloc[0]
        official_user_id = int(first_entry['ui_id'])
        official_username = str(first_entry['user'])
        official_email = str(first_entry['user_email'])
    else:
        outlier = outlier.reset_index(drop=True)
        first_entry = outlier.iloc[0]

        official_user_id = int(first_entry['ui_id'])
        official_username = str(first_entry['user'])
        official_email = str(first_entry['user_email'])


    return official_user_id, official_username, official_email

def find_outliers_chauvenet(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finds outliers in a DataFrame using Chauvenet's criterion.
    Pseudocode (chau_peirce_thomson.pdf):
    1. Calculate mean and std
    2. If n · erfc(|value - mean|/ std) < 1/2 then reject value
    3. Repeat steps 1 and 2
    4. Report final mean, std, and n

    Args:
        df (pd.DataFrame): The DataFrame to find outliers in

    Returns:
        pd.DataFrame: A DataFrame containing only the outliers
    """
    N = len(df)
    mean = df['value'].mean()
    std_dev = df['value'].std()

    df['z_score'] = (np.abs(df['value'] - mean)) / std_dev

    # scipy.special.erfc - complementary error function.
    df['probability'] = erfc(df['z_score'])

    # probability threshold
    chauvenet_criterion = 1 / (2 * N)

    df['outlier'] = df['probability'] < chauvenet_criterion

    outlier = df[df['outlier']]
    
    return outlier

def pierce_critical_value(N) -> float:
    """
    Approximate critical value based on dataset size N.
    Pierce's criterion uses lookup tables to get the exact critical value.
    Here, we use a rough approximation based on the dataset size.

    Args:
        N (int): The number of data points in the dataset
    
    Returns:
        float: The critical value for Pierce's criterion
    """
    # This is a rough approximation. Normally you'd look up exact values.
    if N < 3:
        return np.inf  # No outliers can be detected if less than 3 points
    return 3 + 1.1 * np.log(N)  # Increase with log(N) for approximation

def find_outliers_pierce(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finds outliers in a DataFrame using Pierce's criterion.
    Pseudocode (chau_peirce_thomson.pdf):
    1. Calculate mean and std
    2. Calculate Z-scores for each data point
    3. Find the most extreme outlier (highest Z-score)
    4. If the Z-score is greater than the critical value, remove the outlier
    5. Repeat steps 1-4 until no more outliers are found

    Args:
        df (pd.DataFrame): The DataFrame to find outliers in

    Returns:
        pd.DataFrame: A DataFrame containing only the outliers
    """
    df_clean = df.copy()  # Work on a copy of the dataframe
    N = len(df_clean)

    while N > 2:  # Stop if less than 3 points remain
        mean = df_clean['value'].mean()
        std_dev = df_clean['value'].std()

        # Z-scores for each data point
        z_scores = np.abs((df_clean['value'] - mean) / std_dev)

        # Find the most extreme outlier (highest Z-score)
        max_z_score = z_scores.max()

        # Get the Pierce's critical value for the current number of data points
        critical_z = pierce_critical_value(N)

        # Check if the most extreme point is an outlier
        if max_z_score > critical_z:
            # Remove the outlier from the dataset
            df_clean = df_clean[z_scores != max_z_score]
            N = len(df_clean)
        else:
            # No more outliers to remove, break the loop
            break
    
    # Return the dataframe of outliers (original points minus the cleaned points)
    outliers_df = df[~df.index.isin(df_clean.index)]
    
    return outliers_df

def qq_calc_cooks_dist(df_group: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Cook's distance for a group of data points.

    Args:
        df_group (pd.DataFrame): A group of data points to calculate Cook's distance for

    Returns:
        pd.DataFrame: The original DataFrame with Cook's distance added as a new column
    """
    # Calculate Cook's distance
    if len(df_group) > 1:
        lm = ols('value ~ norm_quants', data=df_group).fit()
        infl = lm.get_influence()
        df_group['cooksd'] = infl.cooks_distance[0]
    else:
        df_group['cooksd'] = np.nan
    return df_group

def find_outliers_qq(df: pd.DataFrame) -> pd.DataFrame:
    """
    Finds outliers in a DataFrame using QQ plots and Cook's distance.

    Args:
        df (pd.DataFrame): The DataFrame to find outliers in.

    Returns:
        pd.DataFrame: A DataFrame containing only the outliers.
    """
    # Ensure 'value' is numeric to avoid issues with StandardScaler and other numerical operations
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Group solo points (where the group size is 1)
    solo_points = df.groupby('field_name').filter(lambda x: len(x) == 1)
    df = df.groupby('field_name').filter(lambda x: len(x) > 1)

    # Add z-score, probabilities, normal quantiles, and Cook's distance
    df['zscore'] = df.groupby('field_name')['value'].transform(lambda x: StandardScaler().fit_transform(x.values.reshape(-1, 1)).flatten())
    df['probs'] = df.groupby('field_name')['value'].transform(lambda x: np.arange(1, len(x)+1) / (len(x)+1))
    df['norm_quants'] = df.groupby('field_name')['value'].transform(lambda x: norm.ppf(np.arange(1, len(x)+1) / (len(x)+1), np.mean(x), np.std(x)))
    
    # Apply QQ calculation with Cook's distance
    df = df.groupby('field_name').apply(qq_calc_cooks_dist).reset_index(drop=True)
    
    # Rejoin solo points
    df = pd.concat([df, solo_points], ignore_index=True)

    # Sort by absolute z-score
    df = df.sort_values(by=['field_name', 'zscore'], ascending=[True, False], key=lambda x: abs(x) if x.name == 'zscore' else x)
    
    # Prepare for loop
    vars_unique = df['field_name'].unique()
    df['trim_count'] = np.nan
    df['qq_step'] = np.nan
    df['qq_step_cd'] = np.nan

    for v in vars_unique:
        var_data = df[df['field_name'] == v].copy()
        if len(var_data) > 3:
            slopes = pd.DataFrame(columns=['trim_count', 'intercept', 'slope'])
            
            for i in range(len(var_data) - 2):
                x = var_data.iloc[i:].copy()
                x['norm_quants'] = norm.ppf((np.arange(1, len(x)+1) / (len(x)+1)), np.mean(x['value']), np.std(x['value']))
                coeff = np.polyfit(np.sort(x['value']), x['norm_quants'], 1)
                slopes.loc[i] = [i, coeff[1], coeff[0]]
            
            # Get magnitude of change from slope to slope
            slopes['step'] = slopes['slope'].diff().abs()
            slopes = slopes.dropna(subset=['step'])
            
            # Calculate Cook's distance for slopes
            if not slopes.empty:
                slopes['cooksd'] = sm.OLS(slopes['step'], sm.add_constant(slopes['trim_count'])).fit().get_influence().cooks_distance[0]
            
            # Save data
            rep_len = len(var_data) - len(slopes)
            df.loc[df['field_name'] == v, 'qq_step'] = list(slopes['step']) + [np.nan] * rep_len
            df.loc[df['field_name'] == v, 'qq_step_cd'] = list(slopes['cooksd']) + [np.nan] * rep_len
            df.loc[df['field_name'] == v, 'trim_count'] = list(slopes['trim_count']) + [np.nan] * rep_len

    # Calculate outlier indicators based on Cook's distance (comparison is now within group)
    df['qq_out'] = df.groupby('field_name')['qq_step'].transform(lambda x: x > np.nanmean(df['qq_step_cd']))
    
    # Fill missing values with False (not outliers)
    df['qq_out'].fillna(False, inplace=True)

    # Extract only the outliers
    outliers = df[df['qq_out']].copy()
    return outliers

def create_data_res_workflow_entry(conn: mariadb.connections.Connection, project_id: int, event_id: int, hnrcid: int, field_name: str, value: str, repeat_instance: int, assigned_user_id: int, user_id: int, ping: bool, comment: str, ts: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)) -> None:
    """
    Creates a new data entry in the redcap_data_quality_status and redcap_data_quality_resolutions tables.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server
        project_id (int): The project_id of the data entry
        event_id (int): The event_id of the data entry
        hnrcid (int): The hnrcid of the data entry
        field_name (str): The field_name of the data entry
        value (str): The value of the data entry
        repeat_instance (int): The repeat_instance of the data entry
        assigned_user_id (int): The user_id of the recipient of the data query
        user_id (int): The user_id of the author of the data query
        ping (bool): A boolean indicating whether to send a message to the recipient
        comment (str): The comment of the data query
        ts (datetime.datetime, optional): The time the data query was entered (default is the current time)

    Returns:
        None
    """
    # redcap tables to be modified
    dq_table_names = ['redcap_data_quality_status', 'redcap_data_quality_resolutions']
    mess_table_names = ['redcap_messages_threads', 'redcap_messages', 'redcap_messages_recipients', 'redcap_user_information', 'redcap_projects']

    dq_table_cols = get_colnames(conn, dq_table_names)
    mess_table_cols = get_colnames(conn, mess_table_names)

    dq_tables = get_table_data(conn, dq_table_cols)
    mess_tables = get_table_data(conn, mess_table_cols)

    drw_rows = prepare_drw_data(dq_tables, ts, project_id, event_id, hnrcid, field_name, value, repeat_instance, assigned_user_id, user_id, comment)
    mess_rows = prepare_mess_data(mess_tables, author_user_id = user_id, recipient_user_id = assigned_user_id, sent_time = ts, project_id = project_id, status = drw_rows[0][10], status_id = drw_rows[0][0])
    update_thread = mess_rows.pop(0)

    mess_table_names.remove('redcap_user_information')
    mess_table_names.remove('redcap_projects')
    
    # for both DQ tables, creates a row with all the necessary fields entered
    for table in range(len(dq_table_names)):
        table_name = dq_table_names[table]
        col_names = dq_table_cols[table_name]
        num_qs = ('?, ' * len(col_names))[:-2]
        sql_comm = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({num_qs})"
        drw_row = drw_rows[table]
        execute_maria_cmd(conn, sql_comm, drw_row)

    # for three messages tables, creates a row with all the necessary fields entered. 
    for table in range(len(mess_table_names)):
        table_name = mess_table_names[table]
        col_names = mess_table_cols[table_name]
        num_qs = ('?, ' * len(col_names))[:-2]
        sql_comm = f"INSERT INTO {table_name} ({', '.join(col_names)}) VALUES ({num_qs})"
        mess_row = mess_rows[table]

        # if set to ping, and if one of the messages tables, sends the message
        if ping:
            if ((table_name == 'redcap_messages') or (update_thread & (table_name == 'redcap_messages_recipients')) or (update_thread & (table_name == 'redcap_messages_threads'))):
                execute_maria_cmd(conn, sql_comm, mess_row)

    return None


def check_existing_drw_entry(project_id: int, event_id: int, hnrcid: int, field_name: str, official_user_id: int, repeat_instance: int) -> pd.DataFrame:
    """
    Searches redcap_data_quality_status table to see if a DRW entry exists for that record already. 
    Prevents key-errors as duplicate entries cannot be added to DRW.  

    Args:
        project_id (int): The project_id of the data entry
        event_id (int): The event_id of the data entry
        hnrcid (int): The hnrcid of the data entry
        field_name (str): The field_name of the data entry
        official_user_id (int): The user_id of the recipient of the data query
        repeat_instance (int): The repeat_instance of the data entry
    
    Returns:
        pd.DataFrame: A DataFrame containing the existing DRW entry
    """
    table_data = retrieve_database_table(['redcap_data_quality_status'])

    dq_status = table_data['redcap_data_quality_status']
    dq_status[['record', 'event_id', 'assigned_user_id']] = dq_status[['record', 'event_id', 'assigned_user_id']].apply(pd.to_numeric, errors='coerce')

    dq_status = dq_status[
        (dq_status['record'].astype(int) == int(hnrcid)) &
        (dq_status['project_id'].astype(int) == int(project_id)) &
        (dq_status['event_id'].astype(int) == int(event_id)) &
        (dq_status['assigned_user_id'].astype(int) == int(official_user_id)) &
        (dq_status['instance'].astype(int) == int(repeat_instance)) &
        (dq_status['field_name'] == field_name)]

    return dq_status

def data_workflow_submission(project_id: int, event_id: int, hnrcid: int, form_name: str, field_name: str, value: str, repeat_instance: int, ping: bool = True) -> None:
    """
    Submits a new data entry to the redcap_data_quality_status and redcap_data_quality_resolutions tables after checking for duplicates.

    Args:
        project_id (int): The project_id of the data entry
        event_id (int): The event_id of the data entry
        hnrcid (int): The hnrcid of the data entry
        form_name (str): The form_name of the data entry
        field_name (str): The field_name of the data entry
        value (str): The value of the data entry
        repeat_instance (int): The repeat_instance of the data entry
        ping (bool, optional): A boolean indicating whether to send a message to the recipient (default is True)

    Returns:
        None
    """
    conn = connect_to_maria()

    official_user_id, username, email = get_entry_of_outlier(conn, project_id, event_id, hnrcid, form_name, field_name, value, repeat_instance)
    log_msg = f'project_id {project_id}, hnrcid {hnrcid}, event_id {event_id}, repeat_instance {repeat_instance}, field_name {field_name}, value {value}, user {official_user_id}: {username} {email}. '

    dq_status = check_existing_drw_entry(project_id, event_id, hnrcid, field_name, official_user_id, repeat_instance)

    if (len(dq_status.index) == 0):
        try:
            create_data_res_workflow_entry(conn, project_id, event_id, hnrcid, field_name, value, repeat_instance, official_user_id, official_user_id, comment = f"Flagged Value", ping = ping)
            log_msg += "Created a Data Resolution Workflow entry. "
            if ping:
                log_msg += f"Sent ping to user {official_user_id}: {username}"
                # send_email("Flagged Value", [email])
            else:
                log_msg += f"Did not ping user {official_user_id}: {username}"
        except:
            log_msg += "Already exists as a Data Resolution Workflow entry. "
    else:
        log_msg += "Already exists as a Data Resolution Workflow entry. "
    
    logging.info(log_msg)
    
    conn.commit()       # commit changes to the database so they can be officially submitted once the process is over
    conn.close()        # connection MUST be closed at end of process so it is not infinitely hanging

    return None

def operate_outlier_qc(merged_data_table: pd.DataFrame, data_entry_table: pd.DataFrame, outlier_method: str = 'Chauvanet', production_mode: bool = False) -> None:
    """
    Operates the outlier detection and submission process for a given DataFrame.

    Args:
        merged_data_table (pd.DataFrame): The DataFrame containing all the data for the relevant project
        data_entry_table (pd.DataFrame): The DataFrame containing the data that has been submitted
        outlier_method (str, optional): The method to use for outlier detection (default is 'Chauvanet')
        production_mode (bool, optional): A boolean indicating whether to run in production mode (default is False)

    Returns:
        None
    """
    # Fetches the data dictionary and merge with the data entry table
    data_dictionary = get_data_dictionary()
    data_dictionary = data_dictionary[['project_id', 'field_name','form_name']]
    data_entry_table = (data_entry_table.merge(data_dictionary, on = ['project_id', 'field_name']))

    # display(data_entry_table)

    field_name = data_entry_table['field_name'].iloc[0]
    project_id = data_entry_table['project_id'].iloc[0]
    event_id = data_entry_table['event_id'].iloc[0]


    drw_table = get_drw_table()

    merged_data_table['instance'] = merged_data_table['instance'].fillna(1).astype(int)
    merged_data_table['outlier'] = False
    merged_data_table = merged_data_table.astype({'project_id': int, 'event_id': int, 'record': int, 'instance': int, 'field_name': str})
    # marks rows that have drw entries
    merged_data_table = merged_data_table.merge(drw_table, left_on = ['project_id', 'record', 'event_id', 'field_name', 'instance'], right_on = ['project_id', 'record', 'event_id', 'field_name', 'instance'], how='left', indicator=True)
    
    # Parses through DataFrame based on each field_name to check for outliers
    df_list = []
    cols = list(data_entry_table['field_name'])
    for col in cols:
        df = merged_data_table[merged_data_table['field_name'] == col]
        df['value'] = df['value'].astype(float)
        df = (df.merge(data_dictionary, on = ['project_id', 'field_name']))
        if len(df) > 0:
            df_list.append(df)

    # Uses Chauvenet's criterion to find outliers in each DataFrame
    outlier_list = []
    for df in df_list:
        # print(df)
        if outlier_method == 'Chauvanet':
            # display(df)
            outliers = find_outliers_chauvenet(df)
        elif outlier_method == 'Pierce':
            outliers = find_outliers_pierce(df)
        elif outlier_method == 'QQ':
            outliers = find_outliers_qq(df)
        else:
            outliers = find_outliers_chauvenet(df)
        # logging.info(f"Detected outlier using {outlier_method}: {outliers}")
        outlier_list.append(outliers)
    
    # Submits a data resolution workflow entry for each outlier
    with open('stored_data/drw_entries.csv', 'a', newline='') as file:
        for df in outlier_list:
            if df.empty:
                pass
            else:
                # needs both because database sometimes lowers case
                df = df[~df['comment'].isin(['Flagged Value', 'Flagged value'])]
                # df = df[df['_merge'] == 'left_only'].drop('_merge', axis=1)
                # display(df)
            for index, rows in df.iterrows():
                if production_mode:
                    logging.info(f"Detected outlier using {outlier_method}: {rows['project_id']}: {rows['event_id']}, {rows['record']} - {rows['field_name']} - {rows['value']} - {rows['instance']}")
                    data_workflow_submission(rows['project_id'], rows['event_id'], rows['record'], rows['form_name'], rows['field_name'], rows['value'], rows['instance'])
                file.write(f"{rows['project_id']},{rows['event_id']},{rows['record']},{rows['form_name']},{rows['field_name']},{rows['value']},{rows['instance']}\n")

    logging.info(f"Completed outlier detection and submission for project {project_id} and field {field_name}.")
    return None

def get_entry_of_missing(conn: mariadb.connections.Connection, project_id: int, event_id: int, hnrcid: int, form_name: str, field_name: str, value: str, repeat_instance: int) -> tuple[int,str,str]:
    """
    Retrieves the user_id and username of the data entrist by filtering on the hnrcid, event_id, field_name, and instance attributes.

    Args:
        conn (mariadb.connections.Connection): The active connection to the mariaDB server
        project_id (int): The project_id of the data entry
        event_id (int): The event_id of the data entry
        hnrcid (int): The hnrcid of the data entry
        form_name (str): The form_name of the data entry
        field_name (str): The field_name of the data entry
        value (str): The value of the data entry
        repeat_instance (int): The repeat_instance of the data entry

    Returns:
        tuple[int,str,str]: A tuple containing the user_id, username, and email of the data entry
    """
    # imported studies have multiple project_ids and therefore need to be joined before processing
    log_event_tables, data_tables = get_log_event_and_data_tables(conn, project_id)
    table_name = []
    for log_event_table in range(len(log_event_tables)):
        table_name.append(log_event_tables[log_event_table])
    table_name.append('redcap_user_information')
    for data_table in range(len(data_tables)):
        table_name.append(data_tables[data_table])
    col_names = get_colnames(conn, table_name)
    table_data = get_table_data(conn, col_names)

    unioned_log_table = pd.DataFrame(columns=col_names[table_name[0]])
    unioned_data_table = pd.DataFrame(columns=['project_id', 'event_id', 'pk', 'instance', 'field_name', 'value'])

    for log_event_table in range(len(log_event_tables)):
        # loads relevant log table and splits multi-entries into individual rows
        table = filter_log_event_table(table_data[log_event_tables[log_event_table]])
        unioned_log_table = unioned_log_table.append(table, ignore_index=True)
    
    for data_table in range(len(data_tables)):
        # loads relevant data table
        table = filter_data_table(table_data[data_tables[data_table]])
        unioned_data_table = unioned_data_table.append(table, ignore_index=True)
    
    # loads user info table and merges with log table to find user_id
    user_info = table_data['redcap_user_information'][['ui_id', 'username', 'user_email']]
    unioned_log_table = (unioned_log_table.merge(user_info, left_on = 'user', right_on = 'username')).drop(columns=['username'])

    data_dictionary = retrieve_data_dictionary()
    data_dictionary = data_dictionary[['project_id', 'field_name','form_name']]
    unioned_data_table = (unioned_data_table.merge(data_dictionary, on = ['project_id', 'field_name']))

    cols = ['project_id', 'event_id', 'pk', 'instance', 'field_name', 'value']
    
    unioned_super_table = unioned_data_table.merge(unioned_log_table, left_on=cols, right_on=cols)

    # display(unioned_super_table)

    # table with all of that patient's data entries for that project. requires a user to proceed. needs to be one entry. 
    # missing['event_id'] needs to be equal to event_id
    # missing['instance'] needs to be equal to repeat_instance if instance_value exists
    # missing['pk'] needs to be equal to hnrcid
    # if there are more than one user for that hnrcid for that event, make missing['user'] whoever has greater value_counts with that hnrcid
    # if the field_name exists for that event and pk, make missing['field_name'] the field name. 

    # print(f"{project_id} {event_id} {hnrcid} {field_name} {value} {repeat_instance}")

    missing = unioned_super_table.copy()
    if len(missing[(missing['form_name'] == form_name)]) > 0:
        missing = missing[(missing['form_name'] == form_name)]
        
    if len(missing[(missing['event_id'].astype(int) == int(event_id))]) > 0:
        missing = missing[(missing['event_id'].astype(int) == int(event_id))]

    if len(missing[(missing['pk'].astype(int) == int(hnrcid))]) > 0:
        missing = missing[(missing['pk'].astype(int) == int(hnrcid))]

    if len(missing[(missing['instance'].astype(int) == int(repeat_instance))]) > 0:
        missing = missing[(missing['instance'].astype(int) == int(repeat_instance))]

    # display(missing)

    if len(missing) == 0:
        missing = retrieve_default_reviewer(project_id, form_name).reset_index(drop=True)
        first_entry = missing.iloc[0]
        official_user_id = int(first_entry['ui_id'])
        official_username = str(first_entry['user'])
        official_email = str(first_entry['user_email'])
    else:
        missing = missing.reset_index(drop=True)
        first_entry = missing.iloc[0]

        official_user_id = int(first_entry['ui_id'])
        official_username = str(first_entry['user'])
        official_email = str(first_entry['user_email'])


    return official_user_id, official_username, official_email

def navigate_branching_logic(personalized_data_dic: pd.DataFrame, missing_check_dict: dict) -> pd.DataFrame:
    """
    This function navigates the branching logic of the personalized data dictionary to remove rows that do not meet the criteria of the branching logic.

    Steps:
    1. Iterate through each row in the personalized data dictionary.
        1a. Check if the branching logic is not null.
        1b. Iterate through the other rows in the personalized data dictionary to check if the branching logic is met.
        1c. Drop rows if the branching logic is confirmed to be not met.

    2. Iterate through each row in the personalized data dictionary.
        2a. Drop rows if field_name is not vital or misc HIDDEN logic criteria are met.
    
    3. Iterate through each row in the personalized data dictionary.
        3a. If a row is missing, check if the row references another field in the branching logic.
        3b. Drop the row if the referenced field is not present.


    Args:
        personalized_data_dic (pd.DataFrame): The data dictionary to navigate the branching logic of for that exact event/form
        missing_check_dict (dict): A dictionary containing the event_name, event_id, and form_name of the missing data entry

    Returns:
        pd.DataFrame: The updated personalized data dictionary after navigating the branching logic
    """
    event_name = missing_check_dict['event_name']
    event_id = missing_check_dict['event_id']
    form_name = missing_check_dict['form_name']


    for index, row in personalized_data_dic.iterrows():
        x = row['field_name']
        y = row['value']
        branching_logic = row['branching_logic']

        if pd.isna(branching_logic):
            continue
        remove_row = False

        # print(list(row))
        for _, other_row in personalized_data_dic.iterrows():
            other_x = other_row['field_name']
            other_y = other_row['value']
            try:
                other_y = float(other_y)
            except:
                continue
            if (f" AND " in branching_logic) or (f" and " in branching_logic):
                remove_row = True
                break
            if (f"[{other_x}]" in branching_logic and (np.isnan(float(other_y)))):
                remove_row = True
                break
            elif (f"[{other_x}] = " in branching_logic and f"[{other_x}] = {other_y}" not in branching_logic) or (f"[{other_x}] = " in branching_logic and f"[{other_x}] = '{other_y}'" not in branching_logic):
                remove_row = True
                break
            # uses regex to find the value of any digits following a comparison operator
            elif (f"[{other_x}]>" in branching_logic and len(re.findall(r"[>]=?\s*(-?\d+\.?\d*)", branching_logic)) > 0):
                value = int(re.findall(r"[>]=?\s*(-?\d+\.?\d*)", branching_logic)[0])
                if int(other_y) <= value:
                    remove_row = True
                    break
            elif (f"[{other_x}]<" in branching_logic and len(re.findall(r"[<]=?\s*(-?\d+\.?\d*)", branching_logic)) > 0):
                value = int(re.findall(r"[<]=?\s*(-?\d+\.?\d*)", branching_logic)[0])
                if int(other_y) >= value:
                    remove_row = True
                    break
            elif (f"[{other_x}] >" in branching_logic and len(re.findall(r"[>]=?\s*(-?\d+\.?\d*)", branching_logic)) > 0):
                value = int(re.findall(r"[>]=?\s*(-?\d+\.?\d*)", branching_logic)[0])
                if int(other_y) <= value:
                    remove_row = True
                    break
            elif (f"[{other_x}] <" in branching_logic and len(re.findall(r"[<]=?\s*(-?\d+\.?\d*)", branching_logic)) > 0):
                value = int(re.findall(r"[<]=?\s*(-?\d+\.?\d*)", branching_logic)[0])
                if int(other_y) >= value:
                    remove_row = True
                    break
            elif (f"[{other_x}] != " in branching_logic and f"[{other_x}] != {other_y}" in branching_logic) or (f"[{other_x}] != " in branching_logic and f"[{other_x}] != '{other_y}'" in branching_logic):
                remove_row = True
                break
            elif (f"[event-name] = '{event_name}'" in branching_logic) or (f"[event-number] = '{event_id}'" in branching_logic):
                continue
            elif (f"[event-name] = '" in branching_logic) and (f"{event_name}'" not in branching_logic):
                remove_row = True
                break
            elif (f"[event-name] != '{event_name}'" in branching_logic) or (f"[event-number] != '{event_id}'" in branching_logic):
                remove_row = True
                break
            elif (f"[event-name] != '" in branching_logic) and (f"{event_name}'" not in branching_logic):
                continue
            # elif (f"[event-number] = '" in branching_logic) and (f"{event_id}'" not in branching_logic):
            #     remove_row = True
            #     break
            # elif (f"[event-number] != '" in branching_logic) and (f"{event_id}'" not in branching_logic):
            #     continue
            elif (f"[event-number]'" in branching_logic):
                remove_row = True
                break
            elif (f"[{other_x}(" in branching_logic):
                remove_row = True
                break
            else:
                remove_row = False
        if remove_row:
            personalized_data_dic = personalized_data_dic[personalized_data_dic['field_name'] != x].reset_index(drop=True)
        
    for _, row in personalized_data_dic.iterrows():
        # or (f"other" in row['field_name'])
        if (row['field_name'] == f"{form_name}_complete") or (f"comment" in row['field_name']) or (f"note" in row['field_name']):
             personalized_data_dic =  personalized_data_dic[personalized_data_dic['field_name'] != row['field_name']]

        if (pd.notna(row['misc'])):
            misc_list = [f"@IF([event-name]='{event_name}', @HIDDEN, '')", f"@IF([{row['field_name']}]='', @HIDDEN, '')", f"', '', @HIDDEN)", f"@CALCTEXT", f"@CALCDATE",f"@READONLY"]
            for misc in misc_list:
                if misc in row['misc']:
                    personalized_data_dic = personalized_data_dic[personalized_data_dic['field_name'] != row['field_name']]
                    break
            if row['misc'] == '@HIDDEN':
                 personalized_data_dic =  personalized_data_dic[personalized_data_dic['field_name'] != row['field_name']]

            else:
                pass
    # print(personalized_data_dic)
    for _, row in personalized_data_dic.iterrows():
        if (row['missing'] == True):
            if (pd.notna(row['branching_logic'])):
                # searches for [] brackets in the branching logic to find potentially referenced fields
                field_references = re.findall(r"\[([^\]]+)\]", row['branching_logic'])

                for ref in field_references:
                    if ref not in personalized_data_dic['field_name'].values and ref != 'event-name':
                        personalized_data_dic = personalized_data_dic[personalized_data_dic['field_name'] != row['field_name']]
                        break
    personalized_data_dic = personalized_data_dic.reset_index(drop=True)

    return personalized_data_dic
def find_missing_data(merged_data_table: pd.DataFrame, data_dictionary: pd.DataFrame, missing_check_dict: dict) -> pd.DataFrame:
    """
    Finds missing data entries in a DataFrame using the data dictionary and the merged data table.

    Args:
        merged_data_table (pd.DataFrame): The DataFrame containing all the data for the relevant project
        data_dictionary (pd.DataFrame): The DataFrame containing the data dictionary for the relevant project
        missing_check_dict (dict): A dictionary containing the project_id, event_id, form_name, and event_name of the missing data entry
    
    Returns:
        pd.DataFrame: A DataFrame containing the missing data entries
    """
    # missing data entries are when there is no entry in the merged_data_table for a given field_name for a given record, 
    # but there is an entry in the same form_name and event_id for that record
    all_records_in_project = merged_data_table['record'].astype(int).unique()
    
    project_id = missing_check_dict['project_id']
    event_id = missing_check_dict['event_id']
    form_name = missing_check_dict['form_name']
    event_name = missing_check_dict['event_name']    
    
    filtered_data_dic = data_dictionary[
        (data_dictionary['project_id'] == project_id) &
        (data_dictionary['event_id'] == event_id) &
        (data_dictionary['form_name'] == form_name) & 
        (data_dictionary['element_type'] != 'calc')
    ]
    field_max = len(filtered_data_dic)
    
    max_instance = merged_data_table['instance'].astype(int).max()
    # print(max_instance)
    if np.isnan(max_instance):
        return pd.DataFrame()
    else:    
        merged_data_table = merged_data_table.astype({'project_id': 'int', 'event_id': 'int', 'record': 'int', 'instance': 'int', 'field_name': 'str', 'value': 'str'})
        merged_data_table = merged_data_table[['project_id', 'event_id', 'record', 'form_name', 'field_name', 'instance', 'value']]


        # create df with all possible data entries for each record in the form
        filtered_data_dic = filtered_data_dic.assign(record=[all_records_in_project] * len(filtered_data_dic))
        filtered_data_dic = filtered_data_dic.explode('record', ignore_index=True)
        filtered_data_dic = filtered_data_dic.loc[filtered_data_dic.index.repeat(max_instance)].reset_index(drop=True)
        filtered_data_dic['event_name'] = event_name
        filtered_data_dic['instance'] = list(range(1, max_instance + 1)) * (len(filtered_data_dic) // max_instance)

        # merge the filtered data dictionary with the data table to find missing data entries
        filtered_data_dic = filtered_data_dic.astype({'project_id': 'int', 'event_id': 'int', 'record': 'int', 'instance': 'int', 'form_name': 'str', 'field_name': 'str'})
        filtered_data_dic = filtered_data_dic.merge(merged_data_table, on=['project_id', 'event_id', 'record', 'form_name', 'field_name', 'instance'], how='left', indicator='indicate')
        filtered_data_dic['missing'] = (filtered_data_dic['indicate'] == 'left_only')

        # iterate through each group of data entries to find data entries that have missing fields but are not entirely missing
        grouped = filtered_data_dic.groupby(['project_id', 'event_id', 'record', 'form_name'])
        missing_data_entries = []
        for group_keys, group_df in grouped:
            project_id, event_id, record, form_name = group_keys
            sub_grouped = group_df.groupby(['project_id', 'event_id', 'record', 'form_name', 'instance'])
            
            # iterate through each instance of the form to find missing fields
            for instance_keys, instance_df in sub_grouped:
                _, _, _, _, instance = instance_keys

                missing_fields = instance_df[instance_df['missing']]['field_name'].to_list()
                present_fields = instance_df[instance_df['missing'] == False]['field_name'].to_list()

                if 0 < len(missing_fields) < field_max:
                    instance_df = navigate_branching_logic(instance_df, missing_check_dict)

                new_field_max = len(instance_df)
                missing_count = len(instance_df[instance_df['missing']])

                if missing_count not in {new_field_max, 0}:
                    missing_data_entries.append({
                        'project_id': project_id, 
                        'event_id': event_id, 
                        'record': record, 
                        'form_name': form_name, 
                        'field_name': f"{form_name}_complete",
                        'missing_fields': missing_fields,
                        'present_fields': present_fields,
                        'instance': instance
                    })
            
                if missing_count == new_field_max:
                    break

        missing_data = pd.DataFrame(missing_data_entries)
        # display(missing_data)


        return missing_data
def missing_data_submission(project_id: int, event_id: int, hnrcid: int, form_name: str, field_name: str, value: str, repeat_instance: int, missing_fields: list, ping: bool = True) -> None:
    """
    Submits a new data entry to the redcap_data_quality_status and redcap_data_quality_resolutions tables after checking for duplicates.

    Args:
        project_id (int): The project_id of the data entry
        event_id (int): The event_id of the data entry
        hnrcid (int): The hnrcid of the data entry
        form_name (str): The form_name of the data entry
        field_name (str): The field_name of the data entry
        value (str): The value of the data entry
        repeat_instance (int): The repeat_instance of the data entry
        missing_fields (list): A list of the missing fields in the data entry
        ping (bool, optional): A boolean indicating whether to send a message to the recipient (default is True)

    Returns:
        None
    """
    conn = connect_to_maria()


    official_user_id, username, email = get_entry_of_missing(conn, project_id, event_id, hnrcid, form_name, field_name, value, repeat_instance)
    log_msg = f'project_id {project_id}, hnrcid {hnrcid}, event_id {event_id}, repeat_instance {repeat_instance}, field_name {field_name}, value {value}, user {official_user_id}: {username} {email}. '

    dq_status = check_existing_drw_entry(project_id, event_id, hnrcid, field_name, official_user_id, repeat_instance)
    
    if (len(dq_status.index) == 0):
        try:
            create_data_res_workflow_entry(conn, project_id, event_id, hnrcid, field_name, value, repeat_instance, official_user_id, official_user_id, comment = f"Missing data", ping = ping)
            log_msg += "Created a Data Resolution Workflow entry. "
            if ping:
                log_msg += f"Sent ping to user {official_user_id}: {username}"
                # send_email("Missing data", [email])
            else:
                log_msg += f"Did not ping user {official_user_id}: {username}"
        except:
            log_msg += "Already exists as a Data Resolution Workflow entry. "
    else:
        log_msg += "Already exists as a Data Resolution Workflow entry. "
    
    logging.info(log_msg)
    
    conn.commit()       # commit changes to the database so they can be officially submitted once the process is over
    conn.close()        # connection MUST be closed at end of process so it is not infinitely hanging

    return None

def submit_stored_drw_entries() -> None:
    """
    Retrieves csv file with stored DRW entries and submits any entries that do not exist in the DRW to REDCap

    Returns:
        None
    """
    drw_table = get_drw_table()
    potential_submissions = pd.read_csv('stored_data/drw_entries.csv')
    potential_submissions = potential_submissions.drop_duplicates()
    potential_submissions = potential_submissions.merge(drw_table, on=['project_id', 'event_id', 'record', 'field_name', 'instance'], how='left', indicator=True)
    potential_submissions = potential_submissions[potential_submissions['_merge'] == 'left_only']
    
    logging.info(f"{len(potential_submissions)} entries to submit...")
    counter = 0
    for index, row in potential_submissions.iterrows():
        if row['value'] == f"'Missing'":
            missing_data_submission(row['project_id'], row['event_id'], row['record'], row['form_name'], row['field_name'], row['value'], row['instance'], row['form_name'])
        else:
            data_workflow_submission(row['project_id'], row['event_id'], row['record'], row['form_name'], row['field_name'], row['value'], row['instance'], row['form_name'])
        # counter += 1
        # if counter % 10 == 0:
        #     time.sleep(3)
    pd.DataFrame(columns=['project_id', 'event_id', 'record', 'form_name', 'field_name', 'value', 'instance']).to_csv('stored_data/drw_entries.csv', index=False)
    return None

def operate_missing_qc(merged_data_table: pd.DataFrame, data_entry_table: pd.DataFrame, production_mode: bool = False) -> None: 
    """

    Args:
        merged_data_table (pd.DataFrame): The merged data table containing all data entries for a given project
        data_entry_table (pd.DataFrame): The data entry table containing the inputted data 
        production_mode (bool, optional): A boolean indicating whether to run the function in production mode (default is False)
    
    Returns:
        None
    """
    data_dictionary = retrieve_data_dictionary()
    data_dictionary = data_dictionary[['project_id', 'field_name','form_name', 'field_order', 'element_type', 'element_validation_type', 'branching_logic', 'misc']]
    data_dictionary = data_dictionary.sort_values(by=['project_id', 'form_name', 'field_order'], ignore_index=True)
    
    drw_table = get_drw_table()
    event_arms_table = get_arm_data()
    event_arms_table = event_arms_table[['project_id', 'event_id', 'event_name', 'form_name', 'custom_repeat_form_label']]
    data_dictionary = (data_dictionary.merge(event_arms_table, on = ['project_id', 'form_name']))

    data_dictionary = check_for_confirmed_correct_fields(data_dictionary)

    data_entry_table = (data_entry_table.merge(data_dictionary, on = ['project_id',  'event_id', 'field_name']))
    data_entry_table['instance'] = data_entry_table['instance'].fillna(1).astype(int)

    missing_check_dict = {'project_id': None, 'event_id': None, 'form_name': None, 'event_name': None}

    missing_check_dict['project_id'] = int(data_entry_table['project_id'].unique()[0])
    missing_check_dict['event_id'] = int(data_entry_table['event_id'].unique()[0])
    missing_check_dict['form_name'] = data_entry_table['form_name'].unique()[0]
    missing_check_dict['event_name'] = data_entry_table['event_name'].unique()[0]

    # only keep fields that are in the merged_data_table (only fields that are filled out at least once are considered)
    dd_mask = data_dictionary[['project_id', 'event_id', 'field_name']].isin(merged_data_table[['project_id', 'event_id', 'field_name']].to_dict(orient='list')).all(axis=1)
    data_dictionary = data_dictionary[dd_mask]

    merged_data_table = merged_data_table[merged_data_table['project_id'] == missing_check_dict['project_id']]
    merged_data_table = merged_data_table[merged_data_table['event_id'].astype(int) == missing_check_dict['event_id']]
    merged_data_table = (merged_data_table.merge(data_dictionary, on = ['project_id', 'event_id',  'field_name']))
    merged_data_table['instance'] = merged_data_table['instance'].fillna(1).astype(int)

    merged_data_table = merged_data_table[merged_data_table['form_name'] == missing_check_dict['form_name']]

    # logging.info(f"Checking for missing data in project {missing_check_dict['project_id']} for {missing_check_dict['form_name']} form and event {missing_check_dict['event_id']} {missing_check_dict['event_name']}")
    # display(merged_data_table)

    missing_data = find_missing_data(merged_data_table, data_dictionary, missing_check_dict)

    if missing_data.empty:
        pass
    else:
        missing_data = missing_data.reset_index(drop=True)
        missing_data = missing_data.explode('missing_fields').reset_index(drop=True)
        # only keep one entry per project id, record, field_name, event_id, form_name, and instance
        missing_data = missing_data.drop_duplicates(subset = ['project_id', 'record', 'event_id', 'missing_fields', 'form_name', 'instance'])
        # merge with drw table and only keep entries that do not have a drw entry
        missing_data = missing_data.merge(drw_table, left_on = ['project_id', 'record', 'event_id', 'missing_fields', 'instance'], right_on = ['project_id', 'record', 'event_id', 'field_name', 'instance'], how='left', indicator=True)
        missing_data = missing_data[missing_data['_merge'] == 'left_only'].drop('_merge', axis=1)
        # display(missing_data)
    
    with open('stored_data/drw_entries.csv', 'a', newline='') as file:
        for _, row in missing_data.iterrows():
            if production_mode:
                logging.info(f"Detected missing data in proj {row['project_id']}: event {row['event_id']}, hnrcid {row['record']}, instance {row['instance']} - missing {row['missing_fields']}")
                missing_data_submission(row['project_id'], row['event_id'], row['record'], row['form_name'], row['missing_fields'], 'Missing', row['instance'], row['missing_fields'], ping = True)
            file.write(f"{row['project_id']},{row['event_id']},{row['record']},{row['form_name']},{row['missing_fields']},'Missing',{row['instance']}\n")

    logging.info(f"Completed missing data detection and submission for form {missing_check_dict['form_name']} in project {missing_check_dict['project_id']} and event {missing_check_dict['event_id']}.")
    return None

def operate_quality_control_individual(data_entry: dict, outlier_method: str = 'Chauvanet', outlier_qc: bool = True, missing_qc: bool = True, routine: bool = False, production_mode: bool = False) -> None:
    """
    Operates the quality control process on a data entry.

    Args:
        data_entry (dict): The data entry to operate the quality control process on
        outlier_method (str, optional): The method to use for outlier detection (default is 'Chauvanet')
        outlier_qc (bool, optional): A boolean indicating whether to perform outlier quality control (default is True)
        missing_qc (bool, optional): A boolean indicating whether to perform missing data quality control (default is True)
        routine (bool, optional): A boolean indicating whether to perform the quality control routine (default is False)
        production_mode (bool, optional): A boolean indicating whether to run the process in production mode (default is False)
    
    Returns:
        None
    """
    proj_id = data_entry['project_id']
    data_entry_table = pd.json_normalize(data_entry)
    if not routine:
        data_entry_table = filter_log_event_table(data_entry_table)
    
    if data_entry_table.empty:
        logging.info(f"No data entries found with proj_id {proj_id}.")
        return None

    data_dictionary = retrieve_data_dictionary()
    # check data_dictionary to see if data_entry_table, event_id, and field_name are in the data dictionary
    data_dictionary = data_dictionary[['project_id', 'field_name']]
    data_dictionary = data_dictionary[data_dictionary['project_id'] == proj_id]
    data_entry_table = (data_entry_table.merge(data_dictionary, on = ['project_id', 'field_name']))


    log_table_names, data_table_names = get_log_event_and_data_tables(proj_id)
    data_tables = retrieve_database_table(data_table_names)

    completed_users = retrieve_completed_users()
    completed_user_list = completed_users[completed_users['project_id'] == proj_id]['record'].to_list()

    # Creates joined table of all redcap_data tables, and filters to only include data from the associated projects
    merged_data_table = pd.concat(data_tables.values())
    merged_data_table = merged_data_table[merged_data_table['project_id'].isin([proj_id])]
    merged_data_table = merged_data_table[~merged_data_table['record'].isin(completed_user_list)]
    

    if missing_qc:
        operate_missing_qc(merged_data_table, data_entry_table, production_mode)
    if outlier_qc:
        # print(data_entry_table)
        operate_outlier_qc(merged_data_table, data_entry_table, outlier_method, production_mode)


    return None

def operate_quality_control_routine(data_entry: dict, merged_data_table: pd.DataFrame, outlier_method: str = 'Chauvanet', outlier_qc: bool = True, missing_qc: bool = True, routine: bool = False, production_mode: bool = False) -> None:
    """
    Operates the quality control process on a data entry.

    Args:
        data_entry (dict): The data entry to operate the quality control process on
        merged_data_table (pd.DataFrame): The merged data table containing all data entries for a given project
        outlier_method (str, optional): The method to use for outlier detection (default is 'Chauvanet')
        outlier_qc (bool, optional): A boolean indicating whether to perform outlier quality control (default is True)
        missing_qc (bool, optional): A boolean indicating whether to perform missing data quality control (default is True)
        routine (bool, optional): A boolean indicating whether to perform the quality control routine (default is False)
        production_mode (bool, optional): A boolean indicating whether to run the process in production mode (default is False)

    Returns:
        None
    """
    proj_id = data_entry['project_id']
    data_entry_table = pd.json_normalize(data_entry)
    if not routine:
        data_entry_table = filter_log_event_table(data_entry_table)
    
    if data_entry_table.empty:
        logging.info(f"No data entries found with proj_id {proj_id}.")
        return None

    data_dictionary = retrieve_data_dictionary()
    # check data_dictionary to see if data_entry_table, event_id, and field_name are in the data dictionary
    data_dictionary = data_dictionary[['project_id', 'field_name']]
    data_dictionary = data_dictionary[data_dictionary['project_id'] == proj_id]
    data_entry_table = (data_entry_table.merge(data_dictionary, on = ['project_id', 'field_name']))


    completed_users = retrieve_completed_users()
    completed_user_list = completed_users[completed_users['project_id'] == proj_id]['record'].to_list()

    # Creates joined table of all redcap_data tables, and filters to only include data from the associated projects
    
    merged_data_table = merged_data_table[merged_data_table['project_id'].isin([proj_id])]
    merged_data_table = merged_data_table[~merged_data_table['record'].isin(completed_user_list)]
    

    if missing_qc:
        operate_missing_qc(merged_data_table, data_entry_table, production_mode)
    if outlier_qc:
        # print(data_entry_table)
        operate_outlier_qc(merged_data_table, data_entry_table, outlier_method, production_mode)


    return None

def find_empty_forms(data_dictionary: pd.DataFrame, project_form_event_combos: pd.DataFrame, pid_list: list) -> list:
    """
    Finds all empty forms in a given project.

    one df (project_form_event_combos) has all the possible field_name and event_id combos. 
    The other (unioned_data_table) has all the pk, field_name and event_id combos that have been used. 
    If a pk has a field_name and event_id combo that is not in the used df, then it is missing.
    
    Args:
        data_dictionary (pd.DataFrame): The data dictionary to use for the process
        project_form_event_combos (pd.DataFrame): The project form event combos that need to be checked
        pid_list (list): The list of project ids
    
    Returns:
        list: A list of dataframes containing the missing forms separated by project id
    """    
    missing_forms_list = []

    completed_users = retrieve_completed_users()
    drw_table = get_drw_table()

    for project_id in pid_list:  
        
        unioned_data_table = retrieve_all_data(pid_list)
        unioned_data_table = unioned_data_table[unioned_data_table['project_id'] == project_id]
        # display(unioned_data_table)        
        unioned_data_table = (unioned_data_table.merge(data_dictionary, on = ['project_id', 'event_id', 'field_name']))
        unioned_data_table = unioned_data_table[['pk', 'project_id', 'event_id', 'form_name', 'field_name', 'field_order']].drop_duplicates()
        unioned_data_table = unioned_data_table[(unioned_data_table['field_name'].str.contains('_complete', case=False, na=False))]
        unioned_data_table = unioned_data_table.drop(columns=['form_name']).reset_index(drop=True)
        unioned_data_table = unioned_data_table.sort_values(by=['pk', 'event_id', 'field_order', 'field_name']).reset_index(drop=True)

        for index, row in unioned_data_table.iterrows():
            if (project_id, row['pk']) in completed_users:
                unioned_data_table.drop(index, inplace=True)



        temp_project_form_event_combos = project_form_event_combos[project_form_event_combos['project_id'] == project_id]
        
        pk_list = unioned_data_table['pk'].unique().tolist()
        temp_project_form_event_combos['pk'] = np.nan
        temp_project_form_event_combos = temp_project_form_event_combos.assign(pk=[pk_list] * len(temp_project_form_event_combos))
        temp_project_form_event_combos = temp_project_form_event_combos.explode('pk').reset_index(drop=True)
        

        # join so all possible combinations are present, then filter out the ones that are actually present in the data
        temp_missing_forms = (temp_project_form_event_combos.merge(unioned_data_table, on=['project_id', 'event_id', 'field_name', 'pk'], how='left', indicator=True))
        temp_missing_forms['missing_form'] = (temp_missing_forms['_merge'] == 'left_only')
        temp_missing_forms = temp_missing_forms[['pk', 'project_id', 'event_id', 'form_name', 'field_name', 'missing_form']].reset_index(drop=True)

        # marks forms where the pk does not have matches at all for the event
        temp_missing_forms = temp_missing_forms.merge(unioned_data_table, left_on=['pk', 'project_id', 'event_id'], right_on=['pk', 'project_id', 'event_id'], how='left', indicator=True)
        temp_missing_forms['pk_missing_event'] = (temp_missing_forms['_merge'] == 'left_only')
        temp_missing_forms = temp_missing_forms[['pk', 'project_id', 'event_id', 'form_name', 'field_name_x', 'missing_form', 'pk_missing_event']].drop_duplicates().reset_index(drop=True)

        # marks forms that exist in the drw table
        temp_missing_forms = temp_missing_forms.merge(drw_table, left_on=['pk', 'project_id', 'event_id', 'field_name_x'], right_on=['record', 'project_id', 'event_id', 'field_name'], how='left', indicator=True)
        temp_missing_forms['drw_exists'] = (temp_missing_forms['_merge'] == 'both')
        temp_missing_forms = temp_missing_forms[['pk', 'project_id', 'event_id', 'form_name', 'field_name_x', 'missing_form', 'pk_missing_event', 'drw_exists']].reset_index(drop=True)

        missing_forms_list.append(temp_missing_forms)
    
    return missing_forms_list

def filter_missing_forms(pid_list: list, ping: bool = True, production_mode: bool = False) -> None:
    """
    Filters out missing forms from the data dictionary and sends a message to the user to fill out the missing forms.
    
    Args:
        pid_list (list): A list of project_ids to filter missing forms for
        ping (bool, optional): A boolean indicating whether to send a message to the recipient (default is True)
        production_mode (bool, optional): A boolean indicating whether to run the function in production mode (default is False)
    
    Returns:
        None
    """
    logging.info("Filtering missing forms")
    outlier_file_name = 'stored_data/last_checked_outlier.log'
    missing_file_name = 'stored_data/last_checked_missing.log'
    run_empty_forms = False

    with open(outlier_file_name, 'r') as f1, open(missing_file_name, 'r') as f2:
        last_checked_outlier = f1.read()
        last_checked_missing = f2.read()

        if (last_checked_outlier == 'Finished') and (last_checked_missing == 'Finished'):
            run_empty_forms = True


    if run_empty_forms:

        data_dictionary = retrieve_data_dictionary()
        data_dictionary = data_dictionary[['project_id', 'field_name','form_name', 'field_order', 'element_type', 'element_validation_type', 'branching_logic', 'misc']]

        project_table = retrieve_project_data()
        project_table = project_table[['project_id', 'investigators']]

        event_arms_table = get_arm_data()
        event_arms_table = event_arms_table[['project_id', 'event_id', 'event_name', 'form_name', 'custom_repeat_form_label']]
        data_dictionary = (data_dictionary.merge(event_arms_table, on = ['project_id', 'form_name']))
        data_dictionary = (data_dictionary.merge(project_table, on = ['project_id']))

        data_dictionary = check_for_confirmed_correct_fields(data_dictionary)

        # data_dictionary = data_dictionary[data_dictionary['investigators'] == 'auto']
        data_dictionary = data_dictionary.sort_values(by=['project_id', 'field_order', 'event_id', 'form_name'], ignore_index=True)

        # uses _complete field name for each form_name and event_id combo
        project_form_event_combos = data_dictionary[['project_id', 'event_id', 'form_name', 'field_name']].drop_duplicates()
        project_form_event_combos = project_form_event_combos[project_form_event_combos['field_name'] == (project_form_event_combos['form_name'].astype(str) + '_complete')]
   

        missing_forms_list = find_empty_forms(data_dictionary, project_form_event_combos, pid_list)

        # if the event has entries, any empty forms are considered missing, except forms that have not been filled out yet by anyone
        # if someone has not filled out any form in that event, then it is not considered missing
        for i, missing_forms_project in enumerate(missing_forms_list):
            filled_event_forms = set(missing_forms_project[missing_forms_project['missing_form'] == False][['event_id', 'form_name']].drop_duplicates().itertuples(index=False, name=None))
            
            with open('stored_data/drw_entries.csv', 'a', newline='') as file:
                for index, row in missing_forms_project.iterrows():
                    if (((row['event_id'], row['form_name']) in filled_event_forms) and (row['missing_form'] == True) and (row['pk_missing_event'] == False) and (row['drw_exists'] == False)):
                        instance = 1
                        if production_mode:
                            missing_data_submission(row['project_id'], row['event_id'], row['pk'], row['form_name'], row['field_name_x'], 'Missing', instance, missing_fields=[row['form_name']], ping=ping)
                        file.write(f"{row['project_id']},{row['event_id']},{row['pk']},{row['form_name']},{row['field_name_x']},'Missing',{instance}\n")

    return None

def check_for_all_outliers(pid_list: list, outlier_method = 'Chauvanet', alert_threshold: int = 100, ping: bool = True, production_mode: bool = False) -> None:
    """
    Checks for all missing data entries in the data dictionary and sends an email if the number of entries exceeds the alert threshold.

    Args:
        pid_list (list): A list of project_ids to check for missing data entries
        outlier_method (str, optional): The method to use for outlier detection (default is 'Chauvanet')
        alert_threshold (int, optional): The threshold for the number of missing data entries to send an alert (default is 100)
        ping (bool, optional): A boolean indicating whether to send a message to the recipient (default is True)
        production_mode (bool, optional): A boolean indicating whether to run the function in production mode (default is False)

    Returns:
        None
    """

    data_dictionary = retrieve_data_dictionary()
    data_dictionary = data_dictionary[['project_id', 'field_name','form_name', 'field_order', 'element_type', 'element_validation_type', 'branching_logic', 'misc']]

    project_table = retrieve_project_data()
    project_table = project_table[['project_id', 'investigators']]

    event_arms_table = get_arm_data()
    event_arms_table = event_arms_table[['project_id', 'event_id', 'event_name', 'form_name', 'custom_repeat_form_label']]
    data_dictionary = (data_dictionary.merge(event_arms_table, on = ['project_id', 'form_name']))
    data_dictionary = (data_dictionary.merge(project_table, on = ['project_id']))
    data_dictionary = data_dictionary[data_dictionary['project_id'].isin(pid_list)]

    data_dictionary = check_for_confirmed_correct_fields(data_dictionary)
    data_dictionary = data_dictionary.sort_values(by=['project_id', 'event_id', 'form_name'], ignore_index=True) 

    data_dictionary = data_dictionary[(data_dictionary['element_validation_type'] == 'int') | (data_dictionary['element_validation_type'] == 'float')]
    project_field_combos = data_dictionary[['project_id', 'field_name']].drop_duplicates().reset_index(drop=True)

    data_table_names = []
    for pid in pid_list:
        log_table_name, data_table_name = get_log_event_and_data_tables(pid)
        for data_table in data_table_name:
            data_table_names.append(data_table)
    
    data_tables = retrieve_database_table(data_table_names)
    merged_data_table = pd.concat(data_tables.values())

    redcap_data = {
        'log_event_id': None,
        'project_id': None,
        'ts': None,
        'user': None,
        'ip': None,
        'page': None,
        'event': None,
        'object_type': None,
        'sql_log': None,
        'pk': None,
        'event_id': None,
        'data_values': None,
        'description': None,
        'legacy': None,
        'change_reason': None
        }
        
    status_id_count = get_current_drw_count()
    alert_sent = False

    # reverse order so that the most recent projects are checked first
    # project_field_combos = project_field_combos[::-1].reset_index(drop=True)

    outlier_file_name = 'stored_data/last_checked_outlier.log'
    missing_file_name = 'stored_data/last_checked_missing.log'
    run_outlier = False

    with open(outlier_file_name, 'r') as f1, open(missing_file_name, 'r') as f2:
        last_checked_outlier = f1.read()
        last_checked_missing = f2.read()

        if (last_checked_missing == 'Finished'):
            run_outlier = True

    if run_outlier:
        # remove fields that have already been checked this cycle
        try:
            if last_checked_outlier != 'Finished':
                last_checked_field = last_checked_outlier.split(' ')
                last_proj_id = int(last_checked_field[0])
                last_field_name = last_checked_field[1]
                last_index = project_field_combos[
                    (project_field_combos['project_id'] == last_proj_id) &
                    (project_field_combos['field_name'] == last_field_name)].index[0]
            
            project_field_combos = project_field_combos.iloc[last_index:]
        except:
            pass


        for _, row in project_field_combos.iterrows():
            redcap_data['project_id'] = row['project_id']
            redcap_data['field_name'] = row['field_name']

            operate_quality_control_routine(redcap_data, merged_data_table, outlier_method, outlier_qc = True, missing_qc = False, routine=True, production_mode=production_mode)

            set_last_checked(outlier_file_name, f"{row['project_id']} {row['field_name']}")

            status_id_count_now = get_current_drw_count()
            if (((status_id_count_now - status_id_count) > alert_threshold) and (not alert_sent)):
                send_error_email(message=f"Alarming number of DRW entries ({status_id_count_now - status_id_count}) have been created recently. Please check the DRW table.")
                alert_sent = True

        set_last_checked(outlier_file_name, f"Finished")
    logging.info("All outlier data entries have been checked.")
    return None
    
def check_for_all_missing(pid_list: list, alert_threshold: int = 100, ping: bool = True, production_mode: bool = False) -> None:
    """
    Checks for all missing data entries in the data dictionary and sends an email if the number of entries exceeds the alert threshold.

    Args:
        pid_list (list): A list of project_ids to check for missing data entries
        alert_threshold (int, optional): The threshold for the number of missing data entries to send an alert (default is 100)
        ping (bool, optional): A boolean indicating whether to send a message to the recipient (default is True)
        production_mode (bool, optional): A boolean indicating whether to run the function in production mode (default is False)

    Returns:
        None
    """
    data_dictionary = retrieve_data_dictionary()
    data_dictionary = data_dictionary[['project_id', 'field_name','form_name', 'field_order', 'element_type', 'element_validation_type', 'branching_logic', 'misc']]

    project_table = retrieve_project_data()
    project_table = project_table[['project_id', 'investigators']]

    event_arms_table = get_arm_data()
    event_arms_table = event_arms_table[['project_id', 'event_id', 'event_name', 'form_name', 'custom_repeat_form_label']]
    data_dictionary = (data_dictionary.merge(event_arms_table, on = ['project_id', 'form_name']))
    data_dictionary = (data_dictionary.merge(project_table, on = ['project_id']))
    data_dictionary = data_dictionary[data_dictionary['project_id'].isin(pid_list)]

    data_dictionary = check_for_confirmed_correct_fields(data_dictionary)
    data_dictionary = data_dictionary.sort_values(by=['project_id', 'event_id', 'form_name'], ignore_index=True) 
    project_form_event_combos = data_dictionary[['project_id', 'event_id', 'form_name', 'field_name']].drop_duplicates()

    # uses _complete field name for each form_name and event_id combo
    project_form_event_combos = project_form_event_combos[(project_form_event_combos['field_name'].str.contains('_complete', case=False, na=False))]
    project_form_event_combos = project_form_event_combos.drop(columns=['form_name'])

    data_table_names = []
    for pid in pid_list:
        log_table_name, data_table_name = get_log_event_and_data_tables(pid)
        for data_table in data_table_name:
            data_table_names.append(data_table)
    
    data_tables = retrieve_database_table(data_table_names)
    merged_data_table = pd.concat(data_tables.values())

    redcap_data = {
        'log_event_id': None,
        'project_id': None,
        'ts': None,
        'user': None,
        'ip': None,
        'page': None,
        'event': None,
        'object_type': None,
        'sql_log': None,
        'pk': None,
        'event_id': None,
        'data_values': None,
        'description': None,
        'legacy': None,
        'change_reason': None
        }
    
    
    status_id_count = get_current_drw_count()
    alert_sent = False

    # reverse order so that the most recent projects are checked first
    project_form_event_combos = project_form_event_combos[::-1].reset_index(drop=True)
    file_name = 'stored_data/last_checked_missing.log'

    with open(file_name, 'r') as f:
        last_checked_form = f.read()


    # remove forms that have already been checked this cycle
    try:
        if last_checked_form != 'Finished':
            last_checked_form = last_checked_form.split(' ')
            last_proj_id = int(last_checked_form[0])
            last_event_id = int(last_checked_form[1])
            last_field_name = last_checked_form[2]
            last_index = project_form_event_combos[
                (project_form_event_combos['project_id'] == last_proj_id) &
                (project_form_event_combos['event_id'] == last_event_id) &
                (project_form_event_combos['field_name'] == last_field_name)].index[0]
            
            project_form_event_combos = project_form_event_combos.iloc[last_index:]
    except:
        pass

    for _, row in project_form_event_combos.iterrows():
        redcap_data['project_id'] = row['project_id']
        redcap_data['event_id'] = row['event_id']
        redcap_data['field_name'] = row['field_name']
        redcap_data['instance'] = 1
        operate_quality_control_routine(redcap_data, merged_data_table, outlier_method = '', outlier_qc = False, missing_qc = True, routine=True, production_mode=production_mode)

        set_last_checked(file_name, f"{row['project_id']} {row['event_id']} {row['field_name']}")

        status_id_count_now = get_current_drw_count()
        if (((status_id_count_now - status_id_count) > alert_threshold) and (not alert_sent)):
            send_error_email(message=f"Alarming number of DRW entries ({status_id_count_now - status_id_count}) have been created recently. Please check the DRW table.")
            alert_sent = True

    set_last_checked(file_name, f"Finished")
    logging.info("All missing data entries have been checked.")
    return None
    
def check_for_all_outlier_and_missing(pid_list: list, outlier_method: str = 'Chauvanet', alert_threshold: int = 100, ping: bool = True, production_mode: bool = False) -> None:
    """
    Checks for all missing data entries and outlier data in the data dictionary and sends an email if the number of entries exceeds the alert threshold.

    Args:
        pid_list (list): A list of project_ids to check for missing data entries
        outlier_method (str, optional): The method to use for outlier detection (default is 'Chauvanet')
        alert_threshold (int, optional): The threshold for the number of missing data entries to send an alert (default is 100)
        ping (bool, optional): A boolean indicating whether to send a message to the recipient (default is True)
        production_mode (bool, optional): A boolean indicating whether to run the function in production mode (default is False)

    Returns:
        None
    """
    refresh_all_stored_data()
    if production_mode:
        resolve_open_queries(pid_list)
    check_drw_enabled(pid_list)
    filter_missing_forms(pid_list, ping, production_mode)
    check_for_all_outliers(pid_list, outlier_method, alert_threshold, ping, production_mode)
    check_for_all_missing(pid_list, alert_threshold, ping, production_mode)
    return None

def test():
    # pid_list = [25,19]
    # pid_list = [129, 146, 151]
    # check_for_all_outlier_and_missing(pid_list)
    # check_for_all_missing(pid_list)
    
    # # redcap_data = {'log_event_id': 1530, 'project_id': 25, 'ts': 20241209182024, 'user': 'dgandh03', 'ip': '192.168.9.56', 'page': 'DataEntry/index.php', 'event': 'UPDATE', 'object_type': 'redcap_data', 'sql_log': "UPDATE redcap_data4 SET value = '29' WHERE project_id = 25 AND record = '42964' AND event_id = 414 AND field_name = 'v_pulse' AND instance is NULL;\nDELETE FROM redcap_data4 WHERE project_id = 25 AND record = '42964' AND event_id = 414 AND field_name = 'v_resp' AND instance is NULL;\nDELETE FROM redcap_data4 WHERE project_id = 25 AND record = '42964' AND event_id = 414 AND field_name = 'v_bp_sys' AND instance is NULL", 'pk': '42964', 'event_id': 414, 'data_values': "v_pulse = '29',\nv_resp = '',\nv_bp_sys = ''", 'description': 'Update record', 'legacy': 0, 'change_reason': None}
    # # operate_quality_control(redcap_data)
    # submit_stored_drw_entries()

    # pid_list = [25,19]
    pid_list = [129, 146, 151]
    production_mode = False
    check_last_run()
    if production_mode:
            send_periodic_email()
    with open('stored_data/last_routine.log', 'w') as file:
        file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    check_for_all_outlier_and_missing(pid_list, production_mode = production_mode, ping = False)
    # check_for_all_outliers(pid_list, production_mode = production_mode, ping = False)

    # submit_stored_drw_entries()
    return None

# test()


