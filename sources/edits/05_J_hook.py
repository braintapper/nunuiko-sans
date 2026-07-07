"""Glyph edit 5: capital J — upturned hooked foot, widened to 66% of U.

Reference: Google Sans Flex J. Nunito Sans's J sweeps left and dies at the
baseline; the new foot is a U-hook: down the stem, around the bottom, up
the left side, ending in a terminal cap. The glyph is also WIDENED:
advance = WIDTH_FRAC_OF_U x U's width. All growth is bowl-side — the stem
shifts right by delta, the hook's outer-left keeps its old extent, so LSB
and RSB are both preserved.

Nunito Sans replay: J is a 12-node single path (Nunito: 22); landmarks
re-derived from its own outline (asserted):
  node 3  curve smooth  stem right + curve-start y
  node 4  line          stem right top
  node 5  line          stem left top
  node 6  line smooth   stem left + curve-start y
  node 9  curve smooth  inner bottom (keeps the original bottom taper)
  node 10 line          hook outer-left (LSB)
  node 11 line          outer bottom overshoot

**Terminal is a FLAT CUT, not Nunito's rounded cap.** Nunito matched its
rounded stem-top cap; Nunito Sans's stem top is a flat cut (line corners),
so the J hook ends in a flat horizontal cut at height H (two line corners),
matching the font's vocabulary. The bottom of the U stays round (kappa
arcs). Output: 16 nodes.

Composites follow: IJ, I_J.loclNLD, Iacute_J.loclNLD, Je-cy, LJ, NJ get
width += delta; Jcircumflex also gets its accent transform tx += delta.
Lowercase j is CANCELLED (left stock).

Run once from sources/: python3 edits/05_J_hook.py
"""
import math
import sys

from glyphsLib import GSFont

from lib import WIDTH_RE, apply_edit

# roman by default; pass the italic source as argv[1] for the italic pass
GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"
WIDTH_FRAC_OF_U = 0.66
H_FRAC = 0.9            # terminal height, fraction of stem curve-start y
HOOK_MAX_FRAC = 0.55    # hook weight cap, fraction of the left span
KAPPA = 0.5523
SLANT = math.tan(math.radians(9))

WIDTH_ONLY_COMPOSITES = ["IJ", "I_J.loclNLD", "Iacute_J.loclNLD",
                         "Je-cy", "LJ", "NJ"]


def edit_factory(font):
    masters = {m.id: m.name for m in font.masters}
    u_width = {l.layerId: l.width for l in font.glyphs["U"].layers
               if l.layerId in masters}
    deltas = {}

    def edit(mname, layer, nodes):
        assert len(nodes) == 12, (mname, len(nodes))
        for i, t, sm in ((3, "curve", True), (4, "line", False),
                         (5, "line", False), (6, "line", True),
                         (9, "curve", True), (10, "line", False),
                         (11, "line", False)):
            assert nodes[i].type == t and bool(nodes[i].smooth) == sm, (mname, i)

        w_new = round(WIDTH_FRAC_OF_U * u_width[layer.layerId])
        delta = w_new - layer.width
        deltas[layer.layerId] = delta

        s = SLANT if "Italic" in mname else 0.0
        de = lambda n: (n.position.x - s * n.position.y, n.position.y)
        re_ = lambda x, y: (x + s * y, y)

        sr_x, y3 = de(nodes[3])
        sl_x, y6 = de(nodes[6])
        top_y = nodes[4].position.y
        sr_x += delta
        sl_x += delta
        xO = de(nodes[10])[0]
        apexI_y = nodes[9].position.y
        apexO_y = nodes[11].position.y

        w_stem = sr_x - sl_x
        w_hook = min(w_stem, HOOK_MAX_FRAC * (sl_x - xO))
        xI = xO + w_hook
        H = H_FRAC * y3
        midx = (xO + xI) / 2
        apexI_x = (sl_x + xI) / 2
        apexO_x = (sr_x + xO) / 2
        k = KAPPA

        out = [
            (*re_(sr_x, y3), "curve", True),               # 0 stem right curve-start
            (*re_(sr_x, top_y), "line", False),            # 1 stem right top
            (*re_(sl_x, top_y), "line", False),            # 2 stem left top
            (*re_(sl_x, y6), "line", True),                # 3 stem left curve-start
            (*re_(sl_x, y6 - k * (y6 - apexI_y)), "offcurve", False),
            (*re_(apexI_x + k * (sl_x - apexI_x), apexI_y), "offcurve", False),
            (*re_(apexI_x, apexI_y), "curve", True),       # 6 inner bottom apex
            (*re_(apexI_x - k * (apexI_x - xI), apexI_y), "offcurve", False),
            (*re_(xI, apexI_y + k * (H - apexI_y)), "offcurve", False),
            (*re_(xI, H), "curve", False),                 # 9 inner terminal (ends inner rise)
            (*re_(xO, H), "line", False),                  # 10 outer terminal; seg 9->10 = flat cut
            (*re_(xO, H - k * (H - apexO_y)), "offcurve", False),
            (*re_(apexO_x - k * (apexO_x - xO), apexO_y), "offcurve", False),
            (*re_(apexO_x, apexO_y), "curve", True),       # 13 outer bottom apex
            (*re_(apexO_x + k * (sr_x - apexO_x), apexO_y), "offcurve", False),
            (*re_(sr_x, y3 - k * (y3 - apexO_y)), "offcurve", False),
        ]
        assert len(out) == 16
        anchors = {}
        for a in layer.anchors:
            if a.name == "top":
                anchors["top"] = (a.position.x + delta, a.position.y)
            elif a.name == "bottom":
                anchors["bottom"] = (re_((xO + sr_x) / 2, 0)[0], 0)
        print(f"{mname:26s} width {layer.width:g}->{w_new} (d={delta}) "
              f"w_hook={w_hook:.0f} H={H:.0f} xO={xO:.0f}")
        return {"replace_nodes": out, "width": w_new, "anchors": anchors}

    return edit, deltas


