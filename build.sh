#!/usr/bin/env bash
# Build Nunuiko Display (Nunito Sans-derived straight-terminal cut).
#
# gftools 0.9.996's builder reads sources/config.yaml, builds the static
# instances + the two variable fonts (roman + italic), splits roman/italic
# itself, and sets STAT / italic bits — its output is already final (no
# separate instancer / gen-stat / fix.py step; see PLAYBOOK.md).
#
# display_name.py then stamps the diaeresis onto the PUBLIC name records
# (Nunuiko Display -> Nunuïko Display); PostScript names / filenames stay
# ASCII. Run from the repo root with the venv active:
#   source .venv/bin/activate && ./build.sh
set -e

cd "$(dirname "$0")/sources"

gftools builder config.yaml

# public family name -> diaeresis form (post-build, on the built VFs)
python3 display_name.py

# builder scratch dirs
rm -rf instance_ufos master_ufo build.ninja .ninja_log 2>/dev/null || true

echo "build.sh: done"
