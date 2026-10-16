# Nunuïko glyph change log

Detailed record of every glyph modification, precise enough to **replay the
same edit on Nunito Sans** (→ Nunuïko Display) without re-deriving it.
Design rationale lives in `fonts.md`; this file is the engineering log.

## Conventions

- Coordinates are in font units (UPM 1000), `(x, y)` from the glyph origin.
- Every edit is recorded **per master**. Masters in `Nunuiko.glyphs`
  (3 weights × upright/italic; stems ≈ 42 / 125 / 208):

  | # | Master | Stem | Italic |
  |---|--------|------|--------|
  | 1 | Light | 42 | no |
  | 2 | Regular | 125 | no |
  | 3 | Heavy | 208 | no |
  | 4 | Light Italic | 42 | 9° |
  | 5 | Regular Italic | 125 | 9° |
  | 6 | Heavy Italic | 208 | 9° |

- For each glyph record: **before** (point structure + key coordinates),
  **operation** (what moved/was added/deleted, and the rule used to derive
  it — e.g. "tail shortened to 60% of original length"), **after**, and
  the **compatibility check** (same point count/order in all masters).
- Prefer *rules* over raw deltas ("terminal cut at y=520, angle follows
  stroke" transfers to Nunito Sans's different outlines; "move point 12 by
  (−18, 40)" does not). Record both when possible.
- Affected composites/related glyphs (accented forms, small caps if any)
  are listed per glyph — the same edit or component update must cover them.
- Status flags: ☐ not started · ◐ in progress · ✅ done (all masters) ·
  🔁 replayed on Nunito Sans.

## Edit order (easiest first)

l → f → J → Q → G → K/k → fl width (metrics fix)

**G, K, k reverted to stock (2026-07-07, user decision).** Edits 03/03b
(G) and 06 (K/k) were backed out — the glyph blocks for G, K, k,
kgreenlandic were restored from the pre-edit baseline (commit `638e704`,
unmodified Nunito Sans geometry). The scripts and their log entries below
are kept for reference in case the work is revisited. Composites (Gbreve…,
Kcommaaccent…) reverted automatically via their components. Active edits:
**01 l · 02 f · 04 Q · 05 J · 07 fl width.**

---

## 1. l (lowercase L) — shorter tail ✅ (2026-07-06; since edit 14 this is the ss02 alternate)

**Intent:** reduce the foot/tail. ⚠️ The tail is Nunito's main
`l` / `I` / `1` disambiguator — shorten, don't remove; test `Il1` adjacent
at ~10px before committing.

**Composites using `l` (all verified OK, they reference the component so
they picked the edit up automatically):** fl, lacute, lcaron,
lcommaaccent, ldot, ldotbelow, lj, llinebelow, lslash.

**Script:** `sources/edits/01_l_tail.py` (run once; asserts structure).

### Structure (identical in all 6 masters)

One closed path, 26 nodes. Node 14 = stem bottom-right junction
(x = stem right edge at tail height) — the **pivot**. Tail region =
nodes 0–13 (terminal cap + inner sweep) + 23–25 (outer bottom curve).
Nodes 15–22 = stem sides + rounded top cap.

### Operation / rule

**Compress the tail region horizontally toward the pivot by FACTOR = 0.6**
(`x' = pivot + 0.6·(x − pivot)`, applied only to tail nodes with
x > pivot; y untouched). Shrink advance width by the tail tip's retreat
(`width' = width − (tip − tip')`). Move anchors `bottom` and `dot` by the
same rule (they sit in the tail zone / right sidebearing); leave `top`,
`topright`, `center`.

Why this works: the map is affine in x, so collinearity — and therefore
every SMOOTH joint — is preserved exactly. The terminal cap gets ~40%
narrower horizontally but keeps its full stroke height, which reads as
"same terminal, shorter tail".

**Refinement 1b (user feedback):** the compression squashed the tip's
top-right corner arc (nodes 5→6,7→8) to 0.6 of its x-extent — visibly
sharp. After compressing, restore that arc's x-extent to
**min(original, 0.65 × the new cap-top span 5→11)** — the cap keeps the
top edge from degenerating in the heavy masters, whose corner is too big
to fit whole (Heavy 40→29, Heavy It 33→23; EL/EL It get their full
original 17/11 back). Control 7 keeps its original x-offset from node 8
scaled by the same ratio, control 6 stays on node 5's vertical, and
top-edge controls 9,10 sit at their original fractions of the 8→11 span.
y never changes; the 4-5-6 vertical and 7-8-9 / 10-11-12 horizontal
collinearities survive exactly. Folded into the main script — a single
run of 01 produces the final tail.

### Per-master numbers (pivot / tip old→new / width old→new)

| Master | pivot | tip | width |
|---|---|---|---|
| ExtraLight | 127 | 269→212 | 275→218 |
| Bold | 190 | 318→267 | 319→268 |
| Heavy | 252 | 363→319 | 364→320 |
| ExtraLight Italic | 111 | 233→184 | 275→226 |
| Bold Italic | 179 | 287→244 | 319→276 |
| Heavy Italic | 247 | 340→303 | 364→327 |

Tail extent beyond stem: EL 142→85 · Bold 128→77 · Heavy 111→67 units.

### Compatibility & size-ramp check
- [x] Same point count/order in all masters — only coordinates changed;
      fontmake build clean
- [x] `Il1` distinct at 10px (proof sheets: Regular + Bold ramp 10–28px,
      Heavy @72, Italic @84 + 12px)
- [x] lcaron: caron offset is baked (x=177 EL), NOT anchor-driven — checked
      visually, still sits correctly; no edit needed
- 🔁 **Nunito Sans replay — DONE (2026-07-06).** FACTOR 0.6 and the
      width/anchor rules carried over unchanged; only indices re-derived.
      - **Fork-wide finding (affects ALL edits):** the Nunito Sans source is
        **Glyphs 3** (`.formatVersion = 3`). Nodes serialize as `(x,y,code)`
        (code ∈ o/c/cs/l/ls), anchors as `pos = (x,y)`, and some masters
        carry **fractional widths** — all different from Nunito's Glyphs 2.
        `lib.py` was adapted once (NODE_RE, `fmt_node`, anchor regex, float
        widths) and now drives every edit.
      - **Topology differs from Nunito:** Nunito Sans's `l` is a **16-node**
        single path (Nunito: 26), with a **straight-cut** terminal, not a
        round bulb. Landmarks: node 10 = stem top-right (**pivot = its x**),
        node 11 = stem top-left, tip = **max x** (node 3, except the 6pt
        masters bulge at node 2). Tail = every node with x > pivot.
      - **Nunito's 1b round-corner restore is NOT needed here** — the cut
        terminal's top-right is already a hard corner, so plain compression
        keeps it clean (verified on the big-`l` ramp, EL/Bold/ExtraBlack).
      - 14 roman masters, structure preserved, fontmake interpolation clean;
        `Il1` distinct at 10px; foot clearly shortened, terminal cut intact.
      - Composites (fl, lacute, lslash, …) reference the `l` component and
        inherit automatically (build clean). **Italics deferred.**

      Per-master (pivot / tip old→new / width old→new / tail-ext old→new):

      | Master | pivot | tip | width | ext |
      |---|---|---|---|---|
      | 12pt ExtraLight | 127 | 268→212 | 275→219 | 141→85 |
      | 12pt Bold | 190 | 309→261 | 319→271 | 119→71 |
      | 12pt ExtraBlack | 252 | 349→310 | 364→325 | 97→58 |
      | 12pt Cond ExtraLight | 112 | 225→180 | 237→192 | 113→68 |
      | 12pt Cond ExtraBlack | 224 | 297→268 | 314→285 | 73→44 |
      | 12pt Exp ExtraLight | 150 | 328→257 | 332→261 | 178→107 |
      | 12pt Exp ExtraBlack | 291 | 421→369 | 437→385 | 130→78 |
      | 6pt ExtraLight | 158 | 301→244 | 314→257 | 143→86 |
      | 6pt Bold | 223 | 355→302 | 362.78→310 | 132→79 |
      | 6pt ExtraBlack | 287 | 411→361 | 411→361 | 124→74 |
      | 12pt XL/XBlk YTLC Min/Max | = 12pt base | | | |

---

## 2. f — downturned top terminal ✅ (2026-07-06)

**Intent:** top curves back **down**, but slightly.

**Related glyphs — IMPORTANT finding:** `fl` and `fl.ss02` are components
of `f` (inherit automatically), but **`fi` is drawn separately** and
carries its own copy of the hook — it must be edited too. `florin` (ƒ)
has a *different* terminal construction (flat ball cap) and was left
stock. No `longs`/`ffi`/`ffl` in the font.

**Script:** `sources/edits/02_f_terminal.py` (+ shared
`sources/edits/lib.py`). Run once; locates the terminal by pattern.

### Structure / locator (works in both f and fi)

The terminal is a 7-node motif; find every match, keep the one whose cap
control sits highest (abs. y-max is unreliable — fi's i-dot can be the
tallest point in heavy masters):

| offset | type | role |
|---|---|---|
| p | curve smooth | **pivot** — hook-underside neck |
| p+1 | line smooth | underside end of terminal |
| p+2, p+3 | offcurve | cap controls (p+3 ≈ tip) |
| p+4 | curve smooth | topside end of cap |
| p+5 | line smooth | topside neck |
| p+6 | offcurve | first handle of the long top curve |

In `f`: p = node 16 (all 6 masters). In `fi`: p = node 21.

### Operation / rule

**Rotate nodes p+1 … p+6 clockwise by 12° about node p.** Rotation is an
isometry with the pivot on the incoming smooth chain, so every SMOOTH
joint survives exactly; the long top curve reshapes smoothly via the
rotated p+6 handle. No width or anchor changes (the f terminal already
overhangs the advance; the overhang grows a little — checked in
fluff/offer/fjord strings, no collisions).

Pivots / tip-x drift (f): EL (269,670) 324→331 · Bold (332,615) 402→421 ·
Heavy (381,564) 478→509 · same pattern italics. fi within 1–2 units of f.

### Compatibility & size-ramp check
- [x] Same point count/order in all masters — rotation only
- [x] fi edited to match; fl/fl.ss02 inherit via components; florin
      deliberately stock
- [x] No collision in fluff / offer / fjord at Regular, Heavy, Italic
- 🔁 **Nunito Sans replay — DONE (2026-07-06).** Same operation
      (rotate the terminal + both approach handles clockwise about the
      underside neck), **angle re-judged to 10°**.
      - **Topology:** f = 22-node single path; the terminal is a STRAIGHT
        CUT (4-node run: curve-smooth neck / two line corners / line-smooth
        neck), not Nunito's round bulb — Nunito's 7-node round-cap pattern
        does not exist here. New locator matches this cut-cap signature
        inside path 0 and takes the highest cap. Pivot: **f n9**, **fi n11**.
      - **fi IS drawn separately** (28 nodes, 2 paths — confirms Nunito's
        finding) and was edited too; its i-dot (path 1, four plain lines)
        is skipped by the path-0-only locator. fl/fl.ss02 inherit via
        components; florin (32 nodes, different terminal) left stock.
      - **Angle: 10°, not 12°.** A straight cut reads an angle ~1.3× more
        strongly than a round bulb, so 10° matches the sibling's
        perceived-subtle 12°. Verified by eye at 8/10/12: 12 over-hooked at
        Bold/ExtraBlack, 8 barely read at UI sizes; 10 is a clean, subtle
        downturn that survives the fjord/fluff ramp with no collisions.
      - Rotating the cap plus BOTH approach handles (n_p-1 outer, n_p+4
        inner) about the neck keeps every SMOOTH joint exact; only the
        outer arch and inner return reshape slightly. 14 roman masters,
        structure preserved, fontmake interpolation clean. **Italics
        deferred.**

---

## 3. J (capital) — upturned hooked foot ✅ (2026-07-07, done 5th)

**Intent:** U-hook foot per **Google Sans Flex** reference — stem down,
around the bowl, back **up** the left side, ending in a rounded cap.
**Lowercase `j` is CANCELLED** (user decision: stock j is fine — do not
touch it, here or in the Nunito Sans replay).

**Composites (inherit automatically):** IJ, I_J.loclNLD,
Iacute_J.loclNLD, Jcircumflex, Je-cy, LJ, NJ.

**Script:** `sources/edits/05_J_hook.py` (22 → 26 nodes).

### Operation / rule

Full reconstruction of the foot; stem + top cap (old nodes 3–11) kept
verbatim but **shifted right by δ** — because the J is also **widened**:

- **Advance width = 0.66 × U's width** (user spec — the original bowl
  was far too narrow for the font's proportions): 297→475 (δ=178) /
  354→487 (δ=133) / 411→498 (δ=87); italics identical. All growth is
  bowl-side: hook outer-left keeps the old leftmost extent
  (−11/−14/−16; italics ≈−51 deslanted) → LSB and RSB both preserved.
- Inner bottom y = old inner-bottom y (36/100/164) → keeps Nunito's
  existing bottom taper. Outer bottom = old overshoot (−2/−5/−7).
- **Hook weight = min(stem weight, 0.55 × left span)** — with the wider
  bowl, EL and Bold now fit the full stem weight (42/128); Heavy is
  capped 215→133.
- **Terminal height H = 0.9 × stem curve-start y** (EL 159 / Bold 179 /
  Heavy 199); rounded terminal cap = same construction as the stem's own
  top cap (rise = hook weight / 2, kappa 0.5523 quarter arcs) — corners
  stay in Nunito's rounded vocabulary (user requirement).
- Italics: landmarks deslanted by tan 9°, built upright, reslanted.
- Anchors: top follows the stem (+δ); bottom recentered on the bowl.

### Composites (widening propagation — replay this too!)

IJ, I_J.loclNLD, Iacute_J.loclNLD, Je-cy, LJ, NJ: **width += δ** (their
J component offsets stay — growth is inside J's box, left of the stem).
Jcircumflex: width += δ **and** its circumflexcomb.case transform
tx += δ (the accent must track the shifted stem; some layers carry the
transform once, some twice incl. background).

### Compatibility & size-ramp check
- [x] 26 nodes, same order/types, all 6 masters; fontmake clean
- [x] JU proportion pairs at 200/400/1000; Ĵ accent centered; context
      Jump/Justice/IJssel/JOJO/NJ verified upright + italic
- 🔁 **Nunito Sans replay — DONE (2026-07-06).** Same landmark-based
      construction; parameters (WIDTH_FRAC_OF_U 0.66, H_FRAC 0.9,
      HOOK_MAX_FRAC 0.55) all kept — verified by eye.
      - **Topology:** J is a 12-node single path (Nunito: 22). Landmarks
        re-derived: node 3 = stem-right/curve-start, 4/5 = stem top,
        6 = stem-left/curve-start, 9 = inner bottom, 10 = hook outer-left
        (LSB), 11 = outer bottom. Output 16 nodes (Nunito: 26).
      - **Terminal is a FLAT CUT, not Nunito's rounded cap.** Nunito's cap
        copied its rounded stem-top; Nunito Sans's stem top is a flat cut,
        so the hook ends in a flat horizontal cut (node 9 curve = end of
        inner rise, node 10 line, segment 9→10 = the cut). Bottom of the U
        stays round (kappa arcs). Gotcha: node 9 must be `curve` (it ends
        an offcurve pair) — a `line` there triggers fontmake "Illegal line
        segment point count: 3".
      - Widen bowl-side (delta 87–229 across masters): stem shifts right,
        hook outer-left (LSB) and RSB preserved. Composites IJ/I_J.loclNLD/
        Iacute_J.loclNLD/Je-cy/LJ/NJ get width += delta; Jcircumflex also
        gets accent `pos` tx += delta (Glyphs 3 stores the accent offset as
        `pos = (x,y)`, not Nunito's `transform` string). j CANCELLED.
      - 14 roman masters, fontmake clean; JU pairs + Jump/IJ/NJ + Ĵ centered
        verified. **Italics deferred.**

---

## 4. Q — Jost-style slash ✅ (2026-07-06, done 4th)

**Intent (refined by user):** straight slash crossing the bowl at the
bottom right, reference **Jost**. Originally baseline-aligned (slash
bottom at y = 0, no descender); **refinement 4d lengthened it so it now
dips slightly below the baseline** — see 4d. Still far short of the old
swash's −276 (Heavy Italic), so line fitting stays tight.

**Structure discovery:** Q = `O` component + `_part.Qtail` component
(used only by Q) — the entire edit lives in `_part.Qtail`
(12 curved nodes → capsule, 14 nodes).

**Refinement 4b (user feedback):** flat Jost corners looked out of place —
corners filleted with r = 0.18 × slash weight. **Superseded by 4c.**

**Refinement 4c (user feedback):** slash ends made **fully round** —
semicircular caps like the font's other terminals, so the slash is a
capsule/stadium (two quarter-arc cubics per cap, tension 0.5523; 14
nodes). Ink extents preserved from 4a/4b: the outer cap's *center* is
solved so the circle is tangent to y = 0 exactly (no post-shift needed),
and the inner cap center is pulled back by w/2 so the round tip's ink
ends where the flat end used to. Folded into the main script — a single
run of 04 produces the round-cap slash.

**Refinement 4d (user feedback):** slash lengthened **10% at each end** —
after the 4c caps are placed, both cap centers are pushed outward along
±d by `EXTEND_FRAC (0.10) × tip-to-tip length`. The outer tip now dips
below the baseline (EL ~13 units, more at heavier weights) and the inner
tip reaches deeper into the counter. Guard asserts the inner tip stays on
the ring side of the counter center so the counter never closes. Folded
into the script (single run of 04 produces the final slash).

**Script:** `sources/edits/04_Q_slash.py`. All geometry derived from O's
outlines per master:

- **M** = midpoint of the outer & inner bottom-right arc midpoints
  (ring midline at ~4:30); **w_ring** = distance between them.
- **Direction** 45° down-right; sheared by tan 9° for italic masters.
- **Slash weight** = min(w_ring, 0.6 × counter radius) — the cap is the
  key Heavy fix: at full ring weight the slash swallowed the counter and
  barely poked out. EL/Bold use ring weight (42/123); Heavy capped
  204→104, Heavy Italic 204→96. NB slash weight is non-monotonic
  Bold→Heavy — visually fine, interpolation clean.
- **Outer cap** center starts on the slash midline at y = w/2 (tangent
  to the baseline), then pushed out by 4d.
- **Inner ink tip** = inner-arc midpoint + 0.35 × counter radius along
  −d (cap center w/2 short of that), then pushed in by 4d.
- **4d extension** = 0.10 × tip-to-tip length added at each end.
- Winding matched to O's outer ring (else nonzero fill cancels the
  overlap); rect corners converted to part-local space via Q's
  per-master component offset. Same node order in all masters
  (interpolation-safe — verify the orientation flip decides identically
  everywhere when replaying).

### Compatibility & size-ramp check
- [x] Same 14-node capsule structure, same order, all masters
- [x] Counter stays open at all weights incl. Heavy/Heavy Italic (incl.
      the deeper 4d inner tip; guard assert in the script)
- [x] 4d slash length/dip verified against baseline guide at 200/700/1000
      upright + italic (outer tip dips below, inner reaches deeper)
- 🔁 **Nunito Sans replay — DONE (2026-07-06); caps revised to HARD
        corners (user feedback).**
      - **Q IS `O` + `_part.Qtail`** (both at offset 0,0; tail used only by
        Q), and O is structurally identical to Nunito's, so ALL the
        O-derived geometry (M, w_ring, counter_r, direction, 4d extension)
        ported UNCHANGED. `_part.Qtail` is fully replaced.
      - **Caps are FLAT butt caps (hard corners), NOT Nunito's round caps.**
        Nunito's 4c round semicircular caps are its rounded vocabulary;
        Nunito Sans is straight-cut, so the slash ends flat (perpendicular
        to the slash), four line corners — a true Jost slash. The flat end
        sits at the tip (C + d·R) so ink extent matches the round version;
        winding matched to O's outer ring. `_part.Qtail` is now 4 nodes.
      - **MAX_COUNTER_FRAC 0.6 kept** — counter stays open at every weight
        incl. ExtraBlack (weight capped 104 vs ring 204); outer tip dips
        just below baseline (4d). 14 roman masters, fontmake clean.
        **Italics deferred.**

---

## 5. G — rebuilt on O's bowl ✅ (2026-07-06, done 3rd)

**Intent (refined by user):** G is based on **O** — full round bowl — with
the horizontal bar at the same height as the original G and the upper-arm
terminal (top overhang) ending in the same place as the original G.

**Composites (inherit automatically):** Gbreve, Gcaron, Gcircumflex,
Gcommaaccent, Gdotaccent, Gmacron.

**Script:** `sources/edits/03_G_bowl.py`.

### Key insight enabling the graft

Nunito's G and O **share a skeleton**: G's outer top/left is O's outer
top/left within ≤9 units (exact in ExtraLight). So the new G can be
assembled from verbatim pieces with only two computed joins.

### Assembly (44 → 35 nodes, single path, original traversal order)

1. **G bar left-end U** (G nodes 10–16) — verbatim; bar height and left
   end unchanged by construction.
2. Bar underside LINE right to **corner B** = O's *inner* right arc split
   (de Casteljau) at the bar's underside y.
3. Down O's inner right (split remainder) → O inner bottom/left/top
   nodes verbatim.
4. **G arm inner + terminal cap + outer top** (G nodes 29–37) — verbatim;
   terminal ends where it always did. Junction at inner top works because
   both curves are horizontal (y=672) there.
5. Outer left grafted **at O's node** (G's ≤9 units away, tangent shared)
   → O outer bottom verbatim → rising right arc to **corner A** at the
   bar's *top* edge y. Upright quirk: O's right extremum sits ~1 unit
   below the bar top → A is the extremum nudged up, no split. Italics:
   real split (their extremum is higher, y≈416).
6. LINE left along the bar top back to start. A and B are true corners
   (non-smooth); every other joint keeps SMOOTH exactly.

**Refinement 3b (user feedback: corner A too sharp):**
`sources/edits/03b_G_corner.py` replaces corner A with a fillet whose
radius = the bar left-end's own corner rounding (r = barTopY − leftU
cornerY, read per master: EL 19 · Bold 47 · Heavy 74 · italics 22/54/86),
so it matches the font's corner vocabulary and scales with weight
automatically. Fillet controls at 55% tension toward the old corner.
35 → 38 nodes. Corner B (inside the counter, underside) left sharp —
it reads as the bar tucking into the bowl. **Replay order: 03 then 03b.**

