import os
from typing import List

from valhalla.common.logger import info, error
from valhalla.version.version_to_release import ReleaseKind, VersionToRelease, BASE_PREFIX, \
    get_version_to_release_from_str


def get_version_to_release_from_command(release_kinds: List[ReleaseKind]) -> VersionToRelease | None:
    command = os.environ.get('VALHALLA_RELEASE_CMD')

    if command:
        info(f'Value of VALHALLA_RELEASE_CMD is: {command}')

        if command.startswith(BASE_PREFIX):
            return get_version_to_release_from_str(command, release_kinds)
        else:
            error(
                f'This is not a correct release command! VALHALLA_RELEASE_CMD should start from {BASE_PREFIX} prefix, f.e. {BASE_PREFIX}1.2.3')
            exit(-1)
    else:
        info("Cloud not find VALHALLA_RELEASE_CMD environment variable, skipping and going to check branch name")
        return None
