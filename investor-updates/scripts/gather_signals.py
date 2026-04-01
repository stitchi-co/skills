#!/usr/bin/env python3
"""
gather_signals.py — Fetch investor update signals from all data sources.

Usage:
    python3 gather_signals.py [--lookback-days 90] [--pipedrive] [--front] [--notion-history] [--all]

Outputs a structured JSON to stdout with signal data from each source.
"""

import argparse
import json
import os
import sys
import datetime
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

NOTION_KEY = Path("~/.config/notion/api_key").expanduser().read_text().strip()
PIPEDRIVE_KEY = Path("~/.config/pipedrive/api_key").expanduser().read_text().strip()
NOTION_VERSION = "2025-09-03"
INVESTOR_UPDATES_DB = "b037f250481c476e98e46dc9198138b5"

# Slack config — read from ~/.openclaw/.env
def _load_slack_token():
    env_path = Path("~/.openclaw/.env").expanduser()
    if not env_path.exists():
        return None
    for line in env_path.read_text().splitlines():
        if line.startswith("SLACK_EVEREST_BOT_TOKEN="):
            return line.split("=", 1)[1].strip()
    return None

SLACK_BOT_TOKEN = _load_slack_token()

SLACK_CHANNELS = {
    "team-revenue": "C032HCCEB88",
    "team-delivery": "C092NHPRSSZ",
    "team-product": "C065F2C1TGF",
    "general": "C031M06D5HU",
}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }

def pipedrive_url(path):
    sep = "&" if "?" in path else "?"
    return f"https://api.pipedrive.com/v1/{path}{sep}api_token={PIPEDRIVE_KEY}"

def date_n_days_ago(n):
    return (datetime.datetime.now() - datetime.timedelta(days=n)).strftime("%Y-%m-%d")

# ─── Notion: Investor Update History ──────────────────────────────────────────

