import os
import logging
from time import sleep
from datetime import timedelta, datetime
from typing import List, Optional
from pytz import utc
from pbu import set_timezone, ensure_directory, DATE_FORMAT

def get_utc_offset():
    local_dt = set_timezone(datetime.now(), utc)
    utc_dt = datetime.now(tz=utc)

    return round(local_dt.timestamp() - utc_dt.timestamp())


SERVER_UTC_OFFSET = get_utc_offset()
LOG_DATETIME_FORMAT = f"{DATE_FORMAT} %H:%M:%S.%f"
LOG_STR = {
    logging.ERROR: "ERROR",
    logging.INFO: "INFO",
    logging.WARN: "WARN",
    logging.DEBUG: "DEBUG",
}


def to_server_timezone(localised_datetime: datetime) -> datetime:
    return datetime.fromtimestamp(localised_datetime.timestamp())

def format_date(dt: datetime) -> str:
    return dt.strftime(LOG_DATETIME_FORMAT)[:-3]

def parse_date(date_str: str) -> datetime:
    return datetime.strptime(f"{date_str}000", LOG_DATETIME_FORMAT)

def round_to_nearest_interval(date_time: datetime, interval: timedelta) -> datetime:
    """
    Given a specific date time, this function will find the nearest interval given a time delta.
    :param date_time: the datetime to start from
    :param interval: a timedelta to round to
    :returns: a datetime object that is rounded.
    """

    seconds = round(interval.total_seconds())
    ts = round(date_time.timestamp()) + SERVER_UTC_OFFSET
    mod = ts % seconds
    # round down
    return datetime.fromtimestamp(ts - mod - SERVER_UTC_OFFSET, tz=date_time.tzinfo)


class AdvancedLogger:
    def __init__(self, log_folder: Optional[str], log_duration: Optional[timedelta] = timedelta(days=1)) -> None:
        if log_duration is not None and log_duration.total_seconds() < 3600:
            # less than an hour
            raise ValueError("Log duration of less than 1h is currently not supported")
        
        if log_folder is not None:
            ensure_directory(log_folder)

        # configuration values
        self.log_folder = log_folder
        self.log_duration = log_duration

        # in-memory handles for datetimes and open files
        self._log_files = {}  # log level > open file
        self._log_intervals = {}  # log level > datetime

    def log_message(self, message: logging.LogRecord):
        # extract log level and compose message
        log_level: str = LOG_STR[message.levelno]
        result = f"[{format_date(datetime.now())}] {log_level}:{message.name}:{message.lineno} {message.msg}"
        if self.log_folder is None:
            print(result)  # just print to console
            return 
        
        # handle file logging
        interval = round_to_nearest_interval(datetime.now(), self.log_duration)

        if log_level not in self._log_intervals or log_level not in self._log_files:
            # logger needs to be initialised
            self._init_logger(interval, log_level)
        
        # check the interval
        if self._log_intervals[log_level] != interval:
            # need to close old logger and create new one
            self._close_logger(log_level)
            self._init_logger(interval, log_level)

        self._write_message(log_level, result)

    def get_log_messages(self, log_level: str, start_date: datetime, end_date: datetime) -> List[dict]:
        """
        Retrieve log messages of the given log level between start and end date.
        :param log_level: the log level expresses as capitalised string
        :param start_date: the start date as localised date provided in the interface
        :param end_date: the end date as localised date provided in the interface
        :returns: a list of messages provided as dictionaries
        """
        start_dt = to_server_timezone(start_date)
        end_dt = to_server_timezone(end_date)

        result = []
        current_file_dt = round_to_nearest_interval(start_dt, self.log_duration) - self.log_duration
        while current_file_dt < end_dt:
            current_file_dt += self.log_duration

            log_path = self._get_log_file_path(log_level, current_file_dt)
            if not os.path.exists(log_path):   
                continue  # log file doesn't exist, next file
            
            # read log file
            fp = open(log_path, "r")
            lines = fp.readlines()
            fp.close()

            file_messages = []
            current_message = None
            for line in lines:
                if line.startswith("["):
                    # new log message starts here
                    if current_message is not None:
                        # we have a previous log message, that needs to be added
                        file_messages.append(current_message)
                    
                    # reset current message
                    current_message = None
                    # parse datetime and check if it fits within the requested interval
                    message_tokens = line.split(" ")
                    log_dt = parse_date(" ".join(message_tokens[0:2])[1:-1])
                    if log_dt > end_dt:
                        break  # stop processing this log file as we've reached the end of the requested time frame
                    if log_dt < start_dt:
                        continue  # message too early, skip this

                    current_message = {
                        "ts": round(log_dt.timestamp()),
                        "name": message_tokens[2],
                        "msg": " ".join(message_tokens[3:]).replace("\n", "")
                    }
                    continue

                if current_message is not None:
                    # additional log details (error trace)
                    if "detail" not in current_message:
                        current_message["detail"] = []
                    current_message["detail"].append(line.replace("\n", ""))
            
            # after reaching the end of the log file, append that last message
            if current_message is not None:
                file_messages.append(current_message)
            
            # store previous file messages to result
            result.extend(file_messages)

        return result
        
    
    def _get_log_file_path(self, log_level: str, interval: datetime) -> str:
        log_suffix = interval.strftime(DATE_FORMAT) if self.log_duration.total_seconds() >= 60 * 60 * 24 else interval.strftime(f"{DATE_FORMAT}_%H")
        return os.path.join(self.log_folder, f"{log_level.lower()}_{log_suffix}.log")

    def _init_logger(self, interval: datetime, log_level: str):

        if log_level in self._log_intervals and self._log_intervals[log_level] is not None and self._log_intervals != interval:
            self._close_logger(log_level)
        
        if log_level in self._log_files and self._log_files[log_level] is not None:
            self._close_logger(log_level)

        if self.log_folder is None:
            raise ValueError("Cannot init logger without a log folder")
        
        fp = open(self._get_log_file_path(log_level, interval), "a")
        self._log_files[log_level] = fp
        self._log_intervals[log_level] = interval

    def _close_logger(self, log_level: str):
        if self._log_files[log_level] is None:
            return  # nothing to do
        
        self._log_files[log_level].close()
        del self._log_files[log_level]

    def _write_message(self, log_level: str, message: str, is_retry: bool = False):
        try:
            self._log_files[log_level].write(f"{message}\n")
            self._log_files[log_level].flush()
        except BaseException as be:
            #  this can happen if the file handler was just closed or some other parallel activity interrupted the write
            if is_retry is True:
                raise be   # this is already the retry, something is wrong!
            # wait 2s and try again
            sleep(2)
            self._write_message(log_level, message, is_retry=True)
