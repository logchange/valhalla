from typing import List, Any

from valhalla.ci_provider.git_host import GitHost
from valhalla.version.version_to_release import BASE_PREFIX


def get_other_release_in_progress(git_host: GitHost) -> list[Any]:
    branches = git_host.get_branches()

    current_branch = git_host.get_current_branch()

    other_releases = []
    for branch in branches:
        if branch.startswith(BASE_PREFIX) and branch != current_branch:
            other_releases.append(branch)

    if not other_releases:
        return []

    return other_releases
