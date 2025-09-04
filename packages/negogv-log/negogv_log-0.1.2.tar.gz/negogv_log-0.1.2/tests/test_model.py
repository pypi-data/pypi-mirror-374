import os
import logging
import unittest
from unittest.mock import Mock, patch

from ..negogv_log import (
    cols,
    log_exception,
    MaxLevelFilter,
    CustomFormatter,
    CustomFileFormatter,
    logger as configured_logger,
)

class TestCustomFormatter(unittest.TestCase):
    def test_format_per_level(self):
        """Tests if CustomFormatter returns the correct format string for each level."""
        formatter = CustomFormatter()
        record_debug = logging.LogRecord('name', logging.DEBUG, 'pathname', 1, 'msg', None, None)
        record_info = logging.LogRecord('name', logging.INFO, 'pathname', 1, 'msg', None, None)
        record_warning = logging.LogRecord('name', logging.WARNING, 'pathname', 1, 'msg', None, None)
        record_error = logging.LogRecord('name', logging.ERROR, 'pathname', 1, 'msg', None, None)
        record_critical = logging.LogRecord('name', logging.CRITICAL, 'pathname', 1, 'msg', None, None)


class TestCustomFileFormatter(unittest.TestCase):
    def test_newline_replacement(self):
        """Tests if newlines in the message are correctly replaced."""
        formatter = CustomFileFormatter()
        record = logging.LogRecord('name', logging.INFO, 'pathname', 1, 'first line\nsecond line', None, None)
        
        # The formatter modifies the record in place
        formatter.format(record)
        
        self.assertEqual(record.msg, 'first line\n\t\t| second line')

    def test_no_newline(self):
        """Tests that messages without newlines are unchanged."""
        formatter = CustomFileFormatter()
        original_msg = 'this is a single line'
        record = logging.LogRecord('name', logging.INFO, 'pathname', 1, original_msg, None, None)
        
        formatter.format(record)
        
        self.assertEqual(record.msg, original_msg)


class TestMaxLevelFilter(unittest.TestCase):
    def test_filter(self):
        """Tests if the filter correctly allows and blocks records."""
        max_level_filter = MaxLevelFilter(logging.INFO)
        
        debug_record = logging.LogRecord('name', logging.DEBUG, 'pathname', 1, 'msg', None, None)
        info_record = logging.LogRecord('name', logging.INFO, 'pathname', 1, 'msg', None, None)
        warning_record = logging.LogRecord('name', logging.WARNING, 'pathname', 1, 'msg', None, None)

        self.assertTrue(max_level_filter.filter(debug_record))
        self.assertTrue(max_level_filter.filter(info_record))
        self.assertFalse(max_level_filter.filter(warning_record))


class TestLogException(unittest.TestCase):
    def test_log_exception_format(self):
        """Tests the formatting of the exception log message."""
        try:
            raise ValueError("This is a test error.")
        except ValueError as e:
            log_message = log_exception(e)
            
        self.assertEqual(log_message, "ValueError | Inappropriate argument value (of correct type).")


class TestLoggerConfiguration(unittest.TestCase):
    
    @patch('logging.FileHandler')
    def test_logger_handlers(self, mock_file_handler):
        """
        This is a more complex test that checks if the logger is configured correctly.
        We use mocks to avoid creating actual files.
        """
        # In negogv_log.py, 3 handlers are added.
        # 2 FileHandlers and 1 StreamHandler
        self.assertEqual(len(configured_logger.handlers), 3)

        # Let's check the levels and filters
        error_handler = configured_logger.handlers[0] # file_handler for errors
        app_handler = configured_logger.handlers[1]   # file_low_lvl for app
        
        # error.log handler
        self.assertEqual(error_handler.level, logging.WARNING)
        
        # app.log handler
        self.assertEqual(app_handler.level, logging.DEBUG)
        self.assertEqual(len(app_handler.filters), 1)
        self.assertIsInstance(app_handler.filters[0], MaxLevelFilter)
        self.assertEqual(app_handler.filters[0].max_level, logging.INFO)

        # Let's simulate logging and see if the correct handlers are called
        # We need to mock the handle method of each handler
        error_handler.handle = Mock()
        app_handler.handle = Mock()
        
        # A DEBUG message should only go to the app_handler
        configured_logger.debug("test debug")
        configured_logger.info("info message")
        configured_logger.warning("test warning")
        configured_logger.error("test error")
        configured_logger.critical("test crititcal msg")


if __name__ == '__main__':
    unittest.main()