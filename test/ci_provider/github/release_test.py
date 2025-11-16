import unittest
from unittest.mock import patch, MagicMock

from valhalla.ci_provider.github.release import GitHubValhallaRelease
from valhalla.release.description import Description
from valhalla.common.get_config import ReleaseDescriptionConfig


class GitHubReleaseTest(unittest.TestCase):

    @patch("valhalla.ci_provider.github.release.GitHubClient")
    @patch("valhalla.ci_provider.github.release.info")
    @patch("valhalla.ci_provider.github.release.warn")
    def test_create_release_success(self, mock_warn, mock_info, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'main'}):
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            release_response = MagicMock()
            release_response.status_code = 201
            release_response.json.return_value = {"html_url": "https://github.com/owner/repo/releases/tag/v1.0.0"}

            mock_client.post.return_value = release_response
            mock_client_cls.return_value = mock_client

            desc = Description(ReleaseDescriptionConfig(from_command="echo hello"))
            # Patch Description.get to avoid running shell
            with patch.object(Description, 'get', return_value='hello'):
                release = GitHubValhallaRelease()

                # when
                release.create(description=desc, milestones=[], release_name="Release 1.0.0", tag_name="v1.0.0", assets=MagicMock())

                # then
                expected_payload = {
                    'tag_name': 'v1.0.0',
                    'name': 'Release 1.0.0',
                    'body': 'hello',
                    'target_commitish': 'main',
                    'make_latest': 'true'
                }
                mock_client.post.assert_called_with("https://api.github.com/repos/owner/repo/releases", json=expected_payload)
                mock_info.assert_any_call("Created release: https://github.com/owner/repo/releases/tag/v1.0.0")
                mock_warn.assert_not_called()

    @patch("valhalla.ci_provider.github.release.GitHubClient")
    @patch("valhalla.ci_provider.github.release.warn")
    def test_create_release_failure_warns(self, mock_warn, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'main'}):
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            release_response = MagicMock()
            release_response.status_code = 400
            release_response.text = "bad request"

            mock_client.post.return_value = release_response
            mock_client_cls.return_value = mock_client

            desc = Description(ReleaseDescriptionConfig(from_command="echo hello"))
            with patch.object(Description, 'get', return_value='hello'):
                release = GitHubValhallaRelease()

                # when
                release.create(description=desc, milestones=[], release_name="Release 1.0.0", tag_name="v1.0.0", assets=MagicMock())

                # then
                mock_warn.assert_any_call("Failed to create release: 400 bad request")
