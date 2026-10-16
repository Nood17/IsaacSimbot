#!/bin/bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate /home/ubuntu/nood/env_isaaclab
export LD_LIBRARY_PATH=${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH}
export OMNI_KIT_ACCEPT_EULA=Yes
cd /home/ubuntu/nood/unitree_rl_lab
exec python scripts/rsl_rl/train.py --task Unitree-G1-29dof-Velocity --headless --max_iterations 10
