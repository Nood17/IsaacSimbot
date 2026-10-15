#!/bin/bash
SRC=/home/administrator/仿真/unitree_rl_lab/logs/rsl_rl/unitree_g1_29dof_velocity/2026-10-01_13-02-31
DST=/home/administrator/仿真/IsaacSimbot/unitree_rl_lab/logs/rsl_rl/unitree_g1_29dof_velocity/2026-10-01_13-02-31
mkdir -p "$DST"
cp "$SRC/model_6900.pt" "$SRC/model_7000.pt" "$SRC/model_7100.pt" "$DST/"
cp "$SRC"/events.out.tfevents.* "$DST/"
cp -r "$SRC/git" "$DST/" 2>/dev/null
ls -la "$DST"
du -sh "$DST"
echo "=== git status ==="
cd /home/administrator/仿真/IsaacSimbot && git status --short | head -20
