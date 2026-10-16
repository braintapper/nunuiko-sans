"""Glyph edit 10: round dots — every square dot becomes a circle.

Nunito Sans draws its dots (i j, dieresis, dot accent, dot below, period,
colon, semicolon, ! ? and their inverted forms, middle dot, divide, the
dots inside stacked accents...) as plain 4-point rectangles. Replace each
with a 4-segment circle.

Which contours: a path is a dot when, in EVERY master, it is 4 line nodes
forming a rectangle (upright) or a parallelogram slanted at the italic
angle (italic): two horizontal edges of equal width, aspect 0.6-1.7.
Acute/grave strokes (other slants) and the ff bridge (unequal top and
bottom) don't qualify.

Size, per master: the circle has the same area as a square of side
sqrt(w*h) (d = 2*sqrt(w*h/pi), ~1.128x the side), the usual optical
correction so a round dot doesn't read smaller than the square. Capped at
1.128x the height, so the squashed dots in heavy stacked accents
(e.g. 168x115) grow upward no more than a square one would. Centred on the
rectangle's centre. Dots stay round in the italic (not slanted).

Direction and start: the circle runs in the same direction as the
rectangle it replaces, starting at its bottom, in every master, so all
masters stay compatible. Only master layers are written (no glyph here has
brace layers; the unnamed 6pt ExtraLight backups don't export).

Composites (ä, ï, ȧ, ḅ, ŀ...) use these as components and follow.
Run once per source:
  python3 edits/10_round_dots.py
  python3 edits/10_round_dots.py NunuikoDisplay-Italic.glyphs
Add --dry-run to list the dots without writing.
"""
import math
import re
import sys

from glyphsLib import GSFont

args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry-run" in sys.argv
GLYPHS_FILE = args[0] if args else "NunuikoDisplay.glyphs"
KAPPA = 0.5522847498
AREA = 2 / math.sqrt(math.pi)  # circle diameter / square side, equal area
SLANT_TOL = 1.5  # degrees from the italic angle
NODES_RE = re.compile(r"nodes = \(\n.*?\n\);", re.S)


def dot_shape(path, italic_angle):
    """(cx, cy, w, h, ccw) if path is a square-ish dot, else None."""
    n = path.nodes
    if len(n) != 4 or any(q.type != "line" for q in n):
        return None
    P = [(q.position.x, q.position.y) for q in n]
    ys = sorted({y for _, y in P})
    if len(ys) != 2:
        return None
    h = ys[1] - ys[0]
    bot = sorted(x for x, y in P if y == ys[0])
    top = sorted(x for x, y in P if y == ys[1])
    if len(bot) != 2 or len(top) != 2 or h <= 0:
        return None
    w = bot[1] - bot[0]
    if abs(w - (top[1] - top[0])) > 1 or not 0.6 < w / h < 1.7:
        return None
    slant = math.degrees(math.atan2(top[0] - bot[0], h))
    if abs(slant - italic_angle) > SLANT_TOL:
        return None
    # shoelace: positive = counter-clockwise (y up)
    area2 = sum(P[i][0] * P[(i + 1) % 4][1] - P[(i + 1) % 4][0] * P[i][1]
                for i in range(4))
    cx = sum(x for x, _ in P) / 4
    cy = (ys[0] + ys[1]) / 2
    return cx, cy, w, h, area2 > 0


def circle_nodes(cx, cy, d, ccw):
    """Glyphs 3 node lines for a circle, starting at the bottom point."""
    r = d / 2
    k = r * KAPPA
    # on-curve points from the bottom, with the unit tangent (direction
    # of travel) at each; each segment = 2 off-curves + on-curve
    if ccw:
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        tang = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    else:
        pts = [(cx, cy - r), (cx - r, cy), (cx, cy + r), (cx + r, cy)]
        tang = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    out = []
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        ta, tb = tang[i], tang[(i + 1) % 4]
        c1 = (a[0] + ta[0] * k, a[1] + ta[1] * k)
        c2 = (b[0] - tb[0] * k, b[1] - tb[1] * k)
        out += [f"({round(c1[0])},{round(c1[1])},o)",
                f"({round(c2[0])},{round(c2[1])},o)",
                f"({round(b[0])},{round(b[1])},cs)"]
    return "nodes = (\n" + ",\n".join(out) + "\n);"


def main():
    text = open(GLYPHS_FILE).read()
    font = GSFont(GLYPHS_FILE)
    masters = {m.id: m for m in font.masters}
    total = 0
    for g in font.glyphs:
        layers = [l for l in g.layers if l.layerId in masters]
        if len(layers) != len(masters):
            continue
        npaths = {len(l.paths) for l in layers}
        if len(npaths) != 1:
            continue
        dots = {}
        for ci in range(npaths.pop()):
            shapes = [dot_shape(l.paths[ci], masters[l.layerId].italicAngle)
                      for l in layers]
            if all(shapes):
                dots[ci] = shapes
        if not dots:
            continue
        total += len(dots)
        sizes = [s for s in dots[min(dots)]]
        print(f"{g.name:30s} dots at contour {sorted(dots)}"
              f"  {sizes[0][2]:g}x{sizes[0][3]:g} .. {max(s[2] for s in sizes):g}x"
              f"{max(s[3] for s in sizes):g}")
        if DRY:
            continue

        marker = f"glyphname = {g.name};"
        if marker not in text:
            marker = f'glyphname = "{g.name}";'
        bs = text.index(marker)
        be = text.index("\nglyphname = ", bs + 1) if "\nglyphname = " in text[bs + 1:] else len(text)
        block = text[bs:be]
        for li, l in enumerate(layers):
            ls = block.index(f'layerId = "{l.layerId}";')
            le = re.compile(r"\nwidth = ").search(block, ls).start()
            region = block[ls:le]
            spans = [m.span() for m in NODES_RE.finditer(region)]
            assert len(spans) == len(l.paths), (g.name, l.layerId, len(spans))
            pieces, prev = [], 0
            for ci, (s, e) in enumerate(spans):
                pieces.append(region[prev:s])
                if ci in dots:
                    cx, cy, w, h, ccw = dots[ci][li]
                    d = min(AREA * math.sqrt(w * h), AREA * h)
                    pieces.append(circle_nodes(cx, cy, d, ccw))
                else:
                    pieces.append(region[s:e])
                prev = e
            pieces.append(region[prev:])
            block = block[:ls] + "".join(pieces) + block[le:]
        text = text[:bs] + block + text[be:]
    print(f"{total} dot contours" + (" (dry run)" if DRY else ""))
    if not DRY:
        open(GLYPHS_FILE, "w").write(text)
        print("written", GLYPHS_FILE)


if __name__ == "__main__":
    main()
