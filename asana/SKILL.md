---
name: asana
description: Interact with Asana project management via REST API. Use when checking tasks, projects, deadlines, workload, or project status. Covers tasks, projects, sections, and search.
compatibility: Requires curl and ASANA_API_KEY environment variable.
metadata:
  author: stitchi-co
  version: "1.0.0"
---

# Asana

Query and manage Asana data via REST API v1.

## Auth

Requires `ASANA_API_KEY` environment variable.

```bash
ASANA_TOKEN="$ASANA_API_KEY"
```

All requests use header: `-H "Authorization: Bearer $ASANA_TOKEN"`

Base URL: `https://app.asana.com/api/1.0`

## Setup

You need your workspace GID. Find it:
```bash
curl -s "https://app.asana.com/api/1.0/workspaces" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

List projects in a workspace:
```bash
curl -s "https://app.asana.com/api/1.0/projects?workspace=WORKSPACE_GID&opt_fields=name" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

## Common Queries

**My tasks (assigned to me, incomplete):**
```bash
curl -s "https://app.asana.com/api/1.0/tasks?assignee=me&workspace=WORKSPACE_GID&completed_since=now&opt_fields=name,due_on,projects.name,assignee_section.name" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

**Tasks in a project (with sections and assignees):**
```bash
curl -s "https://app.asana.com/api/1.0/tasks?project=PROJECT_GID&completed_since=now&opt_fields=name,due_on,assignee.name,memberships.section.name" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

**Overdue tasks (my tasks, then filter due_on < today):**
```bash
curl -s "https://app.asana.com/api/1.0/tasks?assignee=me&workspace=WORKSPACE_GID&completed_since=now&opt_fields=name,due_on,projects.name" \
  -H "Authorization: Bearer $ASANA_TOKEN"
# Filter in code: due_on < today's date
```

**Search tasks (full-text):**
```bash
curl -s "https://app.asana.com/api/1.0/workspaces/WORKSPACE_GID/tasks/search?text=QUERY&completed=false&opt_fields=name,due_on,assignee.name,projects.name" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

**Tasks due soon (next 7 days):**
```bash
curl -s "https://app.asana.com/api/1.0/workspaces/WORKSPACE_GID/tasks/search?due_on.before=YYYY-MM-DD&due_on.after=YYYY-MM-DD&completed=false&assignee.any=me&opt_fields=name,due_on,projects.name" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

**Create a task:**
```bash
curl -s -X POST "https://app.asana.com/api/1.0/tasks" \
  -H "Authorization: Bearer $ASANA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data":{"name":"Task name","projects":["PROJECT_GID"],"assignee":"me","due_on":"YYYY-MM-DD"}}'
```

**Project sections:**
```bash
curl -s "https://app.asana.com/api/1.0/projects/PROJECT_GID/sections?opt_fields=name" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

**Get a specific task:**
```bash
curl -s "https://app.asana.com/api/1.0/tasks/TASK_GID?opt_fields=name,notes,due_on,assignee.name,projects.name,completed" \
  -H "Authorization: Bearer $ASANA_TOKEN"
```

## Key Response Fields (Tasks)

- `name` — task title
- `completed` — boolean
- `due_on` — date string (YYYY-MM-DD) or null
- `assignee.name` — who it's assigned to
- `projects[].name` — which project(s)
- `memberships[].section.name` — which section within a project
- `notes` — task description (plain text)

## opt_fields

Asana returns minimal data by default. Use `opt_fields` to request specific fields (comma-separated). Always include the fields you need.

## Pagination

Responses may include `next_page.uri` — follow it for more results. Default limit: 20. Max: 100 (`&limit=100`).

## Rate Limits

1500 requests per minute. Standard `Retry-After` header on 429s.
