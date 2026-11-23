#!/usr/bin/env bash
# Re-port check: diff upstream promoted skills against what's installed in Hermes.
# Usage: ./hermes/sync.sh
# Report-only. Nothing is copied or applied.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

UPSTREAM="origin"  # this repo's origin remote points at mattpocock/skills
INSTALLED="${HERMES_SKILLS_DIR:-$HOME/.hermes/skills/mattpocock}"
SRC_A="$PWD/skills/engineering"
SRC_B="$PWD/skills/productivity"

if [ ! -d "$INSTALLED" ]; then
  echo "ERROR: installed skills dir not found: $INSTALLED" >&2
  exit 1
fi

git fetch -q "$UPSTREAM"
echo "upstream $UPSTREAM/main at: $(git log --oneline -1 "$UPSTREAM/main")"
echo "last ported from:          $(git log --oneline -1 -- hermes/skills 2>/dev/null || echo 'no prior port commit')"
echo

new=(); changed=(); removed=(); unchanged=0

# names upstream
upstream_names=$( { ls "$SRC_A" "$SRC_B" 2>/dev/null; } | sort -u | grep -v '^README' || true )

for name in $upstream_names; do
  for src in "$SRC_A" "$SRC_B"; do
    if [ -f "$src/$name/SKILL.md" ]; then
      if [ -f "$INSTALLED/$name/SKILL.md" ]; then
        if diff -qr "$src/$name" "$INSTALLED/$name" >/dev/null 2>&1; then
          unchanged=$((unchanged+1))
        else
          changed+=("$name")
        fi
      else
        new+=("$name")
      fi
      break
    fi
  done
done

# names installed but gone upstream
for d in "$INSTALLED"/*/; do
  name=$(basename "$d")
  [ "$name" = "README.md" ] && continue
  [ ! -f "$d/SKILL.md" ] && continue
  if ! { [ -d "$SRC_A/$name" ] || [ -d "$SRC_B/$name" ]; }; then
    removed+=("$name")
  fi
done

echo "=== diff: upstream vs installed ($INSTALLED) ==="
echo "unchanged: $unchanged"
[ ${#new[@]} -gt 0 ]     && { echo "NEW upstream:";     printf '  %s\n' "${new[@]}"; }
[ ${#changed[@]} -gt 0 ] && { echo "CHANGED upstream:";  printf '  %s\n' "${changed[@]}"; }
[ ${#removed[@]} -gt 0 ] && { echo "REMOVED upstream:";  printf '  %s\n' "${removed[@]}"; }
if [ ${#new[@]} -eq 0 ] && [ ${#changed[@]} -eq 0 ] && [ ${#removed[@]} -eq 0 ]; then
  echo "up to date — nothing to re-port."
fi
echo
echo "To apply: copy the flagged skill dirs into $INSTALLED, then commit"
echo "  1) the local skills repo:  cd ~/.hermes/skills && git add mattpocock && git commit"
echo "  2) this fork:              refresh hermes/skills/ from the installed dir, commit, push"
