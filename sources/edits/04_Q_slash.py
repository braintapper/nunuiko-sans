"""Glyph edit 4: Q slashed tail, Jost-style, baseline-aligned.

Design (user spec): replace Nunito's curved below-baseline Qtail swash
with a straight Jost-like slash crossing the bowl's bottom-right ring.
The slash's LOWEST corner sits exactly on the baseline (y = 0) — the new
Q has no descender.

Q = O component + _part.Qtail component, so only _part.Qtail changes
(12 curved nodes -> capsule/stadium: straight stroke with fully round
semicircular caps, matching the font's other terminals).

All geometry is derived from O's own outlines per master:
  - M     = midpoint between the outer and inner bottom-right arc
            midpoints (t=0.5) — the ring midline at ~4:30
  - w     = distance between those arc midpoints — the ring thickness
  - d     = slash direction, 45 deg down-right; sheared by the italic
            angle (9 deg) for italic masters
  - outer cap: center solved so the cap circle is tangent to y = 0
  - inner cap: ink reaches K_IN_FRAC of the counter radius past the
            inner arc midpoint along -d (cap center pulled back by w/2
            so the round tip ends where the flat end used to)
  - both caps are then pushed outward by EXTEND_FRAC of the slash's
            tip-to-tip length, lengthening it past the baseline (outer)
            and deeper into the counter (inner)
Coordinates are converted from O-space to part-local space via Q's
per-master component offset. Winding matched to O's outer ring so the
overlap unions (not cancels) under nonzero fill.

Run once from sources/: python3 edits/04_Q_slash.py
"""
import math

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
ANGLE_DEG = 45          # slash angle below horizontal, upright masters
ITALIC_SHEAR = math.tan(math.radians(9))
K_IN_FRAC = 0.35        # inner ink tip: fraction of counter radius past the ring
MAX_COUNTER_FRAC = 0.6  # slash weight cap, as fraction of counter radius
EXTEND_FRAC = 0.10      # lengthen the slash this fraction of its length per end
CAP_TENSION = 0.5523    # circle-approximation control distance


def cubic_point(p0, c1, c2, p3, t):
    u = 1 - t
    return tuple(
        u**3 * p0[i] + 3 * u * u * t * c1[i] + 3 * u * t * t * c2[i] + t**3 * p3[i]
        for i in (0, 1)
    )


def xy(n):
    return (n.position.x, n.position.y)


def signed_area(points):
    s = 0.0
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        s += x1 * y2 - x2 * y1
    return s / 2


