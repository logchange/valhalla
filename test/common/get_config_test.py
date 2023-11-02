import unittest
from unittest.mock import mock_open, patch

from valhalla.common.get_config import get_config


class GetConfigTest(unittest.TestCase):

    def setUp(self):
        self.config_path = 'test_config.yml'
        self.mock_yml_content = """
        git_host: gitlab
        project_name: valhalla
        commit: 
            enabled: True
            before:
              - echo "test"
              - echo "test2"
        """

    @patch('builtins.open', new_callable=mock_open, read_data="""
        git_host: gitlab
        project_name: valhalla
        commit: 
            enabled: True
            before:
              - echo "test"
              - echo "test2"
        """)
    def test_get_config(self, mock_open_file):
        config = get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)

        self.assertEqual(config.git_host, 'gitlab')
        self.assertEqual(config.project_name, 'valhalla')
        self.assertEqual(config.commit.enabled, True)
        self.assertEqual(config.commit.before_commands, ['echo "test"', 'echo "test2"'])

        mock_open_file.assert_called_once_with(self.config_path)

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_get_config_file_not_found(self, mock_open_file):
        with self.assertRaises(SystemExit) as context:
            get_config(self.config_path)

        mock_open_file.assert_called_once_with(self.config_path)
        self.assertEqual(context.exception.code, -1)


if __name__ == '__main__':
    unittest.main()
