---
name: front
description: Interact with Front helpdesk via REST API. Use when checking conversations, inbox backlog, response times, or team workload. Covers conversations, inboxes, teammates, tags, and search.
compatibility: Requires curl and FRONT_API_TOKEN environment variable.
metadata:
  author: stitchi-co
  version: "1.0.0"
---

# Front

Query Front helpdesk data via Core API v2.

## Auth

Requires `FRONT_API_TOKEN` environment variable.

```bash
curl -s "https://api2.frontapp.com/..." \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

## Common Queries

**List conversations (most recently updated first):**

```bash
curl -s "https://api2.frontapp.com/conversations?limit=50" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**Unassigned conversations (nobody picked up):**

```bash
curl -s "https://api2.frontapp.com/conversations?q[statuses][]=unassigned&limit=50" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**Open conversations (active, assigned):**

```bash
curl -s "https://api2.frontapp.com/conversations?q[statuses][]=open&limit=50" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**Search conversations (advanced):**

```bash
curl -s "https://api2.frontapp.com/conversations/search/QUERY" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

Search syntax supports: `inbox:NAME`, `assignee:EMAIL`, `status:open|unassigned|archived`, `tag:NAME`, `from:EMAIL`, `to:EMAIL`, `subject:TEXT`, `before:YYYY-MM-DD`, `after:YYYY-MM-DD`.

**List all inboxes:**

```bash
curl -s "https://api2.frontapp.com/inboxes" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**Conversations in a specific inbox:**

```bash
curl -s "https://api2.frontapp.com/inboxes/INBOX_ID/conversations?q[statuses][]=open&limit=50" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**List teammates:**

```bash
curl -s "https://api2.frontapp.com/teammates" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**Conversations assigned to a teammate:**

```bash
curl -s "https://api2.frontapp.com/teammates/TEAMMATE_ID/conversations?q[statuses][]=open&limit=50" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**Get a specific conversation (with messages):**

```bash
curl -s "https://api2.frontapp.com/conversations/CONVERSATION_ID" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

**Messages in a conversation:**

```bash
curl -s "https://api2.frontapp.com/conversations/CONVERSATION_ID/messages" \
  -H "Authorization: Bearer $FRONT_API_TOKEN"
```

## Key Response Fields (Conversations)

- `id` — conversation ID (e.g., `cnv_abc123`)
- `subject` — conversation subject line
- `status` — `open`, `unassigned`, `archived`, `spam`, `trash`
- `assignee` — teammate object (or null if unassigned)
- `inboxes[]` — which inboxes the conversation is in
- `tags[]` — applied tags
- `last_message` — most recent message object
- `created_at` / `updated_at` — Unix timestamps (seconds)
- `is_private` — boolean

## Key Response Fields (Messages)

- `id` — message ID
- `type` — `email`, `sms`, `call`, `custom`, etc.
- `is_inbound` — boolean (true = from customer)
- `author` — who sent it
- `body` — message content (HTML)
- `created_at` — Unix timestamp
- `recipients[]` — to/cc/bcc

## Pagination

Responses include `_pagination`:

- `next` — URL for next page (null if no more)
  Follow `next` for additional results.

## Rate Limits

Varies by plan. Standard rate limiting with `Retry-After` header on 429s.
Search endpoint has additional proportional limiting at 40% of company rate limit.
