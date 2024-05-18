import os
from typing import List

from valhalla.common.logger import info, error
from valhalla.version.version_to_release import VersionToRelease, ReleaseKind

BASE_PREFIX = "release-"


def get_version_to_release(release_kinds: List[ReleaseKind]) -> VersionToRelease:
    ci_commit_branch = os.environ.get('CI_COMMIT_BRANCH')

    if ci_commit_branch:
        info(f'Name of branch is: {ci_commit_branch}')

        if ci_commit_branch.startswith('release-'):

            # first we search for specific release kinds
            for release_kind in release_kinds:
                if release_kind.suffix != "":
                    prefix = __get_branch_prefix(release_kind)
                    if ci_commit_branch.startswith(prefix):
                        return __matched(ci_commit_branch, prefix, release_kind)

            # now if specific release kind not found we search for main
            for release_kind in release_kinds:
                if release_kind.suffix == "":
                    prefix = BASE_PREFIX
                    if ci_commit_branch.startswith(prefix):
                        return __matched(ci_commit_branch, prefix, release_kind)

            __no_matching_release_kind(ci_commit_branch, release_kinds)

        else:
            error('This is not a release branch! This script should not be run! The name of the branch must be '
                  'release-X.X.X')
            error('Check valhalla configration and manual !')
            exit(-1)
    else:
        error('CI_COMMIT_BRANCH environment variable is not set. Are you using GitLab CI? If not change your '
              'valhalla configration!')
        exit(-1)


def __get_branch_prefix(release_kind: ReleaseKind) -> str:
    prefix = (BASE_PREFIX + release_kind.suffix).replace("--", "-")
    if prefix.endswith("-"):
        return prefix
    else:
        return prefix + "-"


def __matched(ci_commit_branch: str, prefix: str, release_kind: ReleaseKind) -> VersionToRelease:
    info(f"Branch name {ci_commit_branch} has prefix {prefix} and matches with release kind {release_kind}")
    project_version = ci_commit_branch[len(prefix):]
    info(f'Project version that is going to be released: {project_version}')
    return VersionToRelease(project_version, release_kind)


def __no_matching_release_kind(ci_commit_branch: str, release_kinds: List[ReleaseKind]):
    error('This is a release branch, but valhalla could not find matching valhalla.yml file!')
    error(f'Name of branch is: {ci_commit_branch}')
    for kind in release_kinds:
        error(f'Available release kind: {kind}')
        prefix = __get_branch_prefix(kind)
        error(f'To match this release kind you branch must starts with {prefix} f.e {prefix}1.5.3')

    error('Create branch name with correct prefix to the release kind that you want to match with and start!')
    exit(-1)
