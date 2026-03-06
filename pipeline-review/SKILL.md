---
name: pipeline-review
description: "Prepare and deliver sales pipeline reviews from Pipedrive CRM data. Default: weekly pipeline review covering Projects (orders/revenue) and New Business (new logos/growth) pipelines. Supports ad-hoc queries like 'show me Samsara across both pipelines' or 'Kyle pipeline only.' Outputs to a rolling Notion page. Use when: user asks for pipeline review, sales review, pipeline health check, deal status, rep performance, pipeline prep, or any sales pipeline analysis. Also triggers on: weekly review, pipeline update, sales summary, deal review, how is the pipeline looking."
---

# Pipeline Review

Prepare sales pipeline reviews analyzing two Pipedrive pipelines that tell different stories:

- **Projects Pipeline** (id=3): Actual orders/projects. Lumpy, transactional revenue.
- **New Business Pipeline** (id=9): Annual expected value of new logos. Growth indicator.

For pipeline/stage definitions and account tiers, read `references/pipelines.md`.
For Notion output structure, read `references/review-template.md`.

## Workflow

### 1. Confirm Review Type

If the user doesn't specify, ask:
> "Running a **weekly pipeline review** — covering both Projects and New Business pipelines. Want to proceed, or did you have something specific in mind?"

For ad-hoc requests (specific org, rep, or pipeline), skip confirmation and proceed directly.

### 2. Confirm Notion Destination

Ask where to store the output:
> "Where should I put this in Notion? Give me a page URL or database, and I'll update the rolling review page."

If user has a previously-used page, offer to reuse it. Skip for ad-hoc (chat-only) reviews.

### 3. Fetch Data

```bash
export PIPEDRIVE_API_TOKEN=$(cat ~/.config/pipedrive/api_key)
DATA_DIR=$(bash scripts/fetch_pipeline_data.sh --pipeline both --output /tmp/pipeline-review-data)
```

For ad-hoc with a specific pipeline:
```bash
DATA_DIR=$(bash scripts/fetch_pipeline_data.sh --pipeline projects --output /tmp/pipeline-review-data)
```

### 4. Analyze

```bash
python3 scripts/analyze_pipeline.py "$DATA_DIR" --type weekly --days 7 --trend-days 30
```

For ad-hoc queries, use filters:
```bash
python3 scripts/analyze_pipeline.py "$DATA_DIR" --type adhoc --filter-org "Samsara"
python3 scripts/analyze_pipeline.py "$DATA_DIR" --type adhoc --filter-rep "Kyle"
python3 scripts/analyze_pipeline.py "$DATA_DIR" --type adhoc --filter-pipeline newbiz
```

### 5. Compose the Review

Read `references/review-template.md` for structure. Key principles:

**Executive Summary** — Lead with what changed and what matters. Not a data dump.

**New Business Pipeline:**
- Bucket distribution: Are we pursuing the right-sized accounts?
- Stage velocity: Average days in each stage. Flag outliers.
- Stage movement this period: Which deals advanced? (Signal of progress.)
- Win rate: Trailing 30-day conversion.
- Concentration risk: Any org >15% of weighted pipeline.

**Projects Pipeline:**
- Stage breakdown with top deals by value.
- Overdue close dates: List with days overdue. These need date updates or closure.
- Zero-value deals: Flag for pricing (especially events/scheduled items).
- In Production + Approved = near-term revenue. Highlight.
- Concentration risk.

**Period Comparison:**
- Week-over-week: deals added, won, lost, value movement.
- Monthly trend (30-day rolling) for New Business since those deals move slower.

**Rep Breakdown:**
- Keep supportive, not disciplinary.
- Pull rep data from Pipedrive users (tenure via `created` field) to calibrate tone internally.
- **Never include start dates or tenure in the output** — this is internal context only.
- New reps: coaching-oriented suggestions ("consider reaching out to...").
- Experienced reps: peer-level flags ("X deal may need attention").
- Distribution of pipeline across reps — flag if one rep carries disproportionate load.

**Activity Insights:**
- Deals with no activities = biggest red flag for stale pipeline.
- Note: deals with more activities tend to have higher close rates. Surface this pattern.
- Overdue activities list.

**Action Items:**
- Light and practical. 3-7 items max.
- Tailored to rep tenure and context.
- Manager-level strategic items (concentration risk, capacity).
- Always include: "Update overdue close dates" if any exist.

### 6. Output

**Weekly Review:**
- Update the rolling Notion page using the Notion skill.
- Also provide a concise summary in chat.

**Ad-hoc Review:**
- Quick summary in chat only. No Notion update.

## Review Cadence Defaults

| Type | Comparison Period | Trend Period |
|------|------------------|--------------|
| Weekly | 7 days (Fri–Thu) | 30 days rolling |
| Monthly | 30 days | 90 days rolling |
| Quarterly | 90 days | 365 days rolling |

### Week Boundaries

Reviews use **fixed week boundaries**: Friday 00:00 ET → Thursday 23:59 ET.
When run on Friday, it covers the just-completed week. The analysis script computes this automatically.

- **Review period:** current Fri–Thu week
- **Previous period:** the Fri–Thu week before that (for week-over-week comparison)
- **Trend period:** rolling 30 days from now (for directional context, not precise reporting)

This ensures clean cutoffs, reproducible results, and no partial-day weirdness.

## What "Stale" Means

A deal is stale if:
1. No activities associated with it (past or upcoming), OR
2. No stage movement in an extended period (Pipedrive's rotting feature tracks this), OR
3. No update in 14+ days with no scheduled next activity

Flag all three signals. The analysis script catches #1 and #3; mention #2 if Pipedrive's rot indicator is visible in deal data.

## New Business Health Metrics

These are the key health indicators for the New Business pipeline:
1. **Pipeline coverage ratio** — weighted pipeline vs. target (ask user for target if unknown)
2. **Stage velocity** — avg days in each stage; flag deals 2x+ above average
3. **Bucket distribution** — healthy = mix of tiers; unhealthy = all XS/S with no L/XL
4. **Win rate** — trailing 30-day (won / (won + lost))
5. **Activity-to-close correlation** — note that higher-activity deals tend to close more
6. **Stage advancement rate** — what % of deals moved forward this period?

## Scheduling & Catch-Up

The weekly review is triggered two ways for resilience:

1. **Cron job** — `0 8 * * 5` (Friday 8am ET, exact, isolated session). Announces summary to webchat.
2. **Heartbeat guard** — HEARTBEAT.md checks on Fri/Sat if the review was missed and catches up.

Both use a shared state file (`~/.openclaw/pipeline-review-state.json`) to avoid duplicate runs:

```bash
# Check if review needs to run (exit 0 = yes, exit 1 = already done)
bash scripts/should_run_review.sh check

# Mark this week's review as complete
bash scripts/should_run_review.sh mark

# View last run info
bash scripts/should_run_review.sh status
```

**After every successful weekly review, always run `should_run_review.sh mark`.**

Notion page ID for recurring reviews: `2539c12100fd8015aa76d7d12074ac70`

## Tone

Write for a sales manager sharing with their team:
- Direct, not corporate.
- Numbers first, narrative second.
- Celebrate wins. Flag risks without blame.
- Action items are suggestions, not mandates.
