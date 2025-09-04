import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

__all__ = ['set_standard_logging_config', 'init_root_logger']

def suppress_common_packages():
    """Suppress INFO logs from common packages to reduce clutter"""
    # setting warning level to various packages to avoid additional logs
    packages = ('botocore', 'boto3', 'requests', 'urllib3', 'rasterio', 'shapely', 'paramiko')
    for p in packages:
        p_logger = logging.getLogger(p)
        p_logger.setLevel(logging.WARNING)


def get_fmt_string(code: str = None, env: str = None) -> str:
    """Creates common format string for logging

    Args:
        code: an optional flight code to include
        env: an optional environment to include

    Returns:
        a format string
    """
    format_str = "[{asctime}][{levelname}][{name}]: {message}"

    if code:
        format_str = "[{}]{}".format(code, format_str)

    if env:
        format_str = "[{}]{}".format(env, format_str)

    return format_str


def set_standard_logging_config(*, level=logging.INFO, stdout: bool = True, stderr: bool = False, logfile: str = None,
                                code: str = None, env: str = None, suppress_packages: bool = True):
    """Sets a standard logging context

    Args:
        level: the logging level of the root logger
        stdout: if true will print logs to stdout
        stderr: if true will print logs to stderr
        logfile: an optional path to write logs to
        code: an optional code to include in the logging output
        env: an optional environment to include in the logging output
        suppress_packages: if true will suppress info messages from common packages
    """

    if env is None and 'IA_ENV' in os.environ:
        env = os.environ['IA_ENV']

    if suppress_packages:
        suppress_common_packages()

    if 'IA_LOGGING_FMT' in os.environ and os.environ['IA_LOGGING_FMT'] != '':
        fmt_string = os.environ['IA_LOGGING_FMT']
    else:
        fmt_string = get_fmt_string(code=code, env=env)

    handlers = list()

    if stdout:
        handlers.append(logging.StreamHandler(sys.stdout))

    if stderr:
        handlers.append(logging.StreamHandler(sys.stderr))

    if logfile:
        handlers.append(logging.FileHandler(logfile))

    if 'IA_LOGFILE' in os.environ and os.environ['IA_LOGFILE'] != '':
        handlers.append(logging.FileHandler(os.environ['IA_LOGFILE']))

    logging.basicConfig(level=level, handlers=handlers, format=fmt_string, style='{', force=True)


def init_root_logger(
    logfile=None, code=None, env=None, logging_level=logging.INFO, log_rotate=False, daily_log_file=None
):
    packages = (
        "botocore",
        "boto3",
        "requests",
        "urllib3",
        "rasterio",
        "shapely",
        "paramiko",
        "fiona",
        "filelock",
        "s3transfer",
    )
    for p in packages:
        logger = logging.getLogger(p)
        logger.setLevel(logging.WARNING)

    # resets all loggers handlers to escape from duplicate handlers
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]

    for l in loggers:
        if l.handlers:
            l.handlers.clear()

    format_str = get_fmt_string(code=code, env=env)

    handlers = []
    handlers.append(logging.StreamHandler(sys.stdout))

    if logfile:
        handlers.append(logging.FileHandler(logfile))

    if log_rotate:
        # This piece of code will create a log file but the log will be moved to a new log file
        # named log-daily-{machine_name}.txt.{previous_date}
        # when the current day ends at midnight.

        handler = TimedRotatingFileHandler(daily_log_file, when="midnight", backupCount=1)
        handlers.append(handler)

    root_logger = logging.getLogger()

    # imitating `force=True` flag in `logging.basicConfig`
    root_logger.handlers.clear()

    for handler in handlers:
        handler.setFormatter(logging.Formatter(format_str, style="{"))
        handler.setLevel(logging_level)
        root_logger.addHandler(handler)
