import io
import sys
import unittest
from unittest.mock import patch


class MainCliTest(unittest.TestCase):

    def test_main_no_args_calls_start(self):
        with patch('valhalla.main.start') as mock_start, \
                patch.object(sys, 'argv', ['valhalla']):
            from valhalla.main import main  # import here to ensure patches applied
            main()
            mock_start.assert_called_once()

    def test_main_help_calls_print_help_short_and_long(self):
        # -h
        with patch('valhalla.main.print_help') as mock_help, \
                patch.object(sys, 'argv', ['valhalla', '-h']):
            from valhalla.main import main
            main()
            mock_help.assert_called_once()
        # --help
        with patch('valhalla.main.print_help') as mock_help, \
                patch.object(sys, 'argv', ['valhalla', '--help']):
            from valhalla.main import main
            main()
            mock_help.assert_called_once()

    def test_main_start_subcommand_calls_start(self):
        with patch('valhalla.main.start') as mock_start, \
                patch.object(sys, 'argv', ['valhalla', 'start']):
            from valhalla.main import main
            main()
            mock_start.assert_called_once()

    def test_main_unknown_command_prints_and_exits(self):
        with patch.object(sys, 'argv', ['valhalla', 'unknown-cmd']), \
                patch('valhalla.main.print_help') as mock_help, \
                patch('sys.stdout', new_callable=io.StringIO) as stdout:
            from valhalla.main import main
            with self.assertRaises(SystemExit) as cm:
                main()
            # ensure exit code is 1
            self.assertEqual(cm.exception.code, 1)
            # ensure it printed the unknown command message and called help
            output = stdout.getvalue()
            self.assertIn('Unknown command: unknown-cmd', output)
            mock_help.assert_called_once()

    def test_print_help_outputs_expected(self):
        # capture stdout and check that key parts of help are present
        from valhalla.main import print_help
        with patch('sys.stdout', new_callable=io.StringIO) as stdout:
            print_help()
            out = stdout.getvalue()
            self.assertIn('valhalla is a toolkit designed', out)
            self.assertIn('Usage:', out)
            self.assertIn("valhalla start      Start the release process.", out)
            self.assertIn('Docs: https://logchange.dev/tools/valhalla/', out)


if __name__ == '__main__':
    unittest.main()
