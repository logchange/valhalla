import unittest
from unittest.mock import MagicMock, patch


def fake_environ_get(key, default=None):
    if key == "GITLAB_CI":
        return "true"
    return ""


class MainStartTest(unittest.TestCase):

    def test_start_happy_path(self):
        # given: version_to_release is present, config is provided, and all steps are executed
        mock_vtr = MagicMock()
        mock_vtr.is_version_empty.return_value = False
        mock_vtr.get_config_file_path.return_value = "test/resources/valhalla.yml"
        mock_vtr.version_number_to_release = "1.2.3"

        # mock requests.get used by ValhallaExtends to return local extended file content
        def _mock_requests_get(url):
            class R:
                status_code = 200

                def __init__(self, text):
                    self.text = text

            with open("test/resources/valhalla-extended.yml", "r") as f:
                return R(f.read())

        with patch('valhalla.main.__version_to_release', return_value=mock_vtr), \
                patch('valhalla.extends.valhalla_extends.requests.get', side_effect=_mock_requests_get), \
                patch('valhalla.main.get_valhalla_token', return_value='TOKEN') as mock_get_token, \
                patch('os.environ.get', side_effect=fake_environ_get),\
                patch('valhalla.ci_provider.git_host.GitHost.get_author', return_value='AUTHOR') as mock_get_author, \
                patch('valhalla.main.commit') as mock_commit, \
                patch('valhalla.main.get_other_release_in_progress', return_value=[]), \
                patch('valhalla.main.create_release') as mock_create_release, \
                patch('valhalla.main.create_merge_request') as mock_create_mr:
            from valhalla.main import start

            # when: running start should not raise
            start()

            # logger & resolver initialization
            mock_get_token.assert_called_once()
            mock_get_author.assert_called_once()

            # core actions
            self.assertEqual(mock_commit.call_count, 2, "commit should be called twice (before and after release)")
            # create_release called with some Config and the correct version
            args, kwargs = mock_create_release.call_args
            self.assertEqual(args[2], "1.2.3")
            # merge request config is default and disabled in our test YAML
            self.assertEqual(mock_create_mr.call_count, 1)

    def test_start_creates_mr_and_posts_error_when_version_empty(self):
        # given: version is empty and from_config does not resolve it (e.g. command failed)
        mock_vtr = MagicMock()
        mock_vtr.is_version_empty.return_value = True
        mock_vtr.get_config_file_path.return_value = "test/resources/valhalla.yml"

        provider_hook = MagicMock()

        def _mock_requests_get(url):
            class R:
                status_code = 200

                def __init__(self, text):
                    self.text = text

            with open("test/resources/valhalla-extended.yml", "r") as f:
                return R(f.read())

        with patch('valhalla.main.__version_to_release', return_value=mock_vtr), \
                patch('valhalla.extends.valhalla_extends.requests.get', side_effect=_mock_requests_get), \
                patch('valhalla.main.get_valhalla_token', return_value='TOKEN'), \
                patch('os.environ.get', side_effect=fake_environ_get), \
                patch('valhalla.ci_provider.git_host.GitHost.get_author', return_value='AUTHOR'), \
                patch('valhalla.main.create_merge_request', return_value=provider_hook) as mock_create_mr:
            from valhalla.main import start

            # when: running start should exit with error
            with self.assertRaises(SystemExit):
                start()

            # then: MR is created so the error is posted as a comment
            self.assertEqual(mock_create_mr.call_count, 1)
            # The "Version to release is empty" error is posted to the MR
            posted = "\n".join(
                call_args[0][0] for call_args in provider_hook.add_comment.call_args_list
            )
            self.assertIn("Version to release is empty", posted)
