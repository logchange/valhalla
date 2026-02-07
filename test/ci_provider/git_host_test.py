import unittest
from unittest.mock import patch, MagicMock
import os
from valhalla.ci_provider.git_host import GitHost, Release, MergeRequest, VersionToReleaseProvider


class GitHostTest(unittest.TestCase):

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    def test_should_detect_github_via_github_actions(self):
        # given: os.environ has GITHUB_ACTIONS
        
        # when:
        git_host = GitHost()
        
        # then:
        self.assertTrue(git_host.is_github())
        self.assertFalse(git_host.is_gitlab())

    @patch.dict(os.environ, {"GITHUB_REPOSITORY": "user/repo"}, clear=True)
    def test_should_detect_github_via_github_repository(self):
        # given: os.environ has GITHUB_REPOSITORY
        
        # when:
        git_host = GitHost()
        
        # then:
        self.assertTrue(git_host.is_github())

    @patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True)
    def test_should_detect_gitlab_via_gitlab_ci(self):
        # given: os.environ has GITLAB_CI
        
        # when:
        git_host = GitHost()
        
        # then:
        self.assertTrue(git_host.is_gitlab())
        self.assertFalse(git_host.is_github())

    @patch.dict(os.environ, {"CI_SERVER_HOST": "gitlab.com"}, clear=True)
    def test_should_detect_gitlab_via_ci_server_host(self):
        # given: os.environ has CI_SERVER_HOST
        
        # when:
        git_host = GitHost()
        
        # then:
        self.assertTrue(git_host.is_gitlab())

    @patch.dict(os.environ, {}, clear=True)
    def test_should_raise_exception_when_no_provider_detected(self):
        # given: empty environment
        
        # when / then:
        with self.assertRaises(Exception) as context:
            GitHost()
        
        self.assertIn("Could not detect git host", str(context.exception))

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    @patch('valhalla.ci_provider.github.release.GitHubValhallaRelease')
    def test_get_release_impl_github(self, mock_release):
        # given:
        git_host = GitHost()
        
        # when:
        release_type = git_host.get_release_impl()
        
        # then:
        from valhalla.ci_provider.github.release import GitHubValhallaRelease
        self.assertEqual(release_type, GitHubValhallaRelease)

    @patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True)
    @patch('valhalla.ci_provider.gitlab.release.GitLabValhallaRelease')
    def test_get_release_impl_gitlab(self, mock_release):
        # given:
        git_host = GitHost()
        
        # when:
        release_type = git_host.get_release_impl()
        
        # then:
        from valhalla.ci_provider.gitlab.release import GitLabValhallaRelease
        self.assertEqual(release_type, GitLabValhallaRelease)

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    @patch('valhalla.ci_provider.github.merge_request.GitHubValhallaPullRequest')
    def test_create_merge_request_github(self, mock_pr_class):
        # given:
        git_host = GitHost()
        mock_pr_instance = mock_pr_class.return_value
        mock_config = MagicMock()
        
        # when:
        git_host.create_merge_request(mock_config)
        
        # then:
        mock_pr_class.assert_called_once()
        mock_pr_instance.create.assert_called_once_with(mock_config)

    @patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True)
    @patch('valhalla.ci_provider.gitlab.merge_request.GitLabValhallaMergeRequest')
    def test_create_merge_request_gitlab(self, mock_mr_class):
        # given:
        git_host = GitHost()
        mock_mr_instance = mock_mr_class.return_value
        mock_config = MagicMock()
        
        # when:
        git_host.create_merge_request(mock_config)
        
        # then:
        mock_mr_class.assert_called_once()
        mock_mr_instance.create.assert_called_once_with(mock_config)

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    @patch('valhalla.ci_provider.github.get_version.GitHubVersionToReleaseProvider')
    def test_get_version_to_release_github(self, mock_provider_class):
        # given:
        git_host = GitHost()
        mock_provider_instance = mock_provider_class.return_value
        release_kinds = MagicMock()
        
        # when:
        git_host.get_version_to_release(release_kinds)
        
        # then:
        mock_provider_class.assert_called_once()
        mock_provider_instance.get_from_branch_name.assert_called_once_with(release_kinds)

    @patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True)
    @patch('valhalla.ci_provider.gitlab.get_version.GitLabVersionToReleaseProvider')
    def test_get_version_to_release_gitlab(self, mock_provider_class):
        # given:
        git_host = GitHost()
        mock_provider_instance = mock_provider_class.return_value
        release_kinds = MagicMock()
        
        # when:
        git_host.get_version_to_release(release_kinds)
        
        # then:
        mock_provider_class.assert_called_once()
        mock_provider_instance.get_from_branch_name.assert_called_once_with(release_kinds)

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    @patch('valhalla.ci_provider.github.common.get_author')
    def test_get_author_github(self, mock_get_author):
        # given:
        git_host = GitHost()
        mock_get_author.return_value = "github-author"
        
        # when:
        author = git_host.get_author()
        
        # then:
        self.assertEqual(author, "github-author")
        mock_get_author.assert_called_once()

    @patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True)
    @patch('valhalla.ci_provider.gitlab.common.get_author')
    def test_get_author_gitlab(self, mock_get_author):
        # given:
        git_host = GitHost()
        mock_get_author.return_value = "gitlab-author"
        
        # when:
        author = git_host.get_author()
        
        # then:
        self.assertEqual(author, "gitlab-author")
        mock_get_author.assert_called_once()

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    @patch('valhalla.ci_provider.github.common.GitHubClient')
    def test_get_branches_github(self, mock_client_class):
        # given:
        git_host = GitHost()
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.api_url = "https://api.github.com"
        mock_client_instance.repo = "user/repo"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"name": "main"}, {"name": "develop"}]
        mock_client_instance.get.return_value = mock_response
        
        # when:
        branches = git_host.get_branches()
        
        # then:
        self.assertEqual(branches, ["main", "develop"])
        mock_client_instance.get.assert_called_once_with("https://api.github.com/repos/user/repo/branches")

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    @patch('valhalla.ci_provider.github.common.GitHubClient')
    def test_get_branches_github_pagination(self, mock_client_class):
        # given:
        git_host = GitHost()
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.api_url = "https://api.github.com"
        mock_client_instance.repo = "user/repo"

        # Mock first page response with Link header to next page
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = [{"name": "branch1"}]
        mock_response_1.links = {'next': {'url': 'https://api.github.com/repos/user/repo/branches?page=2'}}

        # Mock second page response
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = [{"name": "branch2"}]
        mock_response_2.links = {}

        mock_client_instance.get.side_effect = [mock_response_1, mock_response_2]

        # when:
        branches = git_host.get_branches()

        # then:
        self.assertEqual(branches, ["branch1", "branch2"])
        self.assertEqual(mock_client_instance.get.call_count, 2)

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}, clear=True)
    @patch('valhalla.ci_provider.github.common.GitHubClient')
    def test_get_branches_github_error(self, mock_client_class):
        # given:
        git_host = GitHost()
        mock_client_instance = mock_client_class.return_value
        mock_client_instance.api_url = "https://api.github.com"
        mock_client_instance.repo = "user/repo"
        
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_client_instance.get.return_value = mock_response
        
        # when / then:
        with self.assertRaises(Exception) as context:
            git_host.get_branches()
        
        self.assertIn("Failed to get branches from GitHub: 404 Not Found", str(context.exception))

    @patch.dict(os.environ, {"GITLAB_CI": "true"}, clear=True)
    @patch('valhalla.ci_provider.gitlab.common.get_gitlab_client')
    @patch('valhalla.ci_provider.gitlab.common.get_project_id')
    def test_get_branches_gitlab(self, mock_get_project_id, mock_get_gitlab_client):
        # given:
        git_host = GitHost()
        mock_get_project_id.return_value = 123
        mock_gl = mock_get_gitlab_client.return_value
        mock_project = MagicMock()
        mock_gl.projects.get.return_value = mock_project
        
        mock_branch_1 = MagicMock()
        mock_branch_1.name = "main"
        mock_branch_2 = MagicMock()
        mock_branch_2.name = "develop"
        mock_project.branches.list.return_value = [mock_branch_1, mock_branch_2]
        
        # when:
        branches = git_host.get_branches()
        
        # then:
        self.assertEqual(branches, ["main", "develop"])
        mock_gl.projects.get.assert_called_once_with(123)
        mock_project.branches.list.assert_called_once_with(all=True)

    @patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_REF_NAME": "feat/test"}, clear=True)
    def test_get_current_branch_github(self):
        # given:
        git_host = GitHost()
        
        # when:
        branch = git_host.get_current_branch()
        
        # then:
        self.assertEqual(branch, "feat/test")

    @patch.dict(os.environ, {"GITLAB_CI": "true", "CI_COMMIT_BRANCH": "feat/gitlab"}, clear=True)
    def test_get_current_branch_gitlab(self):
        # given:
        git_host = GitHost()
        
        # when:
        branch = git_host.get_current_branch()
        
        # then:
        self.assertEqual(branch, "feat/gitlab")


class AbstractClassesTest(unittest.TestCase):
    
    def test_release_abstract_method(self):
        class ConcreteRelease(Release):
            def create(self, description, milestones, release_name, tag_name, assets):
                return super().create(description, milestones, release_name, tag_name, assets)
        
        with self.assertRaises(TypeError):
            Release()
        
        with self.assertRaises(NotImplementedError):
            ConcreteRelease().create(None, None, None, None, None)

    def test_merge_request_abstract_method(self):
        class ConcreteMergeRequest(MergeRequest):
            def create(self, merge_request_config):
                return super().create(merge_request_config)

        with self.assertRaises(TypeError):
            MergeRequest()

        with self.assertRaises(NotImplementedError):
            ConcreteMergeRequest().create(None)

    def test_version_to_release_provider_abstract_method(self):
        class ConcreteVersionToReleaseProvider(VersionToReleaseProvider):
            def get_from_branch_name(self, release_kinds):
                return super().get_from_branch_name(release_kinds)

        with self.assertRaises(TypeError):
            VersionToReleaseProvider()

        with self.assertRaises(NotImplementedError):
            ConcreteVersionToReleaseProvider().get_from_branch_name([])
