# Data Sources Reference

## Notion — Investor Updates Database

**Database ID:** `b037f250481c476e98e46dc9198138b5`
**Status:** ✅ Connected to Clawdbot integration

**Historical updates available:**
| Title | Date | Status |
|---|---|---|
| 2026 Q1 | 2026-01-01 | Draft (outline only) |
| 2025 - Q4 | 2025-10-01 | Complete |
| 2025 - Q3 | 2025-07-01 | Complete |
| 2025 - Q2 | 2025-04-01 | Partial (some bullets empty) |
| 2025 - Q1 | 2025-01-01 | Complete |
| 2024 - Q4 | 2024-10-01 | Complete |
| 2024 - Q3, Q2, Feb 2024, Jan 2024 | Earlier | Available |

**Database properties:** Name (title), Date, Period, Type

**Fetching updates:**
```bash
python3 scripts/gather_signals.py --notion-history    # List recent update pages
python3 scripts/gather_signals.py --page-id <id>      # Read full content of one update
```

**Draft storage:** Create new pages in this database.
- Title: `{YYYY} Q{N}` (matches existing convention)
- Set Date property to quarter start date

---

## Pipedrive — Pipeline & Revenue Signals

**Auth:** `~/.config/pipedrive/api_key`
**CLI:** `python3 scripts/gather_signals.py --pipedrive`

**Key pipelines:**
| Pipeline | ID | Signal |
|---|---|---|
| Projects | 3 | Won deals → customer wins for Highlights. Active pipeline → forward revenue signal. |
| New Business | 9 | New logo acquisition → growth narrative. |

**What the script returns:**
- Won deals (period): org name, value, date — use for Highlights section
- Active pipeline by stage + total value — use for narrative context
- New Business funnel status — use for GTM narrative

**Note:** Pipedrive values are project-based revenue, not MRR. Revenue figures for tl;dr come from Everest (accounting), not Pipedrive.

**Use Pipedrive for:** Customer names in Highlights, deal narratives in Challenges (e.g., lost deals), pipeline health for Up Next.

---

## Front — Customer & Investor Conversations

**Auth:** API token via OpenClaw plugin env `FRONT_API_TOKEN` or `~/.config/front/api_token`
**CLI:** `python3 scripts/gather_signals.py --front`

**Signal extraction:**
| Inbox | ID | Look for |
|---|---|---|
| Clients | inb_jsv8n | New customer threads, reorders, escalations |
| Projects | inb_jvnfr | Order velocity, operational issues |

**What to look for:**
- New customer onboarding conversations → potential Highlights
- Customer complaints or escalations → potential Challenges
- Reorder conversations → retention signal for narrative

**Front is noisy.** Only surface high-signal conversations: new logos, large deal activity, notable escalations, customer praise.

---

## Stitchi Case Studies

**URL:** https://www.stitchi.com/case-studies
**Access:** `web_fetch` the page

Case study highlights from site:
- $70k+ in single campaign savings (Morning Brew)
- 5x increase in sales-qualified demos (Porter)
- 6 weeks implementation (San Morello)
- 30% reduction in fulfillment time (RevolutionParts)

**How to use:** Extract one-line headline metrics to support claims in Highlights. Don't recite the full case study.

---

## Manual Data (from Everest)

The following are NOT available from automated sources. Prompt Everest for these when drafting:
- **Revenue** (exact, from accounting/QuickBooks)
- **Gross Margin** (if including)
- **Account Signups** (from Stitchi platform analytics)
- **Website Traffic** and **Organic Clicks** (from Google Analytics / Search Console)
- **Net New Logos** (manual count or from Pipedrive with Everest's verification)
- **Up Next priorities** (from Everest's planning)
- **Specific asks** (from Everest's current needs)
- **Narrative framing** (what the quarter felt like, headline story)

---

## Slack — Internal Signals

**Status:** ✅ Connected via OpenClaw (Socket Mode)
**Auth:** Bot token from `~/.openclaw/.env` (`SLACK_EVEREST_BOT_TOKEN`)
**CLI:** `python3 scripts/gather_signals.py --slack`

**Monitored channels:**

| Channel | ID | Signal type |
|---|---|---|
| `#team-revenue` | C032HCCEB88 | Deal wins, pipeline updates, sales activity |
| `#team-delivery` | C092NHPRSSZ | Fulfillment, ops milestones, shipping volume |
| `#team-product` | C065F2C1TGF | Shipped features, product milestones, tech decisions |
| `#general` | C031M06D5HU | Company-wide wins, announcements, team updates |

**⚠️ Setup required:** EverestBot must be invited to each channel:
```
/invite @EverestBot
```

**What the script returns:**
- Messages sorted by reaction count (most engaged = most signal)
- Top 30 messages per channel within the lookback period
- Human messages only (bot/system messages filtered out)

**Signal extraction guidance:**
- **High-reaction messages** → the team considered this important (wins, milestones)
- **`#team-revenue`** → deal closings, new logos, pipeline wins → maps to Highlights
- **`#team-delivery`** → fulfillment volume, ops improvements → maps to Highlights or Challenges
- **`#team-product`** → shipped features, integrations → maps to Highlights and Up Next
- **`#general`** → company announcements, hires, culture moments → maps to narrative/Highlights

**Adding more channels:** Edit `SLACK_CHANNELS` dict in `scripts/gather_signals.py`. Get channel IDs from the Slack API or channel details in Slack UI.

---

## Signal Priority

| Source | Trust Level | Use for |
|---|---|---|
| Everest (manual) | Highest | Revenue, KPIs, narrative, asks |
| Slack | High (internal team) | Wins, milestones, deal activity, team updates, culture moments |
| Pipedrive | High (structured) | Customer names, deal stories, pipeline context |
| Notion history | High | Tone/structure calibration |
| Front | Medium (qualitative) | Customer sentiment, escalation anecdotes |
| Case studies | High (published) | Proof points |

**If data is missing or unverified → omit. Never estimate without flagging.**
