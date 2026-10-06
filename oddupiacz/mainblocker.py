"""Decides whether a push updates a protected branch and whether the user confirmed it."""

from .models import PushRef

_HEADS_PREFIX = "refs/heads/"


def parse_push_refs(stdin_text: str) -> list[PushRef]:
    """
    Parse the ref list git writes to a pre-push hook's stdin.

    Args:
        stdin_text: Raw stdin from the pre-push hook

    Returns:
        One PushRef per well-formed line. Blank and malformed lines are skipped.
    """
    refs = []
    for line in stdin_text.splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        refs.append(
            PushRef(
                local_ref=parts[0],
                local_sha=parts[1],
                remote_ref=parts[2],
                remote_sha=parts[3],
            )
        )
    return refs


def find_protected_refs(refs: list[PushRef], protected_branches: list[str]) -> list[str]:
    """
    Return bare branch names whose remote ref is protected.

    Args:
        refs: Ref updates from the push
        protected_branches: Branch names that require confirmation

    Returns:
        Protected branch names present in the push, in input order.
        Matching uses the remote ref, so pushing another local branch
        onto main or master is still caught.
    """
    protected = set(protected_branches)
    found = []
    for ref in refs:
        if not ref.remote_ref.startswith(_HEADS_PREFIX):
            continue
        branch = ref.remote_ref.removeprefix(_HEADS_PREFIX)
        if branch in protected:
            found.append(branch)
    return found


def is_confirmed(answer: str, repo_name: str) -> bool:
    """
    Return whether the typed answer is exactly the repository name.

    Args:
        answer: Text the user typed
        repo_name: Repository directory name that must be matched

    Returns:
        True only on an exact match
    """
    return answer == repo_name
