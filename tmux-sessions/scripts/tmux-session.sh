#!/usr/bin/env bash
# tmux-session.sh — Create and manage a tmux workspace with named windows on a shared socket.
# Usage:
#   tmux-session.sh create <session> [--dir <path>]
#   tmux-session.sh add-window <session> <name> [--dir <path>] [--panes <n>] [--layout <layout>]
#   tmux-session.sh list [<session>]
#   tmux-session.sh attach <session>
#   tmux-session.sh send <session> <window> [--pane <n>] -- <command...>
#   tmux-session.sh capture <session> <window> [--pane <n>] [--lines <n>]
#   tmux-session.sh kill <session>
#   tmux-session.sh kill-all
#   tmux-session.sh info <session>

set -euo pipefail

SOCKET_DIR="${OPENCLAW_TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/clawdbot-tmux-sockets}"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/clawdbot.sock"

usage() {
  cat <<'EOF'
tmux-session.sh — Manage tmux workspaces with named windows on a shared socket.

One session = one workspace. Multiple named windows inside, switchable with Ctrl+b <n>.

Commands:
  create <session> [--dir <path>]
      Create a new session (first window is named "main" by default).

  add-window <session> <window-name> [options]
      Add a named window to an existing session.
      --dir <path>             Working directory (default: ~)
      --panes <n>              Number of panes (1-4, default: 1)
      --layout <layout>        tiled, even-horizontal, even-vertical,
                               main-horizontal, main-vertical (default: tiled)

  list [<session>]             List sessions, or windows/panes for a session.
  attach <session>             Print the attach command for your terminal.
  send <session> <window> [--pane <n>] -- <cmd>
                               Send a command to a window pane.
  capture <session> <window> [--pane <n>] [--lines <n>]
                               Capture pane output (default: 200 lines).
  kill <session>               Kill a session.
  kill-all                     Kill all sessions on the socket.
  info <session>               Show session details.

Navigate windows:
  Ctrl+b 1/2/3   Jump to window by number
  Ctrl+b n/p     Next/previous window
  Ctrl+b w       Window picker

Socket: $SOCKET_DIR/clawdbot.sock
EOF
  exit 0
}

die() { echo "ERROR: $*" >&2; exit 1; }

tmx() { tmux -S "$SOCKET" "$@"; }

resolve_dir() {
  local d="${1/#\~/$HOME}"
  [[ -d "$d" ]] || die "Directory not found: $d"
  echo "$d"
}

cmd_create() {
  local name="" dir="$HOME"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dir)  dir="$2"; shift 2 ;;
      -*)     die "Unknown option: $1" ;;
      *)      [[ -z "$name" ]] && name="$1" || die "Unexpected arg: $1"; shift ;;
    esac
  done

  [[ -z "$name" ]] && die "Session name required."
  tmx has-session -t "$name" 2>/dev/null && die "Session '$name' already exists."
  dir=$(resolve_dir "$dir")

  tmx new-session -d -s "$name" -n "main" -c "$dir"

  echo "✅ Session '$name' created (window: main, dir: $dir)"
  echo ""
  echo "Add windows:  tmux-session.sh add-window $name <name> --dir <path>"
  echo "Attach:       tmx attach -t $name"
}

cmd_add_window() {
  local session="" winname="" dir="$HOME" panes=1 layout="tiled"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dir)    dir="$2"; shift 2 ;;
      --panes)  panes="$2"; shift 2 ;;
      --layout) layout="$2"; shift 2 ;;
      -*)       die "Unknown option: $1" ;;
      *)
        if [[ -z "$session" ]]; then session="$1"
        elif [[ -z "$winname" ]]; then winname="$1"
        else die "Unexpected arg: $1"
        fi
        shift ;;
    esac
  done

  [[ -z "$session" ]] && die "Session name required."
  [[ -z "$winname" ]] && die "Window name required."
  [[ "$panes" =~ ^[1-4]$ ]] || die "Panes must be 1-4"
  tmx has-session -t "$session" 2>/dev/null || die "Session '$session' not found."
  dir=$(resolve_dir "$dir")

  tmx new-window -t "$session" -n "$winname" -c "$dir"

  local i
  for (( i=2; i<=panes; i++ )); do
    tmx split-window -t "${session}:${winname}" -c "$dir"
  done

  if [[ "$panes" -gt 1 ]]; then
    tmx select-layout -t "${session}:${winname}" "$layout" 2>/dev/null || true
  fi

  echo "✅ Window '$winname' added to '$session' ($panes pane(s), layout: $layout, dir: $dir)"
}

