<!-- markdownlint-disable -->

# <kbd>module</kbd> `app`




**Global Variables**
---------------
- **rootdir**
- **logdir**
- **logfile**
- **outlier_method**
- **pid_list**
- **alert_threshold**
- **ping**
- **production_mode**
- **routine_hours**
- **ipfile**
- **file**
- **ip_list**

---

## <kbd>function</kbd> `common_troubleshooting`

```python
common_troubleshooting()
```

Returns common troubleshooting fixes. 


---

## <kbd>function</kbd> `logfile_tail`

```python
logfile_tail()
```

Returns the last 10 lines of the log file. 


---

## <kbd>function</kbd> `routing_links`

```python
routing_links()
```

Returns the webpage routes. 


---

## <kbd>function</kbd> `default_page`

```python
default_page()
```

Returns the default webpage structure with routing, troubleshooting, and log file. 


---

## <kbd>function</kbd> `home`

```python
home()
```

Routed from / and /flaskApp/. Returns the default webpage.  


---

## <kbd>function</kbd> `update_triggers`

```python
update_triggers()
```

Routed from /flaskApp/update-triggers/ and when triggered by POST request from MariaDB. POST request is triggered when projects table is updated. 

Refreshes all stored data and triggers for all projects. 


---

## <kbd>function</kbd> `outlier_and_missing_routine`

```python
outlier_and_missing_routine()
```

Runs when triggered by POST request from MariaDB. Checks for outliers and missing data in all projects. Sends email if the last run was more than routine_hours ago. Sends email blast for drw entries that are more than 24 hours old. 


---

## <kbd>function</kbd> `receive_from_maria`

```python
receive_from_maria()
```

Runs when triggered by POST request from MariaDB.  Receives data from MariaDB and runs quality control if IP is authorized. 

Inputs data from redcap_log_event table 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
