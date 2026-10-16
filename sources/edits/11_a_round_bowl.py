"""Glyph edit 11: a — rounder bowl that arches down into the stem.

Stock Nunito Sans's a bowl has a flat top: both its outer edge and the
counter's top run level into the stem, leaving a square inside corner.
The user wants a "bulbous" bowl like Proxima Nova's, whose top arches and
comes DOWN into the stem (the way this font's own d bowl meets its stem).

Structure (39 nodes, same in every master, upright and italic):
  19 -> 20       stem left edge, down into the counter
  20 -> 23 -> 26 counter: bottom (23) and left (26) extremes
  26 -> 29       counter top-left curve; 29 = counter top
  29 -> 30       counter top runs level into the stem (30 sits inside it)
  30 -> 31       up inside the stem
  31 -> 32       bowl top runs level out of the stem
  32 -> 35       bowl top-left curve; 35 = bowl left extreme, 38 = bottom

Rule, per master (worked in unslanted space, so it holds on the italic
masters: x' = x - y*tan(italic angle), then slanted back):
  - The counter and bowl peaks move over their bottom extremes (29 above
    23, 32 above 38), keeping their heights.
  - The left quarters (26 -> 29, 35 -> 32) take their handle fractions
    from the same master's o (counter and outer contour), so the bowl
    gets the family's own roundness. The italic o is a true italic oval
    (skewed even unslanted), so italic masters use the matching upright
    master's o.
  - 29 -> 30 and 31 -> 32 become curves (two off-curves each, 39 -> 43
    nodes) that arch down to the junctions inside the stem:
      inner 30 at  peak - INNER_DROP * counter height
      outer 31 at  peak - OUTER_DROP * bowl height
    leaving the peak level (handle = o fraction of the run) and meeting
    the stem TILT degrees off vertical, so the join stays a visible
    crotch as in d rather than melting in tangentially.
  - 20 (where the stem edge turns into the counter bottom) drops to the
    inner junction if it sat above it, its handle 21 scaled to match.
  - First of all (user, same day): the bowl is BOWL_RISE (10%) taller.
    Its top rises by 0.10 x the stock bowl height; the bottom stays on the
    baseline. Points at or below the counter bottom don't move, points at
    or above the counter top rise fully, those between in proportion, so
    the top and bottom stroke thicknesses are unchanged.
INNER_DROP / OUTER_DROP / TILT / BOWL_RISE are the taste knobs.

Composites (aacute, adieresis, ...) follow. a.ss01 is left alone.
Run once per source:
  python3 edits/11_a_round_bowl.py
  python3 edits/11_a_round_bowl.py NunuikoDisplay-Italic.glyphs
"""
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

args = [a for a in sys.argv[1:] if not a.startswith("--")]
GLYPHS_FILE = args[0] if args else "NunuikoDisplay.glyphs"
INNER_DROP = 0.40  # counter: junction depth below its top, x counter height
OUTER_DROP = 0.22  # bowl: junction depth below its top, x bowl height
TILT = 15          # degrees off vertical where the arches meet the stem
BOWL_RISE = 0.10   # bowl grows taller by this x its stock height
BOWL_NODES = list(range(0, 4)) + list(range(20, 39))  # bowl + counter

STRUCT = "oocllllsoocsoocloocsoocslsoocsoocsoocslllsoocsoocs"


def struct(nodes):
    return "".join(
        {"offcurve": "o", "curve": "c", "line": "l"}[n.type] + ("s" if n.smooth else "")
        for n in nodes)


_font = GSFont(GLYPHS_FILE)
_masters = {m.name: m for m in _font.masters}
# the italic o is a true italic oval (skewed even unslanted), so its
# handle fractions don't read cleanly: italic masters borrow the matching
# upright master's o
_upright = GSFont("NunuikoDisplay.glyphs")
_umasters = {m.name: m for m in _upright.masters}


def o_fractions(mname, tan):
    """Handle fractions of the (upright) o's top-left quarters:
    (inner_h, inner_v, outer_h, outer_v)."""
    m = _umasters[mname.replace(" Italic", "")]
    lay = _upright.glyphs["o"].layers[m.id]
    out = []
    for path, (top, h, v, left) in ((lay.paths[1], (5, 4, 3, 2)),
                                    (lay.paths[0], (5, 6, 7, 8))):
        P = lambda i: (path.nodes[i].position.x, path.nodes[i].position.y)
        T, H, V, L = P(top), P(h), P(v), P(left)
        out += [(T[0] - H[0]) / (T[0] - L[0]), (V[1] - L[1]) / (T[1] - L[1])]
    return out


