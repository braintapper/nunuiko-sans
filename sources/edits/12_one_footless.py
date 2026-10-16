"""Glyph edit 12: 1 without the foot (bottom horizontal stroke).

Nunito Sans already draws a footless 1 as a stylistic alternate (one.ss01,
one.tosf.ss01: stem + flag, recentred in the 600 tabular width). Make it
the default by SWAPPING outlines: one <-> one.ss01 and one.tosf <->
one.tosf.ss01. ss01 now gives the footed 1, so it stays available.

one.dnom (fractions; one.numr, onesuperior, oneinferior, onehalf,
onequarter are built from it) has no footless alternate, so its foot is
removed by rule. 12 nodes: 0,1 / 10,11 are the foot ends, 2 and 9 where
the stem meets the foot top. Keep 2..9 and extend the stem edges (lines
3->2 and 8->9, which follows the slant in the italic) down to the
baseline.

Centring (user: "spacing around the 1 seems unbalanced"): the stock
footless alternates sit off-centre, with more room on the right (12pt
ExtraLight 165/218, Bold 104/170, oldstyle 58/331). After the swap, one,
one.tosf and the footless one.dnom are each shifted so their left and
right sidebearings are equal, measured unslanted (so italic centring
follows the slant). Advance widths stay (figures are tabular).

Only master layers are written. Run once per source:
  python3 edits/12_one_footless.py
  python3 edits/12_one_footless.py NunuikoDisplay-Italic.glyphs
"""
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"
SWAPS = (("one", "one.ss01"), ("one.tosf", "one.tosf.ss01"))

font = GSFont(GLYPHS_FILE)
masters = {m.name: m for m in font.masters}


def outline(glyph, mid):
    lay = font.glyphs[glyph].layers[mid]
    assert len(lay.paths) == 1 and not lay.components, glyph
    return [(n.position.x, n.position.y, n.type, n.smooth) for n in lay.paths[0].nodes]


def swap(a, b):
    stock = {g: {m.id: outline(g, m.id) for m in font.masters} for g in (a, b)}
    for g, other in ((a, b), (b, a)):
        assert apply_edit(GLYPHS_FILE, g,
                          lambda mname, layer, nodes, other=other:
                          {"replace_nodes": stock[other][layer.layerId]})
        print(f"{g} <- {other}'s outline")


def centre_shift(pts, width, tan):
    """x shift that makes the unslanted sidebearings equal"""
    ux = [x - y * tan for x, y in pts]
    return width / 2 - (min(ux) + max(ux)) / 2


def centre_edit(mname, layer, nodes):
    tan = math.tan(math.radians(masters[mname].italicAngle))
    pts = [(n.position.x, n.position.y) for n in nodes]
    shift = centre_shift(pts, layer.width, tan)
    print(f"{mname:34s} {layer.parent.name} centred, shifted {shift:+.0f}")
    return {"nodes": {i: (x + shift, y) for i, (x, y) in enumerate(pts)}}


def dnom_edit(mname, layer, nodes):
    m = masters[mname]
    tan = math.tan(math.radians(m.italicAngle))
    P = [(n.position.x, n.position.y) for n in nodes]
    assert len(P) == 12 and all(n.type == "line" for n in nodes), mname
    assert P[0][1] == P[11][1] == 0 and P[1][1] == P[2][1] == P[9][1], mname

    def to_base(a, b):  # line a -> b extended to y = 0
        return (b[0] - b[1] * (a[0] - b[0]) / (a[1] - b[1]), 0)

    pts = [to_base(P[3], P[2])] + P[3:9] + [to_base(P[8], P[9])]

    shift = centre_shift(pts, layer.width, tan)
    print(f"{mname:34s} one.dnom foot removed, centred, shifted {shift:+.0f}")
    return {"replace_nodes": [(x + shift, y, "line", False) for x, y in pts]}


if __name__ == "__main__":
    for a, b in SWAPS:
        swap(a, b)
        font = GSFont(GLYPHS_FILE)  # reload after writing
    masters = {m.name: m for m in font.masters}
    for g in ("one", "one.tosf"):
        assert apply_edit(GLYPHS_FILE, g, centre_edit)
    assert apply_edit(GLYPHS_FILE, "one.dnom", dnom_edit)
    print("done")
