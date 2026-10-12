# Penpot uploads

`../../penpot-uploads/` holds the Nunuiko Display font files that were uploaded to the owner's
self-hosted Penpot as a custom font, so the interface designs there use the same typeface as the
apps. That folder contains font files only, so everything in it can be selected at once in the
upload dialog.

Generated 2026-10-12 from `fonts/ttf/` at commit `c0f05f3`.

## Why these files exist

Penpot (2.16, as installed) cannot convert between font formats: its server is missing the
converter program. A `.ttf` uploaded by itself fails. So each weight is supplied as `.ttf`, `.otf`
and `.woff` together and nothing is left for the server to convert.

Penpot also wants one file per weight, so the static files in `fonts/ttf/` are used, not the
variable fonts. The width and optical-size axes are therefore not available in Penpot.

## What is in the folder

54 files, three formats for each of 18 static fonts:

- **Nunuiko Display**: eight weights (ExtraLight 200 to Black 900), upright and italic.
- **Nunuiko Display ExtraBlack**: upright and italic. The font files name this as its own family,
  so Penpot lists it separately.

The `.ttf` files are byte-for-byte copies of `fonts/ttf/`. The `.otf` files have their outlines
converted from quadratic to cubic curves. They are for Penpot only; do not ship them anywhere else.

## Uploading

1. In the Penpot dashboard (not inside a file), open **Fonts**.
2. Add fonts, and select **every file in `penpot-uploads/` in one pick**. Penpot groups the three
   formats of a weight into one entry only when they arrive together; a format uploaded by itself
   fails.
3. Press **Upload all**.

Penpot shows a warning about vertical metrics. It is expected: the fonts use the usual
Google Fonts setup, where the Windows clipping bounds differ from the line-height values on
purpose. Do not "fix" the files to silence it.

## Regenerating

Do this when the fonts change and the Penpot copy should follow. It needs `fonttools`.

```bash
# from the repo root
python sources/penpot/make_formats.py fonts/ttf penpot-uploads
```

`make_formats.py` copies each `.ttf` and writes the `.otf` and `.woff` beside it. Then delete the
old Nunuiko Display families in Penpot's Fonts page and upload the new files.
