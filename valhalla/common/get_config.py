from typing import List
from yaml import safe_load

from valhalla.common.logger import info, error, warn
from valhalla.extends.ValhallaExtends import ValhallaExtends


class MergeRequestConfig:
    def __init__(self, enabled: bool, target_branch: str, title: str, description: str, reviewers: List[str]):
        self.enabled = enabled
        self.target_branch = target_branch
        self.title = title
        self.description = description
        self.reviewers = reviewers

    def __repr__(self):
        return f"\n" \
               f"   MergeRequestConfig( \n" \
               f"     enabled={self.enabled} \n" \
               f"     target_branch={self.target_branch} \n" \
               f"     title={self.title} \n" \
               f"     description={self.description} \n" \
               f"     reviewers={self.reviewers} \n" \
               f"   )"


class CommitConfig:
    def __init__(self, enabled: bool, git_username: str, git_email: str, msg: str, before_commands: List[str]):
        self.enabled = enabled
        self.git_username = git_username
        self.git_email = git_email
        self.msg = msg
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
    def __init__(self,
                 variables: dict,
                 git_host: str,
                 commit_before_release: CommitConfig,
                 release_config: ReleaseConfig,
                 commit_after_release: CommitConfig,
                 merge_request: MergeRequestConfig):
        self.variables = variables
        self.git_host = git_host
        self.commit_before_release = commit_before_release
        self.release_config = release_config
        self.commit_after_release = commit_after_release
        self.merge_request = merge_request

    def __repr__(self):
        return f" Config( \n" \
               f"   variables={self.variables} \n" \
               f"   git_host={self.git_host} \n" \
               f"   commit_before_release={self.commit_before_release} \n" \
               f"   release_config={self.release_config} \n" \
               f"   commit_after_release={self.commit_after_release} \n" \
               f"   merge_request={self.merge_request} \n" \
               f" )"


def get_config(path) -> Config:
    try:
        with open(path) as f:
            info(f"Trying to load config from: {path}")
            yml_dict = safe_load(f)

            extends_list = get_from_dict(yml_dict, 'extends', False)
            extends = ValhallaExtends(extends_list)
            yml_dict = extends.merge(yml_dict)

            variables = get_from_dict(yml_dict, 'variables', False)

            git_host = yml_dict['git_host']

            commit_before_release_dict = yml_dict['commit_before_release']
            commit_before_release = get_commit_part(commit_before_release_dict)

            release_config_dict = yml_dict['release']
            release_config = get_release_config_part(release_config_dict)

            commit_after_release_dict = get_from_dict(yml_dict, 'commit_after_release', False)
            commit_after_release = get_commit_part(commit_after_release_dict)

            merge_request_dict = get_from_dict(yml_dict, 'merge_request', False)
            merge_request = get_merge_request_part(merge_request_dict)

            config = Config(
                variables,
                git_host,
                commit_before_release,
                release_config,
                commit_after_release,
                merge_request
            )

            info("Loaded config: ")
            info(config)

            return config
    except FileNotFoundError as e:
        error(f"No config found at path: {path} error: {e}")
        exit(-1)


def get_commit_part(commit_config_dict: dict) -> CommitConfig:
    enabled = str_to_bool(get_from_dict(commit_config_dict, 'enabled', True))
    commit_other_options_required = enabled

    git_username = get_from_dict(commit_config_dict, 'username', False)
    git_email = get_from_dict(commit_config_dict, 'email', False)
    msg = get_from_dict(commit_config_dict, 'msg', commit_other_options_required)

    before_commands = get_from_dict(commit_config_dict, 'before', commit_other_options_required)
    return CommitConfig(enabled, git_username, git_email, msg, before_commands)


def get_release_config_part(release_config_dict: dict) -> ReleaseConfig:
    description_dict = release_config_dict['description']
    description = get_release_description_config_part(description_dict)

    assets_dict = get_from_dict(release_config_dict, 'assets', False)
    assets = get_release_assets_config_part(assets_dict)

    return ReleaseConfig(description, assets)


def get_release_description_config_part(description_dict: dict) -> ReleaseDescriptionConfig:
    from_command = description_dict['from_command']
    return ReleaseDescriptionConfig(from_command)


def get_release_assets_config_part(assets_dict: dict) -> ReleaseAssetsConfig:
    if assets_dict is None:
        return ReleaseAssetsConfig([])
    
    links_dict = assets_dict['links']
    links = get_release_assets_links_config_part(links_dict)

    return ReleaseAssetsConfig(links)


def get_release_assets_links_config_part(links_list_of_dicts: List[dict]) -> List[ReleaseAssetsLinkConfig]:
    result = []

    if links_list_of_dicts is None:
        return result

    for link_dict in links_list_of_dicts:
        name = link_dict['name']
        url = link_dict['url']
        link_type = link_dict['link_type']

        result.append(ReleaseAssetsLinkConfig(name, url, link_type))

    return result


def get_merge_request_part(merge_request_dict: dict) -> MergeRequestConfig:
    enabled = str_to_bool(get_from_dict(merge_request_dict, 'enabled', True))
    merge_request_other_options_required = enabled

    target_branch = get_from_dict(merge_request_dict, 'target_branch', False)

    title = get_from_dict(merge_request_dict, 'title', merge_request_other_options_required)
    description = get_from_dict(merge_request_dict, 'description', False)

    reviewers = get_from_dict(merge_request_dict, 'reviewers', False)
    return MergeRequestConfig(enabled, target_branch, title, description, reviewers)


def str_to_bool(value: str) -> bool:
    if "True" or "true":
        return True
    if "False" or "false":
        return False
    warn("Could not parse boolean value for input: " + value + " using False instead")
    return False


def get_from_dict(d: dict, key: str, required: bool):
    try:
        return d[key]
    except KeyError as e:
        if required:
            print(e)
            error(f"Missing required {key} in valhalla.yml!")
            exit(1)
        else:
            info(f"Could not find optional filed: {key}")
            return None
