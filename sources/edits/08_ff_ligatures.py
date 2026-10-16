"""Glyph edit 8: ff / ffi / ffl ligatures with a joined crossbar.

Nunito Sans has no ff ligature: "ff" is two f's pulled together by the
f-f kern. The crossbars have square ends that meet head on, but the kern
does not close them at the light end: the gap is 11 units at 12pt
ExtraLight (about 2 at Regular), 21 Condensed, 55 at 6pt, before the bars
start to overlap toward Bold (user-reported "teeny tiny gap").

Rule, per master:
  offset = width(f) + kern(@MMK_L_f, @MMK_R_f)   (where the kerned 2nd f sits)
  glyph  = bridge path + component f at 0 + component <second> at offset
  bridge = quad over the bar band, from the first f's stem right edge
           (nodes 1 bottom, 4 top) to the second f's stem left edge
           (nodes 20 bottom, 17 top, + offset). Spanning stem to stem
           keeps it the right way round in every master, whether the bars
           gap or overlap there, so the union is one flat bar. Works on
           the italic masters unchanged: the bar is horizontal there too.
  width  = offset + width(<second>)

Glyphs (second component): f_f (f), f_f_i (fi), f_f_l (fl),
f_f_l.ss02 (fl.ss02). fi is drawn rather than built from f, so for f_f_i
the bridge ends on fi's own stem points (its bar can sit off f's, e.g.
5 units higher in ExtraBlack YTLC Max; the bridge ramps). Carets: caret_1 at offset, caret_2 at
offset + the second glyph's caret_1. Kerning groups: left f, right taken
from the second glyph. liga/ss02 feature code gets the matching subs.
Only master layers are written; the unnamed backup layers every glyph
carries on 6pt ExtraLight don't export.

Text-surgery on the .glyphs file (see lib.py). Run once per source:
  python3 edits/08_ff_ligatures.py
  python3 edits/08_ff_ligatures.py NunuikoDisplay-Italic.glyphs
"""
import sys

from glyphsLib import GSFont

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"
# name -> (second component, unicode or None)
LIGATURES = {
    "f_f": ("f", 0xFB00),
    "f_f_i": ("fi", 0xFB03),
    "f_f_l": ("fl", 0xFB04),
    "f_f_l.ss02": ("fl.ss02", None),
}
INSERT_BEFORE = "{\nglyphname = ordfeminine;\n"
STEM_R_BOTTOM, STEM_R_TOP = 1, 4  # first f: stem right edge at the bar
STEM_L_TOP, STEM_L_BOTTOM = 17, 20  # second f: stem left edge at the bar
BAR_BOTTOM, BAR_TOP = 2, 3  # bar's right end, for the band's y

LIGA_OLD = "code = \"lookupflag IgnoreMarks;\nsub f i by fi;\nsub f l by fl;\n\";\ntag = liga;"
LIGA_NEW = ("code = \"lookupflag IgnoreMarks;\nsub f f i by f_f_i;\n"
            "sub f f l by f_f_l;\nsub f f by f_f;\nsub f i by fi;\n"
            "sub f l by fl;\n\";\ntag = liga;")
SS02_OLD = "sub fl by fl.ss02;\n\";"
SS02_NEW = "sub fl by fl.ss02;\nsub f_f_l by f_f_l.ss02;\n\";"


def num(v):
    return f"{round(v, 3):g}"


def layer_text(master_id, offset, second, width, bridge, carets):
    anchors = ",\n".join(
        f"{{\nname = caret_{i};\npos = ({num(x)},0);\n}}"
        for i, x in enumerate(carets, 1)
    )
    nodes = ",\n".join(f"({num(x)},{num(y)},l)" for x, y in bridge)
    return (f"{{\nanchors = (\n{anchors}\n);\nlayerId = \"{master_id}\";\n"
            f"shapes = (\n{{\nclosed = 1;\nnodes = (\n{nodes}\n);\n}},\n"
            f"{{\nref = f;\n}},\n{{\npos = ({num(offset)},0);\nref = {second};\n}}\n"
            f");\nwidth = {num(width)};\n}}")