cmd_list() {
  local session="${1:-}"

  if [[ -n "$session" ]]; then
    tmx has-session -t "$session" 2>/dev/null || die "Session '$session' not found."
    echo "Session: $session"
    echo ""
    echo "Windows:"
    tmx list-windows -t "$session" -F '  #{window_index}: #{window_name} (#{window_panes} panes)'
    echo ""
    echo "Panes:"
    tmx list-panes -t "$session" -a -F '  #{window_name}.#{pane_index}: #{pane_current_path}'
  else
    if ! tmx list-sessions 2>/dev/null; then
      echo "No active sessions."
      return
    fi
    echo ""
    echo "Socket: $SOCKET"
  fi
}

cmd_attach() {
  local name="${1:?Session name required}"
  tmx has-session -t "$name" 2>/dev/null || die "Session '$name' not found."
  echo "Run in your terminal:"
  echo ""
  echo "  tmx attach -t $name"
  echo ""
  echo "Window navigation: Ctrl+b 1/2/3 | Ctrl+b n/p | Ctrl+b w"
}

cmd_send() {
  local session="" window="" pane="" cmd_args=()
  local parsing_cmd=false

  while [[ $# -gt 0 ]]; do
    if $parsing_cmd; then
      cmd_args+=("$1"); shift; continue
    fi
    case "$1" in
      --)       parsing_cmd=true; shift ;;
      --pane)   pane="$2"; shift 2 ;;
      -*)       die "Unknown option: $1" ;;
      *)
        if [[ -z "$session" ]]; then session="$1"
        elif [[ -z "$window" ]]; then window="$1"
        else die "Unexpected arg: $1"
        fi
        shift ;;
    esac
  done

  [[ -z "$session" ]] && die "Session name required."
  [[ -z "$window" ]] && die "Window name required."
  [[ ${#cmd_args[@]} -eq 0 ]] && die "Command required after --"

  local target="${session}:${window}"
  [[ -n "$pane" ]] && target="${target}.${pane}"

  local cmd_str="${cmd_args[*]}"
  tmx send-keys -t "$target" -l -- "$cmd_str"
  tmx send-keys -t "$target" Enter
  echo "✅ Sent to $target: $cmd_str"
}

cmd_capture() {
  local session="" window="" pane="" lines=200

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --pane)   pane="$2"; shift 2 ;;
      --lines)  lines="$2"; shift 2 ;;
      -*)       die "Unknown option: $1" ;;
      *)
        if [[ -z "$session" ]]; then session="$1"
        elif [[ -z "$window" ]]; then window="$1"
        else die "Unexpected arg: $1"
        fi
        shift ;;
    esac
  done

  [[ -z "$session" ]] && die "Session name required."
  [[ -z "$window" ]] && die "Window name required."

  local target="${session}:${window}"
  [[ -n "$pane" ]] && target="${target}.${pane}"

  tmx capture-pane -p -J -t "$target" -S "-${lines}"
}

cmd_kill() {
  local name="${1:?Session name required}"
  tmx has-session -t "$name" 2>/dev/null || die "Session '$name' not found."
  tmx kill-session -t "$name"
  echo "✅ Session '$name' killed."
}

cmd_kill_all() {
  if tmx list-sessions &>/dev/null; then
    tmx kill-server
    echo "✅ All sessions killed."
  else
    echo "No active sessions."
  fi
}

cmd_info() {
  local name="${1:?Session name required}"
  tmx has-session -t "$name" 2>/dev/null || die "Session '$name' not found."

  echo "Session: $name"
  echo "Socket:  $SOCKET"
  echo ""
  echo "Windows:"
  tmx list-windows -t "$name" -F '  #{window_index}: #{window_name} (#{window_panes} panes)'
  echo ""
  echo "Panes:"
  tmx list-panes -t "$name" -F '  #{window_name}.#{pane_index}: #{pane_width}x#{pane_height} #{pane_current_path}'
  echo ""
  echo "Attach:  tmx attach -t $name"
  echo "Navigate: Ctrl+b 1/2/3 | Ctrl+b n/p | Ctrl+b w"
}

# Main
[[ $# -eq 0 ]] && usage

cmd="$1"; shift
case "$cmd" in
  create)     cmd_create "$@" ;;
  add-window) cmd_add_window "$@" ;;
  list)       cmd_list "$@" ;;
  attach)     cmd_attach "$@" ;;
  send)       cmd_send "$@" ;;
  capture)    cmd_capture "$@" ;;
  kill)       cmd_kill "$@" ;;
  kill-all)   cmd_kill_all ;;
  info)       cmd_info "$@" ;;
  help|-h|--help) usage ;;
  *)          die "Unknown command: $cmd. Run with --help for usage." ;;
esac
