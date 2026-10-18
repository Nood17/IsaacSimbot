#!/usr/bin/env bash
# One iteration round of the session-chained devin loop.
#
# - Maintains .devin/loop/state.json: {session_id, continue_count, round, last_rc}
# - New session:  devin -p --prompt-file <iteration-prompt.md>
# - Continue:     devin -r <session_id> -p -- "continue"
# - After MAX_CONT continues -> new session; a failed round also forces new session.
# - devin runs inside GNU screen (name bmmms-<ts>); stdout is filtered and tee'd
#   to logs/round-<ts>.log; exit code is passed back via logs/round-<ts>.rc.
set -uo pipefail

REPO=/home/nood/IsaacSimbot
LOOP=$REPO/.devin/loop
PROMPT=$REPO/.devin/iteration-prompt.md
STATE=$LOOP/state.json
STATUS=$LOOP/STATUS.md
LOGD=$LOOP/logs
LOCK=$LOOP/.lock
STOP=$LOOP/STOP

MAX_CONT=5                 # continuations per session before a fresh conversation
CONTINUE_PROMPT="continue" # per user spec; change here to alter in-round prompt
PERMISSION_MODE=dangerous  # unattended loop needs exec; tighten if desired

export PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
unset ACP_BACKEND   # poisons devin CLI auth when inherited from an IDE/ACP shell
mkdir -p "$LOGD"

# single-round guard
exec 9>"$LOCK"
flock -n 9 || exit 0

# termination protocol: STOP file => no-op
[ -f "$STOP" ] && exit 0

cd "$REPO" || exit 1

[ -f "$STATE" ] || echo '{"session_id": "", "continue_count": 0, "round": 0, "last_rc": 0}' > "$STATE"

# auth preflight: devin -p needs a logged-in CLI; idle until `devin auth login`
if devin auth status 2>&1 | grep -qi "not logged in"; then
    # log at most once per hour to avoid spam
    marker=$LOOP/.auth_warned
    if [ ! -f "$marker" ] || [ $(( $(date +%s) - $(stat -c%Y "$marker") )) -gt 3600 ]; then
        echo "## $(date -Is) | auth | devin CLI not logged in -- run \`devin auth login\`" >> "$STATUS"
        touch "$marker"
    fi
    exit 0
fi
rm -f "$LOOP/.auth_warned"

session_id=$(jq -r '.session_id // ""' "$STATE")
cont=$(jq -r '.continue_count // 0' "$STATE")
round=$(( $(jq -r '.round // 0' "$STATE") + 1 ))

ts=$(date +%Y%m%d-%H%M%S)
sname="bmmms-$ts"
roundlog=$LOGD/round-$ts.log
rcfile=$LOGD/round-$ts.rc

if [ -z "$session_id" ] || [ "$cont" -ge "$MAX_CONT" ]; then
    mode=new
    cmd=(devin -p --prompt-file "$PROMPT" --permission-mode "$PERMISSION_MODE" --respect-workspace-trust false)
else
    mode=continue
    cmd=(devin -r "$session_id" -p --permission-mode "$PERMISSION_MODE" --respect-workspace-trust false -- "$CONTINUE_PROMPT")
fi

echo "## $(date -Is) | round $round ($mode, session=${session_id:-none}, cont=$cont) | log=round-$ts.log" >> "$STATUS"

screen -dmS "$sname" "$LOOP/screen-round.sh" "$roundlog" "$rcfile" "${cmd[@]}"

# wait for the round to finish (watchdog may kill it -> rcfile still appears)
while [ ! -f "$rcfile" ]; do sleep 10; done
rc=$(cat "$rcfile" 2>/dev/null || echo 1)

# a 0 exit code isn't proof of success: devin prints "Error: ..." with rc 0
# only match CLI-level failure prefixes -- agent prose legitimately contains
# words like "traceback" when reporting on logs
failed=0
[ "$rc" != "0" ] && failed=1
grep -qiE "^Error:|not logged in|session.*not found|invalid session" "$roundlog" 2>/dev/null && failed=1

if [ "$mode" = new ]; then
    # capture the session we just created (most recent activity in this dir)
    new_id=$(devin list --format json 2>/dev/null | jq -r 'sort_by(.last_activity_at // "") | last | .id // empty')
    [ -n "$new_id" ] && session_id="$new_id"
    cont=0
else
    cont=$((cont + 1))
fi
[ "$failed" = 1 ] && cont=$MAX_CONT   # force a fresh session next round

jq -n --arg sid "$session_id" --argjson cont "$cont" --argjson round "$round" --argjson rc "$rc" \
    '{session_id: $sid, continue_count: $cont, round: $round, last_rc: $rc}' > "$STATE.tmp"
mv "$STATE.tmp" "$STATE"

echo "## $(date -Is) | round $round done | rc=$rc failed=$failed | session=$session_id cont=$cont" >> "$STATUS"
exit 0
