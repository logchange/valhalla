import unittest
from unittest.mock import mock_open, patch

from valhalla.common.get_config import get_config


class GetConfigTest(unittest.TestCase):

    def setUp(self):
        self.config_path = "test_config.yml"
        self.mock_yml_content = """
        git_host: gitlab
        commit_before_release:
            enabled: True
            before:
              - echo "test"
              - echo "test2"
        """

    @patch(
        "valhalla.common.get_config.open",
        new_callable=mock_open,
        read_data="""
        git_host: gitlab
        commit_before_release:
            enabled: True
            msg: test commit message
            before:
              - echo "test"
              - echo "test2"
        release:
            name: "Test Release Name"
            description:
                from_command: "cat changelog/v{VERSION}/version_summary.md"
        tag:
            name: "Test Tag Name"
        merge_request:
            enabled: On
            title: test mr title
        """,
    )
    def test_get_config(self, mock_open_file):
        config = get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)

        self.assertEqual(config.git_host, "gitlab")
        self.assertEqual(config.commit_before_release.enabled, True)
        self.assertEqual(
            config.commit_before_release.before_commands,
            ['echo "test"', 'echo "test2"'],
        )
        self.assertEqual(config.merge_request.enabled, True)

        mock_open_file.assert_called_once_with(self.config_path)

    @patch(
        "valhalla.common.get_config.open",
        new_callable=mock_open,
        read_data="""
        version:
            from_command: "cat version.txt"
        git_host: gitlab
        release:
            name: "Test Release Name"
        """,
    )
    def test_get_version_config(self, mock_open_file):
        config = get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)

        self.assertIsNotNone(config.version_config)
        self.assertEqual(config.version_config.from_command, "cat version.txt")

        mock_open_file.assert_called_once_with(self.config_path)

    @patch(
        "valhalla.common.get_config.open",
        new_callable=mock_open,
        read_data="""
        git_host: gitlab
        commit_before_release:
            enabled: True
            msg: test commit message
            before:
              - echo "test"
              - echo "test2"
        release:
            description:
                from_command: "cat changelog/v{VERSION}/version_summary.md"
        """,
    )
    def test_get_config_no_mr_section(self, mock_open_file):
        config = get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)

        self.assertEqual(config.merge_request.enabled, True)
        self.assertEqual(config.merge_request.target_branch, "")
        self.assertEqual(config.merge_request.title, "Releasing version {VERSION} with valhalla!")
        self.assertEqual(config.merge_request.description, "Created by Valhalla! Visit https://github.com/logchange/valhalla and leave a star!")
        self.assertEqual(config.merge_request.reviewers, [])

        mock_open_file.assert_called_once_with(self.config_path)

    @patch(
        "valhalla.common.get_config.open",
        new_callable=mock_open,
        read_data="""
        git_host: gitlab
        commit_before_release:
            enabled: True
            msg: test commit message
            before:
              - echo "test"
              - echo "test2"
        release:
            description:
                from_command: "cat changelog/v{VERSION}/version_summary.md"
        merge_request:
            enabled: False
            title: test mr title
        """,
    )
    def test_get_config_mr_disabled(self, mock_open_file):
        config = get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)

        self.assertEqual(config.merge_request.enabled, False)
        self.assertEqual(config.merge_request.target_branch, None)
        self.assertEqual(config.merge_request.title, "test mr title")
        self.assertEqual(config.merge_request.description, "Created by Valhalla! Visit https://github.com/logchange/valhalla and leave a star!")
        self.assertEqual(config.merge_request.reviewers, None)

        mock_open_file.assert_called_once_with(self.config_path)

    @patch("valhalla.common.get_config.open", side_effect=FileNotFoundError)
    def test_get_config_file_not_found(self, mock_open_file):
        with self.assertRaises(SystemExit) as context:
            get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)
        self.assertEqual(context.exception.code, -1)

    @patch(
        "valhalla.common.get_config.open",
        new_callable=mock_open,
        read_data="""
        git_host: gitlab
        release:
            name: "Test Release Name {VERSION}"
            milestones: 
                - "Test Milestone"
            description:
                from_command: "cat changelog/v{VERSION}/version_summary.md"
        """,
    )
    def test_get_release_config(self, mock_open_file):
        config = get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)

        self.assertIsNotNone(config.release_config)
        self.assertEqual(config.release_config.name, "Test Release Name {VERSION}")
        self.assertEqual(config.release_config.milestones, ['Test Milestone'])
        self.assertEqual(config.release_config.description_config.from_command,
                         "cat changelog/v{VERSION}/version_summary.md")

        mock_open_file.assert_called_once_with(self.config_path)

    @patch(
        "valhalla.common.get_config.open",
        new_callable=mock_open,
        read_data="""
        git_host: gitlab
        release:
            name: "Test Release Name {VERSION}"
            description:
                from_command: "cat changelog/v{VERSION}/version_summary.md"
        tag:
            name: "Test Tag Name {VERSION}"
        """,
    )
    def test_get_tag_config(self, mock_open_file):
        config = get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)

        self.assertIsNotNone(config.tag_config)
        self.assertEqual(config.tag_config.name, "Test Tag Name {VERSION}")

        mock_open_file.assert_called_once_with(self.config_path)


if __name__ == "__main__":
    unittest.main()
