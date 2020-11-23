from dotenv import load_dotenv
import os
import logging
import warnings


DEFAULTS = {
    # system
    "LOG_FOLDER": "_logs",  # folder where to log the log files
    "AUTH_TOKEN": None,  # no authentication required
    "PORT": 4999,  # default port
    "ENABLED_LOG_LEVELS": "ERROR,INFO",
}

_NAME_TO_LOG_LEVEL = {
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


def load_config():
    """
    Loads values from the environment variables provided to this application via the .env file or by passing them in as
    regular environment variables. After extracting from whatever environment variables are available, default values
    will be applied for any environment variable that is not provided, but for which a default exists.
    :return: a config map with the whole system configuration
    """
    # read out existing os environment
    load_dotenv()
    config = {}
    for key in [] + list(DEFAULTS.keys()):
        # database
        config[key] = os.getenv(key)

    # apply defaults for missing config params
    for key in DEFAULTS:
        if key not in config or config[key] is None:
            config[key] = DEFAULTS[key]

    return config


def get_log_folder():
    config = load_config()
    return config["LOG_FOLDER"]


def get_port():
    config = load_config()
    return config["PORT"]


def get_auth_token():
    config = load_config()
    if "AUTH_TOKEN" in config:
        return config["AUTH_TOKEN"]
    return None


def get_enabled_log_levels():
    config = load_config()
    enabled = list(map(lambda x: x.strip(), config["ENABLED_LOG_LEVELS"].split(",")))

    result = []
    for log_level in enabled:
        if log_level not in _NAME_TO_LOG_LEVEL:
            warnings.warn("Provided invalid log level in 'ENABLED_LOG_LEVELS': {}".format(log_level))
            continue
        result.append(_NAME_TO_LOG_LEVEL[log_level])

    if len(result) == 0:
        warnings.warn("No log levels enabled. Log server will not log anything.")
    return result
