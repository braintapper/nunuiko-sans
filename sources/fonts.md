# Fonts — UI type direction

The font is one of the cheapest, highest-impact polish levers (see
`theming.md`). One consistent UI family, applied across all KDE font roles, does a
lot of the "one product" work KDE lacks by default.

## Naming rule (house style)

No names starting with **K**. (The whole reason KDE grates aesthetically — KWin,
Kate, Konsole, KWrite, K-everything.) The eventual custom font needs its own,
non-K name.

## Taste reference (aspirational, NOT free)

Favorites — the target *feel*:
- **Proxima Nova** (Mark Simonson) — geometric-humanist hybrid; the web's UI
  darling precisely because it stays legible at UI sizes.
- **Gotham** (H&Co / Monotype) — colder, purely geometric, architectural (based on
  NYC signage).

Both are commercial and can't be redistributed — same problem as Icons8. They serve
as the *reference*, not the shippable asset.

## License lens (consistent with the whole project)

To ship in a public repo, the UI font must be **OFL / redistributable**.

- **Google Sans Flex — SIL OFL. Now free & shippable (as of late 2025).** A
  multi-axis, ground-up open rebuild of the proprietary Google Sans (by David
  Berlow), released under OFL — modify/redistribute freely, just don't sell it
  standalone. Geometric-humanist, i.e. *closer to the Proxima Nova taste target*
  than Nunito. **Strong front-runner.**
  - Naming: the plain brand **"Google Sans"** may still be restricted; **"Google
    Sans Flex"** is the open OFL version — use that one.
  - **5 axes: weight, grade, slant, width, and _roundness_.** The roundness axis is
    the key enabler for the custom-variant plan — dial rounded↔architectural on one
    family and bake a custom instance, instead of choosing between rounded (Nunito)
    and cold-geometric (Gotham/Jost) bases.
  - **"Google Sans Code"** is a *separate monospace* family, also OFL — candidate for
    terminal/editor, not the UI sans.
- **Nunito — SIL OFL. Co-front-runner.** License-clean, large x-height, open forms,
  rounded terminals; holds up well at UI sizes. Warmer/rounder than Google Sans Flex
  — pick based on whether the target feel is friendly (Nunito) or more
  architectural/Proxima-like (Google Sans Flex tuned via roundness).

## Taste axis: rounded vs. architectural

Nunito is geometric but with **rounded terminals** → warmer/friendlier than
Proxima/Gotham, which have sharp, cut terminals. If a variant drifts toward wanting
something more serious / Proxima-like, the closest OSS bases:

| Font | License | Feel |
|---|---|---|
| **Montserrat** | OFL | Most-cited free Proxima/Gotham stand-in |
| **Nunito Sans** | OFL | Straight-terminal sibling of Nunito; less round, more serious |
| **Jost*** | OFL | Pure Futura/Gotham geometry — cold, architectural |
| Mulish, Hanken Grotesk, Figtree, Onest | OFL | Other modern geometric-ish options |

## Why Nunito works at UI sizes (9–11px)

At small sizes legibility is driven by **x-height, aperture openness, spacing, and
hinting** — not geometric purity. Nunito's large x-height and open apertures are why
it stays readable small; tight, small-aperture geometrics (pure Futura, Jost) get
muddy at UI sizes. Same reason Proxima Nova became the UI standard.

## Plan: roll a custom variant of an OSS base

**Base: Nunito (rounded) for text sizes; Nunito Sans for display sizes** — an
*optical-sizing* pairing (see below). Originally used Nunito Sans throughout, but
Nunito's rounded terminals proved easier on the eyes at small UI sizes (less
corner-acuity noise); Nunito Sans's straight terminals look less bulbous/informal
big. Use each where it wins.

### Optical sizing: rounded small → straight large

The instinct "Nunito ≤ ~18px, Nunito Sans above" is textbook **optical sizing** — the
reason type historically shipped separate text/display cuts. Terminal roundness is
the optical axis here: soft small, informal big. Three ways to realize it, by
context:

1. **Where you control size→font (web/CSS, reports, docs):** assign per element/role.
   Easy, no font engineering — covers reporting output directly.
2. **Desktop UI (KDE/Qt/GTK): NO automatic size-threshold switching exists.** Fonts
   are settable only per *role* (general / small / menu / toolbar / window-title),
   not "family A under 18px, B over." Approximate: small roles → Nunito, genuinely
   large roles (window titles) → Nunito Sans. No clean pixel threshold.
