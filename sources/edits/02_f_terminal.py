"""Glyph edit 2: slight downturn on the f top terminal.

Rule (see GLYPHLOG.md): rotate the terminal section clockwise by ANGLE
about the hook-underside junction (the "neck"). The terminal section is
located by pattern, not fixed indices, so it also finds the hook inside
the separately-drawn `fi` ligature:

  [p]   curve smooth   <- pivot (underside neck)
  [p+1] line  smooth   <- underside end of terminal
  [p+2] offcurve
  [p+3] offcurve       <- cap outer control = path's y-max
  [p+4] curve smooth   <- topside end of cap
  [p+5] line  smooth   <- topside neck
  [p+6] offcurve       <- first handle of the long top curve

Rotating p+1..p+6 about p is an isometry with the pivot on the incoming
smooth chain, so every SMOOTH joint is preserved exactly; the long top
curve reshapes smoothly via the rotated p+6 handle.

`florin` has a different terminal construction (flat ball) — left stock.
`fl`, `fl.ss02` are components of f — inherit automatically.

Run once from sources/: python3 edits/02_f_terminal.py
"""
import math

from lib import apply_edit

ANGLE_DEG = 12  # clockwise = downturn on the right


PATTERN = [
    ("curve", True), ("line", True), ("offcurve", False),
    ("offcurve", False), ("curve", True), ("line", True),
    ("offcurve", False),
]


def matches(nodes, p):
    if p < 0 or p + len(PATTERN) > len(nodes):
        return False
    return all(nodes[p + off].type == t and nodes[p + off].smooth == sm
               for off, (t, sm) in enumerate(PATTERN))


def find_terminal(nodes):
    """Find every occurrence of the terminal pattern and take the one
    whose cap control (p+3) sits highest — the hook tip. (Absolute y-max
    is unreliable: in some fi masters the i-dot is the highest point.)"""
    hits = [p for p in range(len(nodes)) if matches(nodes, p)]
    assert hits, "terminal pattern not found"
    return max(hits, key=lambda p: nodes[p + 3].position.y)


def rotate_cw(x, y, px, py, deg):
    a = math.radians(deg)
    dx, dy = x - px, y - py
    return (px + dx * math.cos(a) + dy * math.sin(a),
            py - dx * math.sin(a) + dy * math.cos(a))


def edit(mname, layer, nodes):
    p = find_terminal(nodes)
    px, py = nodes[p].position.x, nodes[p].position.y
    new = {}
    for i in range(p + 1, p + 7):
        n = nodes[i]
        new[i] = rotate_cw(n.position.x, n.position.y, px, py, ANGLE_DEG)
    tip_old = max(n.position.x for n in nodes[p + 1 : p + 7])
    tip_new = max(x for x, _ in new.values())
    print(f"{mname:20s} pivot n{p} ({px:g},{py:g})  "
          f"tip x {tip_old:g}->{tip_new:.0f}")
    return {"nodes": new}


if __name__ == "__main__":
    for glyph in ("f", "fi"):
        print(f"--- {glyph}")
        changed = apply_edit("Nunuiko.glyphs", glyph, edit)
        assert changed, glyph
    print("done")
