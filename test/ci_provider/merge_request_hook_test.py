import unittest
from unittest.mock import MagicMock, patch
from valhalla.ci_provider.merge_request_hook import MergeRequestHook

class MergeRequestHookTest(unittest.TestCase):

    def test_add_comment_calls_impl(self):
        # given:
        mock_impl = MagicMock()
        hook = MergeRequestHook(mr_id=1, add_comment_impl=mock_impl)
        comment = "Test comment"

        # when:
        hook.add_comment(comment)

        # then:
        mock_impl.assert_called_once_with(comment)

    @patch("valhalla.ci_provider.merge_request_hook.info")
    def test_skip_logs_info_on_add_comment(self, mock_info):
        # given:
        hook = MergeRequestHook.Skip()
        comment = "Test comment"

        # when:
        hook.add_comment(comment)

        # then:
        mock_info.assert_called_once_with(f"Skipping adding comment: {comment}, merge request has not been created")
        self.assertIsNone(hook.id)

    def test_init_with_only_id(self):
        # given:
        hook = MergeRequestHook(mr_id=123)

        # then:
        self.assertEqual(hook.id, 123)
        self.assertIsNone(hook._add_comment_impl)
