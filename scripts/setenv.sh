#!/usr/bin/env bash

# for Isaac Lab
export ISAACLAB_PATH=/home/ubuntu/nood/IsaacLab
alias isaaclab=/home/ubuntu/nood/IsaacLab/isaaclab.sh

# show icon if not running headless
export RESOURCE_NAME="IsaacSim"

# for unitree_rl_lab
source /home/ubuntu/nood/unitree_rl_lab/unitree_rl_lab.sh

# non-interactive EULA acceptance
export OMNI_KIT_ACCEPT_EULA=Yes

# WSL: PhysX dlopen("libcuda.so") / getDeviceInfo need unversioned driver libs;
# kit plugins need libGLU/libXt from conda env
export LD_LIBRARY_PATH=${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH}
