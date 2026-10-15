#!/bin/bash
cd /home/administrator/仿真/unitree_model || exit 1
BASE="https://hf-mirror.com/datasets/unitreerobotics/unitree_model/resolve/main"
files=(
"B2/usd/configuration/b2_description_base.usd"
"G1/23dof/usd/g1_23dof_rev_1_0/configuration/g1_23dof_rev_1_0_base.usd"
"G1/29dof/usd/g1_29dof_rev_1_0/configuration/g1_29dof_rev_1_0_base.usd"
"Go2/usd/configuration/go2_description_base.usd"
"Go2W/usd/configuration/go2w_description_base.usd"
"H1-2/h1_2/configuration/h1_2_base.usd"
"H1-2/h1_2_handless/configuration/h1_2_handless_base.usd"
"H1/h1/usd/configuration/h1_base.usd"
"H2/configuration/H2_dae_base.usd"
)
for f in "${files[@]}"; do
  echo ">>> $f"
  curl -sL --retry 3 --connect-timeout 15 -o "$f" "$BASE/$f"
done
find . -name "*_base.usd" -exec ls -la {} \;
