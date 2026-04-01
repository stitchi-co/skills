#!/usr/bin/env bash
# Fetch pipeline data from Pipedrive for review analysis.
# Usage: fetch_pipeline_data.sh [--pipeline projects|newbiz|both] [--days 7]
# Requires: PIPEDRIVE_API_TOKEN env var, curl, jq
# Outputs JSON files to stdout or a temp directory.

set -euo pipefail

API_TOKEN="${PIPEDRIVE_API_TOKEN:?Missing PIPEDRIVE_API_TOKEN}"
BASE="https://api.pipedrive.com/v1"
PIPELINE="both"
DAYS=7
OUTPUT_DIR=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --pipeline) PIPELINE="$2"; shift 2;;
    --days) DAYS="$2"; shift 2;;
    --output) OUTPUT_DIR="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 1;;
  esac
done

if [[ -z "$OUTPUT_DIR" ]]; then
  OUTPUT_DIR=$(mktemp -d)
fi
mkdir -p "$OUTPUT_DIR"

# Pipeline IDs
PROJECTS_ID=3
NEWBIZ_ID=9

fetch_all_deals() {
  local pipeline_id="$1"
  local status="$2"
  local start=0
  local limit=500
  local all="[]"
  local pipeline_param=""
  if [[ -n "$pipeline_id" ]]; then
    pipeline_param="&pipeline_id=${pipeline_id}"
  fi

  while true; do
    local resp
    resp=$(curl -sf "${BASE}/deals?api_token=${API_TOKEN}${pipeline_param}&status=${status}&limit=${limit}&start=${start}&sort=update_time%20DESC" 2>/dev/null)
    local data
    data=$(echo "$resp" | jq -r '.data // []')
    if [[ "$data" == "null" || "$data" == "[]" ]]; then
      break
    fi
    all=$(echo "$all" "$data" | jq -s '.[0] + .[1]')
    local more
    more=$(echo "$resp" | jq -r '.additional_data.pagination.more_items_in_collection // false')
    if [[ "$more" != "true" ]]; then
      break
    fi
    start=$((start + limit))
  done
  echo "$all"
}

fetch_activities() {
  local done_flag="$1"
  local start=0
  local limit=500
  local all="[]"

  while true; do
    local resp
    resp=$(curl -sf "${BASE}/activities?api_token=${API_TOKEN}&done=${done_flag}&limit=${limit}&start=${start}&sort=due_date%20DESC" 2>/dev/null)
    local data
    data=$(echo "$resp" | jq -r '.data // []')
    if [[ "$data" == "null" || "$data" == "[]" ]]; then
      break
    fi
    all=$(echo "$all" "$data" | jq -s '.[0] + .[1]')
    local more
    more=$(echo "$resp" | jq -r '.additional_data.pagination.more_items_in_collection // false')
    if [[ "$more" != "true" ]]; then
      break
    fi
    start=$((start + limit))
  done
  echo "$all"
}

fetch_users() {
  curl -sf "${BASE}/users?api_token=${API_TOKEN}" | jq '.data // []'
}

fetch_stages() {
  curl -sf "${BASE}/stages?api_token=${API_TOKEN}" | jq '.data // []'
}

fetch_deal_summary() {
  local pipeline_id="$1"
  local status="$2"
  curl -sf "${BASE}/deals/summary?api_token=${API_TOKEN}&status=${status}&pipeline_id=${pipeline_id}" | jq '.data // {}'
}

echo "Fetching stages..." >&2
fetch_stages > "$OUTPUT_DIR/stages.json"

echo "Fetching users..." >&2
fetch_users > "$OUTPUT_DIR/users.json"

# Fetch all open/won/lost deals (API pipeline_id filter is unreliable, so we post-filter)
echo "Fetching all open deals..." >&2
ALL_OPEN=$(fetch_all_deals "" "open")
echo "Fetching all won deals..." >&2
ALL_WON=$(fetch_all_deals "" "won")
echo "Fetching all lost deals..." >&2
ALL_LOST=$(fetch_all_deals "" "lost")

if [[ "$PIPELINE" == "projects" || "$PIPELINE" == "both" ]]; then
  echo "Filtering Projects pipeline..." >&2
  echo "$ALL_OPEN" | jq "[.[] | select(.pipeline_id == $PROJECTS_ID)]" > "$OUTPUT_DIR/projects_open.json"
  echo "$ALL_WON" | jq "[.[] | select(.pipeline_id == $PROJECTS_ID)]" > "$OUTPUT_DIR/projects_won.json"
  echo "$ALL_LOST" | jq "[.[] | select(.pipeline_id == $PROJECTS_ID)]" > "$OUTPUT_DIR/projects_lost.json"

  echo "Fetching Projects pipeline summary..." >&2
  fetch_deal_summary "$PROJECTS_ID" "open" > "$OUTPUT_DIR/projects_summary.json"
fi

