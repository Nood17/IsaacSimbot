# Go2 `Unitree-Go2-Velocity` 环境配置逐项解读

> A0 验收项："能逐条解释每个奖励项的作用"。对应 `unitree_rl_lab/.../robots/go2/velocity_env_cfg.py`（A2 版，commit d9f5baf）。函数实现在 `tasks/locomotion/mdp/`（自定义）与 IsaacLab 内置 mdp。
> 2026-10-17 对照源码核实。

## 仿真骨架

- `decimation=4` × `sim.dt=0.005` → 策略 50Hz、物理 200Hz；`episode_length_s=20`。
- 地形 `TerrainImporterCfg` + `COBBLESTONE_ROAD_CFG` 生成器：8×8m 格子，10 行难度 × 20 列类型，curriculum=True（行号=难度）。当前子地形比例：flat 0.1 / random_rough 0.2 / 正/倒 pyramid_slope 各 0.2 / 正/倒 pyramid_stairs 各 0.15（台阶高 0.05–0.20m 随行号线性上升）。列→类型按 cumsum 固定分配（0-1 flat、2-5 rough、6-9 slope、10-13 slope_inv、14-16 stairs、17-19 stairs_inv）。
- `max_init_terrain_level=5`：训练时 env 初始只撒在低半区（0–5 行），往上靠课程爬。
- 传感器：`contact_forces`（全身接触力，history 3，track_air_time=True）；`height_scanner` 已实例化但**未接入观测**（policy/critic 都注释着）——纯盲走，A3 的预留接口。

## Commands

`base_velocity` = `UniformLevelVelocityCommandCfg`（仅在 UniformVelocityCommandCfg 上加 `limit_ranges` 字段）：
- 每 10s 重采样指令 (vx, vy, wz)；`rel_standing_envs=0.1` → 10% env 指令恒零（练站立）。
- `ranges` 是当前生效范围（课程会加宽），`limit_ranges` 是上限。A2 后 ranges=(±0.5, ±0.3, ±1.0)，limit=(−1.0~1.5, ±0.6, ±1.0)。
- 指标 `error_vel_xy/yaw`：指令窗内**平均绝对误差**（m/s、rad/s），日志在 `Metrics/base_velocity/*`。

## Observations

policy（带噪声 corruption + clip，history 5 拼接）：

| 项 | 内容 | scale/噪声 |
|---|---|---|
| base_ang_vel | 机体系角速度 | ×0.2，U±0.2 |
| projected_gravity | 重力在机体系投影（姿态感知） | U±0.05 |
| velocity_commands | 当前指令 (vx,vy,wz) | — |
| joint_pos_rel | 相对默认关节角 | U±0.01 |
| joint_vel_rel | 关节速度 | ×0.05，U±1.5 |
| last_action | 上步动作 | — |
| gait_phase | sin/cos(2π·t/0.8s) 节拍时钟 | — |

critic（无噪声、非对称 PPO 的特权信息）：多了 `base_lin_vel`（真值线速度）、`joint_effort`（关节力矩 ×0.01）；height_scanner 注释着。

注意 Go2 与 G1 的对照：**Go2 有 gait_phase 观测但没有 gait 奖励**（时钟输入仍帮策略学周期步态）；G1 基线反过来——`gait` 奖励开着、观测被注释，是 G1 卡 gait~0.51 的候选根因（见 `docs/biped/状态-G1基线诊断.md`）。

## Rewards（权重见 cfg；+为奖、−为罚）

**任务项**
- `track_lin_vel_xy` w=1.5：`exp(-‖cmd_xy - vel_xy‖²/std²)`，std=√0.25≈0.5 → 误差 0.5m/s 时只剩 e⁻¹。主任务项。
- `track_ang_vel_z` w=0.75：同上对 yaw 角速度。

