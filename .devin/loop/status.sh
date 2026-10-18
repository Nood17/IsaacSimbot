#!/usr/bin/env bash
LOOP=/home/nood/IsaacSimbot/.devin/loop
echo "=== state.json ==="; cat "$LOOP/state.json" 2>/dev/null || echo "(none)"
echo; echo "=== timers ==="; systemctl --user list-timers 'bmmms-*' --no-pager 2>/dev/null
echo; echo "=== iteration service ==="; systemctl --user status bmmms-iteration.service --no-pager 2>/dev/null | head -5
echo; echo "=== screens ==="; screen -ls 2>/dev/null | grep bmmms || echo "(no bmmms screens)"
echo; echo "=== STATUS.md tail ==="; tail -15 "$LOOP/STATUS.md" 2>/dev/null
echo; echo "=== latest round log tail ==="; latest=$(ls -t "$LOOP"/logs/round-*.log 2>/dev/null | head -1); [ -n "$latest" ] && tail -15 "$latest" || echo "(no rounds yet)"
[ -f "$LOOP/STOP" ] && echo; echo "!! STOP file present - loop is halted"
