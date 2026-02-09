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
        self.assertEqual(hook.id, 1)
        self.assertIsNotNone(hook._add_comment_impl)

    @patch('valhalla.ci_provider.merge_request_hook.resolve')
    def test_add_comment_calls_resolve(self, mock_resolve):
        # given:
        mock_impl = MagicMock()
        hook = MergeRequestHook(mr_id=1, add_comment_impl=mock_impl)
        comment = "Comment with {VAR}"
        mock_resolve.return_value = "Comment with VALUE"

        # when:
        hook.add_comment(comment)

        # then:
        mock_resolve.assert_called_once_with(comment)
        mock_impl.assert_called_once_with("Comment with VALUE")

    def test_skip_add_comment(self):
        # given:
        hook = MergeRequestHook.Skip()
        comment = "Test comment"

        # when:
        hook.add_comment(comment)

        # then:
        self.assertIsNone(hook.id)
        self.assertIsNone(hook._add_comment_impl)


    def test_init_with_only_id(self):
        # given:
        hook = MergeRequestHook(mr_id=123)

        # then:
        self.assertEqual(hook.id, 123)
        self.assertIsNone(hook._add_comment_impl)
