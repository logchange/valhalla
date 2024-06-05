import unittest
from unittest.mock import patch, Mock

from valhalla.extends.valhalla_extends import get_from_url


class TestGetFromUrl(unittest.TestCase):

    @patch('requests.get')
    def test_get_from_url_success(self, mock_get):
        # given:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_get.return_value = mock_response

        # when:
        result = get_from_url('http://example.com')

        # then:
        self.assertEqual(result, "Success")

    @patch('requests.get')
    @patch('valhalla.extends.valhalla_extends.exit')
    def test_get_from_url_failure(self, mock_exit, mock_get):
        # given:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        # when:
        get_from_url('http://example.com')

        # then:
        mock_exit.assert_called_with(1)
