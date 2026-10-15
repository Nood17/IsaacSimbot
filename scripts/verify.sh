#!/bin/bash
echo "===== 1. USD magic check (should be PXR-USDC) ====="
find /home/administrator/仿真/unitree_model -name "*.usd" -size +1k | while read f; do
  magic=$(head -c 8 "$f")
  size=$(stat -c%s "$f")
  echo "$size  [$magic]  $f"
done

echo ""
echo "===== 2. git repo integrity (fsck) ====="
for repo in IsaacLab unitree_rl_lab unitree_ros unitree_model; do
  d="/home/administrator/仿真/$repo"
  if [ -d "$d/.git" ]; then
    echo "--- $repo ---"
    git -C "$d" fsck --no-progress 2>&1 | head -5
    echo "files: $(git -C "$d" ls-files | wc -l), HEAD: $(git -C "$d" rev-parse --short HEAD)"
  fi
done

echo ""
echo "===== 3. unitree_rl_lab structure ====="
ls /home/administrator/仿真/unitree_rl_lab/
echo "---"
ls /home/administrator/仿真/unitree_rl_lab/source/unitree_rl_lab/unitree_rl_lab/ 2>/dev/null

echo ""
echo "===== 4. IsaacLab structure ====="
ls /home/administrator/仿真/IsaacLab/source/ 2>/dev/null

echo ""
echo "===== 5. isaacsim pip progress ====="
tail -5 /tmp/isaacsim_pip.log 2>/dev/null || echo "no log file"
