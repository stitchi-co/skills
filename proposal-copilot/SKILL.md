---
name: proposal-copilot
description: |
  Create, review, and improve Stitchi program proposals (company stores, recurring swag programs,
  event support). Use when: drafting a new proposal, reviewing a proposal against an RFP, analyzing
  an RFP for gaps, improving proposal format/content, generating stakeholder personas, writing
  executive summaries, or any task involving Stitchi customer proposals. Triggers on: "write a
  proposal", "review this RFP", "proposal for {client}", "what's missing from our proposal",
  "improve the proposal", "stakeholder personas for", "executive summary for". NOT for: one-off
  project quotes, pricing calculations, or order-level quoting.
---

# Proposal Copilot

Stitchi's proposal sidekick for program-based proposals: company stores, recurring swag/kit programs, and event support.

## Source of Truth

**stitchi.com is canonical** for case studies, positioning, capabilities, and stats. Fetch live:
- Case studies → `https://www.stitchi.com/case-studies` (and linked pages)
- Company positioning → `https://www.stitchi.com`

**Fallback:** If stitchi.com pages are client-rendered or fail to return full content, use the headline stats from the case-studies page (Morning Brew: $70K+ savings, Porter: 5x demos, San Morello: 6 weeks implementation, RevolutionParts: 30% fulfillment reduction) and note that the user should verify these are current.

**Reference files** (internal details not on the website):
- `references/proposal-template.md` — current 18-section structure, custom vs boilerplate markers, PandaDoc variables
- `references/stakeholder-personas.md` — 12 persona archetypes, tailoring guide
- `references/pricing-and-operations.md` — hosting tiers, build packages, fulfillment rates, SLAs
- `references/rfp-review-checklist.md` — 10 RFP requirement categories with gap analysis guidance
- `references/competitive-positioning.md` — competitor landscape, objection handling, win themes
- `references/discovery-framework.md` — structured discovery inputs, questions, context sources
- `references/vertical-playbooks.md` — 7 industry playbooks with personas, language, case study mapping

The original PandaDoc proposal PDF is in `assets/company-store-proposal-template.pdf`.

## Modes

### 1. Draft — "Help me write a proposal"

**Step 1: Gather discovery inputs.**
Read `references/discovery-framework.md`. Collect the 6 required inputs before writing. Check Pipedrive, Front, and Granola for existing intel. If inputs are thin, surface the high-value discovery questions to the user — don't draft blind.

**Step 2: Select vertical playbook.**
Read `references/vertical-playbooks.md`. Identify the client's primary vertical (and secondary if applicable). Pull in industry-specific personas, language cues, merch emphasis, and objection pre-emption.

**Step 3: Generate custom sections.**

Read `references/proposal-template.md` for structure context, then generate:

**Executive Summary** — the make-or-break section. Structure:

> Stitchi is pleased to present our proposal to {Client} for a comprehensive [program type]. As a Michigan-based partner with deep expertise in branded merchandise programs, Stitchi specializes in building seamless, technology-driven solutions that simplify the way organizations [do what the client specifically needs].
>
> We understand {Client}'s priorities: [2–3 specific client priorities drawn from discovery]. Stitchi's approach combines [mapped capabilities] with [service differentiator].
>
> Key highlights of our program include:
> - **[Client need as a header]** — [Stitchi capability that solves it, specific to their world]
> - **[Client need]** — [Capability]
> - **[Client need]** — [Capability]
> - **[Client need]** — [Capability]
> - **[Client need]** — [Capability]
>
> By choosing Stitchi, {Client} will gain [partnership framing, not vendor framing]. Our proven experience with [similar organizations / industry] ensures we are positioned to deliver both immediate impact and long-term value.

Rules: Open with the client's world, not Stitchi's. Every bullet maps a client need to a Stitchi capability. Close on partnership. Never use "leverage", "synergy", "holistic", or "cutting-edge."

**Stakeholder Personas & Merch Matrix** — read `references/stakeholder-personas.md`:
- Pick 4–6 archetypes matching client's actual org
- Rename for their industry (construction: "Crew Chief Carlos", healthcare: "Nurse Nina")
- Customize events to their actual calendar and business rhythm
- Customize merch to their brand, industry norms, and budget
- Add "Quick Takeaways" grouped by theme

**Case Study Selection** — fetch from stitchi.com, pick 3–4 by relevance:
- Match by industry, program type, company size, or challenge
- Read `references/vertical-playbooks.md` for recommended case study pairings
- If no strong industry match, pick studies demonstrating the most relevant capability

**Competitive Pre-emption** — read `references/competitive-positioning.md`:
- Identify likely competitor category (large distributor, platform vendor, or local shop)
- Weave counter-positioning into exec summary and "Why Stitchi" language
- Don't name competitors; position against the category

