---
title: Levels of detail and the budget
parent: Course export
nav_order: 4
---

# Levels of detail and the budget

The finest level of everything placed around a circuit is several million
triangles. For example, 950 guardrail segments at 960 triangles each and 820 tyre
stacks at 1,400. A city corridor holds over a hundred thousand copies. So every
course export gives the placed models a **triangle budget** and decides, per
model, which level of detail it is drawn at, and, if needed, which copies to leave
out.

The scheme was written for Forza
([`forzaplacement.py`](https://github.com/Holdi601/3DHeat-GameFiles/blob/main/heat3d_gamefiles/forzaplacement.py):
`choose_levels`, `auto_budget`, `_fit`), and BeamNG and AC Rally reuse its parts.
The terrain does not count against the budget.

## Distance bands

Each copy's distance to the driving is measured in the ground plane, to the
nearest lap sample. The lap is thinned to at most 1,000 points first, which costs
a few metres of precision and nothing that matters here. Copies then fall into
three bands, and each (model, band) pair is budgeted separately:

| Band | Distance | Starts at |
|---|---|---|
| near | under 25 m (`NEAR`) | the finest level |
| middle | 25-60 m (`FAR`) | one level coarser |
| far | 60 m and more | the coarsest level |

Without a route (Forza `terrain --box`), distance is measured to the middle of the
box.

## Stepping down to fit

The cost of a (model, band) entry is copies x triangles at its current level.
While the total is over the budget, the entry costing most steps down one level,
and that repeats until the total fits or nothing can step further. Pinned entries
never step:

| Game | Pinned at full detail |
|---|---|
| Forza | kerbs (`road_gen_rum*`) |
| BeamNG | kerbs, and every shape that carries driving surface |
| AC Rally | kerbs |

The Forza summary reports this as
`N of M models drawn at a coarser level to fit the budget`.

## The automatic budget

Without `--detail-budget`, the budget sizes itself so that **no copy is left
out**:

```
budget = max(1,500,000, 1.25 x sum(copies x coarsest level))
```

Pinned entries count at their finest level. The 25% (`HEADROOM`) lets things
beside the road keep some detail. On a country circuit this is the 1.5 million
floor (`DEFAULT_BUDGET`). On a city course, where the corridor holds about 120,000
copies (air conditioners, bicycles, laundry, walls along an expressway), it grows
to about 15 million, and the file to about 660 MB. The viewer loads that.

## A budget you give

`--detail-budget N` is a **ceiling**. Levels step down as above. If even the
coarsest levels do not fit, copies are left out:

| Game | Order copies are left out in |
|---|---|
| Forza | first everything 25 m or more from the driving, then what stands beside the road; within each group, what looks smallest from the road first: largest distance / size (size = the model's bounding-box diagonal times its largest scale, at least 0.25 m) |
| BeamNG | furthest from the driving first |
| AC Rally | furthest from the driving first, as BeamNG |
| Battlefield 6 | smallest first: bounding-box diagonal times scale |

Kerbs (and, for BeamNG, driving-surface models) are never left out, so a budget
smaller than they cost on their own is exceeded by them and by nothing else.

The tool uses distance over size for Forza because, ordered by distance alone, an
air-conditioning unit on a wall nine metres away outlives the twenty-metre facade
it hangs on, twelve metres away. Things beside the road go last whatever their
size, because a three-metre barrier five metres from the line is the edge of the
track, while a fifty-metre building sixty metres back is scenery.

The summary reports
`N of M copies left out to fit the budget, the smallest and furthest from the driving first (--detail-budget raises it)`
(Forza), or `N copies left out to fit the budget, the furthest from the driving first (--detail-budget raises it)`
(BeamNG, AC Rally).

## Whole buildings (Forza)

A whole-building stand-in counts as one copy, at a distance measured to the
building's nearest edge. It is kept or left out as a unit. The modular pieces it
replaces are not budgeted at all. See
[Forza Horizon](course-forza-horizon.md#buildings-drawn-whole).

## What a level of detail is, per game

| Game | Levels come from |
|---|---|
| Forza | the per-triangle level mask of the model's `Mesh` submeshes (bit `level + 1`); `0xFFFF` breakable pieces only for a model with no marked level |
| BeamNG | the `.cdae` shape's `details` with a non-negative size, largest first; for `.dae`, the trailing number on mesh node names (`barrier75`, `barrier40`) |
| AC Rally | the static mesh's stored levels of detail, finest first |
| Battlefield 6 | the MeshSet's levels of detail, finest first, counting only the sections drawn (not the shadow and depth-only copies) |

Battlefield 6's `level` has no lap, so there are no distance bands: each mesh is
one entry, every copy at the same level. The automatic budget is the formula
above with the terrain backdrop pinned; the heightfield is outside the budget
and sized by `--ground-spacing`. Under a budget you give, once every mesh
is at its coarsest, copies are left out smallest first, size being the mesh's
bounding-box diagonal times the copy's scale, since there is no driving to
measure distance from. The terrain backdrop is never left out. A level comes to
about ten million triangles automatically.

## Choosing a number

| You want | Try |
|---|---|
| everything, full detail near the road | leave it automatic |
| a file a few times smaller | `--detail-budget 500000` with `--texture-size 1024` |
| ground only | `--no-placed` (no budget involved) |
