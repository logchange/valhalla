import unittest
from unittest.mock import patch, MagicMock
import subprocess
from valhalla.common.executor import Executor

class ExecutorTest(unittest.TestCase):
    
    @patch('subprocess.run')
    def test_run_success(self, mock_run):
        # given:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        # when:
        result = Executor.run("ls", check=True)
        
        # then:
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "output")
        self.assertEqual(result.stderr, "")
        mock_run.assert_called_once_with("ls", shell=True, check=True, capture_output=True, text=True)

    @patch('subprocess.run')
    def test_run_error(self, mock_run):
        # given:
        mock_run.side_effect = subprocess.CalledProcessError(1, "ls", stderr="error output", output="error output")
        
        # when:
        result = Executor.run("ls", check=True)
        
        # then:
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "error output")

    @patch('subprocess.run')
    def test_run_exception(self, mock_run):
        # given:
        mock_run.side_effect = Exception("unexpected error")
        
        # when:
        result = Executor.run("ls", check=True)
        
        # then:
        self.assertIsNone(result)
