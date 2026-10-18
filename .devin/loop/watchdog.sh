#!/usr/bin/env bash
# Watchdog: if a round's log has been silent for SILENT_SEC while the iteration
# service is still active, kill the round -- the relay timer revives the loop.
set -u
REPO=/home/nood/IsaacSimbot
LOOP=$REPO/.devin/loop
LOGD=$LOOP/logs
SILENT_SEC=1500   # 25 min

[ -f "$LOOP/STOP" ] && exit 0

systemctl --user is-active --quiet bmmms-iteration.service || exit 0

latest=$(ls -t "$LOGD"/round-*.log 2>/dev/null | head -1)
[ -z "$latest" ] && exit 0

age=$(( $(date +%s) - $(stat -c%Y "$latest") ))
if [ "$age" -le "$SILENT_SEC" ]; then
    exit 0
fi

for s in $(screen -ls 2>/dev/null | awk '/bmmms-/{print $1}'); do
    screen -S "$s" -X quit
done
systemctl --user kill --signal=SIGKILL bmmms-iteration.service 2>/dev/null
echo "## $(date -Is) | watchdog | killed silent round (${age}s quiet): $latest" >> "$LOOP/STATUS.md"
exit 0
