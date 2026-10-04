from __future__ import annotations

from typing import Callable, Optional

from valhalla.common.resolver import resolve


class MergeRequestHook:
    """
    Simple hook returned after creating a Merge Request (or Pull Request).

    - id: identifier of the created MR/PR
    - add_comment: method to add a comment to the created MR/PR
    - enable_auto_merge: method to let the git host merge the MR/PR once approvals and checks pass

    If creation is skipped, use MergeRequestHook.Skip which prints info that MR was not created.
    """

    def __init__(self, mr_id: Optional[int], add_comment_impl: Optional[Callable[[str], None]] = None,
                 enable_auto_merge_impl: Optional[Callable[[], None]] = None):
        self.id = mr_id
        self._add_comment_impl = add_comment_impl
        self._enable_auto_merge_impl = enable_auto_merge_impl

    def add_comment(self, comment: str):
        if self._add_comment_impl is None:
            return
        self._add_comment_impl(resolve(comment))

    def enable_auto_merge(self):
        if self._enable_auto_merge_impl is None:
            return
        self._enable_auto_merge_impl()

    @classmethod
    def Skip(cls) -> "MergeRequestHook":
        # No MR created, provide a hook that only logs on add_comment
        return cls(None, None)
