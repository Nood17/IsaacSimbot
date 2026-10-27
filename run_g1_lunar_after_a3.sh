#!/usr/bin/env bash
# G1 lunar-surface training launcher (native Ubuntu workspace).
# Waits for the currently running train.py (A3 teacher) to finish and the GPU
# to be free, then trains G1-29dof on real LOLA-DEM lunar terrain
# (100% lunar_dem, uniform difficulty band ~12deg, NO difficulty curriculum,
# lunar gravity 1.62 m/s^2). Task: Unitree-G1-29dof-Velocity-LunarSurface.
#
# Usage: setsid nohup bash /home/ubuntu/nood/run_g1_lunar_after_a3.sh > /tmp/g1_lunar_launch.log 2>&1 &
set -u
BASE=/home/ubuntu/nood
LAB=$BASE/unitree_rl_lab
LOG=$LAB/logs/g1_lunar_console.log

echo "[$(date +%T)] waiting for current train.py to exit..."
while pgrep -f "rsl_rl/train.py" > /dev/null; do
    sleep 30
done
echo "[$(date +%T)] trainer exited; waiting for GPU to free..."

while nvidia-smi --query-compute-apps=pid --format=csv,noheader 2>/dev/null | grep -q .; do
    echo "[$(date +%T)] GPU busy, waiting 15s..."
    sleep 15
done
sleep 20   # let the driver release memory fully

source ~/miniconda3/etc/profile.d/conda.sh
conda activate /home/ubuntu/nood/env_isaaclab
cd "$LAB"
echo "[$(date +%T)] launching G1 lunar: Unitree-G1-29dof-Velocity-LunarSurface num_envs=4096 max_iterations=15000"
echo "[$(date +%T)] log: $LOG"
export OMNI_KIT_ACCEPT_EULA=YES PYTHONFAULTHANDLER=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8
"$CONDA_PREFIX/bin/python" scripts/rsl_rl/train.py --headless \
    --task Unitree-G1-29dof-Velocity-LunarSurface --num_envs 4096 \
    --run_name g1_lunar_real --max_iterations 15000 >> "$LOG" 2>&1
rc=$?
echo "[$(date +%T)] G1 lunar exited rc=$rc"
