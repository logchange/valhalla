import unittest
from unittest.mock import mock_open, patch

from valhalla.common.get_config import get_config


class ReleaseAssetsFilesParsingTest(unittest.TestCase):

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='''
        git_host: gitlab
        release:
          name: "Rel"
          assets:
            files:
              - "./bins/*.zip"
              - "dist/app.tar.gz"
        '''
    )
    def test_parse_assets_files(self, mock_open_file):
        cfg = get_config('valhalla.yml')
        self.assertIsNotNone(cfg.release_config)
        self.assertIsNotNone(cfg.release_config.assets_config)
        files = cfg.release_config.assets_config.files
        self.assertEqual(["./bins/*.zip", "dist/app.tar.gz"], files)


if __name__ == '__main__':
    unittest.main()
