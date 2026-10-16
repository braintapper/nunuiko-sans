"""Glyph edit 14: plain l (like I) by default; the tailed l moves to ss02.

Nunuiko (the UI family) keeps the tailed l to disambiguate Il1. For
Nunuiko Display the user prefers an undisambiguated l that looks like the
capital I. Nunito Sans already has it: l.ss02 is a plain stem with the
same outline as I, and every l-based glyph has a complete .ss02 twin
built on it (same structure, consistent widths and kerning groups).

So the pairs SWAP NAMES (the outlines, widths, anchors and kerning groups
travel with their shape):
  l lacute lcaron lcommaaccent ldot ldotbelow lj llinebelow lslash fl f_f_l
  <->  the same + .ss02
Renamed everywhere a name points at a SHAPE: glyphname lines, component
refs (palochka-cy keeps the plain stem), kerning keys (llinebelow and
lslash have direct pairs, which belong to the tailed shapes), and dlig's
"sub f l by fl.ss02" (it meant the plain fl, now named fl). Unicode values
move to the new default glyphs. Feature code that means default vs
alternate (liga, ss02, ccmp, locl) is left as is: by name, l is now the
plain default and ss02 gives the tailed one.

Edits 01 (l tail) and 07 (fl width) now shape the ss02 alternates.
Run once per source:
  python3 edits/14_plain_l_default.py
  python3 edits/14_plain_l_default.py NunuikoDisplay-Italic.glyphs
"""
import re
import sys

GLYPHS_FILE = sys.argv[1] if len(sys.argv) > 1 else "NunuikoDisplay.glyphs"
BASES = ["l", "lacute", "lcaron", "lcommaaccent", "ldot", "ldotbelow", "lj",
         "llinebelow", "lslash", "fl", "f_f_l"]
SWAP = {}
for b in BASES:
    SWAP[b], SWAP[b + ".ss02"] = b + ".ss02", b
DLIG_OLD = "sub f l by fl.ss02;\n\";\ntag = dlig;"
DLIG_NEW = "sub f l by fl;\n\";\ntag = dlig;"


def block_span(text, name):
    m = f"{{\nglyphname = {name};\n"
    assert text.count(m) == 1, (name, text.count(m))
    s = text.index(m)
    return s, text.index("\n{\nglyphname = ", s + 1) + 1


def main():
    text = open(GLYPHS_FILE).read()
    assert "glyphname = l.ss02;" in text and DLIG_OLD in text, "already applied?"

    # unicode values stay with the base NAMES: note them before renaming
    uni = {}
    for b in BASES:
        s, e = block_span(text, b)
        m = re.search(r"^unicode = (\d+);\n", text[s:e], re.M)
        uni[b] = m.group(1) if m else None
        if m:
            text = text[:s] + text[s:e].replace(m.group(0), "", 1) + text[e:]

    sub = lambda m: m.group(1) + SWAP.get(m.group(2), m.group(2)) + m.group(3)
    text = re.sub(r"^(glyphname = )([^;\n]+)(;)$", sub, text, flags=re.M)
    text = re.sub(r"^(ref = )([^;\n]+)(;)$", sub, text, flags=re.M)

    # kerning keys, inside the kerningLTR dict only (brace-matched)
    ks = text.index("\nkerningLTR = {\n") + 1
    depth, i = 0, text.index("{", ks)
    while True:
        c = text[i]
        depth += c == "{"
        depth -= c == "}"
        i += 1
        if depth == 0:
            break
    kern = re.sub(r"^()([A-Za-z0-9_.]+)( = )", sub, text[ks:i], flags=re.M)
    text = text[:ks] + kern + text[i:]

    assert text.count(DLIG_OLD) == 1
    text = text.replace(DLIG_OLD, DLIG_NEW)

    for b in BASES:  # unicode back on the (new) default glyphs
        if uni[b] is None:
            continue
        s, e = block_span(text, b)
        # right after the glyphname line: always glyph level (a layer can
        # carry its own userData, so anchoring on that is unsafe)
        head = f"{{\nglyphname = {b};\n"
        text = text[:s] + head + f"unicode = {uni[b]};\n" + text[s + len(head):]
    open(GLYPHS_FILE, "w").write(text)
    print("swapped", len(BASES), "pairs in", GLYPHS_FILE)


if __name__ == "__main__":
    main()
