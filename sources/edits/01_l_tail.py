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

Text-surgery via lib.apply_edit (glyphsLib read-only; its save drops
kerning groups / feature code). Run once from sources/:
    python3 edits/01_l_tail.py
"""
from lib import apply_edit

GLYPHS_FILE = "NunuikoDisplay.glyphs"
GLYPH = "l"
FACTOR = 0.6
EXPECTED_NODE_COUNT = 16
STEM_TR, STEM_TL = 10, 11   # stem top-right / top-left landmark nodes
MOVE_ANCHORS = {"bottom", "dot"}


def compress(x, pivot):
    return pivot + FACTOR * (x - pivot)


def edit(mname, layer, nodes):
    assert len(layer.paths) == 1, (mname, "expected single path")
    assert len(nodes) == EXPECTED_NODE_COUNT, (mname, len(nodes))

    top_y = max(n.position.y for n in nodes)
    tr, tl = nodes[STEM_TR], nodes[STEM_TL]
    assert tr.type == "line" and tl.type == "line", (mname, "stem top not lines")
    assert tr.position.y == top_y == tl.position.y, (mname, "stem top not at max y")
    assert tr.position.x > tl.position.x, (mname, "node 10 not the right corner")
    pivot = tr.position.x

    # tail tip = rightmost ink; which node holds it varies by master (the
    # 6pt cut bulges at the bottom-right node, not the top corner) — take
    # the max directly. Compression is monotonic in x, so the max-x node is
    # unchanged and tip_new = compress(tip_old).
    tip_old = max(n.position.x for n in nodes)

    new_nodes = {i: (compress(n.position.x, pivot), n.position.y)
                 for i, n in enumerate(nodes) if n.position.x > pivot}
    tip_new = compress(tip_old, pivot)
    new_width = round(layer.width - (tip_old - tip_new))

    anchors = {a.name: (compress(a.position.x, pivot), a.position.y)
               for a in layer.anchors
               if a.name in MOVE_ANCHORS and a.position.x > pivot}

    print(f"{mname:26s} pivot={pivot:g} tip {tip_old:g}->{tip_new:.0f} "
          f"width {layer.width:g}->{new_width}  "
          f"ext {tip_old - pivot:.0f}->{tip_new - pivot:.0f}")
    return {"nodes": new_nodes, "width": new_width, "anchors": anchors}


if __name__ == "__main__":
    changed = apply_edit(GLYPHS_FILE, GLYPH, edit)
    assert changed, "nothing changed — already applied?"
    print("written", GLYPHS_FILE)
