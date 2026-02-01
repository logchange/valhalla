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
    def test_create_merge_request_with_reviewers(self, mock_warn, mock_info, mock_resolve, mock_get_project_id,
                                                 mock_get_gitlab_client):
        with patch.dict('os.environ', {'CI_COMMIT_BRANCH': 'feature-branch'}):
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

            # mock users for reviewers
            mock_user = MagicMock()
            mock_user.id = 55
            mock_gitlab_client.users.list.return_value = [mock_user]

            merge_request = GitLabValhallaMergeRequest()

            config = MergeRequestConfig(
                enabled=True,
                target_branch="develop",
                title="Test MR",
                description="Desc",
                reviewers=["user1"]
            )

            # when:
            merge_request.create(config)

            # then:
            mock_gitlab_client.users.list.assert_called_once_with(username="user1")
            mock_project.mergerequests.create.assert_called_once()
            args = mock_project.mergerequests.create.call_args[0][0]
            self.assertEqual(args['reviewer_ids'], [55])
            mock_info.assert_any_call("Adding reviewer: user1 with id 55")

    @patch("valhalla.ci_provider.gitlab.merge_request.get_gitlab_client")
    @patch("valhalla.ci_provider.gitlab.merge_request.get_project_id")
    @patch("valhalla.ci_provider.gitlab.merge_request.resolve")
    @patch("valhalla.ci_provider.gitlab.merge_request.info")
    @patch("valhalla.ci_provider.gitlab.merge_request.warn")
    def test_create_merge_request_with_missing_reviewer(self, mock_warn, mock_info, mock_resolve, mock_get_project_id,
                                                        mock_get_gitlab_client):
        with patch.dict('os.environ', {'CI_COMMIT_BRANCH': 'feature-branch'}):
            # given:
            mock_get_project_id.return_value = "123"
            mock_resolve.side_effect = lambda x: x
            mock_gitlab_client = MagicMock()
            mock_project = MagicMock()
            mock_project.mergerequests.create.return_value = MagicMock()
            mock_gitlab_client.projects.get.return_value = mock_project
            mock_get_gitlab_client.return_value = mock_gitlab_client

            # mock user not found
            mock_gitlab_client.users.list.return_value = []

            merge_request = GitLabValhallaMergeRequest()
            config = MergeRequestConfig(enabled=True, target_branch="main", title="T", description="D", reviewers=["ghost"])

            # when:
            merge_request.create(config)

            # then:
            mock_warn.assert_any_call("Could not find username: ghost")
            args = mock_project.mergerequests.create.call_args[0][0]
            self.assertEqual(args['reviewer_ids'], [])

    @patch("valhalla.ci_provider.gitlab.merge_request.get_gitlab_client")
    @patch("valhalla.ci_provider.gitlab.merge_request.get_project_id")
    @patch("valhalla.ci_provider.gitlab.merge_request.resolve")
    @patch("valhalla.ci_provider.gitlab.merge_request.info")
    @patch("valhalla.ci_provider.gitlab.merge_request.warn")
    def test_create_merge_request_default_target_branch(self, mock_warn, mock_info, mock_resolve, mock_get_project_id,
                                                       mock_get_gitlab_client):
        with patch.dict('os.environ', {'CI_COMMIT_BRANCH': 'feature-branch', 'CI_DEFAULT_BRANCH': 'main'}):
            # given:
            mock_get_project_id.return_value = "123"
            mock_resolve.side_effect = lambda x: x
            mock_gitlab_client = MagicMock()
            mock_project = MagicMock()
            mock_project.mergerequests.create.return_value = MagicMock()
            mock_gitlab_client.projects.get.return_value = mock_project
            mock_get_gitlab_client.return_value = mock_gitlab_client

            merge_request = GitLabValhallaMergeRequest()
            config = MergeRequestConfig(enabled=True, target_branch="", title="T", description="", reviewers=[])

            # when:
            merge_request.create(config)

            # then:
            mock_info.assert_any_call("target_branch not set, using default instead")
            args = mock_project.mergerequests.create.call_args[0][0]
            self.assertEqual(args['target_branch'], 'main')
            mock_info.assert_any_call("merge_request.description not specified, using default")

    @patch("valhalla.ci_provider.gitlab.merge_request.get_gitlab_client")
    @patch("valhalla.ci_provider.gitlab.merge_request.get_project_id")
    @patch("valhalla.ci_provider.gitlab.merge_request.resolve")
    @patch("valhalla.ci_provider.gitlab.merge_request.info")
    @patch("valhalla.ci_provider.gitlab.merge_request.warn")
    def test_add_comment_to_merge_request(self, mock_warn, mock_info, mock_resolve, mock_get_project_id,
                                          mock_get_gitlab_client):
        with patch.dict('os.environ', {'CI_COMMIT_BRANCH': 'feature-branch'}):
            # given:
            mock_get_project_id.return_value = "123"
            mock_resolve.side_effect = lambda x: x
            mock_gitlab_client = MagicMock()
            mock_project = MagicMock()
            mock_mr_instance = MagicMock()
            mock_mr_instance.iid = 101
            mock_project.mergerequests.create.return_value = mock_mr_instance
            mock_gitlab_client.projects.get.return_value = mock_project
            mock_get_gitlab_client.return_value = mock_gitlab_client

            # Setup for get and note creation
            mock_mr_obj = MagicMock()
            mock_project.mergerequests.get.return_value = mock_mr_obj

            merge_request = GitLabValhallaMergeRequest()
            config = MergeRequestConfig(enabled=True, target_branch="main", title="T", description="D", reviewers=[])

            # when:
            hook = merge_request.create(config)
            hook.add_comment("Test comment")

            # then:
            mock_project.mergerequests.get.assert_called_once_with(101, iid=True)
            mock_mr_obj.notes.create.assert_called_once_with({'body': "Test comment"})

    @patch("valhalla.ci_provider.gitlab.merge_request.get_gitlab_client")
    @patch("valhalla.ci_provider.gitlab.merge_request.get_project_id")
    @patch("valhalla.ci_provider.gitlab.merge_request.resolve")
    @patch("valhalla.ci_provider.gitlab.merge_request.info")
    @patch("valhalla.ci_provider.gitlab.merge_request.warn")
    def test_add_comment_exception(self, mock_warn, mock_info, mock_resolve, mock_get_project_id,
                                   mock_get_gitlab_client):
        with patch.dict('os.environ', {'CI_COMMIT_BRANCH': 'feature-branch'}):
            # given:
            mock_get_project_id.return_value = "123"
            mock_resolve.side_effect = lambda x: x
            mock_gitlab_client = MagicMock()
            mock_project = MagicMock()
            mock_mr_instance = MagicMock()
            mock_mr_instance.iid = 101
            mock_project.mergerequests.create.return_value = mock_mr_instance
            mock_gitlab_client.projects.get.return_value = mock_project
            mock_get_gitlab_client.return_value = mock_gitlab_client

            # Setup for failure
            mock_project.mergerequests.get.side_effect = Exception("GitLab error")

            merge_request = GitLabValhallaMergeRequest()
            config = MergeRequestConfig(enabled=True, target_branch="main", title="T", description="D", reviewers=[])

            # when:
            hook = merge_request.create(config)
            hook.add_comment("Test comment")

            # then:
            mock_warn.assert_any_call("Could not add comment to merge request because: GitLab error")
