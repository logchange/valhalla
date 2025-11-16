import unittest
from unittest.mock import Mock, patch, call

from valhalla.commit.commit import is_ignored, GitRepository


class IsIgnoredTest(unittest.TestCase):
    def test_is_ignored_true_for_m2(self):
        self.assertTrue(is_ignored(".m2/repository/file.jar"))
        self.assertTrue(is_ignored(".m2/cache/anything"))

    def test_is_ignored_false_other_paths(self):
        self.assertFalse(is_ignored("src/main.py"))
        self.assertFalse(is_ignored("README.md"))


class GitRepositoryInitTest(unittest.TestCase):
    @patch('valhalla.commit.commit.info')
    @patch('valhalla.commit.commit.Repo')
    def test_init_sets_defaults_and_writes_config(self, mock_repo_cls: Mock, mock_info: Mock):
        repo = Mock()
        mock_repo_cls.init.return_value = repo

        config_writer = Mock()
        # config_writer().set_value().release() pattern
        repo.config_writer.return_value = config_writer
        config_writer.set_value.return_value = config_writer

        GitRepository(git_username=None, git_email=None)

        # Defaults should be logged
        mock_info.assert_any_call("Git username not set, using default valhalla-bot")
        mock_info.assert_any_call("Git email not set, using default valhalla-bot@logchange.dev")

        # Config should be written twice: name and email
        expected_calls = [
            call.set_value("user", "name", "valhalla-bot"),
            call.release(),
            call.set_value("user", "email", "valhalla-bot@logchange.dev"),
            call.release(),
        ]
        self.assertEqual(expected_calls, config_writer.method_calls)


class GitRepositoryStatusTest(unittest.TestCase):
    @patch('valhalla.commit.commit.info')
    @patch('valhalla.commit.commit.Repo')
    def test_status_logs_untracked_and_modified(self, mock_repo_cls: Mock, mock_info: Mock):
        repo = Mock()
        mock_repo_cls.init.return_value = repo
        # Untracked files
        repo.untracked_files = ['a.txt', 'dir/b.txt']
        # Modified files: provide objects with a_path
        modified_1 = Mock(a_path='m1.txt')
        modified_2 = Mock(a_path='dir/m2.txt')
        repo.index.diff.return_value = [modified_1, modified_2]

        gr = GitRepository('u', 'e')
        gr.status()

        # Ensure logs for untracked and modified
        mock_info.assert_any_call('a.txt is untracked')
        mock_info.assert_any_call('dir/b.txt is untracked')
        mock_info.assert_any_call('m1.txt is modified')
        mock_info.assert_any_call('dir/m2.txt is modified')


class GitRepositoryCommitTest(unittest.TestCase):
    @patch('valhalla.commit.commit.resolve', side_effect=lambda x: x)
    @patch('valhalla.commit.commit.warn')
    @patch('valhalla.commit.commit.info')
    @patch('valhalla.commit.commit.Repo')
    def test_commit_adds_untracked_and_modified_and_commits(self, mock_repo_cls: Mock, mock_info: Mock, mock_warn: Mock, mock_resolve: Mock):
        repo = Mock()
        mock_repo_cls.init.return_value = repo
        # Provide git facade
        repo.git = Mock()
        # One ignored file and one regular file
        repo.untracked_files = ['.m2/repository/x', 'new.txt']
        # Modified files
        modified = Mock(a_path='mod.txt')
        repo.index.diff.return_value = [modified]

        gr = GitRepository('u', 'e')
        result = gr.commit('My message')

        # Should skip the .m2 file and warn once
        mock_warn.assert_any_call("Skipping untracked file: .m2/repository/x check your .gitignore! see: https://github.com/logchange/valhalla/blob/master/README.md#-gitignore")
        # Should add new.txt and mod.txt to stage
        repo.git.add.assert_any_call('new.txt')
        repo.git.add.assert_any_call('mod.txt')
        # Should commit with appended marker and resolved message
        repo.index.commit.assert_called_once_with('My message [VALHALLA SKIP]')
        self.assertTrue(result)

    @patch('valhalla.commit.commit.resolve', side_effect=lambda x: x)
    @patch('valhalla.commit.commit.warn')
    @patch('valhalla.commit.commit.info')
    @patch('valhalla.commit.commit.Repo')
    def test_commit_when_no_changes_returns_false(self, mock_repo_cls: Mock, mock_info: Mock, mock_warn: Mock, mock_resolve: Mock):
        repo = Mock()
        mock_repo_cls.init.return_value = repo
        repo.git = Mock()
        repo.untracked_files = []
        repo.index.diff.return_value = []

        gr = GitRepository('u', 'e')
        result = gr.commit('Nothing')

        mock_warn.assert_any_call('There is noting to commit!')
        repo.index.commit.assert_not_called()
        self.assertFalse(result)

    @patch('valhalla.commit.commit.resolve', side_effect=lambda x: x)
    @patch('valhalla.commit.commit.info')
    @patch('valhalla.commit.commit.Repo')
    def test_commit_with_add_false_only_modified_are_added(self, mock_repo_cls: Mock, mock_info: Mock, mock_resolve: Mock):
        repo = Mock()
        mock_repo_cls.init.return_value = repo
        repo.git = Mock()
        repo.untracked_files = ['untracked.txt']
        modified = Mock(a_path='changed.txt')
        repo.index.diff.return_value = [modified]

        gr = GitRepository('u', 'e')
        result = gr.commit('Msg', add=False)

        # untracked should not be added
        repo.git.add.assert_called_once_with('changed.txt')
        repo.index.commit.assert_called_once_with('Msg [VALHALLA SKIP]')
        self.assertTrue(result)


class GitRepositoryPushTest(unittest.TestCase):
    @patch('valhalla.commit.commit.info')
    @patch('valhalla.commit.commit.Repo')
    def test_push_uses_computed_url_and_branch(self, mock_repo_cls: Mock, mock_info: Mock):
        repo = Mock()
        mock_repo_cls.init.return_value = repo
        repo.git = Mock()
        # Simulate active branch stringable
        repo.active_branch = 'main'

        # remote url without creds
        origin = Mock()
        origin.url = 'https://github.com/org/repo.git'
        repo.remote.return_value = origin

        gr = GitRepository('u', 'e')
        gr.push('abc')

        expected_push_url = 'https://valhalla-bot:abc@github.com/org/repo.git'
        repo.git.push.assert_called_once_with(expected_push_url, 'main')

    @patch('valhalla.commit.commit.info')
    @patch('valhalla.commit.commit.Repo')
    def test__get_push_url_various_remote_formats(self, mock_repo_cls: Mock, mock_info: Mock):
        repo = Mock()
        mock_repo_cls.init.return_value = repo
        gr = GitRepository('u', 'e')

        origin = Mock()
        repo.remote.return_value = origin

        # Case 1: http URL
        origin.url = 'http://gitlab.com/group/project.git'
        self.assertEqual(
            'https://valhalla-bot:tok@gitlab.com/group/project.git',
            gr._GitRepository__get_push_url('tok')
        )

        # Case 2: https URL with user part
        origin.url = 'https://user@bitbucket.org/team/repo.git'
        self.assertEqual(
            'https://valhalla-bot:tok@bitbucket.org/team/repo.git',
            gr._GitRepository__get_push_url('tok')
        )

        # Case 3: SSH-like URL (it will trim part before @)
        origin.url = 'git@github.com:org/repo.git'
        self.assertEqual(
            'https://valhalla-bot:tok@github.com:org/repo.git',
            gr._GitRepository__get_push_url('tok')
        )


if __name__ == '__main__':
    unittest.main()
