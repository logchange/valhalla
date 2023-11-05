from git import Repo

from valhalla.common.logger import info


class GitRepository:
    def __init__(self):
        self.repository = Repo.init(".")

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

    def commit(self, msg: str, add=True):
        self.status()

        if add:
            if self.repository.is_dirty():
                untracked = self.repository.untracked_files
                for f in untracked:
                    self.repository.index.add(f)
                    info(f"{f} added to stage")
        else:
            info(f"add={add}, skipping adding untracked files")

        self.repository.index.commit(msg)
        self.status()

    def push(self):
        origin = self.repository.remote('origin')
        origin.push()


# if __name__ == '__main__':
#     git_repo = GitRepository()
#     git_repo.commit("testing commiting")
