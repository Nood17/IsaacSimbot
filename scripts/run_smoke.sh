#!/bin/bash
source /home/administrator/miniconda3/etc/profile.d/conda.sh
conda activate env_isaaclab
export LD_LIBRARY_PATH=/home/administrator/仿真/wsl_lib_links:/usr/lib/wsl/lib:${CONDA_PREFIX}/lib
export OMNI_KIT_ACCEPT_EULA=Yes
cd /home/administrator/仿真/unitree_rl_lab
exec python scripts/rsl_rl/train.py --task Unitree-G1-29dof-Velocity --headless --max_iterations 10