def main():
    text = open(GLYPHS_FILE).read()
    font = GSFont(GLYPHS_FILE)
    for name in LIGATURES:
        if font.glyphs[name] is not None:
            sys.exit(f"{name} already exists — already applied?")
    masters = [m.id for m in font.masters]
    mnames = {m.id: m.name for m in font.masters}

    def master_layer(glyph, mid):
        return next(l for l in font.glyphs[glyph].layers if l.layerId == mid)

    blocks = []
    for name, (second, uni) in LIGATURES.items():
        layers = []
        for mid in masters:
            f = master_layer("f", mid)
            n = f.paths[0].nodes
            assert len(n) == 22, (mnames[mid], len(n))
            pos = lambda i: (n[i].position.x, n[i].position.y)
            yb, yt = pos(BAR_BOTTOM)[1], pos(BAR_TOP)[1]
            rb, rt = pos(STEM_R_BOTTOM), pos(STEM_R_TOP)
            lt, lb = pos(STEM_L_TOP), pos(STEM_L_BOTTOM)
            assert rb[1] == lb[1] == yb and rt[1] == lt[1] == yt, mnames[mid]
            kern = font.kerning[mid]["@MMK_L_f"]["@MMK_R_f"]
            offset = f.width + kern
            if second == "fi":
                # drawn, not a component of f: its f part has two extra
                # nodes, so f's 17-20 are fi's 19-22. The bar can sit a
                # little off f's (ExtraBlack YTLC Max: 5 units higher), so
                # the bridge ends on fi's own points and ramps across the
                # gap instead of stepping.
                m = master_layer("fi", mid).paths[0].nodes
                assert len(m) == 24, (mnames[mid], len(m))
                p2 = lambda i: (m[i + 2].position.x, m[i + 2].position.y)
                lt, lb = p2(STEM_L_TOP), p2(STEM_L_BOTTOM)
                # same structure as f: bar runs left from the stem at the
                # top (17 -> 18) and back from its left end at the bottom
                # (19 -> 20)
                assert (p2(18)[1] == lt[1] and p2(19)[1] == lb[1]
                        and p2(18)[0] < lt[0] and p2(19)[0] < lb[0]), (
                    mnames[mid], "fi structure")
                if (lb[1], lt[1]) != (yb, yt):
                    print(f"{'':11s} {mnames[mid]}: fi bar {lb[1]:g}-{lt[1]:g}"
                          f" vs f {yb:g}-{yt:g}, bridge ramps")
            bridge = [rb, (lb[0] + offset, lb[1]), (lt[0] + offset, lt[1]), rt]
            assert rb[0] < bridge[1][0] and rt[0] < bridge[2][0], mnames[mid]
            sec = master_layer(second, mid)
            carets = [offset] + [offset + a.position.x for a in sec.anchors
                                 if a.name == "caret_1"]
            width = offset + sec.width
            layers.append(layer_text(mid, offset, second, width, bridge, carets))
            print(f"{name:11s} {mnames[mid]:34s} offset {num(offset)}"
                  f" width {num(width)} bar gap {num(pos(19)[0] + offset - pos(BAR_BOTTOM)[0])}")
        right = font.glyphs[second].rightKerningGroup
        block = (f"{{\nglyphname = {name};\nkernLeft = f;\nkernRight = {right};\n"
                 f"layers = (\n" + ",\n".join(layers) + "\n);\n"
                 + (f"unicode = {uni};\n" if uni else "") + "},\n")
        blocks.append(block)

    assert text.count(INSERT_BEFORE) == 1
    text = text.replace(INSERT_BEFORE, "".join(blocks) + INSERT_BEFORE)
    for old, new in ((LIGA_OLD, LIGA_NEW), (SS02_OLD, SS02_NEW)):
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    open(GLYPHS_FILE, "w").write(text)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
