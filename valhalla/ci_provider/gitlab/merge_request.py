import os
from typing import List

from valhalla.ci_provider.gitlab.common import get_gitlab_client, get_project_id
from valhalla.common.get_config import MergeRequestConfig
from valhalla.common.logger import info, warn
from valhalla.common.resolver import resolve
from valhalla.ci_provider.git_host import MergeRequest


def get_description(description: str):
    if not description:
        info("merge_request.description not specified, using default")
        return "Created by Valhalla! Visit https://github.com/logchange/valhalla and leave a star!"

    return description


class GitLabValhallaMergeRequest(MergeRequest):
    def __init__(self):
        self.gl = get_gitlab_client()
        self.project = self.gl.projects.get(get_project_id(), lazy=True)

    def create(self, merge_request_config: MergeRequestConfig):
        source_branch = os.environ.get('CI_COMMIT_BRANCH')

        if merge_request_config.target_branch:
            info("Target branch for merge request:")
            target_branch = resolve(merge_request_config.target_branch)
        else:
            info("target_branch not set, using default instead")
            target_branch = os.environ.get('CI_DEFAULT_BRANCH')

        info(f"Creating merge request from {source_branch} to {target_branch}")

        if not merge_request_config.description:
            info("merge_request.description not specified, using default")

        mr = self.project.mergerequests.create(
            {
                'source_branch': source_branch,
                'target_branch': target_branch,
                'title': resolve(merge_request_config.title),
                'description': resolve(get_description(merge_request_config.description)),
                'remove_source_branch': True,
                'reviewer_ids': self.__get_reviewer_ids(merge_request_config.reviewers)
            }
        )

        info(f"Created merge request: " + mr.web_url)

    def __get_reviewer_ids(self, reviewers: List[str]) -> List[int]:
        result = []

        if not reviewers:
            warn("Reviewers list is None or empty")
            return result

        for rev in reviewers:
            try:
                user = self.gl.users.list(username=rev)[0]
                rev_id = int(user.id)
                info(f"Adding reviewer: {rev} with id {rev_id}")
                result.append(rev_id)
            except IndexError:
                warn(f"Could not find username: {rev}")

        return result
