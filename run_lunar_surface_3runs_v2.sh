#!/usr/bin/env bash
# Supervisor v2 for the lunar-surface 3-run experiment.
# Runs three Unitree-G1-29dof-Velocity-LunarSurface trainings sequentially,
# each with a 15000-iteration budget on lunar-surface terrain:
#   1) lsurface_scratch   from scratch                          -> final model_14999.pt
#   2) lsurface_finetune  resume init_lunar_ft/model_17998.pt   -> final model_32997.pt
#   3) lsurface_earth     resume init_earth/model_14999_ft.pt   -> final model_29998.pt
#
# rsl_rl note: --max_iterations N with --resume means "train until
# current_iter + N", so we pass remaining = target - iter + 1.
#
# Features vs v1:
#  - per-run completion check against the correct final iteration number
#  - partial-resume: picks up the latest checkpoint in any *_<run_name> dir
#  - waits until the GPU is actually free before each launch
#  - exits rc=1 if any run failed (loop sessions can detect failure)
set -u
BASE=/home/nood/IsaacSimbot
LAB=$BASE/unitree_rl_lab
LOGROOT=$LAB/logs/rsl_rl/unitree_g1_29dof_velocity_lunarsurface
OLDLOG=$LAB/logs/rsl_rl/unitree_g1_29dof_velocity
TASK=Unitree-G1-29dof-Velocity-LunarSurface
NEW_ITERS=15000

# --- stage init checkpoints -------------------------------------------------
mkdir -p "$LOGROOT/init_lunar_ft" "$LOGROOT/init_earth"
cp -n "$OLDLOG/2026-10-05_07-15-52/model_17998.pt" "$LOGROOT/init_lunar_ft/model_17998.pt"
cp -n "$OLDLOG/2026-10-03_10-25-34/model_14999_ft.pt" "$LOGROOT/init_earth/model_14999_ft.pt"

# --- sanity: DEM crops must be in place -------------------------------------
waited=0
until compgen -G "$LAB/source/unitree_rl_lab/unitree_rl_lab/assets/lunar_dem/*.npy" >/dev/null; do
    if [ $waited -ge 3600 ]; then
        echo "[FATAL] no DEM crops under assets/lunar_dem after 60min -- run prepare_dem_crops.py" >&2
        exit 1
    fi
    echo "[$(date +%T)] waiting for DEM crops..."
    sleep 120; waited=$((waited+120))
done

source ~/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
cd "$LAB"

wait_gpu_free() {
    while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
        echo "[$(date +%T)] GPU busy, waiting 60s..."
        sleep 60
    done
    sleep 30   # let the driver release memory fully
}

# latest_ckpt <run_name> <init_dir> <init_file> <init_iter>
# prints "<load_run_dir> <ckpt_file> <iter>" = best checkpoint for the run:
# the init checkpoint, or any higher-iteration model_NNNNN.pt in *_<run_name> dirs.
latest_ckpt() {
    local run_name=$1 init_dir=$2 init_file=$3 init_iter=$4
    local best_iter=$init_iter best_dir="" best_file=""
    if [ -n "$init_file" ] && [ -f "$init_dir/$init_file" ]; then
        best_dir=$(basename "$init_dir"); best_file=$init_file
    fi
    local d f n
    for d in "$LOGROOT"/*_"${run_name}"; do
        [ -d "$d" ] || continue
        for f in "$d"/model_*.pt; do
            [ -f "$f" ] || continue
            n=${f##*/model_}; n=${n%.pt}
            [ "$n" -eq "$n" ] 2>/dev/null || continue   # skip non-numeric like model_14999_ft.pt
            if [ "$n" -gt "$best_iter" ]; then
                best_iter=$n; best_dir=$(basename "$d"); best_file=$(basename "$f")
            fi
        done
    done
    echo "$best_dir $best_file $best_iter"
}

FAILED=""

# run_train <name> <run_name> <init_dir> <init_file> <init_iter> [extra args...]
# init_iter=-1 + init_file="" means: no init checkpoint, train from scratch.
run_train() {
    local name=$1 run_name=$2 init_dir=$3 init_file=$4 init_iter=$5; shift 5
    local target=$((init_iter + NEW_ITERS - 1))
    [ "$init_iter" -lt 0 ] && target=$((NEW_ITERS - 1))

    read -r ck_dir ck_file ck_iter < <(latest_ckpt "$run_name" "$init_dir" "$init_file" "$init_iter")

    if [ "$ck_iter" -ge "$target" ]; then
        echo "[$(date +%T)] === $name already complete (iter $ck_iter >= target $target), skipping ==="
        return 0
    fi

    local extra=()
    if [ -n "$ck_file" ]; then
        local remaining=$((target - ck_iter + 1))
        echo "[$(date +%T)] === resuming $name from $ck_dir/$ck_file (iter $ck_iter), +$remaining iters to reach $target ==="
        extra=(--resume --load_run "$ck_dir" --checkpoint "$ck_file" --max_iterations "$remaining")
    else
        echo "[$(date +%T)] === starting $name from scratch, target iter $target ==="
        extra=(--max_iterations "$NEW_ITERS")
    fi

    wait_gpu_free
    echo "[$(date +%T)] === launching $name ==="
    OMNI_KIT_ACCEPT_EULA=YES PYTHONFAULTHANDLER=1 \
        PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8 \
        ./unitree_rl_lab.sh -t --task "$TASK" --num_envs 4096 \
        --run_name "$run_name" "${extra[@]}" "$@" \
        > "$BASE/g1_${name}.log" 2>&1
    local rc=$?

    read -r _ _ new_iter < <(latest_ckpt "$run_name" "$init_dir" "$init_file" "$init_iter")
    if [ "$new_iter" -ge "$target" ]; then
        echo "[$(date +%T)] === $name COMPLETE (iter $new_iter) ==="
    else
        echo "[$(date +%T)] === $name FAILED rc=$rc (iter $new_iter < target $target) ==="
        FAILED="$FAILED $name"
    fi
    sleep 60
    return $rc
}

#                 name               run_name                init_dir              init_file            init_iter
run_train lsurface_scratch  lunar_surface_scratch  "$LOGROOT/nonexistent"  ""                    -1
run_train lsurface_finetune lunar_surface_finetune "$LOGROOT/init_lunar_ft" "model_17998.pt"      17998
run_train lsurface_earth    lunar_surface_earth    "$LOGROOT/init_earth"    "model_14999_ft.pt"   14999

if [ -n "$FAILED" ]; then
    echo "[$(date +%T)] DONE WITH FAILURES:$FAILED"
    exit 1
fi
echo "[$(date +%T)] ALL THREE RUNS DONE"
