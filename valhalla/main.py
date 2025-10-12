from valhalla.ci_provider.gitlab.common import get_author
from valhalla.ci_provider.get_token import get_valhalla_token
from valhalla.ci_provider.gitlab.get_version import get_version_to_release_from_branch_name
from valhalla.ci_provider.gitlab.merge_request import GitLabValhallaMergeRequest
from valhalla.ci_provider.gitlab.release import GitLabValhallaRelease
from valhalla.commit import before
from valhalla.commit.commit import GitRepository
from valhalla.common.get_config import get_config, CommitConfig, MergeRequestConfig, Config
from valhalla.common.logger import info, error, init_logger
from valhalla.version.release_command import get_version_to_release_from_command
from valhalla.common.resolver import init_str_resolver, init_str_resolver_custom_variables, resolve
from valhalla.release.assets import Assets
from valhalla.release.description import Description
from valhalla.version.version_to_release import get_release_kinds, VersionToRelease
from version.version_to_release import BASE_PREFIX


def start():
    info(f'Release the Valhalla!')

    version_to_release = __version_to_release()
    config = get_config(version_to_release.get_config_file_path())

    if version_to_release.is_version_empty():
        version_to_release.from_config(config)

    if version_to_release.is_version_empty():
        error(f"Version to release is empty, exiting! Create branch with name {BASE_PREFIX}X.X.X or just {BASE_PREFIX}\n"
              f"and define in valhalla.yml version to release. You can also you VALHALLA_RELEASE_CMD to define it.\n"
              f"Check https://logchange.dev/tools/valhalla/ for more info.\n")
        exit(-1)

    info(f'Project version that is going to be released: {version_to_release.version_number_to_release}')

    token = get_valhalla_token()
    author = get_author()
    init_logger(token)

    init_str_resolver(version_to_release.version_number_to_release, token, author)

    init_str_resolver_custom_variables(config.variables)

    commit(config.commit_before_release, token)

    create_release(config, version_to_release.version_number_to_release)

    commit(config.commit_after_release, token)

    create_merge_request(config.merge_request)


def __version_to_release() -> VersionToRelease:
    current_dir = "."
    release_kinds = get_release_kinds(current_dir)
    version_to_release = get_version_to_release_from_command(release_kinds)

    if version_to_release is None:
        version_to_release = get_version_to_release_from_branch_name(release_kinds)

    return version_to_release


def create_merge_request(merge_request_config: MergeRequestConfig):
    if merge_request_config is None:
        info("merge_request not specified in valhalla.yml, skipping")
        return
    if merge_request_config.enabled:
        info("Preparing to create merge request")

        merge_request = GitLabValhallaMergeRequest()
        merge_request.create(merge_request_config)
    else:
        info("merge_request.enabled is False in valhalla.yml, skipping")


def create_release(config: Config, version_to_release: str):
    info("Preparing to create release")
    release = GitLabValhallaRelease()
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


if __name__ == '__main__':
    start()
