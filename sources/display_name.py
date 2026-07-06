"""Set the public family name to "Nunuïko" (with diaeresis).

Only display-facing name records get the diacritic; PostScript names
(IDs 6, 25) and filenames stay ASCII "Nunuiko" to avoid fontconfig/CSS/
shell friction. Runs on all built variable fonts, after fix.py.
"""
import glob

from fontTools.ttLib import TTFont

ASCII_NAME = "Nunuiko Display"
DISPLAY_NAME = "Nunuïko Display"

# 1: family, 4: full name, 16: typographic family, 21: WWS family
DISPLAY_NAME_IDS = {1, 4, 16, 21}

if __name__ == "__main__":
    for font_path in glob.glob("../fonts/variable/*.ttf"):
        font = TTFont(font_path)
        name_table = font["name"]
        changed = False
        for record in name_table.names:
            if record.nameID not in DISPLAY_NAME_IDS:
                continue
            value = record.toUnicode()
            if ASCII_NAME in value:
                name_table.setName(
                    value.replace(ASCII_NAME, DISPLAY_NAME),
                    record.nameID,
                    record.platformID,
                    record.platEncID,
                    record.langID,
                )
                changed = True
        if changed:
            print("Set display name in {}".format(font_path))
            font.save(font_path)
