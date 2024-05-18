from valhalla.ci_provider.get_token import get_valhalla_token
from valhalla.ci_provider.gitlab.get_version import get_version_to_release
from valhalla.ci_provider.gitlab.merge_request import GitLabValhallaMergeRequest
from valhalla.ci_provider.gitlab.release import GitLabValhallaRelease
from valhalla.commit import before
from valhalla.commit.commit import GitRepository
from valhalla.common.get_config import get_config, CommitConfig, MergeRequestConfig, Config
from valhalla.common.logger import info, init_logger
from valhalla.common.resolver import init_str_resolver, init_str_resolver_custom_variables
from valhalla.release.assets import Assets
from valhalla.release.description import Description
from valhalla.version.version_to_release import get_release_kinds


def start():
    print(f'Release the Valhalla!')

    release_kinds = get_release_kinds(".")

    version_to_release = get_version_to_release(release_kinds)
    token = get_valhalla_token()
    init_logger(token)

    init_str_resolver(version_to_release.version_number_to_release, token)

    config = get_config(version_to_release.get_config_file_path())
    init_str_resolver_custom_variables(config.variables)

    commit(config.commit_before_release, token)

    create_release(config, version_to_release.version_number_to_release)

    commit(config.commit_after_release, token)

    create_merge_request(config.merge_request)


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
    release.create(version_to_release, description, assets)
    info("Finished creating release")


def commit(commit_config: CommitConfig, token: str):
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
        info("Commit disabled(enabled: False), skipping  scripts, commit, push!")


if __name__ == '__main__':
    start()
