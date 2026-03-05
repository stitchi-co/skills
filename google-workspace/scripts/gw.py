#!/usr/bin/env python3
"""Google Workspace CLI — Calendar + Shared Drives.

Requires:
  - GOOGLE_SERVICE_ACCOUNT_FILE: path to service account JSON key
  - GOOGLE_WORKSPACE_USER: email to impersonate (e.g., user@domain.com)

Optional:
  - GOOGLE_CUSTOMERS_DRIVE_ID: shared drive ID for customer folder lookups
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

SA_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", "")
DEFAULT_USER = os.environ.get("GOOGLE_WORKSPACE_USER", "")
CUSTOMERS_DRIVE_ID = os.environ.get("GOOGLE_CUSTOMERS_DRIVE_ID", "")

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("Missing dependencies. Install with: pip install google-auth google-api-python-client", file=sys.stderr)
    sys.exit(1)


def check_env():
    if not SA_FILE:
        print("Error: GOOGLE_SERVICE_ACCOUNT_FILE not set", file=sys.stderr)
        sys.exit(1)
    if not DEFAULT_USER:
        print("Error: GOOGLE_WORKSPACE_USER not set", file=sys.stderr)
        sys.exit(1)


def get_service(api, version, scopes, user=None):
    user = user or DEFAULT_USER
    creds = service_account.Credentials.from_service_account_file(SA_FILE, scopes=scopes)
    creds = creds.with_subject(user)
    return build(api, version, credentials=creds, cache_discovery=False)


# --- Calendar ---

def calendar_today(args):
    service = get_service("calendar", "v3", ["https://www.googleapis.com/auth/calendar.readonly"], args.user)
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0).isoformat()
    end = now.replace(hour=23, minute=59, second=59).isoformat()
    events = service.events().list(
        calendarId="primary", timeMin=start, timeMax=end,
        maxResults=50, singleEvents=True, orderBy="startTime"
    ).execute().get("items", [])
    for e in events:
        t = e["start"].get("dateTime", e["start"].get("date", ""))
        if "T" in t:
            t = t.split("T")[1][:5]
        attendees = [a.get("email", "") for a in e.get("attendees", [])]
        print(f"  {t}  {e.get('summary', '(no title)')}")
        if attendees and not args.brief:
            print(f"        with: {', '.join(attendees[:5])}")
    if not events:
        print("  No events today.")


def calendar_upcoming(args):
    service = get_service("calendar", "v3", ["https://www.googleapis.com/auth/calendar.readonly"], args.user)
    now = datetime.now(timezone.utc)
    end = (now + timedelta(days=args.days)).isoformat()
    events = service.events().list(
        calendarId="primary", timeMin=now.isoformat(), timeMax=end,
        maxResults=100, singleEvents=True, orderBy="startTime"
    ).execute().get("items", [])
    current_date = ""
    for e in events:
        d = e["start"].get("dateTime", e["start"].get("date", ""))
        day = d[:10]
        if day != current_date:
            current_date = day
            print(f"\n  📅 {day}")
        t = d.split("T")[1][:5] if "T" in d else "all-day"
        print(f"    {t}  {e.get('summary', '(no title)')}")
    if not events:
        print("  No upcoming events.")


# --- Drive (Shared Drives) ---

def drive_shared_list(args):
    service = get_service("drive", "v3", ["https://www.googleapis.com/auth/drive.readonly"], args.user)
    results = service.drives().list(pageSize=50).execute()
    drives = results.get("drives", [])
    for d in drives:
        print(f"  {d['name']}  (id: {d['id']})")
    if not drives:
        print("  No shared drives found.")


def drive_shared_recent(args):
    service = get_service("drive", "v3", ["https://www.googleapis.com/auth/drive.readonly"], args.user)
    results = service.files().list(
        corpora="allDrives",
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        orderBy="modifiedTime desc",
        pageSize=args.limit,
        fields="files(id,name,mimeType,modifiedTime,driveId,webViewLink)",
        q="trashed=false"
    ).execute()
    files = results.get("files", [])
    for f in files:
        mod = f.get("modifiedTime", "")[:10]
        mime = f.get("mimeType", "").split(".")[-1]
        link = f.get("webViewLink", "")
        print(f"  {mod}  [{mime}]  {f['name']}")
        if link:
            print(f"         {link}")
    if not files:
        print("  No recent files in shared drives.")


def drive_customer(args):
    if not CUSTOMERS_DRIVE_ID:
        print("Error: GOOGLE_CUSTOMERS_DRIVE_ID not set. Set it to search customer folders.", file=sys.stderr)
        sys.exit(1)
    service = get_service("drive", "v3", ["https://www.googleapis.com/auth/drive.readonly"], args.user)
    q = f"name contains '{args.name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(
        corpora="drive",
        driveId=CUSTOMERS_DRIVE_ID,
        includeItemsFromAllDrives=True,
        supportsAllDrives=True,
        q=q,
        fields="files(id,name,webViewLink)",
        pageSize=10
    ).execute()
    folders = results.get("files", [])
    if not folders:
        print(f"  No customer folder found matching '{args.name}'.")
        return
    for folder in folders:
        print(f"\n  📁 {folder['name']}")
        if folder.get("webViewLink"):
            print(f"     {folder['webViewLink']}")
        contents = service.files().list(
            corpora="drive",
            driveId=CUSTOMERS_DRIVE_ID,
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            q=f"'{folder['id']}' in parents and trashed=false",
            fields="files(id,name,mimeType,modifiedTime,webViewLink)",
            orderBy="modifiedTime desc",
            pageSize=20
        ).execute().get("files", [])
        for f in contents:
            mod = f.get("modifiedTime", "")[:10]
            is_folder = "folder" in f.get("mimeType", "")
            icon = "📁" if is_folder else "📄"
            print(f"     {icon} {mod}  {f['name']}")


# --- Main ---

def main():
    check_env()
    parser = argparse.ArgumentParser(description="Google Workspace CLI")
    parser.add_argument("--user", default=DEFAULT_USER, help="Impersonate user")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("cal-today", help="Today's calendar events")
    p.add_argument("--brief", action="store_true", help="Skip attendees")

    p = sub.add_parser("cal-upcoming", help="Upcoming events")
    p.add_argument("--days", type=int, default=3, help="Days ahead (default: 3)")

    sub.add_parser("drive-shared-list", help="List shared drives")

    p = sub.add_parser("drive-shared-recent", help="Recent files in shared drives")
    p.add_argument("--limit", type=int, default=10, help="Max results")

    p = sub.add_parser("drive-customer", help="Customer folder lookup")
    p.add_argument("--name", required=True, help="Customer name to search")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "cal-today": calendar_today,
        "cal-upcoming": calendar_upcoming,
        "drive-shared-list": drive_shared_list,
        "drive-shared-recent": drive_shared_recent,
        "drive-customer": drive_customer,
    }
    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
