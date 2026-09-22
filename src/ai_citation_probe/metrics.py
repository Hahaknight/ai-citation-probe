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
            union = left | right
            scores.append(1.0 if not union else len(left & right) / len(union))
    return sum(scores) / len(scores)
