from logging import Logger


class _EasyLoggerCustomLogger(Logger):
    """
    This class defines a custom logger that extends the logging.Logger class.
    It includes methods for logging at different levels such as info, warning, error, debug, and critical.
     Additionally, there is a private static method _print_msg that can be used to print a log message
     based on the provided kwargs. Each logging method in this class calls _print_msg before delegating
     the actual logging to the corresponding method in the parent class.
     The logging methods accept parameters for the log message, additional arguments,
     exception information, stack information, stack level, and extra information.
      Additional keyword arguments can be provided to control printing behavior.
    """
    @staticmethod
    def _print_msg(msg, **kwargs):
        if kwargs.get('print_msg', False):
            print(msg)

    def info(self, msg: object, *args: object, exc_info=None,
             stack_info: bool = False, stacklevel: int = 1,
             extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().info(msg, *args, exc_info=exc_info,
                     stack_info=stack_info, stacklevel=stacklevel,
                     extra=extra)

    def warning(self, msg: object, *args: object, exc_info=None,
                stack_info: bool = False, stacklevel: int = 1,
                extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().warning(msg, *args, exc_info=exc_info,
                        stack_info=stack_info, stacklevel=stacklevel,
                        extra=extra)

    def error(self, msg: object, *args: object, exc_info=None,
              stack_info: bool = False, stacklevel: int = 1,
              extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().error(msg, *args, exc_info=exc_info,
                      stack_info=stack_info, stacklevel=stacklevel,
                      extra=extra)

    def debug(self, msg: object, *args: object, exc_info=None,
              stack_info: bool = False, stacklevel: int = 1,
              extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().debug(msg, *args, exc_info=exc_info,
                      stack_info=stack_info, stacklevel=stacklevel,
                      extra=extra)

    def critical(self, msg: object, *args: object, exc_info=None,
                 stack_info: bool = False, stacklevel: int = 1,
                 extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().critical(msg, *args, exc_info=exc_info,
                         stack_info=stack_info, stacklevel=stacklevel,
                         extra=extra)
