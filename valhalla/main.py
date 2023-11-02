from valhalla.before_commit import before_commit
from valhalla.ci_provider.gitlab.get_version import get_version_number_to_release
from valhalla.common.get_config import get_config
from valhalla.model.project import Project


def start():
    print(f'Release the Valhalla!')
    version_to_release = get_version_number_to_release()
    config = get_config("./valhalla.yml")
    project = Project(config.project_name, version_to_release)
    before_commit.execute(config.before_commit_commands)


if __name__ == '__main__':
    start()