### Metrics & classes

- Width := O's width per master (718→751 / 736→785 / 754→820; italics
  same). LSB unchanged; RSB now O's.
- Anchors top/bottom := O's (bowl recentered) — composites follow.
- **rightKerningGroup G → O** (right side is now O's round bowl; left was
  already O).

### Compatibility & size-ramp check
- [x] Same 35-node structure in all masters; fontmake clean
- [x] Overlay + EL/Regular/Heavy @200px + Google/GIGA/OGRE context +
      italics all verified visually
- 🔁 **Nunito Sans replay — DONE (2026-07-06). 03b SKIPPED by design.**
      - **O is structurally identical to Nunito's** (2 paths × 12 nodes,
        same extrema semantics), so the entire O-side split/graft logic
        ported UNCHANGED. G/O DO share the skeleton: G's outer left/bottom
        and inner left are O's verbatim (only outer-right + inner-right
        were pulled in) — so the graft is even cleaner than Nunito's.
      - **G is 31 nodes here (Nunito: 44); assembly is 28 (Nunito: 35).**
        Bar left-end is a **straight cut** (two line corners, nodes 4/5),
        not Nunito's rounded U. Arm/terminal/outer-top = G nodes 18–24
        verbatim (terminal is a straight cut, ends where it always did).
        Corner A nudge branch fires (O right extremum y≈354 ≈ bar top 355).
      - **03b (fillet corner A) is NOT applied.** Nunito rounded corner A
        because a sharp corner clashed with its *round* terminals. Nunito
        Sans's vocabulary is the opposite — straight cuts, sharp corners
        (its bar left-end and arm terminal are sharp; the *original* G's
        aperture corner was sharp too). A crisp corner A is correct here;
        rounding it would break consistency. Verified by eye at
        EL/Bold/ExtraBlack (big G): clean aperture, no spike.
      - **rightKerningGroup G→O is N/A:** O, C and G all have no source
        kerning groups in Nunito Sans (kerning is via generated GPOS
        classes), so there is nothing to assign.
      - Width := O's (per-master 718→751 / 736→785 / 754→820 / …); anchors
        top/bottom := O's (bowl recentered); composites (Gbreve, Gcaron,
        …) inherit via components. 14 roman masters, fontmake clean.
        **Italics deferred.**

