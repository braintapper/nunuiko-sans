"""Glyph edit 3 (fonts.md item 5): rebuild G on O's bowl.

Design (see GLYPHLOG.md): the new G is O's full round bowl, opened at the
top right for the arm, keeping from the original G the horizontal bar (at
its own height + left end) and the upper-arm terminal (ending where it
always did). G and O already share a skeleton (outer left/bottom, inner
left are O's), so only the pulled-in outer-right and inner-right are
replaced with O's rounder arcs, joined at two computed corners.

Nunito Sans replay: O is structurally identical to Nunito's O (2 paths x
12 nodes, extrema at local 2/5/8/11 = right/top/left/bottom outer,
left/top/right/bottom inner), so the O-side split/graft logic ports
UNCHANGED. Only the G-side landmark indices differ (G is 31 nodes here,
44 in Nunito) and the bar left-end is a STRAIGHT cut (two line corners),
not Nunito's rounded U. Assembly is 28 nodes (Nunito: 35).

  gn[4]  line      bar top-left corner   (bar_top_y)
  gn[5]  line      bar bottom-left corner (bar_bot_y)
  gn[18,19] off / gn[20] curve / gn[21] line / gn[22,23] off / gn[24] cs
                   = arm inner + straight-cut terminal + outer top (verbatim)

Assembly order (single path, original traversal direction):
  bar top-left -> bar bottom-left -> bar underside LINE to corner B (split
  O inner-right at bar_bot_y) -> down to O inner bottom/left/top -> G arm
  inner + terminal + outer top -> O outer top->left->bottom -> rise O
  outer-right to corner A (split/nudge at bar_top_y) -> LINE bar top back.

Also: width := O's; anchors top/bottom := O's (bowl recentered).
Run once from sources/: python3 edits/03_G_bowl.py  (then 03b).
"""
from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "NunuikoDisplay.glyphs"

BAR_TL, BAR_BL = 4, 5           # bar left-end corners (define the two y's)
ARM = (18, 19, 20, 21, 22, 23, 24)  # arm inner / terminal / outer top


def cubic_point(p0, c1, c2, p3, t):
    u = 1 - t
    return tuple(u**3 * p0[i] + 3 * u * u * t * c1[i]
                 + 3 * u * t * t * c2[i] + t**3 * p3[i] for i in (0, 1))


def split_cubic(p0, c1, c2, p3, t):
    lerp = lambda a, b: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    a, b, c = lerp(p0, c1), lerp(c1, c2), lerp(c2, p3)
    d, e = lerp(a, b), lerp(b, c)
    f = lerp(d, e)
    return (p0, a, d, f), (f, e, c, p3)


def solve_t_for_y(p0, c1, c2, p3, y, increasing):
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        ym = cubic_point(p0, c1, c2, p3, mid)[1]
        if (ym < y) == increasing:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def xy(n):
    return (n.position.x, n.position.y)


def check(nodes, idx, ntype, smooth=None):
    n = nodes[idx]
    assert n.type == ntype, (idx, n.type, ntype)
    if smooth is not None:
        assert bool(n.smooth) == smooth, (idx, n.smooth)
    return xy(n)


def build_new_g(gn, o_outer, o_inner):
    check(gn, BAR_TL, "line")
    check(gn, BAR_BL, "line")
    check(gn, 20, "curve", False)
    check(gn, 21, "line", False)
    check(gn, 24, "curve", True)
    for i in (2, 5, 8, 11):
        check(o_outer, i, "curve", True)
        check(o_inner, i, "curve", True)

    bar_top_y = gn[BAR_TL].position.y
    bar_bot_y = gn[BAR_BL].position.y
    assert bar_top_y > bar_bot_y, (bar_top_y, bar_bot_y)

    # corner B: split O inner-right arc (8 -> 9,10 -> 11) at bar underside y
    p0, c1, c2, p3 = (xy(o_inner[8]), xy(o_inner[9]), xy(o_inner[10]), xy(o_inner[11]))
    t = solve_t_for_y(p0, c1, c2, p3, bar_bot_y, increasing=False)
    _, (B, B1, B2, _) = split_cubic(p0, c1, c2, p3, t)
    B = (B[0], bar_bot_y)

    # corner A: rise up O outer-right arc (11 -> 0,1 -> 2) to bar top y.
    # If O's right extremum sits at/just below the bar top, nudge it up
    # (no split); else split the arc at bar_top_y.
    p0, c1, c2, p3 = (xy(o_outer[11]), xy(o_outer[0]), xy(o_outer[1]), xy(o_outer[2]))
    if p3[1] <= bar_top_y + 2:
        A1, A2, A = c1, c2, (p3[0], bar_top_y)
    else:
        (_, A1, A2, A), _ = split_cubic(
            p0, c1, c2, p3, solve_t_for_y(p0, c1, c2, p3, bar_top_y, increasing=True))
        A = (A[0], bar_top_y)

    out = []
    add = lambda pt, t_, sm=False: out.append((pt[0], pt[1], t_, sm))
    add(xy(gn[BAR_TL]), "line")            # bar top-left corner (start)
    add(xy(gn[BAR_BL]), "line")            # bar bottom-left corner
    add(B, "line")                         # bar underside -> corner B
    add(B1, "offcurve"); add(B2, "offcurve")
    add(xy(o_inner[11]), "curve", True)    # inner bottom
    add(xy(o_inner[0]), "offcurve"); add(xy(o_inner[1]), "offcurve")
    add(xy(o_inner[2]), "curve", True)     # inner left
    add(xy(o_inner[3]), "offcurve"); add(xy(o_inner[4]), "offcurve")
    add(xy(o_inner[5]), "curve", True)     # inner top
    add(xy(gn[18]), "offcurve"); add(xy(gn[19]), "offcurve")
    add(xy(gn[20]), "curve")               # arm inner end
    add(xy(gn[21]), "line")                # terminal tip (straight cut)
    add(xy(gn[22]), "offcurve"); add(xy(gn[23]), "offcurve")
    add(xy(gn[24]), "curve", True)         # outer top
    add(xy(o_outer[6]), "offcurve"); add(xy(o_outer[7]), "offcurve")
    add(xy(o_outer[8]), "curve", True)     # outer left
    add(xy(o_outer[9]), "offcurve"); add(xy(o_outer[10]), "offcurve")
    add(xy(o_outer[11]), "curve", True)    # outer bottom
    add(A1, "offcurve"); add(A2, "offcurve")
    add(A, "curve")                        # corner A (sharp; LINE closes to start)
    assert len(out) == 28, len(out)
    return out


def main():
    font = GSFont(GLYPHS_FILE)
    masters = {m.id: m.name for m in font.masters}
    o_layers = {l.layerId: l for l in font.glyphs["O"].layers if l.layerId in masters}

    def edit(mname, layer, nodes):
        o = o_layers[layer.layerId]
        o_outer, o_inner = o.paths[0].nodes, o.paths[1].nodes
        new_nodes = build_new_g(nodes, o_outer, o_inner)
        o_anch = {a.name: (a.position.x, a.position.y) for a in o.anchors}
        print(f"{mname:26s} 31->28 nodes, width {layer.width:g}->{o.width:g}")
        return {
            "replace_nodes": new_nodes,
            "width": int(o.width),
            "anchors": {"top": o_anch["top"], "bottom": o_anch["bottom"]},
        }

    assert apply_edit(GLYPHS_FILE, "G", edit)
    print("done")


if __name__ == "__main__":
    main()
