"""Build the Nunuïko specimen/diff proof page (self-contained HTML).

Embeds four variable fonts as base64 woff2: the ORIGINAL upstream Nunito
(pulled from git history so it never drifts) and the CURRENT Nunuïko build
outputs. The result is published as a Claude artifact after each glyph
edit — same URL each time, so it doubles as a visual changelog.

Run from the repo root:  .venv/bin/python sources/proof/make_proof.py
Output: sources/proof/nunuiko-proof.html (gitignored; regenerate at will)

Nunito Sans fork: change ORIG_COMMIT/paths to that repo's originals and
swap the display strings in template.html.
"""
import base64
import pathlib
import subprocess
import tempfile

from fontTools.ttLib.woff2 import compress

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent

# last upstream commit before the rename/edits — the pristine Nunito
ORIG_COMMIT = "8c6a9bb9"
FONTS = {
    "%%OR%%": (ORIG_COMMIT, "fonts/variable/Nunito[wght].ttf"),
    "%%OI%%": (ORIG_COMMIT, "fonts/variable/Nunito-Italic[wght].ttf"),
    "%%NR%%": (None, "fonts/variable/Nunuiko[wght].ttf"),
    "%%NI%%": (None, "fonts/variable/Nunuiko-Italic[wght].ttf"),
}


def font_b64(commit, path):
    with tempfile.NamedTemporaryFile(suffix=".ttf") as ttf, \
         tempfile.NamedTemporaryFile(suffix=".woff2") as woff:
        if commit:
            ttf.write(subprocess.run(
                ["git", "-C", ROOT, "show", f"{commit}:{path}"],
                capture_output=True, check=True).stdout)
            ttf.flush()
            src = ttf.name
        else:
            src = ROOT / path
        compress(str(src), woff.name)
        return base64.b64encode(pathlib.Path(woff.name).read_bytes()).decode()


def main():
    html = (HERE / "template.html").read_text()
    for token, (commit, path) in FONTS.items():
        html = html.replace(token, font_b64(commit, path))
    out = HERE / "nunuiko-proof.html"
    out.write_text(html)
    print(out, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
