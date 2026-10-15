#!/bin/bash
PID=$1
echo "=== status ==="
grep -iE "State|Threads|VmRSS" /proc/$PID/status 2>/dev/null
echo "=== thread names (top by cpu) ==="
top -b -n1 -H -p $PID 2>/dev/null | tail -10
echo "=== wchan of busy threads ==="
for t in /proc/$PID/task/*/stat; do
  read -r line < "$t" || continue
  comm=$(echo "$line" | sed 's/.*(\(.*\)).*/\1/')
  wchan=$(cat "$(dirname $t)/wchan" 2>/dev/null)
  echo "$comm wchan=$wchan"
done | sort | uniq -c | sort -rn | head -15
echo "=== open fds of interest ==="
ls -l /proc/$PID/fd 2>/dev/null | grep -vE "pipe|null|urandom|socket" | tail -10
