"""For each static TTF, also write an OTF (CFF outlines) and a WOFF, so a server
that cannot convert fonts itself receives all three formats ready-made."""
import glob, os, shutil, sys
from fontTools.ttLib import TTFont, newTable
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.qu2cuPen import Qu2CuPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.t2CharStringPen import T2CharStringPen

TT_ONLY = ["glyf", "loca", "cvt ", "fpgm", "prep", "gasp", "hdmx", "LTSH", "VDMX", "gvar", "cvar"]

def to_otf(src, dst):
    font = TTFont(src)
    glyph_set = font.getGlyphSet()
    order = font.getGlyphOrder()
    charstrings = {}
    for name in order:
        rec = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(rec)
        t2 = T2CharStringPen(glyph_set[name].width, glyph_set)
        rec.replay(Qu2CuPen(t2, max_err=0.5, all_cubic=True))
        charstrings[name] = t2.getCharString()
    ps_name = font["name"].getDebugName(6)
    for tag in TT_ONLY:
        if tag in font:
            del font[tag]
    fb = FontBuilder(font=font, isTTF=False)
    fb.setupCFF(ps_name, {"FullName": font["name"].getDebugName(4)}, charstrings, {})
    fb.setupMaxp()
    font["post"].formatType = 3.0
    font.sfntVersion = "OTTO"
    font.save(dst)

def to_woff(src, dst):
    font = TTFont(src)
    font.flavor = "woff"
    font.save(dst)

src_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)
for ttf in sorted(glob.glob(os.path.join(src_dir, "*.ttf"))):
    base = os.path.splitext(os.path.basename(ttf))[0]
    shutil.copy(ttf, os.path.join(out_dir, base + ".ttf"))
    to_otf(ttf, os.path.join(out_dir, base + ".otf"))
    to_woff(ttf, os.path.join(out_dir, base + ".woff"))
print(out_dir, len(os.listdir(out_dir)), "files")
