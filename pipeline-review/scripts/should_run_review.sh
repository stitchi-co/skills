#!/usr/bin/env bash
# Check if the weekly pipeline review should run.
# Exits 0 (should run) or 1 (already done this week).
# Also used to record that a review was completed.
#
# Usage:
#   should_run_review.sh check    # exit 0 = needs to run, exit 1 = already done
#   should_run_review.sh mark     # record that this week's review is done
#   should_run_review.sh status   # print last run info

set -euo pipefail

STATE_FILE="${PIPELINE_REVIEW_STATE:-$HOME/.openclaw/pipeline-review-state.json}"
mkdir -p "$(dirname "$STATE_FILE")"

ACTION="${1:-check}"

# Get the current review week's Friday date (start of Fri-Thu boundary)
# If today is Fri-Thu, the review week started on the most recent Friday
get_week_friday() {
  local dow
  dow=$(date +%u)  # 1=Mon, 5=Fri, 7=Sun
  local days_since_fri=$(( (dow - 5 + 7) % 7 ))
  if [[ "$OSTYPE" == "darwin"* ]]; then
    date -v-"${days_since_fri}"d +%Y-%m-%d
  else
    date -d "-${days_since_fri} days" +%Y-%m-%d
  fi
}

WEEK_FRIDAY=$(get_week_friday)

case "$ACTION" in
  check)
    if [[ ! -f "$STATE_FILE" ]]; then
      exit 0  # No state file = never run
    fi
    LAST_WEEK=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('last_review_week', ''))" 2>/dev/null || echo "")
    if [[ "$LAST_WEEK" == "$WEEK_FRIDAY" ]]; then
      exit 1  # Already done this week
    fi
    exit 0  # Needs to run
    ;;
  mark)
    NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    cat > "$STATE_FILE" <<EOF
{
  "last_review_week": "$WEEK_FRIDAY",
  "last_run_at": "$NOW",
  "notion_page_id": "2539c12100fd8015aa76d7d12074ac70"
}
EOF
    echo "Marked review complete for week of $WEEK_FRIDAY"
    ;;
  status)
    if [[ -f "$STATE_FILE" ]]; then
      cat "$STATE_FILE"
    else
      echo "No review state found"
    fi
    ;;
  *)
    echo "Usage: $0 {check|mark|status}" >&2
    exit 2
    ;;
esac
