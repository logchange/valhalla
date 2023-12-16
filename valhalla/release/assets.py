from typing import List

import json

from valhalla.common.get_config import ReleaseAssetsConfig, ReleaseAssetsLinkConfig
from valhalla.common.logger import info
from valhalla.common.resolver import resolve


class AssetsLink:
    name: str
    url: str
    link_type: str

    def __init__(self, link: ReleaseAssetsLinkConfig):
        self.name = resolve(link.name)
        self.url = resolve(link.url)
        self.link_type = link.link_type


class Assets:
    links: List[AssetsLink]

    def __init__(self, assets: ReleaseAssetsConfig):
        self.links = []

        for link in assets.links:
            self.links.append(AssetsLink(link))

    def json(self):
        assets_json = json.dumps(self.__dict__, default=lambda o: o.__dict__)
        info("assets_json: " + assets_json)
        return assets_json

    def to_dict(self):
        test = json.loads(json.dumps(self, default=lambda o: o.__dict__))
        print(test)
        return test