import sys

from valhalla.ci_provider.get_token import get_valhalla_token
from valhalla.ci_provider.git_host import GitHost
from valhalla.ci_provider.merge_request_hook import MergeRequestHook
from valhalla.commit import before
from valhalla.commit.commit import GitRepository
from valhalla.common.checks import get_other_release_in_progress
from valhalla.common.get_config import get_config, CommitConfig, MergeRequestConfig, Config
from valhalla.common.logger import info, error, init_logger, init_logger_mr_hook
from valhalla.common.resolver import init_str_resolver, init_str_resolver_set_version, \
    init_str_resolver_custom_variables, resolve
from valhalla.release.assets import Assets
from valhalla.release.description import Description
from valhalla.version.release_command import get_version_to_release_from_command
from valhalla.version.version_to_release import BASE_PREFIX
from valhalla.version.version_to_release import get_release_kinds, VersionToRelease


def print_help():
    msg = (
        "🌌 valhalla is a toolkit designed to streamline the release of new versions of software 🌌\n"
        "\n"
        "Usage:\n"
        "  valhalla            Start the release process (same as 'valhalla start').\n"
        "  valhalla start      Start the release process.\n"
        "  valhalla -h, --help Show this help and exit.\n"
        "\n"
        "Docs: https://logchange.dev/tools/valhalla/\n"
        "\n"
        "Notes:\n"
        "- The 'valhalla' command starts the process by detecting the release version,\n"
        "  reading configuration (valhalla.yml), creating a release and optionally a\n"
        "  merge request.\n"
        "- You can also provide the 'start' subcommand, which does exactly the same as\n"
        "  running 'valhalla' without arguments.\n"
    )
    print(msg)


def main():
    argv = sys.argv[1:]

    if not argv:
        # Default behavior: start the process
        start()
        return

    if argv[0] in ("-h", "--help"):
        print_help()
        return

    if argv[0] == "start":
        start()
        return

    # Unknown command -> print help and exit with error
    print("Unknown command: {}".format(argv[0]))
    print_help()
    sys.exit(1)


def start():
    info(f'Release the Valhalla!')

    git_host = GitHost()

    token = get_valhalla_token()
    author = git_host.get_author()
    init_logger(token)
    init_str_resolver(token, author)

    version_to_release = __version_to_release(git_host)
    config = get_config(version_to_release.get_config_file_path())
    init_str_resolver_custom_variables(config.variables)

    if version_to_release.is_version_empty():
        version_to_release.from_config(config)

    if version_to_release.is_version_empty():
        error(
            f"Version to release is empty, exiting! Create branch with name {BASE_PREFIX}X.X.X or just {BASE_PREFIX}\n"
            f"and define in valhalla.yml version to release. You can also you VALHALLA_RELEASE_CMD to define it.\n"
            f"Check https://logchange.dev/tools/valhalla/ for more info.\n")
        exit(-1)

    info(f'Project version that is going to be released: {version_to_release.version_number_to_release}')
    init_str_resolver_set_version(version_to_release.version_number_to_release)

    mr_hook = create_merge_request(git_host, config.merge_request)
    init_logger_mr_hook(mr_hook)

    other_release = get_other_release_in_progress(git_host)
    if other_release:
        error(
            f"Cannot have more than one release in progress at the same time because it leads to inconsistencies and conflicts!\n"
            f"Other releases in progress: {other_release}. You should merge changes from previous releases and delete branches. CC @{{AUTHOR}}")
        exit(-1)

    mr_hook.add_comment(
        f"⏳ Release proces of version {version_to_release.version_number_to_release} has begun! Please wait.")

    commit(config.commit_before_release, token)

    create_release(git_host, config, version_to_release.version_number_to_release)

    commit(config.commit_after_release, token)

    mr_hook.add_comment(f"✅ Release successful! Now wait for tagged version to be build. CC @{{AUTHOR}}")


def __version_to_release(git_host: GitHost) -> VersionToRelease:
    current_dir = "."
    release_kinds = get_release_kinds(current_dir)
    version_to_release = get_version_to_release_from_command(release_kinds)

    if version_to_release is None:
        version_to_release = git_host.get_version_to_release(release_kinds)

    return version_to_release


def create_merge_request(git_host: GitHost, merge_request_config: MergeRequestConfig | None) -> MergeRequestHook:
    if merge_request_config is None:
        info("merge_request not specified in valhalla.yml, skipping")
        return MergeRequestHook.Skip()
    if merge_request_config.enabled:
        info("Preparing to create merge request")
        return git_host.create_merge_request(merge_request_config)
    else:
        info("merge_request.enabled is False in valhalla.yml, skipping")
        return MergeRequestHook.Skip()


def create_release(git_host: GitHost, config: Config, version_to_release: str):
    info("Preparing to create release")
    ReleaseImpl = git_host.get_release_impl()
    release = ReleaseImpl()
    description = Description(config.release_config.description_config)
    assets = Assets(config.release_config.assets_config)

    if config.release_config is not None and config.release_config.milestones is not None:
        milestones = list(map(resolve, config.release_config.milestones))
    else:
        milestones = []

    if config.release_config is not None and config.release_config.name is not None:
        release_name = resolve(config.release_config.name)
    else:
        release_name = version_to_release

    if config.tag_config is not None and config.tag_config.name is not None:
        tag_name = resolve(config.tag_config.name)
    else:
        tag_name = version_to_release

    release.create(description, milestones, release_name, tag_name, assets)
    info("Finished creating release")


def commit(commit_config: CommitConfig, token: str):
    if commit_config is None:
        info("Commit config is missing, skipping scripts to execute, commit, push!")
        return

    if commit_config.enabled:
        info("Commit enabled is True so scripts, commit, push will be performed")

        before.execute(commit_config.before_commands)
        git = GitRepository(commit_config.git_username, commit_config.git_email)
        commit_success = git.commit(commit_config.msg)

        if commit_success:
            info("Commit successful, preparing to push")
            git.push(token)
            info("Pushed successful!")

    else:
        info("Commit disabled(enabled: False), skipping  scripts to execute, commit, push!")
