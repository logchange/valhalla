import os


def is_github() -> bool:
    return bool(os.getenv("GITHUB_ACTIONS") or os.getenv("GITHUB_REPOSITORY"))


def is_gitlab() -> bool:
    return bool(os.getenv("GITLAB_CI") or os.getenv("CI_SERVER_HOST"))


def get_provider() -> str:
    if is_github():
        return "github"
    return "gitlab"
