"""Glyph edit 3 (fonts.md item 5): rebuild G on O's bowl.

Design (see GLYPHLOG.md): the new G is O's full round bowl, opened at the
top right, keeping from the original G:
  - the horizontal bar at its original height and original left end,
  - the upper-arm terminal ending in the same place,
  - the arm/top/left outer (which is ALREADY identical to O's left side —
    G and O share a skeleton in Nunito).

Assembly (single path, 35 nodes, in original G's traversal order):
  G bar left-end U (G nodes 10-16, verbatim)
  -> bar underside LINE right to corner B on O's INNER right side at the
     bar's underside y (cubic split)
  -> down O's inner right (split remainder), inner bottom, inner left,
     inner top (O inner nodes 9..5 semantics)
  -> original G arm inner + terminal cap + outer top + outer left
     (G nodes 29..40, verbatim; G40 == O outer left node)
  -> O's outer bottom + outer right rising to corner A at the bar's TOP
     edge y (cubic split; in uprights O's right extremum sits ~1 unit
     below the bar top, so A is the extremum nudged up — no split)
  -> LINE left along bar top back to start.

Also: width := O's width; anchors top/bottom := O's (bowl recentered);
rightKerningGroup G -> O (right side is now O's round bowl).

Run once from sources/: python3 edits/03_G_bowl.py
"""
from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"


def cubic_point(p0, c1, c2, p3, t):
    u = 1 - t
    return tuple(
        u**3 * p0[i] + 3 * u * u * t * c1[i] + 3 * u * t * t * c2[i] + t**3 * p3[i]
        for i in (0, 1)
    )


def split_cubic(p0, c1, c2, p3, t):
    """De Casteljau: returns (first piece, second piece), each
    (p0, c1, c2, p3)."""
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
        assert n.smooth == smooth, (idx, n.smooth)
    return xy(n)


def build_new_g(gn, o_outer, o_inner):
    """gn: G nodes (44); o_outer/o_inner: O path nodes (12 each).
    Returns list of (x, y, type, smooth)."""
    # sanity-check the semantics we rely on
    check(gn, 10, "line", True)      # bar top, left of it the left-end U
    check(gn, 13, "curve", True)
    check(gn, 16, "curve", True)     # bar underside left
    check(gn, 17, "line")            # bar underside right end
    check(gn, 31, "curve", True)     # arm inner end
    check(gn, 34, "curve", True)     # terminal cap outer end
    check(gn, 37, "curve", True)     # outer top
    check(gn, 40, "curve", True)     # outer left == O outer node 8
    for i in (2, 5, 8, 11):
        check(o_outer, i, "curve", True)
        check(o_inner, i, "curve", True)
    # G's outer left must sit close to O's so the graft is invisible; the
    # junction node uses O's position so the O-side joint is exact
    g40, o8 = xy(gn[40]), xy(o_outer[8])
    assert abs(g40[0] - o8[0]) <= 2 and abs(g40[1] - o8[1]) <= 10, (g40, o8)

    bar_top_y = gn[10].position.y
    bar_bot_y = gn[16].position.y

    # corner B: split O inner right-descending arc (8 -> 9,10 -> 11)
    p0, c1, c2, p3 = xy(o_inner[8]), xy(o_inner[9]), xy(o_inner[10]), xy(o_inner[11])
    t = solve_t_for_y(p0, c1, c2, p3, bar_bot_y, increasing=False)
    _, (B, B1, B2, _) = split_cubic(p0, c1, c2, p3, t)
    B = (B[0], bar_bot_y)

    # corner A: split O outer bottom-to-right-extremum arc (11 -> 0,1 -> 2)
    p0, c1, c2, p3 = xy(o_outer[11]), xy(o_outer[0]), xy(o_outer[1]), xy(o_outer[2])
    if p3[1] <= bar_top_y + 2:
        # extremum sits at/just below the bar top: nudge it up, keep controls
        A1, A2, A = c1, c2, (p3[0], bar_top_y)
    else:
        (_, A1, A2, A), _ = split_cubic(p0, c1, c2, p3,
                                        solve_t_for_y(p0, c1, c2, p3, bar_top_y, increasing=True))
        A = (A[0], bar_top_y)

    out = []
    add = lambda pt, t_, sm=False: out.append((pt[0], pt[1], t_, sm))
    add(xy(gn[10]), "line", True)            # bar top left end
    for i in (11, 12):
        add(xy(gn[i]), "offcurve")
    add(xy(gn[13]), "curve", True)
    for i in (14, 15):
        add(xy(gn[i]), "offcurve")
    add(xy(gn[16]), "curve", True)
    add(B, "line")                           # bar underside -> corner B
    add(B1, "offcurve")
    add(B2, "offcurve")
    add(xy(o_inner[11]), "curve", True)      # inner bottom
    add(xy(o_inner[0]), "offcurve")
    add(xy(o_inner[1]), "offcurve")
    add(xy(o_inner[2]), "curve", True)       # inner left
    add(xy(o_inner[3]), "offcurve")
    add(xy(o_inner[4]), "offcurve")
    add(xy(o_inner[5]), "curve", True)       # inner top
    for i in (29, 30):
        add(xy(gn[i]), "offcurve")           # arm inner
    add(xy(gn[31]), "curve", True)
    for i in (32, 33):
        add(xy(gn[i]), "offcurve")
    add(xy(gn[34]), "curve", True)           # terminal cap
    for i in (35, 36):
        add(xy(gn[i]), "offcurve")
    add(xy(gn[37]), "curve", True)           # outer top
    for i in (38, 39):
        add(xy(gn[i]), "offcurve")
    add(o8, "curve", True)                   # outer left (graft at O's node)
    add(xy(o_outer[9]), "offcurve")
    add(xy(o_outer[10]), "offcurve")
    add(xy(o_outer[11]), "curve", True)      # outer bottom
    add(A1, "offcurve")
    add(A2, "offcurve")
    add(A, "curve")                          # corner A (not smooth)
    assert len(out) == 35
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
        print(f"{mname:20s} 44->35 nodes, width {layer.width:g}->{o.width:g}")
        return {
            "replace_nodes": new_nodes,
            "width": int(o.width),
            "anchors": {"top": o_anch["top"], "bottom": o_anch["bottom"]},
        }

    assert apply_edit(GLYPHS_FILE, "G", edit)

    # kerning class: right side is now O-shaped
    text = open(GLYPHS_FILE).read()
    bs = text.index("glyphname = G;")
    be = text.index("glyphname = ", bs + 1)
    block = text[bs:be]
    assert block.count("rightKerningGroup = G;") == 1
    block = block.replace("rightKerningGroup = G;", "rightKerningGroup = O;")
    open(GLYPHS_FILE, "w").write(text[:bs] + block + text[be:])
    print("rightKerningGroup G -> O\ndone")


if __name__ == "__main__":
    main()
