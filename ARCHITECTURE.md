# Skills Architecture (Dev/skills)

This repo is the **source-of-truth** for Stitchi-managed Agent Skills.

## Goals

- Keep skill behavior stable (no accidental prompt/script drift)
- Add predictable versioning + provenance
- Support safe adoption of third-party skills
- Enable repeatable publishing and updates

## Layout

```text
skills/
├── <skill-name>/                 # first-party skills (existing behavior)
├── catalog/
│   ├── skills.yaml               # inventory + ownership + status + version
│   └── sources.yaml              # approved upstream sources (for imports)
├── docs/
│   ├── GOVERNANCE.md             # review/approval policy
│   └── RELEASES.md               # versioning + release workflow
├── scripts/
│   ├── skill_audit.py            # frontmatter + structure checks
│   └── import_upstream_skill.sh  # controlled vendoring flow (no auto trust)
└── README.md
```

## Ownership model

- **First-party skills**: folders at repo root (`asana/`, `pipedrive/`, etc.)
- **Third-party imports**: only after review; tracked in `catalog/sources.yaml` and `catalog/skills.yaml`
- **Do not install unreviewed external skills directly into this repo**

## Versioning model

- Skill versions are tracked in `catalog/skills.yaml` (SemVer)
- Optional in-skill metadata (`metadata.version`) may mirror catalog version
- Any behavior change (instructions/scripts/references) requires version bump
- Metadata-only/documentation-only updates may use patch bumps

## Precedence in runtime (OpenClaw)

OpenClaw resolves skills in this order:

1. `<workspace>/skills` (highest)
2. `~/.openclaw/skills`
3. bundled skills (lowest)

This repository is intended to feed curated skills into one of those locations.

## Operational rule

When importing external skills, prefer this flow:

1. Inspect + pin source commit/tag
2. Vendor reviewed skill folder
3. Record provenance in `catalog/skills.yaml`
4. Run `python3 scripts/skill_audit.py`
5. Commit with a conventional message
