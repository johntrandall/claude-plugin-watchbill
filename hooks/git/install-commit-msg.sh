#!/usr/bin/env bash
# Install the watchbill commit-msg hook (build events as trailers, council S2) into
# one system repository. Copies, so a plugin update never changes a repo's hook
# silently; re-run to update.
#   install-commit-msg.sh <repo> [--chain]
# An existing commit-msg hook that is not watchbill's is refused unless --chain,
# which renames it commit-msg.local; the watchbill hook runs it first.
set -euo pipefail
repo="${1:?usage: install-commit-msg.sh <repo> [--chain]}"
chain="${2:-}"
source_hook="$(cd "$(dirname "$0")" && pwd)/commit-msg"
hooks_dir="$(git -C "$repo" rev-parse --path-format=absolute --git-path hooks)"
mkdir -p "$hooks_dir"
target="$hooks_dir/commit-msg"
if [[ -e "$target" ]] && ! grep -q "watchbill commit-msg" "$target"; then
  if [[ "$chain" != "--chain" ]]; then
    echo "install-commit-msg: $target exists and is not watchbill's; re-run with --chain to keep it as commit-msg.local" >&2
    exit 1
  fi
  mv "$target" "$hooks_dir/commit-msg.local"
  echo "kept the existing hook as $hooks_dir/commit-msg.local"
fi
cp "$source_hook" "$target"
chmod +x "$target"
echo "installed $("$target" --version) at $target"
