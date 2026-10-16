"""Glyph edit 13: proportional 1 by default, tabular 1 under tnum.

Every figure is tabular (600). Without its foot (edit 12) the 1 is a narrow
stem + flag in that 600 advance, so typed numbers with 1s (2011, 1,111)
open up around it (user-reported, even after centring). Give the default
1 proportional spacing and keep the tabular, centred 1 for tables:

  one, one.tosf   outline shifted, advance narrowed:
                    RSB = I's sidebearing (straight stem next to the
                          neighbour, same master)
                    LSB = LSB_FRAC x that (the flag leaves open space
                          under it)
                  measured unslanted, so the italic follows the slant
  one.tf,         NEW: component of the STOCK footed 1 (one.ss01 /
  one.tosf.tf     one.tosf.ss01 since edit 12's swap), 600 wide. User: the
                  foot gives the tabular 1 better optical balance
  tnum            NEW feature after onum: one -> one.tf,
                  one.tosf -> one.tosf.tf
  ss01            + one.tf -> one.ss01, one.tosf.tf -> one.tosf.ss01, so
                  the footed 1 still comes through with tnum on

Fraction / super / subscript figures (one.dnom etc.) stay tabular.
Only master layers are written. Run once per source:
  python3 edits/13_one_proportional.py
  python3 edits/13_one_proportional.py NunuikoDisplay-Italic.glyphs
"""
import math
import sys

from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"
LSB_FRAC = 0.75
PAIRS = (("one", "one.tf"), ("one.tosf", "one.tosf.tf"))
TABULAR = {"one.tf": "one.ss01", "one.tosf.tf": "one.tosf.ss01"}  # footed
INSERT_BEFORE = "{\nglyphname = one.dnom;\n"
ONUM_END = "sub nine by nine.tosf;\n\";\ntag = onum;\n},\n"
TNUM = ("{\ncode = \"sub one by one.tf;\nsub one.tosf by one.tosf.tf;\n\";\n"
        "tag = tnum;\n},\n")
SS01_OLD = "sub one.tosf by one.tosf.ss01;\n"
SS01_NEW = ("sub one.tosf by one.tosf.ss01;\nsub one.tf by one.ss01;\n"
            "sub one.tosf.tf by one.tosf.ss01;\n")

font = GSFont(GLYPHS_FILE)
masters = {m.name: m for m in font.masters}
for _, tf in PAIRS:
    if font.glyphs[tf] is not None:
        sys.exit(f"{tf} already exists — already applied?")


def unslanted_x(layer, tan):
    return [n.position.x - n.position.y * tan for n in layer.paths[0].nodes]




def proportional(mname, layer, nodes):
    m = masters[mname]
    tan = math.tan(math.radians(m.italicAngle))
    ux = unslanted_x(layer, tan)
    i_lay = font.glyphs["I"].layers[m.id]
    ix = unslanted_x(i_lay, tan)
    sb = (min(ix) + (i_lay.width - max(ix))) / 2
    lsb, rsb = LSB_FRAC * sb, sb
    shift = lsb - min(ux)
    width = round(lsb + (max(ux) - min(ux)) + rsb)
    print(f"{mname:34s} {layer.parent.name:9s} sidebearings {lsb:.0f}/{rsb:.0f}"
          f"  width {layer.width:g} -> {width}")
    return {"nodes": {i: (n.position.x + shift, n.position.y)
                      for i, n in enumerate(nodes)},
            "width": width}


def tabular_block(base, tf):
    layers = []
    for m in font.masters:
        w = font.glyphs[TABULAR[tf]].layers[m.id].width  # 600
        layers.append(f"{{\nlayerId = \"{m.id}\";\nshapes = (\n{{\n"
                      f"ref = {TABULAR[tf]};\n}}\n);\nwidth = {w:g};\n}}")
    return f"{{\nglyphname = {tf};\nlayers = (\n" + ",\n".join(layers) + "\n);\n},\n"


if __name__ == "__main__":
    for base, _ in PAIRS:
        assert apply_edit(GLYPHS_FILE, base, proportional)
    blocks = "".join(tabular_block(base, tf) for base, tf in PAIRS)
    text = open(GLYPHS_FILE).read()
    for old, new in ((INSERT_BEFORE, blocks + INSERT_BEFORE),
                     (ONUM_END, ONUM_END + TNUM),
                     (SS01_OLD, SS01_NEW)):
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    open(GLYPHS_FILE, "w").write(text)
    print("written", GLYPHS_FILE)
