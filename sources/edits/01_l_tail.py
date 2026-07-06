"""Glyph edit 1 (+1b): shorten the tail of lowercase l.

Rule (see GLYPHLOG.md): compress the tail region horizontally toward the
stem's bottom-right edge (pivot = node 14 x, per master) by FACTOR.
Tail region = node indices 0-13 (terminal cap + inner sweep) and 23-25
(outer bottom curve); stem/top nodes 14-22 untouched. Advance width
shrinks by the tail tip's retreat. Anchors `bottom` and `dot` follow the
same compression; `top`, `topright`, `center` stay.

Refinement 1b (user feedback): the compression squashes the tip's
TOP-RIGHT corner arc (nodes 5 -> 6,7 -> 8) to 0.6 of its x-extent, which
reads as a sharp corner. After compressing, restore that arc's original
x-extent: node 8 moves left to newx5 - (origx5 - origx8), control 7
keeps its original x-offset from node 8, control 6 stays on node 5's
vertical, and the top-edge controls 9,10 are redistributed at their
original fractions of the 8 -> 11 span. y is never touched, and every
junction (4-5-6 vertical, 7-8-9 and 10-11-12 horizontal) stays exactly
collinear, so all SMOOTH joints survive. A rigid (untranslated) cap was
considered instead but does not fit: Heavy's cap is deeper (72 units)
than the whole shortened tail extent (67).

Compression is affine in x, so collinear points stay collinear. Same
26-node structure required in every master (asserted).

Text-surgery on the .glyphs file — glyphsLib is used read-only for
parsing (its save drops kerning groups / feature code; see PLAYBOOK.md).
Run once from sources/: python3 edits/01_l_tail.py
Backgrounds are left untouched (they don't ship), EXCEPT anchors, which
are mirrored in backgrounds and kept in sync.
"""
import re
import sys

from glyphsLib import GSFont

GLYPHS_FILE = "Nunuiko.glyphs"
GLYPH = "l"
FACTOR = 0.6
PIVOT_NODE = 14  # stem bottom-right junction; also first untouched node
TAIL_NODES = list(range(0, 14)) + [23, 24, 25]
# top-right corner arc of the tip: node 5 (right edge) -> 6,7 -> 8 (top
# edge), then controls 9,10 into node 11 (top edge inner end)
CORNER = (5, 6, 7, 8, 9, 10, 11)
MAX_CORNER_FRAC = 0.65  # corner arc's max share of the cap-top x-span
EXPECTED_NODE_COUNT = 26
MOVE_ANCHORS = {"bottom", "dot"}


def fmt_node(x, y, ntype, smooth):
    s = f'"{x:g} {y:g} {ntype.upper()}'
    if smooth:
        s += " SMOOTH"
    return s + '"'


def compress(x, pivot):
    return round(pivot + FACTOR * (x - pivot))


def main():
    text = open(GLYPHS_FILE).read()
    font = GSFont(GLYPHS_FILE)
    masters = {m.id: m.name for m in font.masters}
    glyph = font.glyphs[GLYPH]

    # scope all replacements to this glyph's block
    block_start = text.index(f"glyphname = {GLYPH};")
    block_end = text.index("glyphname = ", block_start + 1)
    block = text[block_start:block_end]

    for layer in glyph.layers:
        if layer.layerId not in masters:
            continue
        mname = masters[layer.layerId]
        (path,) = layer.paths
        nodes = path.nodes
        assert len(nodes) == EXPECTED_NODE_COUNT, (mname, len(nodes))
        pivot = nodes[PIVOT_NODE].position.x
        old_tip = max(n.position.x for n in nodes)
        ox = [n.position.x for n in nodes]

        # base rule: compress tail-node x toward the pivot
        newx = [compress(x, pivot) if i in TAIL_NODES and x > pivot else x
                for i, x in enumerate(ox)]

        # 1b: restore the top-right corner arc's x-extent toward the
        # original, capped so the remaining top edge keeps >= 35% of the
        # cap-top span (the heavy masters' corners are too big to fit)
        n5, n6, n7, n8, n9, n10, n11 = CORNER
        assert ox[n6] == ox[n5], (mname, "corner entry not vertical")
        rx_orig = ox[n5] - ox[n8]
        rx = min(rx_orig, MAX_CORNER_FRAC * (newx[n5] - newx[n11]))
        newx[n8] = newx[n5] - round(rx)
        newx[n7] = newx[n8] + round((ox[n7] - ox[n8]) * rx / rx_orig)
        for c in (n9, n10):  # original fractions of the 8 -> 11 span
            f = (ox[n8] - ox[c]) / (ox[n8] - ox[n11])
            newx[c] = round(newx[n8] - f * (newx[n8] - newx[n11]))
        assert newx[n11] < newx[n10] < newx[n9] < newx[n8] < newx[n7], mname
        print(f"{mname:20s} corner rx {rx_orig:g} -> {rx:.0f}"
              f" (bare compression would give {FACTOR * rx_orig:.0f})")

        # active outline region: from this layerId line to its width line
        lstart = block.index(f'layerId = "{layer.layerId}";')
        wmatch = re.compile(r"width = (\d+);").search(block, lstart)
        region = block[lstart : wmatch.end()]

        # positional replacement: node lines appear in file in node order;
        # matching by content is unsafe (a compressed line can collide with
        # a later original line)
        node_re = re.compile(r'"-?\d+ -?\d+ (?:OFFCURVE|CURVE|LINE|QCURVE)(?: SMOOTH)?"')
        spans = [m.span() for m in node_re.finditer(region)]
        assert len(spans) == EXPECTED_NODE_COUNT, (mname, len(spans))
        pieces, prev = [], 0
        for i, (s, e) in enumerate(spans):
            n = nodes[i]
            x, y = n.position.x, n.position.y
            old = fmt_node(x, y, n.type, n.smooth)
            assert region[s:e] == old, (mname, i, region[s:e], old)
            x = newx[i]
            pieces.append(region[prev:s])
            pieces.append(fmt_node(x, y, n.type, n.smooth))
            prev = e
        pieces.append(region[prev:])
        new_region = "".join(pieces)

        new_tip = compress(old_tip, pivot)
        old_width = int(wmatch.group(1))
        assert old_width == layer.width
        new_width = old_width - (old_tip - new_tip)
        new_region = new_region.replace(
            f"width = {old_width};", f"width = {new_width};"
        )
        block = block.replace(region, new_region)
        print(
            f"{mname:20s} pivot={pivot:g} tip {old_tip:g}->{new_tip}"
            f" width {old_width}->{new_width}"
        )

        # anchors: appear twice per layer (active + background), same values
        for a in layer.anchors:
            if a.name not in MOVE_ANCHORS or a.position.x <= pivot:
                continue
            old = f'position = "{{{a.position.x:g}, {a.position.y:g}}}";'
            new = (
                f'position = "{{{compress(a.position.x, pivot):g},'
                f" {a.position.y:g}}}\";"
            )
            assert block.count(old) == 2, (mname, a.name, old)
            block = block.replace(old, new)
            print(f"{'':20s} anchor {a.name}: x {a.position.x:g}"
                  f" -> {compress(a.position.x, pivot)}")

    new_text = text[:block_start] + block + text[block_end:]
    if new_text == text:
        sys.exit("nothing changed — already applied?")
    open(GLYPHS_FILE, "w").write(new_text)
    print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
