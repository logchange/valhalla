import os
import time
from typing import List

from git import Repo
from gitlab.exceptions import GitlabError

from valhalla.ci_provider.git_host import MergeRequest
from valhalla.ci_provider.gitlab.common import get_gitlab_client, get_project_id
from valhalla.common.get_config import MergeRequestConfig
from valhalla.common.logger import info, warn
from valhalla.common.resolver import resolve
from valhalla.ci_provider.merge_request_hook import MergeRequestHook


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
                'description': resolve(merge_request_config.description),
                'remove_source_branch': True,
                'reviewer_ids': self.__get_reviewer_ids(merge_request_config.reviewers)
            }
        )

        info(f"Created merge request: " + mr.web_url)

        mr_iid = getattr(mr, 'iid', None)

        def _add_comment(comment: str):
            try:
                mr_obj = self.project.mergerequests.get(mr_iid, iid=True)
                mr_obj.notes.create({'body': comment})
            except Exception as e:
                warn(f"Could not add comment to merge request because: {e}")

        def _enable_auto_merge():
            mr_obj = None
            try:
                head_sha = Repo('.').head.commit.hexsha
                mr_obj = self.project.mergerequests.get(mr_iid, iid=True)
                # GitLab refreshes the MR and creates its pipeline asynchronously after push; enabling auto-merge
                # before that (or without sha) makes GitLab abort it with "source branch was updated" or reject it
                # with 405, because without a pipeline there is nothing to wait for and it tries to merge right away
                for _ in range(60):
                    if (mr_obj.sha == head_sha and
                            (getattr(mr_obj, 'head_pipeline', None) or {}).get('sha') == head_sha and
                            getattr(mr_obj, 'detailed_merge_status', None) not in ('checking', 'preparing', 'unchecked')):
                        break
                    time.sleep(2)
                    mr_obj = self.project.mergerequests.get(mr_iid, iid=True)
                else:
                    warn("Pipeline for merge request did not start in time, trying to enable auto-merge anyway")
                for attempt in range(3):
                    try:
                        mr_obj.merge(sha=head_sha, merge_when_pipeline_succeeds=True)
                        break
                    except GitlabError as e:
                        if e.response_code != 405 or attempt == 2:
                            raise
                        time.sleep(5)
                        mr_obj = self.project.mergerequests.get(mr_iid, iid=True)
                info("Auto-merge enabled, merge request will be merged when approvals and pipeline succeed")
            except Exception as e:
                status = getattr(mr_obj, 'detailed_merge_status', 'unknown')
                warn(f"Could not enable auto-merge for merge request because: {e} (detailed_merge_status: {status})")

        return MergeRequestHook(mr_iid, _add_comment, _enable_auto_merge if merge_request_config.auto_merge else None)

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
