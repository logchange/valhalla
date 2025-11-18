import unittest
from unittest.mock import patch

from valhalla.ci_provider.github.release import expand_file_patterns


class ExpandFilePatternsTest(unittest.TestCase):

    @patch("valhalla.ci_provider.github.release.os.path.abspath")
    @patch("valhalla.ci_provider.github.release.glob.glob")
    def test_expand_mixed_patterns_multiple_matches(self, mock_glob, mock_abspath):
        # given
        def glob_side_effect(pattern):
            if pattern == "./bins/*.zip":
                return ["./bins/a.zip", "./bins/b.zip"]
            if pattern == "dist/app.tar.gz":
                return ["dist/app.tar.gz"]
            return []

        def abspath_side_effect(path):
            # create a deterministic absolute path for assertions
            cleaned = path.replace("./", "")
            return f"/abs/{cleaned}"

        mock_glob.side_effect = glob_side_effect
        mock_abspath.side_effect = abspath_side_effect

        patterns = ["./bins/*.zip", "dist/app.tar.gz"]

        # when
        result = expand_file_patterns(patterns)

        # then
        self.assertEqual([
            ("a.zip", "/abs/bins/a.zip"),
            ("b.zip", "/abs/bins/b.zip"),
            ("app.tar.gz", "/abs/dist/app.tar.gz"),
        ], result)

    @patch("valhalla.ci_provider.github.release.glob.glob", return_value=[])
    def test_expand_no_matches_returns_empty(self, mock_glob):
        # given
        patterns = ["nope/*.txt"]

        # when
        result = expand_file_patterns(patterns)

        # then
        self.assertEqual([], result)


if __name__ == '__main__':
    unittest.main()
