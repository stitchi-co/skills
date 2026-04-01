#!/usr/bin/env python3
"""
Analyze Pipedrive pipeline data for weekly/ad-hoc review.

Usage:
  analyze_pipeline.py <data_dir> [--type weekly|adhoc] [--focus org|rep|pipeline]
                      [--filter-org NAME] [--filter-rep NAME] [--filter-pipeline projects|newbiz]
                      [--days 7] [--trend-days 30]

Reads JSON files produced by fetch_pipeline_data.sh.
Outputs structured JSON analysis to stdout.
"""

import json
import sys
import os
import argparse
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from zoneinfo import ZoneInfo

# --- Pipeline & Stage Config ---
PROJECTS_PIPELINE_ID = 3
NEWBIZ_PIPELINE_ID = 9

PROJECTS_STAGES = {
    55: {"name": "Scheduled", "prob": 0.40, "order": 1},
    48: {"name": "Request", "prob": 0.60, "order": 2},
    25: {"name": "Quoted", "prob": 0.70, "order": 3},
    23: {"name": "Approved", "prob": 0.90, "order": 4},
    56: {"name": "In Production", "prob": 0.95, "order": 5},
}

NEWBIZ_STAGES = {
    59: {"name": "Discovery", "prob": 0.25, "order": 1},
    60: {"name": "Proposal", "prob": 0.50, "order": 2},
    61: {"name": "Negotiation", "prob": 0.75, "order": 3},
}

ACCOUNT_TIERS = {246: "XS", 247: "S", 248: "M", 249: "L", 250: "XL"}

# Pipedrive custom field keys (hashed)
CUSTOM_FIELD_ACCOUNT_TIER = "f331c0d704a785facd6d48b0af3cf1a08ff2b55c"
CUSTOM_FIELD_OPPORTUNITY_TYPE = "7568cd7dc2b8dfa1900802ebae3b4950f461075b"
CUSTOM_FIELD_IN_HANDS_DATE = "4f370fd7ef57ae614f7aece2d3eb06fa4def8463"
CUSTOM_FIELD_SOURCE_CAMPAIGN = "7ddcc3c39b35eea5ed08af59e2dfe3ff89ef9a52"

OPPORTUNITY_TYPES = {251: "New Account", 252: "New Program", 253: "Expansion"}


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        data = json.load(f)
    return data if isinstance(data, list) else [data] if data else []


