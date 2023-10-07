import unittest
from unittest.mock import patch

from valhalla.ci_provider.gitlab.get_version import get_version


class TestGetVersion(unittest.TestCase):

    @patch('os.environ.get')
    def test_release_branch(self, mock_env_get):
        mock_env_get.return_value = 'release-1.0.0'
        result = get_version()
        self.assertEqual(result, '1.0.0')

    @patch('os.environ.get')
    @patch('valhalla.ci_provider.gitlab.get_version.exit')
    def test_non_release_branch(self, mock_exit, mock_env_get):
        mock_env_get.return_value = 'feature-branch'
        result = get_version()
        self.assertIsNone(result)
        mock_exit.assert_called_with(-1)

    @patch('os.environ.get')
    @patch('valhalla.ci_provider.gitlab.get_version.exit')
    def test_no_ci_commit_branch(self, mock_exit, mock_env_get):
        mock_env_get.return_value = None
        result = get_version()
        self.assertIsNone(result)
        mock_exit.assert_called_with(-1)