def edit(mname, layer, nodes):
    assert len(nodes) == 39, (mname, len(nodes))
    s = struct(nodes)
    tan = math.tan(math.radians(_masters[mname].italicAngle))
    un = lambda p: (p[0] - p[1] * tan, p[1])
    re_ = lambda p: (p[0] + p[1] * tan, p[1])
    P = [un((n.position.x, n.position.y)) for n in nodes]
    T = [(n.type, n.smooth) for n in nodes]
    fih, fiv, foh, fov = o_fractions(mname, tan)

    # taller bowl: raise its top by BOWL_RISE x the bowl height, keeping
    # the bottom on the baseline and both stroke thicknesses. Points at or
    # below the counter bottom stay, points at or above the counter top
    # rise fully, those between rise in proportion (unslanted, so italic
    # points move along the slant).
    yb, yt = P[23][1], P[29][1]
    rise = BOWL_RISE * (P[32][1] - P[38][1])
    for i in BOWL_NODES:
        f = min(1, max(0, (P[i][1] - yb) / (yt - yb)))
        P[i] = (P[i][0], P[i][1] + f * rise)

    # counter
    bot_i, left_i = P[23], P[26]
    peak_i = (bot_i[0], P[29][1])
    ci_h = peak_i[1] - bot_i[1]
    j_i = (P[30][0], peak_i[1] - INNER_DROP * ci_h)
    # bowl
    bot_o, left_o = P[38], P[35]
    peak_o = (bot_o[0], P[32][1])
    co_h = peak_o[1] - bot_o[1]
    j_o = (P[31][0], peak_o[1] - OUTER_DROP * co_h)
    assert j_i[1] < j_o[1], mname

    t = (math.sin(math.radians(TILT)), math.cos(math.radians(TILT)))  # up-left

    def arch(peak, j, fh, fv):
        """off-curves from the peak (level) down to the junction j"""
        c1 = (peak[0] + fh * (j[0] - peak[0]), peak[1])
        L = fv * (peak[1] - j[1])
        c2 = (j[0] - t[0] * L, j[1] + t[1] * L)
        return c1, c2

    new = list(P)
    # 20/21: stem edge turns into the counter no higher than the junction
    if P[20][1] > j_i[1]:
        k = (j_i[1] - P[23][1]) / (P[20][1] - P[23][1])
        new[20] = (P[20][0], j_i[1])
        new[21] = (P[21][0], P[23][1] + k * (P[21][1] - P[23][1]))
    # counter top-left quarter 26 -> 29 (26 left, 29 peak)
    new[27] = (left_i[0], left_i[1] + fiv * (peak_i[1] - left_i[1]))
    new[28] = (peak_i[0] - fih * (peak_i[0] - left_i[0]), peak_i[1])
    new[29] = peak_i
    new[30] = j_i
    new[31] = j_o
    new[32] = peak_o
    # bowl top-left quarter 32 -> 35 (32 peak, 35 left)
    new[33] = (peak_o[0] - foh * (peak_o[0] - left_o[0]), peak_o[1])
    new[34] = (left_o[0], left_o[1] + fov * (peak_o[1] - left_o[1]))

    ia1, ia2 = arch(peak_i, j_i, fih, fiv)   # 29 -> 30
    oa2, oa1 = arch(peak_o, j_o, foh, fov)   # 31 -> 32 runs the other way

    out = []
    for i in range(39):
        typ, sm = T[i]
        if i == 30:
            out += [(*re_(ia1), "offcurve", False), (*re_(ia2), "offcurve", False)]
            typ, sm = "curve", False
        if i == 32:
            out += [(*re_(oa1), "offcurve", False), (*re_(oa2), "offcurve", False)]
            typ, sm = "curve", True
        out.append((*re_(new[i]), typ, sm))
    print(f"{mname:34s} counter peak y {peak_i[1]:g} -> stem at {j_i[1]:.0f};"
          f" bowl peak y {peak_o[1]:g} -> stem at {j_o[1]:.0f}"
          f"  (o fractions {fih:.2f}/{fiv:.2f}, {foh:.2f}/{fov:.2f})")
    return {"replace_nodes": out}


if __name__ == "__main__":
    for m in _font.masters:  # every master must share the stock structure
        s = struct(_font.glyphs["a"].layers[m.id].paths[0].nodes)
        assert s == STRUCT, (m.name, s)
    assert apply_edit(GLYPHS_FILE, "a", edit)
    print("done")
