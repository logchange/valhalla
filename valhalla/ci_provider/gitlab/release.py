import os

from valhalla.ci_provider.gitlab.common import get_gitlab_client, get_project_id
from valhalla.common.logger import info
from valhalla.release.assets import Assets
from valhalla.release.description import Description


class GitLabValhallaRelease:
    def __init__(self):
        self.gl = get_gitlab_client()
        self.project = self.gl.projects.get(get_project_id(), lazy=True)

    def create(self, version: str, description: Description, assets: Assets):
        branch = os.environ.get('CI_COMMIT_BRANCH')

        info(f"Creating release from branch: " + branch)

        release = self.project.releases.create(
            {'name': version,
             'tag_name': version,
             'ref': branch,
             'description': description.get(),
             'assets': assets.to_dict()})

        info(f"Created release: " + release._links['self'])
