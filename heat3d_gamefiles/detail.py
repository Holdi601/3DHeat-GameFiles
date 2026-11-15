"""
How much detail an export keeps: a triangle budget, a level of detail per model that fits it,
and how far each copy is from the driving. Shared by every game's course and level export.
"""

from __future__ import annotations

import heapq

import numpy as np

#: Triangles for everything placed, before the terrain: the least a budget
#: is. By default it grows past this to whatever keeps every copy in the
#: corridor (see `auto_budget`); given as a number, it is a ceiling.
DEFAULT_BUDGET = 1_500_000

#: What the automatic budget allows beyond keeping every copy at its coarsest:
#: room for the things beside the road to keep some of their detail.
HEADROOM = 1.25


def auto_budget(costs: dict, pinned=()) -> int:
    """
    A budget that keeps every copy: all of them at their coarsest level (kerbs
    at their finest), with `HEADROOM` on top, and never under `DEFAULT_BUDGET`.

    A city corridor is 120,000 copies - air conditioners, bicycles, laundry,
    walls along the expressway - and 11.5 million triangles at their coarsest.
    A fixed 1.5 million left nine in ten of them out; this leaves none out.
    """
    least = sum(
        copies * (levels[0] if name in pinned else levels[-1])
        for name, (copies, levels) in costs.items()
    )
    return max(DEFAULT_BUDGET, int(least * HEADROOM))


#: Copies further than this from the driving start one level coarser, and
#: further than `FAR` at their coarsest. What stands beside the road is what a
#: lap is read against; a building sixty metres back is backdrop.
NEAR = 25.0
FAR = 60.0


def choose_levels(
    costs: dict, budget: int, pinned=(), start: dict | None = None
) -> dict:
    """
    A detail level per model that fits `budget` triangles in all, if it can.

    `costs` is name -> (copies, triangles per level, finest first). The model
    costing most at its current level steps down one, and again, until the total
    fits or nothing can step. `pinned` models stay at their finest; `start`
    gives a level some begin at, which is how distant copies start coarse.
    """
    start = start or {}
    chosen = {
        name: 0 if name in pinned else min(start.get(name, 0), len(levels) - 1)
        for name, (_copies, levels) in costs.items()
    }
    total = sum(copies * levels[chosen[name]] for name, (copies, levels) in costs.items())
    heap = [
        (-copies * levels[chosen[name]], name)
        for name, (copies, levels) in costs.items()
        if name not in pinned and chosen[name] + 1 < len(levels)
    ]
    heapq.heapify(heap)
    while total > budget and heap:
        _cost, name = heapq.heappop(heap)
        copies, levels = costs[name]
        level = chosen[name]
        if level + 1 >= len(levels):
            continue
        saving = copies * (levels[level] - levels[level + 1])
        chosen[name] = level + 1
        total -= saving
        if level + 2 < len(levels):
            heapq.heappush(heap, (-copies * levels[level + 1], name))
    return chosen


def route_distance(points: np.ndarray, route: np.ndarray) -> np.ndarray:
    """
    Distance in the ground plane from each (x, z) point to the nearest route
    point.

    The route is thinned to at most a thousand points first - a library of
    forty laps is seventeen thousand, nearly all of them on top of one another -
    which costs a few metres of precision and nothing that matters to a budget.
    """
    points = np.asarray(points, dtype=np.float64)
    route = np.asarray(route, dtype=np.float64)
    route = route[:: max(1, len(route) // 1000)]
    out = np.empty(len(points))
    for start in range(0, len(points), 2048):
        block = points[start : start + 2048]
        gap = ((block[:, None, :] - route[None, :, :]) ** 2).sum(axis=2)
        out[start : start + 2048] = np.sqrt(gap.min(axis=1))
    return out
