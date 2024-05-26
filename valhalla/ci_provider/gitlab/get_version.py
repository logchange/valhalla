import os
from typing import List

from valhalla.common.logger import info, error
from valhalla.version.version_to_release import VersionToRelease, ReleaseKind, BASE_PREFIX, \
    get_version_to_release_from_str


def get_version_to_release(release_kinds: List[ReleaseKind]) -> VersionToRelease:
    ci_commit_branch = os.environ.get('CI_COMMIT_BRANCH')

    if ci_commit_branch:
        info(f'Name of branch is: {ci_commit_branch}')

        if ci_commit_branch.startswith(BASE_PREFIX):
            return get_version_to_release_from_str(ci_commit_branch, release_kinds)
        else:
            error('This is not a release branch! This script should not be run! The name of the branch must be '
                  'release-X.X.X')
            error('Check valhalla configration and manual !')
            exit(-1)
    else:
        error('CI_COMMIT_BRANCH environment variable is not set. Are you using GitLab CI? If not change your '
              'valhalla configration!')
        exit(-1)
