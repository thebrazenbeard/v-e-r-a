from __future__ import annotations

from collections import Counter, defaultdict
from math import log2
from typing import Hashable, Iterable


def _materialize(x: Iterable[Hashable]) -> list[Hashable]:
    return list(x)


def entropy(values: Iterable[Hashable]) -> float:
    vals = _materialize(values)
    if not vals:
        return 0.0
    counts = Counter(vals)
    n = len(vals)
    return -sum((c / n) * log2(c / n) for c in counts.values())


def mutual_information(x: Iterable[Hashable], y: Iterable[Hashable]) -> float:
    xs, ys = _materialize(x), _materialize(y)
    if len(xs) != len(ys):
        raise ValueError("x and y must have the same length")
    if not xs:
        return 0.0

    joint = Counter(zip(xs, ys))
    cx, cy = Counter(xs), Counter(ys)
    n = len(xs)
    mi = 0.0
    for (a, b), c in joint.items():
        pxy = c / n
        px = cx[a] / n
        py = cy[b] / n
        mi += pxy * log2(pxy / (px * py))
    return max(0.0, mi)


def conditional_mutual_information(
    x: Iterable[Hashable],
    y: Iterable[Hashable],
    given: Iterable[Hashable],
) -> float:
    """I(X;Y|Z), exactly for discrete observations.

    Useful for testing whether an acoustic channel carries information about an
    outcome after conditioning on speaker, device, context, or interaction phase.
    """
    xs, ys, zs = _materialize(x), _materialize(y), _materialize(given)
    if not (len(xs) == len(ys) == len(zs)):
        raise ValueError("x, y, and given must have the same length")
    if not xs:
        return 0.0

    groups: dict[Hashable, list[int]] = defaultdict(list)
    for i, z in enumerate(zs):
        groups[z].append(i)

    n = len(xs)
    total = 0.0
    for idxs in groups.values():
        gx = [xs[i] for i in idxs]
        gy = [ys[i] for i in idxs]
        total += (len(idxs) / n) * mutual_information(gx, gy)
    return max(0.0, total)
