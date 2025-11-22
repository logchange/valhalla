import unittest
from unittest.mock import patch, MagicMock

from valhalla.ci_provider.gitlab.merge_request import GitLabValhallaMergeRequest
from valhalla.common.get_config import MergeRequestConfig


class TestGitLabValhallaMergeRequest(unittest.TestCase):

    @patch("valhalla.ci_provider.gitlab.merge_request.get_gitlab_client")
    @patch("valhalla.ci_provider.gitlab.merge_request.get_project_id")
    @patch("valhalla.ci_provider.gitlab.merge_request.resolve")
    @patch("valhalla.ci_provider.gitlab.merge_request.info")
    @patch("valhalla.ci_provider.gitlab.merge_request.warn")
    def test_create_merge_request(self, mock_warn, mock_info, mock_resolve, mock_get_project_id,
                                  mock_get_gitlab_client):
        with patch.dict('os.environ', {'CI_COMMIT_BRANCH': 'feature-branch', 'CI_DEFAULT_BRANCH': 'main'}):
            # given:
            mock_get_project_id.return_value = "123"
            mock_resolve.side_effect = lambda x: x
            mock_gitlab_client = MagicMock()
            mock_project = MagicMock()
            mock_merge_request = MagicMock()
            mock_project.mergerequests.create.return_value = mock_merge_request
            mock_merge_request.web_url = "https://example.com/mr/1"
            mock_gitlab_client.projects.get.return_value = mock_project
            mock_get_gitlab_client.return_value = mock_gitlab_client

            merge_request = GitLabValhallaMergeRequest()

            config = MergeRequestConfig(
                enabled=True,
                target_branch="develop",
                title="Test MR",
                description="Created by Valhalla!",
                reviewers=[]
            )

            # when:
            merge_request.create(config)

            # then:
            mock_info.assert_any_call("Creating merge request from feature-branch to develop")
            mock_project.mergerequests.create.assert_called_once_with({
                'source_branch': 'feature-branch',
                'target_branch': 'develop',
                'title': 'Test MR',
                'description': "Created by Valhalla!",
                'remove_source_branch': True,
                'reviewer_ids': []
            })
            mock_warn.assert_called_with("Reviewers list is None or empty")
            mock_info.assert_any_call("Created merge request: https://example.com/mr/1")
