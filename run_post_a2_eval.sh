#!/usr/bin/env bash
# Post-A2 watcher: when the A2 resume train process exits, run per-terrain
# eval_terrain.py on selected checkpoints, then analyze_eval.py on each
# eval_summary.csv. Mirrors the lunar supervisor's wait_gpu_free pattern.
#
# Usage: nohup ./run_post_a2_eval.sh [TRAIN_PID] >> post_a2_eval.log 2>&1 &
set -u
BASE=/home/nood/IsaacSimbot
LAB=$BASE/unitree_rl_lab
LOGROOT=$LAB/logs/rsl_rl/unitree_go2_velocity
LEG1_DIR=2026-10-17_05-28-33_A2_stairs_slope_ft   # model_8700.pt = leg1 end
RESUME_DIR=2026-10-17_18-41-04_A2_stairs_slope_ft # resume run (instability onset ~10626)
TASK=Unitree-Go2-Velocity-Stairs
TRAIN_PID=${1:-7928}

source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
cd "$LAB"

# 1) wait for the training process to exit (skip if already gone)
if kill -0 "$TRAIN_PID" 2>/dev/null; then
    echo "[$(date +%T)] waiting for A2 train pid $TRAIN_PID to exit..."
    while kill -0 "$TRAIN_PID" 2>/dev/null; do sleep 60; done
fi
echo "[$(date +%T)] train pid $TRAIN_PID gone; waiting for GPU to free..."

# 2) wait until no compute apps hold the GPU (15s poll beats supervisor's 60s loop)
while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date +%T)] GPU busy, waiting 15s..."
    sleep 15
done
sleep 20   # let the driver release memory fully

run_eval() {
    local load_run=$1 ckpt=$2
    [ -f "$LOGROOT/$load_run/$ckpt" ] || { echo "[$(date +%T)] SKIP $load_run/$ckpt (missing)"; return 0; }
    echo "[$(date +%T)] === eval_terrain: run=$load_run ckpt=$ckpt ==="
    OMNI_KIT_ACCEPT_EULA=YES PYTHONFAULTHANDLER=1 \
        PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8 \
        "$CONDA_PREFIX/bin/python" scripts/rsl_rl/eval_terrain.py \
        --task "$TASK" --headless --num_envs 1024 \
        --load_run "$load_run" --checkpoints "$ckpt"
    echo "[$(date +%T)] eval rc=$? for $load_run/$ckpt"
    # eval_summary.csv is overwritten per invocation (eval_rows.csv appends):
    # snapshot per-ckpt so consecutive evals don't erase earlier summaries.
    local s="$LOGROOT/$load_run/eval/eval_summary.csv"
    [ -f "$s" ] && cp "$s" "$LOGROOT/$load_run/eval/eval_summary_${ckpt%.pt}.csv"
}

# 3) eval set: leg1 end (8700) + resume last-pre-onset (10600) + resume latest
run_eval "$LEG1_DIR" "model_8700.pt"
run_eval "$RESUME_DIR" "model_10600.pt"
latest=$(basename "$(ls -v "$LOGROOT/$RESUME_DIR"/model_*.pt | tail -1)")
run_eval "$RESUME_DIR" "$latest"

# 4) analyze every produced summary (snapshots + latest) against the roadmap gates
for d in "$LEG1_DIR" "$RESUME_DIR"; do
    for s in "$LOGROOT/$d"/eval/eval_summary*.csv; do
        [ -f "$s" ] || continue
        echo "[$(date +%T)] === analyze_eval: $s ==="
        python3 scripts/rsl_rl/analyze_eval.py "$s"
    done
done
echo "[$(date +%T)] post-A2 eval done."
