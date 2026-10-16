#!/bin/bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate /home/ubuntu/nood/env_isaaclab
export TMPDIR=/home/ubuntu/nood/.pip_tmp
mkdir -p /home/ubuntu/nood/pip_wheels
for i in 1 2 3 4 5 6 7 8 9 10; do
  echo "===== torch download attempt $i ====="
  pip download torch==2.7.0 torchvision==0.22.0 \
    --index-url https://mirror.sjtu.edu.cn/pytorch-wheels/cu128 \
    -d /home/ubuntu/nood/pip_wheels \
    --retries 30 --resume-retries 30 --timeout 60 && break
  echo "attempt $i failed, sleeping 10s"
  sleep 10
done
ls -la /home/ubuntu/nood/pip_wheels/
