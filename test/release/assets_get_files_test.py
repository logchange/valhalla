import unittest
from unittest.mock import patch

from valhalla.release.assets import Assets
from valhalla.common.get_config import ReleaseAssetsConfig


class AssetsGetFilesTest(unittest.TestCase):

    @patch("valhalla.release.assets.resolve", side_effect=lambda x: x)
    @patch("valhalla.release.assets.os.path.isfile")
    @patch("valhalla.release.assets.glob.glob")
    def test_get_files_expands_patterns_and_filters_only_files(self, mock_glob, mock_isfile, mock_resolve):
        # given
        # Patterns contain a wildcard and a single explicit file
        cfg = ReleaseAssetsConfig(links=[], files=["./bins/*.zip", "dist/app.tar.gz"]) 
        assets = Assets(cfg)

        def glob_side_effect(pattern):
            if pattern == "./bins/*.zip":
                # Include two files and a directory in matches
                return ["./bins/a.zip", "./bins/b.zip", "./bins/subdir"]
            if pattern == "dist/app.tar.gz":
                return ["dist/app.tar.gz"]
            return []

        mock_glob.side_effect = glob_side_effect

        def isfile_side_effect(path):
            # Treat paths ending with .zip or .gz as files; others as non-files
            return path.endswith(".zip") or path.endswith(".gz")

        mock_isfile.side_effect = isfile_side_effect

        # when
        result = assets.get_files()

        # then
        # Expect directory to be filtered out and order preserved
        self.assertEqual(["./bins/a.zip", "./bins/b.zip", "dist/app.tar.gz"], result)

    @patch("valhalla.release.assets.resolve", side_effect=lambda x: x)
    @patch("valhalla.release.assets.glob.glob", return_value=[])
    def test_get_files_with_no_matches_returns_empty_list(self, mock_glob, mock_resolve):
        # given
        cfg = ReleaseAssetsConfig(links=[], files=["nope/*.txt"]) 
        assets = Assets(cfg)

        # when
        result = assets.get_files()

        # then
        self.assertEqual([], result)


if __name__ == '__main__':
    unittest.main()
