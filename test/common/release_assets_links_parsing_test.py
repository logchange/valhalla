import unittest
from unittest.mock import mock_open, patch

from valhalla.common.get_config import get_config


class ReleaseAssetsLinksParsingTest(unittest.TestCase):

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='''
        git_host: gitlab
        release:
          name: "Rel"
          assets:
            links:
              - name: "Documentation"
                url: "https://example.com/docs"
                link_type: "doc"
              - name: "Image"
                url: "https://example.com/diagram.png"
                link_type: "image"
        '''
    )
    def test_parse_assets_links(self, mock_open_file):
        cfg = get_config('valhalla.yml')
        self.assertIsNotNone(cfg.release_config)
        self.assertIsNotNone(cfg.release_config.assets_config)
        links = cfg.release_config.assets_config.links
        self.assertEqual(2, len(links))
        self.assertEqual(('Documentation', 'https://example.com/docs', 'doc'),
                         (links[0].name, links[0].url, links[0].link_type))
        self.assertEqual(('Image', 'https://example.com/diagram.png', 'image'),
                         (links[1].name, links[1].url, links[1].link_type))

    @patch(
        'builtins.open',
        new_callable=mock_open,
        read_data='''
        git_host: gitlab
        release:
          name: "Rel"
          assets: {}
        '''
    )
    def test_assets_links_none(self, mock_open_file):
        cfg = get_config('valhalla.yml')
        self.assertEqual([], cfg.release_config.assets_config.links)


if __name__ == '__main__':
    unittest.main()
