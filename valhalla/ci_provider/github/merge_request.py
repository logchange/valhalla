import os
import requests

from valhalla.ci_provider.github.common import get_repository_slug, get_api_url, get_default_branch_fallback
from valhalla.common.get_config import MergeRequestConfig
from valhalla.common.logger import info, warn
from valhalla.common.resolver import resolve


def _get_description(description: str):
    if not description:
        info("merge_request.description not specified, using default")
        return "Created by Valhalla! Visit https://github.com/logchange/valhalla and leave a star!"

    return description


class GitHubValhallaPullRequest:
    def __init__(self):
        self.api_url = get_api_url()
        self.repo = get_repository_slug()
        self.token = os.getenv('VALHALLA_TOKEN')
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Accept': 'application/vnd.github+json'
            })

    def create(self, merge_request_config: MergeRequestConfig):
        source_branch = os.environ.get('GITHUB_REF_NAME')

        if merge_request_config.target_branch:
            info("Target branch for pull request:")
            target_branch = resolve(merge_request_config.target_branch)
        else:
            info("target_branch not set, using default instead")
            # GitHub doesn't expose default branch in env by default. Use fallback env or main.
            target_branch = get_default_branch_fallback()

        info(f"Creating pull request from {source_branch} to {target_branch}")

        title = resolve(merge_request_config.title)
        description = resolve(_get_description(merge_request_config.description))

        url = f"{self.api_url}/repos/{self.repo}/pulls"
        payload = {
            'title': title,
            'head': source_branch,
            'base': target_branch,
            'body': description
        }

        resp = self.session.post(url, json=payload)
        if resp.status_code >= 300:
            warn(f"Failed to create pull request: {resp.status_code} {resp.text}")
            return

        pr = resp.json()
        info(f"Created pull request: {pr.get('html_url')}")

        reviewers = merge_request_config.reviewers or []
        if reviewers:
            self.__request_reviewers(pr.get('number'), reviewers)

    def __request_reviewers(self, pr_number: int, reviewers):
        try:
            url = f"{self.api_url}/repos/{self.repo}/pulls/{pr_number}/requested_reviewers"
            payload = {"reviewers": reviewers}
            resp = self.session.post(url, json=payload)
            if resp.status_code >= 300:
                warn(f"Could not add reviewers: {resp.status_code} {resp.text}")
            else:
                info(f"Requested reviewers: {', '.join(reviewers)}")
        except Exception as e:
            warn(f"Error while requesting reviewers: {e}")


def __get_description(description: str):
    if not description:
        info("merge_request.description not specified, using default")
        return "Created by Valhalla! Visit https://github.com/logchange/valhalla and leave a star!"

    return description
