from yaml import safe_load

from valhalla.common.logger import info, error


class Config:
    def __init__(self, git_host: str, project_name: str, before_commit_commands: list[str]):
        self.git_host = git_host
        self.project_name = project_name
        self.before_commit_commands = before_commit_commands

    def __repr__(self):
        return f"   Config( \n" \
               f"       git_host={self.git_host} \n" \
               f"       project_name={self.project_name} \n" \
               f"       before_commit_commands={self.before_commit_commands} \n" \
               f"   )"


def get_config(path):
    try:
        with open(path) as f:
            info(f"Trying to load config from: {path}")
            yml_dict = safe_load(f)

            git_host = yml_dict['git_host']
            project_name = yml_dict['project_name']
            before_commit_commands = yml_dict['before_commit']

            config = Config(git_host, project_name, before_commit_commands)

            info("Loaded config: ")
            info(config)

            return config
    except FileNotFoundError as e:
        error(f"No config found at path: {path}")
        exit(-1)
