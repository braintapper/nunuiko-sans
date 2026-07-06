"""Shared machinery for glyph edits on the raw .glyphs file.

glyphsLib is used READ-ONLY to parse geometry; edits are applied as
targeted text surgery (GSFont.save drops kerning groups / feature code —
see PLAYBOOK.md). Node lines are replaced positionally, never by content
matching (a new coordinate can collide with a later node's line).

Nunito Sans note: this source is Glyphs 3 (.formatVersion = 3), whose
serialization differs from Nunito's Glyphs 2 file:
  - nodes are `(x,y,code)` tuples, code in o/c/cs/l/ls/q/qs, NOT the
    Glyphs 2 `"x y TYPE SMOOTH"` strings;
  - anchors use `pos = (x,y)`, NOT `position = "{x, y}"`.
"""
import re

from glyphsLib import GSFont

NUM = r"-?\d+(?:\.\d+)?"
# Glyphs 3 node: (x,y,code)
NODE_RE = re.compile(rf"\({NUM},{NUM},(?:o|c|cs|l|ls|q|qs)\)")
# widths may be fractional in interpolated / 6pt masters
WIDTH_RE = re.compile(rf"width = ({NUM});")

# glyphsLib (type, smooth) <-> Glyphs 3 one/two-letter code
_CODE_FOR = {
    ("offcurve", False): "o", ("offcurve", True): "o",
    ("curve", False): "c", ("curve", True): "cs",
    ("line", False): "l", ("line", True): "ls",
    ("qcurve", False): "q", ("qcurve", True): "qs",
}


def _num(v):
    # match Glyphs' own formatting: ints without a trailing .0
    return f"{v:.10g}"


def fmt_node(x, y, ntype, smooth):
    code = _CODE_FOR[(ntype.lower(), bool(smooth))]
    return f"({_num(x)},{_num(y)},{code})"


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
            old_width_str = wmatch.group(1)
            assert abs(float(old_width_str) - layer.width) < 1e-6, (
                mname, old_width_str, layer.width)
            new_region = new_region.replace(
                f"width = {old_width_str};", f"width = {result['width']};"
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
            old = f"pos = ({_num(a.position.x)},{_num(a.position.y)});"
            new = f"pos = ({round(nx):g},{round(ny):g});"
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
