import unittest
from unittest.mock import patch
from EasyLoggerAJM.easy_logger import EasyLogger, _EasyLoggerCustomLogger
from logging import StreamHandler, DEBUG, shutdown
from shutil import rmtree
from pathlib import Path
from io import StringIO


class TestEasyLoggerCustomLogger(unittest.TestCase):
    """
    TestEasyLoggerCustomLogger class represents a unit test case for the EasyLoggerCustomLogger class.
    It provides methods to test logging functionalities for different log levels
    such as info, debug, warning, error, and critical.
    The setUp method initializes the logger and log methods for testing.
    The _iter_subtests method iterates over log methods and asserts the expected behavior of logging messages.
    The test_print_msg_for_all_log_levels and test_not_print_msg_for_all_log_levels methods further test printing
     messages for all log levels when should_print flag is set to True and False respectively.
    """
    def setUp(self):
        self.logger = EasyLogger().UseLogger()  # ._EasyLoggerCustomLogger("TestLogger")
        self.log_methods = {
            'info': self.logger.info,
            'debug': self.logger.debug,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }
        self.should_print = True
        self._initialize_for_log_check()

    @classmethod
    def tearDownClass(cls):
        shutdown()
        TestEasyLoggerCustomLogger.remove_test_dirs()

    @staticmethod
    def remove_test_dirs():
        for x in Path('./').iterdir():
            if x.name.startswith('test_logs') and x.is_dir():
                rmtree(x, ignore_errors=True)
                print(f'{x} removed')

    def _initialize_for_log_check(self):
        self.log_capture_string = StringIO()
        self.log_handler = StreamHandler(self.log_capture_string)
        self.logger.addHandler(self.log_handler)
        self.logger.setLevel(DEBUG)

    def _iter_subtests(self, mock_print):
        log_msg = "Test message"
        for level, method in self.log_methods.items():
            with self.subTest(level=level):
                with patch.object(_EasyLoggerCustomLogger, '_print_msg',
                                  wraps=_EasyLoggerCustomLogger._print_msg) as mock_print_msg:
                    method(log_msg, print_msg=self.should_print)
                    mock_print_msg.assert_called_once_with(log_msg, print_msg=self.should_print)
                    if not self.should_print:
                        mock_print.assert_not_called()
                    else:
                        mock_print.assert_called_once_with(log_msg)

                    # Check if the log message was actually logged
                    self.assertIn(log_msg, self.log_capture_string.getvalue())
                    mock_print.reset_mock()

    @patch('builtins.print')
    def test_print_msg_for_all_log_levels(self, mock_print):
        self.should_print = True
        self._iter_subtests(mock_print)

    @patch('builtins.print')
    def test_not_print_msg_for_all_log_levels(self, mock_print):
        self.should_print = False
        self._iter_subtests(mock_print)


"""class TestEasyLoggerCustomLoggerDEPRECATED(unittest.TestCase):
    def setUp(self):
        self.logger = EasyLogger().UseLogger().logger  # ._EasyLoggerCustomLogger("TestLogger")
        self.log_methods = {
            'info': self.logger.info,
            'debug': self.logger.debug,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }

    @patch('builtins.print')
    def test_internal_print_call_within_print_msg(self, mock_print):
        with patch.object(_EasyLoggerCustomLogger, '_print_msg',
                          wraps=_EasyLoggerCustomLogger._print_msg) as mock_print_msg:
            # Call the info method to execute _print_msg
            self.logger.info("Test message", print_msg=True)

            # Assert that _print_msg was called within the scope
            mock_print_msg.assert_called_once_with("Test message", print_msg=True)
            # Now check that the print function was called within _print_msg
            mock_print.assert_called_once_with("Test message")

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_info_print(self, mock_print):
        self.logger.info("info_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("info_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_warning_print(self, mock_print):
        self.logger.warning("warning_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("warning_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_error_print(self, mock_print):
        self.logger.error("error_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("error_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_debug_print(self, mock_print):
        self.logger.debug("debug_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("debug_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_critical_print(self, mock_print):
        self.logger.critical("critical_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("critical_msg", print_msg=True)"""


if __name__ == "__main__":
    unittest.main()
