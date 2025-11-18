import unittest
from unittest.mock import MagicMock, patch, mock_open

from valhalla.ci_provider.github.release import GitHubValhallaRelease
from valhalla.common.get_config import ReleaseDescriptionConfig
from valhalla.release.description import Description


class GitHubReleaseUploadTest(unittest.TestCase):

    @patch("valhalla.ci_provider.github.release.info")
    @patch("valhalla.ci_provider.github.release.warn")
    @patch("valhalla.ci_provider.github.release.GitHubClient")
    def test_uploads_assets_on_successful_release(self, mock_client_cls, mock_warn, mock_info):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'main'}):
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            # Response for creating a release
            release_response = MagicMock()
            release_response.status_code = 201
            release_response.json.return_value = {
                "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
                "upload_url": "https://uploads.github.com/repos/owner/repo/releases/1/assets{?name,label}"
            }
            mock_client.post.return_value = release_response

            # Mock session.post used for uploading assets
            mock_session_post = MagicMock()
            # Simulate 201 Created for both uploads
            mock_session_post.side_effect = [
                MagicMock(status_code=201),
                MagicMock(status_code=201)
            ]
            mock_client.session.post = mock_session_post

            mock_client_cls.return_value = mock_client

            # Assets mock
            assets_mock = MagicMock()
            assets_mock.get_files.return_value = ["build/a.zip", "dist/app.tar.gz"]

            # Ensure deterministic content-type to assert headers
            with patch("valhalla.ci_provider.github.release.Assets.guess_mime", side_effect=[
                "application/zip", "application/gzip"
            ]):
                # Patch open so no real filesystem is used
                m = mock_open(read_data=b"data")
                # The code opens files in binary mode; mock needs to return a file-like object
                with patch("builtins.open", m):
                    desc = Description(ReleaseDescriptionConfig(from_command="echo hello"))
                    with patch.object(Description, 'get', return_value='hello'):
                        release = GitHubValhallaRelease()
                        # when
                        release.create(description=desc, milestones=[], release_name="Release 1.0.0",
                                       tag_name="v1.0.0", assets=assets_mock)

            # then
            # It should call upload endpoint twice with appropriate params and headers
            upload_base = "https://uploads.github.com/repos/owner/repo/releases/1/assets"
            expected_calls = [
                unittest.mock.call(upload_base, params={'name': 'a.zip'}, headers={'Content-Type': 'application/zip'}, data=unittest.mock.ANY),
                unittest.mock.call(upload_base, params={'name': 'app.tar.gz'}, headers={'Content-Type': 'application/gzip'}, data=unittest.mock.ANY)
            ]
            self.assertEqual(mock_session_post.call_args_list, expected_calls)
            mock_warn.assert_not_called()

    @patch("valhalla.ci_provider.github.release.info")
    @patch("valhalla.ci_provider.github.release.GitHubClient")
    def test_no_files_skips_upload(self, mock_client_cls, mock_info):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'main'}):
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            # Response for creating a release without using session.post later
            release_response = MagicMock()
            release_response.status_code = 201
            release_response.json.return_value = {
                "html_url": "https://github.com/owner/repo/releases/tag/v1.0.0",
                "upload_url": "https://uploads.github.com/repos/owner/repo/releases/1/assets{?name,label}"
            }
            mock_client.post.return_value = release_response

            mock_client_cls.return_value = mock_client

            assets_mock = MagicMock()
            assets_mock.get_files.return_value = []

            desc = Description(ReleaseDescriptionConfig(from_command="echo hello"))
            with patch.object(Description, 'get', return_value='hello'):
                release = GitHubValhallaRelease()
                # when
                release.create(description=desc, milestones=[], release_name="Release 1.0.0",
                               tag_name="v1.0.0", assets=assets_mock)

        # then
        # Should log info about no files and never call upload session.post
        mock_info.assert_any_call("No files to upload")
        self.assertFalse(mock_client.session.post.called)


if __name__ == '__main__':
    unittest.main()
