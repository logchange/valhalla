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
