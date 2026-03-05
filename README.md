# Skills

Portable [Agent Skills](https://agentskills.io) for Stitchi's tool integrations.

## Install

```bash
# All skills
npx skills add stitchi-co/skills --all

# Specific skill
npx skills add stitchi-co/skills --skill pipedrive
```

Works with Claude Code, OpenClaw, Cursor, Codex, and [40+ other agents](https://skills.sh).

## Skills

| Skill | Description |
|-------|-------------|
| [asana](./asana/) | Asana project management — tasks, projects, sections, search |
| [front](./front/) | Front helpdesk — conversations, inboxes, teammates, tags |
| [google-workspace](./google-workspace/) | Google Workspace — Calendar, Drive (service account) |
| [notion](./notion/) | Notion — pages, databases, blocks |
| [pipedrive](./pipedrive/) | Pipedrive CRM — deals, contacts, orgs, activities, pipelines |

## Environment Variables

Most skills require API credentials via environment variables:

| Skill | Required Env |
|-------|-------------|
| asana | `ASANA_API_KEY` |
| front | `FRONT_API_TOKEN` |
| google-workspace | `GOOGLE_WORKSPACE_SERVICE_ACCOUNT_URL` |
| notion | `NOTION_API_KEY` |
| pipedrive | `PIPEDRIVE_API_TOKEN` |

## Creating Skills

Each skill follows the [Agent Skills spec](https://agentskills.io/specification):

```
skill-name/
├── SKILL.md          # Required — frontmatter + instructions
├── scripts/          # Optional — executable code
├── references/       # Optional — additional docs
└── assets/           # Optional — templates, schemas
```

## License

MIT
