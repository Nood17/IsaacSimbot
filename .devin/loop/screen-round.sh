#!/usr/bin/env bash
# Inner round wrapper: runs a command inside screen, streams filtered output to
# the round log, and writes the command's exit code to an rc file.
# usage: screen-round.sh <logfile> <rcfile> <cmd...>
set -o pipefail
log=$1; rcfile=$2; shift 2
"$@" 2>&1 \
    | sed -u -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' -e 's/\x1b\][^\x07]*\x07//g' -e 's/\r/\n/g' \
    | tee "$log"
echo "${PIPESTATUS[0]}" > "$rcfile"