def edit_factory(font):
    masters = {m.id: m.name for m in font.masters}
    o_layers = {l.layerId: l for l in font.glyphs["O"].layers
                if l.layerId in masters}
    q_offsets = {}
    for l in font.glyphs["Q"].layers:
        if l.layerId in masters:
            (tail_comp,) = [c for c in l.components if c.name == "_part.Qtail"]
            q_offsets[l.layerId] = (tail_comp.position.x, tail_comp.position.y)

    def edit(mname, layer, nodes):
        o = o_layers[layer.layerId]
        outer, inner = o.paths[0].nodes, o.paths[1].nodes
        # bottom-right arcs: outer 11 -> (0,1) -> 2 ; inner 8 -> (9,10) -> 11
        om = cubic_point(xy(outer[11]), xy(outer[0]), xy(outer[1]), xy(outer[2]), 0.5)
        im = cubic_point(xy(inner[8]), xy(inner[9]), xy(inner[10]), xy(inner[11]), 0.5)
        M = ((om[0] + im[0]) / 2, (om[1] + im[1]) / 2)
        w_ring = math.dist(om, im)

        a = math.radians(ANGLE_DEG)
        d = (math.cos(a), -math.sin(a))
        if "Italic" in mname:
            d = (d[0] + ITALIC_SHEAR * d[1], d[1])
            norm = math.hypot(*d)
            d = (d[0] / norm, d[1] / norm)
        n = (-d[1], d[0])  # n[1] > 0: +n is the upper side

        c_inner = tuple(sum(xy(inner[i])[j] for i in (2, 5, 8, 11)) / 4
                        for j in (0, 1))
        counter_r = math.dist(im, c_inner)
        # cap the slash weight against the counter so Heavy keeps an open
        # counter and a visible outer stub (full ring weight would swallow it)
        w = min(w_ring, MAX_COUNTER_FRAC * counter_r)

        R = w / 2
        # base outer cap center: circle bottom (center_y - R) tangent to y = 0
        t_out = (R - M[1]) / d[1]
        assert t_out > 0, (mname, t_out)
        C_out0 = (M[0] + t_out * d[0], M[1] + t_out * d[1])
        assert abs(C_out0[1] - R) < 1e-6, (mname, C_out0)
        # base inner cap center: round tip's ink ends where the flat end did
        p_in = K_IN_FRAC * counter_r
        C_in0 = (im[0] - (p_in - R) * d[0], im[1] - (p_in - R) * d[1])

        # 4d: lengthen the slash by EXTEND_FRAC of its tip-to-tip length at
        # EACH end — the outer tip then dips below the baseline (+d) and the
        # inner tip reaches deeper into the counter (-d)
        ext = EXTEND_FRAC * (math.dist(C_out0, C_in0) + 2 * R)
        C_out = (C_out0[0] + ext * d[0], C_out0[1] + ext * d[1])
        C_in = (C_in0[0] - ext * d[0], C_in0[1] - ext * d[1])
        # keep the counter open: inner tip must stay on the ring side of the
        # counter center (not spear across it)
        T_in = (C_in[0] - R * d[0], C_in[1] - R * d[1])
        assert (T_in[0] - c_inner[0]) * d[0] + (T_in[1] - c_inner[1]) * d[1] > 0, mname

        # winding must match O's outer ring (else nonzero fill cancels);
        # flipping the normal mirrors the traversal orientation
        half = (n[0] * R, n[1] * R)
        rect = [(C_in[0] - half[0], C_in[1] - half[1]),
                (C_out[0] - half[0], C_out[1] - half[1]),
                (C_out[0] + half[0], C_out[1] + half[1]),
                (C_in[0] + half[0], C_in[1] + half[1])]
        # NB the capsule below traverses this cycle in REVERSE (out_hi ->
        # out_lo -> in_lo -> in_hi), so flip n when the areas AGREE
        s = -1 if signed_area(rect) * signed_area([xy(p) for p in outer]) > 0 else 1
        n = (s * n[0], s * n[1])

        # capsule: two semicircular caps (two quarter-arc cubics each,
        # tension 0.5523) joined by straight edges — fully round terminals
        # like the font's other line ends
        add = lambda p, v, k=1.0: (p[0] + k * v[0], p[1] + k * v[1])
        kR = CAP_TENSION * R
        nodes_out = []
        # sg = which side of the stroke the cap is entered from, so the
        # two straight edges connect exit(outer)->entry(inner) and back
        for C, e, sg in ((C_out, d, 1), (C_in, (-d[0], -d[1]), -1)):
            A = add(C, n, sg * R)     # entry side point (ends straight edge)
            T = add(C, e, R)          # round tip
            B = add(C, n, -sg * R)    # exit side point
            nodes_out += [
                (*A, "line", True),
                (*add(A, e, kR), "offcurve", False),
                (*add(T, n, sg * kR), "offcurve", False),
                (*T, "curve", True),
                (*add(T, n, -sg * kR), "offcurve", False),
                (*add(B, e, kR), "offcurve", False),
                (*B, "curve", True),
            ]
        ox, oy = q_offsets[layer.layerId]
        nodes_out = [(x - ox, y - oy, t, sm) for x, y, t, sm in nodes_out]
        print(f"{mname:20s} w_slash={w:.0f} R={R:.1f} "
              f"caps in=({C_in[0]:.0f},{C_in[1]:.0f}) out=({C_out[0]:.0f},{C_out[1]:.0f})")
        return {"replace_nodes": nodes_out}

    return edit


if __name__ == "__main__":
    font = GSFont(GLYPHS_FILE)
    assert apply_edit(GLYPHS_FILE, "_part.Qtail", edit_factory(font))
    print("done")
