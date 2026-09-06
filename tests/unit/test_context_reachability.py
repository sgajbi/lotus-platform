"""The reachability helper must be able to say no, and must actually traverse.

Four documentation assertions now rest on subject_is_reachable. If it returned
True indiscriminately -- by scanning the whole repository, or by an empty-set
`any` inversion -- all four would pass while proving nothing, which is the
failure mode of every guard that is only ever tested on what it accepts.
"""

from __future__ import annotations

from context_reachability import (
    REPO_CONTEXT,
    documents_reachable_from_repo_context,
    subject_is_reachable,
)


def test_a_subject_that_appears_nowhere_is_not_reachable() -> None:
    assert not subject_is_reachable("Kfz9Qm-subject-that-does-not-exist-anywhere")


def test_a_subject_is_reachable_through_a_linked_index() -> None:
    # Owned by context/LOTUS-ENGINEERING-CONTEXT.md, not by the repository
    # context, and reached from it by following one link.
    assert subject_is_reachable("Data Mesh Standard")


def test_reachability_traverses_links_rather_than_scanning_the_repository() -> None:
    """With no hops allowed, only the repository context itself counts.

    This is what separates traversal from a repository-wide grep: a subject the
    context does not name must be unreachable at zero hops and reachable once
    its index is followed.
    """
    at_zero_hops = documents_reachable_from_repo_context(max_hops=0)

    assert at_zero_hops == {REPO_CONTEXT}
    assert not subject_is_reachable("Data Mesh Standard", max_hops=0)
    assert subject_is_reachable("Data Mesh Standard", max_hops=1)


def test_more_hops_reach_at_least_as_much() -> None:
    one_hop = documents_reachable_from_repo_context(max_hops=1)
    two_hops = documents_reachable_from_repo_context(max_hops=2)

    assert one_hop <= two_hops
    assert len(two_hops) > len(one_hop), "the second hop reaches nothing new"
