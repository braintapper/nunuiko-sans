This repo is a fork of googlefonts/nunito-sans. The goal is to produce Nunuïko Display — the Nunito Sans sibling of a cut I've already finished on Nunito proper (public "Nunuïko Display", internal ASCII "Nunuiko Display").

All the design work is already done and documented — your job is to replay it here, not re-derive it. Start by reading, in order: PLAYBOOK.md (process + a "Nunito Sans run — differences to expect" section), GLYPHLOG.md (the six glyph edits with per-master rules and numbers), and fonts.md (original design intent). Then read sources/edits/lib.py and sources/edits/01_l_tail.py to see the machinery.

The work is six glyph edits, replayed in order: 01 l tail · 02 f terminal · 03/03b G on O bowl · 04/04b/04c/04d Q slash · 05 J hook · 06 K/k notch. For each, apply the rule from GLYPHLOG to Nunito Sans's own outlines.

Hard constraints:
- glyphsLib is READ-ONLY — its save() drops kerning groups and feature code. Compute with glyphsLib, apply edits as text surgery on the raw source via lib.py (see how each 0N_*.py does it).
- Node structure must stay identical across all masters or interpolation breaks. The edit scripts carry hardcoded node indices and asserts from Nunito's topology — Nunito Sans's node counts/orders will differ, so re-derive the indices; the asserts are built to fail loudly and show you where.
- Nunito Sans may have different axes than Nunito (possibly opsz/wdth alongside wght) — check fvar after your first build before assuming the recipe maps 1:1.

Before editing anything: set up the venv, reproduce a clean baseline build with this repo's own builder config (don't copy Nunito's config.yaml), and confirm fvar/masters. Also check OFL.txt for the reserved font name and whether tabular figures need handling. Then append the display_name.py step (family → "Nunuïko Display") to the build.

For each glyph: edit script → per-master asserts pass → build → render a size ramp to inspect → fill in that glyph's "Nunito Sans replay notes" in GLYPHLOG → commit. Don't move to the next glyph until the current one verifies.

Give me your plan before you start editing — especially anything about this fork (source format, axes, config) that diverges from what the docs assume.
