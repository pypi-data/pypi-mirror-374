import unittest
import re

from EasyLoggerAJM.easy_logger import EasyLogger
from EasyLoggerAJM.easy_logger import _EasyLoggerCustomLogger
from logging import getLogger, Logger
from test_EasyLoggerCustomLogger import TestEasyLoggerCustomLogger


# noinspection PyStatementEffect
class TestEasyLogger(unittest.TestCase):
    def setUp(self):
        test_attrs = {"project_name": "TestProject", "root_log_location": "./test_logs"}

        self.easy_logger_default = EasyLogger(** test_attrs)
        self.test_dir = self.easy_logger_default._root_log_location
        self.default_logger = self.easy_logger_default.logger

        self.easy_logger_non_default = EasyLogger(** test_attrs,
                                                  logger=getLogger())
        self.non_default_logger = self.easy_logger_non_default.logger

    def test_creation(self):
        self.assertIsInstance(self.easy_logger_default, EasyLogger)

    def test_logger_inst_creation(self):
        self.assertIsInstance(self.default_logger, _EasyLoggerCustomLogger)

    def test_logger_nonCustomLogger_inst_creation(self):
        self.assertNotIsInstance(self.non_default_logger, _EasyLoggerCustomLogger)
        self.assertIsInstance(self.non_default_logger, Logger)

    def test_project_name(self):
        self.assertEqual(self.easy_logger_default.project_name, "TestProject")

    def test_default_format(self):
        self.assertEqual(self.easy_logger_default.DEFAULT_FORMAT, '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

    def test_inner_log_fstructure(self):
        self.assertIsNotNone(self.easy_logger_default.inner_log_fstructure)

    def test_log_location(self):
        posix_with_leading_dir = ('./' + self.easy_logger_default.log_location.as_posix())
        self.assertTrue(re.match(f"{self.test_dir}.*", posix_with_leading_dir))

    def test_useLogger_creation(self):
        logger_cl = EasyLogger(project_name="TestProject2", root_log_location=f"{self.test_dir}2")
        logger = EasyLogger.UseLogger()
        self.assertIsInstance(logger, _EasyLoggerCustomLogger)
        self.assertEqual(logger_cl.project_name, "TestProject2")

        posix_with_leading_dir = ('./' + logger_cl.log_location.as_posix())
        self.assertTrue(re.match(f"{self.test_dir}2.*", posix_with_leading_dir))

    def test_make_file_handlers(self):
        self.easy_logger_default.make_file_handlers()
        self.assertIsNotNone(self.default_logger.handlers)
        self.assertGreaterEqual(len(self.default_logger.handlers), len(self.easy_logger_default.file_logger_levels))

    def test_logger_level_normalization_with_kwargs(self):
        self.easy_logger_default = EasyLogger(project_name="TestProject", root_log_location="./test_logs", file_logger_levels=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
        self.easy_logger_default.make_file_handlers()
        for x in self.easy_logger_default.file_logger_levels:
            self.assertIn(x, [x.level for x in self.default_logger.handlers])
            self.assertIsInstance(x, int)

    def test_is_daily_log_spec(self):
        dls_logger = EasyLogger(project_name="TestProject3",
                                root_log_location=f"{self.test_dir}3",
                                is_daily_log_spec=True)
        dls_logger.make_file_handlers()
        self.assertEqual(dls_logger.inner_log_fstructure.split('/')[0], dls_logger.DAILY_LOG_SPEC_FORMAT)

    def test_given_dictionary_when_getting_log_spec_then_return_value(self):
        self.easy_logger_default._log_spec = {'name': 'minute'}
        self.assertEqual(self.easy_logger_default.log_spec, self.easy_logger_default.LOG_SPECS['minute'])

    def test_given_incorrect_key_dictionary_when_getting_log_spec_then_raise_exception(self):
        self.easy_logger_default._log_spec = {'wrong_key': 'minute'}
        with self.assertRaises(KeyError):
            self.easy_logger_default.log_spec

    def test_given_string_when_getting_log_spec_then_return_value(self):
        self.easy_logger_default._log_spec = 'minute'
        self.assertEqual(self.easy_logger_default.log_spec, self.easy_logger_default.LOG_SPECS['minute'])

    def test_given_wrong_string_when_getting_log_spec_then_raise_exception(self):
        self.easy_logger_default._log_spec = 'wrong_string'
        with self.assertRaises(AttributeError):
            self.easy_logger_default.log_spec

    def test_given_wrong_case_string_when_getting_log_spec_then_make_lowercase(self):
        self.easy_logger_default._log_spec = 'Minute'
        self.assertTrue(self.easy_logger_default.log_spec['name'].islower())

    def test_given_wrong_case_string_in_dict_when_getting_log_spec_then_make_lowercase(self):
        self.easy_logger_default._log_spec = {'name': 'Minute'}
        self.assertTrue(self.easy_logger_default.log_spec['name'].islower())

    def test_given_none_when_getting_log_spec_then_return_default_value(self):
        self.easy_logger_default._log_spec = None
        self.assertEqual(self.easy_logger_default.log_spec, self.easy_logger_default.LOG_SPECS['minute'])


if __name__ == "__main__":
    unittest.main()
    TestEasyLoggerCustomLogger.tearDownClass()

