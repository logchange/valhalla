import os
from abc import ABC, abstractmethod
from typing import List

from valhalla.common.get_config import MergeRequestConfig
from valhalla.release.assets import Assets
from valhalla.release.description import Description
from valhalla.version.version_to_release import ReleaseKind, VersionToRelease


class Release(ABC):
    @abstractmethod
    def create(self, description: Description, milestones: List[str], release_name: str, tag_name: str, assets: Assets):
        raise NotImplementedError


class MergeRequest(ABC):
    @abstractmethod
    def create(self, merge_request_config: MergeRequestConfig):
        raise NotImplementedError


class VersionToReleaseProvider(ABC):
    @abstractmethod
    def get_from_branch_name(self, release_kinds: List[ReleaseKind]) -> VersionToRelease:
        raise NotImplementedError


class GitHost:
    def __init__(self):
        # Detect and store provider at construction time
        if bool(os.getenv("GITHUB_ACTIONS") or os.getenv("GITHUB_REPOSITORY")):
            self._provider = "github"
        elif bool(os.getenv("GITLAB_CI") or os.getenv("CI_SERVER_HOST")):
            self._provider = "gitlab"
        else:
            raise Exception(
                "Could not detect git host! Are you running in GitHub Actions or GitLab Pipeline? There should be GITHUB_ACTIONS/GITHUB_REPOSITORY or GITLAB_CI/CI_SERVER_HOST environment variable set.")

    def is_github(self) -> bool:
        return self._provider == "github"

    def is_gitlab(self) -> bool:
        return self._provider == "gitlab"

    # Factory helpers as instance methods
    def get_release_impl(self):
        if self.is_github():
            from valhalla.ci_provider.github.release import GitHubValhallaRelease as ReleaseType
        else:
            from valhalla.ci_provider.gitlab.release import GitLabValhallaRelease as ReleaseType
        return ReleaseType

    def create_merge_request(self, merge_request_config: MergeRequestConfig):
        if self.is_github():
            from valhalla.ci_provider.github.merge_request import GitHubValhallaPullRequest as MergeRequestType
        else:
            from valhalla.ci_provider.gitlab.merge_request import GitLabValhallaMergeRequest as MergeRequestType

        merge_request = MergeRequestType()
        return merge_request.create(merge_request_config)

    def get_version_to_release(self, release_kinds: list[ReleaseKind]) -> VersionToRelease:
        if self.is_github():
            from valhalla.ci_provider.github.get_version import \
                GitHubVersionToReleaseProvider as VersionToReleaseProviderType
        else:
            from valhalla.ci_provider.gitlab.get_version import \
                GitLabVersionToReleaseProvider as VersionToReleaseProviderType
        provider = VersionToReleaseProviderType()
        return provider.get_from_branch_name(release_kinds)

    def get_author(self):
        if self.is_github():
            from valhalla.ci_provider.github.common import get_author as gh_get_author
            return gh_get_author()
        else:
            from valhalla.ci_provider.gitlab.common import get_author as gl_get_author
            return gl_get_author()

    def get_branches(self) -> List[str]:
        if self.is_github():
            from valhalla.ci_provider.github.common import GitHubClient
            client = GitHubClient()
            url = f"{client.api_url}/repos/{client.repo}/branches"

            branches = []

            while url:
                resp = client.get(url)
                if resp.status_code >= 300:
                    raise Exception(f"Failed to get branches from GitHub: {resp.status_code} {resp.text}")

                branches.extend([b['name'] for b in resp.json()])

                if 'next' in resp.links:
                    url = resp.links['next']['url']
                else:
                    url = None

            return branches
        else:
            from valhalla.ci_provider.gitlab.common import get_gitlab_client, get_project_id
            gl = get_gitlab_client()
            project_id = get_project_id()
            project = gl.projects.get(project_id)
            branches = project.branches.list(all=True)
            return [b.name for b in branches]

    def get_current_branch(self) -> str:
        if self.is_github():
            return os.environ.get('GITHUB_REF_NAME')
        else:
            return os.environ.get('CI_COMMIT_BRANCH')
