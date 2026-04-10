#!/usr/bin/env python3
"""
Extract Notion database properties from analyze_pipeline.py output.

Reads the analysis JSON and outputs the exact properties needed for 
the Notion pipeline review database entry. This prevents manual 
transcription errors in the won/lost fields.

Usage:
  python3 extract_notion_properties.py <analysis.json>

Output: JSON with Notion-ready property values.
"""

import json
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: extract_notion_properties.py <analysis.json>", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    period = data.get("review_period", {})
    
    # Extract won/lost from the analysis
    proj_wl = data.get("projects_won_lost", {}).get("this_week", {})
    nb_wl = data.get("new_business_won_lost", {}).get("this_week", {})
    
    projects_won = proj_wl.get("won", {}).get("value", 0)
    projects_lost = proj_wl.get("lost", {}).get("value", 0)
    nb_won = nb_wl.get("won", {}).get("value", 0)
    nb_lost = nb_wl.get("lost", {}).get("value", 0)
    
    # Weighted pipeline values
    projects_weighted = round(data.get("projects", {}).get("total_weighted", 0))
    nb_weighted = round(data.get("new_business", {}).get("total_weighted", 0))
    
    # Build the week label
    start = period.get("start", "")
    end = period.get("end", "")
    label = period.get("label", f"{start} – {end}")
    # Convert to "Mar 27 – Apr 02, 2026" format
    from datetime import datetime
    try:
        s = datetime.strptime(start, "%Y-%m-%d")
        e = datetime.strptime(end, "%Y-%m-%d")
        label = f"{s.strftime('%b %d')} – {e.strftime('%b %d, %Y')}"
    except (ValueError, TypeError):
        pass

    properties = {
        "Week": {"title": [{"text": {"content": label}}]},
        "Date": {"date": {"start": start, "end": end}},
        "Projects Won": {"number": projects_won},
        "Projects Lost": {"number": projects_lost},
        "Projects Weighted": {"number": projects_weighted},
        "NB Won": {"number": nb_won},
        "NB Lost": {"number": nb_lost},
        "NB Weighted": {"number": nb_weighted},
        "Status": {"select": {"name": "Published"}}
    }

    # Also output a human-readable summary for the composing LLM
    summary = {
        "properties": properties,
        "_summary": {
            "period": label,
            "projects_won": f"${projects_won:,} ({proj_wl.get('won', {}).get('count', 0)} deals)",
            "projects_won_deals": proj_wl.get("won", {}).get("deals", []),
            "projects_lost": f"${projects_lost:,} ({proj_wl.get('lost', {}).get('count', 0)} deals)",
            "projects_lost_deals": proj_wl.get("lost", {}).get("deals", []),
            "nb_won": f"${nb_won:,} ({nb_wl.get('won', {}).get('count', 0)} deals)",
            "nb_won_deals": nb_wl.get("won", {}).get("deals", []),
            "nb_lost": f"${nb_lost:,} ({nb_wl.get('lost', {}).get('count', 0)} deals)",
            "nb_lost_deals": nb_wl.get("lost", {}).get("deals", []),
            "projects_weighted": f"${projects_weighted:,}",
            "nb_weighted": f"${nb_weighted:,}",
        }
    }

    json.dump(summary, sys.stdout, indent=2, default=str)
    print()


if __name__ == "__main__":
    main()
