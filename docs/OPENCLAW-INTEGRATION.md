# OpenClaw Integration (for this repo)

Point OpenClaw to this repository as an extra skills directory:

```json5
// ~/.openclaw/openclaw.json
{
  skills: {
    load: {
      extraDirs: ["/Users/everestguerra/Dev/skills"],
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

Notes:
- Workspace skills still take precedence over extraDirs.
- Use this when you want this repo to act as a shared curated skill pack.
- Restart session after major changes (or rely on watcher refresh).
