#!/bin/bash
# Free call: checks the Runway key works and prints the credit balance. Never prints the key.
cd "$(dirname "$0")/.."
KEY="${RUNWAYML_API_SECRET:-$(grep -E '^RUNWAYML_API_SECRET=' .env 2>/dev/null | cut -d= -f2- | tr -d '"'"'"' ')}"
[ -z "$KEY" ] && { echo "No key: paste it into .env after RUNWAYML_API_SECRET="; exit 1; }
curl -s https://api.dev.runwayml.com/v1/organization \
  -H "Authorization: Bearer $KEY" -H "X-Runway-Version: 2024-11-06" \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print("credits:", d.get("creditBalance", d))'
