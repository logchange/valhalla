import os
from typing import List

from valhalla.ci_provider.gitlab.common import get_gitlab_client, get_project_id
from valhalla.common.logger import info
from valhalla.release.assets import Assets
from valhalla.release.description import Description


class GitLabValhallaRelease:
    def __init__(self):
        self.gl = get_gitlab_client()
        self.project = self.gl.projects.get(get_project_id(), lazy=True)

    def create(self, description: Description, milestones: List[str], release_name: str, tag_name: str, assets: Assets):
        branch = os.environ.get('CI_COMMIT_BRANCH')

        info(f"Creating release from branch: " + branch)

        data = {'name': release_name,
                'tag_name': tag_name,
                'ref': branch,
                'description': description.get(),
                'milestones': milestones,
                'assets': assets.to_dict()}

        info(f"Release data: \n {data}")

        release = self.project.releases.create(data)

        info(f"Created release: " + release._links['self'])