def parse_dt(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    return None


def days_since(dt_str, now):
    dt = parse_dt(dt_str)
    if not dt:
        return None
    return (now - dt).days


def get_stage_name(stage_id, pipeline_id):
    if pipeline_id == PROJECTS_PIPELINE_ID:
        return PROJECTS_STAGES.get(stage_id, {}).get("name", f"Unknown({stage_id})")
    elif pipeline_id == NEWBIZ_PIPELINE_ID:
        return NEWBIZ_STAGES.get(stage_id, {}).get("name", f"Unknown({stage_id})")
    return f"Stage {stage_id}"


def analyze_deals(deals, stages_map, pipeline_name, now, review_days, trend_days):
    """Core analysis for a set of open deals."""
    result = {
        "pipeline": pipeline_name,
        "total_count": len(deals),
        "total_value": sum(d.get("value", 0) or 0 for d in deals),
        "total_weighted": sum(d.get("weighted_value", 0) or 0 for d in deals),
        "by_stage": {},
        "by_rep": {},
        "overdue_close": [],
        "stale_deals": [],
        "zero_value_deals": [],
        "top_deals": [],
        "concentration_risk": [],
    }

    # By stage
    stage_groups = defaultdict(list)
    for d in deals:
        sid = d.get("stage_id")
        stage_groups[sid].append(d)

    for sid, stage_info in sorted(stages_map.items(), key=lambda x: x[1]["order"]):
        stage_deals = stage_groups.get(sid, [])
        result["by_stage"][stage_info["name"]] = {
            "count": len(stage_deals),
            "value": sum(d.get("value", 0) or 0 for d in stage_deals),
            "weighted": sum(d.get("weighted_value", 0) or 0 for d in stage_deals),
            "deals": [
                {
                    "title": d["title"],
                    "value": d.get("value", 0),
                    "org": d.get("org_name"),
                    "owner": d.get("owner_name"),
                    "expected_close": d.get("expected_close_date"),
                    "days_since_update": days_since(d.get("update_time"), now),
                }
                for d in sorted(stage_deals, key=lambda x: -(x.get("value", 0) or 0))
            ],
        }

    # By rep
    rep_groups = defaultdict(list)
    for d in deals:
        rep_groups[d.get("owner_name", "Unassigned")].append(d)

    for rep, rep_deals in rep_groups.items():
        result["by_rep"][rep] = {
            "count": len(rep_deals),
            "value": sum(d.get("value", 0) or 0 for d in rep_deals),
            "weighted": sum(d.get("weighted_value", 0) or 0 for d in rep_deals),
        }

    # Overdue close dates
    for d in deals:
        ecd = d.get("expected_close_date")
        if ecd:
            ecd_dt = parse_dt(ecd)
            if ecd_dt and ecd_dt < now:
                result["overdue_close"].append({
                    "title": d["title"],
                    "value": d.get("value", 0),
                    "org": d.get("org_name"),
                    "owner": d.get("owner_name"),
                    "expected_close": ecd,
                    "days_overdue": (now - ecd_dt).days,
                })
    result["overdue_close"].sort(key=lambda x: -x["days_overdue"])

    # Stale deals: Pipedrive rotten_time OR no update in threshold days (stage-aware)
    # Scheduled (55) deals are future events — only flag if Pipedrive marks rotten
    # All other stages: flag if no update in 14+ days OR rotten
    SCHEDULED_STAGE_ID = 55
    stale_threshold = 14
    for d in deals:
        ds = days_since(d.get("update_time"), now)
        is_rotten = d.get("rotten_time") is not None
        is_scheduled = d.get("stage_id") == SCHEDULED_STAGE_ID

        if is_scheduled:
            # Only flag scheduled deals if Pipedrive explicitly marks them rotten
            should_flag = is_rotten
        else:
            should_flag = is_rotten or (ds is not None and ds >= stale_threshold)

        if should_flag:
            result["stale_deals"].append({
                "title": d["title"],
                "value": d.get("value", 0),
                "org": d.get("org_name"),
                "owner": d.get("owner_name"),
                "stage": get_stage_name(d.get("stage_id"), d.get("pipeline_id")),
                "days_since_update": ds,
                "rotten": is_rotten,
                "last_activity_date": d.get("last_activity_date"),
                "next_activity_date": d.get("next_activity_date"),
            })
    result["stale_deals"].sort(key=lambda x: -(x["days_since_update"] or 0))

    # Zero-value deals
    for d in deals:
        if not d.get("value"):
            result["zero_value_deals"].append({
                "title": d["title"],
                "org": d.get("org_name"),
                "owner": d.get("owner_name"),
                "stage": get_stage_name(d.get("stage_id"), d.get("pipeline_id")),
            })

    # Top deals by value
    result["top_deals"] = [
        {
            "title": d["title"],
            "value": d.get("value", 0),
            "weighted": d.get("weighted_value", 0),
            "org": d.get("org_name"),
            "owner": d.get("owner_name"),
            "stage": get_stage_name(d.get("stage_id"), d.get("pipeline_id")),
            "expected_close": d.get("expected_close_date"),
        }
        for d in sorted(deals, key=lambda x: -(x.get("value", 0) or 0))[:10]
    ]

    # Account concentration risk
    org_values = defaultdict(float)
    total_weighted = result["total_weighted"] or 1
    for d in deals:
        org = d.get("org_name") or "Unknown"
        org_values[org] += d.get("weighted_value", 0) or 0

    for org, val in sorted(org_values.items(), key=lambda x: -x[1]):
        pct = (val / total_weighted) * 100 if total_weighted else 0
        if pct >= 15:  # Flag if >=15% of weighted pipeline
            result["concentration_risk"].append({
                "org": org,
                "weighted_value": val,
                "pct_of_pipeline": round(pct, 1),
            })

    return result


def analyze_won_lost(won_deals, lost_deals, week_start, week_end, prev_week_start, prev_week_end, trend_cutoff):
    """Analyze won/lost deals for fixed week boundaries and rolling trend."""

    def filter_window(deals, start, end, time_field):
        out = []
        for d in deals:
            dt = parse_dt(d.get(time_field))
            if dt and start <= dt <= end:
                out.append(d)
        return out

    def filter_since(deals, cutoff, time_field):
        return [d for d in deals if parse_dt(d.get(time_field)) and parse_dt(d.get(time_field)) >= cutoff]

    this_week_won = filter_window(won_deals, week_start, week_end, "won_time")
    this_week_lost = filter_window(lost_deals, week_start, week_end, "lost_time")
    prev_week_won = filter_window(won_deals, prev_week_start, prev_week_end, "won_time")
    prev_week_lost = filter_window(lost_deals, prev_week_start, prev_week_end, "lost_time")
    trend_won = filter_since(won_deals, trend_cutoff, "won_time")
    trend_lost = filter_since(lost_deals, trend_cutoff, "lost_time")

    def summarize(deals):
        return {
            "count": len(deals),
            "value": sum(d.get("value", 0) or 0 for d in deals),
            "deals": [
                {"title": d["title"], "value": d.get("value", 0), "org": d.get("org_name")}
                for d in sorted(deals, key=lambda x: -(x.get("value", 0) or 0))[:10]
            ],
        }

    return {
        "this_week": {
            "won": summarize(this_week_won),
            "lost": summarize(this_week_lost),
        },
        "previous_week": {
            "won": summarize(prev_week_won),
            "lost": summarize(prev_week_lost),
        },
        "trend": {
            "won": summarize(trend_won),
            "lost": summarize(trend_lost),
        },
    }


def analyze_activities(upcoming, done, deals, now, review_days):
    """Activity analysis: deal-level activity counts, activity-to-close correlation."""
    review_cutoff = now - timedelta(days=review_days)

    # Build deal_id -> activity count map for completed activities
    deal_activity_count = defaultdict(int)
    for a in done:
        did = a.get("deal_id")
        if did:
            deal_activity_count[did] += 1

    # Deals with no activities
    deal_ids_with_activities = set(deal_activity_count.keys())
    no_activity_deals = []
    for d in deals:
        did = d.get("id")
        if did and did not in deal_ids_with_activities:
            no_activity_deals.append({
                "title": d["title"],
                "value": d.get("value", 0),
                "org": d.get("org_name"),
                "owner": d.get("owner_name"),
            })

    # Overdue activities
    overdue_activities = []
    for a in upcoming:
        due = parse_dt(a.get("due_date"))
        if due and due < now:
            overdue_activities.append({
                "subject": a.get("subject"),
                "type": a.get("type"),
                "deal_title": a.get("deal_title"),
                "owner": a.get("owner_name"),
                "due_date": a.get("due_date"),
            })

    return {
        "deals_with_no_activities": no_activity_deals[:20],
        "overdue_activities_count": len(overdue_activities),
        "overdue_activities": overdue_activities[:15],
        "total_upcoming": len(upcoming),
        "total_completed_all_time": len(done),
    }


def analyze_stage_movement(all_deals, stage_changes, stages_map, pipeline_id, week_start, week_end):
    """Identify deals with actual stage_id changes during the review week using changelog data.

    Args:
        all_deals: List of all deals (open + won + lost) for this pipeline.
        stage_changes: List of changelog entries with field_key=='stage_id' and deal_id.
        stages_map: Stage ID -> {name, prob, order} mapping for this pipeline.
        pipeline_id: Pipeline ID to filter deals.
        week_start: Start of review week (datetime).
        week_end: End of review week (datetime).

    Returns:
        List of stage movement records with from/to stage names and timestamps.
    """
    # Build deal lookup
    deal_map = {}
    for d in all_deals:
        if d.get("pipeline_id") == pipeline_id:
            deal_map[d.get("id")] = d

    movements = []
    for change in stage_changes:
        change_time = parse_dt(change.get("time"))
        if not change_time or not (week_start <= change_time <= week_end):
            continue

        deal_id = change.get("deal_id")
        deal = deal_map.get(deal_id)
        if not deal:
            continue

        old_stage_id = int(change.get("old_value", 0)) if change.get("old_value") else None
        new_stage_id = int(change.get("new_value", 0)) if change.get("new_value") else None

        old_stage_name = stages_map.get(old_stage_id, {}).get("name", f"Unknown({old_stage_id})") if old_stage_id else "New"
        new_stage_name = stages_map.get(new_stage_id, {}).get("name", f"Unknown({new_stage_id})") if new_stage_id else "Unknown"

        # Determine direction: forward, backward, or lateral
        old_order = stages_map.get(old_stage_id, {}).get("order", 0) if old_stage_id else 0
        new_order = stages_map.get(new_stage_id, {}).get("order", 0) if new_stage_id else 0
        if new_order > old_order:
            direction = "forward"
        elif new_order < old_order:
            direction = "backward"
        else:
            direction = "lateral"

        movements.append({
            "deal_id": deal_id,
            "title": deal.get("title", f"Deal {deal_id}"),
            "value": deal.get("value", 0),
            "org": deal.get("org_name"),
            "owner": deal.get("owner_name"),
            "from_stage": old_stage_name,
            "to_stage": new_stage_name,
            "direction": direction,
            "change_time": change.get("time"),
        })

    # Sort: forward first, then by time
    direction_order = {"forward": 0, "lateral": 1, "backward": 2}
    movements.sort(key=lambda m: (direction_order.get(m["direction"], 9), m.get("change_time", "")))

    return movements


def analyze_newbiz_stage_movement(open_deals, week_start, week_end):
    """Legacy fallback: flag NB deals updated during review week (update_time proxy).
    Used only when changelog data is not available."""
    recently_updated = []
    for d in open_deals:
        ut = parse_dt(d.get("update_time"))
        if ut and week_start <= ut <= week_end:
            recently_updated.append({
                "title": d["title"],
                "value": d.get("value", 0),
                "org": d.get("org_name"),
                "owner": d.get("owner_name"),
                "stage": get_stage_name(d.get("stage_id"), d.get("pipeline_id", NEWBIZ_PIPELINE_ID)),
                "update_time": d.get("update_time"),
            })
    return recently_updated


def analyze_newbiz_health(open_deals, won_deals, lost_deals, stages_map, now, trend_days):
    """New Business pipeline health metrics."""
    # Bucket distribution (Account Tier custom field)
    bucket_counts = defaultdict(lambda: {"count": 0, "value": 0})
    for d in open_deals:
        tier_val = d.get(CUSTOM_FIELD_ACCOUNT_TIER)
        tier_label = "Unknown"
        if tier_val is not None:
            tier_id = int(tier_val) if str(tier_val).isdigit() else 0
            tier_label = ACCOUNT_TIERS.get(tier_id, "Unknown")
        bucket_counts[tier_label]["count"] += 1
        bucket_counts[tier_label]["value"] += d.get("value", 0) or 0

    # Stage velocity (days since add_time, grouped by current stage)
    velocity = {}
    stage_groups = defaultdict(list)
    for d in open_deals:
        sid = d.get("stage_id")
        stage_groups[sid].append(d)

    for sid, info in stages_map.items():
        stage_deals = stage_groups.get(sid, [])
        if stage_deals:
            ages = [days_since(d.get("add_time"), now) for d in stage_deals]
            ages = [a for a in ages if a is not None]
            if ages:
                velocity[info["name"]] = {
                    "avg_age_days": round(sum(ages) / len(ages), 1),
                    "max_age_days": max(ages),
                    "count": len(ages),
                }

    # Win rate (trend period)
    trend_cutoff = now - timedelta(days=trend_days)
    trend_won = [d for d in won_deals if parse_dt(d.get("won_time")) and parse_dt(d.get("won_time")) >= trend_cutoff]
    trend_lost = [d for d in lost_deals if parse_dt(d.get("lost_time")) and parse_dt(d.get("lost_time")) >= trend_cutoff]
    total_closed = len(trend_won) + len(trend_lost)
    win_rate = round(len(trend_won) / total_closed * 100, 1) if total_closed else None

    return {
        "bucket_distribution": dict(bucket_counts),
        "stage_velocity": velocity,
        "win_rate_pct": win_rate,
        "trend_period_days": trend_days,
        "won_count": len(trend_won),
        "lost_count": len(trend_lost),
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze Pipedrive pipeline data")
    parser.add_argument("data_dir", help="Directory with JSON data files")
    parser.add_argument("--type", default="weekly", choices=["weekly", "adhoc"])
    parser.add_argument("--days", type=int, default=7, help="Review period in days")
    parser.add_argument("--trend-days", type=int, default=30, help="Trend period in days")
    parser.add_argument("--filter-org", default=None, help="Filter by org name")
    parser.add_argument("--filter-rep", default=None, help="Filter by rep name")
    parser.add_argument("--filter-pipeline", default=None, choices=["projects", "newbiz"])
    args = parser.parse_args()

    data_dir = args.data_dir
    tz = ZoneInfo("America/Detroit")
    now = datetime.now(tz).replace(tzinfo=None)  # naive local time for comparisons

    # Fixed week boundary: Fri 00:00 → Thu 23:59 (ET)
    # Find the most recent Thursday (end of review week)
    # weekday(): Mon=0 .. Sun=6; Thu=3
    days_since_thu = (now.weekday() - 3) % 7
    if days_since_thu == 0 and now.hour >= 0:
        # It's Thursday or later — this Thursday is the end of the current week
        week_end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        if now.weekday() != 3:
            # It's Fri-Sun, so last Thursday was the boundary
            week_end = (now - timedelta(days=days_since_thu)).replace(hour=23, minute=59, second=59, microsecond=0)
    else:
        week_end = (now - timedelta(days=days_since_thu)).replace(hour=23, minute=59, second=59, microsecond=0)

    week_start = week_end - timedelta(days=6)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    prev_week_end = week_start - timedelta(seconds=1)
    prev_week_start = prev_week_end - timedelta(days=6)
    prev_week_start = prev_week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    # Trend period is still rolling from now
    trend_cutoff = now - timedelta(days=args.trend_days)

    output = {
        "generated_at": now.isoformat(),
        "review_period": {
            "start": week_start.strftime("%Y-%m-%d"),
            "end": week_end.strftime("%Y-%m-%d"),
            "label": f"Week of {week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}",
        },
        "previous_period": {
            "start": prev_week_start.strftime("%Y-%m-%d"),
            "end": prev_week_end.strftime("%Y-%m-%d"),
        },
        "trend_days": args.trend_days,
    }

    # Load data
    projects_open = load_json(os.path.join(data_dir, "projects_open.json"))
    projects_won = load_json(os.path.join(data_dir, "projects_won.json"))
    projects_lost = load_json(os.path.join(data_dir, "projects_lost.json"))
    newbiz_open = load_json(os.path.join(data_dir, "newbiz_open.json"))
    newbiz_won = load_json(os.path.join(data_dir, "newbiz_won.json"))
    newbiz_lost = load_json(os.path.join(data_dir, "newbiz_lost.json"))
    activities_upcoming = load_json(os.path.join(data_dir, "activities_upcoming.json"))
    activities_done = load_json(os.path.join(data_dir, "activities_done.json"))
    users = load_json(os.path.join(data_dir, "users.json"))
    stage_changes = load_json(os.path.join(data_dir, "deal_stage_changes.json"))
    has_changelog = len(stage_changes) > 0 or os.path.exists(os.path.join(data_dir, "deal_stage_changes.json"))

    # Apply filters
    def apply_filters(deals):
        filtered = deals
        if args.filter_org:
            filtered = [d for d in filtered if args.filter_org.lower() in (d.get("org_name") or "").lower()]
        if args.filter_rep:
            filtered = [d for d in filtered if args.filter_rep.lower() in (d.get("owner_name") or "").lower()]
        return filtered

    projects_open = apply_filters(projects_open)
    newbiz_open = apply_filters(newbiz_open)

    # Users/reps info
    output["reps"] = [
        {"name": u.get("name"), "email": u.get("email"), "active": u.get("active_flag"),
         "created": u.get("created"), "role": u.get("role_id")}
        for u in users if u.get("active_flag")
    ]

    # Projects pipeline
    if args.filter_pipeline != "newbiz":
        output["projects"] = analyze_deals(
            projects_open, PROJECTS_STAGES, "Projects", now, args.days, args.trend_days
        )
        output["projects_won_lost"] = analyze_won_lost(
            projects_won, projects_lost, week_start, week_end,
            prev_week_start, prev_week_end, trend_cutoff
        )

    # New Business pipeline
    if args.filter_pipeline != "projects":
        output["new_business"] = analyze_deals(
            newbiz_open, NEWBIZ_STAGES, "New Business", now, args.days, args.trend_days
        )
        output["new_business_won_lost"] = analyze_won_lost(
            newbiz_won, newbiz_lost, week_start, week_end,
            prev_week_start, prev_week_end, trend_cutoff
        )
        output["new_business_health"] = analyze_newbiz_health(
            newbiz_open, newbiz_won, newbiz_lost, NEWBIZ_STAGES, now, args.trend_days
        )
        if has_changelog:
            all_newbiz = newbiz_open + newbiz_won + newbiz_lost
            output["new_business_stage_movement"] = analyze_stage_movement(
                all_newbiz, stage_changes, NEWBIZ_STAGES, NEWBIZ_PIPELINE_ID, week_start, week_end
            )
        else:
            # Legacy fallback when changelog data not available
            output["new_business_stage_movement"] = analyze_newbiz_stage_movement(
                newbiz_open, week_start, week_end
            )

    # Projects stage movement (new — only available with changelog data)
    if args.filter_pipeline != "newbiz" and has_changelog:
        all_projects = projects_open + projects_won + projects_lost
        output["projects_stage_movement"] = analyze_stage_movement(
            all_projects, stage_changes, PROJECTS_STAGES, PROJECTS_PIPELINE_ID, week_start, week_end
        )

    # Activities
    all_open_deals = []
    if args.filter_pipeline != "newbiz":
        all_open_deals += projects_open
    if args.filter_pipeline != "projects":
        all_open_deals += newbiz_open

    output["activities"] = analyze_activities(
        activities_upcoming, activities_done, all_open_deals, now, args.days
    )

    json.dump(output, sys.stdout, indent=2, default=str)
    print()


if __name__ == "__main__":
    main()
