"""Glyph edit 1: shorten the tail/foot of lowercase l.

Rule (see GLYPHLOG.md): compress the tail region horizontally toward the
stem's right edge (the pivot) by FACTOR (x' = pivot + FACTOR*(x - pivot),
y untouched). Affine in x, so collinearity — and every SMOOTH joint —
is preserved exactly. Advance width shrinks by the tail tip's retreat;
anchors `bottom` and `dot` (which sit in the tail zone) follow the same
compression, `top`/`topright`/`center` stay.

Nunito Sans replay: Nunito Sans's l is a DIFFERENT outline from Nunito's
(16 nodes, single path, straight-cut terminal — not Nunito's 26-node
round bulb). Landmarks re-derived from its own topology (asserted):
  - node 10 = stem top-right corner  -> pivot x = stem right edge
  - node 11 = stem top-left corner   (both at the ascender top y)
  - node  3 = terminal tip           (max x)
The tail = every node with x > pivot (terminal cut + inner sweep + outer
bottom curve); the stem/top/left nodes all sit at x <= pivot.

Nunito's 1b round-corner restore does NOT port: Nunito Sans's terminal is
a hard cut (node 3 is a corner, not a round quarter-arc), so plain
compression is enough — verified by eye on the size ramp.

Italic pass: the compression pivot is the stem's RIGHT edge, which is a
clean vertical only in upright space — on a slanted stem it is a diagonal.
So the whole edit runs in DESLANTED space (shear x by -tan(9deg)*y so the
stem becomes vertical), then results are reslanted. The tail top cut is
horizontal even in italic (nodes 10/11 share y), so the y-landmarks hold.
Roman is the s=0 case (deslant is identity) — unchanged behaviour.

Text-surgery via lib.apply_edit (glyphsLib read-only; its save drops
kerning groups / feature code). Run once from sources/ (roman default;
pass the italic source as argv[1] for the italic pass):
    python3 edits/01_l_tail.py [NunuikoDisplay-Italic.glyphs]
"""
import math
import sys

from lib import apply_edit

# roman by default; pass the italic source as argv[1] for the italic pass
GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"
GLYPH = "l"
FACTOR = 0.6
EXPECTED_NODE_COUNT = 16
STEM_TR, STEM_TL = 10, 11   # stem top-right / top-left landmark nodes
MOVE_ANCHORS = {"bottom", "dot"}
SLANT = math.tan(math.radians(9))


def edit(mname, layer, nodes):
    assert len(layer.paths) == 1, (mname, "expected single path")
    assert len(nodes) == EXPECTED_NODE_COUNT, (mname, len(nodes))

    s = SLANT if "Italic" in mname else 0.0
    de = lambda x, y: (x - s * y, y)          # deslant -> upright space
    re_ = lambda x, y: (x + s * y, y)         # reslant -> italic space
    D = [de(n.position.x, n.position.y) for n in nodes]   # deslanted coords

    top_y = max(y for _, y in D)
    (trx, tryy), (tlx, tly) = D[STEM_TR], D[STEM_TL]
    assert nodes[STEM_TR].type == "line" and nodes[STEM_TL].type == "line", (
        mname, "stem top not lines")
    assert tryy == top_y == tly, (mname, "stem top not at max y")
    assert trx > tlx, (mname, "node 10 not the right corner")
    pivot = trx   # stem right edge, vertical in deslanted space

    compress = lambda x: pivot + FACTOR * (x - pivot)
    # tail = every node right of the stem (terminal cut + inner sweep +
    # outer bottom curve); compress its x toward the pivot, then reslant.
    new_nodes = {i: re_(compress(x), y) for i, (x, y) in enumerate(D)
                 if x > pivot}

    # preserve RSB: shrink advance by the retreat of the rightmost ink
    # point, measured in actual (slanted) coordinates
    max_before = max(n.position.x for n in nodes)
    max_after = max(re_(compress(x) if x > pivot else x, y)[0] for x, y in D)
    new_width = round(layer.width - (max_before - max_after))

    anchors = {}
    for a in layer.anchors:
        if a.name not in MOVE_ANCHORS:
            continue
        ax, ay = de(a.position.x, a.position.y)
        if ax > pivot:
            anchors[a.name] = re_(compress(ax), ay)

    print(f"{mname:26s} pivot={pivot:.0f} maxx {max_before:.0f}->{max_after:.0f} "
          f"width {layer.width:g}->{new_width}")
    return {"nodes": new_nodes, "width": new_width, "anchors": anchors}


if __name__ == "__main__":
    changed = apply_edit(GLYPHS_FILE, GLYPH, edit)
    assert changed, "nothing changed — already applied?"
    print("written", GLYPHS_FILE)
