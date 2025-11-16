import os

from valhalla.ci_provider.github.common import GitHubClient
from valhalla.common.logger import info, warn
from valhalla.release.assets import Assets
from valhalla.release.description import Description
from valhalla.ci_provider.git_host import Release


class GitHubValhallaRelease(Release):
    def __init__(self):
        self.client = GitHubClient()
        self.repo = self.client.repo

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

        url = f"{self.client.api_url}/repos/{self.repo}/releases"
        resp = self.client.post(url, json=data)
        if resp.status_code >= 300:
            warn(f"Failed to create release: {resp.status_code} {resp.text}")
            return
        release = resp.json()
        info(f"Created release: {release.get('html_url')}")

        # Assets: GitHub API would require uploads to uploads.github.com; keeping minimal for now.
