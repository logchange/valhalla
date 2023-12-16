import os

import gitlab

from valhalla.ci_provider.get_token import get_valhalla_token
from valhalla.common.logger import info


# For now we have to use oauth_token because CI_JOB_TOKEN
# cannot create MR, cannot push to repo, cannot resolve user ids
# For now GitLab https://gitlab.com/gitlab-org/gitlab/-/issues/389060 cannot push to repo
#

def get_gitlab_client():
    protocol = os.getenv("CI_SERVER_PROTOCOL")
    host = os.getenv("CI_SERVER_HOST")
    port = os.getenv("CI_SERVER_PORT")

    gitlab_url = f"{protocol}://{host}:{port}"
    info("GitLab URL: " + gitlab_url)

    token = get_valhalla_token()

    gl = gitlab.Gitlab(gitlab_url, oauth_token=token)
    return gl


def get_project_id():
    project_id = os.getenv("CI_PROJECT_ID")
    info("GitLab project id: " + project_id)
    return project_id