---

## 6. K / k — notched joint, not a chevron ❌ REVERTED to stock (2026-07-07, in `613e862`; superseded by edit 9)

**Intent:** Nunito's K is single-junction (arm and leg meet the stem at one
point — a chevron). Change to a **notched joint**: arm meets the stem, leg
branches off the **arm** a short distance out from the stem, opening the
crotch. Apply identically to `k`.

**Related glyphs:** Kcommaaccent/kcommaaccent are composites of K/k —
inherit automatically. **kgreenlandic** shares k's exact 34-node topology —
edited by the same script (added to its glyph loop). **Ka-cy/ka-cy have a
different construction** (35/34 nodes, different type sequence — curled
leg) — left stock; would need their own rule if desired.

**Script:** `sources/edits/06_K_notch.py` (K, k, kgreenlandic in one run).

### Operation / rule

Key discovery: the **heavy masters are already notched** (fat strokes can't
converge at one point) — Bold sits at frac 0.25–0.39, Heavy at 0.45–0.67.
So the rule is a *floor*, not an offset: move the crotch vertex out along
the arm-bottom line to **max(current, 0.25) of the arm's horizontal run**
(measured from the stem-right ∩ arm-bottom intersection S to the arm tip).
Masters already at/past the floor are untouched — the light masters simply
catch up to the design logic the heavy ones already had.

