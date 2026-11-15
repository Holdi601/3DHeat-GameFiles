"""The documentation's diagrams. Edit a label here, then run `python tools/docs_diagrams.py --strings`.
See diagram_engine.py for the options (--lang draws a translated set)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from diagram_engine import CARD, INK, LINE, SUB, W, esc, run, steps, legend, svg, text  # noqa: E402


def lap_to_course():
    title = "A lap goes in, the track around it comes out"
    out = [text(20, 32, title, 18, "600", anchor="start")]
    # left: the lap, a dotted line
    out.append('<rect x="20" y="52" width="330" height="200" rx="8" fill="#ffffff" stroke="#8a94a3"/>')
    out.append('<path d="M60,210 C90,90 170,80 200,140 S300,220 320,90" fill="none" stroke="#d9534f" '
               'stroke-width="4" stroke-dasharray="2 9" stroke-linecap="round"/>')
    out.append(text(185, 280, "lap.json: where you drove", 15, "600"))
    # arrow
    out.append('<path d="M370,152 H480" stroke="#8a94a3" stroke-width="3" fill="none"/>'
               '<path d="M480,144 L496,152 L480,160 z" fill="#8a94a3"/>')
    out.append(text(432, 140, "course", 15, "600", mono=True))
    # right: the course, grass + road + kerbs + barrier
    out.append('<rect x="510" y="52" width="330" height="200" rx="8" fill="#9bbf6a" stroke="#8a94a3"/>')
    road = "M550,210 C580,90 660,80 690,140 S790,220 810,90"
    out.append(f'<path d="{road}" fill="none" stroke="#c8b48a" stroke-width="40" stroke-linecap="round"/>')
    out.append(f'<path d="{road}" fill="none" stroke="#55595f" stroke-width="28" stroke-linecap="round"/>')
    out.append(f'<path d="{road}" fill="none" stroke="#f1f1f1" stroke-width="1.5" stroke-dasharray="10 10"/>')
    out.append('<path d="M548,110 C560,80 590,64 620,66" fill="none" stroke="#d9534f" stroke-width="5" stroke-dasharray="6 6"/>')
    out.append('<path d="M700,215 C730,232 770,230 790,210" fill="none" stroke="#5f6670" stroke-width="5"/>')
    out.append(text(675, 280, "course.glb: road, verge, kerbs, barriers", 15, "600"))
    out.append(text(20, 312, "The lap only says where to look; the shapes come from the game's own files.", 14,
                    fill=SUB, anchor="start"))
    return svg(W, 330, title, out)


DIAGRAMS = {
    "lap-to-course.svg": lap_to_course,
    "where-it-fits.svg": lambda: steps("Where GameFiles fits", [
        ("Installed game", "the files it ships", "(.pak, .utoc, .toc, zip ...)"),
        ("3DHeat GameFiles", "course, level, ue-map,", "enfusion-world, cars"),
        ("One .glb", "the game's own", "coordinates"),
        ("3DHeat viewer", "Level panel: your heat", "lies on the level"),
    ], per_row=2),
    "detail-budget.svg": lambda: steps("--detail-budget: fitting placed models under a triangle ceiling", [
        ("Every copy", "at the detail its distance asks:", "<25 m / 25-60 m / >60 m"),
        ("Over budget?", "the costliest models", "drop one level"),
        ("Still over?", "repeat down to", "the coarsest level"),
        ("Still over?", "the furthest copies", "are left out"),
    ], per_row=2, notes=[("Kerbs", "always stay at full detail", "(not part of the budget)")]),
    "ue-map-steps.svg": lambda: steps("ue-map: an Unreal 5 World Partition map", [
        ("ue-maps <game>", "lists maps with", "World Partition cells"),
        ("Landscape", "component heights,", "--ground-spacing"),
        ("HLOD meshes", "merged buildings", "(--no-structures)"),
        ("Water bodies", "above the ground", "(--no-water)"),
        ("<map>.glb", "Unreal centimetres,", "Y up"),
    ]),
    "glb-parts.svg": lambda: legend("Parts in the .glb: the node name says what each is", [
        ("#6f8f4e", "ground:terrain", "the land; per tile or 512 m square"),
        ("#55595f", "ground:road", "the driving surface"),
        ("#c8b48a", "ground:verge", "the edge of the road"),
        ("#d9534f", "ground:kerbs", "kerbs, always full detail"),
        ("#f1f1f1", "ground:markings", "painted lines"),
        ("#8a8f99", "structure:barriers", "barriers, tyre walls"),
        ("#b07a4f", "structure:buildings", "buildings and what stands on the ground"),
        ("#4a90d9", "water:<name>", "water"),
        ("#5cb85c", "nav:walkable", "Battlefield 6 --navmesh: where a soldier can stand"),
    ], note="The swatch colours are illustrative; the viewer chooses how each kind is drawn."),
}

if __name__ == "__main__":
    run(DIAGRAMS, os.path.join(os.path.dirname(__file__), ".."))
