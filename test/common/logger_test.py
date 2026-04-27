import unittest
from unittest.mock import patch, call, MagicMock

from valhalla.common.logger import info, warn, error, init_logger, init_logger_mr_hook


class LoggerTest(unittest.TestCase):

    def tearDown(self):
        from valhalla.common import logger
        logger.MR_HOOK = None
        logger.MR_HOOK_COMMENTS_COUNT = 0
        logger.PENDING_MR_COMMENTS = []

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

    @patch('builtins.print')
    def test_warn_adds_comment_to_mr_when_hook_is_set(self, mock_print):
        # given:
        mr_hook = MagicMock()
        init_logger_mr_hook(mr_hook)
        msg = "warn message"

        # when:
        warn(msg)

        # then:
        mr_hook.add_comment.assert_called_once_with("[WARN] warn message")
        mock_print.assert_called_once_with("[WARN] warn message")

    @patch('builtins.print')
    def test_error_adds_comment_to_mr_when_hook_is_set(self, mock_print):
        # given:
        mr_hook = MagicMock()
        init_logger_mr_hook(mr_hook)
        msg = "error message"

        # when:
        error(msg)

        # then:
        mr_hook.add_comment.assert_called_once_with("[ERROR] error message")
        mock_print.assert_called_once_with("[ERROR] error message")

    @patch('builtins.print')
    def test_multiline_warn_adds_comment_with_proper_newlines(self, mock_print):
        # given:
        mr_hook = MagicMock()
        init_logger_mr_hook(mr_hook)
        msg = "line1\nline2"

        # when:
        warn(msg)

        # then:
        expected_comment = "[WARN] line1  \n[WARN] line2"
        mr_hook.add_comment.assert_called_once_with(expected_comment)

    @patch('builtins.print')
    def test_no_comment_when_hook_not_set(self, mock_print):
        # given:
        init_logger_mr_hook(None)
        mr_hook = MagicMock()  # this one is not registered
        msg = "error message"

        # when:
        error(msg)

        # then:
        mr_hook.add_comment.assert_not_called()
        mock_print.assert_called_once_with("[ERROR] error message")

    @patch('builtins.print')
    @patch('sys.exit')
    def test_exit_after_50_comments(self, mock_exit, mock_print):
        # given:
        from valhalla.common import logger
        mr_hook = MagicMock()
        init_logger_mr_hook(mr_hook)
        logger.MR_HOOK_COMMENTS_COUNT = 0  # reset count for test
        
        # when:
        for i in range(50):
            warn(f"warn {i}")
        
        # then:
        mock_exit.assert_not_called()
        self.assertEqual(mr_hook.add_comment.call_count, 50)
        
        # when:
        warn("the 51st warn")
        
        # then:
        mock_exit.assert_called_once_with(1)
        mock_print.assert_any_call("[ERROR] Too many comments added to Merge Request (limit: 50). Please fix previous warnings.")
        
        # cleanup
        logger.MR_HOOK_COMMENTS_COUNT = 0

    @patch('builtins.print')
    def test_pending_warn_and_error_flushed_when_hook_set_later(self, mock_print):
        # given: errors logged before MR hook is initialized
        warn("early warn")
        error("early error")

        # when: MR hook is initialized later
        mr_hook = MagicMock()
        init_logger_mr_hook(mr_hook)

        # then: pending comments are flushed in order
        mr_hook.add_comment.assert_any_call("[WARN] early warn")
        mr_hook.add_comment.assert_any_call("[ERROR] early error")
        self.assertEqual(mr_hook.add_comment.call_count, 2)

    @patch('builtins.print')
    def test_pending_buffer_cleared_after_flush(self, mock_print):
        # given: an early error and a hook set up
        error("early error")
        mr_hook = MagicMock()
        init_logger_mr_hook(mr_hook)

        # when: a new hook is set up afterwards
        mr_hook.reset_mock()
        another_hook = MagicMock()
        init_logger_mr_hook(another_hook)

        # then: previously flushed comments are not re-flushed
        another_hook.add_comment.assert_not_called()

    @patch('builtins.print')
    def test_info_not_buffered_before_hook(self, mock_print):
        # given: an info log before MR hook is initialized
        info("informational")

        # when: MR hook is initialized later
        mr_hook = MagicMock()
        init_logger_mr_hook(mr_hook)

        # then: info messages are never sent to MR
        mr_hook.add_comment.assert_not_called()

    @patch('builtins.print')
    def test_resolve_author_in_log(self, mock_print):
        # given:
        from valhalla.common import resolver
        resolver.init_str_resolver("token123", "John Doe")
        msg = f"Author is {{AUTHOR}}"

        # when:
        info(msg)

        # then:
        mock_print.assert_called_once_with("[INFO] Author is John Doe")
