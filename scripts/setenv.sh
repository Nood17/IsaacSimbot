#!/usr/bin/env bash

# for Isaac Lab
export ISAACLAB_PATH=/home/administrator/仿真/IsaacLab
alias isaaclab=/home/administrator/仿真/IsaacLab/isaaclab.sh

# show icon if not running headless
export RESOURCE_NAME="IsaacSim"

# for unitree_rl_lab
source /home/administrator/仿真/unitree_rl_lab/unitree_rl_lab.sh

# non-interactive EULA acceptance
export OMNI_KIT_ACCEPT_EULA=Yes

# WSL: PhysX dlopen("libcuda.so") / getDeviceInfo need unversioned driver libs;
# kit plugins need libGLU/libXt from conda env
export LD_LIBRARY_PATH=/home/administrator/仿真/wsl_lib_links:/usr/lib/wsl/lib:${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH}
