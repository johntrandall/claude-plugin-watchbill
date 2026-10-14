#!/usr/bin/env bash
# Run the watchbill eval suite from a clean copy of the plugin (the repo's plugin/ folder):
# copying only tracked and untracked-not-ignored files keeps eval results and caches out of
# the graded copy, and keeps the repo's gitignored reference/ clones (over 20,000 files, which
# `claude plugin eval` refuses) out even if someone points the copy at the repo root.
#   plugin/evals/run-clean.sh [--extra-cases DIR]... [extra `claude plugin eval` options]
# --extra-cases DIR copies each case folder in DIR (a folder holding prompt.md) into the copy's
# evals/, so private cases (your own configuration values) run beside the public ones without
# shipping. Cases pin their configuration with EVAL_WATCHBILL_<KEY> in their env: frontmatter
# (eval cases may set only EVAL_* variables). The judge is Sonnet: Haiku failed answers that met
# every criterion.
set -euo pipefail
plugin="$(cd "$(dirname "$0")/.." && pwd)"
copy="$(mktemp -d "${TMPDIR:-/tmp}/watchbill-eval.XXXXXX")/watchbill"
mkdir -p "$copy"
git -C "$plugin" ls-files -co --exclude-standard -z -- . | rsync -a --from0 --files-from=- "$plugin/" "$copy/"
args=()
while [ $# -gt 0 ]; do
  case "$1" in
    --extra-cases)
      [ $# -ge 2 ] || { echo "run-clean.sh: --extra-cases needs a folder" >&2; exit 2; }
      src="$(cd "$2" && pwd)"
      for case_dir in "$src"/*/; do
        [ -f "$case_dir/prompt.md" ] || continue
        name="$(basename "$case_dir")"
        if [ -e "$copy/evals/$name" ]; then echo "run-clean.sh: case $name already exists" >&2; exit 2; fi
        rsync -a --exclude results "$case_dir" "$copy/evals/$name/"
        echo "extra case: $name" >&2
      done
      shift 2 ;;
    *) args+=("$1"); shift ;;
  esac
done
echo "eval copy: $copy" >&2
claude plugin eval "$copy" --trust-plugin --no-publish --judge-model sonnet --output-dir "$plugin/evals/results/$(date +%Y-%m-%dT%H-%M-%S)" ${args[@]+"${args[@]}"} < /dev/null
