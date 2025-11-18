import os
import glob

from valhalla.ci_provider.git_host import Release
from valhalla.ci_provider.github.common import GitHubClient
from valhalla.common.logger import info, warn
from valhalla.release.assets import Assets
from valhalla.release.description import Description


def expand_file_patterns(patterns):
    """
    Takes a list of string patterns (e.g., ["./bins/*.zip"])
    and returns a list of (filename, full_path) tuples.
    """
    results = []

    for pattern in patterns:
        for path in glob.glob(pattern):
            full_path = os.path.abspath(path)
            filename = os.path.basename(full_path)
            results.append((filename, full_path))

    return results


class GitHubValhallaRelease(Release):
    def __init__(self):
        self.client = GitHubClient()
        self.repo = self.client.repo

    def create(self, description: Description, milestones, release_name: str, tag_name: str, assets: Assets):
        branch = os.environ.get('GITHUB_REF_NAME')
        info(f"Creating release from branch: " + str(branch))

        data = {
            'tag_name': tag_name,
            'name': release_name,
            'body': description.get(),
            'target_commitish': branch,
            'make_latest': 'true'
        }

        info(f"Release data: \n {data}")

        url = f"{self.client.api_url}/repos/{self.repo}/releases"
        resp = self.client.post(url, json=data)
        if resp.status_code >= 300:
            warn(f"Failed to create release: {resp.status_code} {resp.text}")
            return
        release = resp.json()
        info(f"Created release: {release.get('html_url')}")

        self.__upload_files(assets, release)

    def __upload_files(self, assets: Assets, release_response):
        files = assets.get_files()

        if not files:
            info("No files to upload")
            return

        upload_url_tmpl = release_response.get('upload_url')
        if not upload_url_tmpl:
            info("No upload_url provided by GitHub API response; skipping asset uploads.")
            return

        # Strip the template part {...}
        # "upload_url": "https://uploads.github.com/repos/octocat/Hello-World/releases/1/assets{?name,label}",
        # https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#create-a-release
        upload_base = upload_url_tmpl.split('{')[0]
        info(f"Uploading files to {upload_base}")

        for name, path in expand_file_patterns(files):
            params = {'name': name}
            content_type = Assets.guess_mime(path)
            info(f"Uploading asset '{name}' from '{path}' with content-type '{content_type}'")
            with open(path, 'rb') as f:
                resp_up = self.client.session.post(upload_base, params=params, headers={'Content-Type': content_type},
                                                   data=f)
            if resp_up.status_code >= 300:
                warn(f"Failed to upload asset '{name}': {resp_up.status_code} {resp_up.text}")
            else:
                info(f"Uploaded asset '{name}'")
