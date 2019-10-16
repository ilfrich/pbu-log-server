from dotenv import load_dotenv
import os


DEFAULTS = {
    # system
    "LOG_FOLDER": "_logs",  # folder where to log the log files
    "AUTH_TOKEN": None,  # no authentication required
    "PORT": 4999,  # default port
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

    # check if log folder exists
    if not os.path.isdir(config["LOG_FOLDER"]):
        os.mkdir(config["LOG_FOLDER"])

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
