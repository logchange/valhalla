import unittest

from valhalla.common.get_config import ReleaseAssetsLinkConfig, ReleaseAssetsConfig
from valhalla.common.resolver import init_str_resolver
from valhalla.release.assets import AssetsLink, Assets


class TestAssetsLink(unittest.TestCase):
    def test_assets_link_creation(self):
        init_str_resolver("1.1.1", "alamaKota", "kot")

        link_config = ReleaseAssetsLinkConfig('Test Asset', 'http://example.com/test_asset', 'image')

        assets_link = AssetsLink(link_config)

        self.assertEqual(assets_link.name, 'Test Asset')
        self.assertEqual(assets_link.url, 'http://example.com/test_asset')
        self.assertEqual(assets_link.link_type, 'image')


class TestAssets(unittest.TestCase):
    def test_assets_creation(self):
        init_str_resolver("1.1.1", "alamaKota", "kot")

        assets_config = ReleaseAssetsConfig([
            ReleaseAssetsLinkConfig('Test Asset 1', 'http://example.com/test_asset_1', 'image'),
            ReleaseAssetsLinkConfig('Test Asset 2', 'http://example.com/test_asset_2', 'other')
        ])

        assets = Assets(assets_config)

        self.assertEqual(len(assets.links), 2)
        self.assertEqual(assets.links[0].name, 'Test Asset 1')
        self.assertEqual(assets.links[0].url, 'http://example.com/test_asset_1')
        self.assertEqual(assets.links[0].link_type, 'image')
        self.assertEqual(assets.links[1].name, 'Test Asset 2')
        self.assertEqual(assets.links[1].url, 'http://example.com/test_asset_2')
        self.assertEqual(assets.links[1].link_type, 'other')

    def test_assets_json_empty(self):
        init_str_resolver("1.1.1", "alamaKota", "kot")

        assets_config = ReleaseAssetsConfig([])
        assets = Assets(assets_config)

        json = assets.json()

        self.assertEqual(json, '{"links": []}')

    def test_assets_json(self):
        init_str_resolver("1.1.1", "alamaKota", "kot")

        assets_config = ReleaseAssetsConfig([
            ReleaseAssetsLinkConfig('Test Asset 1', 'http://example.com/test_asset_1', 'image'),
            ReleaseAssetsLinkConfig('Test Asset 2', 'http://example.com/test_asset_2', 'other')
        ])
        assets = Assets(assets_config)

        json = assets.json()

        self.assertEqual(json, '{"links": [{"name": "Test Asset 1", "url": "http://example.com/test_asset_1", "link_type": "image"}, {"name": "Test Asset 2", "url": "http://example.com/test_asset_2", "link_type": "other"}]}')
