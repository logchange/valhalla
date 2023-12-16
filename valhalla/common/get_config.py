from typing import List
from yaml import safe_load

from valhalla.common.logger import info, error, warn


class Commit:
    def __init__(self, enabled: bool, git_username: str, git_email: str, before_commands: List[str]):
        self.enabled = enabled
        self.git_username = git_username
        self.git_email = git_email
        self.before_commands = before_commands

    def __repr__(self):
        return f"\n" \
               f"   Commit( \n" \
               f"     enabled={self.enabled} \n" \
               f"     git_username={self.git_username} \n" \
               f"     git_email={self.git_email} \n" \
               f"     before_commands={self.before_commands} \n" \
               f"   )"


class ReleaseAssetsLinkConfig:
    def __init__(self, name: str, url: str, link_type: str):
        self.name = name
        self.url = url
        self.link_type = link_type

    def __repr__(self):
        return f"\n" \
               f"   ReleaseAssetsLinkConfig( \n" \
               f"           name={self.name} \n" \
               f"           url={self.url} \n" \
               f"           link_type={self.link_type} \n" \
               f"   )"


class ReleaseAssetsConfig:
    def __init__(self, links: List[ReleaseAssetsLinkConfig]):
        self.links = links

    def __repr__(self):
        return f"\n" \
               f"   ReleaseAssetsConfig( \n" \
               f"           links={self.links} \n" \
               f"   )"


class ReleaseDescriptionConfig:
    def __init__(self, from_command: str):
        self.from_command = from_command

    def __repr__(self):
        return f"\n" \
               f"   ReleaseDescriptionConfig( \n" \
               f"           from_command={self.from_command} \n" \
               f"   )"


class ReleaseConfig:
    def __init__(self, description_config: ReleaseDescriptionConfig, assets_config: ReleaseAssetsConfig):
        self.description_config = description_config
        self.assets_config = assets_config

    def __repr__(self):
        return f"\n" \
               f"   ReleaseConfig( \n" \
               f"           description_config={self.description_config} \n" \
               f"           assets_config={self.assets_config} \n" \
               f"   )"


class Config:
    def __init__(self, git_host: str, commit: Commit, release_config: ReleaseConfig):
        self.git_host = git_host
        self.commit = commit
        self.release_config = release_config

    def __repr__(self):
        return f" Config( \n" \
               f"   git_host={self.git_host} \n" \
               f"   commit={self.commit} \n" \
               f"   release_config={self.release_config} \n" \
               f" )"


def get_config(path):
    try:
        with open(path) as f:
            info(f"Trying to load config from: {path}")
            yml_dict = safe_load(f)

            git_host = yml_dict['git_host']

            commit_dict = yml_dict['commit']
            commit = get_commit_part(commit_dict)

            release_config_dict = yml_dict['release']
            release_config = get_release_config_part(release_config_dict)

            config = Config(git_host, commit, release_config)

            info("Loaded config: ")
            info(config)

            return config
    except FileNotFoundError as e:
        error(f"No config found at path: {path} error: {e}")
        exit(-1)


def get_commit_part(commit: dict) -> Commit:
    enabled = commit['enabled']
    git_username = commit['username']
    git_email = commit['email']
    before_commands = commit['before']
    return Commit(str_to_bool(enabled), git_username, git_email, before_commands)


def get_release_config_part(release_config_dict: dict) -> ReleaseConfig:
    description_dict = release_config_dict['description']
    description = get_release_description_config_part(description_dict)

    assets_dict = release_config_dict['assets']
    assets = get_release_assets_config_part(assets_dict)

    return ReleaseConfig(description, assets)


def get_release_description_config_part(description_dict: dict) -> ReleaseDescriptionConfig:
    from_command = description_dict['from_command']
    return ReleaseDescriptionConfig(from_command)


def get_release_assets_config_part(assets_dict: dict) -> ReleaseAssetsConfig:
    links_dict = assets_dict['links']
    links = get_release_assets_links_config_part(links_dict)

    return ReleaseAssetsConfig(links)


def get_release_assets_links_config_part(links_list_of_dicts: List[dict]) -> List[ReleaseAssetsLinkConfig]:
    result = []

    for link_dict in links_list_of_dicts:
        name = link_dict['name']
        url = link_dict['url']
        link_type = link_dict['link_type']

        result.append(ReleaseAssetsLinkConfig(name, url, link_type))

    return result


def str_to_bool(value: str) -> bool:
    if "True" or "true":
        return True
    if "False" or "false":
        return False
    warn("Could not parse boolean value for input: " + value + " using False instead")
    return False
