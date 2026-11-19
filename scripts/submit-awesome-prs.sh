#!/usr/bin/env bash
# Open "add Sounds of the Adriatic" PRs against prepared awesome-list targets.
#
# Requirements:
#   1. gh CLI installed and authenticated with rights to fork + open PRs on public repos:
#        gh auth login -h github.com          # pick 'repo' (or public_repo) scope
#   2. git SSH access to github.com (already working in this environment)
#
# Usage:
#   bash scripts/submit-awesome-prs.sh            # all targets
#   bash scripts/submit-awesome-prs.sh 1 3        # only targets #1 and #3
#
# Targets are defined in TARGETS below: repo|anchor-substring|entry line.
# The script inserts the entry line directly after the first README line that
# contains the anchor, in a fresh branch of a fork, then opens the PR.
# Idempotent: skips targets that already have an open PR from our branch.

set -euo pipefail

BRANCH="add-sounds-of-the-adriatic"
PR_TITLE="Add Sounds of the Adriatic — sound map of the Croatian coast"
PR_BODY="Adds [Sounds of the Adriatic](https://sound.marespot.com/) — a dark, static sound map of the Croatian coast: tap a pin to play a field recording. 11 sounds, all CC0/CC-BY with creator, license and source credited on every pin (see the [credits page](https://sound.marespot.com/credits.html)). Map coastline: Natural Earth (public domain). Audio loads only when a pin is tapped. No tracking.

Happy to adjust wording or placement to fit the list."

# repo|anchor|entry
TARGETS=(
"landscape82/awesome-sound-design-resources|radio aporee ::: maps|- **[Sounds of the Adriatic](https://sound.marespot.com/)** 🆓 🌐 - Dark sound map of the Croatian coast: tap a pin to play free CC0/CC-BY field recordings (creator + license on every pin)."
"sshuair/awesome-gis|CHATTY MAPS|- [Sounds of the Adriatic](https://sound.marespot.com/) - Sound map of the Croatian coast: tap a pin to hear CC0/CC-BY field recordings (harbours, coves, wind, bells)."
"Spacial/awesome-arts|SOUNDS OF THE FOREST|- [Sounds of the Adriatic](https://sound.marespot.com/): a dark sound map of the Croatian coast — free CC-BY field recordings, tap a pin to listen."
"fmariv/awesome-web-gis-resources|- [Flourish](https://flourish.studio/)|- [Sounds of the Adriatic](https://sound.marespot.com/) — interactive sound map of the Croatian coast: tap a pin to play CC0/CC-BY field recordings."
)

insert_after_anchor() {
  # $1 = readme path, $2 = anchor substring, $3 = entry line
  python3 - "$1" "$2" "$3" <<'PY'
import sys
path, anchor, entry = sys.argv[1], sys.argv[2], sys.argv[3]
lines = open(path).read().splitlines(keepends=True)
for i, ln in enumerate(lines):
    if anchor in ln:
        if any('sound.marespot.com' in l for l in lines):
            print('already present, skipping insert'); sys.exit(0)
        lines.insert(i + 1, entry + '\n')
        open(path, 'w').write(''.join(lines))
        print(f'inserted after line {i+1}')
        sys.exit(0)
print(f'ANCHOR NOT FOUND: {anchor}', file=sys.stderr); sys.exit(1)
PY
}

main() {
  gh auth status >/dev/null 2>&1 || { echo "gh not authenticated — run: gh auth login -h github.com"; exit 1; }
  local GHUSER; GHUSER=$(gh api user -q .login)
  echo "Authenticated as $GHUSER"
  local workdir="/tmp/awesome-prs"; mkdir -p "$workdir"
  local only=("$@"); local idx=0
  for t in "${TARGETS[@]}"; do
    idx=$((idx+1))
    if [ ${#only[@]} -gt 0 ] && ! printf '%s\n' "${only[@]}" | grep -qx "$idx"; then continue; fi
    IFS='|' read -r repo anchor entry <<< "$t"
    local name="${repo##*/}" fork="$GHUSER/$name"
    echo "=== [$idx] $repo"
    # existing open PR from our branch? then skip
    if gh pr list --repo "$repo" --head "$GHUSER:$BRANCH" --json number -q '.[].number' 2>/dev/null | grep -q .; then
      echo "    PR already open, skipping"; continue
    fi
    # fork (if missing) and clone
    gh repo view "$fork" >/dev/null 2>&1 || gh repo fork "$repo" --clone=false
    local dir="$workdir/$name"
    rm -rf "$dir"
    git clone -q "git@github.com:$fork.git" "$dir"
    cd "$dir"
    git checkout -q -b "$BRANCH"
    insert_after_anchor README.md "$anchor" "$entry"
    git add README.md
    git commit -q -m "Add Sounds of the Adriatic sound map"
    git push -q origin "$BRANCH"
    local prurl
    prurl=$(gh pr create --repo "$repo" --head "$GHUSER:$BRANCH" --title "$PR_TITLE" --body "$PR_BODY" -q .url)
    echo "    PR opened: $prurl"
    cd - >/dev/null
  done
  echo "Done."
}

main "$@"
