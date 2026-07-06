"""Glyph edit 6: K and k — notched joint (leg branches off the arm).

Nunito Sans's K/k joint is a near-chevron in the light masters (arm and
leg converge at the stem); the heavy masters are already notched (fat
strokes can't converge). The rule is a FLOOR, not an offset: slide the
notch out along the arm to max(current, BRANCH_FRAC) of the arm's run.
Masters already past the floor are left untouched.

Nunito Sans replay: K/k/kgreenlandic are 14-node all-straight paths
(Nunito: 34, with a rounded leg-foot cap). Landmarks (per master):
  node 1 = stem right edge (lower)     -> stem_x
  node 6 = arm-bottom inner end (crotch, on the arm-bottom line)
  node 7 = arm tip (arm-bottom far end)
  node 5 = leg-bottom inner end; edge 5->6 = the notch face

Because Nunito Sans's leg foot is a FLAT baseline cut (not Nunito's
rounded cap), the leg cannot rotate rigidly about its foot without tilting
off the baseline. Instead the notch is opened directly: slide the notch
face (nodes 5,6) out along the arm-bottom line to BRANCH_FRAC, keeping the
face rigid; the leg-bottom edge (foot->node5) re-angles, the arm-bottom
edge (node6->tip) starts further out, and the foot / stem attachments /
arm tip stay put. Pure line geometry — interpolation-safe (only nodes 5,6
move, same 14-node structure everywhere), works unchanged in italic space.

Run once from sources/: python3 edits/06_K_notch.py
"""
from lib import apply_edit

GLYPHS_FILE = "NunuikoDisplay.glyphs"
BRANCH_FRAC = 0.25      # min crotch position, fraction of the arm's run


def edit(mname, layer, nodes):
    assert len(nodes) == 14, (mname, len(nodes))
    for n in nodes:
        assert n.type == "line", (mname, n.type)
    xy = lambda i: (nodes[i].position.x, nodes[i].position.y)
    n1, n5, n6, n7 = xy(1), xy(5), xy(6), xy(7)

    stem_x = n1[0]
    adir = (n7[0] - n6[0], n7[1] - n6[1])          # arm-bottom direction
    assert adir[0] != 0, mname
    # S = stem right edge (vertical) intersected with the arm-bottom line
    Sy = n6[1] + (stem_x - n6[0]) / adir[0] * adir[1]
    S = (stem_x, Sy)
    run = n7[0] - S[0]
    cur = (n6[0] - S[0]) / run
    frac = max(BRANCH_FRAC, cur)
    if frac - cur < 0.005:
        print(f"{mname:26s} already notched at {cur:.2f} — unchanged")
        return {}

    nx = S[0] + frac * run
    new6 = (nx, S[1] + (nx - S[0]) / adir[0] * adir[1])
    face = (n5[0] - n6[0], n5[1] - n6[1])          # notch face, kept rigid
    new5 = (new6[0] + face[0], new6[1] + face[1])
    print(f"{mname:26s} frac {cur:.2f}->{frac:.2f} "
          f"crotch ({n6[0]:.0f},{n6[1]:.0f})->({new6[0]:.0f},{new6[1]:.0f})")
    return {"nodes": {5: new5, 6: new6}}


if __name__ == "__main__":
    for glyph in ("K", "k", "kgreenlandic"):
        print(f"--- {glyph}")
        assert apply_edit(GLYPHS_FILE, glyph, edit)
    print("done")
