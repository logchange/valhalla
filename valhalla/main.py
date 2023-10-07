from valhalla.ci_provider.gitlab.get_version import get_version
from valhalla.common.get_config import get_config


def start():
    # Use a breakpoint in the code line below to debug your script.
    print(f'Release the Valhalla!')  # Press Ctrl+F8 to toggle the breakpoint.
    version = get_version()
    config = get_config("./valhalla.yml")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start()