Per glyph, per master (34-node topology, K and k and kgreenlandic
identical): crotch vertex = node 13; leg foot cap = nodes 5–11; notch face
= edge 12→13 (Nunito's little perpendicular cut, preserved verbatim but
rotated with the leg).
1. node 13 → floor position on the arm-bottom line.
2. Leg pivots **rigidly about its foot-cap center**; rotation angle solved
   by fixed-point iteration so the leg's top edge passes through the new
   node 12 — stroke width and cap shape preserved exactly.
3. node 12 = new 13 + rotated original face vector.
4. node 4 = rotated leg bottom edge ∩ arm-bottom line.
5. node 3 = stem right edge ∩ arm-bottom line (S).
Pure line/intersection/rotation geometry — works unchanged in slanted
(italic) space.

### Changed masters (others already ≥ 0.25)

| Glyph | Master | frac | crotch (13) | leg rotation |
|---|---|---|---|---|
| K | ExtraLight | 0.05→0.25 | (158,342)→(239,414) | −12.5° |
| K | ExtraLight Italic | 0.06→0.25 | (178,339)→(266,408) | −13.9° |
| k | ExtraLight | 0.10→0.25 | (154,231)→(198,270) | −10.1° |
| k | ExtraLight Italic | 0.09→0.25 | (149,225)→(200,266) | −12.2° |
| ĸ | ExtraLight | 0.10→0.25 | (154,231)→(198,270) | −10.1° |
| ĸ | ExtraLight Italic | 0.09→0.25 | (149,225)→(200,266) | −12.2° |

