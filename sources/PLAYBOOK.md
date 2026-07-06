# Nunuïko build playbook

How this repo (a fork of `googlefonts/nunito`) was brought to a reproducible
build, and the remaining steps to turn it into the Nunuïko derivative. Written
to be repeated verbatim for **Nunito Sans** (`googlefonts/nunito-sans` → the
straight-terminal display cut). Everywhere it says `Nunito`, substitute
`NunitoSans` / `Nunito Sans` for the second run. Background and design
rationale live in `fonts.md`.

## Repo layout (what a Google Fonts upstream gives you)

- `sources/Nunito.glyphs` — the single Glyphs source. **6 masters**:
  3 weights (Light / Regular / Heavy stems ≈ 42 / 125 / 208 units) × upright + italic.
  Every glyph edit must be applied once per master.
- `sources/config.yaml` — gftools builder config (upstream renamed it from
  `builder.yaml`; some scripts may still reference the old name — see fixes).
- `sources/build.sh` — build script: gftools builder → slice combined
  `[ital,wght]` VF into separate roman/italic `[wght]` VFs → STAT/name fixes.
- `sources/fix.py` — post-build italic name/bit fixes (imports `fontbakery`).
- `fonts/variable/` — built variable TTFs (committed binaries).
- `OFL.txt` — license. **Nunito declares NO Reserved Font Name** (the copyright
  line has no "with Reserved Font Name" clause), so the rename is by choice,
  not legal necessity. **Check this again for Nunito Sans** — read the first
  line of its `OFL.txt`.

## Step 1 — reproduce the stock build (DONE for Nunito, 2026-07-05)

Golden rule: prove you can build the *unmodified* font before editing anything.

### 1a. Environment

```bash
cd <repo>
python3 -m venv .venv          # Python 3.14.5 at time of writing
.venv/bin/pip install -r requirements.txt
```

`requirements.txt` was updated to the known-good set (the upstream pin
`gftools==0.8.8` no longer installs cleanly — see fixes below):

```
gftools==0.9.996
fontbakery
setuptools<81
```

Resolved versions that worked: fontmake 3.12.1, fonttools 4.63.0,
glyphsLib 6.13.1, protobuf 3.20.3.

