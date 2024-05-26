import unittest
from unittest.mock import patch

from valhalla.version.release_command import get_version_to_release_from_command
from valhalla.version.version_to_release import ReleaseKind


class ReleaseCommandTest(unittest.TestCase):

    @patch('os.environ.get')
    def test_release_command(self, mock_env_get):
        # given:
        mock_env_get.return_value = 'release-1.0.0'
        release_kinds = [ReleaseKind("valhalla.yml", "", ".")]

        # when:
        result = get_version_to_release_from_command(release_kinds)

        # then:
        self.assertEqual(result.version_number_to_release, '1.0.0')
        self.assertEqual(result.release_kind.filename, "valhalla.yml")
        self.assertEqual(result.get_config_file_path(), "./valhalla.yml")

    @patch('os.environ.get')
    @patch('valhalla.version.release_command.exit')
    def test_wrong_release_command(self, mock_exit, mock_env_get):
        # given:
        mock_env_get.return_value = 'some-value'
        release_kinds = [ReleaseKind("valhalla.yml", "", ".")]

        # when:
        result = get_version_to_release_from_command(release_kinds)

        # then:
        self.assertIsNone(result)
        mock_exit.assert_called_with(-1)

    @patch('os.environ.get')
    def test_no_release_command(self, mock_env_get):
        # given:
        mock_env_get.return_value = None
        release_kinds = [ReleaseKind("valhalla.yml", "", ".")]

        # when:
        result = get_version_to_release_from_command(release_kinds)

        # then:
        self.assertIsNone(result)

    @patch('os.environ.get')
    def test_release_hotfix_command(self, mock_env_get):
        # given:
        mock_env_get.return_value = 'release-hotfix-1.2.3'
        release_kinds = [ReleaseKind("valhalla.yml", "", "."),
                         ReleaseKind("valhalla-hotfix.yml", "-hotfix", ".")]

        # when:
        result = get_version_to_release_from_command(release_kinds)

        # then:
        self.assertEqual(result.version_number_to_release, '1.2.3')
        self.assertEqual(result.release_kind.filename, "valhalla-hotfix.yml")
        self.assertEqual(result.get_config_file_path(), "./valhalla-hotfix.yml")

    @patch('os.environ.get')
    @patch('valhalla.version.version_to_release.exit')
    def test_no_matching_valhalla_command(self, mock_exit, mock_env_get):
        # given:
        mock_env_get.return_value = 'release-1.2.3'
        release_kinds = [ReleaseKind("valhalla-hotfix.yml", "-hotfix", ".")]

        # when:
        result = get_version_to_release_from_command(release_kinds)

        # then:
        self.assertIsNone(result)
        mock_exit.assert_called_with(-1)
