"""Glyph edit 9: K and k — the leg grows out of the arm (Proxima Nova style).

Stock Nunito Sans draws K/k as a chevron: the arm and the leg both meet the
stem. (Edit 06 tried a notch with the leg's lower edge still on the stem; it
was reverted.) Here the leg is detached from the stem entirely: both of its
edges end on the underside of the arm, so the open space below the arm runs
up to the arm's underside and the leg reads as a branch of the arm.

Landmarks (14-node all-straight path, every master, upright and italic):
  0 -> 1   stem right edge (1 is where the outline leaves the stem)
  2 -> 3   leg lower/left edge, 3 on the baseline
  3 -> 4   leg foot (baseline)
  4 -> 5   leg upper/right edge
  6 -> 7   arm bottom edge, 7 = arm tip
  8 .. 13  arm top, stem (untouched)

Rule, per master (pure line geometry, so it holds in slanted space):
  S   = stem right edge (0-1) ∩ arm bottom line (6-7)
  C   = S + c * (7 - S)              where the leg's centreline meets the arm,
        c solved (bisection) so the leg's lower edge meets the arm at
        GAP_FRAC of the way from S to the tip: the gap between stem and
        leg stays proportionally the same at every weight
  Fc  = midpoint of the foot (3, 4)  stays put
  w   = original leg stroke width (perpendicular, from line 2-3 to node 4)
  leg edges = lines parallel to Fc -> C at ±w/2
  1 = S, 2 = lower edge ∩ arm, 5 = upper edge ∩ arm,
  3/4 = edges ∩ baseline, 6 = midpoint of 5 and 7 (on the arm, keeps
  the 14-node structure). Nodes 0 and 7-13 don't move.

GAP_FRAC is the taste knob (--gap=0.2 to try another value). kgreenlandic shares k's topology; Kcommaaccent /
kcommaaccent are composites. Cyrillic Ka-cy/ka-cy are left stock.
Run once per source:
  python3 edits/09_K_leg_from_arm.py
  python3 edits/09_K_leg_from_arm.py NunuikoDisplay-Italic.glyphs
Add --dry-run to print the numbers without writing.
"""
import math
import sys

from lib import apply_edit

args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry-run" in sys.argv
GLYPHS_FILE = args[0] if args else "NunuikoDisplay.glyphs"
GAP_FRAC = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--gap=")), 0.15))


def intersect(p1, p2, q1, q2):
    """Intersection of line p1-p2 with line q1-q2."""
    d1 = (p2[0] - p1[0], p2[1] - p1[1])
    d2 = (q2[0] - q1[0], q2[1] - q1[1])
    den = d1[0] * d2[1] - d1[1] * d2[0]
    assert abs(den) > 1e-9, "parallel"
    t = ((q1[0] - p1[0]) * d2[1] - (q1[1] - p1[1]) * d2[0]) / den
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def edit(mname, layer, nodes):
    assert len(nodes) == 14, (mname, len(nodes))
    assert all(n.type == "line" for n in nodes), mname
    P = [(n.position.x, n.position.y) for n in nodes]
    assert P[3][1] == P[4][1] == 0, (mname, "foot not on baseline")

    S = intersect(P[0], P[1], P[6], P[7])
    arm = (P[7][0] - S[0], P[7][1] - S[1])
    along = lambda p: ((p[0] - S[0]) * arm[0] + (p[1] - S[1]) * arm[1]) / (
        arm[0] ** 2 + arm[1] ** 2)

    # original perpendicular leg width: node 4 to the line 2-3
    e = (P[3][0] - P[2][0], P[3][1] - P[2][1])
    w = abs((P[4][0] - P[2][0]) * e[1] - (P[4][1] - P[2][1]) * e[0]) / math.hypot(*e)

    Fc = ((P[3][0] + P[4][0]) / 2, 0)

    def leg_edges(c):
        C = (S[0] + c * arm[0], S[1] + c * arm[1])
        d = (C[0] - Fc[0], C[1] - Fc[1])
        ln = math.hypot(*d)
        nrm = (-d[1] / ln * w / 2, d[0] / ln * w / 2)  # up-left of the leg
        lo = ((Fc[0] + nrm[0], Fc[1] + nrm[1]), (C[0] + nrm[0], C[1] + nrm[1]))
        hi = ((Fc[0] - nrm[0], Fc[1] - nrm[1]), (C[0] - nrm[0], C[1] - nrm[1]))
        return lo, hi

    a, b = 0.0, 1.0  # tA rises with c: bisect for tA == GAP_FRAC
    for _ in range(60):
        c = (a + b) / 2
        lo, hi = leg_edges(c)
        if along(intersect(*lo, P[6], P[7])) < GAP_FRAC:
            a = c
        else:
            b = c
    base = ((0, 0), (1, 0))
    n2 = intersect(*lo, P[6], P[7])
    n5 = intersect(*hi, P[6], P[7])
    n3 = intersect(*lo, *base)
    n4 = intersect(*hi, *base)
    n6 = ((n5[0] + P[7][0]) / 2, (n5[1] + P[7][1]) / 2)
    tA, tB = along(n2), along(n5)
    assert 0 < tA < tB < along(n6) < 1, (mname, tA, tB)
    gap = math.hypot(n2[0] - S[0], n2[1] - S[1])
    print(f"{mname:34s} w {w:5.1f}  leg on arm {tA:.2f}-{tB:.2f}"
          f"  gap from stem {gap:5.1f}  foot {P[3][0]:g},{P[4][0]:g}"
          f" -> {n3[0]:.0f},{n4[0]:.0f}  width {layer.width:g}")
    if DRY:
        return {}
    return {"nodes": {1: S, 2: n2, 3: n3, 4: n4, 5: n5, 6: n6}}


if __name__ == "__main__":
    for glyph in ("K", "k", "kgreenlandic"):
        print(f"--- {glyph}")
        changed = apply_edit(GLYPHS_FILE, glyph, edit)
        assert DRY or changed
    print("dry run" if DRY else "done")
