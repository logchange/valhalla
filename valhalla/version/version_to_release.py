import re
import os

from typing import List

from valhalla.common.logger import info, error


class ReleaseKind:

    def __init__(self, filename: str, suffix: str, path: str):
        self.filename = filename
        self.suffix = suffix
        self.path = path

    def __repr__(self):
        return f"filename={self.filename}, suffix={self.suffix}, path={self.path}"


class VersionToRelease:

    def __init__(self, version_number_to_release: str, release_kind: ReleaseKind):
        self.version_number_to_release = version_number_to_release
        self.release_kind = release_kind

    def get_config_file_path(self):
        return self.release_kind.path + "/" + self.release_kind.filename


def get_release_kinds(path: str) -> List[ReleaseKind]:
    info(f"Searching for valhalla*.yml files in: {path}")
    info(f"Current pwd: {os.getcwd()}")

    pattern = re.compile(r'valhalla(.*)\.yml')
    release_kinds = []

    for root, dirs, files in os.walk(path):
        for file in files:
            match = pattern.match(file)
            if match:
                release_kinds.append(ReleaseKind(file, match.group(1), path))

    for kind in release_kinds:
        info(f"Found: {kind}")

    if len(release_kinds) == 0:
        error("Cloud not find any valhalla file! You have to have at least one file matching valhalla*.yml f.e "
              "valhalla.yml. You can define valhalla-hotfix.yml but remember to use release-hotfix-* branch to start"
              "valhalla proces :)")
        exit(-1)

    return release_kinds
