"""Public consistency metrics.

These functions are intentionally small and testable. Reporting code must not
calculate a competing formula; every rendered metric should trace back here.
"""

from __future__ import annotations

from collections.abc import Sequence


def agreement_rate(verdicts: Sequence[bool | None]) -> float | None:
    """Return majority-agreement for comparable two-state verdicts.

    `None` means not comparable and is excluded. If no comparable verdict
    remains, the result is deliberately `None`.
    """

    values = [value for value in verdicts if value is not None]
    if not values:
        return None
    majority = sum(values) >= (len(values) + 1) / 2
    return sum(value == majority for value in values) / len(values)


def jaccard(url_sets: Sequence[set[str] | None]) -> float | None:
    """Return mean pairwise Jaccard similarity for cited URL sets.

    `None` entries represent observations without citations and are excluded.
    Fewer than two comparable observations returns `None`.
    """

    values = [value for value in url_sets if value is not None]
    if len(values) < 2:
        return None
    scores = []
    for index, left in enumerate(values[:-1]):
        for right in values[index + 1 :]:
            scores.append(_safe_pair_jaccard(left, right))
    return sum(scores) / len(scores)


def _safe_pair_jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return 1.0 if not union else len(left & right) / len(union)


def jaccard_union(
    provider_a: Sequence[set[str] | None], provider_b: Sequence[set[str] | None]
) -> float | None:
    """Compare each provider's citation pool using optimistic union semantics.

    If either provider has no citations, coverage similarity is not comparable.
    """

    comparable_a = [value for value in provider_a if value is not None]
    comparable_b = [value for value in provider_b if value is not None]
    if not comparable_a or not comparable_b:
        return None
    if not provider_a or not provider_b:
        return None
    pool_a = set.union(*comparable_a)
    pool_b = set.union(*comparable_b)
    if not pool_a or not pool_b:
        return None
    return _safe_pair_jaccard(pool_a, pool_b)


def jaccard_intersect(
    provider_a: Sequence[set[str] | None], provider_b: Sequence[set[str] | None]
) -> float | None:
    """Pair observations by sample index and exclude non-cited observations."""

    if len(provider_a) != len(provider_b):
        raise ValueError("cross-provider Jaccard requires equal sample counts")
    scores = []
    for left, right in zip(provider_a, provider_b, strict=True):
        if left is None or right is None:
            continue
        scores.append(_safe_pair_jaccard(left, right))
    return sum(scores) / len(scores) if scores else None
