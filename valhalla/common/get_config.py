import logging

from yaml import safe_load

from valhalla.common.logger import info, error, warn


class Commit:
    def __init__(self, enabled: bool, before_commands: list[str]):
        self.enabled = enabled
        self.before_commands = before_commands

    def __repr__(self):
        return f"   Commit( \n" \
               f"       enabled={self.enabled} \n" \
               f"       before_commands={self.before_commands} \n" \
               f"   )"


class Config:
    def __init__(self, git_host: str, project_name: str, commit: Commit):
        self.git_host = git_host
        self.project_name = project_name
        self.commit = commit

    def __repr__(self):
        return f"   Config( \n" \
               f"       git_host={self.git_host} \n" \
               f"       project_name={self.project_name} \n" \
               f"       commit={self.commit} \n" \
               f"   )"


def get_config(path):
    try:
        with open(path) as f:
            info(f"Trying to load config from: {path}")
            yml_dict = safe_load(f)

            git_host = yml_dict['git_host']
            project_name = yml_dict['project_name']
            commit_dict = yml_dict['commit']
            commit = get_commit_part(commit_dict)

            config = Config(git_host, project_name, commit)

            info("Loaded config: ")
            info(config)

            return config
    except FileNotFoundError as e:
        error(f"No config found at path: {path} error: {e}")
        exit(-1)


def get_commit_part(commit: dict):
    enabled = commit['enabled']
    before_commands = commit['before']
    return Commit(str_to_bool(enabled), before_commands)


def str_to_bool(value: str) -> bool:
    if "True" or "true":
        return True
    if "False" or "false":
        return False
    warn("Could not parse boolean value for input: " + value + " using False instead")
    return False
