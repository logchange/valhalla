import os
import requests

from valhalla.ci_provider.github.common import get_repository_slug, get_api_url
from valhalla.common.logger import info, warn
from valhalla.release.assets import Assets
from valhalla.release.description import Description
from valhalla.ci_provider.git_host import Release


class GitHubValhallaRelease(Release):
    def __init__(self):
        self.api_url = get_api_url()
        self.repo = get_repository_slug()
        self.token = os.getenv('VALHALLA_TOKEN')
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Accept': 'application/vnd.github+json'
            })

    def create(self, description: Description, milestones, release_name: str, tag_name: str, assets: Assets):
        branch = os.environ.get('GITHUB_REF_NAME')
        info(f"Creating release from branch: " + str(branch))

        data = {
            'tag_name': tag_name,
            'name': release_name,
            'body': description.get(),
            'target_commitish': branch,
            'make_latest': 'true'
        }

        info(f"Release data: \n {data}")

        url = f"{self.api_url}/repos/{self.repo}/releases"
        resp = self.session.post(url, json=data)
        if resp.status_code >= 300:
            warn(f"Failed to create release: {resp.status_code} {resp.text}")
            return
        release = resp.json()
        info(f"Created release: {release.get('html_url')}")

        # Assets: GitHub API would require uploads to uploads.github.com; keeping minimal for now.
