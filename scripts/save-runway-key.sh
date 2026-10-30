#!/bin/bash
# Saves the Runway key into the repo .env (gitignored) without echoing it or touching shell history.
# Needs a real terminal: the `!` prompt in Claude Code can't take typed input.
cd "$(dirname "$0")/.."
printf 'Paste Runway key, then Enter: '
read -rs KEY; echo
[ -z "$KEY" ] && { echo "Nothing pasted, .env unchanged."; exit 1; }
{ grep -v '^RUNWAYML_API_SECRET=' .env 2>/dev/null; echo "RUNWAYML_API_SECRET=$KEY"; } > .env.tmp
mv .env.tmp .env && chmod 600 .env
unset KEY
echo "Saved. Checking balance (free call):"
./scripts/runway-balance.sh
