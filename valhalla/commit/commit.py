from git import Repo

import os

from valhalla.common.logger import info, warn
from valhalla.common.resolver import resolve


class GitRepository:
    def __init__(self, git_username, git_email):
        self.repository = Repo.init(".")

        if not git_username:
            info("Git username not set, using default valhalla-bot")
            git_username = "valhalla-bot"

        if not git_email:
            info("Git email not set, using default valhalla-bot@logchange.dev")
            git_email = "valhalla-bot@logchange.dev"

        self.repository.config_writer().set_value("user", "name", git_username).release()
        self.repository.config_writer().set_value("user", "email", git_email).release()

    def status(self):
        info("----------------------")
        info("Git status")

        untracked = self.repository.untracked_files
        for f in untracked:
            info(f"{f} is untracked")

        diffs = self.repository.index.diff(None)
        for d in diffs:
            info(f"{d.a_path} is modified")

        info("----------------------")

    def commit(self, msg: str, add=True) -> bool:
        self.status()

        new_changes_in_stage = False

        if add:
            untracked = self.repository.untracked_files
            for f in untracked:
                if self.__is_ignored(f):
                    warn(f"Skipping untracked file: {f} check your .gitignore! see: https://github.com/logchange/valhalla/blob/master/README.md#-gitignore")
                else:
                    self.repository.git.add(f)
                    info(f"Untracked file: {f} added to stage")
                    new_changes_in_stage = True
        else:
            info(f"add={add}, skipping adding untracked files")

        modified = self.repository.index.diff(None)
        for f in modified:
            self.repository.git.add(f.a_path)
            info(f"Modified file: {f.a_path} added to stage")
            new_changes_in_stage = True

        if not new_changes_in_stage:
            warn("There is noting to commit!")
            return False

        msg += " [VALHALLA SKIP]"
        commit = self.repository.index.commit(resolve(msg))
        info(f"Created commit: {commit}")
        self.status()
        return True

    def push(self, token):
        info("Preparing to push")
        branch = self.repository.active_branch

        info(f"Current branch: {branch}")

        self.repository.git.push(self.__get_push_url(token), str(branch))
        info("Performed push")

    def __get_push_url(self, token):
        origin = self.repository.remote(name='origin')
        remote_url = origin.url
        info(f"Remote url: {remote_url}")
        remote_url = remote_url.replace("https://", "").replace("http://", "")
        trimmed_url = remote_url.split('@')[-1] if '@' in remote_url else remote_url
        info(f"trimmed_url: {trimmed_url}")
        push_url = "https://{}:{}@{}".format("valhalla-bot", token, trimmed_url)
        info(f"push_url: {push_url}")
        return push_url
    
    def __is_ignored(self, file_path: str) -> bool:
        if file_path.startswith(".m2/"):
            return True
        return False