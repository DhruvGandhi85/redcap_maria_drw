# C:/ProgramData/Anaconda3/python.exe -m pip list --format=freeze > stored_data/requirements.txt
# C:/ProgramData/Anaconda3/python.exe -m pip install -r stored_data/requirements.txt

from redcom_API import *
import flask
import waitress
import threading

app = flask.Flask(__name__)

# _____________________________________________
# MAKE CHANGES HERE
outlier_method = 'Chauvanet'     # 'Chauvanet', 'QQ', 'Pierce'
# pid_list = [25, 19]
pid_list = [146, 129, 151]      # list of project ids
alert_threshold = 100           # number of drw entries in an interval 
ping = False                    # send redcap messenger ping
production_mode = False         # True to submit data to redcap server
routine_hours = 9               # Sends an email if the last routine was more than this many hours ago
# _____________________________________________

ipfile = 'stored_data/ip_list.txt'
logdir = fr"C:\\inetpub\\flaskApp\\output_logs\\{datetime.datetime.now().strftime('%Y-%m')}"
logfile = fr"{logdir}\\redcom_log_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
if not os.path.exists(logdir):
    os.makedirs(logdir)

with open(ipfile, 'r') as file:
    ip_list = file.read().splitlines()

def common_troubleshooting():
    """
    Returns common troubleshooting fixes.
    """
    return_links = f'<h3>Common Troubleshooting</h3>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu/flaskApp/update-triggers/">Update Triggers</a> <br>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu/flaskApp/update-data-dic/">Update Data Dictionary</a> <br>'
    return return_links

def logfile_tail():
    """
    Returns the last 10 lines of the log file.
    """
    log_tail = read_log_file(logfile)
    return (
        f"<h3>Recent Log Entries</h3>"
        f"<pre style='word-wrap: break-word; white-space: pre-wrap;'>{log_tail}</pre>" )

def routing_links():
    """
    Returns the webpage routes.
    """
    return_links = f'<h3>Pages</h3>'
    return_links += f'<a href="https://rctest.hnrc.tufts.edu">https://rctest.hnrc.tufts.edu</a> <br>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu">https://redcom.hnrc.tufts.edu</a> <br>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu/flaskApp/">https://redcom.hnrc.tufts.edu/flaskApp/</a> <br>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu/flaskApp/update-triggers/">https://redcom.hnrc.tufts.edu/flaskApp/update-triggers/</a> <br>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu/flaskApp/update-data-dic/">https://redcom.hnrc.tufts.edu/flaskApp/update-data-dic/</a> <br>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu/flaskApp/outliers-and-missing-routine/">https://redcom.hnrc.tufts.edu/flaskApp/outliers-and-missing-routine/</a> <br>'
    return_links += f'<a href="https://redcom.hnrc.tufts.edu/flaskApp/receive-from-maria/">https://redcom.hnrc.tufts.edu/flaskApp/receive-from-maria/</a> <br>'
    return return_links

def default_page():
    """
    Returns the default webpage structure with routing, troubleshooting, and log file.
    """
    return f'<h1>Redcom Flask App</h1>' + routing_links() + common_troubleshooting() + logfile_tail()

@app.route('/')
@app.route('/flaskApp/')
def home():
    """
    Routed from / and /flaskApp/.
    Returns the default webpage. 
    """
    return default_page()

@app.route('/flaskApp/update-triggers/', methods=['GET', 'POST'])
def update_triggers():
    """
    Routed from /flaskApp/update-triggers/ and when triggered by POST request from MariaDB.
    POST request is triggered when projects table is updated.

    Refreshes all stored data and triggers for all projects.
    """
    thread_trig = threading.Thread(target=refresh_background_trigger)
    thread_trig.start()
    thread_store = threading.Thread(target=refresh_all_stored_data)
    thread_store.start()
    return 'Processing triggers in the background \n' + default_page()

@app.route('/flaskApp/update-data-dic/', methods=['GET', 'POST'])
def update_data_dic_triggers():
    """
    Routed from /flaskApp/update-data-dic/ and when triggered by POST request from MariaDB.
    POST request is triggered when metadata table is updated.

    Refreshes stored data dictionary.
    """
    # when the metadata (data dictionary) table is updated. 
    thread_dd = threading.Thread(target=store_data_dictionary)
    thread_dd.start()
    return 'Processing data dictionary in the background \n' + default_page()

@app.route('/flaskApp/outliers-and-missing-routine/', methods=['POST'])
def outlier_and_missing_routine():
    """
    Runs when triggered by POST request from MariaDB.
    Checks for outliers and missing data in all projects.
    Sends email if the last run was more than routine_hours ago.
    Sends email blast for drw entries that are more than 24 hours old.
    """
    check_last_run(hours=routine_hours)
    if production_mode:
        send_periodic_email()
    with open('stored_data/last_routine.log', 'w') as file:
        file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    thread_check = threading.Thread(target=check_for_all_outlier_and_missing, kwargs={'pid_list': pid_list, 
                                                                                      'outlier_method': outlier_method, 
                                                                                      'alert_threshold': alert_threshold, 
                                                                                      'ping': ping, 
                                                                                      'production_mode': production_mode})
    thread_check.start()
    return 'Checking for outliers and missing in the background \n'

@app.route('/flaskApp/receive-from-maria/', methods=['POST'])
def receive_from_maria():
    """
    Runs when triggered by POST request from MariaDB. 
    Receives data from MariaDB and runs quality control if IP is authorized.

    Inputs data from redcap_log_event table
    """
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
    
    # use this with official redcap API data entry trigger 
    # redcap_data = {"project_id": None, "username": None, "instrument": None, "record": None, "redcap_event_name": None, 
    #                "redcap_data_access_group": None, "instrument_complete": None, "redcap_repeat_instance": None, "redcap_repeat_instrument": None, 
    #                "redcap_url": None, "project_url": None}

    if flask.request.method == 'POST':
        if flask.request.remote_addr in ip_list:
            data = flask.request.get_json(force=True)
            
            for data_field in redcap_data.keys():
                redcap_data[data_field] = data.get(data_field, None)

            logging.info(f"inputted redcap_data: {redcap_data}")

            thread_qc = threading.Thread(target=operate_quality_control_individual, kwargs={'data_entry': redcap_data, 
                                                                                            'outlier_method': outlier_method, 
                                                                                            'outlier_qc': True, 
                                                                                            'missing_qc': True, 
                                                                                            'routine': False, 
                                                                                            'production_mode': production_mode})
            thread_qc.start()
        else:
            logging.info(f"Unauthorized access from {flask.request.remote_addr}")
            return 'Unauthorized access \n'

    return 'Running QC in the background \n'

if __name__ == '__main__':
    waitress.serve(app, host="127.0.0.1", port=5000, connection_limit=1500, threads=50)
