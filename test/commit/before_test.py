import unittest
from unittest.mock import patch, Mock, call, MagicMock
from valhalla.commit.before import execute  # Adjust the import according to your module structure


class TestExecuteFunction(unittest.TestCase):

    @patch('valhalla.commit.before.exit')
    @patch('valhalla.commit.before.resolve')
    @patch('valhalla.common.executor.info')
    @patch('valhalla.commit.before.info')
    @patch('valhalla.commit.before.error')
    @patch('valhalla.common.executor.subprocess.run')
    def test_execute_success(self, mock_subprocess_run: Mock, mock_error: Mock, mock_info: Mock, mock_executor_info: Mock, mock_resolve: Mock, mock_exit: Mock):
        # given:
        mock_resolve.side_effect = lambda x: x
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Hello World\n"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        # when:
        execute(["echo 'Hello World'"])

        # then:
        mock_executor_info.assert_called_with("Output for command 'echo 'Hello World'':\nHello World\n")
        mock_info.assert_called_with("Successfully executed command: 'echo 'Hello World''")
        mock_error.assert_not_called()
        mock_exit.assert_not_called()

    @patch('valhalla.commit.before.exit')
    @patch('valhalla.commit.before.resolve')
    @patch('valhalla.common.executor.error')
    @patch('valhalla.commit.before.info')
    @patch('valhalla.commit.before.error')
    @patch('valhalla.common.executor.subprocess.run')
    def test_execute_error(self, mock_subprocess_run: Mock, mock_error: Mock, mock_info: Mock, mock_executor_error: Mock, mock_resolve: Mock, mock_exit: Mock):
        # given:
        mock_resolve.side_effect = lambda x: x
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "mvn error"
        mock_subprocess_run.return_value = mock_result

        # when:
        execute(["mvn clean"])

        # then:
        mock_executor_error.assert_called_with("Error output for command 'mvn clean':\nmvn error")
        mock_exit.assert_called_with(1)
