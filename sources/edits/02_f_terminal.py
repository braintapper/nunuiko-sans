"""Glyph edit 2: slight downturn on the f top terminal.

Rule (see GLYPHLOG.md): rotate the free end of the top hook clockwise by
ANGLE about the underside-neck node, so the terminal curls back down a
little. Rotating the cap plus BOTH approach handles about the neck keeps
every SMOOTH joint intact; only the outer arch and inner return reshape
slightly as the end turns down.

Nunito Sans replay: Nunito Sans's f terminal is a STRAIGHT CUT, not
Nunito's round bulb, so Nunito's 7-node round-cap pattern does not exist
here. The cut cap is a 4-node run (curve-smooth neck, two line corners,
line-smooth neck):

  [p-1] offcurve          <- outer approach handle (rotated: keeps p smooth)
  [p]   curve  smooth     <- pivot, underside neck
  [p+1] line              <- cap corner (tip, ~max x)
  [p+2] line              <- cap corner (top)
  [p+3] line   smooth     <- topside neck
  [p+4] offcurve          <- first inner-return handle (rotated: keeps p+3 smooth)

The locator matches this type signature within path 0 only (the f
outline) and takes the highest cap, so fi's separately-drawn hook is
found while its i-dot (path 1, four plain lines) is skipped. In f: p=9;
in fi: p=11. florin has a different terminal (left stock); fl / fl.ss02
are components of f and inherit.

ANGLE re-judged by eye against the straight cut (Nunito's 12 was chosen
against a round terminal). Run once from sources/:
    python3 edits/02_f_terminal.py
"""
import math
import sys

from lib import apply_edit

# roman by default; pass the italic source as argv[1] for the italic pass
GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"
ANGLE_DEG = 10  # clockwise = downturn on the right. Re-judged by eye for
# the straight cut: a cut terminal reads an angle ~1.3x stronger than
# Nunito's round bulb, so 10 here matches the sibling's perceived-subtle
# 12 (12 looked over-hooked at Bold/ExtraBlack; 8 barely read at UI sizes).

# (type, smooth) signature of the cut cap, starting at the pivot p
PATTERN = [("curve", True), ("line", False), ("line", False),
           ("line", True)]


def matches(nodes, p):
    if p - 1 < 0 or p + 4 >= len(nodes):
        return False
    if nodes[p - 1].type != "offcurve" or nodes[p + 4].type != "offcurve":
        return False
    return all(nodes[p + off].type == t and bool(nodes[p + off].smooth) == sm
               for off, (t, sm) in enumerate(PATTERN))


def find_terminal(path0):
    """Highest cut cap within the f outline (path 0)."""
    hits = [p for p in range(len(path0)) if matches(path0, p)]
    assert hits, "cut-cap pattern not found"
    # cap tip = max y over the two line corners p+1,p+2
    return max(hits, key=lambda p: max(path0[p + 1].position.y,
                                       path0[p + 2].position.y))


def rotate_cw(x, y, px, py, deg):
    a = math.radians(deg)
    dx, dy = x - px, y - py
    return (px + dx * math.cos(a) + dy * math.sin(a),
            py - dx * math.sin(a) + dy * math.cos(a))


def edit(mname, layer, nodes):
    path0 = layer.paths[0].nodes           # global indices 0..len-1 (first path)
    p = find_terminal(path0)
    px, py = path0[p].position.x, path0[p].position.y
    new = {}
    for i in (p - 1, p + 1, p + 2, p + 3, p + 4):
        n = path0[i]
        new[i] = rotate_cw(n.position.x, n.position.y, px, py, ANGLE_DEG)
    tip_old = max(path0[p + 1].position.x, path0[p + 2].position.x)
    tip_new = max(new[p + 1][0], new[p + 2][0])
    print(f"{mname:26s} pivot n{p} ({px:.0f},{py:.0f})  "
          f"tip x {tip_old:.0f}->{tip_new:.0f}")
    return {"nodes": new}


if __name__ == "__main__":
    for glyph in ("f", "fi"):
        print(f"--- {glyph}")
        changed = apply_edit(GLYPHS_FILE, glyph, edit)
        assert changed, glyph
    print("done")
