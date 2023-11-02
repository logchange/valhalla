import os

from valhalla.common.logger import info, error


def get_version_number_to_release() -> str:
    ci_commit_branch = os.environ.get('CI_COMMIT_BRANCH')

    if ci_commit_branch:
        info(f'Name of branch is: {ci_commit_branch}')

        if ci_commit_branch.startswith('release-'):
            project_version = ci_commit_branch[len('release-'):]
            info(f'Project version that is going to be released: {project_version}')
            return project_version
        else:
            error('This is not a release branch! This script should not be run! The name of the branch must be release-X.X.X')
            error('Check valhalla configration and manual !')
            exit(-1)
    else:
        error('CI_COMMIT_BRANCH environment variable is not set. Are you using GitLab CI? If not change your '
              'valhalla configration')
        exit(-1)
