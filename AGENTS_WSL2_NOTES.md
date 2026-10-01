# 环境说明（WSL2 新机器，DESKTOP-9S36E5P）

## 环境就绪状态（2026-10-01）

- GPU: RTX 4070 Ti 12GB（Ada/sm_89），驱动 591.74，CUDA 13.1
- conda env `env_isaaclab`：python 3.11.16 + IsaacSim 5.1.0.0(pip) + IsaacLab @3c6e67bb (editable) + torch 2.7.0+cu128 + rsl-rl-lib 3.0.1
- unitree_rl_lab @4960b847 editable，路径已修正；5 个任务可用
- 冒烟测试：Unitree-G1-29dof-Velocity headless 跑通 10 iter，~28k steps/s，3.5s/iter，PhysX 在 GPU 上（CUDA ordinal 0）
- 项目数据已从 `github.com/Nood17/IsaacSimbot` 克隆：`~/仿真/.devin/skills/`（5 技能）、`~/仿真/lunar-grav-loco/`、`~/仿真/unitree_rl_lab/logs/`（Go2 早期 ckpt）

## 关键命令

```bash
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
# activate.d/setenv.sh 已自动导出 ISAACLAB_PATH/OMNI_KIT_ACCEPT_EULA/LD_LIBRARY_PATH
cd ~/仿真/unitree_rl_lab && ./unitree_rl_lab.sh -t --task Unitree-G1-29dof-Velocity --headless --num_envs 4096
```

## 本机特有的坑（WSL2）

1. **exec 工具外层会预展开 `$var`/`$(...)`**：复杂命令写脚本文件执行；文件工具的 `/tmp` = Windows `C:\tmp`，脚本放 `I:\仿真\`（WSL 内 `/mnt/i/仿真/`）。
2. **PhysX GPU 需要 `libcuda.so`（无版本号）**：WSL 的 `/usr/lib/wsl/lib` 只有 `libcuda.so.1`。已建 `~/仿真/wsl_lib_links/`（libcuda.so、libnvidia-ml.so 软链），setenv.sh 已加进 LD_LIBRARY_PATH。
3. **缺 X11/GLU 库**：`libneuray.so` 需要 `libGLU.so.1`，MaterialX 需要 `libXt.so.6`，已 conda 装 `libglu xorg-libxt`（无 sudo，apt 不可用），LD_LIBRARY_PATH 含 `$CONDA_PREFIX/lib`。
4. **gpu.foundation "No device could be created"**：WSL2 无 Vulkan RT，RTX 渲染器起不来——**不影响 headless RL 训练**（物理走 CUDA，渲染报错发生在退出阶段）。可视化播放（`-p`）需要宿主 Windows 端 Isaac Sim 或原生 Linux。
5. **egl_probe/flatdict**：需 g++（已 conda 装 `gxx_linux-64`）+ `CMAKE_POLICY_VERSION_MINIMUM=3.5`；flatdict 需 `setuptools==80.9.0` + `--no-build-isolation`。
6. **WSL DNS 间歇性失败**：pip 重试脚本带 `--resume-retries`；git 已配 `url."https://ghfast.top/https://github.com/".insteadOf`。
7. **pip 依赖会抢装 torch 新版**：用 `PIP_CONSTRAINT=/mnt/i/仿真/constraints.txt`（torch/torchvision/torchaudio/numpy pin）。
8. **文件工具的绝对路径是 Windows 命名空间**：`/home/...` 会落到 `C:\home\...`；写 WSL 内文件用 `\\wsl.localhost\Ubuntu\home\administrator\...`。

## 长线自主迭代循环（2026-10-01 已建）

仓库根 = `~/仿真`（WSL）。机制：systemd --user timer 接力 `devin -p` / `devin -r <id> -p "continue"`（同 session 续 ≤5 次后自动开新会话），watchdog 每 2min 巡检日志 ≥25min 静默则 kill 接力，handoff 出现 `MISSION-COMPLETE` 行则自停。

- 提示词：`~/仿真/.devin/iteration-prompt.md`（使命/收口/汇报规则，**使命段待填写**）
- handoff：`~/仿真/.devin/handoff.md`
- 脚本：`~/仿真/.devin/run-iteration.sh`、`watchdog.sh`（参数均可 env 覆盖：ITERATION_REPO/MAX_RESUME/TITLE_REGEX 等）
- 单元：`~/.config/systemd/user/{iteration,watchdog}.{service,timer}`，另有 kickstart.timer 模板（需先填 OnCalendar）
- 运行时：`~/仿真/.workspace/runtime/{scheduler.log,round-*.log,session-chain.env}`
- 依赖：devin v3000.11.3 已装 `~/.local/bin/devin`（**WSL 侧需单独 `devin auth login` 一次**），jq 1.8.1 静态二进制在 `~/.local/bin/jq`，linger 已开
- 注意：未登录时 `devin -p` 会挂死在登录 TUI——runner 已加 `devin auth status` 前置检查，未登录直接跳过本轮
