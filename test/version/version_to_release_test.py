import os
import unittest
from unittest.mock import patch

from valhalla.version.version_to_release import get_release_kinds


class GetValhallaReleaseKindsTest(unittest.TestCase):

    def test_main_file(self):
        path = os.path.dirname(os.path.abspath(__file__)) + "/resources/test_main_file"
        result = get_release_kinds(path)

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0].filename, "valhalla.yml")
        self.assertEqual(result[0].suffix, "")
        self.assertEqual(result[0].path, path)

    def test_main_and_hotfix_file(self):
        path = os.path.dirname(os.path.abspath(__file__)) + "/resources/test_main_and_hotfix_file"
        result = get_release_kinds(path)

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].filename, "valhalla.yml")
        self.assertEqual(result[0].suffix, "")
        self.assertEqual(result[0].path, path)

        self.assertEqual(result[1].filename, "valhalla-hotfix.yml")
        self.assertEqual(result[1].suffix, "-hotfix")
        self.assertEqual(result[1].path, path)

    @patch('valhalla.version.version_to_release.exit')
    def test_empty(self, mock_exit):
        path = os.path.dirname(os.path.abspath(__file__)) + "/resources/empty"
        result = get_release_kinds(path)
        mock_exit.assert_called_with(-1)