def fetch_investor_updates_history(limit=5):
    """Fetch recent investor updates from Notion for style/structure reference."""
    import urllib.request

    body = json.dumps({
        "sorts": [{"property": "Date", "direction": "descending"}],
        "page_size": limit
    }).encode()

    # Use older API version for database queries (2022-06-28 uses /databases/ endpoint)
    headers = notion_headers()
    headers["Notion-Version"] = "2022-06-28"
    req = urllib.request.Request(
        f"https://api.notion.com/v1/databases/{INVESTOR_UPDATES_DB}/query",
        data=body,
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        pages = data.get("results", [])
        updates = []
        for p in pages:
            props = p.get("properties", {})
            title = ""
            for v in props.values():
                if v.get("type") == "title":
                    parts = v.get("title", [])
                    if parts:
                        title = parts[0].get("plain_text", "")
                        break
            updates.append({
                "id": p["id"],
                "title": title,
                "url": p.get("url", ""),
                "last_edited": p.get("last_edited_time", ""),
            })
        return {"status": "ok", "updates": updates}
    except Exception as e:
        return {"status": "error", "error": str(e), "hint": "Share the Investor Updates database with Clawdbot integration in Notion."}

def fetch_notion_page_content(page_id):
    """Fetch full text content of a Notion page."""
    import urllib.request

    headers = notion_headers()
    headers["Notion-Version"] = "2022-06-28"
    req = urllib.request.Request(
        f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        blocks = data.get("results", [])
        lines = []
        for b in blocks:
            btype = b.get("type", "")
            block_data = b.get(btype, {})
            rich = block_data.get("rich_text", [])
            text = "".join(r.get("plain_text", "") for r in rich)
            if text:
                lines.append(text)
        return "\n".join(lines)
    except Exception as e:
        return f"[Error fetching page: {e}]"

# ─── Pipedrive: Pipeline Signals ──────────────────────────────────────────────

def fetch_pipedrive_signals(lookback_days=90):
    """Fetch pipeline data: won deals, active deals by stage, revenue."""
    import urllib.request

    since = date_n_days_ago(lookback_days)
    results = {}

    # Recent won deals (Projects pipeline id=3)
    try:
        url = pipedrive_url(f"deals?pipeline_id=3&status=won&start=0&limit=50")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        deals = data.get("data") or []
        won = []
        for d in deals:
            won_time = (d.get("won_time") or "").replace(" ", "T")
            if won_time[:10] >= since:
                won.append({
                    "title": d.get("title"),
                    "value": d.get("value"),
                    "currency": d.get("currency"),
                    "org": d.get("org_name"),
                    "won_time": won_time[:10],
                })
        results["won_deals_projects"] = won
    except Exception as e:
        results["won_deals_projects"] = {"error": str(e)}

    # Active deals in Projects pipeline
    try:
        url = pipedrive_url("deals?pipeline_id=3&status=open&start=0&limit=100")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        deals = data.get("data") or []
        by_stage = {}
        total_value = 0
        for d in deals:
            stage = d.get("stage_id")
            stage_name = d.get("stage_name", str(stage))
            by_stage.setdefault(stage_name, {"count": 0, "value": 0})
            by_stage[stage_name]["count"] += 1
            by_stage[stage_name]["value"] += d.get("value") or 0
            total_value += d.get("value") or 0
        results["active_pipeline_projects"] = {
            "total_value": total_value,
            "by_stage": by_stage,
            "count": len(deals),
        }
    except Exception as e:
        results["active_pipeline_projects"] = {"error": str(e)}

    # New Business pipeline (id=9)
    try:
        url = pipedrive_url("deals?pipeline_id=9&status=open&start=0&limit=100")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        deals = data.get("data") or []
        results["new_business_pipeline"] = {
            "count": len(deals),
            "deals": [{"title": d.get("title"), "stage": d.get("stage_name"), "value": d.get("value"), "org": d.get("org_name")} for d in deals[:20]],
        }
    except Exception as e:
        results["new_business_pipeline"] = {"error": str(e)}

    return results

# ─── Front: Customer & Investor Conversations ─────────────────────────────────

def fetch_front_signals(lookback_days=90):
    """Fetch high-signal conversations from Front (customer, investor, partner)."""
    import urllib.request

    try:
        front_token_path = Path("~/.config/front/api_token").expanduser()
        if not front_token_path.exists():
            return {"status": "error", "error": "No Front API token at ~/.config/front/api_token"}
        front_token = front_token_path.read_text().strip()
    except Exception as e:
        return {"status": "error", "error": str(e)}

    headers = {
        "Authorization": f"Bearer {front_token}",
        "Content-Type": "application/json",
    }

    since_ts = int((datetime.datetime.now() - datetime.timedelta(days=lookback_days)).timestamp())
    results = {}

    # Recent conversations — limit to clients inbox
    try:
        url = "https://api2.frontapp.com/conversations?q[statuses][]=archived&q[statuses][]=assigned&limit=50&sort_by=last_message_at&sort_order=desc"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        convos = data.get("_results", [])
        recent = []
        for c in convos:
            subject = c.get("subject", "")
            last_msg = c.get("last_message", {})
            ts = last_msg.get("created_at", 0)
            if ts >= since_ts:
                recent.append({
                    "subject": subject,
                    "status": c.get("status"),
                    "assignee": (c.get("assignee") or {}).get("email"),
                    "tags": [t.get("name") for t in c.get("tags", [])],
                    "last_message_at": ts,
                })
        results["recent_conversations"] = recent[:20]
    except Exception as e:
        results["recent_conversations"] = {"error": str(e)}

    return results

# ─── Slack: Internal Signal Channels ──────────────────────────────────────────

def fetch_slack_signals(lookback_days=90, channels=None):
    """Fetch recent messages from Slack channels for signal extraction."""
    import urllib.request

    if not SLACK_BOT_TOKEN:
        return {"status": "error", "error": "No SLACK_EVEREST_BOT_TOKEN in ~/.openclaw/.env"}

    target_channels = channels or SLACK_CHANNELS
    oldest = str(int((datetime.datetime.now() - datetime.timedelta(days=lookback_days)).timestamp()))
    results = {}

    for name, channel_id in target_channels.items():
        try:
            url = f"https://slack.com/api/conversations.history?channel={channel_id}&oldest={oldest}&limit=200"
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json",
            })
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())

            if not data.get("ok"):
                results[name] = {"error": data.get("error", "unknown"), "hint": f"Invite EverestBot to #{name}: /invite @EverestBot"}
                continue

            messages = data.get("messages", [])
            # Filter to human messages (no bot/system), deduplicate, keep text
            filtered = []
            for m in messages:
                if m.get("subtype") in ("bot_message", "channel_join", "channel_leave", "channel_topic", "channel_purpose"):
                    continue
                text = m.get("text", "").strip()
                if not text or len(text) < 10:
                    continue
                ts = float(m.get("ts", 0))
                filtered.append({
                    "text": text[:500],  # Truncate long messages
                    "user": m.get("user", ""),
                    "date": datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                    "reactions": sum(r.get("count", 0) for r in m.get("reactions", [])),
                })

            # Sort by reaction count (most engaged first), then by date
            filtered.sort(key=lambda x: (-x["reactions"], x["date"]))
            results[name] = {
                "total_messages": len(filtered),
                "top_messages": filtered[:30],  # Top 30 by engagement
            }
        except Exception as e:
            results[name] = {"error": str(e)}

    return {"status": "ok", "channels": results}

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Gather investor update signals")
    parser.add_argument("--lookback-days", type=int, default=90, help="Days of history to pull")
    parser.add_argument("--pipedrive", action="store_true")
    parser.add_argument("--front", action="store_true")
    parser.add_argument("--slack", action="store_true")
    parser.add_argument("--notion-history", action="store_true")
    parser.add_argument("--all", action="store_true", help="Pull all sources")
    parser.add_argument("--page-id", type=str, help="Fetch full content of a specific Notion page")
    args = parser.parse_args()

    run_all = args.all or not (args.pipedrive or args.front or args.slack or args.notion_history or args.page_id)

    output = {"generated_at": datetime.datetime.now().isoformat(), "lookback_days": args.lookback_days}

    if args.page_id:
        output["page_content"] = fetch_notion_page_content(args.page_id)

    if run_all or args.notion_history:
        output["investor_updates_history"] = fetch_investor_updates_history(limit=5)

    if run_all or args.pipedrive:
        output["pipedrive"] = fetch_pipedrive_signals(lookback_days=args.lookback_days)

    if run_all or args.front:
        output["front"] = fetch_front_signals(lookback_days=args.lookback_days)

    if run_all or args.slack:
        output["slack"] = fetch_slack_signals(lookback_days=args.lookback_days)

    print(json.dumps(output, indent=2, default=str))

if __name__ == "__main__":
    main()