3. **The elegant, portable, automatic way — one variable font with an `opsz`
   (optical-size) axis:** rounded terminals at low `opsz`, straight at high `opsz`.
   Renderers with `font-optical-sizing: auto` (CSS default; many apps) interpolate by
   point size automatically — the Nunito→Nunito-Sans transition, seamless, in a
   single family. Collapses "two fonts" into one; folds into the custom-variant plan.
   - **Catch:** an `opsz` axis needs *interpolation-compatible* masters. Nunito and
     Nunito Sans are drawn separately, so one must be redrawn to match the other's
     point structure — real work, but the "right" answer. (Google Sans Flex's
     roundness axis proves rounded↔straight as an axis is buildable.)

Threshold note: ~18px is low for a text→display switch (still text; classic
transitions are ~24px+) — but it's your eyes; the mechanism is identical wherever the
crossover sits. Find it empirically with a size ramp.

> ⚠️ **Nunito Sans is not currently installed** on `bosgame6600h` — `fc-match "Nunito
> Sans"` falls back to Noto Sans. Install it before evaluating the pairing or
> rendering a real ramp.

**Fully OFL-legal**, with one hard rule:
- OFL explicitly permits modification/derivatives.
- **If the base declares a Reserved Font Name (RFN)** — most Google Fonts do,
  Nunito included — **you must rename the derivative.** Can't keep "Nunito" in the
  name. (Verify the exact RFN in Nunito's OFL header — almost certainly just
  "Nunito".)

### Name: **Nunuïko** (display) / `Nunuiko` (internal, ASCII)

Etymology — three nods: **Nun**ito (the source) + **UI** (user interface) + **k**
(a nod to KDE). The `k` is a deliberate, rule-compliant smuggle: the house rule bans
names *starting* with K; this hides one lowercase at the tail (same move as
`oKely-DokEly`).

**Pronunciation:** Nu·nu·i·ko — "Noo-noo-**EE**-koe", four syllables, stress on the
"EE". Deliberately distinct from Nunito ("Noo-**NEE**-toe"): different syllable count,
stressed vowel, and rhythm — which also keeps it clear of the OFL "confusingly
similar" concern. The embedded **UI** lands as its own two-vowel beat in the middle
(u→i = "oo-ee"), a buried easter egg.

**The diaeresis (`ï`)** — two dots — is a **diaeresis / trema**, marking that the `i`
is voiced as a *separate syllable* from the preceding `u` (as in naïve, Noël, Chloë).
It is **not** an umlaut: same glyph (¨), opposite intent —
- *diaeresis* = "voice this vowel separately" (syllable break) ← what's meant here
- *umlaut* = "change this vowel's sound" (German ü/ö/ä)

**ASCII caveat (font-engineering):** keep the diacritic only in the **display /
human-facing name** (`Nunuïko`). Keep the **PostScript name and the filename ASCII**
(`Nunuiko`) — diacritics in font family names cause friction with fontconfig
matching, CSS `font-family`, shells/filenames, and apps that mangle non-ASCII.

**Family scheme** (decide up front — retrofitting names is painful):
- Two-font route: `Nunuïko` = rounded **text** cut; `Nunuïko Display` = straight
  (Nunito-Sans-derived) **display** cut.
- Single-font route: one `opsz` variable font, just `Nunuïko` (no suffix; the
  optical-size axis carries rounded→straight). See optical-sizing section above.

> Note: the six glyph edits (Q/J/l/f/G/K) must be applied to **both** cuts (text and
> display) — or to both masters if going the single `opsz` variable-font route.

### Drawing plan: draw the extremes, not the weights (plain English)

**The one idea:** you draw the *extremes*, and the computer fills in everything
between. Like a **dimmer switch** — you wire up "off" and "full bright," and every
level in the middle is automatic. You never wire each brightness by hand.

