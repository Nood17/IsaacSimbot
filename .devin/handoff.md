# Iteration Handoff

<!-- Agent 每轮把最新状态写到本文件顶部；使命完成时在最顶部单独写一行 MISSION-COMPLETE -->

## 状态 2026-10-15 晚（理论梳理 + 诊断新证据）

- 本轮做了什么：
  - 拉取 76a668e（两任务线重整）并完成知识对接：调研成果归档在 `docs/research/`，PPO/rsl_rl 学习路径已建立（Spinning Up PPO 页已存 `docs/research/spinningup_ppo.{html,pdf}`）
  - **诊断清单第 5 项有新证据**：`gait` 奖励开着但 `gait_phase` 观测被注释——奖励按节拍打分、策略看不到节拍，是 gait~0.51 停滞的强候选解释（详见 `docs/biped/状态-G1基线诊断.md` 新加小节）
  - **发现隐患**：`velocity_env_cfg.py` 工作区有未提交的 `sim.gravity=-1.62`，地球基线任务当前实为月面重力，恢复训练前必须删除
  - 配置实验（未提交）：G1 `history_length` 5→80（两个步态周期）、`push_robot` 间隔 (5,5)→(10,30)
  - 决策：A3 暂缓 DreamWaQ/GRU 隐式估计，默认 height scanner + teacher-student
  - 已推送：`docs/agent/Agent运行环境-Skills-MCP-环境配置需求.md`（77cd5c3）、lunar_panel 及月面任务归档（91fe05f）
- 验证结果：本轮无训练验证（任务 B 暂停中，只做文档与配置层面的整理）
- 下一步建议：
  1. 任务 A 按路线图跑 A0：`Unitree-Go2-Velocity` flat 基线
  2. 恢复任务 B 前：先删 `velocity_env_cfg.py` 的 `sim.gravity=-1.62`，再按诊断文档做 gait_phase A/B 对照
  3. push 走 `https://github.com` 直连（ghfast.top 代理无凭据）；可考虑 origin 拆分 fetch/push URL

## 状态 2026-10-15（项目方向重整）

- 本轮做了什么：
  - **项目重整为两条任务线**，文档全部归拢到 `I:\仿真\docs\`（Windows 侧 = `/mnt/i/仿真/docs/`）：
    - 任务 A（当前主线）：Go2 四足复杂地形训练，路线图 `docs/quadruped/路线图-Go2复杂地形训练.md`
    - 任务 B（暂停）：G1 lunar-grav-loco，诊断记录 `docs/biped/状态-G1基线诊断.md`
  - **停用了 iteration.timer / watchdog.timer**（`systemctl --user disable`）——旧使命指向 lunar-grav-loco，与新方向冲突；恢复迭代前需重开：`systemctl --user enable --now iteration.timer watchdog.timer`
  - 修订 `lunar-grav-loco/研究路径.md`：删除两篇论文/LunarLoco-Bench/VLA 等未验证前提的目标，降级为远期设想；当前唯一目标是 G1 平地真正站稳走稳
  - 全部调研报告（四足/双足/训练失败专项 + 旧版 + 低重力领域图）在 `I:\仿真\docs\research\`
- 验证结果：目录结构已建立，定时器已停用（list-timers 确认无 iteration/watchdog）
- 下一步建议：
  1. 按 `docs/quadruped/路线图-Go2复杂地形训练.md` 从 A0 开始：跑通 `Unitree-Go2-Velocity` flat 基线
  2. A1 放开 `go2/velocity_env_cfg.py` 第 36–56 行注释的地形模板
  3. G1 任务不要续训/不要上月面重力，直到完成 `docs/biped/状态-G1基线诊断.md` 的诊断清单

## 状态 2026-10-01 19:35

- 本轮做了什么：
  - M1 第一步：新增月面重力任务 `Unitree-G1-29dof-Velocity-Lunar`（新文件 `unitree_rl_lab/.../g1/29dof/lunar_velocity_env_cfg.py`，继承基线 RobotEnvCfg 仅改 `sim.gravity=(0,0,-1.62)`；基线任务未动）。
  - 补写了 `iteration-prompt.md` 空的使命字段（按 `研究路径.md`：M1→M4，验收=重力条件化单策略过 LunarLoco-Bench）。
  - 环境摸底：WSL2 + RTX 4070 Ti 12GB（非 5060）；conda `env_isaaclab` 已装 Isaac Sim 5.1 + IsaacLab 2.3.0 + unitree_rl_lab 0.2.1（均为 editable/pip install）。
  - research_state.json：literature 标记 completed，method 置 in_progress。
- 验证结果：
  - `list_envs.py` 可见新任务；smoke 训练 `logs/rsl_rl/unitree_g1_29dof_velocity_lunar/2026-10-01_19-23-30_lunar_smoke/`（num_envs=64，5 iter，EXIT 0），`params/env.yaml` 确认 `gravity=(0,0,-1.62)`，kit log 显示 PhysX 拿到 CUDA handle（GPU 物理生效）。
- 环境坑（后续每轮必读）：
  - 必须激活 `env_isaaclab` 或手动 `export LD_LIBRARY_PATH=~/仿真/wsl_lib_links:/usr/lib/wsl/lib:$CONDA_PREFIX/lib`，否则 PhysX GPU 初始化失败、进程在加载 USD 时**静默退出**（无 traceback）。
  - 非交互首次运行需 `OMNI_KIT_ACCEPT_EULA=YES`。
  - Vulkan/渲染在 WSL headless 下报 "No device could be created" 属正常，不影响 PhysX GPU 训练。
- 下一步建议：
  1. 地球基线 run `2026-10-01_13-02-31` 已训到 iter 7100/15000（`model_7100.pt`），续训：`train.py --headless --task Unitree-G1-29dof-Velocity --resume --load_run 2026-10-01_13-02-31 --checkpoint model_7100.pt`（参数名以 cli_args 为准），或检查 events 曲线判断是否已收敛够用。
  2. 起月面从零训练（全规模 num_envs，后台 nohup 长挂，注意用 setsid 防会话结束被杀）。
  3. 基线收敛后用其 ckpt 对 Lunar 任务做 `--resume` 微调 → 完成 M1 三策略对比。
  4. 之后做步态对比分析（步幅/前掌着地/CoM 前移）验证文献现象。

## 状态（初始）

- 迭代循环尚未开始第一轮。
