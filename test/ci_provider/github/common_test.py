import unittest
from unittest.mock import patch, MagicMock

from valhalla.ci_provider.github.common import (
    get_repository_slug,
    get_author,
    get_api_url,
    get_default_branch_fallback,
    GitHubClient,
)


class GitHubCommonTest(unittest.TestCase):

    @patch("os.getenv")
    def test_get_repository_slug(self, mock_getenv):
        # given:
        mock_getenv.side_effect = lambda k, d=None: {
            "GITHUB_REPOSITORY": "owner/repo"
        }.get(k, d)

        # when:
        repo = get_repository_slug()

        # then:
        self.assertEqual(repo, "owner/repo")

    @patch("os.getenv")
    def test_get_author(self, mock_getenv):
        # given:
        mock_getenv.side_effect = lambda k, d=None: {
            "GITHUB_ACTOR": "octocat"
        }.get(k, d)

        # when:
        author = get_author()

        # then:
        self.assertEqual(author, "octocat")

    @patch("os.getenv")
    def test_get_api_url_default_and_custom(self, mock_getenv):
        # default
        mock_getenv.side_effect = lambda k, d=None: {}.get(k, d)
        self.assertEqual(get_api_url(), "https://api.github.com")

        # custom
        mock_getenv.side_effect = lambda k, d=None: {
            "GITHUB_API_URL": "https://ghe.example.com/api/v3"
        }.get(k, d)
        self.assertEqual(get_api_url(), "https://ghe.example.com/api/v3")

    @patch("os.getenv")
    def test_get_default_branch_fallback_default_and_custom(self, mock_getenv):
        # default
        mock_getenv.side_effect = lambda k, d=None: {}.get(k, d)
        self.assertEqual(get_default_branch_fallback(), "main")

        # custom
        mock_getenv.side_effect = lambda k, d=None: {
            "GITHUB_DEFAULT_BRANCH": "develop"
        }.get(k, d)
        self.assertEqual(get_default_branch_fallback(), "develop")

    @patch("valhalla.ci_provider.github.common.get_valhalla_token")
    @patch("requests.Session")
    @patch("os.getenv")
    def test_github_client_headers_with_token(self, mock_getenv, mock_session_cls, mock_get_token):
        # given:
        mock_get_token.return_value = "secrettoken"
        mock_getenv.side_effect = lambda k, d=None: {
            "GITHUB_API_URL": "https://api.github.com",
            "GITHUB_REPOSITORY": "owner/repo",
        }.get(k, d)
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        # when:
        client = GitHubClient()

        # then:
        self.assertEqual(client.api_url, "https://api.github.com")
        self.assertEqual(client.repo, "owner/repo")
        mock_session.headers.update.assert_called_once()
        called_headers = mock_session.headers.update.call_args[0][0]
        self.assertEqual(called_headers["Authorization"], "Bearer secrettoken")
        self.assertEqual(called_headers["Accept"], "application/vnd.github+json")

    @patch("valhalla.ci_provider.github.common.get_valhalla_token")
    @patch("os.getenv")
    def test_github_client_raises_without_token(self, mock_getenv, mock_get_token):
        # given: simulate empty token returned
        mock_get_token.return_value = ""
        mock_getenv.side_effect = lambda k, d=None: {
            "GITHUB_API_URL": "https://api.github.com",
            "GITHUB_REPOSITORY": "owner/repo",
        }.get(k, d)

        # when / then:
        with self.assertRaises(Exception):
            GitHubClient()
