import re
import os

from typing import List

from valhalla.common.logger import info, error

BASE_PREFIX = "release-"


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


def get_version_to_release_from_str(value: str, release_kinds: List[ReleaseKind]) -> VersionToRelease:
    info(f"Analyzing {value} to match release kind")
    # first we search for specific release kinds
    for release_kind in release_kinds:
        if release_kind.suffix != "":
            prefix = __get_branch_prefix(release_kind)
            if value.startswith(prefix):
                return __matched(value, prefix, release_kind)

    info(f"{value} doesn't match specific release kind, checking main kind")
    # now if specific release kind not found we search for main
    for release_kind in release_kinds:
        if release_kind.suffix == "":
            prefix = BASE_PREFIX
            if value.startswith(prefix):
                return __matched(value, prefix, release_kind)

    __no_matching_release_kind(value, release_kinds)


def __get_branch_prefix(release_kind: ReleaseKind) -> str:
    prefix = (BASE_PREFIX + release_kind.suffix).replace("--", "-")
    if prefix.endswith("-"):
        return prefix
    else:
        return prefix + "-"


def __matched(value: str, prefix: str, release_kind: ReleaseKind) -> VersionToRelease:
    info(
        f"Branch name or VALHALLA_RELEASE_CMD is {value} and has prefix {prefix} and matches with release kind {release_kind}")
    project_version = value[len(prefix):]
    info(f'Project version that is going to be released: {project_version}')
    return VersionToRelease(project_version, release_kind)


def __no_matching_release_kind(value: str, release_kinds: List[ReleaseKind]):
    error(
        'This is a release branch or VALHALLA_RELEASE_CMD was used, but valhalla could not find matching valhalla.yml file!')
    error(f'Name of branch or VALHALLA_RELEASE_CMD is: {value}')
    for kind in release_kinds:
        error(f'Available release kind: {kind}')
        prefix = __get_branch_prefix(kind)
        error(
            f'To match this release kind your branch or VALHALLA_RELEASE_CMD must starts with {prefix} f.e {prefix}1.5.3')

    error(
        'Create branch or use VALHALLA_RELEASE_CMD with correct prefix to the release kind that you want to match with and start!')
    exit(-1)
