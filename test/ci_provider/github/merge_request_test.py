import unittest
from unittest.mock import patch, MagicMock

from valhalla.ci_provider.github.merge_request import GitHubValhallaPullRequest
from valhalla.common.get_config import MergeRequestConfig


class GitHubMergeRequestTest(unittest.TestCase):

    @patch("valhalla.ci_provider.github.merge_request.GitHubClient")
    @patch("valhalla.ci_provider.github.merge_request.resolve")
    @patch("valhalla.ci_provider.github.merge_request.info")
    @patch("valhalla.ci_provider.github.merge_request.warn")
    def test_create_pr_with_reviewers(self, mock_warn, mock_info, mock_resolve, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'feature-branch'}):
            mock_resolve.side_effect = lambda x: x
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            # simulate successful PR creation response
            pr_response = MagicMock()
            pr_response.status_code = 201
            pr_response.json.return_value = {"html_url": "https://github.com/owner/repo/pull/1", "number": 1}
            # response for reviewers request
            reviewers_response = MagicMock()
            reviewers_response.status_code = 201

            def post_side_effect(url, json=None):
                if url.endswith("/pulls"):
                    return pr_response
                if url.endswith("/pulls/1/requested_reviewers"):
                    return reviewers_response
                raise AssertionError("Unexpected URL " + url)

            mock_client.post.side_effect = post_side_effect
            mock_client_cls.return_value = mock_client

            pr = GitHubValhallaPullRequest()
            config = MergeRequestConfig(enabled=True, target_branch="develop", title="My PR", description="desc", reviewers=["r1", "r2"])

            # when
            pr.create(config)

            # then
            expected_payload = {
                'title': 'My PR',
                'head': 'feature-branch',
                'base': 'develop',
                'body': 'desc'
            }
            mock_client.post.assert_any_call("https://api.github.com/repos/owner/repo/pulls", json=expected_payload)
            mock_info.assert_any_call("Created pull request: https://github.com/owner/repo/pull/1")
            mock_info.assert_any_call("Requested reviewers: r1, r2")
            mock_warn.assert_not_called()

    @patch("valhalla.ci_provider.github.merge_request.GitHubClient")
    @patch("valhalla.ci_provider.github.merge_request.resolve")
    @patch("valhalla.ci_provider.github.merge_request.info")
    @patch("valhalla.ci_provider.github.merge_request.warn")
    def test_create_pr_with_default_description_and_fallback_target(self, mock_warn, mock_info, mock_resolve, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'feature-branch', 'GITHUB_DEFAULT_BRANCH': 'main'}):
            mock_resolve.side_effect = lambda x: x
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            pr_response = MagicMock()
            pr_response.status_code = 201
            pr_response.json.return_value = {"html_url": "https://github.com/owner/repo/pull/2", "number": 2}

            reviewers_response = MagicMock()
            reviewers_response.status_code = 201

            mock_client.post.side_effect = [pr_response, reviewers_response]
            mock_client_cls.return_value = mock_client

            pr = GitHubValhallaPullRequest()
            config = MergeRequestConfig(enabled=True, target_branch="", title="Title", description="Created by Valhalla!", reviewers=[])

            # when
            pr.create(config)

            # then
            # default description is used and no reviewers added (empty list)
            expected_payload = {
                'title': 'Title',
                'head': 'feature-branch',
                'base': 'main',
                'body': "Created by Valhalla!"
            }
            mock_client.post.assert_any_call("https://api.github.com/repos/owner/repo/pulls", json=expected_payload)
            # Only one post call (to create PR), because reviewers list is empty
            self.assertEqual(mock_client.post.call_count, 1)
            mock_warn.assert_not_called()
            mock_info.assert_any_call("target_branch not set, using default instead")

    @patch("valhalla.ci_provider.github.merge_request.GitHubClient")
    @patch("valhalla.ci_provider.github.merge_request.resolve")
    @patch("valhalla.ci_provider.github.merge_request.info")
    @patch("valhalla.ci_provider.github.merge_request.warn")
    def test_create_pr_failure_warns(self, mock_warn, mock_info, mock_resolve, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'feature-branch'}):
            mock_resolve.side_effect = lambda x: x
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            pr_response = MagicMock()
            pr_response.status_code = 422
            pr_response.text = "validation failed"
            mock_client.post.return_value = pr_response
            mock_client_cls.return_value = mock_client

            pr = GitHubValhallaPullRequest()
            config = MergeRequestConfig(enabled=True, target_branch="develop", title="Title", description="", reviewers=["u1"]) 

            # when
            pr.create(config)

            # then
            mock_warn.assert_any_call("Failed to create pull request: 422 validation failed")

    @patch("valhalla.ci_provider.github.merge_request.GitHubClient")
    @patch("valhalla.ci_provider.github.merge_request.resolve")
    @patch("valhalla.ci_provider.github.merge_request.info")
    @patch("valhalla.ci_provider.github.merge_request.warn")
    def test_add_comment_to_pull_request(self, mock_warn, mock_info, mock_resolve, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'feature-branch'}):
            mock_resolve.side_effect = lambda x: x
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            pr_response = MagicMock()
            pr_response.status_code = 201
            pr_response.json.return_value = {"html_url": "url", "number": 123}

            mock_client.post.return_value = pr_response
            mock_client_cls.return_value = mock_client

            pr = GitHubValhallaPullRequest()
            config = MergeRequestConfig(enabled=True, target_branch="main", title="T", description="D", reviewers=[])

            # when
            hook = pr.create(config)
            hook.add_comment("My comment")

            # then
            expected_comment_url = "https://api.github.com/repos/owner/repo/issues/123/comments"
            mock_client.post.assert_any_call(expected_comment_url, json={"body": "My comment"})
            mock_info.assert_any_call(f"Adding comment to pull request: {expected_comment_url}")

    @patch("valhalla.ci_provider.github.merge_request.GitHubClient")
    @patch("valhalla.ci_provider.github.merge_request.resolve")
    @patch("valhalla.ci_provider.github.merge_request.info")
    @patch("valhalla.ci_provider.github.merge_request.warn")
    def test_add_comment_exception(self, mock_warn, mock_info, mock_resolve, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'feature-branch'}):
            mock_resolve.side_effect = lambda x: x
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            pr_response = MagicMock()
            pr_response.status_code = 201
            pr_response.json.return_value = {"html_url": "url", "number": 123}

            # First call (create PR) succeeds, second call (add comment) raises exception
            mock_client.post.side_effect = [pr_response, Exception("Network error")]
            mock_client_cls.return_value = mock_client

            pr = GitHubValhallaPullRequest()
            config = MergeRequestConfig(enabled=True, target_branch="main", title="T", description="D", reviewers=[])

            # when
            hook = pr.create(config)
            hook.add_comment("My comment")

            # then
            mock_warn.assert_any_call("Could not add comment to pull request because: Network error")

    @patch("valhalla.ci_provider.github.merge_request.GitHubClient")
    @patch("valhalla.ci_provider.github.merge_request.resolve")
    @patch("valhalla.ci_provider.github.merge_request.info")
    @patch("valhalla.ci_provider.github.merge_request.warn")
    def test_request_reviewers_failure(self, mock_warn, mock_info, mock_resolve, mock_client_cls):
        # given
        with patch.dict('os.environ', {'GITHUB_REF_NAME': 'feature-branch'}):
            mock_resolve.side_effect = lambda x: x
            mock_client = MagicMock()
            mock_client.api_url = "https://api.github.com"
            mock_client.repo = "owner/repo"

            pr_response = MagicMock()
            pr_response.status_code = 201
            pr_response.json.return_value = {"html_url": "url", "number": 123}

            rev_response = MagicMock()
            rev_response.status_code = 404
            rev_response.text = "Not found"

            mock_client.post.side_effect = [pr_response, rev_response]
            mock_client_cls.return_value = mock_client

            pr = GitHubValhallaPullRequest()
            config = MergeRequestConfig(enabled=True, target_branch="main", title="T", description="D", reviewers=["user1"])

            # when
            pr.create(config)

            # then
            mock_warn.assert_any_call("Could not add reviewers: 404 Not found")
