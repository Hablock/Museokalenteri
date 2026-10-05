#!/usr/bin/env bash
# Käsittele jokainen erä omassa Claude-istunnossaan. Epäonnistunut erä ei kaada muita;
# sen lähteet jäävät käsittelemättömiksi ja yritetään seuraavassa ajossa.
set -uo pipefail

MODEL="${CLAUDE_MODEL:-claude-sonnet-5}"
ALLOWED="Read,Glob,Grep,Edit(./museonayttelyt-auto.json),Edit(./gallerianayttelyt-auto.json),Edit(./automation/cache/changes/**),Bash(python3 automation/fetch_page.py:*),Bash(python3 automation/validate.py)"
DENIED="Read(./.git/**),Edit(./automation/*.py),Edit(./automation/*.sh),Edit(./automation/*.md),Edit(./automation/sources.json),Edit(./.github/**),WebFetch,WebSearch"

mkdir -p automation/cache/changes automation/cache/usage

for batch in automation/cache/batches/batch-*.json; do
  [ -e "$batch" ] || continue
  name=$(basename "$batch" .json)
  echo "::group::$name"
  claude -p "Lue ohjeet tiedostosta automation/prompt.md ja noudata niitä. Käsittele erätiedosto $batch. Kirjoita muutoslista tiedostoon automation/cache/changes/$name.json." \
    --model "$MODEL" \
    --max-turns 150 \
    --permission-mode dontAsk \
    --allowedTools "$ALLOWED" \
    --disallowedTools "$DENIED" \
    --output-format json > "automation/cache/usage/$name.json" \
    || echo "::warning::$name päättyi virheeseen"
  jq -r '"kierroksia: \(.num_turns), virhe: \(.is_error), \(.result // "" | .[0:500])"' "automation/cache/usage/$name.json" 2>/dev/null || true
  echo "::endgroup::"
done
exit 0
