import logging
import warnings
from typing import List, Optional
from pbu import BasicConfig


DEFAULTS = {
    # system
    "IS_DEBUG": "0",
    "LOG_FOLDER": "_logs",  # folder where to log the log files
    "AUTH_TOKEN": None,  # no authentication required
    "PORT": 5337,  # default port
    # logging
    "ENABLED_LOG_LEVELS": "ERROR,INFO",
}

_NAME_TO_LOG_LEVEL = {
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


class AppConfig(BasicConfig):
    def __init__(self):
        super().__init__(default_values=DEFAULTS, directory_keys=["LOG_FOLDER"])


    def get_log_folder(self) -> str:
        return self.get_config_value("LOG_FOLDER")


    def get_port(self) -> int:
        return int(self.get_config_value("PORT"))


    def get_auth_token(self) -> Optional[str]:
        return self.get_config_value("AUTH_TOKEN")


    def get_enabled_log_levels(self) -> List[str]:
        values = self.get_config_value("ENABLED_LOG_LEVELS")
        if values is None or values == "":
            warnings.warn("No log levels enabled. Log server will not log anything.")

        enabled = list(map(lambda x: x.strip(), values.split(",")))

        result = []
        for log_level in enabled:
            if log_level not in _NAME_TO_LOG_LEVEL:
                warnings.warn(f"Provided invalid log level in 'ENABLED_LOG_LEVELS': {log_level}")
                continue
            result.append(_NAME_TO_LOG_LEVEL[log_level])

        if len(result) == 0:
            warnings.warn("No log levels enabled. Log server will not log anything.")
        return result

    def is_debug(self) -> bool:
        return self.get_config_value("IS_DEBUG", "0") == "1"