def bump_widths(glyph_name, font, deltas):
    def edit(mname, layer, nodes):
        return {"width": int(layer.width + deltas[layer.layerId])}
    assert apply_edit(GLYPHS_FILE, glyph_name, edit)
    print(f"{glyph_name}: widths += delta")


def fix_jcircumflex(font, deltas):
    """width += delta and accent transform tx += delta, per master."""
    masters = {m.id: m.name for m in font.masters}
    text = open(GLYPHS_FILE).read()
    bs = text.index("glyphname = Jcircumflex;")
    be = text.index("glyphname = ", bs + 1)
    block = text[bs:be]
    for layer in font.glyphs["Jcircumflex"].layers:
        if layer.layerId not in masters:
            continue
        d = deltas[layer.layerId]
        (acc,) = [c for c in layer.components if c.name != "J"]
        lstart = block.index(f'layerId = "{layer.layerId}";')
        wmatch = WIDTH_RE.search(block, lstart)
        prev = [m for m in WIDTH_RE.finditer(block) if m.start() < lstart]
        scope_start = prev[-1].end() if prev else 0
        scope = block[scope_start : wmatch.end()]
        # Glyphs 3 component transform: pos = (x,y) (angle/scale omitted when identity)
        old_t = f"pos = ({acc.position.x:g},{acc.position.y:g});"
        new_t = f"pos = ({acc.position.x + d:g},{acc.position.y:g});"
        assert scope.count(old_t) in (1, 2), (masters[layer.layerId], old_t, scope.count(old_t))
        new_scope = scope.replace(old_t, new_t)
        ow = WIDTH_RE.search(scope).group(1)
        new_scope = new_scope.replace(
            f"width = {ow};", f"width = {int(layer.width + d)};")
        assert block.count(scope) == 1
        block = block.replace(scope, new_scope)
    open(GLYPHS_FILE, "w").write(text[:bs] + block + text[be:])
    print("Jcircumflex: widths + accent transforms += delta")


if __name__ == "__main__":
    font = GSFont(GLYPHS_FILE)
    edit, deltas = edit_factory(font)
    assert apply_edit(GLYPHS_FILE, "J", edit)
    font2 = GSFont(GLYPHS_FILE)
    for name in WIDTH_ONLY_COMPOSITES:
        bump_widths(name, font2, deltas)
    fix_jcircumflex(font2, deltas)
    print("done")