Unchanged fracs — K: Bold 0.25, Heavy 0.45, Bold It 0.27, Heavy It 0.48;
k/ĸ: Bold 0.37, Heavy 0.63, Bold It 0.39, Heavy It 0.67.

### Compatibility & size-ramp check
- [x] Same 34-node count/order in all masters; fontmake clean
- [x] K, k, ĸ joints visually matched at 200/1000, upright + italic
- [x] 10px legibility strip (Kick KLERK kayak) at 200/400/1000
- 🔁 **Nunito Sans replay — DONE (2026-07-06); construction REDONE after
        user feedback** (arm must reach the stem; leg must branch off the
        arm with a consistent stroke width).
      - **Topology:** K/k/kgreenlandic are 14-node all-straight paths
        (Nunito: 34, rounded foot cap). Landmarks: node 1 = stem right,
        2 = leg-lower inner (on stem), 3/4 = leg foot (flat on baseline),
        5 = leg-upper inner, 6 = arm-bottom inner (crotch), 7 = arm tip,
        9 = arm-top inner (on stem).
      - **Three dead ends:** (a) sliding the notch face out with node2
        fixed bulged the leg at frac 0.25; (b) a strictly consistent-width
        leg steepened about the foot is clean but INVISIBLE on the light
        masters (the notch face scales with the thin stroke — Nunito Sans
        draws its own light K as a chevron for this reason); (c) opening the
        notch deep AND raising node2 high to kill the bulge merged the arm
        and leg into a lopsided **"<"** — user rejected all three.
      - **Shipped construction (two clean strokes + visible notch):** move
        the branch (nodes 5,6) out to a **MODERATE BRANCH_FRAC 0.18** so the
        leg clearly branches off the arm, but keep node2 (leg-lower on the
        stem) **LOW** — only a light **RAISE 0.25** toward 0.85·(node9−S) to
        tidy the near-stem width. Keeping node2 low is what makes the arm
        and leg read as two balanced strokes (raising it high was dead end
        c). Cost: a small width variation, well under (a)'s bulge. Applied
        as a floor; heavy masters (Bold 0.21, ExtraBlack 0.34) unchanged.
        Only nodes 2,5,6 move.
      - kgreenlandic shares k's topology; Cyrillic Ka-cy/ka-cy left stock.
        Verified by eye + ramp 200–1000 (two strokes, notch visible and
        balanced at every weight). 14 roman masters, fontmake clean.
        Italics deferred. BRANCH_FRAC / RAISE are the taste knobs.

---

## 7. fl — trailing advance fix after the l tail edit ✅ (2026-07-07)

**Intent:** remove extra space *before the next character* on `fl` / `ffl`
(user-reported). `fl` is a composite (`f` + `l` components) whose advance
was authored as `l_offset + l's ORIGINAL advance`. Edit 01 shortened `l`
and shrank its advance, but the ligature width was never updated — so
every `fl` carried the l-tail retreat (29–71 units) as trailing space.

**Related glyphs:** `ffl` has **no glyph of its own** — it shapes to
`f` + `fl` (no `ff`/`ffl`/`ffi` in the font), so fixing `fl` fixes it too.
`fl.ss02` (= `f` + `l.ss02`) is **already correct**: `l.ss02` is a separate
stylistic alternate that was NOT tail-edited, so its width still matches —
left alone. `fi` is drawn separately (not an `l` composite) — unaffected.

**Script:** `sources/edits/07_fl_width.py`.

### Operation / rule

Per master, set `fl.width = l_offset + l's CURRENT advance` (round to int).
This subtracts exactly the l-tail retreat, so `l`'s right sidebearing
*inside* the ligature is unchanged — only the surplus trailing advance is
removed. Metrics only; no outline/component change. Applied to all 14 roman
masters (unchanged masters would be skipped, but all 14 needed it).

