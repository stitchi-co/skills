---
name: investor-updates
description: Generate quarterly investor updates for Stitchi. Synthesizes data from Slack (internal team signals), Pipedrive (pipeline/customer wins), Front (customer conversations), Notion (historical updates), and Stitchi case studies into a polished update in Everest's voice for ~120 friends, family, and supporters. Use when asked to draft an investor update, write a quarterly letter, prepare a quarterly update, or review/improve an existing investor update draft.
---

# Investor Updates

Quarterly updates for Stitchi's ~120 friends, family, and investors. Bootstrapped company — these are relationship-building letters, not board reports.

## References

- **Voice, structure & KPIs:** `references/voice-and-structure.md` — read before every draft
- **Data sources & setup:** `references/data-sources.md` — read for data gathering
- **Data gathering script:** `scripts/gather_signals.py`

## Workflow

### 1. Load context
Read `references/voice-and-structure.md` for tone, structure, emoji headers, and KPI definitions.

### 2. Review historical updates
Fetch the last 2 completed updates from Notion to calibrate tone:
```bash
python3 scripts/gather_signals.py --notion-history
python3 scripts/gather_signals.py --page-id <most_recent_complete_id>
```

### 3. Collect manual data from Everest
Prompt for numbers that can't be pulled automatically:
- Revenue (exact, from accounting)
- Net New Logos
- Account Signups
- Organic Clicks (and Website Traffic if including)
- Gross Margin (only if notable)
- The "one-line summary" — what did this quarter feel like?
- Top 3–4 priorities for "Up Next"
- Current asks (intros needed, hiring, feedback)
- Any specific wins, hires, deals, or challenges not in Pipedrive/Front
- Any context not captured in automated sources (e.g., conference appearances, partner updates)

### 4. Gather automated signals
```bash
python3 scripts/gather_signals.py --all --lookback-days 90
```
This pulls from Pipedrive, Front, Slack, and Notion in one call.

Slack channels pulled: `#team-revenue`, `#team-delivery`, `#team-product`, `#general`. Messages are sorted by reaction count — high-reaction messages are the strongest signals. See `references/data-sources.md` for what to extract from each channel.

Also check:
- Stitchi case studies: `web_fetch https://www.stitchi.com/case-studies`
- Pipedrive for customer names, deal stories, lost deal context

### 5. Draft the update

Follow exact structure from `references/voice-and-structure.md`:

1. **Email envelope** — Subject line + confidentiality notice + salutation
2. **Opening narrative** — 1–3 paragraphs, personal, sets the quarter's story
3. **⌛ tl;dr** — Revenue, Net New Logos, Account Signups, Organic Clicks (+ others if material)
4. **⭐ Wins & Highlights** — 4–8 items grouped by theme, short paragraphs
5. **🎓 Challenges & Learnings** — 2–4 items, bold label + paragraph, specific and honest
6. **🚀 Up Next** — 3–6 concrete priorities
7. **❓ Asks** — 3–4 specific, actionable
8. **Sign-off** — Rotate closing, always sign `Everest Guerra`

**Target length:** 700–1200 words.

### 6. Save draft to Notion

Create a new page in the investor updates database (`b037f250481c476e98e46dc9198138b5`):
- Title: `{YYYY} Q{N}` (e.g., "2026 Q2")
- Date property: quarter start date
- Append full update as paragraph blocks

### 7. Present for review

Share the Notion URL with Everest and flag:
- Any sections where data was missing or estimated
- Sections where Everest's input is still needed
- Any KPI deltas that look surprising and should be verified

## Common Scenarios

**"Draft the Q2 update"**
Run full workflow. Ask Everest for: (1) Revenue + KPIs, (2) The headline story, (3) Any wins/challenges not in CRM, (4) Asks.

**"Review my draft"**
Read `references/voice-and-structure.md`. Audit against voice guidelines, structure, KPIs. Flag anti-patterns (hype, vague, missing specifics). Return revised version with change notes.

**"What metrics should we include?"**
Reference the KPI table in `references/voice-and-structure.md` — it's derived from analysis of all 5 historical updates.
