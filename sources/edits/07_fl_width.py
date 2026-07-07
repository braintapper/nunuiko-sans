"""Glyph edit 7: fix `fl` trailing advance after the `l` tail edit.

`fl` is a composite (f + l components); its advance was authored as
`l_offset + l's_original_advance`. Edit 01 shortened `l` and reduced its
advance, but `fl`'s width was never updated, leaving 29-71 units of extra
space before the following character (user-reported). Restore the tight fit
by setting each master's width to `l_offset + l's current advance` — this
removes exactly the l-tail retreat, so l's right sidebearing inside the
ligature is unchanged.

`ffl` shapes to f + `fl` (no ff/ffl glyph exists), so this fixes it too.
`fl.ss02` is already consistent (its `l.ss02` component was not tail-edited)
and is left alone. Run once: python3 edits/07_fl_width.py
"""
from glyphsLib import GSFont

from lib import apply_edit

GLYPHS_FILE = "NunuikoDisplay.glyphs"

# l's current advance per master id (post edit 01)
_font = GSFont(GLYPHS_FILE)
_lw = {l.layerId: l.width for l in _font.glyphs["l"].layers}


def edit(mname, layer, nodes):
    lx = next(c.position.x for c in layer.components if c.componentName == "l")
    new_w = round(lx + _lw[layer.layerId])
    if new_w == round(layer.width):
        print(f"{mname:26s} stays {layer.width:.0f}")
        return {}
    print(f"{mname:26s} width {layer.width:.0f} -> {new_w}")
    return {"width": new_w}


if __name__ == "__main__":
    assert apply_edit(GLYPHS_FILE, "fl", edit)
    print("done")
