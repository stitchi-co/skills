# Pipeline Review Output Template

Use this structure for the Notion page. The page should be a **rolling update** — replace content each review, not append.

## Notion Page Structure

```
# Pipeline Review — Week of {date}
Generated: {timestamp}

## Executive Summary
- 2-3 sentence overview of pipeline health
- Key number changes vs. last period
- Top risk or opportunity to highlight

## New Business Pipeline
### Overview
- Total open deals: X ($XXK total, $XXK weighted)
- Win rate (trailing {trend_days} days): X%
- Stage movement this week: list deals that advanced

### Bucket Distribution
- Table or list: tier → count, total value
- Flag if over-indexed on low tiers or light on L/XL

### Stage Breakdown
For each stage (Discovery → Proposal → Negotiation):
- Count, value
- Notable deals (largest, most recently moved)
- Average age in stage, flag outliers

### Health Signals
- Deals with no activities
- Stale deals (no stage movement)
- Concentration risk (any org >15% of weighted pipeline)

### Period Comparison (Fri–Thu boundaries)
- This week won/lost vs. previous week won/lost (count + value)
- Trailing {trend_days} day trend (rolling, for directional context)
- Movement: which deals advanced stages this week?

## Projects Pipeline
### Overview
- Total open deals: X ($XXK total, $XXK weighted)
- In Production value: $XXK
- Approved/ready for production: $XXK

### Stage Breakdown
For each stage (Scheduled → Request → Quoted → Approved → In Production):
- Count, value
- Top deals by value

### Attention Items
- Overdue close dates (list with days overdue)
- Stale deals
- Zero-value deals that need pricing
- Concentration risk

### Period Comparison (Fri–Thu boundaries)
- This week won: count, total value, notable deals
- This week lost: count, total value
- vs. previous week: won/lost count + value delta
- Trailing {trend_days} day trend

## Rep Breakdown
For each active rep — keep supportive, not disciplinary:
- Deal count, total value, weighted value
- Notable wins this period
- Deals needing attention (overdue, stale)
- Upcoming activities count
- Do NOT include start dates or tenure in the output — use tenure internally to calibrate tone only

## Activity Insights
- Deals with zero activities (flag for attention)
- Overdue activities
- Activity volume trends

## Action Items
Light, practical. Consider rep tenure and context:
- New reps: more coaching-oriented ("consider reaching out to...")
- Experienced reps: peer-level ("flag: X deal may need attention")
- Manager: strategic ("pipeline concentration in Samsara warrants backup plan")
```

## Formatting Notes
- Use Notion-compatible markdown (headers, bullet lists, bold, tables)
- Keep tables simple — Notion handles basic markdown tables
- Use emoji sparingly for visual anchors (🔴 risk, 🟡 watch, 🟢 healthy)
- Bold key numbers and org names for scannability
