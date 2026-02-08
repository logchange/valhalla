from __future__ import annotations

from typing import Callable, Optional


class MergeRequestHook:
    """
    Simple hook returned after creating a Merge Request (or Pull Request).

    - id: identifier of the created MR/PR
    - add_comment: method to add a comment to the created MR/PR

    If creation is skipped, use MergeRequestHook.Skip which prints info that MR was not created.
    """

    def __init__(self, mr_id: Optional[int], add_comment_impl: Optional[Callable[[str], None]] = None):
        self.id = mr_id
        self._add_comment_impl = add_comment_impl

    def add_comment(self, comment: str):
        if self._add_comment_impl is None:
            return
        self._add_comment_impl(comment)

    @classmethod
    def Skip(cls) -> "MergeRequestHook":
        # No MR created, provide a hook that only logs on add_comment
        return cls(None, None)
