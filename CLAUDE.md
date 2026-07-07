# Working ground rules

1. **Don't visual-test the fonts.** After a glyph change, build and output to the
   proof (`sources/proof/`) — the user does the visual testing. Do not render
   glyphs to images or judge their appearance yourself.

   **Always regenerate the proof whenever you generate a TTF.** Every time the
   variable font(s) are rebuilt, immediately run
   `.venv/bin/python sources/proof/make_proof.py` (from the repo root) so
   `sources/proof/nunuiko-proof.html` reflects the new build. A rebuilt TTF
   without a refreshed proof is an incomplete step.

2. **Weights over 700 are unlikely to ever be used.** The user works in the
   ExtraLight–Bold range (200–700). When judging trade-offs or where a fix has
   to hold up, prioritize ≤700; don't sink effort into making Heavy/900 (or
   interpolation toward them) perfect at the expense of the usable range.

## When we do address italics

Prefer **propagating upright fixes into the existing true-italic masters
algorithmically** over regenerating italics by slanting the upright. The italics
are separately designed masters, not obliques — auto-slanting the upright would
discard them.

To make a fix propagate, express it as a **geometric rule** (line intersections,
rotations, fractions, reversal/overlap tests) that loops over every master —
the way edits 01–06 already do — rather than as pasted literal coordinates.
Rule-based edits land on the italic masters unchanged because the geometry holds
in slanted space.

Watch out for edits written with **hand-picked coordinates copied from a
single-master SFD** (e.g. edit 07's crotch collapse used literal ExtraLight
points). Those don't transfer to the slant and must be reformulated as a
construction before they can auto-apply to italics.