**机体正则**（都是 L2 罚，抑抖/抑冲）
- `base_linear_velocity`(lin_vel_z, −2.0) 压竖直弹跳；`base_angular_velocity`(ang_vel_xy, −0.05) 压横滚俯仰速率。
- `joint_vel`(−0.001)、`joint_acc`(−2.5e-7)、`joint_torques`(−2e-4)、`action_rate`(−0.1)：平滑动作/减功耗/减冲击。
- `dof_pos_limits`(−10.0)：接近关节限位大罚，保护硬件行为的仿真对应物。
- `energy`(−2e-5)：Σ|qvel|·|torque|，功率代理。

**姿态/站姿**
- `flat_orientation_l2`(−2.5)：压机身倾斜（投影重力 xy 分量）。
- `joint_pos`(−0.7)：‖q − q_default‖；**站立时×5**（cmd=0 且体速<0.3 判定静止）→ 逼着停下时回标准站姿、不瘫不劈叉。

**足部**（全部走 contact_forces 传感器 `.*_foot`）
- `feet_air_time` w=+0.5：首次落地时发 `(last_air_time − 0.5s)`——滞空>0.5s 奖、<0.5s 罚，且仅当 |cmd|>0.1 生效。日志值**为负是正常的**（快步频→短滞空→小罚），不是 bug。
- `feet_stumble`(−0.5)：足部水平接触力 >4× 竖直力 → 判"踢到立面"。楼梯场景的关键惩罚（撞台阶竖面）。
- `feet_clearance` w=+0.5：摆动足（水平速度 tanh 加权≈1）足端高度贴 0.05m 目标给 exp 核奖励；支撑足近似不计。防拖地绊台阶。
- `air_time_variance`(−1.0)：四足滞空/触地时间的方差（clip 0.5s）——步态整齐度。
- `feet_slide`(−0.1)：触地时足端水平滑动惩罚。

**其他**
- `undesired_contacts`(−1.0)：Head/hip/thigh/calf 接触力>1N 即罚——非足端碰地。`feet_contact_forces`（足底大力罚）整段注释未启用。

## Terminations

- `time_out`：20s 到点（time_out=True，走 truncated 而非 terminated）。
- `base_contact`：base 身 >1N 接触 → 倒地。
- `bad_orientation`：横滚/俯仰超 0.8 rad（≈46°）→ 翻倒。
- 摔倒率口径 = 1 − time_out 比例 ≈ bad_orientation + base_contact。

## Events（域随机化）

- startup：`physics_material` 摩擦 U(0.3,1.2)/恢复 U(0,0.15) 64 桶；`add_base_mass` base 加 −1~+3kg。
- reset：`base_external_force_torque`（当前 0，占位）；`reset_base` 出生位姿 x/y±0.5m、yaw±π、零速；`reset_robot_joints` 关节按默认位 ×1.0、速度 U(−1,1)。
- interval：`push_robot` 每 10–30s 给 base 一次 ±0.5m/s 水平速度脉冲（抗扰训练）。

## Curriculum（两条）

- `terrain_levels_vel`（IsaacLab 内置）：回合结束时位移 >4m（地形边长一半）升 1 行；位移 < 指令应有距离一半 降 1 行（两者互斥）。日志 `Curriculum/terrain_levels`=全 env 行号均值——**是"存活位置"不是进度条**，均值低≠没学会，要 per-terrain 评估看分布。
- `lin_vel_cmd_levels`（自定义）：当 `track_lin_vel_xy` 回合均酬 > 0.8×权重（=1.2）且距上次升级 ≥1 个回合长，`ranges` x/y 各 ±0.1 加宽至 limit。日志返回 `ranges.lin_vel_x[1]` 当前值。**注意 resume 后从 cfg 值重爬**。

## 评语

这套配置 = IsaacLab velocity 标准件 + 若干 unitree 定制（joint_pos 站立×5、energy、air_time_variance、feet_stumble 改 4× 阈值）。奖励结构对"盲走台阶"天然吃亏：没有为攀爬设计的项（无 foot_height_body/upward），stumble/clearance 反而抑止蹭台阶——这是 A2 观察到的摔倒率上升的结构原因之一，也是 A3 决策时要权衡的（单纯开 height scanner 不一定够，可能要配合 rewards 调整）。