### Per-master (width old → new / removed)

| Master | fl width | removed |
|---|---|---|
| 12pt ExtraLight | 581→525 | 56 |
| 12pt Bold | 683→635 | 48 |
| 12pt ExtraBlack | 787→748 | 39 |
| 12pt Cond ExtraLight | 500→455 | 45 |
| 12pt Cond ExtraBlack | 680→651 | 29 |
| 12pt Exp ExtraLight | 702→631 | 71 |
| 12pt Exp ExtraBlack | 943→891 | 52 |
| 6pt ExtraLight | 712→655 | 57 |
| 6pt Bold | 803→750 | 53 |
| 6pt ExtraBlack | 892→842 | 50 |
| 12pt XL/XBlk YTLC Min/Max | = 12pt base | |

### Compatibility check
- [x] All 14 masters consistent (`fl.width == l_offset + l.width`); fontmake
      interpolation clean; VF default-instance `fl` advance 581→525.
- [x] `fl.ss02` left stock (already consistent); `fi` unaffected.
- ☐ **Italics deferred** (same as the outline edits).

---

## 8. ff / ffi / ffl — ligatures with a joined crossbar ✅ (2026-10-16)

**Intent (user-reported):** a "teeny tiny gap" between the f's in "ff".
Nunito Sans has no ff ligature. "ff" is two f's pulled together by the f–f
kern, and their square-ended crossbars don't meet at the light end. Bar gap
per master (negative = overlap):

| Master | gap |
|---|---|
| 12pt ExtraLight (and YTLC Min/Max) | 11 |
| 12pt Bold | −11 |
| 12pt ExtraBlack | −30 |
| 12pt Condensed ExtraLight / ExtraBlack | 21 / −22 |
| 12pt Expanded ExtraLight / ExtraBlack | 7 / −32 |
| 6pt ExtraLight / Bold / ExtraBlack | 55 / 24.7 / −5 |

The italic masters show the same gaps, except Bold It −8 and ExtraBlack It
−26. At Regular the gap comes to about 2 units: the tiny gap.

**Script:** `sources/edits/08_ff_ligatures.py`, run once per source (roman,
then `NunuikoDisplay-Italic.glyphs`). It refuses to run if the glyphs exist.
Sister edit: Nunuïko's edit 8 (round bar ends there, so its bridge runs cap
to cap).

### Rule (per master)

- `offset = width(f) + kern(@MMK_L_f, @MMK_R_f)` (where the kerned second f
  sits).
- Each glyph is a **bridge** path, plus a component `f` at 0, plus the
  second glyph as a component at `offset`.
- **Bridge:** a quad over the bar band, from the first f's stem right edge
  (f nodes 1 bottom, 4 top) to the second f's stem left edge (f nodes 20
  bottom, 17 top, + offset). Going stem to stem keeps it the right way
  round whether the bars gap or overlap in that master, so the union is one
  flat bar everywhere.
- `width = offset + width(second)`. Carets go at `offset` and at
  `offset + the second glyph's caret_1`. kernLeft is `f`; kernRight comes
  from the second glyph.

| Glyph | Second | Unicode | kernRight |
|---|---|---|---|
| f_f | f | FB00 | f |
| f_f_i | fi | FB03 | i |
| f_f_l | fl | FB04 | ltail |
| f_f_l.ss02 | fl.ss02 | — | l |

**`fi` is drawn, not built from `f`.** Its f part has two extra nodes, so
f's nodes 17–20 are fi's 19–22, and for `f_f_i` the bridge ends on fi's own
points. That matters in **ExtraBlack YTLC Max** (roman and italic), where
stock fi's bar sits 5 units higher than f's (397–549 against 392–544). The
bridge ramps across the gap there instead of stepping. Plain f + fi already
had that 5-unit step before this edit.

**Features:** liga gains `sub f f i by f_f_i; sub f f l by f_f_l; sub f f
by f_f;` (ahead of fi/fl), and ss02 gains `sub f_f_l by f_f_l.ss02;`, in
both sources. Both features are `automatic`, so Glyphs.app would generate
the same lines.

Only master layers are written. The unnamed backup layer every glyph
carries on 6pt ExtraLight doesn't export, so it's skipped.

### Checks
- [x] Roman VF, italic VF and static Regular: offer→f_f, office→f_f_i,
      waffle→f_f_l, waffle+ss02→f_f_l.ss02, U+FB00→f_f; liga off → f f
- [x] Build clean (all statics + both VFs); proof f row shows `ff ffi ffl`
- [ ] Visual check of the joined bar (user)

Edit 7's note that "`ffl` has no glyph of its own" no longer holds: ffl
now shapes to `f_f_l`, whose second component is the width-fixed `fl`.

---

## 9. K / k — the leg grows out of the arm (Proxima Nova style) ◐ (2026-10-16)

**Intent (user):** make K's diagonals work like Proxima Nova's, with the
bottom stroke coming out of the top stroke. The starting point is stock
Nunito Sans (edit 6 was reverted). Unlike edit 6, the leg is detached from
the stem completely: both of its edges end on the underside of the arm, so
the open space below the arm reaches up to the arm's underside.

**Script:** `sources/edits/09_K_leg_from_arm.py` (K, k, kgreenlandic), run
once per source; `--dry-run` prints the numbers and `--gap=` tries another
value. Kcommaaccent / kcommaaccent are composites and follow automatically.
Cyrillic Ka-cy / ka-cy are left stock.

### Rule (per master; line geometry, so it holds on the italic masters)

14-node all-straight path. Landmarks: 0→1 stem right edge, 2→3 leg lower
edge, 3→4 foot on the baseline, 4→5 leg upper edge, 6→7 arm bottom
(7 = tip). Nodes 0 and 7–13 don't move.

- **S** = the stem's right edge (0–1) ∩ the arm's bottom line (6–7).
- The leg keeps its original perpendicular width `w` and the midpoint of
  its foot.
- Its centreline runs from the foot midpoint to a point on the arm, solved
  by bisection so that the leg's **lower edge meets the arm at GAP_FRAC =
  0.15** of the way from S to the arm tip. A fixed fraction keeps the
  stem-to-leg gap similar at every weight. Gaps (12pt, units along the arm):

  | | ExtraLight | Bold | ExtraBlack |
  |---|---|---|---|
  | K | 86 | 99 | 114 |
  | k | 63 | 76 | 95 |

  Italic gaps run 8–13 units larger.
