# PBU Log Server

A small lightweight web server to receive log messages via an API and aggregates them into log files. This is a 
companion repository to the Pip package [`python-basic-utils`](https://github.com/ilfrich/python-basic-utils) (`pbu`).

**Table of Contents**

1. [The Problem](#what-problem-does-the-log-server-solve)
    1. [Multi-Threading](#multi-threaded-python-applications)
    2. [Alternatives](#alternative-solutions)
    3. [Benefits of Log Server](#benefits-of-the-log-server)
2. [Run the Log Server](#how-to-run-the-log-server)
    1. [Configuration](#configure-the-log-server)
3. [Sending Messages to the Log Server](#how-to-use-pbu-to-send-log-messages)


## What Problem does the Log Server solve?

### Multi-Threaded Python Applications

When you have a multi-threaded Python application, that writes log messages into a log file and has any roll-over policy
for those logs (e.g. create a new log file for every day), then the roll-over will cause all the threads in the system
to close and flush the log file at the end of the roll-over period. This leads to only one thread writing to the log 
file and all other log messages being lost.

### Alternative Solutions

The problem can also be solved with some application internal log synchronisation, where all your threads push log 
messages into a queue, which is read by a single thread and written to a log file.

### Benefits of the Log Server

The log server offers an alternative, where each thread of your multi-threaded Python application will send serialised 
`LogRecord` objects and send them via REST to the log server, which runs only a single thread and writes those log 
messages to the log file.

This offers the additional benefit of being able to receive log messages from multiple applications in a cluster and 
aggregate those log messages in one place. 

## What is the Log Server

The log server is a lightweight Flask app, which offers only one POST endpoint to `/api/log`. The payload is of 
`Content-Type: "application/json"` and contains the fields of a Python `logging.LogRecord` object, containing keys such 
as: `asctime`, `created`, `name`, `levelname`, `message` and more. See the keys created for `LogRecord.__dict__`

The log server will create log files `info.log`, `error.log`, `warning.log` and `debug.log` depending on which logging 
levels are activated.

## How to run the Log Server

- Clone the repository
- Install `pip` dependencies: `pip install -r requirements.txt`
- Start the server `make start` (or `python runner.py`)

### Configure the Log Server

The server allows a couple of configuration parameters passed via environment variables:

- `LOG_FOLDER`: a path to a directory where to store the log files. If the directory does not exist, the server will 
attempt to create it. Default: `./_logs`
- `AUTH_TOKEN`: an API token used as `Authentication` header by any Python application submitting log messages to the 
log server. Default: `None` (no authentication required, only use during development)
- `PORT`: the port number to run the log server on. Default: `4999` 
- `ENABLED_LOG_LEVELS`: a comma separated list of capitalised log levels (available: `INFO`, `DEBUG`, `ERROR`, 
`WARNING`). Example: `ENABLED_LOG_LEVELS=WARNING,ERROR`. Default: `INFO,ERROR`.

## How to use `pbu` to send log messages

- Add `pbu` to your applications dependencies: `pip install pbu`
- Provide environment variables to your application:
    - `PBU_LOG_SERVER`: the IP:PORT where the log server is running, e.g. `PBU_LOG_SERVER=http://localhost:4999`
    - `PBU_LOG_SERVER_AUTH`: the API token used to authenticate against the log server, has to match `AUTH_TOKEN` 
    environment variable of the log server. In case the log server doesn't use the `AUTH_TOKEN` variable, the variable 
    can be omitted for your application as well.
- Instantiate the logger in your code and start logging:

```python
from pbu import Logger
logger = Logger("my-logger-name")
logger.info("Hello log server")
```

By providing `PBU_LOG_SERVER` to an application that uses `pbu`, it will ignore the `log_folder=` parameter passed to 
the `pbu.Logger` when the logger is instantiated. It will also ignore the `PBU_LOG_FOLDER` environment variable passed 
to your application.

**Important Note**: Currently, when you use `logger.exception(message)`, the stack trace will be logged on your applications `stdout` 
(`print(message)`). This is planned to be changed and the stack trace being logged into the log-server as well. Details
in issue #1. 