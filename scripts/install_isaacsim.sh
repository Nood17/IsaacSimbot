#!/bin/bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate /home/ubuntu/nood/env_isaaclab
export TMPDIR=/home/ubuntu/nood/.pip_tmp
for i in 1 2 3 4 5 6 7 8 9 10; do
  echo "===== pip attempt $i ====="
  pip install "isaacsim[all,extscache]==5.1.0" \
    -i https://pypi.tuna.tsinghua.edu.cn/simple \
    --extra-index-url https://pypi.nvidia.com \
    --retries 30 --resume-retries 30 --timeout 60 && break
  echo "attempt $i failed, sleeping 10s"
  sleep 10
done
echo "===== DONE, verifying ====="
python -c "import isaacsim; print('isaacsim import OK')" 2>&1
