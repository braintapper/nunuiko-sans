"""Glyph edit 5: capital J — upturned hooked foot, widened to 66% of U.

Reference: Google Sans Flex J. Nunito's J sweeps left and dies at the
baseline; the new foot is a U-hook: down the stem, around the bowl, up
the left side, ending in a rounded cap built exactly like the stem's own
top cap. The glyph is also WIDENED: advance = WIDTH_FRAC_OF_U x U's
width (user spec — the original bowl was far too narrow for the font's
proportions). All growth happens bowl-side: the stem (and top cap)
shifts right by delta = W_new - W_old; LSB (hook outer extent) and RSB
are both preserved.

Landmarks per master (from J's own outline):
  - stem right/left x + curve-start y   (old nodes 3 / 11, shifted +delta)
  - hook outer left xO                  (old node 18 — LSB preserved)
  - inner bottom y (keeps original bottom taper)   (old node 14)
  - outer bottom overshoot              (old node 0)
  - hook weight = min(stem weight, HOOK_MAX_FRAC * (stem_left - xO));
    with the wider bowl EL/Bold get full stem weight, Heavy 215 -> ~133
  - terminal height H = H_FRAC * stem curve-start y
Italics: landmarks deslanted by tan(9 deg), built upright, reslanted.

Composites follow: IJ, I_J.loclNLD, Iacute_J.loclNLD, Je-cy, LJ, NJ get
width += delta (their J component offsets stay — growth is inside J's
box); Jcircumflex gets width += delta AND its circumflexcomb.case
transform tx += delta (the accent tracks the shifted stem).

22 -> 26 nodes. Run once from sources/: python3 edits/05_J_hook.py
"""
import math
import re

from glyphsLib import GSFont

from lib import WIDTH_RE, apply_edit

GLYPHS_FILE = "Nunuiko.glyphs"
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
        assert len(nodes) == 22, (mname, len(nodes))
        for i, t, sm in ((0, "line", True), (3, "curve", True),
                         (4, "line", True), (11, "line", True),
                         (14, "curve", True), (18, "curve", True)):
            assert nodes[i].type == t and nodes[i].smooth == sm, (mname, i)

        w_new = round(WIDTH_FRAC_OF_U * u_width[layer.layerId])
        delta = w_new - layer.width
        deltas[layer.layerId] = delta

        s = SLANT if "Italic" in mname else 0.0
        de = lambda n: (n.position.x - s * n.position.y, n.position.y)
        re_ = lambda x, y: (x + s * y, y)

        sr_x, y3 = de(nodes[3])
        sl_x, y11 = de(nodes[11])
        sr_x += delta
        sl_x += delta
        xO = de(nodes[18])[0]
        apexI_y = nodes[14].position.y
        apexO_y = nodes[0].position.y

        w_stem = sr_x - sl_x
        w_hook = min(w_stem, HOOK_MAX_FRAC * (sl_x - xO))
        xI = xO + w_hook
        H = H_FRAC * y3
        rise = w_hook / 2
        midx = (xO + xI) / 2
        apexI_x = (sl_x + xI) / 2
        apexO_x = (sr_x + xO) / 2
        k = KAPPA

        def orig(i):
            n = nodes[i]
            return (n.position.x + delta, n.position.y, n.type, n.smooth)

        out = [
            (*re_(sr_x, y3), "curve", True),
            orig(4), orig(5), orig(6), orig(7), orig(8), orig(9), orig(10),
            orig(11),
            (*re_(sl_x, y11 - k * (y11 - apexI_y)), "offcurve", False),
            (*re_(apexI_x + k * (sl_x - apexI_x), apexI_y), "offcurve", False),
            (*re_(apexI_x, apexI_y), "curve", True),
            (*re_(apexI_x - k * (apexI_x - xI), apexI_y), "offcurve", False),
            (*re_(xI, apexI_y + k * (H - apexI_y)), "offcurve", False),
            (*re_(xI, H), "curve", True),
            (*re_(xI, H + k * rise), "offcurve", False),
            (*re_(midx + k * (xI - midx), H + rise), "offcurve", False),
            (*re_(midx, H + rise), "curve", True),
            (*re_(midx - k * (midx - xO), H + rise), "offcurve", False),
            (*re_(xO, H + k * rise), "offcurve", False),
            (*re_(xO, H), "curve", True),
            (*re_(xO, H - k * (H - apexO_y)), "offcurve", False),
            (*re_(apexO_x - k * (apexO_x - xO), apexO_y), "offcurve", False),
            (*re_(apexO_x, apexO_y), "curve", True),
            (*re_(apexO_x + k * (sr_x - apexO_x), apexO_y), "offcurve", False),
            (*re_(sr_x, y3 - k * (y3 - apexO_y)), "offcurve", False),
        ]
        assert len(out) == 26
        anchors = {}
        for a in layer.anchors:
            if a.name == "top":
                anchors["top"] = (a.position.x + delta, a.position.y)
            elif a.name == "bottom":
                anchors["bottom"] = (re_((xO + sr_x) / 2, 0)[0], 0)
        print(f"{mname:20s} width {layer.width:g}->{w_new} (d={delta}) "
              f"w_hook={w_hook:.0f} H={H:.0f}")
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
        old_t = (f'transform = "{{1, 0, 0, 1, {acc.position.x:g},'
                 f" {acc.position.y:g}}}\";")
        new_t = (f'transform = "{{1, 0, 0, 1, {acc.position.x + d:g},'
                 f" {acc.position.y:g}}}\";")
        # background copy may be absent in some layers
        assert scope.count(old_t) in (1, 2), (masters[layer.layerId], old_t)
        new_scope = scope.replace(old_t, new_t)
        new_scope = new_scope.replace(
            f"width = {int(layer.width)};",
            f"width = {int(layer.width + d)};")
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
