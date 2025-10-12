import unittest
from unittest.mock import patch

from valhalla.ci_provider.gitlab.get_version import get_version_to_release_from_branch_name
from valhalla.version.version_to_release import ReleaseKind


class GetVersionTest(unittest.TestCase):

    @patch('os.environ.get')
    def test_release_branch(self, mock_env_get):
        # given:
        mock_env_get.return_value = 'release-1.0.0'
        release_kinds = [ReleaseKind("valhalla.yml", "", ".")]

        # when:
        result = get_version_to_release_from_branch_name(release_kinds)

        # then:
        self.assertEqual(result.version_number_to_release, '1.0.0')
        self.assertEqual(result.release_kind.filename, "valhalla.yml")
        self.assertEqual(result.get_config_file_path(), "./valhalla.yml")

    @patch('os.environ.get')
    @patch('valhalla.ci_provider.gitlab.get_version.exit')
    def test_non_release_branch(self, mock_exit, mock_env_get):
        # given:
        mock_env_get.return_value = 'feature-branch'
        release_kinds = [ReleaseKind("valhalla.yml", "", ".")]

        # when:
        result = get_version_to_release_from_branch_name(release_kinds)

        # then:
        self.assertIsNone(result)
        mock_exit.assert_called_with(-1)

    @patch('os.environ.get')
    @patch('valhalla.ci_provider.gitlab.get_version.exit')
    def test_no_ci_commit_branch(self, mock_exit, mock_env_get):
        # given:
        mock_env_get.return_value = None
        release_kinds = [ReleaseKind("valhalla.yml", "", ".")]

        # when:
        result = get_version_to_release_from_branch_name(release_kinds)

        # then:
        self.assertIsNone(result)
        mock_exit.assert_called_with(-1)

    @patch('os.environ.get')
    def test_release_hotfix_branch(self, mock_env_get):
        # given:
        mock_env_get.return_value = 'release-hotfix-1.2.3'
        release_kinds = [ReleaseKind("valhalla.yml", "", "."),
                         ReleaseKind("valhalla-hotfix.yml", "-hotfix", ".")]

        # when:
        result = get_version_to_release_from_branch_name(release_kinds)

        # then:
        self.assertEqual(result.version_number_to_release, '1.2.3')
        self.assertEqual(result.release_kind.filename, "valhalla-hotfix.yml")
        self.assertEqual(result.get_config_file_path(), "./valhalla-hotfix.yml")

    @patch('os.environ.get')
    @patch('valhalla.version.version_to_release.exit')
    def test_no_matching_valhalla_branch(self, mock_exit, mock_env_get):
        # given:
        mock_env_get.return_value = 'release-1.2.3'
        release_kinds = [ReleaseKind("valhalla-hotfix.yml", "-hotfix", ".")]

        # when:
        result = get_version_to_release_from_branch_name(release_kinds)

        # then:
        self.assertIsNone(result)
        mock_exit.assert_called_with(-1)