- The hand-drawn extremes are called **masters**. The automatic in-between blending
  is **interpolation**. (That's the only jargon.)
- **For thickness (weight):** draw one *really thin* and one *really thick* version.
  The computer blends them to make Regular (400), SemiBold (600), Bold — any
  thickness. **So NO — don't draw a separate 400 and 600.** Draw the two ends; 400
  and 600 fall out automatically *and* stay perfectly matched. Drawing each weight by
  hand = redoing every glyph edit per weight, and they drift out of sync.
- **You want TWO sliders** — thickness *and* roundedness (rounded text ↔ straight
  display). Picture a **square**: draw the **4 corners** —
  `thin+rounded`, `thick+rounded`, `thin+straight`, `thick+straight` — and the
  computer blends to *any* point inside (any thickness at any roundedness). Not "draw
  4 fonts" — "draw 4 corners, get the whole square."

**What this means for the edits:** apply each of the six glyph changes **once per
master** (2 masters if weight-only; 4 masters if weight × roundedness), NOT once per
weight you want to ship.

> FontForge caveat (from above): FontForge edits **one master at a time**. Fine for
> getting a glyph's *shape* right, but the multi-master blend/rebuild is a
> source-`fontmake` job, not a FontForge job. Draw shapes in FontForge → build the
> interpolated family with `fontmake`.

### The actual changes are small (three glyphs + figures)

This is a light-touch derivative, not an alphabet redraw:

1. **Q — slashed tail.** Tail crosses *through* the bowl (a "slashed"/crossing-tail
   Q) rather than sitting outside/below it.
2. **J — upturned terminal.** Bottom curves back **up** (hooked foot), not a plain
   straight descender.
3. ~~**l (lowercase) — shorter tail.**~~ Reduce the foot/tail.
   ⚠️ **Caution:** that tail is Nunito's main disambiguator between `l` / `I` / `1`.
   Shorten it, but test `Il1` adjacent at ~10px before committing so they don't
   collapse into each other.
4. **f - downturned terminal.** Top curves back **down**, but slightly
5. **G - more of a curve before the horizontal stroke** Use the O as an example and do the horizontal stroke at the same point as the original G, and the overhead stroke ending at the same place as the original G
6. **K — sligth notched joint, not a chevron.** Nunito uses a *single-junction* K: arm and
   leg meet the stem at one point, forming a chevron/arrowhead (disliked). Change to
   a **notched joint** — arm meets the stem, **leg branches off the arm** a short
   distance out from the stem, opening the crotch. Small edit: move the leg's origin
   off the stem onto the arm; tune branch distance to taste.
   Apply the same notch to lowercase `k` (same chevron) for a matched pair.

Implementation choice: either **bake these as the defaults** in the renamed
derivative (simplest for a personal font) or expose them as **stylistic sets**
(`ss01…` / `cvXX`) to preserve the originals (cleaner practice). Baking-as-default
is fine here.

### Figures: tabular ≠ monospace (avoid over-building)

Requirement: numbers that align cleanly in columns for reports.

- **What this actually needs: tabular figures** (`tnum` OpenType feature) — all ten
  digits share one fixed advance width so they line up in columns, while letters
  stay proportional. Lives **inside the proportional UI font** as a toggle.
  **→ First check whether stock Nunito already ships `tnum`** (many Google fonts do);
  if so, this is solved for free and needs no new font.
- **What it does NOT need: a full monospace.** A "Nunito Mono" (every glyph on a
  fixed grid) is only required for **code/terminal alignment**, and it's a much
  larger project — re-drawing/re-spacing the whole set to one width. Defer or skip
  unless a rounded *coding* font is specifically wanted. If it is, borrow from
  **Google Sans Code** (OFL) rather than building from zero. (Font name TBD.)

### Tooling (all OSS-friendly)

- The Nunito **source is on GitHub** (`googlefonts/nunito`); typically Glyphs/UFO
  source + a `fontmake` / `gftools` build pipeline — cleanest way to regenerate a
  renamed variant with the swapped glyphs baked in.
- **FontForge** — glyph editing (the Q/J/l redraws).
- `fonttools` (Python) — instancing, subsetting, `tnum` handling, and name-table
  edits (the required rename).

## Apply in KDE

Set all font roles to the chosen family so nothing falls back to defaults — in
System Settings → Text & Fonts, or via `kdeglobals`: `[General]` `font`, `menuFont`,
`toolBarFont`, `smallestReadableFont`, and `[WM]` `activeFont` (window titles).
Do the GUI → diff → codify loop to capture exact keys (see `annoyances.md`).
Design and test at **1x scaling** (see `philosophy.md`).
