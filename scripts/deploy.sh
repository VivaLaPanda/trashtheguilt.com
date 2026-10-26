#!/usr/bin/env bash
# Build and deploy to Cloudflare Pages: scripts/deploy.sh [branch]. Token is read from a local file, never committed.
set -euo pipefail
cd "$(dirname "$0")/.."
branch="${1:-main}"
uv run build.py
CLOUDFLARE_API_TOKEN="$(cat "${CF_TOKEN_FILE:-$HOME/.config/cloudflare/token}")"
export CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID="$(curl -fsS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/zones?name=trashtheguilt.com" \
  | python3 -c 'import json, sys; print(json.load(sys.stdin)["result"][0]["account"]["id"])')"
export CLOUDFLARE_ACCOUNT_ID
npx --yes wrangler@4 pages deploy dist --project-name trashtheguilt --branch "$branch" --commit-dirty=true
