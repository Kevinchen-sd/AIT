#!/usr/bin/env zsh
# Toggle or set a repo's visibility using GitHub CLI.
# Usage:
#   ./scripts/visibility-gh.zsh                 # toggles current repo (from cwd)
#   ./scripts/visibility-gh.zsh Kevinchen-sd/AIT
#   ./scripts/visibility-gh.zsh Kevinchen-sd/AIT public
#   ./scripts/visibility-gh.zsh Kevinchen-sd/AIT private

set -euo pipefail

REPO="${1:-}"
TARGET="${2:-toggle}"  # "public" | "private" | "toggle"

if ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI (gh) not found. Install: https://cli.github.com/"
  exit 1
fi

# If no repo given, infer from current directory
if [[ -z "$REPO" ]]; then
  REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner) || {
    echo "Error: not in a Git repo, and no repo arg provided (format owner/repo)."
    exit 1
  }
fi

# Read current visibility
is_private=$(gh repo view "$REPO" --json isPrivate -q .isPrivate)
if [[ "$TARGET" == "toggle" ]]; then
  if [[ "$is_private" == "true" ]]; then
    TARGET="public"
  else
    TARGET="private"
  fi
fi

if [[ "$TARGET" != "public" && "$TARGET" != "private" ]]; then
  echo "Error: TARGET must be 'public', 'private', or 'toggle'."
  exit 1
fi

echo "Repo: $REPO"
echo "Current: $([[ "$is_private" == "true" ]] && echo private || echo public)"
echo "Changing to: $TARGET"

# Accept consequences note (fork detachment, watchers, etc.)
gh repo edit "$REPO" \
  --accept-visibility-change-consequences \
  --visibility "$TARGET"

# Print result
echo -n "New visibility: "
gh repo view "$REPO" --json isPrivate -q '.isPrivate | if . then "private" else "public" end'
echo
