import unittest
from unittest.mock import patch, Mock, call
from valhalla.commit.before import execute  # Adjust the import according to your module structure


class TestExecuteFunction(unittest.TestCase):

    @patch('valhalla.commit.before.exit')
    @patch('valhalla.commit.before.resolve')
    @patch('valhalla.commit.before.info')
    @patch('valhalla.commit.before.error')
    def test_execute_success(self, mock_error: Mock, mock_info: Mock, mock_resolve: Mock, mock_exit: Mock):
        mock_resolve.side_effect = lambda x: x  # Simply return the command itself

        execute(["echo 'Hello World'"])

        mock_info.assert_has_calls([call("Output for command 'echo 'Hello World'':\nHello World\n"),
                                   call("Successfully executed command: 'echo 'Hello World''")])
        mock_error.assert_not_called()
        mock_exit.assert_not_called()

    @patch('valhalla.commit.before.exit')
    @patch('valhalla.commit.before.resolve')
    @patch('valhalla.commit.before.info')
    @patch('valhalla.commit.before.error')
    def test_execute_error(self, mock_error: Mock, mock_info: Mock, mock_resolve: Mock, mock_exit: Mock):
        mock_resolve.side_effect = lambda x: x  # Simply return the command itself

        execute(["mvn clean"])

        mock_exit.assert_called_with(1)
