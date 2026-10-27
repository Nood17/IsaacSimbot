#!/usr/bin/env bash
# A3 Stage A teacher training launcher.
# Waits for the post-A2 eval chain (go2-eval-watcher2) to finish and the GPU to
# be free, then starts the height-scanner teacher from the warm-start ckpt
# (warm_9900_scan.pt, actor obs expanded 235->1170 by expand_actor_obs.py).
#
# Usage: systemd-run --user --unit=go2-a3-teacher bash /home/ubuntu/nood/run_a3_teacher.sh
set -u
BASE=/home/ubuntu/nood
LAB=$BASE/unitree_rl_lab
LOG=$BASE/go2_a3_teacher.log

# 1) wait for the eval chain to finish
while systemctl --user is-active --quiet go2-eval-watcher2 2>/dev/null; do
    sleep 30
done
echo "[$(date +%T)] eval chain done; waiting for GPU to free..."

# 2) wait until no compute apps hold the GPU
while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date +%T)] GPU busy, waiting 15s..."
    sleep 15
done
sleep 20   # let the driver release memory fully

# 3) launch Stage A teacher (height scanner, privileged obs)
source ~/miniconda3/etc/profile.d/conda.sh
conda activate /home/ubuntu/nood/env_isaaclab   # activate.d exports LD_LIBRARY_PATH — required for PhysX GPU
cd "$LAB"
echo "[$(date +%T)] launching A3 teacher: Unitree-Go2-Velocity-Scan-Stairs num_envs=2048 resume ft_init/warm_9900_scan.pt max_iterations=8000"
echo "[$(date +%T)] log: $LOG"
export OMNI_KIT_ACCEPT_EULA=YES PYTHONFAULTHANDLER=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8
"$CONDA_PREFIX/bin/python" scripts/rsl_rl/train.py --headless \
    --task Unitree-Go2-Velocity-Scan-Stairs --num_envs 2048 \
    --run_name A3_teacher --resume --load_run ft_init --checkpoint warm_9900_scan.pt \
    --max_iterations 8000 >> "$LOG" 2>&1
rc=$?
echo "[$(date +%T)] A3 teacher exited rc=$rc"
