from valhalla.ci_provider.get_token import get_token
from valhalla.commit import before
from valhalla.ci_provider.gitlab.get_version import get_version_number_to_release
from valhalla.commit.commit import GitRepository
from valhalla.common.get_config import get_config
from valhalla.common.logger import info
from valhalla.model.project import Project


def start():
    print(f'Release the Valhalla!')
    version_to_release = get_version_number_to_release()
    config = get_config("./valhalla.yml")
    project = Project(config.project_name, version_to_release)

    if config.commit.enabled:
        info("Commit enabled is True so scripts, commit, push will be performed")
        before.execute(config.commit.before_commands)
        git = GitRepository(config.commit.git_username, config.commit.git_email)
        git.commit(f"Releasing version {project.version}")
        token = get_token()
        git.push(token)
        info("Pushed successful!")
    else:
        info("Commit disabled(enabled: False), skipping  scripts, commit, push")


if __name__ == '__main__':
    start()
