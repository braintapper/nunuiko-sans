"""Glyph edit 6: K and k — notched joint (leg branches off the arm).

Nunito Sans's K/k joint is a near-chevron in the light masters (arm and
leg converge at the stem); the heavy masters are already notched natively.
Goal: the arm reaches the stem, and the leg visibly branches off the
arm-bottom a clear distance out, with a roughly consistent stroke width.

Nunito Sans replay: K/k/kgreenlandic are 14-node all-straight paths
(Nunito: 34, rounded foot cap that Nunito rotated rigidly — doesn't port
to Nunito Sans's flat baseline foot). Landmarks (per master):
  node 1 = stem right edge      node 2 = leg-lower inner (on stem)
  node 3/4 = leg foot (baseline) node 5 = leg-upper inner
  node 6 = arm-bottom inner      node 7 = arm tip
  node 9 = arm-top inner (stem)

Two earlier attempts failed: (a) sliding the notch face out along the arm
pulled the arm off the stem and bulged the leg; (b) a strictly
consistent-width leg steepened about the foot stays clean but is nearly
invisible on the light masters — the notch face scales with the (thin)
stroke, so a proper light notch just isn't achievable that way (the base
font itself draws its light K as a chevron for this reason).

This version reads as TWO SEPARATE STROKES (user requirement): move the
branch (nodes 5,6) out to a MODERATE BRANCH_FRAC (0.18) so the leg clearly
branches off the arm, but keep node2 (leg-lower on the stem) LOW — only a
light RAISE (0.25) toward node9 to tidy the near-stem width. Lifting node2
too far (an earlier attempt) merged the arm and leg into a lopsided "<";
keeping it low keeps the arm and leg reading as two balanced strokes with
a visible notch, in exchange for a small width variation. Applied as a
floor (max with current frac); the already-notched heavy masters are left
as drawn. Only nodes 2,5,6 move — 14-node structure preserved, works in
italic (pure line geometry). BRANCH_FRAC / RAISE are the taste knobs.
Run once: python3 edits/06_K_notch.py
"""
from lib import apply_edit

GLYPHS_FILE = "NunuikoDisplay.glyphs"
BRANCH_FRAC = 0.18    # branch position, fraction of the arm run
RAISE = 0.25          # how far to lift node2 toward the target (0..1)
RAISE_TARGET = 0.85   # target height, fraction from S up to node9


def edit(mname, layer, nodes):
    assert len(nodes) == 14, (mname, len(nodes))
    for n in nodes:
        assert n.type == "line", (mname, n.type)
    P = lambda i: (nodes[i].position.x, nodes[i].position.y)
    n2, n5, n6, n7, n9 = P(2), P(5), P(6), P(7), P(9)
    stem_x = P(1)[0]

    adir = (n7[0] - n6[0], n7[1] - n6[1])              # arm-bottom direction
    arm_y = lambda x: n6[1] + (x - n6[0]) / adir[0] * adir[1]
    S = (stem_x, arm_y(stem_x))
    run = n7[0] - S[0]
    cur = (n6[0] - S[0]) / run
    frac = max(BRANCH_FRAC, cur)
    if frac - cur < 0.01:
        print(f"{mname:26s} stays {cur:.2f}")
        return {}

    face = n5[1] - n6[1]                               # keep original face height
    nx = S[0] + frac * run
    new6 = (nx, arm_y(nx))
    new5 = (nx, arm_y(nx) + face)
    # lift node2 toward node9 so the leg doesn't bulge near the stem
    target = S[1] + RAISE_TARGET * (n9[1] - S[1])
    y2 = min(n2[1] + RAISE * (target - n2[1]), n9[1] - 6)
    new2 = (stem_x, y2)
    print(f"{mname:26s} {cur:.2f}->{frac:.2f} n2y {n2[1]:.0f}->{y2:.0f} face={face:.0f}")
    return {"nodes": {2: new2, 5: new5, 6: new6}}


if __name__ == "__main__":
    for glyph in ("K", "k", "kgreenlandic"):
        print(f"--- {glyph}")
        assert apply_edit(GLYPHS_FILE, glyph, edit)
    print("done")
