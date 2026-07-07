"""Build the Nunuïko Display specimen/diff proof page (self-contained HTML).

Embeds two variable fonts as base64 woff2: the ORIGINAL upstream Nunito
Sans (pulled from git history so it never drifts) and the CURRENT Nunuïko
Display build. Roman only — the four edits are done for the 14 roman
masters; italics are a pending second pass. The result is published as a
Claude artifact (interactive proof + visual changelog).

Run from the repo root:  .venv/bin/python sources/proof/make_proof.py
Output: sources/proof/nunuiko-display-proof.html (gitignored).
"""
import base64
import pathlib
import subprocess
import tempfile

from fontTools.ttLib.woff2 import compress

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent

# last upstream commit before the rename/edits — pristine Nunito Sans
ORIG_COMMIT = "058bd7a"
VF = "[YTLC,opsz,wdth,wght].ttf"
FONTS = {
    "%%OR%%": (ORIG_COMMIT, "fonts/variable/NunitoSans" + VF),
    "%%NR%%": (None, "fonts/variable/NunuikoDisplay" + VF),
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
    out = HERE / "nunuiko-display-proof.html"
    out.write_text(html)
    print(out, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
