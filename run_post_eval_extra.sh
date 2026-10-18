#!/usr/bin/env bash
# Post-A2 eval extras the watcher (run_post_a2_eval.sh) doesn't cover:
#   1) model_13900 on the TRAIN distribution — last clean ckpt before the
#      recurrence phase onset (~iter 13942); measures how much better it is
#      vs the in-phase final ckpt.
#   2) held-out task evals on all four eval ckpts (roadmap discipline #4).
# Waits for the GPU to free first, so it can be launched while the watcher is
# still running (evals interleave harmlessly — every eval is its own process
# and each summary is snapshotted per-ckpt immediately).
#
# Usage: nohup ./run_post_eval_extra.sh >> post_a2_eval_extra.log 2>&1 &
set -u
BASE=/home/nood/IsaacSimbot
LAB=$BASE/unitree_rl_lab
LOGROOT=$LAB/logs/rsl_rl/unitree_go2_velocity
LEG1_DIR=2026-10-17_05-28-33_A2_stairs_slope_ft   # model_8700.pt = leg1 end
RESUME_DIR=2026-10-17_18-41-04_A2_stairs_slope_ft # resume run

source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
cd "$LAB"
PY="$CONDA_PREFIX/bin/python"
export OMNI_KIT_ACCEPT_EULA=YES PYTHONFAULTHANDLER=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8

# 1) sequence after the watcher: wait for its done marker (4h cap, then proceed
# anyway — the GPU-free check below still protects against overlap).
WLOG=$BASE/post_a2_eval.log
t0=$SECONDS
while ! grep -q "post-A2 eval done" "$WLOG" 2>/dev/null; do
    if [ $((SECONDS - t0)) -gt 14400 ]; then
        echo "[$(date +%T)] watcher done-marker not seen after 4h, proceeding"
        break
    fi
    sleep 30
done

# 2) then wait for the GPU to actually be free
while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date +%T)] GPU busy, waiting 15s..."
    sleep 15
done
sleep 20   # let the driver release memory fully

run_eval() {  # run_eval <load_run> <ckpt> [extra eval_terrain args...]
    local load_run=$1 ckpt=$2; shift 2
    [ -f "$LOGROOT/$load_run/$ckpt" ] || { echo "[$(date +%T)] SKIP $load_run/$ckpt (missing)"; return 0; }
    echo "[$(date +%T)] === eval_terrain $* : run=$load_run ckpt=$ckpt ==="
    "$PY" scripts/rsl_rl/eval_terrain.py --headless --num_envs 1024 \
        --load_run "$load_run" --checkpoints "$ckpt" "$@"
    echo "[$(date +%T)] eval rc=$? for $load_run/$ckpt ($*)"
}

snap() {  # snap <load_run> <ckpt> <eval_tag>  — per-ckpt summary snapshot
    local s="$LOGROOT/$1/eval/eval_summary$3.csv"
    [ -f "$s" ] && cp "$s" "$LOGROOT/$1/eval/eval_summary$3_${2%.pt}.csv"
}

latest=$(basename "$(ls -v "$LOGROOT/$RESUME_DIR"/model_*.pt | tail -1)")
echo "[$(date +%T)] latest resume ckpt: $latest"

# 1) train-distribution eval of model_13900 (pre-recurrence last clean)
run_eval "$RESUME_DIR" model_13900.pt --task Unitree-Go2-Velocity-Stairs
snap "$RESUME_DIR" model_13900.pt ""

# 2) held-out task eval for the full eval set
for spec in "$LEG1_DIR model_8700.pt" "$RESUME_DIR model_10600.pt" \
            "$RESUME_DIR model_13900.pt" "$RESUME_DIR $latest"; do
    set -- $spec
    run_eval "$1" "$2" --task Unitree-Go2-Velocity-Heldout \
        --experiment_name unitree_go2_velocity --eval_tag _heldout
    snap "$1" "$2" "_heldout"
done

# 3) analyze every summary in both run dirs (train-dist + heldout)
for d in "$LEG1_DIR" "$RESUME_DIR"; do
    for s in "$LOGROOT/$d"/eval/eval_summary*.csv; do
        [ -f "$s" ] || continue
        echo "[$(date +%T)] === analyze_eval: $s ==="
        python3 scripts/rsl_rl/analyze_eval.py "$s"
    done
done
echo "[$(date +%T)] extra eval done."
