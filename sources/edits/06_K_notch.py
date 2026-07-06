"""Glyph edit 6: K and k — notched joint (leg branches off the arm).

Nunito Sans's K/k joint is a near-chevron in the light masters (arm and
leg converge at the stem); the heavy masters are already notched natively
(fat strokes can't converge). The goal: the arm reaches the stem, and the
leg branches off the arm-bottom with a CONSISTENT stroke width.

Nunito Sans replay: K/k/kgreenlandic are 14-node all-straight paths
(Nunito: 34, with a rounded leg-foot cap that Nunito rotated rigidly).
Nunito Sans's foot is a FLAT baseline cut, so the leg can't rotate about
it without tilting off the baseline. Landmarks (per master):
  node 1 = stem right edge          -> stem_x
  node 2 = leg-lower inner (on stem) node 3/4 = leg foot (on baseline)
  node 5 = leg-upper inner           node 6 = arm-bottom inner (crotch)
  node 7 = arm tip                   node 9 = arm-top inner (on stem)

Operation: keep the leg a consistent-width trapezoid and steepen it about
the foot (re-cutting node4 flat on the baseline) just enough to move the
branch — where the leg-upper edge meets the arm-bottom — outward. The
depth is self-limited: node2 (leg-lower on the stem) is placed a fixed
fraction of the way from S (arm-bottom-at-stem) up to node9 (arm-top),
matching how the native heavy masters sit. The light masters are
proportionally WIDE (foot far from the stem), so this yields a subtle
notch there and a pronounced one at heavy weights — the same progression
Nunito Sans already draws. node5/node6 make a small near-vertical notch
face at the branch. Only nodes 2,4,5,6 move; 14-node structure preserved.

Run once from sources/: python3 edits/06_K_notch.py
"""
import math

from lib import apply_edit

GLYPHS_FILE = "NunuikoDisplay.glyphs"
Y2_FRAC = 0.60     # node2 height: fraction from S (arm-bottom@stem) up to node9
FACE_K = 0.55      # notch-face height as a fraction of leg width


def rot(v, a):
    c, s = math.cos(a), math.sin(a)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def inter(p1, d1, p2, d2):
    det = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / det
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def edit(mname, layer, nodes):
    assert len(nodes) == 14, (mname, len(nodes))
    for n in nodes:
        assert n.type == "line", (mname, n.type)
    P = lambda i: (nodes[i].position.x, nodes[i].position.y)
    n2, n3, n4, n5, n6, n7, n9 = P(2), P(3), P(4), P(5), P(6), P(7), P(9)
    stem_x = P(1)[0]

    adir = (n7[0] - n6[0], n7[1] - n6[1])              # arm-bottom direction
    arm_y = lambda x: n6[1] + (x - n6[0]) / adir[0] * adir[1]
    S = (stem_x, arm_y(stem_x))
    run = n7[0] - S[0]
    cur = (n6[0] - S[0]) / run

    # leg: parallelogram-ish stroke; leg-lower n2->n3, leg-upper n5->n4
    ll = (n3[0] - n2[0], n3[1] - n2[1])
    Ll = math.hypot(*ll)
    llu = (ll[0] / Ll, ll[1] / Ll)
    un = (-ll[1] / Ll, ll[0] / Ll)
    if (n5[0] - n2[0]) * un[0] + (n5[1] - n2[1]) * un[1] < 0:  # perp to upper side
        un = (-un[0], -un[1])
    w = abs((n4[0] - n3[0]) * un[0] + (n4[1] - n3[1]) * un[1])
    y2_target = S[1] + Y2_FRAC * (n9[1] - S[1])

    def build(delta):
        v = rot(llu, delta)
        nperp = (-v[1], v[0])
        if nperp[0] * un[0] + nperp[1] * un[1] < 0:
            nperp = (-nperp[0], -nperp[1])
        up0 = (n3[0] + w * nperp[0], n3[1] + w * nperp[1])   # a point on leg-upper
        new2 = inter(n3, v, (stem_x, 0), (0, 1))
        new4 = inter(up0, v, (0, 0), (1, 0))
        Xb = inter(up0, v, n6, adir)
        return new2, new4, Xb, up0, v

    # steepen the leg (rotate toward vertical) until node2 reaches y2_target
    lo, hi = 0.0, math.radians(45)
    for _ in range(50):
        mid = (lo + hi) / 2
        if build(-mid)[0][1] > y2_target:
            hi = mid
        else:
            lo = mid
    new2, new4, Xb, up0, v = build(-lo)
    frac = (Xb[0] - S[0]) / run
    if frac - cur < 0.01:
        print(f"{mname:26s} stays {cur:.2f}")
        return {}

    n6x = Xb[0] - FACE_K * w * 0.4        # small near-vertical notch face
    new6 = (n6x, arm_y(n6x))
    up_y = up0[1] + (n6x - up0[0]) / v[0] * v[1]
    new5 = (n6x, up_y)
    print(f"{mname:26s} {cur:.2f}->{frac:.2f} d={math.degrees(-lo):.1f} "
          f"n2y {n2[1]:.0f}->{new2[1]:.0f} face={new5[1]-new6[1]:.0f}")
    return {"nodes": {2: new2, 4: new4, 5: new5, 6: new6}}


if __name__ == "__main__":
    for glyph in ("K", "k", "kgreenlandic"):
        print(f"--- {glyph}")
        assert apply_edit(GLYPHS_FILE, glyph, edit)
    print("done")
