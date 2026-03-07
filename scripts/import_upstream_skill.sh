#!/usr/bin/env bash
set -euo pipefail

# Controlled import helper (review-first):
#   scripts/import_upstream_skill.sh <git_repo_url> <git_ref> <source_skill_path> <target_dir_name>
#
# Example:
#   scripts/import_upstream_skill.sh \
#     https://github.com/anthropics/skills.git \
#     main \
#     skills/example-skill \
#     example-skill

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <git_repo_url> <git_ref> <source_skill_path> <target_dir_name>"
  exit 1
fi

REPO_URL="$1"
GIT_REF="$2"
SOURCE_PATH="$3"
TARGET_DIR="$4"

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Cloning $REPO_URL@$GIT_REF ..."
git clone --depth 1 --branch "$GIT_REF" "$REPO_URL" "$TMP_DIR/repo"

if [[ ! -d "$TMP_DIR/repo/$SOURCE_PATH" ]]; then
  echo "Source path not found: $SOURCE_PATH"
  exit 1
fi

if [[ -e "$ROOT_DIR/$TARGET_DIR" ]]; then
  echo "Target already exists: $ROOT_DIR/$TARGET_DIR"
  echo "Refusing to overwrite."
  exit 1
fi

cp -R "$TMP_DIR/repo/$SOURCE_PATH" "$ROOT_DIR/$TARGET_DIR"

COMMIT_SHA="$(git -C "$TMP_DIR/repo" rev-parse HEAD)"

cat <<EOF
Imported to: $ROOT_DIR/$TARGET_DIR
Source repo: $REPO_URL
Pinned ref:  $GIT_REF
Commit SHA:  $COMMIT_SHA

Next steps (required):
1) Audit SKILL.md + scripts/references/assets
2) Add catalog entry in catalog/skills.yaml
3) Add source metadata/provenance
4) Run: python3 scripts/skill_audit.py
EOF
