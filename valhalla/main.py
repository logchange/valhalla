from valhalla.before_commit import before_commit
from valhalla.ci_provider.gitlab.get_version import get_version
from valhalla.common.get_config import get_config
from valhalla.model.project import Project


def start():
    # Use a breakpoint in the code line below to debug your script.
    print(f'Release the Valhalla!')  # Press Ctrl+F8 to toggle the breakpoint.
    version = get_version()
    config = get_config("./valhalla.yml")
    project = Project(config.project_name, version)
    before_commit.execute(config.before_commit_commands);

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start()

