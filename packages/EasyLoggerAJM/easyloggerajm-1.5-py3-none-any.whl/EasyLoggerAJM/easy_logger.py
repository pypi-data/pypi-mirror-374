"""
easy_logger.py

logger with already set up generalized file handlers

"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Union, List

from EasyLoggerAJM import ConsoleOneTimeFilter
from EasyLoggerAJM import _EasyLoggerCustomLogger
from EasyLoggerAJM import ColorizedFormatter, NO_COLORIZER


class _LogSpec:
    """
        Class `_LogSpec` is a container for predefined log specifications and timestamp formats,
        organized by time intervals (daily, hourly, and minute-based).
        These specifications are auto-generated based on the current date and time.

        Attributes:
            MINUTE_LOG_SPEC_FORMAT : tuple
                A tuple containing the current date (ISO formatted) and time up to minutes in string format without colons.
            MINUTE_TIMESTAMP : str
                A compact ISO formatted timestamp up to minutes excluding colons.

            HOUR_LOG_SPEC_FORMAT : tuple
                A tuple containing the current date (ISO formatted) and time truncated to the hour in string format
                    (e.g., "1400" for 2 PM).
            HOUR_TIMESTAMP : str
                A compact ISO formatted timestamp indicating the hour without colons.

            DAILY_LOG_SPEC_FORMAT : str
                The current date as an ISO formatted string.
            DAILY_TIMESTAMP : str
                The current date truncated to the hour component formatted in ISO standard.

            LOG_SPECS : dict
                A dictionary containing log specifications for daily, hourly, and minute time intervals.
                    Each key corresponds to the time interval ('daily', 'hourly', 'minute') and its value is another dictionary with:
                    - 'name': Name of the log interval.
                    - 'format': Predefined time format of the given interval.
                    - 'timestamp': Compact timestamp matching the logical interval.
    """
    # this is a tuple of the date and the time down to the minute
    MINUTE_LOG_SPEC_FORMAT = (datetime.now().date().isoformat(),
                              ''.join(datetime.now().time().isoformat().split('.')[0].split(":")[:-1]))
    MINUTE_TIMESTAMP = datetime.now().isoformat(timespec='minutes').replace(':', '')

    HOUR_LOG_SPEC_FORMAT = datetime.now().date().isoformat(), (
            datetime.now().time().isoformat().split('.')[0].split(':')[0] + '00')
    HOUR_TIMESTAMP = datetime.now().time().isoformat().split('.')[0].split(':')[0] + '00'

    DAILY_LOG_SPEC_FORMAT = datetime.now().date().isoformat()
    DAILY_TIMESTAMP = datetime.now().isoformat(timespec='hours').split('T')[0]

    LOG_SPECS = {
        'daily': {
            'name': 'daily',
            'format': DAILY_LOG_SPEC_FORMAT,
            'timestamp': DAILY_TIMESTAMP
        },
        'hourly': {
            'name': 'hourly',
            'format': HOUR_LOG_SPEC_FORMAT,
            'timestamp': HOUR_TIMESTAMP
        },
        'minute': {
            'name': 'minute',
            'format': MINUTE_LOG_SPEC_FORMAT,
            'timestamp': MINUTE_TIMESTAMP
        }
    }


# noinspection PyUnresolvedReferences
class _InternalLoggerMethods:
    """
    This class contains internal utility methods for configuring and logging internal
    operations of the logger. These methods are designed for internal use and handle
    logging of initial attributes, setting up file and stream handlers, and initializing
    the internal logger.

    Methods
    -------
    _log_attributes_internal(logger_kwargs)
        Logs the initial state of key instance attributes and any additional keyword
        arguments passed during initialization.

    _setup_internal_logger_handlers(verbose=False)
        Sets up handlers for the internal logger, including a file handler to log into
        a predefined file and, optionally, a stream handler for console output.

    _setup_internal_logger(**kwargs)
        Initializes and configures the internal logger with a designated logging level
        and handlers. Returns the initialized logger.
    """

    def _log_attributes_internal(self, logger_kwargs):
        """
        Logs internal attributes and initialization parameters for debugging purposes.

        :param logger_kwargs: Arguments passed during the initialization of the instance.
        :type logger_kwargs: dict
        """
        self._internal_logger.info(f"root_log_location set to {self._root_log_location}")
        self._internal_logger.info(f"chosen_format set to {self._chosen_format}")
        self._internal_logger.info(f"no_stream_color set to {self._no_stream_color}")
        self._internal_logger.info(f"kwargs passed to __init__ are {logger_kwargs}")

    def _setup_internal_logger_handlers(self, verbose=False):
        """
        :param verbose: Indicates whether to enable verbose logging. If True, adds a StreamHandler to log messages to the console.
        :type verbose: bool
        :return: None
        :rtype: None
        """
        log_file_path = Path(self._root_log_location,
                             'EasyLogger_internal.log'.replace('\\', '/'))
        fmt = logging.Formatter(self._chosen_format)

        log_file_mode = 'w'
        if not log_file_path.exists():
            Path(self._root_log_location).mkdir(parents=True, exist_ok=True)
        h = logging.FileHandler(log_file_path, mode=log_file_mode)
        h.setFormatter(fmt)
        self._internal_logger.addHandler(h)

        if verbose:
            h2 = logging.StreamHandler()
            h2.setFormatter(fmt)
            self._internal_logger.addHandler(h2)

    def _setup_internal_logger(self, **kwargs):
        """
        Sets up the internal logger for the application.

        :param kwargs: Optional keyword arguments for configuring the logger.
            The key 'verbose' can be used to enable or disable verbose logging.
        :return: The configured internal logger instance.
        :rtype: logging.Logger
        """
        self._internal_logger = logging.getLogger('EasyLogger_internal')
        self._internal_logger.propagate = False
        self._internal_logger.setLevel(10)
        self._setup_internal_logger_handlers(verbose=kwargs.get('verbose', False))

        self._internal_logger.info("internal logger initialized")
        return self._internal_logger


class EasyLogger(_LogSpec, _InternalLoggerMethods):
    """

    EasyLogger
    ==========

    Class to provide an easy logging mechanism for projects.

    Attributes:
    -----------
    DEFAULT_FORMAT : str
        Default log format used in the absence of a specified format.

    INT_TO_STR_LOGGER_LEVELS : dict
        Mapping of integer logger levels to their string representations.

    STR_TO_INT_LOGGER_LEVELS : dict
        Mapping of string logger levels to their integer representations.

    MINUTE_LOG_SPEC_FORMAT : tuple
        Tuple representing the log specification format at minute granularity.

    MINUTE_TIMESTAMP : str
        Timestamp at minute granularity.

    HOUR_LOG_SPEC_FORMAT : tuple
        Tuple representing the log specification format at hour granularity.

    HOUR_TIMESTAMP : str
        Timestamp at hour granularity.

    DAILY_LOG_SPEC_FORMAT : str
        String representing the log specification format at daily granularity.

    DAILY_TIMESTAMP : str
        Timestamp at daily granularity.

    LOG_SPECS : dict
        Dictionary containing predefined logging specifications.

    Methods:
    --------
     __init__(self, project_name=None, root_log_location="../logs", chosen_format=DEFAULT_FORMAT, logger=None, **kwargs)
        Initialize EasyLogger instance with provided parameters.

    file_logger_levels(self)
        Property to handle file logger levels.

    project_name(self)
        Property method to get the project name.

    inner_log_fstructure(self)
        Get the inner log file structure.

    log_location(self)
        Get the log location for file handling.

    log_spec(self)
        Handle logging specifications.

    classmethod UseLogger(cls, **kwargs)
        Instantiate a class with a specified logger.

    Note:
    -----
    The EasyLogger class provides easy logging functionality for projects,
    allowing customization of log formats and levels.

    """
    DEFAULT_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'

    # TODO: replace these with checks using logging.getlevelname()
    INT_TO_STR_LOGGER_LEVELS = {
        10: 'DEBUG',
        20: 'INFO',
        30: 'WARNING',
        40: 'ERROR',
        50: 'CRITICAL'
    }

    STR_TO_INT_LOGGER_LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }

    def __init__(self, project_name=None, root_log_location="../logs",
                 chosen_format=DEFAULT_FORMAT, logger=None, **kwargs):
        self._chosen_format = chosen_format
        self._no_stream_color = kwargs.get('no_stream_color', False)
        self._root_log_location = root_log_location

        self._internal_logger = self._setup_internal_logger(verbose=kwargs.get('internal_verbose', False))

        self._log_attributes_internal(kwargs)

        # properties
        self._file_logger_levels = kwargs.get('file_logger_levels', [])
        self._project_name = project_name
        self._inner_log_fstructure = None
        self._log_location = None
        self._log_spec = kwargs.get('log_spec', None)

        self.show_warning_logs_in_console = kwargs.get('show_warning_logs_in_console', False)
        self._internal_logger.info(f'show_warning_logs_in_console set to {self.show_warning_logs_in_console}')

        self.timestamp = kwargs.get('timestamp', self.log_spec['timestamp'])
        if self.timestamp != self.log_spec['timestamp']:
            self.timestamp = self.set_timestamp(**{'timestamp': self.timestamp})

        self.formatter, self.stream_formatter = self._setup_formatters(**kwargs)

        self.logger = self.initialize_logger(logger=logger)

        self.make_file_handlers()

        if self.show_warning_logs_in_console:
            self._internal_logger.info('warning logs will be printed to console - creating stream handler')
            self.create_stream_handler()

        self.post_handler_setup()

    @staticmethod
    def _get_level_handler_string(handlers: List[logging.Handler]) -> str:
        return ', '.join([' - '.join((x.__class__.__name__, logging.getLevelName(x.level)))
                          for x in handlers])

    @classmethod
    def UseLogger(cls, **kwargs):
        """
        This method is a class method that can be used to instantiate a class with a logger.
        It takes in keyword arguments and returns an instance of the class with the specified logger.

        Parameters:
        - **kwargs: Keyword arguments that are used to instantiate the class.

        Returns:
        - An instance of the class with the specified logger.

        Usage:
            MyClass.UseLogger(arg1=value1, arg2=value2)

        Note:
            The logger used for instantiation is obtained from the `logging` module and is named 'logger'.
        """
        return cls(**kwargs, logger=kwargs.get('logger', None)).logger

    @property
    def file_logger_levels(self):
        if self._file_logger_levels:
            if [x for x in self._file_logger_levels
                if x in self.__class__.STR_TO_INT_LOGGER_LEVELS
                   or x in self.__class__.INT_TO_STR_LOGGER_LEVELS]:
                if any([isinstance(x, str) and not x.isdigit() for x in self._file_logger_levels]):
                    self._file_logger_levels = [self.__class__.STR_TO_INT_LOGGER_LEVELS[x] for x in
                                                self._file_logger_levels]
                elif any([isinstance(x, int) for x in self._file_logger_levels]):
                    pass
        else:
            self._file_logger_levels = [self.__class__.STR_TO_INT_LOGGER_LEVELS["DEBUG"],
                                        self.__class__.STR_TO_INT_LOGGER_LEVELS["INFO"],
                                        self.__class__.STR_TO_INT_LOGGER_LEVELS["ERROR"]]
        return self._file_logger_levels

    @property
    def project_name(self):
        """
        Getter for the project_name property.

        Returns the name of the project. If the project name has not been set previously,
         it is determined based on the filename of the current file.

        Returns:
            str: The name of the project.
        """
        if self._project_name:
            pass
        else:
            self._project_name = __file__.split('\\')[-1].split(".")[0]

        return self._project_name

    @property
    def inner_log_fstructure(self):
        """
        Getter method for retrieving the inner log format structure.

        This method checks the type of the log_spec['format'] attribute and returns
            the inner log format structure accordingly.
        If the log_spec['format'] is of type str, the inner log format structure is set as
            "{}".format(self.log_spec['format']).
        If the log_spec['format'] is of type tuple, the inner log format structure is set as
            "{}/{}".format(self.log_spec['format'][0], self.log_spec['format'][1]).

        Returns:
            str: The inner log format structure.
        """
        if isinstance(self.log_spec['format'], str):
            self._inner_log_fstructure = "{}".format(self.log_spec['format'])
        elif isinstance(self.log_spec['format'], tuple):
            self._inner_log_fstructure = "{}/{}".format(self.log_spec['format'][0], self.log_spec['format'][1])
        return self._inner_log_fstructure

    @property
    def log_location(self) -> Path:
        """
        Getter method for retrieving the log_location property.

        Returns:
            str: The absolute path of the log location.
        """
        self._log_location = Path(self._root_log_location,
                                  self.inner_log_fstructure)
        if self._log_location.is_dir():
            pass
        else:
            self._log_location.mkdir(parents=True, exist_ok=True)
        return self._log_location

    @property
    def log_spec(self):
        if self._log_spec is not None:
            if isinstance(self._log_spec, dict):
                try:
                    self._log_spec = self._log_spec['name']
                except KeyError:
                    raise KeyError("if log_spec is given as a dictionary, "
                                   "it must include the key/value for 'name'."
                                   " otherwise it should be passed in as a string.") from None

            elif isinstance(self._log_spec, str):
                pass

            # since all the keys are in lower case, the passed in self._log_spec should be set to .lower()
            if self._log_spec.lower() in list(self.LOG_SPECS.keys()):
                self._log_spec = self.LOG_SPECS[self._log_spec.lower()]
            else:
                raise AttributeError(
                    f"log spec must be one of the following: {str(list(self.LOG_SPECS.keys()))[1:-1]}.")
        else:
            self._log_spec = self.LOG_SPECS['minute']
        return self._log_spec

    def initialize_logger(self, logger=None) -> Union[logging.Logger, _EasyLoggerCustomLogger]:
        if not logger:
            self._internal_logger.info('no passed in logger detected')
            logging.setLoggerClass(_EasyLoggerCustomLogger)
            self._internal_logger.info('logger class set to _EasyLoggerCustomLogger')
            # Create a logger with a specified name and make sure propagate is True
            self.logger = logging.getLogger('logger')
        else:
            self._internal_logger.info(f'passed in logger ({logger}) detected')
            self.logger: logging.getLogger = logger
        self.logger.propagate = True
        self._internal_logger.info('logger initialized')
        self._internal_logger.info(f'propagate set to {self.logger.propagate}')
        return self.logger

    def post_handler_setup(self):
        # set the logger level back to DEBUG, so it handles all messages
        self.logger.setLevel(10)
        self._internal_logger.info(f'logger level set back to {self.logger.level}')
        self.logger.info(f"Starting {self.project_name} with the following handlers: "
                         f"{self._get_level_handler_string(self.logger.handlers)}")
        if not self._no_stream_color and NO_COLORIZER:
            self.logger.warning("colorizer not available, logs may not be colored as expected.")
        self._internal_logger.info("final logger initialized")
        # print("logger initialized")

    def set_timestamp(self, **kwargs):
        """
        This method, `set_timestamp`, is a static method that can be used to set a timestamp for logging purposes.
        The method takes in keyword arguments as parameters.

        Parameters:
            **kwargs (dict): Keyword arguments that can contain the following keys:
                - timestamp (datetime or str, optional): A datetime object or a string representing a timestamp.
                    By default, this key is set to None.

        Returns:
            str: Returns a string representing the set timestamp.

        Raises:
            AttributeError: If the provided timestamp is not a datetime object or a string.

        Notes:
            - If the keyword argument 'timestamp' is provided, the method will return the provided timestamp if it is a
                datetime object or a string representing a timestamp.
            - If the keyword argument 'timestamp' is not provided or is set to None, the method will generate a
                timestamp using the current date and time in ISO format without seconds and colons.

        Example:
            # Set a custom timestamp
            timestamp = set_timestamp(timestamp='2022-01-01 12:34')

            # Generate a timestamp using current date and time
            current_timestamp = set_timestamp()
        """
        timestamp = kwargs.get('timestamp', None)
        if timestamp is not None:
            if isinstance(timestamp, (datetime, str)):
                self._internal_logger.info(f"timestamp set to {timestamp}")
                return timestamp
            else:
                try:
                    raise AttributeError("timestamp must be a datetime object or a string")
                except AttributeError as e:
                    self._internal_logger.error(e, exc_info=True)
                    raise e from None
        else:
            timestamp = datetime.now().isoformat(timespec='minutes').replace(':', '')
            self._internal_logger.info(f"timestamp set to {timestamp}")
            return timestamp

    def _setup_formatters(self, **kwargs) -> (logging.Formatter, Union[ColorizedFormatter, logging.Formatter]):
        formatter = kwargs.get('formatter', logging.Formatter(self._chosen_format))

        if not self._no_stream_color:
            stream_formatter = kwargs.get('stream_formatter', ColorizedFormatter(self._chosen_format))
        else:
            stream_formatter = kwargs.get('stream_formatter', logging.Formatter(self._chosen_format))
        return formatter, stream_formatter

    def _add_filter_to_file_handler(self, handler: logging.FileHandler):
        """
        this is meant to be overwritten in a subclass to allow for filters
        to be added to file handlers without rewriting the entire method.

        Ex: new_filter = MyFilter()
        handler.addFilter(new_filter)
        :param handler:
        :type handler:
        :return:
        :rtype:
        """
        pass

    def _add_filter_to_stream_handler(self, handler: logging.StreamHandler):
        """
        this is meant to be overwritten in a subclass to allow for filters
        to be added to stream handlers without rewriting the entire method.

        Ex: new_filter = MyFilter()
        handler.addFilter(new_filter)

        :param handler:
        :type handler:
        :return:
        :rtype:
        """
        pass

    def make_file_handlers(self):
        """
        This method is used to create file handlers for the logger.
        It sets the logging level for each handler based on the file_logger_levels attribute.
        It also sets the log file location based on the logger level, project name, and timestamp.

        Parameters:
            None

        Returns:
            None

        Raises:
            None
        """
        self._internal_logger.info("creating file handlers for each logger level and log file location")
        for lvl in self.file_logger_levels:
            self.logger.setLevel(lvl)
            level_string = self.__class__.INT_TO_STR_LOGGER_LEVELS[self.logger.level]

            log_path = Path(self.log_location, '{}-{}-{}.log'.format(level_string,
                                                                     self.project_name, self.timestamp))

            # Create a file handler for the logger, and specify the log file location
            file_handler = logging.FileHandler(log_path)
            # Set the logging format for the file handler
            file_handler.setFormatter(self.formatter)
            file_handler.setLevel(self.logger.level)
            # doesn't do anything unless subclassed
            self._add_filter_to_file_handler(file_handler)

            # Add the file handlers to the loggers
            self.logger.addHandler(file_handler)

    def create_stream_handler(self, log_level_to_stream=logging.WARNING, **kwargs):
        """
        Creates and configures a StreamHandler for warning messages to print to the console.

        This method creates a StreamHandler and sets its logging format.
        The StreamHandler is then set to handle only warning level log messages.

        A one-time filter is added to the StreamHandler to ensure that warning messages are only printed to the console once.

        Finally, the StreamHandler is added to the logger.

        Note: This method assumes that `self.logger` and `self.formatter` are already defined.
        """

        if (log_level_to_stream not in self.__class__.INT_TO_STR_LOGGER_LEVELS
                and log_level_to_stream not in self.__class__.STR_TO_INT_LOGGER_LEVELS):
            raise ValueError(f"log_level_to_stream must be one of {list(self.__class__.STR_TO_INT_LOGGER_LEVELS)} or "
                             f"{list(self.__class__.INT_TO_STR_LOGGER_LEVELS)}, "
                             f"not {log_level_to_stream}")

        self._internal_logger.info(
            f"creating StreamHandler() for {logging.getLevelName(log_level_to_stream)} messages to print to console")

        use_one_time_filter = kwargs.get('use_one_time_filter', True)
        self._internal_logger.info(f"use_one_time_filter set to {use_one_time_filter}")

        # Create a stream handler for the logger
        stream_handler = logging.StreamHandler()
        # Set the logging format for the stream handler
        stream_handler.setFormatter(self.stream_formatter)
        stream_handler.setLevel(log_level_to_stream)
        if use_one_time_filter:
            # set the one time filter, so that log_level_to_stream messages will only be printed to the console once.
            one_time_filter = ConsoleOneTimeFilter()
            stream_handler.addFilter(one_time_filter)

        # doesn't do anything unless subclassed
        self._add_filter_to_stream_handler(stream_handler)

        # Add the stream handler to logger
        self.logger.addHandler(stream_handler)
        self._internal_logger.info(
            f"StreamHandler() for {logging.getLevelName(log_level_to_stream)} messages added. "
            f"{logging.getLevelName(log_level_to_stream)}s will be printed to console")
        if use_one_time_filter:
            self._internal_logger.info(f'Added filter {self.logger.handlers[-1].filters[0].name} to StreamHandler()')


if __name__ == '__main__':
    el = EasyLogger(internal_verbose=True,
                    show_warning_logs_in_console=True)
    el.logger.warning("this is an info message", print_msg=True)
