import gitlab
import os

from valhalla.common.logger import info
from valhalla.release.assets import Assets
from valhalla.release.description import Description


# For now GitLab https://gitlab.com/gitlab-org/gitlab/-/issues/389060 cannot push to repo
#
class ValhallaRelease:
    def __init__(self):
        protocol = os.getenv("CI_SERVER_PROTOCOL")
        host = os.getenv("CI_SERVER_HOST")
        port = os.getenv("CI_SERVER_PORT")
        project_id = os.getenv("CI_PROJECT_ID")

        gitlab_url = f"{protocol}://{host}:{port}"
        info("GitLab URL: " + gitlab_url)
        info("GitLab project id: " + project_id)

        # for production use
        # gl = gitlab.Gitlab(gitlab_url, job_token=os.getenv("CI_JOB_TOKEN"))
        # for testing locally
        gl = gitlab.Gitlab(gitlab_url, oauth_token=os.getenv("CI_JOB_TOKEN"))

        self.project = gl.projects.get(project_id, lazy=True)

    def create(self, version: str, description: Description, assets: Assets):
        branch = os.environ.get('CI_COMMIT_BRANCH')

        info(f"Creating release from branch: " + branch)

        release = self.project.releases.create(
            {'name': version,
             'tag_name': version,
             'ref': branch,
             'description': description.get(),
             'assets': assets.to_dict()})

        info(f"Created release: " + version)
        release.pprint()
