# Skills Governance

## 1) Trust levels

### Level A — First-party (default trusted)
Skills authored and maintained by Stitchi.

### Level B — Reviewed third-party
External skill copied into this repo **after** review.

### Level C — Unreviewed external
Never committed directly to this repo.

## 2) Review checklist (required for Level B)

- [ ] Read full `SKILL.md`
- [ ] Review any `scripts/`, `references/`, and `assets/`
- [ ] Check for network calls, package installs, destructive commands
- [ ] Confirm no hidden prompts for secret exfiltration
- [ ] Record source repo + commit/tag + date
- [ ] Add/confirm license compatibility
- [ ] Add catalog entry with owner and status

## 3) Change policy

- **No behavior changes** without explicit intent and version bump
- Metadata additions are allowed (author, version, compatibility, provenance)
- Keep each skill scoped to one job
- Prefer instruction-only skills unless scripts are truly needed

## 4) Release gates

Before merge:

1. `python3 scripts/skill_audit.py`
2. Confirm catalog entry exists/updated
3. Confirm changelog note in PR/commit

## 5) Security defaults

- Treat third-party skills as untrusted until reviewed
- Keep risky skills explicit-invocation in consuming clients
- Use sandboxed execution where possible for script-heavy skills
