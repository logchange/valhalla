from valhalla.ci_provider.gitlab.get_version import get_version


def start():
    # Use a breakpoint in the code line below to debug your script.
    print(f'Release the Valhalla!')  # Press Ctrl+F8 to toggle the breakpoint.
    version = get_version()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start()

