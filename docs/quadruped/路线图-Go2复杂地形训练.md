# 任务 A 路线图：Go2 复杂地形训练

> 目标：**学会在仿真中训练一个较难任务**，不以最高奖励为目标，以"策略在分布外地形上可复现地工作"为验收。
> 依据：`docs/research/调研报告-四足机器狗复杂地形强化学习训练.md`（方法与策略）、`docs/research/调研-四足复杂地形-v1-本机适配版.md`（本机命令与起步）、`docs/research/调研报告-训练失败应对策略专项.md`（卡住时查）。

## 前提

- Go2（12 dof，静态稳定）比 G1（29 dof，双足）简单一个量级——用它练"课程设计 + 奖励调试 + 评估方法"，结论可迁移回任务 B。
- 本机 unitree_rl_lab 已跑通 Go2 训练；`go2/velocity_env_cfg.py` 第 36–56 行有已写好的地形模板（random_rough / hf_pyramid_slope / boxes / pyramid_stairs），取消注释即得复杂地形。

## 阶段与验收

| 阶段 | 内容 | 通过标准（不是 reward 数字） |
|---|---|---|
| **A0 基线复现** | 跑通 `Unitree-Go2-Velocity` flat，理解 reward/curriculum/event 三个 manager 的每一项 | 能逐条解释每个奖励项的作用；tensorboard 分项曲线无异常 |
| **A1 盲走 rough** | 放开 random_rough + pyramid_slope（保留 10% flat），加 feet_air_time / 接触惩罚 / 地形课程 | rough 地形上速度跟踪误差 <10%，摔倒率 <5%，3 seeds 一致 |
| **A2 诊断练习** | 故意制造一个失败（如删掉某惩罚项/地形难度拉满），观察并记录失效模式 | 能用调研报告的诊断表定位到根因 |
| **A3 楼梯/离散地形** | 启用 pyramid_stairs + boxes；盲走不够时二选一：历史堆叠（GRU，DreamWaQ 路线）或 height scanner | 15cm 台阶能上 |
| **A4 扩展（可选）** | 沟壑/跳跃地形、teacher-student 蒸馏、分层策略 | 视兴趣 |

## 训练纪律（每阶段必做）

1. **分项奖励必须逐个看**：总 reward 上升但某跟踪项不涨 = 奖励黑客或权重失衡。
2. **课程等级日志**：`Curriculum/terrain_levels` 长时间不涨 → 查晋级阈值（任务 B 的 G1 就卡在指令 1 级）。
3. **每 500 iter 存 ckpt，评估时逐 ckpt 播放**（headless 下用 `--checkpoint` + 录制/指标回放；WSL 无法渲染时导出到 Windows 端 Isaac Sim 播放）。
4. **held-out 测试**：训练用 5 种地形，验收用第 6 种没见过的。
5. **3 seeds** 起步再下结论。

## 卡住时

按 `docs/research/调研报告-训练失败应对策略专项.md` 的速查表走：先区分"配置错（平地都学不会）"vs"难度/探索问题（平地能学）"，再对症（终止课程 / RSI / 残差 RL / 奖励路由 / 权重自适应）。
