# Attio MCP overview

Source: official Attio MCP docs (`https://docs.attio.com/mcp/overview` and linked setup pages).

## Connector

Hosted MCP server URL:

`https://mcp.attio.com/mcp`

The official docs describe using Attio MCP from Claude, ChatGPT, Cursor, and VS Code. Setup uses OAuth against the user’s Attio workspace.

## What the MCP server is for

Attio MCP lets an MCP-capable client:
- search and read CRM records
- create and update records
- create and update tasks
- create notes
- search notes, meetings, emails, and call recordings
- read note bodies, email content, and call recording details
- inspect workspace members, teams, and current identity
- inspect attribute definitions for Attio objects

## Tool list called out in the official overview

### Records & schema
- `search-records`
- `get-records-by-ids`
- `create-record`
- `upsert-record`
- `list-attribute-definitions`

### Notes
- `create-note`
- `search-notes-by-metadata`
- `semantic-search-notes`
- `get-note-body`

### Tasks
- `create-task`
- `update-task`

### Meetings, calls, and email
- `search-meetings`
- `search-call-recordings-by-metadata`
- `semantic-search-call-recordings`
- `get-call-recording`
- `search-emails-by-metadata`
- `semantic-search-emails`
- `get-email-content`

### Workspace
- `list-workspace-members`
- `list-workspace-teams`
- `whoami`

## Recommended operating pattern

### 1. Search before writing
Use search to find the right record instead of assuming identifiers.

### 2. Inspect schema before unfamiliar writes
Use `list-attribute-definitions` before writing to custom objects or unfamiliar fields.

### 3. Prefer upsert when a stable key exists
Good examples:
- person by email
- company by domain

### 4. Use semantic search for knowledge retrieval
For prompts like:
- pricing objections
- meeting takeaways
- last discussion about renewal risk

semantic search is usually a better first move than exact metadata search.

## Example user requests from the docs

Representative examples in the official overview include requests like:
- find people at a company
- show a company record
- create a follow-up task
- search notes about a topic
- find transcripts from a recent call

## Rate limits and approvals

The overview states:
- read and write rate limits are separate
- approvals can apply to writes
- the authenticated user’s Attio permissions still govern access

When implementing workflows on top of MCP:
- prefer smaller write batches
- serialize writes when possible
- retry gently if rate limited

## When to stop

If Attio tools are unavailable in the current client session, the likely problem is not the prompt — it is that Attio MCP is not connected. In that case, ask the user to connect the hosted server URL above and complete OAuth.
