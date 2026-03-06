---
name: tmux-sessions
description: Create and manage tmux sessions on the fly. Use when asked to set up workspaces, terminal sessions, coding environments, or run parallel tasks in named tmux sessions. Covers create, list, attach, kill, send commands, and capture output.
---

# tmux-sessions

Manage tmux workspaces with named windows on a shared Clawdbot socket.

**Key concept:** One session = one workspace. Windows live inside the session and are switchable with `Ctrl+b 1/2/3`. No nesting issues — everything lives in one `tmux attach`.

Socket: `$OPENCLAW_TMUX_SOCKET_DIR/clawdbot.sock` (default: `$TMPDIR/clawdbot-tmux-sockets/clawdbot.sock`)

## Script

```
{baseDir}/scripts/tmux-session.sh
```

## Workflow

### 1. Create a session

```bash
{baseDir}/scripts/tmux-session.sh create <session> [--dir <path>]
```

### 2. Add named windows

```bash
{baseDir}/scripts/tmux-session.sh add-window <session> <name> [--dir <path>] [--panes <n>] [--layout <layout>]
```

- `--panes` — 1–4 (default: 1)
- `--layout` — `tiled`, `even-horizontal`, `even-vertical`, `main-horizontal`, `main-vertical`

### 3. User attaches in their terminal

```bash
tmx attach -t <session>
```

Navigate: `Ctrl+b 1/2/3` (by number), `Ctrl+b n/p` (next/prev), `Ctrl+b w` (picker)

## Other commands

```bash
{baseDir}/scripts/tmux-session.sh list [<session>]
{baseDir}/scripts/tmux-session.sh send <session> <window> [--pane <n>] -- <command>
{baseDir}/scripts/tmux-session.sh capture <session> <window> [--pane <n>] [--lines <n>]
{baseDir}/scripts/tmux-session.sh kill <session>
{baseDir}/scripts/tmux-session.sh kill-all
{baseDir}/scripts/tmux-session.sh info <session>
```

## Example: typical workspace

```bash
SCRIPT="{baseDir}/scripts/tmux-session.sh"
$SCRIPT create clawd --dir ~/Dev
$SCRIPT add-window clawd code --dir ~/Dev/stitchi-v2-ui-exploration
$SCRIPT add-window clawd bots --dir ~/Dev/bot-everest --panes 2 --layout even-horizontal
$SCRIPT add-window clawd overflow --dir ~/Dev
```

User runs: `tmx attach -t clawd`

## Tips

- Use descriptive window names (`code`, `bots`, `review`, etc.)
- `even-horizontal` is good for 2-pane side-by-side; `tiled` for 3–4 panes
- Use `send` + `capture` to run commands and check output without attaching
- The `tmx` alias (added to `~/.zshrc`) shortcuts `tmux -S <socket>`
