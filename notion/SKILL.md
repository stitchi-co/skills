---
name: notion
description: Notion API for creating and managing pages, databases, and blocks. Use when reading, creating, or updating Notion content, querying databases, or managing workspace structure.
homepage: https://developers.notion.com
compatibility: Requires curl and NOTION_API_KEY environment variable.
metadata:
  author: stitchi-co
  version: "1.0.0"
---

# notion

Use the Notion API to create/read/update pages, data sources (databases), and blocks.

## Authentication

All requests require these headers:

- `Authorization: Bearer $NOTION_API_KEY`
- `Notion-Version: 2025-09-03`
- `Content-Type: application/json` (for POST/PATCH requests)

The API key is provided via the `$NOTION_API_KEY` environment variable.

## API Base URL

`https://api.notion.com/v1`

## Common Operations

### Search for pages and data sources

`POST /v1/search`

Body:
```json
{"query": "page title"}
```

### Get page

`GET /v1/pages/{page_id}`

### Get page content (blocks)

`GET /v1/blocks/{page_id}/children`

### Create page in a data source

`POST /v1/pages`

Body:
```json
{
  "parent": {"database_id": "xxx"},
  "properties": {
    "Name": {"title": [{"text": {"content": "New Item"}}]},
    "Status": {"select": {"name": "Todo"}}
  }
}
```

### Query a data source (database)

`POST /v1/data_sources/{data_source_id}/query`

Body:
```json
{
  "filter": {"property": "Status", "select": {"equals": "Active"}},
  "sorts": [{"property": "Date", "direction": "descending"}]
}
```

### Create a data source (database)

`POST /v1/data_sources`

Body:
```json
{
  "parent": {"page_id": "xxx"},
  "title": [{"text": {"content": "My Database"}}],
  "properties": {
    "Name": {"title": {}},
    "Status": {"select": {"options": [{"name": "Todo"}, {"name": "Done"}]}},
    "Date": {"date": {}}
  }
}
```

### Update page properties

`PATCH /v1/pages/{page_id}`

Body:
```json
{"properties": {"Status": {"select": {"name": "Done"}}}}
```

### Add blocks to page

`PATCH /v1/blocks/{page_id}/children`

Body:
```json
{
  "children": [
    {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello"}}]}}
  ]
}
```

## Property Types

Common property formats for database items:
- **Title:** `{"title": [{"text": {"content": "..."}}]}`
- **Rich text:** `{"rich_text": [{"text": {"content": "..."}}]}`
- **Select:** `{"select": {"name": "Option"}}`
- **Multi-select:** `{"multi_select": [{"name": "A"}, {"name": "B"}]}`
- **Date:** `{"date": {"start": "2024-01-15", "end": "2024-01-16"}}`
- **Checkbox:** `{"checkbox": true}`
- **Number:** `{"number": 42}`
- **URL:** `{"url": "https://..."}`
- **Email:** `{"email": "a@b.com"}`
- **Relation:** `{"relation": [{"id": "page_id"}]}`

## Key Differences in 2025-09-03

- **Databases → Data Sources:** Use `/data_sources/` endpoints for queries and retrieval
- **Two IDs:** Each database now has both a `database_id` and a `data_source_id`
  - Use `database_id` when creating pages (`parent: {"database_id": "..."}`)
  - Use `data_source_id` when querying (`POST /v1/data_sources/{id}/query`)
- **Search results:** Databases return as `"object": "data_source"` with their `data_source_id`
- **Parent in responses:** Pages show `parent.data_source_id` alongside `parent.database_id`
- **Finding the data_source_id:** Search for the database, or call `GET /v1/data_sources/{data_source_id}`

## Notes

- Page/database IDs are UUIDs (with or without dashes)
- The API cannot set database view filters — that's UI-only
- Rate limit: ~3 requests/second average
- Use `is_inline: true` when creating data sources to embed them in pages
