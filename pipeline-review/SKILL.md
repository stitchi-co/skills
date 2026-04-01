---
name: pipeline-review
description: "Prepare and deliver sales pipeline reviews from Pipedrive CRM data. Default: weekly pipeline review covering Projects (orders/revenue) and New Business (new logos/growth) pipelines. Supports ad-hoc queries like 'show me Samsara across both pipelines' or 'Kyle pipeline only.' Outputs to a Notion database (one row per review). Use when: user asks for pipeline review, sales review, pipeline health check, deal status, rep performance, pipeline prep, or any sales pipeline analysis. Also triggers on: weekly review, pipeline update, sales summary, deal review, how is the pipeline looking."
metadata:
  author: stitchi-co
  version: "1.0.0"
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

### 2. Notion Destination

Reviews are stored in a **Notion database** (one row per review, newest-first):

- **Database ID:** `6def2319-67ef-46a9-b03f-92e3532dd3b0`
- **Parent page:** `2539c12100fd8015aa76d7d12074ac70` (Pipeline Review)
- **API version:** Use `2022-06-28` (the `2025-09-03` version has issues with property creation)

Each database row has these properties:

**Results (what happened):**
| Property | Type | Description |
|----------|------|-------------|
| Projects Won | $ | Revenue closed this period (Projects pipeline) |
| Projects Lost | $ | Revenue lost this period (Projects pipeline) |
| NB Won | $ | New logos landed — annual value (New Business pipeline) |
| NB Lost | $ | New logos lost — annual value (New Business pipeline) |

**Forecast (what's coming):**
| Property | Type | Description |
|----------|------|-------------|
| Projects Weighted | $ | Weighted Projects pipeline (probability × value) |
| NB Weighted | $ | Weighted New Business pipeline |

**Meta:**
| Property | Type | Description |
|----------|------|-------------|
| Week | title | e.g. "Feb 27 – Mar 05, 2026" |
| Date | date | Review period (start + end) |
| Status | select | Draft / Published |

The full narrative review goes in the **page body** (blocks) of each row.

**Design rationale:** Projects and NB are split because they measure different things — Projects is transactional revenue being invoiced, NB is annual account value. Combining them would be misleading. Unweighted pipeline value is omitted (vanity metric — weighted is what matters for forecasting). Deal count and leading indicators (deals added/advanced) are omitted from the table — they're only actionable with deal-level context, which lives in the narrative.

Skip Notion output for ad-hoc (chat-only) reviews.

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
- Stage movement this period: Use `new_business_stage_movement` from the analysis output — these are real stage_id changes from Pipedrive's changelog API, showing from → to transitions with direction (forward/backward). Not an update_time proxy.
- Win rate: Trailing 30-day conversion.
- Concentration risk: Any org >15% of weighted pipeline.

**Projects Pipeline:**
- Stage movement this period: Use `projects_stage_movement` from the analysis output — same changelog-based tracking as NB. Shows which deals advanced (or regressed) stages this week with from → to transitions.
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
- Deals with no activities — flag for visibility, but don't assume it means the deal is unhealthy.
- **Data shows:** 85% of zero-activity deals end up won at Stitchi. Most wins are low-friction (reorders, inbound). High-activity deals (4-20 touches) actually have the *lowest* win rates (25-30%), signaling complexity rather than momentum. Activity logging is valuable for pipeline visibility, but low activity alone is not a red flag.
- Overdue activities list.

**Action Items:**
- Light and practical. 3-7 items max.
- Tailored to rep tenure and context.
- Manager-level strategic items (concentration risk, capacity).
- Always include: "Update overdue close dates" if any exist.

### 6. Output

**Weekly Review:**
1. Create a new row in the Notion database (see Step 2 for schema).
2. Set all properties (Week, Date range, pipeline values, won/lost, deal count, Status=Published).
3. Add the full narrative review as blocks in the page body.
4. Provide a concise summary in chat.

**Creating the Notion entry:**
```python
# Use Notion API version 2022-06-28
# 1. Create page with properties
page = POST /v1/pages {
    "parent": {"database_id": "6def2319-67ef-46a9-b03f-92e3532dd3b0"},
    "properties": {
        "Week": {"title": [{"text": {"content": "Feb 27 – Mar 05, 2026"}}]},
        "Date": {"date": {"start": "2026-02-27", "end": "2026-03-05"}},
        "Projects Won": {"number": 2306},
        "Projects Lost": {"number": 9750},
        "Projects Weighted": {"number": 191921},
        "NB Won": {"number": 0},
        "NB Lost": {"number": 20000},
        "NB Weighted": {"number": 428750},
        "Status": {"select": {"name": "Published"}}
    }
}

# 2. Add blocks to page body (batches of 100)
PATCH /v1/blocks/{page_id}/children {"children": [...blocks...]}
```



**Ad-hoc Review:**
- Quick summary in chat only. No Notion entry.

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
5. **Activity-to-close correlation** — at Stitchi, low-activity deals win at 85%; high-activity (4-20 touches) win at only 25-30%. Use for visibility, not as a health signal.
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

Notion database ID for reviews: `6def2319-67ef-46a9-b03f-92e3532dd3b0`
Notion parent page ID: `2539c12100fd8015aa76d7d12074ac70`

## Tone

Write for a sales manager sharing with their team:
- Direct, not corporate.
- Numbers first, narrative second.
- Celebrate wins. Flag risks without blame.
- Action items are suggestions, not mandates.
