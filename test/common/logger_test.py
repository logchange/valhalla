import unittest
from unittest.mock import patch, call
from valhalla.common.logger import info, warn, error, init_logger

class LoggerTest(unittest.TestCase):

    @patch('builtins.print')
    def test_info(self, mock_print):
        # given:
        msg = "info message"
        
        # when:
        info(msg)
        
        # then:
        mock_print.assert_called_once_with("[INFO] info message")

    @patch('builtins.print')
    def test_warn(self, mock_print):
        # given:
        msg = "warn message"
        
        # when:
        warn(msg)
        
        # then:
        mock_print.assert_called_once_with("[WARN] warn message")

    @patch('builtins.print')
    def test_error(self, mock_print):
        # given:
        msg = "error message"
        
        # when:
        error(msg)
        
        # then:
        mock_print.assert_called_once_with("[ERROR] error message")

    @patch('builtins.print')
    def test_logger_hides_token(self, mock_print):
        # given:
        token = "secret_token_123"
        init_logger(token)
        msg = f"User token is {token}"
        
        # when:
        info(msg)
        
        # then:
        expected_msg = f"User token is {'*' * len(token)}"
        mock_print.assert_called_once_with(f"[INFO] {expected_msg}")

    @patch('builtins.print')
    def test_multiline_log(self, mock_print):
        # given:
        msg = "line1\nline2"
        
        # when:
        info(msg)
        
        # then:
        calls = [call("[INFO] line1"), call("[INFO] line2")]
        mock_print.assert_has_calls(calls)
