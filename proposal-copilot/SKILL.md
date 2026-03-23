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

**Always treat stitchi.com as the source of truth** for:
- Case studies → fetch from `https://www.stitchi.com/case-studies` (and individual study pages)
- Company positioning, differentiators → fetch from `https://www.stitchi.com`
- Capabilities and solutions → fetch from `https://www.stitchi.com` (explore relevant pages)

**Use reference files in this skill** only for:
- Proposal template structure → `references/proposal-template.md`
- Stakeholder persona archetypes → `references/stakeholder-personas.md`
- Pricing, SLAs, operational details → `references/pricing-and-operations.md`
- RFP review checklist → `references/rfp-review-checklist.md`

The original PandaDoc proposal PDF is in `assets/company-store-proposal-template.pdf` for structural reference.

## Modes

### 1. Draft — "Help me write a proposal for [Client]"

Gather context before drafting:
1. **Client name** (company + short name)
2. **Primary contact** (name, title)
3. **What you know** about their org — employee count, locations, industry, use cases, pain points
4. **Program type** — company store, recurring kits, event support, or combination
5. **Any discovery call notes, email threads, or meeting transcripts** (check Granola, Front, Pipedrive if available)

Then generate the **custom sections** in Markdown:

**Executive Summary** (highest value):
- Open with the client's specific priorities (not Stitchi's)
- Map each priority to a Stitchi capability
- Close with 5 bullet-point highlights tailored to their needs
- Tone: consultative, confident, partnership-oriented
- Length: 3–4 paragraphs + 5 bullets

**Stakeholder Personas & Merch Matrix**:
- Read `references/stakeholder-personas.md` for archetypes
- Select and customize 4–6 personas based on the client's actual org structure
- Rename personas to fit their world (industry-appropriate names)
- Include events column and merch ideas column
- Add "Quick Takeaways" summary beneath the table
- These are **end-user/stakeholder** personas, not buyer personas

**Case Study Selection**:
- Fetch current case studies from stitchi.com
- Select 3–4 most relevant by industry, company size, use case, or program type
- If no strong match exists, pick studies that demonstrate relevant capabilities

For boilerplate sections, note which template sections to include but do not rewrite them — they live in PandaDoc.

### 2. Review — "Here's an RFP. What are we missing?"

When given an RFP (PDF or text) and optionally the current proposal:

1. **Parse the RFP** — extract all requirements, questions, and evaluation criteria
2. **Read `references/rfp-review-checklist.md`** — map RFP requirements against Stitchi's known capabilities
3. **Read `references/proposal-template.md`** — identify which proposal sections address which RFP requirements
4. **Gap analysis** — produce a clear table:

| RFP Requirement | Covered in Proposal? | Section | Gap / Action Needed |
|---|---|---|---|
| Company overview | ✅ | Who We Are | — |
| ADA compliance | ⚠️ | Not addressed | Confirm WCAG status, add section |
| References (3+) | ❌ | Missing | Add references section |

5. **Recommendations** — for each gap, suggest specific content or sections to add
6. **Response structure** — when the RFP has a required outline, map Stitchi's content to that outline

### 3. Improve — "How can we make our proposal better?"

Act as a proposal strategist. When asked to improve the proposal format:

1. **Read `references/proposal-template.md`** for current structure
2. **Critique honestly** — identify weak sections, missing opportunities, ordering issues, tone inconsistencies
3. **Suggest additions** — new sections, better framing, competitive positioning, trend-based recommendations
4. **Benchmark** — compare against best practices for B2B program proposals:
   - Is the value proposition clear in the first 30 seconds of reading?
   - Does every section earn its place?
   - Is pricing positioned as transparent and fair (not just listed)?
   - Are proof points (stats, case studies) placed near claims?
   - Does it feel like a partnership pitch or a vendor catalog?
5. **Draft improvements** — write suggested copy, not just recommendations
6. **Update reference files** if changes are approved — keep `references/proposal-template.md` current

## Writing Guidelines

### Tone
- Consultative, not salesy
- Confident, not arrogant
- Partnership-oriented: "we're your merch team, not a swag vendor"
- Detroit pride is a cultural differentiator — use it naturally, don't force it
- Avoid: "leverage", "synergy", "holistic", "cutting-edge", generic B2B buzzwords

### Executive Summary Pattern
```
[Client]'s priorities: [2-3 sentences about THEIR world, THEIR challenges]

Stitchi's approach: [2-3 sentences mapping our solution to their priorities]

Key highlights:
• [Benefit framed around client need] — [Stitchi capability that delivers it]
• [Benefit] — [Capability]
• [Benefit] — [Capability]
• [Benefit] — [Capability]
• [Benefit] — [Capability]

Closing: [1 sentence about partnership and long-term value]
```

### Persona Naming
- Use alliterative names matching the persona's role context
- Make them memorable and relevant to the client's industry
- Construction: "Crew Chief Carlos", not "Employee Emma"
- Healthcare: "Nurse Nina", not "Field Frank"
- Tech: "Developer Dev", not "Employee Emma"

## Updating This Skill

This skill is designed to evolve. When proposal improvements are approved:
1. Update `references/proposal-template.md` with structural changes
2. Update `references/stakeholder-personas.md` with new archetypes
3. Update `references/pricing-and-operations.md` when rates or SLAs change
4. Update `references/rfp-review-checklist.md` when new RFP patterns emerge
5. Keep this file's workflow instructions current

Do NOT duplicate content from stitchi.com into reference files. If it's on the website, fetch it live.
