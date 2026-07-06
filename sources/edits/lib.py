"""Shared machinery for glyph edits on the raw .glyphs file.

glyphsLib is used READ-ONLY to parse geometry; edits are applied as
targeted text surgery (GSFont.save drops kerning groups / feature code —
see PLAYBOOK.md). Node lines are replaced positionally, never by content
matching (a new coordinate can collide with a later node's line).
"""
import re

from glyphsLib import GSFont

NUM = r"-?\d+(?:\.\d+)?"
NODE_RE = re.compile(rf'"{NUM} {NUM} (?:OFFCURVE|CURVE|LINE|QCURVE)(?: SMOOTH)?"')
WIDTH_RE = re.compile(r"width = (\d+);")


def fmt_node(x, y, ntype, smooth):
    s = f'"{x:.10g} {y:.10g} {ntype.upper()}'
    if smooth:
        s += " SMOOTH"
    return s + '"'


def apply_edit(glyphs_path, glyph_name, edit_fn):
    """Apply edit_fn to every master layer of glyph_name.

    edit_fn(master_name, layer, nodes) -> dict with optional keys:
      'nodes':   {global_node_index: (new_x, new_y)}  (index across all
                 paths, concatenated in order)
      'replace_nodes': full replacement outline for a SINGLE-path glyph:
                 list of (x, y, type, smooth) tuples — may change count
      'width':   new advance width (int)
      'anchors': {anchor_name: (new_x, new_y)}
    Coordinates are rounded to int. Returns True if the file changed.
    """
    text = open(glyphs_path).read()
    font = GSFont(glyphs_path)
    masters = {m.id: m.name for m in font.masters}

    # names with specials (e.g. "Je-cy") are quoted in the file
    marker = f"glyphname = {glyph_name};"
    if marker not in text:
        marker = f'glyphname = "{glyph_name}";'
    block_start = text.index(marker)
    block_end = text.index("glyphname = ", block_start + 1)
    block = text[block_start:block_end]

    for layer in font.glyphs[glyph_name].layers:
        if layer.layerId not in masters:
            continue
        mname = masters[layer.layerId]
        nodes = [n for p in layer.paths for n in p.nodes]
        result = edit_fn(mname, layer, nodes) or {}

        lstart = block.index(f'layerId = "{layer.layerId}";')
        wmatch = WIDTH_RE.search(block, lstart)
        region = block[lstart : wmatch.end()]

        if result.get("replace_nodes") is not None:
            assert len(layer.paths) == 1, (mname, "replace_nodes needs 1 path")
            assert region.count("nodes = (") == 1, mname
            ns = region.index("nodes = (")
            ne = region.index(");", ns) + 2
            lines = ",\n".join(
                fmt_node(round(x), round(y), t, sm)
                for x, y, t, sm in result["replace_nodes"]
            )
            new_region = region[:ns] + "nodes = (\n" + lines + "\n);" + region[ne:]
            region_replaced = True
        else:
            region_replaced = False

        new_coords = result.get("nodes", {})
        if new_coords and not region_replaced:
            spans = [m.span() for m in NODE_RE.finditer(region)]
            assert len(spans) == len(nodes), (mname, len(spans), len(nodes))
            pieces, prev = [], 0
            for i, (s, e) in enumerate(spans):
                n = nodes[i]
                old = fmt_node(n.position.x, n.position.y, n.type, n.smooth)
                assert region[s:e] == old, (mname, i, region[s:e], old)
                x, y = new_coords.get(i, (n.position.x, n.position.y))
                pieces.append(region[prev:s])
                pieces.append(fmt_node(round(x), round(y), n.type, n.smooth))
                prev = e
            pieces.append(region[prev:])
            new_region = "".join(pieces)
        elif not region_replaced:
            new_region = region

        if result.get("width") is not None:
            old_width = int(wmatch.group(1))
            assert old_width == layer.width, (mname, old_width, layer.width)
            new_region = new_region.replace(
                f"width = {old_width};", f"width = {result['width']};"
            )

        # this layer's full dict (anchors live BEFORE layerId): spans from
        # the previous layer's width line to this layer's width line
        prev_widths = [m for m in WIDTH_RE.finditer(block) if m.start() < lstart]
        scope_start = prev_widths[-1].end() if prev_widths else 0
        scope = block[scope_start : wmatch.end()]
        new_scope = scope.replace(region, new_region)

        # anchors mirror in the background copy: 1-2 occurrences per layer
        for a in layer.anchors:
            if a.name not in result.get("anchors", {}):
                continue
            nx, ny = result["anchors"][a.name]
            old = f'position = "{{{a.position.x:g}, {a.position.y:g}}}";'
            new = f'position = "{{{round(nx):g}, {round(ny):g}}}";'
            count = new_scope.count(old)
            assert count in (1, 2), (mname, a.name, count)
            new_scope = new_scope.replace(old, new)

        assert block.count(scope) == 1
        block = block.replace(scope, new_scope)

    new_text = text[:block_start] + block + text[block_end:]
    if new_text == text:
        return False
    open(glyphs_path, "w").write(new_text)
    return True
