import logging
import os
from logging.handlers import TimedRotatingFileHandler

class ErrorLogger:
    """
    ErrorLogger provides a simple interface for logging error messages to a
    file located in the same directory as this script. It uses Python's
    built-in logging module to manage log file creation, message formatting,
    and log level handling.
    """
    _instance = None

    @classmethod
    def get_instance(cls, directory=None, log_level=logging.INFO, log_file_name='error.log'):
        if cls._instance is None:
            cls._instance = cls(directory, log_level=log_level, log_file_name=log_file_name)
        return cls._instance

    def __init__(self, directory=None, log_level=logging.INFO, log_file_name='error.log'):
        """
        Initializes the ErrorLogger, setting up the logging configuration
        including the log file name, format, and log level.

        Parameters:
            directory (str): The directory where the log file will be stored.
            log_file_name (str): The name of the file where log messages will be stored.
            log_level (int): The logging level (e.g., logging.ERROR, logging.DEBUG).

        Log levels:
            logging.CRITICAL: 50
            logging.ERROR: 40
            logging.WARNING: 30
            logging.INFO: 20
            logging.DEBUG: 10
            logging.NOTSET: 0
        """
        if self._instance is not None:
            raise Exception("ErrorLogger is a singleton!")
        if directory is None:
            directory = os.getcwd()  # Default to the current working directory
        log_file = os.path.join(directory, log_file_name)

        self.logger = logging.getLogger('ErrorLogger')
        self.logger.setLevel(log_level)

        # Ensure that the logger does not duplicate messages
        if not self.logger.handlers:
            handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=7)  # Rotate daily, keep 7 backups
            formatter = logging.Formatter('%(asctime)s.%(msecs)03d - '
                                          '%(levelname)s - %(message)s',
                                          datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_log_level(self, log_level_str):
        """
        Changes the log level of the current logger instance.

        Parameters:
            log_level (int): The logging level (e.g., logging.ERROR, logging.DEBUG).
        """
        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        try:
            new_log_level = log_levels.get(log_level_str.upper())
            self.logger.setLevel(new_log_level)
            self.log_error(f'Log level set to {new_log_level}')
        except Exception as e:
            self.log_error(f'Error while setting log level: {e}')

    def log_critical(self, message):
        """
        Logs a cricital error message to the configured log file.

        Parameters:
            message (str): The error message to log.
        """
        self.logger.critical(message)

    def log_error(self, message):
        """
        Logs an error message to the configured log file.

        Parameters:
            message (str): The error message to log.
        """
        self.logger.error(message)

    def log_warning(self, message):
        """
        Logs a warning message to the configured log file.

        Parameters:
            message (str): The warning message to log.
        """
        self.logger.warning(message)

    def log_info(self, message):
        """
        Logs an info message to the configured log file.

        Parameters:
            message (str): The info message to log.
        """
        self.logger.info(message)

    def log_debug(self, message):
        """
        Logs a debug message to the configured log file.

        Parameters:
            message (str): The info message to log.
        """
        self.logger.debug(message)