if [[ "$PIPELINE" == "newbiz" || "$PIPELINE" == "both" ]]; then
  echo "Filtering New Business pipeline..." >&2
  echo "$ALL_OPEN" | jq "[.[] | select(.pipeline_id == $NEWBIZ_ID)]" > "$OUTPUT_DIR/newbiz_open.json"
  echo "$ALL_WON" | jq "[.[] | select(.pipeline_id == $NEWBIZ_ID)]" > "$OUTPUT_DIR/newbiz_won.json"
  echo "$ALL_LOST" | jq "[.[] | select(.pipeline_id == $NEWBIZ_ID)]" > "$OUTPUT_DIR/newbiz_lost.json"

  echo "Fetching New Business pipeline summary..." >&2
  fetch_deal_summary "$NEWBIZ_ID" "open" > "$OUTPUT_DIR/newbiz_summary.json"
fi

echo "Fetching activities (upcoming)..." >&2
fetch_activities "0" > "$OUTPUT_DIR/activities_upcoming.json"

echo "Fetching activities (completed)..." >&2
fetch_activities "1" > "$OUTPUT_DIR/activities_done.json"

# Fetch changelog (stage changes) for all open deals across both pipelines
fetch_deal_changelogs() {
  local deals_file="$1"
  local output_file="$2"
  local all="[]"
  local count=0
  local total
  total=$(jq length "$deals_file")

  echo "Fetching changelogs for $total deals..." >&2
  while IFS= read -r deal_id; do
    count=$((count + 1))
    if (( count % 10 == 0 )); then
      echo "  ... $count / $total" >&2
    fi
    local resp
    resp=$(curl -sf "${BASE}/deals/${deal_id}/changelog?api_token=${API_TOKEN}&limit=100" 2>/dev/null || echo '{"data":[]}')
    # Extract only stage_id changes, tag with deal_id
    local stage_changes
    stage_changes=$(echo "$resp" | jq --arg did "$deal_id" '[(.data // [])[] | select(.field_key == "stage_id") | . + {deal_id: ($did | tonumber)}]')
    if [[ "$stage_changes" != "[]" ]]; then
      all=$(echo "$all" "$stage_changes" | jq -s '.[0] + .[1]')
    fi
    # Rate limit: ~10 calls/sec to stay safe
    sleep 0.1
  done < <(jq -r '.[].id' "$deals_file")

  echo "$all" > "$output_file"
  echo "  Fetched $count changelogs, $(jq length "$output_file") stage changes found" >&2
}

# Build combined open deals file for changelog fetch
echo "Fetching deal changelogs for stage movement tracking..." >&2
COMBINED_OPEN="/tmp/pipeline-review-combined-open.json"
if [[ "$PIPELINE" == "both" ]]; then
  jq -s '.[0] + .[1]' "$OUTPUT_DIR/projects_open.json" "$OUTPUT_DIR/newbiz_open.json" > "$COMBINED_OPEN"
elif [[ "$PIPELINE" == "projects" ]]; then
  cp "$OUTPUT_DIR/projects_open.json" "$COMBINED_OPEN"
else
  cp "$OUTPUT_DIR/newbiz_open.json" "$COMBINED_OPEN"
fi

# Also include won+lost deals (they may have had stage changes before closing)
if [[ "$PIPELINE" == "both" || "$PIPELINE" == "projects" ]]; then
  if [[ -f "$OUTPUT_DIR/projects_won.json" && -f "$OUTPUT_DIR/projects_lost.json" ]]; then
    jq -s '.[0] + .[1] + .[2]' "$COMBINED_OPEN" "$OUTPUT_DIR/projects_won.json" "$OUTPUT_DIR/projects_lost.json" > "${COMBINED_OPEN}.tmp"
    mv "${COMBINED_OPEN}.tmp" "$COMBINED_OPEN"
  fi
fi
if [[ "$PIPELINE" == "both" || "$PIPELINE" == "newbiz" ]]; then
  if [[ -f "$OUTPUT_DIR/newbiz_won.json" && -f "$OUTPUT_DIR/newbiz_lost.json" ]]; then
    jq -s '.[0] + .[1] + .[2]' "$COMBINED_OPEN" "$OUTPUT_DIR/newbiz_won.json" "$OUTPUT_DIR/newbiz_lost.json" > "${COMBINED_OPEN}.tmp"
    mv "${COMBINED_OPEN}.tmp" "$COMBINED_OPEN"
  fi
fi

# Deduplicate by deal ID
jq '[group_by(.id)[] | .[0]]' "$COMBINED_OPEN" > "${COMBINED_OPEN}.tmp"
mv "${COMBINED_OPEN}.tmp" "$COMBINED_OPEN"

fetch_deal_changelogs "$COMBINED_OPEN" "$OUTPUT_DIR/deal_stage_changes.json"
rm -f "$COMBINED_OPEN"

echo "$OUTPUT_DIR"
