---
name: attio
description: Interact with an Attio CRM workspace through Attio's hosted MCP server. Use when searching, reading, creating, or updating Attio records, notes, tasks, meetings, call recordings, emails, workspace members, or teams through MCP-capable clients like Claude, ChatGPT, Cursor, or VS Code.
---

# Attio

Use Attio's hosted MCP server to work with CRM data in natural language. Prefer the MCP workflow over raw API calls when the client already exposes Attio MCP tools.

## Quick setup

If Attio MCP is not already connected, add Attio's hosted server URL to the MCP-capable client and complete OAuth:

`https://mcp.attio.com/mcp`

Use this skill only after Attio MCP is connected and the client exposes the Attio tools.

## Recommended workflow

1. Identify the target object and record.
   - People, companies, deals, tasks, notes, meetings, emails, and workspace metadata are common entry points.
2. Start with search.
   - Use record or metadata search before assuming an ID.
3. Inspect schema before writing to unfamiliar objects.
   - Use `list-attribute-definitions` to discover valid fields, types, and option values.
4. Read full details before updating.
   - Fetch the full record or note body when the exact current state matters.
5. Prefer upsert when a stable matching key exists.
   - Email for people and domain for companies are common examples.
6. Keep writes explicit.
   - Summarize the intended create/update action before executing when the user’s request is ambiguous.

## Core tool patterns

### Records & objects

Use for people, companies, deals, and custom objects.

- `search-records` — find records by name, email, domain, or indexed attributes
- `get-records-by-ids` — fetch full details for known records
- `create-record` — create a new record
- `upsert-record` — create or update using a matching attribute
- `list-attribute-definitions` — inspect available fields before writing

Preferred pattern:
1. `search-records`
2. `get-records-by-ids` if needed
3. `list-attribute-definitions` before unfamiliar writes
4. `create-record` or `upsert-record`

### Notes

Use notes for call summaries, meeting takeaways, account updates, and relationship history.

- `create-note`
- `search-notes-by-metadata`
- `semantic-search-notes`
- `get-note-body`

Prefer semantic search when the user asks by topic instead of exact metadata.

### Tasks

Use tasks for follow-ups, deadlines, and next steps.

- `create-task`
- `update-task`

Include deadline, assignee, and linked record when the user provides enough context.

### Meetings & calls

Use when the user asks about upcoming meetings, past calls, transcripts, or recording search.

- `search-meetings`
- `search-call-recordings-by-metadata`
- `semantic-search-call-recordings`
- `get-call-recording`

Prefer metadata search first when the participant, company, or date range is known.

### Emails

Use when the user asks to find or read email history inside Attio.

- `search-emails-by-metadata`
- `semantic-search-emails`
- `get-email-content`

### Workspace

Use to understand workspace structure and identity.

- `list-workspace-members`
- `list-workspace-teams`
- `whoami`

## Prompting guidance

Use direct operational prompts. Good patterns:

- "Find all contacts at Stripe and summarize the key people."
- "Show me the company record for linear.app and list important open tasks."
- "Create a follow-up task for Ramp due next Tuesday and link it to the company record."
- "Search notes for pricing objections related to Notion."
- "Find the transcript from yesterday’s call with Linear."

When a user asks for a broad CRM action, decompose it into:
- search
- inspect
- write
- confirm result

## Safety and reliability

- Expect read operations to be easier to approve than writes.
- Do not guess option values or field names on unfamiliar objects; inspect attribute definitions first.
- Avoid large parallel write bursts.
- If rate limited, reduce concurrency and retry sequentially after a short pause.
- Stay within the authenticated user’s workspace permissions.

## Fallback

If the client does not expose Attio MCP tools, stop and tell the user Attio MCP is not connected in the current environment. Point them to `https://mcp.attio.com/mcp` for the connector URL.

## Reference

For the official setup flow, supported tools, example prompts, rate limits, and approval model, read `references/mcp-overview.md`.
