import os

from valhalla.common.logger import info


def get_repository_slug() -> str:
    # format: owner/repo
    repo = os.getenv("GITHUB_REPOSITORY", "")
    info("GitHub repository: " + repo)
    return repo


def get_author():
    author = os.getenv("GITHUB_ACTOR")
    info(f"Author: {author}")
    return author


def get_api_url() -> str:
    # Allow GHES via GITHUB_API_URL, fallback to public
    return os.getenv("GITHUB_API_URL", "https://api.github.com")


def get_default_branch_fallback() -> str:
    # If GitHub doesn't provide base, use common default
    return os.getenv("GITHUB_DEFAULT_BRANCH", "main")
