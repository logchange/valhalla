import os
from typing import List

from valhalla.ci_provider.gitlab.common import get_gitlab_client, get_project_id
from valhalla.common.get_config import MergeRequestConfig
from valhalla.common.logger import info, warn
from valhalla.common.resolver import resolve


def get_description(description: str):
    if not description:
        info("merge_request.description not specified, using default")
        return "Created by Valhalla! Visit https://github.com/logchange/valhalla and leave a star!"

    return description


class GitLabValhallaMergeRequest:
    def __init__(self):
        self.gl = get_gitlab_client()
        self.project = self.gl.projects.get(get_project_id(), lazy=True)

    def create(self, merge_request_config: MergeRequestConfig):
        branch = os.environ.get('CI_COMMIT_BRANCH')
        default_branch = os.environ.get('CI_DEFAULT_BRANCH')

        info(f"Creating merge request from {branch} to {default_branch}")

        if not merge_request_config.description:
            info("merge_request.description not specified, using default")

        mr = self.project.mergerequests.create(
            {
                'source_branch': branch,
                'target_branch': default_branch,
                'title': resolve(merge_request_config.title),
                'description': resolve(get_description(merge_request_config.description)),
                'remove_source_branch': True,
                'reviewer_ids': self.__get_reviewer_ids(merge_request_config.reviewers)
            }
        )

        info(f"Created merge request: " + mr.web_url)

    def __get_reviewer_ids(self, reviewers: List[str]) -> List[int]:
        result = []

        for rev in reviewers:
            try:
                user = self.gl.users.list(username=rev)[0]
                rev_id = int(user.id)
                info(f"Adding reviewer: {rev} with id {rev_id}")
                result.append(rev_id)
            except IndexError:
                warn(f"Could not find username: {rev}")

        return result
