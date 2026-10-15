# 仿真工作区

腿式机器人强化学习仿真工作区（WSL2 + Isaac Sim 5.1 + Isaac Lab + unitree_rl_lab）。

## 当前任务线（2026-10-15 重整）

本工作区现有**两条相互独立的任务线**，请勿混淆：

### 任务 A：四足机器狗复杂地形训练（当前主线）

- **目的**：通过 Go2 复杂地形 locomotion 积累"难任务仿真训练"的实践经验——奖励设计、课程、域随机化、checkpoint 评估。
- **动机**：双足 G1 基线的训练曲线看起来正常但实际行为不合格，说明缺的是"判断策略好坏"的实战能力，先在更简单/更稳的四足平台上练手。
- **代码位置**：`~/仿真/unitree_rl_lab`（Go2 velocity 任务，地形模板已在 `go2/velocity_env_cfg.py` 中备好注释）
- **路线图**：`docs/quadruped/路线图-Go2复杂地形训练.md`

### 任务 B：双足 G1 项目（暂停，待诊断）

- **状态**：地球重力基线 `Unitree-G1-29dof-Velocity` 已训约 7100 iter（700M steps），纸面指标正常（mean reward ≈42、几乎无摔倒），但**实际行为差**，且日志显示指令课程卡在 1 级、偏航跟踪差 —— 先诊断再决定是否继续。
- **代码位置**：`~/仿真/unitree_rl_lab`（G1 任务 + 已新增的 `lunar_velocity_env_cfg.py`）
- **研究文档**：`~/仿真/lunar-grav-loco/`（研究路径已按现状修订，远期目标已降级）
- **诊断记录**：`docs/biped/状态-G1基线诊断.md`

## 目录结构

```
I:\仿真\                        # Windows 侧工作区（= WSL /mnt/i/仿真）
├── README.md                   # 本文件
├── AGENTS.md                   # 环境说明与 WSL2 坑（引擎/agent 必读）
├── constraints.txt             # pip 版本约束（防依赖抢装 torch 新版）
├── docs/
│   ├── research/               # 调研报告（详见各文件头）
│   ├── quadruped/              # 任务 A 文档
│   └── biped/                  # 任务 B 文档
├── scripts/                    # 安装/运行/冒烟脚本（手动执行用）
└── logs/                       # 安装日志、冒烟日志、G1 地球基线训练日志

~/仿真/                         # WSL 侧代码主目录（两任务线共用）
├── unitree_rl_lab/             # 训练框架（editable install，G1/Go2/H1 任务）
├── IsaacLab/                   # Isaac Lab 源码（editable）
├── lunar-grav-loco/            # 任务 B 研究文档与文献
├── IsaacSimbot/                # GitHub 归档仓库（github.com/Nood17/IsaacSimbot）
├── unitree_model/ unitree_ros/ # 宇树模型与 ROS 包（参考资源）
├── wsl_lib_links/              # PhysX GPU 所需的驱动库软链（勿删）
├── ars-upstream/  alterlab-academic-skills/   # 第三方技能源仓库
└── .devin/                     # 自主迭代循环机制（当前已停用定时器）
```

## 评估纪律（两条任务线通用）

来自调研的核心结论，所有训练/汇报都遵守：

1. **总奖励 ≠ 策略好坏**。必须看分项奖励、课程等级、per-terrain 分解、摔倒率、跟踪误差。
2. **checkpoint 逐个评估**，后期 ckpt 可能更差（PPO 平台震荡）。
3. **多 seed**（≥3）再下结论；同配置 seed 间差异可达数倍。
4. 先平地站稳走稳，再开课程；课程卡住先查晋级阈值。

## 快速开始

```bash
# WSL 内
source ~/miniconda3/etc/profile.d/conda.sh && conda activate env_isaaclab
cd ~/仿真/unitree_rl_lab
./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity --num_envs 4096 --headless
```

环境细节（LD_LIBRARY_PATH、EULA、WSL 坑）见 `AGENTS.md`。