- 1 = S; 2 and 5 = the leg edges ∩ the arm; 3 and 4 = the leg edges ∩ the
  baseline; 6 = the midpoint of 5 and 7, on the arm, which keeps the
  14-node structure.
- The feet move by under 10 units, so advance widths are unchanged.
  Exception: heavy k, where the steeper leg widens the foot by up to 26
  units each way (above 700).

### Checks
- [x] All 14 roman and 13 italic masters; build clean
- [x] Proof gains a K / k row (K k Kick kayak Ķ ķ ĸ)
- [ ] Visual check (user): gap size (GAP_FRAC), leg angle

---

## 10. Round dots — every square dot becomes a circle ◐ (2026-10-16)

**Intent (user):** make the dots (umlauts, i, j, exclamation marks and
so on) circles instead of squares.

**Script:** `sources/edits/10_round_dots.py`, run once per source;
`--dry-run` lists what it would change.

**Which contours:** a path counts as a dot when, in **every** master, it
has 4 line nodes forming a rectangle (upright) or a parallelogram at the
italic angle (italic), with equal top and bottom widths and an aspect of
0.6–1.7. That leaves out acute and grave strokes (other slants) and the
ff bridge (unequal edges). Both sources find the same **50 dot contours in
36 glyphs:**

- **Letters:** i, j, fi
- **Punctuation:** period, colon, semicolon, exclam / exclamdown,
  question / questiondown, periodcentered (+ .loclCAT)
- **Symbols:** bulletoperator, commercialMinusSign, divide
- **Combining marks:** dieresiscomb, dotaccentcomb (+ .i), dotbelowcomb,
  dieresisbelowcomb, plus the .case forms and every stacked-accent combo
  holding a dot

Everything else (ä, ï, ż, ŀ, ellipsis, ij, İ, ǘ and so on) is built from
components and follows.

**Size and shape:**
- The circle's area equals that of a square of side √(w·h), so
  d = 2√(w·h/π) ≈ **1.128×** the side: the usual optical correction, so a
  round dot doesn't read smaller than the square it replaces.
- d is capped at 1.128× the height, so the squashed dots in heavy stacked
  accents (up to 190×130) grow upward no more than a square dot does.
- The circle is centred on the old dot. On the baseline it overshoots by
  about 4 units at ExtraLight, as round shapes should.
- In the italic the dots stay true circles; they aren't slanted.

**Compatibility:** each circle runs in the same direction as the rectangle
it replaces and starts at its bottom point in every master: 12 nodes
(4 smooth curves). Only master layers are written; none of these glyphs has
brace layers.

### Checks
- [x] 14 roman and 13 italic masters; build clean; a re-run finds 0 square
      dots
- [x] Proof gains a dots row (i j ä Ö ż ŀ ! ? ¡ ¿ . : ; … · ÷ ǘ ṡ)
- [ ] Visual check (user): dot size, and spacing around ! ? . : now that
      the dots are round

---

## 11. a — rounder bowl arching down into the stem ◐ (2026-10-16)

**Intent (user):** a more "bulbous" a, like Proxima Nova's. Stock Nunito
Sans's bowl has a flat top: the outer edge and the counter top both run
level into the stem, leaving a square inside corner. The bowl's top should
arch and come **down** into the stem instead, the way this font's own d
bowl meets its stem.

**Script:** `sources/edits/11_a_round_bowl.py`, run once per source. Knobs:
`INNER_DROP` 0.40, `OUTER_DROP` 0.22, `TILT` 15°.

### Rule (per master)

The rule works in unslanted space (x − y·tan(italic angle)), so it holds
on the italic masters. In every master the stock a is 39 nodes with one
type pattern (asserted). The script changes only 20–21 and 27–34, and adds
four off-curves, making 43 nodes.

- **Peaks:** the counter top (29) and the bowl top (32) move over their
  bottom extremes (23, 38) and keep their heights.
- **Left quarters** (26→29 counter, 35→32 bowl): handle fractions come from
  the same master's **o** (about 0.6), so the bowl gets the family's
  roundness. The italic o is a true italic oval, skewed even unslanted, so
  italic masters borrow the matching upright master's o.
- **Arches into the stem:** 29→30 and 31→32 become curves that leave the
  peak level and come down to junctions inside the stem:
  - inner (30) at peak − INNER_DROP × counter height
  - outer (31) at peak − OUTER_DROP × bowl height

  They meet the stem 15° off vertical, so the join reads as a crotch, as in
  d. At 12pt ExtraLight, the counter's top-right meets the stem at 155
  (from 238) and the bowl's at 213 (from 275).
- **Node 20:** where the stem edge turns into the counter bottom, it drops
  to the inner junction if it sat above it, with handle 21 scaled to match.

**Taller bowl (user, same day): `BOWL_RISE` 0.10.** Before the construction
runs, the bowl is stretched 10% taller. Its top rises by 0.10 × the stock
bowl height (ExtraLight 275 → 303, Bold 290 → 320); the bottom stays on the
baseline. Points at or below the counter bottom don't move, points at or
above the counter top rise fully, and those between rise in proportion
(unslanted), so the top and bottom strokes keep their thickness. The arches
are then built on the taller bowl, with junctions at ExtraLight 172 inner
and 235 outer.

The opening under the a's top arch shrinks:

| Masters | Opening (units) |
|---|---|
| ExtraLight | 131–170 |
| Bold | 66–85 |
| ExtraBlack | 15–39 (tight, above 700) |

The composites (á ä ą …) follow. `a.ss01` (single-storey) is untouched.

### Checks
- [x] 14 roman and 13 italic masters; build clean
- [x] Proof gains an a row (a aa ao ad á ä ą banana)
- [ ] Visual check (user): bowl roundness, how low the top meets the stem
      (INNER_DROP / OUTER_DROP), crotch angle (TILT)

---

## 12. 1 — no foot ◐ (2026-10-16)

**Intent (user):** remove the bottom horizontal stroke from the 1.

**Script:** `sources/edits/12_one_footless.py`, run once per source.

- **Swap with the stock alternate.** Nunito Sans already draws a footless 1
  as a stylistic alternate: `one.ss01` and `one.tosf.ss01`, recentred in
  the 600 tabular width. The script swaps outlines, `one` ↔ `one.ss01` and
  `one.tosf` ↔ `one.tosf.ss01`. The footless 1 becomes the default, and
  ss01 now gives the footed 1. (ss01 also switches a to single-storey.)
