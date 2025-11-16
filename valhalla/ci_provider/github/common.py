import os
import requests

from valhalla.common.logger import info
from valhalla.ci_provider.get_token import get_valhalla_token


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


class GitHubClient:
    def __init__(self):
        self.api_url = get_api_url()
        self.repo = get_repository_slug()
        self.token = get_valhalla_token()
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Accept': 'application/vnd.github+json'
            })
        else:
            raise Exception("No token found! Could not authenticate with GitHub!")

    def post(self, url: str, json=None):
        return self.session.post(url, json=json)