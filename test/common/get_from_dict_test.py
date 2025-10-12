import unittest
from unittest.mock import patch

from valhalla.common.get_config import get_from_dict


class GetFromDictTest(unittest.TestCase):

    @patch('valhalla.common.get_config.error')
    def test_required_missing_raises(self, mock_error):
        with self.assertRaises(RuntimeError) as ctx:
            get_from_dict({}, 'git_host', True)
        self.assertIn('Missing required git_host in valhalla.yml!', str(ctx.exception))
        mock_error.assert_called()  # ensure error was logged

    @patch('valhalla.common.get_config.info')
    def test_optional_missing_returns_none_and_logs(self, mock_info):
        value = get_from_dict({}, 'optional_key', False)
        self.assertIsNone(value)
        mock_info.assert_called()  # ensure info was logged


if __name__ == '__main__':
    unittest.main()
