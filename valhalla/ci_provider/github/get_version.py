import os
from typing import List

from valhalla.common.logger import info, error
from valhalla.version.version_to_release import VersionToRelease, ReleaseKind, BASE_PREFIX, \
    get_version_to_release_from_str
from valhalla.ci_provider.git_host import VersionToReleaseProvider


class GitHubVersionToReleaseProvider(VersionToReleaseProvider):
    def get_from_branch_name(self, release_kinds: List[ReleaseKind]) -> VersionToRelease:
        # In GitHub Actions, branch name is available under GITHUB_REF_NAME
        ref_name = os.environ.get('GITHUB_REF_NAME')

        if ref_name:
            info(f'Name of branch is: {ref_name}')

            if ref_name.startswith(BASE_PREFIX):
                return get_version_to_release_from_str(ref_name, release_kinds)
            else:
                error('This is not a release branch! This script should not be run! The name of the branch must be '
                      f'{BASE_PREFIX}X.X.X or just {BASE_PREFIX} if you want to use version from command')
                error('Check valhalla configuration and manual !')
                exit(-1)
        else:
            error('GITHUB_REF_NAME environment variable is not set. Are you using GitHub Actions? If not change your '
                  'valhalla configuration!')
            exit(-1)


def get_version_to_release_from_branch_name(release_kinds: List[ReleaseKind]) -> VersionToRelease:
    # Backward compatible wrapper
    return GitHubVersionToReleaseProvider().get_from_branch_name(release_kinds)
