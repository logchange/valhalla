import unittest
from unittest.mock import MagicMock

from valhalla.ci_provider.merge_request_hook import MergeRequestHook
from valhalla.common.get_config import MergeRequestConfig
from valhalla.main import create_merge_request


class MainCreateMergeRequestTest(unittest.TestCase):

    def test_returns_skip_when_config_none(self):
        git_host = MagicMock()
        hook = create_merge_request(git_host, None)
        self.assertIsInstance(hook, MergeRequestHook)
        self.assertIsNone(hook.id)

    def test_returns_skip_when_disabled(self):
        git_host = MagicMock()
        config = MergeRequestConfig(enabled=False, target_branch="", title="t", description="d", reviewers=[])
        hook = create_merge_request(git_host, config)
        self.assertIsInstance(hook, MergeRequestHook)
        self.assertIsNone(hook.id)
        git_host.create_merge_request.assert_not_called()

    def test_returns_provider_hook_when_enabled(self):
        git_host = MagicMock()
        provider_hook = MergeRequestHook(123, lambda c: None)
        git_host.create_merge_request.return_value = provider_hook
        config = MergeRequestConfig(enabled=True, target_branch="main", title="t", description="d", reviewers=[])

        hook = create_merge_request(git_host, config)

        self.assertEqual(hook.id, 123)
        git_host.create_merge_request.assert_called_once_with(config)
