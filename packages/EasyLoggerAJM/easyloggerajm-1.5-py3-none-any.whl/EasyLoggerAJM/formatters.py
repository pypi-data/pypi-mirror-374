from logging import Formatter

NO_COLORIZER = False
try:
    from ColorizerAJM.ColorizerAJM import Colorizer
except (ModuleNotFoundError, ImportError):
    NO_COLORIZER = True


class ColorizedFormatter(Formatter):
    """
    Class that extends logging.Formatter to provide colored output based on log level.
    It includes methods to format log messages and exceptions with colors specified for
     warnings, errors, and other log levels.
    """
    YELLOW = 'YELLOW'
    RED = 'RED'
    GRAY = 'GRAY'

    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        super().__init__(fmt, datefmt, style, validate)
        if NO_COLORIZER:
            return
        else:
            self.colorizer = Colorizer()
        self.warning_color = self.__class__.YELLOW
        self.error_color = self.__class__.RED
        self.other_color = self.__class__.GRAY

    def _get_record_color(self, record):
        if record.levelname == "WARNING":
            return self.warning_color
        elif record.levelname == "ERROR":
            return self.error_color
        else:
            return self.other_color

    def formatMessage(self, record):
        if NO_COLORIZER:
            return super().formatMessage(record)
        else:
            return self.colorizer.colorize(text=super().formatMessage(record),
                                           color=self._get_record_color(record), bold=True)

    def formatException(self, ei):
        if NO_COLORIZER:
            return super().formatException(ei)
        else:
            return self.colorizer.colorize(text=super().formatException(ei),
                                           color=self._get_record_color(ei), bold=True)
