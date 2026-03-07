# Release & Versioning Guide

## SemVer for skills

- **MAJOR**: breaking behavior change
- **MINOR**: new capability, backward compatible
- **PATCH**: metadata/docs/small non-breaking improvements

## What counts as behavior change?

Any change to:
- `SKILL.md` instructions that alter execution behavior
- scripts under `scripts/`
- references that are explicitly part of execution flow

## Workflow

1. Update skill files (or metadata only)
2. Bump version in `catalog/skills.yaml`
3. Optionally mirror version in `SKILL.md` metadata
4. Run audit: `python3 scripts/skill_audit.py`
5. Commit with conventional message (`feat:`, `fix:`, `chore:`)

## Optional publishing (registry)

When publishing externally (e.g., ClawHub), publish from this curated repo state so versions and provenance stay aligned.