- **`one.dnom` by rule.** It has no alternate, and `one.numr`, ¹, ₁, ½ and
  ¼ are built from it. Nodes 0, 1, 10 and 11 (the foot ends) are dropped.
  The stem edges (lines 3→2 and 8→9, which follow the slant in the italic)
  are extended to the baseline, giving 12 → 8 nodes. The glyph is then
  centred like the others (below).
- **Centring (user: "spacing around the 1 seems unbalanced").** The stock
  footless alternates sit off-centre with more room on the right:

  | 12pt glyph | left / right before | after |
  |---|---|---|
  | one, ExtraLight | 165 / 218 | 192 / 192 |
  | one, Bold | 104 / 170 | 137 / 137 |
  | one.tosf, ExtraLight | 58 / 331 | 194 / 194 |

  After the swap, `one`, `one.tosf` and the footless `one.dnom` are each
  shifted so the left and right sidebearings are equal, measured
  unslanted. Widths are unchanged because the figures are tabular (600).
  The footed 1 in ss01 keeps its stock spacing.
- **Kerning:** no kerning or groups depend on the 1's shape (one is
  ungrouped; the only pair is fraction → oneinferior).

### Checks
- [x] 14 roman and 13 italic masters; build clean
- [x] Proof gains a 1 row (1 11 2024 Il1 ¹ ₁ ½ ¼)
- [ ] Visual check (user), especially the fraction / superscript 1, and
      whether a tabular 1 still looks too loose (proportional figures
      would be a separate change)

---

## 13. 1 — proportional by default, footed tabular 1 under tnum ◐ (2026-10-16)

**Intent (user):** even centred, the footless 1 in its 600 tabular advance
left too much space on both sides in typed numbers (2011, 1,111). Then:
"for the tabular 1 … use the stock 1 with the bottom stroke, since it
provides better optical balance".

**Script:** `sources/edits/13_one_proportional.py`, run once per source,
after edit 12.

### What it does

**`one`, `one.tosf`: proportional.** The outline is shifted and the advance
narrowed, measured unslanted:
- RSB = I's sidebearing in the same master (the 1's right side is a
  straight stem)
- LSB = `LSB_FRAC` 0.75 × that (the flag leaves open space under it)

| 12pt | sidebearings | width |
|---|---|---|
| ExtraLight | 72 / 96 | 600 → 384 |
| Bold | 57 / 76 | 600 → 460 |

The oldstyle 1 lands close by: 380 at ExtraLight, 442 at Bold.

**`one.tf`, `one.tosf.tf`: new.** Each is a single component of the
**stock footed 1** (`one.ss01` / `one.tosf.ss01` since edit 12's swap),
600 wide.

**Features:**
- New `tnum`, placed right after `onum` so oldstyle + tabular chains:
  `sub one by one.tf; sub one.tosf by one.tosf.tf;`
- `ss01` gains `sub one.tf by one.ss01; sub one.tosf.tf by one.tosf.ss01;`
  so ss01 with tnum still gives the footed 1.

The other figures are already tabular, so only the 1 needs a .tf form.
Fraction, superscript and subscript figures (one.dnom and friends) stay
tabular at 380. Edit 12's centring of the default 1 is overridden here,
but its dnom foot removal and centring still apply.

**Replay check:** restoring the stock 1 glyphs and running 12 then 13
reproduces both sources byte for byte.

### Checks
- [x] Shaping, roman and italic VF ("2011"): default one 384; tnum → one.tf
      600; onum+tnum → one.tosf.tf 600
- [x] Build clean; proof 1 row adds 2011 and 1,111, plus a tnum line
- [ ] Visual check (user): proportional 1 spacing (LSB_FRAC, the I
      sidebearing basis)

---

## 14. l — plain stem like I by default; the tailed l moves to ss02 ◐ (2026-10-16)

**Intent (user):** "for nunuiko display in particular i'm leaning towards
not disambiguating the lower case l and making it look like the capital I
- nunuiko is the ui font, and it makes sense to keep it there". The
sister family Nunuïko keeps its tailed l.

**Script:** `sources/edits/14_plain_l_default.py`, run once per source.

Nunito Sans already has the plain l: `l.ss02` is a 4-node stem with the
same outline as I (85–127 × 0–705 at 12pt ExtraLight). Every l-based glyph
has a complete `.ss02` twin built on it. So the pairs **swap names**, and
the outlines, widths, anchors and kerning groups travel with their shapes.
The pairs are l, lacute, lcaron, lcommaaccent, ldot, ldotbelow, lj,
llinebelow, lslash, fl and f_f_l, each with its `.ss02`.

**Renamed** wherever a name points at a shape:
- glyphname lines
- component refs (palochka-cy keeps pointing at the plain stem)
- the direct kerning pairs on llinebelow and lslash, which belong to the
  tailed shapes
- dlig's `sub f l by fl.ss02`, which meant the plain fl and now reads
  `sub f l by fl`

**Unicode values** move to the new default glyphs. Insert them right after
the glyphname line: a layer can carry its own userData, and an early
version that anchored on `userData` lost ł's U+0142.

**Feature code left as is** (liga, ss02, ccmp, locl): by name, l is now the
plain default and ss02 gives the tailed one.

**Edits 01 and 07:** the l tail (01) and the fl width fix (07) now shape the
ss02 alternates.

### Checks
- [x] Shapes moved intact (every master, every pair); unicodes only on the
      defaults; glyph count unchanged (1124)
- [x] Shaping, roman and italic VF: Il1 → I l one; ffl → f_f_l (plain);
      ss02 → f_f_l.ss02 / fl.ss02 / lslash.ss02; dlig → fl
- [x] Build clean; proof l row recaptioned, plus an ss02 line
- [ ] Visual check (user)

---

## Replay procedure (Nunito Sans → Nunuïko Display)

1. For each glyph above, read the **Operation / rule** — apply the rule to
   Nunito Sans's outlines (its coordinates differ; the rules shouldn't).
2. Nunito Sans has straight terminals — some operations may need
   re-interpretation (e.g. the `f` downturn on a cut terminal); note any
   divergence in the glyph's "Nunito Sans replay notes" line and mirror the
   final decision back here.
3. Run the same compatibility + size-ramp checks.
