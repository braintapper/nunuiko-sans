"""Glyph edit 6: K and k — notched joint (leg branches off the arm).

Nunito's K/k joint is a chevron: arm and leg converge essentially at the
stem (EL notch is ~20 units out). Reference Inter / Google Sans: the leg
branches off the ARM a clear distance from the stem, opening the crotch,
and is therefore steeper than the arm. Heavy masters are ALREADY notched
~45% out (fat strokes can't converge) — they stay as they are.

Rule per master, per glyph (K and k share the same 34-node topology):
  - crotch vertex (node 13) moves out along the arm-bottom line to
    max(current fraction, BRANCH_FRAC) of the arm's horizontal run
  - the leg pivots rigidly about its foot-cap center: cap nodes 5..11
    rotate by the angle the leg's top edge turns (solved by fixed-point
    iteration), preserving stroke width and cap smoothness exactly
  - node 12 = crotch vertex + the ORIGINAL notch face vector (12-13),
    rotated with the leg — keeps Nunito's little perpendicular cut
  - node 4 = new leg bottom edge (through rotated node 5, original
    direction rotated) intersected with the arm-bottom line
  - node 3 = stem right edge intersected with the arm-bottom line
Everything else (stem, caps, arm, top edge) is untouched. Same node
count/order in all masters -> interpolation-safe. Works unchanged for
italics (pure line/intersection/rotation geometry in slanted space).

Run once from sources/: python3 edits/06_K_notch.py
"""
import math

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
BRANCH_FRAC = 0.25      # min crotch-vertex position, fraction of arm run
CAP_RANGE = range(5, 12)  # leg foot cap nodes (5..11)


def xy(n):
    return (n.position.x, n.position.y)


def intersect(p1, d1, p2, d2):
    """Line p1+t*d1 vs p2+s*d2."""
    det = d1[0] * d2[1] - d1[1] * d2[0]
    assert abs(det) > 1e-9
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / det
    return (p1[0] + t * d1[0], p1[1] + t * d1[1])


def rot(v, th):
    c, s = math.cos(th), math.sin(th)
    return (v[0] * c - v[1] * s, v[0] * s + v[1] * c)


def edit(mname, layer, nodes):
    assert len(nodes) == 34, (mname, len(nodes))
    for i, t in ((3, "line"), (4, "line"), (12, "line"), (13, "line"),
                 (14, "line"), (21, "line"), (22, "line")):
        assert nodes[i].type == t, (mname, i, nodes[i].type)

    p3, p4, p5, p11, p12, p13, p14 = (xy(nodes[i]) for i in
                                      (3, 4, 5, 11, 12, 13, 14))
    p22 = xy(nodes[22])

    stem_dir = (p22[0] - p3[0], p22[1] - p3[1])
    arm_dir = (p14[0] - p13[0], p14[1] - p13[1])
    S = intersect(p3, stem_dir, p13, arm_dir)

    run_x = p14[0] - S[0]
    cur_frac = (p13[0] - S[0]) / run_x
    frac = max(BRANCH_FRAC, cur_frac)
    if frac - cur_frac < 0.005:
        print(f"{mname:20s} already notched at {cur_frac:.2f} — unchanged")
        return {"nodes": {3: S}}

    tx = S[0] + frac * run_x
    new13 = (tx, p13[1] + (tx - p13[0]) * arm_dir[1] / arm_dir[0])

    face = (p12[0] - p13[0], p12[1] - p13[1])
    cap_c = ((p5[0] + p11[0]) / 2, (p5[1] + p11[1]) / 2)
    ang_orig = math.atan2(p12[1] - p11[1], p12[0] - p11[0])

    th = 0.0
    for _ in range(40):
        p11r = tuple(cap_c[i] + rot((p11[0] - cap_c[0], p11[1] - cap_c[1]), th)[i]
                     for i in (0, 1))
        f = rot(face, th)
        new12 = (new13[0] + f[0], new13[1] + f[1])
        th_new = math.atan2(new12[1] - p11r[1], new12[0] - p11r[0]) - ang_orig
        if abs(th_new - th) < 1e-10:
            break
        th = th_new

    new = {3: S, 12: new12, 13: new13}
    for i in CAP_RANGE:
        p = xy(nodes[i])
        r = rot((p[0] - cap_c[0], p[1] - cap_c[1]), th)
        new[i] = (cap_c[0] + r[0], cap_c[1] + r[1])

    bottom_dir = rot((p5[0] - p4[0], p5[1] - p4[1]), th)
    new[4] = intersect(new[5], bottom_dir, new13, arm_dir)
    assert S[0] < new[4][0] < new13[0], (mname, S, new[4], new13)

    print(f"{mname:20s} frac {cur_frac:.2f}->{frac:.2f} "
          f"crotch ({p13[0]:.0f},{p13[1]:.0f})->({new13[0]:.0f},{new13[1]:.0f}) "
          f"leg rot {math.degrees(th):+.1f}deg")
    return {"nodes": new}


if __name__ == "__main__":
    for glyph in ("K", "k", "kgreenlandic"):
        print(f"--- {glyph}")
        assert apply_edit(GLYPHS_FILE, glyph, edit)
    print("done")
