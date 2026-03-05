---
name: google-workspace
description: Access Google Workspace APIs (Calendar, Drive) via service account with domain-wide delegation. Use when checking calendar events, shared drive files, or customer documents.
compatibility: Requires Python 3 with google-auth and google-api-python-client. Requires GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_WORKSPACE_USER env vars.
metadata:
  author: stitchi-co
  version: "1.0"
---

# Google Workspace

Access Google Workspace APIs via service account with domain-wide delegation.

## Prerequisites

- Python 3.8+
- `google-auth` and `google-api-python-client` packages
- A Google Cloud service account with domain-wide delegation
- Service account JSON key file

```bash
pip install google-auth google-api-python-client
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Yes | Path to service account JSON key file |
| `GOOGLE_WORKSPACE_USER` | Yes | Email to impersonate (e.g., `user@domain.com`) |

## Usage

```bash
python scripts/gw.py cal-today                     # Today's events
python scripts/gw.py cal-today --brief              # Today's events (no attendees)
python scripts/gw.py cal-upcoming --days 3          # Next 3 days
python scripts/gw.py drive-shared-list              # List shared drives
python scripts/gw.py drive-shared-recent --limit 10 # Recent files in shared drives
```

## Available Commands

### Calendar

- `cal-today [--brief]` — Today's calendar events. `--brief` hides attendees.
- `cal-upcoming [--days N]` — Events in the next N days (default: 3).

### Drive (Shared Drives)

- `drive-shared-list` — List all shared drives visible to the service account.
- `drive-shared-recent [--limit N]` — Recently modified files across shared drives.
- `drive-customer --name "Name"` — Search for a customer folder in shared drives and list contents.

## Scopes

The script requests only readonly scopes:
- `https://www.googleapis.com/auth/calendar.readonly`
- `https://www.googleapis.com/auth/drive.readonly`

## Setup Guide

1. Create a service account in Google Cloud Console
2. Enable domain-wide delegation
3. Grant scopes in Google Workspace Admin → Security → API Controls → Domain-wide Delegation
4. Download the JSON key file
5. Set environment variables and run
