"""Glyph edit 3b: round the G bar's top-right corner (corner A from 03).

The 03 reconstruction leaves a sharp corner where the bar's top edge
meets O's outer right arc — out of character for the font. Replace it
with a small fillet whose radius matches the bar left-end's own corner
rounding (read per master: r = barTopY - leftU_cornerY), so weight
scaling is automatic.

  ... arc (split at y = A.y - r) -> P1 curve smooth
      -> fillet controls at 55% toward A -> P2 (A.x - r, A.y) curve smooth
      -> LINE along bar top (unchanged)

35 -> 38 nodes. Run once, after 03: python3 edits/03b_G_corner.py
"""
import importlib

from lib import apply_edit

g3 = importlib.import_module("03_G_bowl")

GLYPHS_FILE = "Nunuiko.glyphs"
FILLET_TENSION = 0.55


def edit(mname, layer, nodes):
    assert len(nodes) == 35, (mname, len(nodes))
    xy = g3.xy
    A = xy(nodes[34])
    assert nodes[34].type == "curve" and not nodes[34].smooth, mname
    assert nodes[0].type == "line" and nodes[0].position.y == A[1], mname
    assert nodes[31].type == "curve" and nodes[31].smooth, mname

    r = nodes[0].position.y - nodes[3].position.y  # left-U corner radius
    assert 10 <= r <= 100, (mname, r)

    p0, c1, c2 = xy(nodes[31]), xy(nodes[32]), xy(nodes[33])
    t = g3.solve_t_for_y(p0, c1, c2, A, A[1] - r, increasing=True)
    (_, L1, L2, P1), _ = g3.split_cubic(p0, c1, c2, A, t)

    P2 = (A[0] - r, A[1])
    lerp = lambda p, q, k: (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)
    C1f = lerp(P1, A, FILLET_TENSION)
    C2f = lerp(P2, A, FILLET_TENSION)

    # keep nodes 0..31 (through outer bottom); replace 32,33,34 (arc
    # controls + sharp corner A) with split controls, fillet, P2
    out = [(n.position.x, n.position.y, n.type, n.smooth) for n in nodes[:32]]
    out.extend([
        (L1[0], L1[1], "offcurve", False),
        (L2[0], L2[1], "offcurve", False),
        (P1[0], P1[1], "curve", True),
        (C1f[0], C1f[1], "offcurve", False),
        (C2f[0], C2f[1], "offcurve", False),
        (P2[0], P2[1], "curve", True),
    ])
    assert len(out) == 38
    print(f"{mname:20s} r={r:g}  A=({A[0]:g},{A[1]:g})  P1=({P1[0]:.0f},{P1[1]:.0f})")
    return {"replace_nodes": out}


if __name__ == "__main__":
    assert apply_edit(GLYPHS_FILE, "G", edit)
    print("done")
