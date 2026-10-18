#!/usr/bin/env bash
# Termination protocol: drop the STOP file, disarm timers, kill any live round.
LOOP=/home/nood/IsaacSimbot/.devin/loop
touch "$LOOP/STOP"
systemctl --user stop bmmms-iteration.timer bmmms-watchdog.timer bmmms-first.timer 2>/dev/null
for s in $(screen -ls 2>/dev/null | awk '/bmmms-/{print $1}'); do
    screen -S "$s" -X quit
done
systemctl --user kill bmmms-iteration.service 2>/dev/null
echo "## $(date -Is) | loop stopped (STOP file set, timers stopped)" >> "$LOOP/STATUS.md"
echo "stopped. resume with: rm $LOOP/STOP && systemctl --user start bmmms-iteration.timer bmmms-watchdog.timer bmmms-iteration.service"