For boilerplate sections, output a checklist of which template sections to include (they live in PandaDoc). Flag any boilerplate sections that should be reordered or omitted for this specific client.

**Step 4: Recommend section ordering.**
Default ordering follows `references/proposal-template.md`, but adjust based on the client's decision criteria. If price sensitivity is the primary concern, move pricing earlier. If technology is the driver, lead with store features. Always keep exec summary and personas first.

### 2. Review — "Here's an RFP. What are we missing?"

Read `references/rfp-review-checklist.md` and `references/proposal-template.md`.

**Step 1: Parse the RFP.** Extract every requirement, question, and evaluation criterion. Identify weighted scoring criteria if provided.

**Step 2: Gap analysis table.**

| # | RFP Requirement | Weight | Covered? | Proposal Section | Gap / Action |
|---|---|---|---|---|---|
| 1 | Company overview | 10% | ✅ | Who We Are | — |
| 2 | ADA compliance | 5% | ⚠️ | Not addressed | Confirm WCAG status, add section |
| 3 | References (3+) | 10% | ❌ | Missing | Collect 3 references, add section |

Mark each: ✅ fully covered, ⚠️ partially covered, ❌ missing. Include RFP weight/priority when available.

**Step 3: Scoring strategy.** For weighted RFPs, rank gaps by weight. Focus effort on high-weight uncovered items — a 20% technical section matters more than a 5% sustainability section.

**Step 4: Response structure.** When the RFP has a required outline, produce a mapping from RFP sections to Stitchi content sources. When responding in Stitchi's own format, justify why the structure serves the evaluator.

**Step 5: No-bid check.** Flag if the RFP contains any of these:
- Requires capabilities Stitchi doesn't have (e.g., in-house manufacturing, specific certifications)
- Budget clearly below viable minimums
- Geography Stitchi can't serve
- Timeline impossible to meet
- Incumbent is specified or decision appears pre-made

If no-bid criteria exist, surface them clearly. Don't waste effort on unwinnable deals.

### 3. Improve — "How can we make our proposal better?"

Read `references/proposal-template.md` and `references/competitive-positioning.md`.

Evaluate against these specific anti-patterns:

| Anti-Pattern | How to Detect | Fix |
|---|---|---|
| Vendor catalog, not partnership pitch | Generic capability lists without client framing | Reframe every feature as a client benefit |
| Buried value prop | Exec summary doesn't land within 30 seconds of reading | Lead with client pain, not Stitchi bio |
| Proof-claim gap | Claims without adjacent proof points | Move case studies / stats next to related claims |
| Price shock | Pricing appears without context or value framing | Add ROI framing or "what this replaces" context |
| Section bloat | 18 sections is a lot — some may not earn their place | For smaller deals, recommend which sections to cut |
| Stale differentiators | "Passion for quality" is generic | Sharpen to specific, provable claims |
| Missing competitive awareness | No reason to choose Stitchi over alternatives | Add subtle counter-positioning per `references/competitive-positioning.md` |
| Weak close | Signature page without urgency or next steps | Add "What happens next" section before signature |

For each finding: describe the issue, show the current state, and draft the improved version. Don't just recommend — write the copy.

When improvements are approved, update the relevant reference files so they compound.

## Proposal Pacing Guide

| Client Size / Deal | Recommended Depth |
|---|---|
| Enterprise, $100K+ annual, formal RFP | Full 18 sections, max depth on custom sections |
| Mid-market, $25K–100K, semi-formal | Full structure, lighter on warehousing/fulfillment detail |
| Growth-stage, under $25K, informal | Streamlined: Exec Summary, Personas, Why Stitchi, Pricing, Case Studies, Onboarding, Signature. Skip feature grids and warehousing detail. |

## Writing Rules

- Consultative, not salesy. Confident, not arrogant.
- "We're your merch team, not a swag vendor" — partnership language throughout.
- Detroit pride is a real differentiator. Use it naturally.
- Open every custom section with the client's context, not Stitchi's.
- Banned words: "leverage", "synergy", "holistic", "cutting-edge", "utilize", "facilitate", "empower".
- Alliterative persona names, industry-appropriate ("Crew Chief Carlos" not "Employee Emma").
- Stats and proof points adjacent to claims, not isolated in their own section.

## Evolving This Skill

This skill improves with use. After each proposal:
1. Update `references/proposal-template.md` if structural changes were made
2. Add new persona archetypes to `references/stakeholder-personas.md`
3. Add new vertical playbooks to `references/vertical-playbooks.md`
4. Log new objections or competitor intel in `references/competitive-positioning.md`
5. Add new RFP patterns to `references/rfp-review-checklist.md`
6. Update `references/pricing-and-operations.md` when rates or SLAs change

Never duplicate stitchi.com content into reference files.