### 1b. Fixes that were needed (expect the same in nunito-sans)

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: pkg_resources` | Python 3.14 / setuptools ≥ 81 removed it | `pip install "setuptools<81"` |
| `TypeError: Descriptors cannot be created directly` (protobuf) | gftools 0.8.8's generated protos clash with modern deps | Upgrade to gftools 0.9.996 **in a fresh venv** (mixing old+new pins leaves an unresolvable protobuf soup — recreate the venv, don't upgrade in place) |
| `FileNotFoundError: builder.yaml` | Upstream renamed the config to `config.yaml` but `build.sh` wasn't updated | `build.sh`: `gftools builder config.yaml` |
| `gen-stat: unrecognized arguments: --axis-order` | CLI flag removed in newer gftools; axis order is now inferred | `build.sh`: drop `--axis-order 'wght' 'ital'`, keep `--inplace` |
| `ModuleNotFoundError: fontbakery` (in `fix.py`) | Never listed in requirements | `pip install fontbakery` (now in requirements.txt) |
| `varLib.instancer: No such file 'X[ital,wght].ttf'` | gftools 0.9.996 builder **splits Roman/Italic itself** and never writes the combined `[ital,wght]` file; it also sets STAT and the italic head/OS/2/post bits | Delete the instancer / `gen-stat` / `fix.py` steps from `build.sh` entirely — the builder output is already final. (Beware: with the *old* build.sh, the instancer silently read the **committed** combined binary, so the "build" wasn't fully from source.) |

### 1c. Build

```bash
source .venv/bin/activate
cd sources && ./build.sh
```

Outputs in `fonts/variable/`: `Nunito[ital,wght].ttf` (combined),
`Nunito[wght].ttf` (roman), `Nunito-Italic[wght].ttf`.
Rebuilt binaries differ byte-wise from the committed ones (newer toolchain) —
expected, not a problem.

### 1d. Sanity check the output

```bash
.venv/bin/python - <<'EOF'
from fontTools.ttLib import TTFont
f = TTFont('fonts/variable/Nunito[wght].ttf')
print('Family:', f['name'].getDebugName(1))
print('Axes:', [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in f['fvar'].axes])
print('Glyphs:', f['maxp'].numGlyphs)
EOF
```

Nunito result: family "Nunito", wght 200–1000, 1103 glyphs, version 3.602.

## Step 2 — tabular figures check (DONE for Nunito: solved for free)

Nunito ships no `tnum` feature because it doesn't need one: **all ten default
digits already share a fixed 600-unit advance width** — figures are tabular out
of the box. The fonts.md "figures" workstream is moot for Nunito.

**Repeat this check for Nunito Sans** (don't assume — it's a separate drawing):

```bash
.venv/bin/python - <<'EOF'
from fontTools.ttLib import TTFont
f = TTFont('fonts/variable/Nunito[wght].ttf')
hmtx, cmap = f['hmtx'], f.getBestCmap()
w = {c: hmtx[cmap[ord(c)]][0] for c in '0123456789'}
print(w, '— tabular:' , len(set(w.values())) == 1)
EOF
```

## Step 3 — rename (Nunito → Nunuiko) — DONE (2026-07-06)

Done as its own commit, **before** any glyph edits, so test installs
coexist with real Nunito for side-by-side comparison.

- The Glyphs source had only **four** name strings to touch (grep for the
  family name, excluding `glyphname`/`unicode` lines): `copyright`,
  `familyName`, and 2× a `"Nunito Heavy"` per-instance familyName override
  (the Heavy instance ships as its own family for legacy weight-class apps).
  `sed` on the .glyphs file is fine — but **keep the file pure ASCII**
  (it contains no non-ASCII bytes; don't introduce the diaeresis or plist
  `\U` escapes there).
- `git mv` the source to `Nunuiko.glyphs`; update `config.yaml` and
  `build.sh`; `git rm` the old committed binaries (recoverable from history).
- **Split naming:** internal/PostScript names (IDs 6, 25) and filenames stay
  ASCII `Nunuiko`; the **public** name records (IDs 1, 4, 16, 21) get the
  diaeresis `Nunuïko`, applied post-build by `sources/display_name.py`
  (last step in `build.sh`). Copy that script to the Nunito Sans fork —
  for the display cut set `ASCII_NAME`/`DISPLAY_NAME` to
  `Nunuiko Display` / `Nunuïko Display`.
- Verify with `fc-scan --format '%{family}\n' <ttf>` → must print `Nunuïko`,
  and name ID 6 must stay ASCII.
- Copyright string keeps the original Nunito Project notice appended after
  the new one (OFL requires retaining it).

## Step 4 — the six glyph edits — TODO

Applies identically to BOTH cuts (this repo and the nunito-sans fork).
Order (easiest first): **l → f → J → Q → G → K/k**. Full design specs in
`fonts.md` § "The actual changes are small".

**Every edit is logged in `GLYPHLOG.md`** — per master, with before/after
coordinates and (more importantly) the *rule* used, so the Nunito Sans run
replays the rule against its own outlines instead of re-deriving the design.
Fill it in as each glyph lands; copy it to the Nunito Sans fork alongside
this playbook.

> ⚠️ **glyphsLib is READ-ONLY for us.** `GSFont.save()` does not round-trip
> this file: it drops kerning groups, feature `code` lines, and even a glyph
> (verified by diffing a load+save against the original). Parse with
> glyphsLib to *compute* edits, then apply them as targeted text surgery on
> the raw .glyphs (see `sources/edits/01_l_tail.py` for the pattern — incl.
> positional node replacement, since content-matching can collide when a
> compressed coordinate equals a later node's line).

Linux workflow (Glyphs.app is Mac-only):

1. Convert source to per-master UFOs + designspace:
   `fontmake -g sources/Nunito.glyphs -o ufo`
   (or `glyphs2ufo` from glyphsLib).
2. Edit each master's glyph in **FontForge** (opens UFOs cleanly). Keep point
   structure identical across masters or interpolation breaks.
   6 masters if keeping italics; consider deferring italics to halve the work.
3. Rebuild: `fontmake -m <designspace> -o variable`; fix any interpolation
   errors fontmake reports.
4. After each glyph: install locally, render a size ramp, inspect at ~10px.
   For `l` specifically: test `Il1` adjacent at 10px before committing
   (the tail is the l/I/1 disambiguator).

## Step 5 — later / deferred

- **opsz variable-font merge** (rounded small ↔ straight large in one family):
  phase 2; requires redrawing one family to match the other's point structure.
  Ship the two renamed cuts first.
- **KDE rollout**: set all font roles (`kdeglobals`: `[General]` `font`,
  `menuFont`, `toolBarFont`, `smallestReadableFont`; `[WM]` `activeFont`) —
  see fonts.md § "Apply in KDE".

## Nunito Sans run — differences to expect

- Fork `googlefonts/nunito-sans`; its source/config layout may differ slightly
  (check for `.glyphs` vs UFO sources, and the builder config filename).
- Different axes: Nunito Sans upstream has **wght AND opsz/wdth variants** in
  some releases — check `fvar` after the first build and read its
  `config.yaml` before assuming the Nunito recipe applies 1:1.
- Re-check RFN in its OFL.txt (step 0) and tabular figures (step 2).
- Target name: **`Nunuiko Display`**.
