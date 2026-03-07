# Skills

Portable [Agent Skills](https://agentskills.io) for Stitchi's tool integrations.

This repo now includes a lightweight architecture for governance + versioning without changing skill behavior.

- Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Governance policy: [docs/GOVERNANCE.md](./docs/GOVERNANCE.md)
- Release/versioning guide: [docs/RELEASES.md](./docs/RELEASES.md)
- OpenClaw wiring: [docs/OPENCLAW-INTEGRATION.md](./docs/OPENCLAW-INTEGRATION.md)
- Skill catalog: [catalog/skills.yaml](./catalog/skills.yaml)
- Approved upstream sources: [catalog/sources.yaml](./catalog/sources.yaml)

## Install

```bash
# All skills
npx skills add stitchi-co/skills --all

# Specific skill
npx skills add stitchi-co/skills --skill pipedrive
```

Works with Claude Code, OpenClaw, Cursor, Codex, and [40+ other agents](https://skills.sh).

## Architecture Ops

```bash
# Validate skill structure + catalog integrity
python3 scripts/skill_audit.py
# or
make audit

# Import a single upstream skill with pinned commit (review required)
scripts/import_upstream_skill.sh <repo_url> <git_ref> <source_skill_path> <target_dir_name>
```

## Skills

| Skill | Description |
|-------|-------------|
| [asana](./asana/) | Asana project management — tasks, projects, sections, search |
| [front](./front/) | Front helpdesk — conversations, inboxes, teammates, tags |
| [google-workspace](./google-workspace/) | Google Workspace — Calendar, Drive (service account) |
| [notion](./notion/) | Notion — pages, databases, blocks |
| [pipedrive](./pipedrive/) | Pipedrive CRM — deals, contacts, orgs, activities, pipelines |
| [skill-creator](./skill-creator/) | Build and improve Agent Skills with eval loops and benchmark tooling |

## Environment Variables

Most skills require API credentials via environment variables:

| Skill | Required Env |
|-------|-------------|
| asana | `ASANA_API_KEY` |
| front | `FRONT_API_TOKEN` |
| google-workspace | `GOOGLE_WORKSPACE_SERVICE_ACCOUNT_URL` |
| notion | `NOTION_API_KEY` |
| pipedrive | `PIPEDRIVE_API_TOKEN` |
| skill-creator | *(none required by default; uses local Python scripts for eval tooling)* |

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
