#!/usr/bin/env bash
# Install the bmmms loop units and arm the relay + watchdog timers.
# usage: install.sh [now | "YYYY-MM-DD HH:MM"]
#   now        -> start first round immediately (default)
#   <datetime> -> arm a one-shot timer for the first round instead
set -e
LOOP=/home/nood/IsaacSimbot/.devin/loop
UDIR=$HOME/.config/systemd/user
mkdir -p "$UDIR"
cp "$LOOP"/units/bmmms-*.service "$LOOP"/units/bmmms-*.timer "$UDIR/"
systemctl --user daemon-reload
systemctl --user enable bmmms-iteration.timer bmmms-watchdog.timer
systemctl --user start bmmms-iteration.timer bmmms-watchdog.timer
rm -f "$LOOP/STOP"

when=${1:-now}
if [ "$when" = "now" ]; then
    systemctl --user start bmmms-iteration.service
    echo "first round started now; relay armed (OnUnitInactiveSec=3min)"
else
    # one-shot timer for the first round; the relay timer takes over after it
    cat > "$UDIR/bmmms-first.service" <<EOF
[Unit]
Description=First bmmms iteration round (scheduled)
[Service]
Type=oneshot
ExecStart=$LOOP/run-iteration.sh
EOF
    cat > "$UDIR/bmmms-first.timer" <<EOF
[Unit]
Description=Scheduled first bmmms round
[Timer]
OnCalendar=$when
Unit=bmmms-first.service
[Install]
WantedBy=timers.target
EOF
    systemctl --user daemon-reload
    systemctl --user enable --now bmmms-first.timer
    echo "first round scheduled at '$when'; relay armed"
fi
systemctl --user list-timers 'bmmms-*' --no-pager
