from typing import List

import json
import glob
import os
import mimetypes

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
        # Store file patterns but keep them out of JSON output semantics
        self._file_patterns = [resolve(p) for p in (assets.files or [])]

        for link in assets.links:
            self.links.append(AssetsLink(link))

    def json(self):
        # Only serialize links to keep backward compatibility with tests/consumers
        data = {"links": [
            {"name": l.name, "url": l.url, "link_type": l.link_type} for l in self.links
        ]}
        assets_json = json.dumps(data)
        info("assets_json: " + assets_json)
        return assets_json

    def to_dict(self):
        # For tests/debug; mirror json structure
        return {"links": [
            {"name": l.name, "url": l.url, "link_type": l.link_type} for l in self.links
        ]}

    def get_files(self) -> List[str]:
        """Expand glob patterns into existing file paths."""
        files: List[str] = []
        for pattern in self._file_patterns:
            matched = glob.glob(pattern)
            for f in matched:
                if os.path.isfile(f):
                    files.append(f)
        return files

    @staticmethod
    def guess_mime(path: str) -> str:
        mime, _ = mimetypes.guess_type(path)
        return mime or 'application/octet-stream'
