#!/usr/bin/env bash
set -euo pipefail

# Publish privacy.md to GitHub Pages as https://<USER>.github.io/privacy/
# and auto-enable Pages (Deploy from branch: main / root) via the GitHub API.
#
# Prereqs:
#  1) Create an empty GitHub repo named "privacy"
#  2) Set env var REMOTE to that repo URL, e.g.:
#       export REMOTE=git@github.com:<USER>/privacy.git
#       # or
#       export REMOTE=https://github.com/<USER>/privacy.git
#  3) Set env var GITHUB_TOKEN with 'repo' scope
#       export GITHUB_TOKEN=ghp_xxx   # or use a fine-grained PAT with Pages access
#  4) Run this script from inside the folder that contains privacy.md

if [[ -z "${REMOTE:-}" ]]; then
  echo "❌ Please set REMOTE to your GitHub repo URL, e.g.:"
  echo "   export REMOTE=git@github.com:<USER>/privacy.git"
  exit 1
fi

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "❌ Please set GITHUB_TOKEN (needs 'repo' scope) before running."
  exit 1
fi

# Extract OWNER and REPO from REMOTE (supports SSH and HTTPS forms)
# Examples:
#   git@github.com:owner/repo.git
#   https://github.com/owner/repo.git
#   https://github.com/owner/repo
OWNER=""
REPO=""
if [[ "$REMOTE" =~ github\.com[:/]+([^/]+)/([^/.]+)(\.git)?$ ]]; then
  OWNER="${BASH_REMATCH[1]}"
  REPO="${BASH_REMATCH[2]}"
else
  echo "❌ Could not parse OWNER/REPO from REMOTE: $REMOTE"
  exit 1
fi

if [[ "$REPO" != "privacy" ]]; then
  echo "⚠️  Target repo is '$REPO' (not 'privacy'). Continuing anyway."
fi

API="https://api.github.com"
API_VER="2022-11-28"
PAGES_URL="https://${OWNER}.github.io/${REPO}/"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

# Prepare minimal site
cp privacy.md "$WORKDIR/index.md"
touch "$WORKDIR/.nojekyll"

# Init, commit, push to main
(
  cd "$WORKDIR"
  git init -q
  git add .
  git commit -m "Initial privacy site"
  git branch -M main
  git remote add origin "$REMOTE"
  git push -u origin main --force
)

echo "✅ Pushed to $REMOTE"

# Enable GitHub Pages: Deploy from branch 'main' with root path '/'
echo "🔧 Enabling GitHub Pages via API…"

create_or_update_pages() {
  # Try POST (create). If it already exists, fall back to PUT (update).
  set +e
  RESP_CREATE="$(curl -sS -w '%{http_code}' -o /tmp/pages_create.json \
    -X POST "${API}/repos/${OWNER}/${REPO}/pages" \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: ${API_VER}" \
    -d '{"source":{"branch":"main","path":"/"}}')"
  set -e

  if [[ "$RESP_CREATE" == "201" || "$RESP_CREATE" == "202" ]]; then
    echo "✅ Pages created."
    return 0
  fi

  # If 409/422 etc., try PUT (update)
  set +e
  RESP_UPDATE="$(curl -sS -w '%{http_code}' -o /tmp/pages_update.json \
    -X PUT "${API}/repos/${OWNER}/${REPO}/pages" \
    -H "Authorization: Bearer ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: ${API_VER}" \
    -d '{"source":{"branch":"main","path":"/"}}')"
  set -e

  if [[ "$RESP_UPDATE" == "200" || "$RESP_UPDATE" == "202" ]]; then
    echo "✅ Pages updated."
    return 0
  fi

  echo "❌ Failed to enable Pages."
  echo "POST status: $RESP_CREATE; body:"
  sed 's/^/   /' /tmp/pages_create.json || true
  echo "PUT  status: $RESP_UPDATE; body:"
  sed 's/^/   /' /tmp/pages_update.json || true
  exit 1
}

create_or_update_pages

# Print final info
echo "🌐 Site URL: ${PAGES_URL}"
echo "ℹ️  If you use custom Pages settings or a different branch/path later,"
echo "    update them under: https://github.com/${OWNER}/${REPO}/settings/pages"