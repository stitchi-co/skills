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

Sidekick for program-based proposals: company stores, recurring swag/kit programs, and event support.

## Business Context

This skill handles **methodology** — how to build great proposals. Company-specific knowledge lives elsewhere:

- **Company website** — canonical for case studies, positioning, capabilities, stats. Fetch live.
- **Agent memory** — pricing, SLAs, competitive positioning, operational details. Search memory for relevant context before drafting.
- **Proposal template PDF** — `assets/company-store-proposal-template.pdf` for structural reference.

## Reference Files (methodology)

- `references/proposal-template.md` — current section structure, custom vs boilerplate markers
- `references/stakeholder-personas.md` — 12 persona archetypes, tailoring guide
- `references/rfp-review-checklist.md` — 10 RFP requirement categories, no-bid criteria, gap analysis framework
- `references/discovery-framework.md` — structured discovery inputs, questions, context sources
- `references/vertical-playbooks.md` — 7 industry playbooks with personas, language, merch emphasis

## Modes

### 1. Draft — "Help me write a proposal"

**Step 1: Gather discovery inputs.**
Read `references/discovery-framework.md`. Collect the 6 required inputs before writing. Check CRM, email, and meeting notes for existing intel. If inputs are thin, surface the high-value discovery questions to the user — don't draft blind.

**Step 2: Load business context.**
Search agent memory for: pricing, capabilities, competitive positioning, case studies, and any existing client relationship history. Fetch the company website for current stats and case studies.

**Step 3: Select vertical playbook.**
Read `references/vertical-playbooks.md`. Identify the client's primary vertical (and secondary if applicable). Pull in industry-specific personas, language cues, and merch emphasis.

**Step 4: Generate custom sections.**
Read `references/proposal-template.md` for structure, then generate:

**Executive Summary** — the make-or-break section. Structure:

> {Company} is pleased to present our proposal to {Client} for a comprehensive [program type]. As a [positioning statement], {Company} specializes in [core capability mapped to client need].
>
> We understand {Client}'s priorities: [2–3 specific client priorities drawn from discovery]. {Company}'s approach combines [mapped capabilities] with [service differentiator].
>
> Key highlights of our program include:
> - **[Client need as header]** — [Capability that solves it, specific to their world]
> - **[Client need]** — [Capability]
> - **[Client need]** — [Capability]
> - **[Client need]** — [Capability]
> - **[Client need]** — [Capability]
>
> By choosing {Company}, {Client} will gain [partnership framing, not vendor framing]. Our proven experience with [similar organizations / industry] ensures we are positioned to deliver both immediate impact and long-term value.

Rules: Open with the client's world, not yours. Every bullet maps a client need to a capability. Close on partnership. Avoid buzzwords ("leverage", "synergy", "holistic", "cutting-edge", "utilize", "facilitate", "empower").

**Stakeholder Personas & Merch Matrix** — read `references/stakeholder-personas.md`:
- Pick 4–6 archetypes matching client's actual org
- Rename for their industry (construction: "Crew Chief Carlos", healthcare: "Nurse Nina")
- Customize events to their actual calendar and business rhythm
- Customize merch to their brand, industry norms, and budget
- Add "Quick Takeaways" grouped by theme

**Case Study Selection** — fetch from company website, pick 3–4 by relevance:
- Match by industry, program type, company size, or challenge
- Consult vertical playbooks for recommended pairings
- If no strong industry match, pick studies demonstrating the most relevant capability

**Competitive Pre-emption** — search memory for competitive positioning:
- Identify likely competitor category the client might also be evaluating
- Weave counter-positioning into exec summary and differentiators language
- Don't name competitors; position against the category

For boilerplate sections, output a checklist of which template sections to include. Flag any that should be reordered or omitted for this specific client.

**Step 5: Recommend section ordering.**
Default follows `references/proposal-template.md`, but adjust for the client's decision criteria. Price-sensitive → move pricing earlier. Tech-driven → lead with platform features. Always keep exec summary and personas first.

### 2. Review — "Here's an RFP. What are we missing?"

Read `references/rfp-review-checklist.md` and `references/proposal-template.md`. Search memory for company capabilities to assess coverage.

**Step 1: Parse the RFP.** Extract every requirement, question, and evaluation criterion. Identify weighted scoring criteria if provided.

**Step 2: No-bid check.** Before detailed analysis, scan for deal-breakers (see checklist). If any exist, surface them and recommend no-bid.

**Step 3: Gap analysis table.**

| # | RFP Requirement | Weight | Covered? | Proposal Section | Gap / Action |
|---|---|---|---|---|---|
| 1 | Company overview | 10% | ✅ | Who We Are | — |
| 2 | ADA compliance | 5% | ⚠️ | Not addressed | Confirm status, add section |
| 3 | References (3+) | 10% | ❌ | Missing | Collect references, add section |

Mark each: ✅ fully covered, ⚠️ partially, ❌ missing. Include weight when available.

**Step 4: Scoring strategy.** Rank gaps by weight. High-weight uncovered items get attention first.

**Step 5: Response structure.** When the RFP has a required outline, map your content to their sections. When using your own format, justify why it serves the evaluator.

### 3. Improve — "How can we make our proposal better?"

Read `references/proposal-template.md`. Search memory for competitive positioning context.

Evaluate against these anti-patterns:

| Anti-Pattern | How to Detect | Fix |
|---|---|---|
| Vendor catalog, not partnership pitch | Generic capability lists without client framing | Reframe every feature as a client benefit |
| Buried value prop | Exec summary doesn't land in 30 seconds | Lead with client pain, not company bio |
| Proof-claim gap | Claims without adjacent proof points | Move case studies/stats next to related claims |
| Price shock | Pricing appears without context | Add ROI framing or "what this replaces" context |
| Section bloat | Sections that don't earn their place | Recommend cuts for smaller deals |
| Stale differentiators | Generic claims ("passion for quality") | Sharpen to specific, provable claims |
| Missing competitive awareness | No reason to choose you over alternatives | Add subtle counter-positioning |
| Weak close | Signature page without urgency | Add "What happens next" before signature |

For each finding: describe the issue, show the current state, draft the improved version. Don't just recommend — write the copy.

When improvements are approved, update the relevant reference files.

## Proposal Pacing Guide

| Deal Size | Recommended Depth |
|---|---|
| Enterprise, $100K+, formal RFP | Full template, max depth on custom sections |
| Mid-market, $25K–100K, semi-formal | Full structure, lighter on warehousing/fulfillment detail |
| Growth, under $25K, informal | Streamlined: Exec Summary, Personas, Differentiators, Pricing, Case Studies, Onboarding, Signature |

## Writing Rules

- Consultative, not salesy. Confident, not arrogant.
- Partnership language throughout — "your merch team, not a swag vendor."
- Open every custom section with the client's context, not yours.
- Banned words: "leverage", "synergy", "holistic", "cutting-edge", "utilize", "facilitate", "empower".
- Alliterative persona names, industry-appropriate.
- Stats and proof points adjacent to claims, not isolated in their own section.

## Evolving This Skill

After each proposal:
1. Add new persona archetypes to `references/stakeholder-personas.md`
2. Add new vertical playbooks to `references/vertical-playbooks.md`
3. Add new RFP patterns to `references/rfp-review-checklist.md`
4. Update `references/proposal-template.md` if structural changes were made
5. Update company-specific knowledge in agent memory, not in this skill
