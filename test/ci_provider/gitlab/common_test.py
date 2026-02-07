import unittest
from unittest.mock import patch

from valhalla.ci_provider.gitlab.common import (
    get_gitlab_client,
    get_project_id,
    get_author,
)


class GitLabCommonTest(unittest.TestCase):

    @patch("valhalla.ci_provider.gitlab.common.get_valhalla_token")
    @patch("gitlab.Gitlab")
    @patch("os.getenv")
    def test_get_gitlab_client(self, mock_getenv, mock_gitlab_cls, mock_get_token):
        # given:
        mock_get_token.return_value = "secrettoken"
        mock_getenv.side_effect = lambda k, d=None: {
            "CI_SERVER_PROTOCOL": "https",
            "CI_SERVER_HOST": "gitlab.com",
            "CI_SERVER_PORT": "443"
        }.get(k, d)
        
        # when:
        client = get_gitlab_client()
        
        # then:
        mock_gitlab_cls.assert_called_once_with("https://gitlab.com:443", oauth_token="secrettoken")
        self.assertEqual(client, mock_gitlab_cls.return_value)

    @patch("os.getenv")
    def test_get_project_id(self, mock_getenv):
        # given:
        mock_getenv.side_effect = lambda k, d=None: {
            "CI_PROJECT_ID": "12345"
        }.get(k, d)
        
        # when:
        project_id = get_project_id()
        
        # then:
        self.assertEqual(project_id, "12345")

    @patch("os.getenv")
    def test_get_author(self, mock_getenv):
        # given:
        mock_getenv.side_effect = lambda k, d=None: {
            "GITLAB_USER_LOGIN": "gitlab_user"
        }.get(k, d)
        
        # when:
        author = get_author()
        
        # then:
        self.assertEqual(author, "gitlab_user")
