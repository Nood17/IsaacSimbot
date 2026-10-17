# Iteration Handoff

<!-- Agent 每轮把最新状态写到本文件顶部；使命完成时在最顶部单独写一行 MISSION-COMPLETE -->

## 状态 2026-10-17 21:40（极端 episode 签名查实 + 日志口径更正：Episode_Reward 项要 ×20s 才对账）

- 本轮做了什么：追查不稳定事件里 rew -82 批次的构成——**签名查实**：极端回合 = 全程剧烈抖动（action_rate 单项 -6.37≈回合-127）但活满 ~880 步不摔倒、吃 timeout 的 episode，产生 -80~-220 极端 return 击穿 critic。顺带更正一个全管线日志口径（对 G1/历次判读同样适用）：`Episode_Reward/<term>` = 回合项和 ÷ episode_length_s(20s)（reward_manager.py:119），对账 Mean reward 需 ×20（iter 10600: 0.75×20≈15.0 vs 14.51 ✓）。机制闭环：std 爬→极端抖动回合→vf 爆→clipped 更新推 std。
- 验证结果：bad-iter 全项分解 + reward_manager.py:113-158 逐行 + env.yaml episode_length_s=20 核实；doc only。
- 训练状态：iter ~11175/23400 仍跑，尖峰继续（最近窗口含 -224 rew iter）。
- 下一步建议：不变——用户在场即停 resume（学习已停）→ eval_terrain（任意 ckpt 可评）→ analyze → Stage A。

## 状态 2026-10-17 21:30（权重级复查推翻"ckpt 污染"判断：actor 未受损，学习实质停摆）

- 本轮做了什么：对上轮发现的 vf 爆炸事件做 ckpt 权重级复查（CPU diff）。**更正上轮红线**：10600→11000 全程 400 iter 的 actor 漂移（rel_L2 0.066、输出层 0.23）≤ 正常 100-iter 漂移（0.072/0.23）——grad clipping 把坏梯度削平，**actor 未被损坏**。真实变化：①critic 空转（vf 爆炸→advantage 失真→学习实质停）②std 胀 0.398→0.435（且 `act_inference`=确定性前向不吃 std——已对安装版源码核实，eval 不受影响）。尖峰速率仍在升（最近 300 iter 59 次）。机制判读与对策已写入状态文档（std 胀→极端 episode→击穿 critic 的慢燃环）。
- 验证结果：torch CPU 逐层 diff（10400/10500/10600/10700/10800/11000 六 ckpt）；act_inference 逐行对源码；doc only。
- 训练状态：iter ~11060/23400 仍跑，不稳定相持续，尖峰加速。**eval 红线作废——任何 ckpt 均可评**，晚 ckpt 只是无新增信息。
- 下一步建议：不变但理由升级——停 resume 因"学习已停"而非"怕污染"；用户在场即停 → eval_terrain（建议扫 8700/10600/latest 三点定平台高度）→ analyze → Stage A。

## 状态 2026-10-17 21:20（巡检发现训练不稳定事件：iter ~10626 起 vf_loss 反复爆炸）

- 本轮做了什么：低频巡检变实检——分段统计发现 resume 段在 iter ~10626 无预兆进入不稳定相：vf_loss 一步 0.038→865，此后 350+ iter 内 >100 尖峰 91 次（峰 ~5600），rew 间歇 -12~-60、action_rate -0.44→-10、entropy 5.9→7.0、std 0.40→0.43；8700-10625 全程零尖峰。主行为指标（fall ~0.17、track ~1.17、clearance ~0.27）暂未漂移，grad clipping 下每次 ~50-100 iter 部分恢复但持续复发——慢燃反馈环而非一次性抖动。已在状态文档落完整事件记录（onset/签名/机制猜测/对策）。
- 验证结果：对 go2_a2_stairs.log 逐 iter 解析核实（onset 前后每 iter 指标、全程尖峰计数、日志无 NaN/error 行）；doc only。
- 训练状态：iter ~10980/23400 仍跑，处不稳定相。**eval ckpt 红线：只用 ≤model_10600.pt**（10600 保存于 onset 前；10800/10900 在不稳相内勿用）。
- 下一步建议：升级——继续跑不再只是"无信息"而是**主动损坏策略**，建议用户在场即停 resume → eval_terrain 扫（ckpt 上限 10600，另扫 leg1 8700/8400）→ analyze → Stage A。agent 仍不主动杀用户 run。lunar-supervisor 照旧等 GPU。

## 状态 2026-10-17 22:15（analyze_eval 默认地形名修正：stairs→pyramid_stairs，15137d1）

- 本轮做了什么：①核实 `unitree_rl_lab.sh -t` 透传任意参数（`train.py --headless "$@"`，--max_iterations 会到达）；②**修了一个真 bug**：analyze_eval.py 默认 `--step_terrains stairs,stairs_inv`，而训练网格 sub_terrain 键名是 `pyramid_stairs/pyramid_stairs_inv`——不指定会静默报 NO DATA。已改默认 + help 注明以 eval 打印的 col->name 为准；文档用法行同步（默认即可，heldout 无 stairs 类报 NO DATA 属正常）。合成 CSV 复测通过。
- 验证结果：默认参数下 ceiling/gate 输出正确；15137d1。
- 训练状态：iter ~10895/23400，平台延续（err 0.27-0.28 微升、fall ~0.18）。
- 下一步建议：不变——等 GPU。

## 状态 2026-10-17 22:00（eval 任务×ckpt 对照表落档：学生只能在含 teacher 组的任务上评，b06aeec）

- 本轮做了什么：核实一个此前没问过的环节——蒸馏学生 ckpt 的 eval 通道。`DistillationRunner.__init__`  eagerly `resolve_obs_groups`（对显式 dict 逐组校验存在性）→ 普通 Velocity 任务无 `teacher` 组 → **学生 ckpt 用 Velocity 任务会 ValueError**；用 BasePPORunnerCfg 也不行（student.* 键与 ActorCritic strict 不匹配）。`StudentTeacher.act_inference`=`self.student(obs)`（学生前向，正确）。已在状态文档落 3类ckpt×2任务 对照表：盲→Velocity/Heldout 默认 cfg；教师→Velocity-Scan 默认 或 Heldout+`--agent_cfg Go2ScanPPORunnerCfg`；学生→Velocity-Scan/Heldout+`--agent_cfg Go2DistillationRunnerCfg`。
- 验证结果：resolve_obs_groups/student_teacher.act_inference 逐行对安装版源码；doc only，b06aeec。
- 训练状态：iter ~10825/23400，平台延续。supervisor 等 GPU。
- 下一步建议：不变——等 GPU，eval → analyze → Stage A。

## 状态 2026-10-17 21:45（Stage-B resume 语义核实 + A3 文档语义修正，a97f9da）

- 本轮做了什么：对安装版源码核实 Stage B 启动链路最后一问——`--load_run`/`--checkpoint` 不带 `--resume` 是否触发教师装载。**结论：触发**。train.py:165/195 条件 `resume OR algorithm.class_name=="Distillation"`，蒸馏恒真；`StudentTeacher.load_state_dict` 见 `actor.` 键→灌 teacher→返回 False→iter=0/optimizer 跳过。忘 `--load_run` 会在 `learn()` 首行 `loaded_teacher` 守卫抛 ValueError（fail-fast，非静默）。顺带修正 A3 文档里同款"`--max_iterations`再训 N"错误说法（与状态文档一致的"绝对上限"口径）。
- 验证结果：on_policy_runner.load / student_teacher.load_state_dict / distillation_runner.learn 逐行对过；doc only，a97f9da。
- 训练状态：iter ~10750/23400，平台延续。
- 下一步建议：不变——等 GPU，eval → analyze → Stage A。两阶段文档语义现已完全一致，无残留错误口径。

## 状态 2026-10-17 21:30（Stage-A 发射命令补 --max_iterations 8000，48368d3）

- 本轮做了什么：巡检发现一个会真烧 GPU 的缺口——Stage A 发射命令没写 `--max_iterations`，Go2ScanPPORunnerCfg 继承 BasePPORunnerCfg 的默认 **50000**（~57h）。已在状态文档改为 `--max_iterations 8000`（~9h）并写清语义：train.py:126 是**绝对上限**非"再训 N"（此前 handoff 里"再训 N"的说法已纠正）；暖启动 iter=0；未收敛可再 resume 抬上限续训。顺带复核：warm_9900_scan.pt 仍在 ft_init/（13MB）、蒸馏 cfg max_iterations=2000 合理、save_interval=100 提供密集 eval ckpt、RobotScanEnvCfg 地形=COBBLESTONE（含 stairs，教师训同一分布）。
- 验证结果：train.py:126/rl cfg 字段逐行对过；doc only。
- 训练状态：iter ~10675/23400，平台延续（fall 0.185、err 0.21-0.25、timeout 0.81）。supervisor 仍等 GPU。
- 下一步建议：不变——GPU 释放后 eval → analyze → Stage A（命令已带 --max_iterations 8000）。**发射链路复核完毕，无新缺口。**

## 状态 2026-10-17 21:15（A1 3-seed 复现通道落地：Unitree-Go2-Velocity-Rough，6f4a122）

- 本轮做了什么：A2 曾原地改地形/指令范围致 A1 配置不可复现——补 `A1_ROUGH_TERRAINS_CFG`（flat .1/rough/slope/slope_inv 各 .3）+ `RobotRoughEnvCfg`（换 generator + 还原 A1 ranges ±0.1/±0.1/±1 与 limit ±1.0/±0.4/±1.0）+ `RobotRoughPlayEnvCfg`，注册 `Unitree-Go2-Velocity-Rough`。**全部字段逐一对照 A1 run 的 `params/env.yaml` 核实**（sub_terrain 参数、max_init_terrain_level=5、curriculum=True 因 swap 发生在父类 post_init 之后需在定义里带）。3-seed 跑法已写入状态文档：`--task Unitree-Go2-Velocity-Rough --seed {1,2,3} --max_iterations 2500`，约 8h GPU 总量，排到 Stage A/B 之后。
- 验证结果：py_compile 过；env.yaml 字段级 diff 无遗漏项。
- 训练状态：iter ~10590/23400，平台延续。lunar-supervisor 仍 wait_gpu_free。
- 下一步建议：不变——GPU 释放后 eval_terrain → analyze_eval → Stage A。轻活至此真正见底：**所有路线图上能预先准备的代码/工具/预案已全部落档**（eval 扫描、判读、暖启动、A/B 发射链路、奖励 Plan-B、A1 3-seed 通道、heldout 地形）。后续轮次只剩训练监测，可低频巡检（每轮看一眼 log 尾 + ckpt 时间戳即可）。

## 状态 2026-10-17 21:00（eval 判读工具 analyze_eval.py 落地，41b009d）

- 本轮做了什么：新增 `unitree_rl_lab/scripts/rsl_rl/analyze_eval.py`——eval_summary.csv → 判读的最后一公里：每 ckpt 打 terrain×level fall_rate / mean_rel_err 矩阵（eps<5 标 `*`）、连续台阶上限（L0 起首个不达标行断；level r → [5+1.5r, 6.5+1.5r)cm）、15cm 门三态判定（stairs/stairs_inv 全部 L≥6 格 fall≤0.10 且 rel≤0.15 → PASS/FAIL/INCONCLUSIVE）。纯 stdlib/CPU，不依赖 conda env。状态文档补用法节 + resume 指标更新到 iter ~10505（fall ~0.167、err_xy 0.22-0.26 波动、timeout ~0.83、terrain_levels 2.41——平台延续）。
- 验证结果：合成 CSV 三态全测（PASS/FAIL/INCONCLUSIVE/连续断档/thin-cell 标记）输出正确；已提交 41b009d。
- 训练状态：iter ~10505/23400，~4.10s/iter，ETA ~14.7h（明 ~11:40）。lunar-supervisor 仍 wait_gpu_free。GPU 4.6/8.1GB。
- 下一步建议：不变——GPU 释放后 `eval_terrain.py` 扫 ckpt → `analyze_eval.py` 读数 → Stage A（warm_9900_scan.pt）。用户在场上可提前停 resume；否则自然跑完。**eval→判读→Stage-A 全链路现在零未准备环节**。

## 状态 2026-10-17 20:40+（Stage-A 奖励 Plan-B 预案落档 + eval 运行时死角清零，0a51fd8）

- 本轮做了什么：
  - eval_terrain 剩余运行时死角核对完毕：`env_cfg.curriculum.terrain_levels/lin_vel_cmd_levels` 字段名对、`__post_init__` 里 `generator.curriculum=True` 已在 parse_env_cfg 实例化时烘好（我们后置置 None 不影响）、`max_init_terrain_level` 是 TerrainImporterCfg 真字段（cfg 里已在用 =5）、`CommandTerm.command` 公有、`parse_env_cfg` 签名匹配。**eval 脚本现在没有未核实的 API 面**。
  - 落档 Stage-A 奖励 Plan-B（预案非实施）：判读前提 + 有序单旋钮表——①`feet_clearance.target_height` 0.05→0.10（现在峰值在 5cm，对 15cm 台阶信号错位）②`feet_stumble.weight` -0.5→-0.25（踢竖板=上台阶动作本身）③可选 `feet_height_body` ④最后手段放宽 track 核。铁律：只子类化 ScanEnvCfg，绝不动 RobotEnvCfg。
- 验证结果：reward func 签名/参数逐个对照 mdp/rewards.py；提交 0a51fd8。
- 训练状态：model_10400 @20:40，~iter 10450，平台延续。
- 下一步建议：不变。轻活见底——剩下可做的只有"等 GPU"。**建议用户在场时停 resume 走 eval→A3**，否则自然跑完明 ~11:00 后再做（已无信息增量）。

## 状态 2026-10-17 20:40（eval difficulty 列修正 + 行→cm 验收映射落地，88d83ba）

- 本轮做了什么：
  - **修正 eval difficulty 口径**：原脚本记 `level/9`，生成器实际 `difficulty=(row+U(0,1))/10` → 改 `(level+0.5)/num_rows`（rows.csv 与 summary 同步）。否则高行 difficulty 虚高 ~5%，对接验收阈值时错判。
  - **落地"15cm 台阶"判读映射**：`step_height=0.05+difficulty×0.15` → **level r ≈ 5+1.5r cm；level≥6 即 15cm 行**——已写入状态文档，eval summary 出来后直接按 (stairs|stairs_inv, level≥6) 读数。
  - eval 建议 `--num_envs` 256→**1024**：200 格网格每格 ~5 env，纯前向显存可承受，per-cell 统计才有意义。
  - resume 平台数据更新到 iter ~10374：fall 末两段 0.161/0.156 仍在平台带内，err_xy 0.242→0.250 微升 + terrain_levels 缓升＝"低行存活稍久"签名，非学会上台阶。
- 验证结果：py_compile 过；difficulty 公式逐行对照 terrain_generator.py:248-252 与 mesh_terrains.py:75。已提交 88d83ba。
- 下一步建议：不变——GPU 释放后 eval_terrain 扫 → Stage A。训练 ETA ~14.5h。

## 状态 2026-10-17 20:30（eval_terrain.py 全文复审 + 3 处小修，已提交 41c8993）

- 本轮做了什么：对从未实跑过的 eval_terrain.py 做逐行复审（对照安装版 IsaacLab/rsl_rl 3.0.1 源码）。**修复 3 处**：
  1. `run_dir` 改为 `dirname(ckpts[0])`——原来直接用 `agent_cfg.load_run` 拼路径，用户漏传 `--load_run`（默认正则 `.*`）时 CSV 会写进不存在的目录。
  2. 换 ckpt 间 `env.reset()`——否则上一 ckpt 半途中的回合会带着清零的累计器记到新 ckpt 名下（每边界 ~256 条污染行，稀有位形格子占比可观）。
  3. `runner.load(..., load_optimizer=False)`——评估不载优化器态省显存。
  - 复核确认无需改：`_term_dones` (num_envs×num_terms) env-major、`act_inference` 吃原始组 TensorDict（内部按 obs_groups["policy"] 取）、`reset()` 返回 (obs, extras)、rsl-rl 3.0.1 下 2.3 兼容分支自然休眠、`termination_manager`/`command_manager`/`step_dt` 均公有属性。
- 验证结果：py_compile 过；所有 API 面对安装版源码核实。提交 `41c8993`（含 A3 文档终验节 + 上轮 handoff）。
- 训练状态：iter ~10300/23400，~4.13s/iter，ETA 15h。lunar-supervisor 仍待命。
- 下一步建议：不变。GPU 释放顺序=eval_terrain 扫（现可直接跑，无 `--load_run` 也安全）→ Stage A。轻活库存已基本清空，后续轮次主要是训练监测。

## 状态 2026-10-17 20:21（Stage A/B 启动链路配置级终验：无可查环节）

- 本轮做了什么：对**安装版**源码（site-packages rsl_rl + `~/仿真/IsaacLab` isaaclab_rl）逐环核对 Stage A/B 全链路：CLI→cfg 字段（update_rsl_rl_cfg 全字段匹配；`--max_iterations` train.py:126 "再训 N"）、`obs_groups` 解析、runner 分发、权重加载。发现并已理解的机制：**`BasePPORunnerCfg.obs_groups` 是 MISSING→to_dict 序列化成 `{}`→resolve_obs_groups 回退自填 policy/critic**（A2 run 的 agent.yaml `obs_groups: {}` 实证）；我们的显式 dict 跳过回退、组名在 ScanObservationsCfg 全部存在。DistillationRunner 继承 OnPolicyRunner（构造/LOAD 签名相同），learn() 守卫 loaded_teacher，StudentTeacher 的 `actor.*`→teacher 重映射 + norm=False 下 Identity strict 空载安全——全部逐行对过。
- 验证结果：核对记录已写入 `A3-teacher-student实现路径.md` 新增"启动链路终验"节。**剩余唯一未测=GPU 运行时**（USD 构建/RayCaster/显存）。
- 训练状态：model_10100 @~20:19，iter ~10200/23400，平台延续。lunar-supervisor 仍在等 GPU。
- 下一步建议：不变——GPU 释放后 eval_terrain 扫 ckpt → Stage A（warm_9900_scan.pt）。配置级准备已 100%，后续轮次若没有 GPU 空档只剩：监测训练/更新文档/补 A1 3-seed 计划这类轻活。

## 状态 2026-10-17 20:14（A3 全套未提交工作入库：4 个 commit，三机同步就绪）

- 本轮做了什么：把工作区累积的 A3 代码改动分批提交（该工作区跨 robot/5090/WSL 三机 git 同步，挂着不提交早晚出冲突）：
  - `bebe252` feat(go2)：Scan teacher obs/heldout 地形/蒸馏 runner cfg/train.py 按 class_name 分发/expand_actor_obs.py（281 行新增）
  - `c184701` go2 eval：eval_terrain.py 的 `--agent_cfg` 覆盖 + runner 分发 + ckpt 名正则防御；events_to_console_log.py
  - `fee58ad` chore：lunar supervisor 两脚本 robot 路径适配（正在跑的 supervisor 用的就是工作树版本，提交只是存档）
  - `f9c5ca6` docs：状态/A3 文档 + spinningup_ppo 离线副本 + handoff
- 验证结果：`git status` 干净（仅剩运行日志 append 与刻意不提交的 .bak/log/lunar_assets/.devin/loop）。未 push（惯例：不主动 push）。训练仍健康：model_10000 @20:10，~iter 10150。
- 下一步建议：不变。GPU 释放后顺序：eval_terrain.py 扫 ckpt → Stage A（warm_9900_scan.pt 已备）。lunar-supervisor 仍在等 GPU——用户裁决。

## 状态 2026-10-17 20:06（A3 Stage-A 暖启动 ckpt 生成并验证，发射就绪）

- 本轮做了什么：用 `expand_actor_obs.py` 从 resume 段最新 ckpt `model_9900.pt` 生成 Stage-A 教师暖启动 `logs/rsl_rl/unitree_go2_velocity_a3/ft_init/warm_9900_scan.pt`（--add_dim 935 --set_iter 0）。**修正了一个位置错误**：此前误以为 `ft_init/` 在 `unitree_go2_velocity/` 下即可——那是 A2-leg1 的 `init_8400.pt` 目录；`--load_run` 按 `<experiment_name>/<load_run>` 解析，Scan 任务的 experiment 是 `unitree_go2_velocity_a3`，故暖启动必须放那边（现已放对）。
- 验证结果：CPU 校验通过——top keys 齐（infos/iter/model_state_dict/optimizer_state_dict）、iter=0、`actor.0.weight` (512,1170)、proprio 块 abs-sum 21322 非零、scan 块全零、无 NaN、optimizer 2d 形状与网络一致、单层前向通过。启动命令已写入 `状态-A1A2训练进展.md`：`./unitree_rl_lab.sh -t --task Unitree-Go2-Velocity-Scan --headless --num_envs 2048 --run_name A3_teacher --resume --load_run ft_init --checkpoint warm_9900_scan.pt`。
- 训练状态：A2 resume 健康，iter ~10000/23400（model_9900 @20:03，~4.1s/iter），最新指标 err_xy 0.241 / bad_orientation 0.191 / timeout 0.808 / terrain_levels 2.30——平台延续。GPU 4.6/8.1GB、RAM 余 ~6GB，不开第二实例。lunar-supervisor 仍在 wait_gpu_free 循环（sleep 60），待用户裁决。
- 下一步建议：不变——用户在场建议停 resume → eval_terrain.py 扫 ckpt → Stage A（暖启动命令已备好；若想让暖基更晚，对 final ckpt 重跑 expand_actor_obs.py 秒级重生成）。

## 状态 2026-10-17 20:35（封顶后 650 iter：平台实锤，resume 已无信息量）

- 本轮做了什么：resume 段封顶后新数据判读（9200→9850，cmd_lvl=1.50 封顶后 ~650 iter）：fall 0.183/0.170/0.160/0.173、err_xy 0.24±0.005、rew 15.7–16.4、timeout ~0.83——**与 leg1 平台带完全重合且无任何斜率**，盲策略台阶平台实锤。terrain_levels 1.7→2.2 缓升仅说明低行存活稍久，非爬台阶能力。
- 验证结果：状态文档 resume 条已更新为"平台实锤"结论。**判断：resume 继续跑到 23400 只剩平台确认价值，决策信息已齐**——但 run 是用户手动起的，agent 不主动杀。
- 下一步建议：用户在场时建议停 resume → `eval_terrain.py --load_run 2026-10-17_18-41-04_A2_stairs_slope_ft --checkpoints "model_*.pt"`（扫 8700/9400/9800 定台阶高度）→ 直接进 Stage A `Unitree-Go2-Velocity-Scan`（可选 expand_actor_obs.py 暖启动）。若任其自然跑完，明 ~11:00 后照此流程。

## 状态 2026-10-17 20:20（Stage-B 教师加载链路 CPU 端到端验证通过）

- 本轮做了什么：
  - **Stage-B 加载链路全链路 CPU 验证**：`expand_actor_obs.py` 产出 1170 维暖启动 ckpt → `StudentTeacher`(student=235/teacher=1170, 双 norm=False) `load_state_dict(strict=True)` → `actor.` 键自动灌入 teacher → `loaded_teacher=True`、resumed=False（iter 0）→ student `act_inference` 正常。**整个 A2→A3→蒸馏的权重链路已无任何未验证环节**。
  - 确认 `./unitree_rl_lab.sh -t` = `train.py --headless`；A3 最终 CLI：Stage A `-t --task Unitree-Go2-Velocity-Scan --num_envs 2048`（暖启动可加 `--resume --load_run ft_init --checkpoint warm_8700_scan.pt`，注意 ft_init 目录需放 `logs/rsl_rl/unitree_go2_velocity_a3/` 下）；Stage B `-t --task Unitree-Go2-Velocity-Distill --load_run <scan_run> --checkpoint model_N.pt`。
  - 核对路线图 A3 验收"15cm 台阶能上"→ 覆盖路径 = eval_terrain.py stairs 列 + heldout boxes 列。
- 验证结果：见上，strict load + inference 均通过。
- 下一步建议：等 A2 resume（iter ~9600+，ETA 明 ~11:00）或用户提前停 → eval_terrain.py → Stage A。

## 状态 2026-10-17 20:10（教师暖启动工具落地 + 修复蒸馏 normalization 崩溃坑）

- 本轮做了什么：
  - 新增 `scripts/rsl_rl/expand_actor_obs.py`：盲 actor ckpt → 教师输入 ckpt（`actor.0.weight` 末尾补零列 + optimizer exp_avg/exp_avg_sq 同步扩 + 可选 normalizer 键）。**CPU 端到端验证通过**：1170 维 ActorCritic strict load + forward + proprio 权重块非零/scan 块全零。
  - `TeacherCfg.height_scanner` 挪到**组末**（IsaacLab history 是 per-term 展平 reshape → proprio 块占 [0,235) 连续 → 拼接=纯列追加）。
  - **修复一个会真崩的配置**：Go2 管线所有 PPO ckpt **无 `*_obs_normalizer.*` 键**（cfg 字段 MISSING→`{}`→falsy→`Identity`，`empirical_normalization:true` 实际没生效）；`StudentTeacher.load_state_dict` strict 加载 `teacher_obs_normalizer` → `teacher_obs_normalization=True` 会崩 → 蒸馏 cfg 双 norm 已改 False（与 anymal 参考一致）。顺带发现：全管线观测归一化实际从未开启（值得记入状态文档的隐藏事实）。
- 验证结果：py_compile 全过；暖启动端到端 CPU 验证（如上）。训练健康 iter ~9600/23400。
- 下一步建议：同前——resume 完/提前停 → eval_terrain → Stage A 教师（可选 `expand_actor_obs.py` 暖启动省 ~8h：`--in_ckpt model_8700.pt --add_dim 935 --out_ckpt ft_init/warm_8700_scan.pt --set_iter 0`）。

## 状态 2026-10-17 19:55（held-out 验收地形实施 + eval_terrain --agent_cfg）

- 本轮做了什么：
  - **held-out 第 6 地形落地**（A3 备忘最后一个待实施项）：`velocity_env_cfg.py` +`HELDOUT_TERRAINS_CFG`（boxes 0.05–0.2m 40% / gap 0.1–0.5m 30% / discrete_obstacles 0.01–0.2m 30%，全为训练集没有的类型，参用 canonical ROUGH_TERRAINS_CFG）+`RobotHeldoutEnvCfg(RobotScanEnvCfg)`（仅换 generator，保留三组观测 → 盲/教师/蒸馏 ckpt 通用）；注册 `Unitree-Go2-Velocity-Heldout`。
  - `eval_terrain.py` +`--agent_cfg module:Class`：按类路径换 agent cfg（experiment_name 跟随 → --load_run 自动找对目录），同一 held-out 任务可评三类 ckpt，无需三个注册。
- 验证结果：全文件 py_compile 通过。训练健康 iter ~9500/23400。
- 下一步建议：同 19:45——resume 完/提前停 → eval_terrain 扫 ckpt → `Unitree-Go2-Velocity-Scan` 训教师 → `-Distill` 蒸馏 → heldout 任务验收泛化。**A3 全部代码侧准备已完成，剩余全是 GPU 排队事项**。

## 状态 2026-10-17 19:45（A3 脚手架已实施 + 修正 train.py 缺蒸馏分发的大坑）

- 本轮做了什么：**A3 两阶段脚手架全部落地**（增量式，不动现有任务/在跑 run）：
  - `velocity_env_cfg.py` +`ScanObservationsCfg`（新增 `teacher` 组 = 无噪 proprio + height_scanner，history=5）+`RobotScanEnvCfg`/`RobotScanPlayEnvCfg`。`teacher` 组刻意不进基础 cfg，A0–A2 不付堆叠开销。
  - 新文件 `agents/rsl_rl_distill_cfg.py`：`Go2ScanPPORunnerCfg`（Stage A：`obs_groups {"policy":["teacher"],"critic":["critic"]}`，PPO actor 即教师）+ `Go2DistillationRunnerCfg`（Stage B：`{"policy":["policy"],"teacher":["teacher"]}`）。**两 cfg 共用 `experiment_name="unitree_go2_velocity_a3"`**——`get_checkpoint_path` 按 `<experiment>/<load_run>/<ckpt>` 解析，不同名会找不到教师 ckpt。
  - `go2/__init__.py` 注册 `Unitree-Go2-Velocity-Scan`（Stage A）/`-Distill`（Stage B）。
  - **发现并修正两个真坑**：① train.py 硬编码 `OnPolicyRunner`，蒸馏 cfg 会 `eval("StudentTeacher")`→NameError——已加与 play.py 相同的 class_name 分发（eval_terrain.py 同步）。② 验证 configclass 语义：裸赋值 override 经 `_add_annotation_types` 自动补注解→生效（与 anymal 参考一致）。
  - 已核实加载链路：`StudentTeacher.load_state_dict` 检测 `actor.` 键自动灌进 teacher 网（PPO ckpt 直接喂）；teacher_obs_normalization 已配对 empirical_normalization。
- 验证结果：全文件 py_compile 通过；API 链逐环对照源码（StudentTeacher 签名/`resolve_obs_groups`/`get_checkpoint_path` 正则解析/`export_deploy_cfg` 只读 policy 组）。**未 GPU 实测**（A2 resume 仍在跑，iter ~9500）。发现：height_scanner RayCaster 一直常驻场景（A2 也在付 raycast），Scan 任务新增成本只是 obs 堆叠内存，num_envs 可先试 2048。
- 下一步建议：① resume 完/用户提前停 → eval_terrain.py 扫 ckpt 定盲策略台阶高度。② 进 A3：`--task Unitree-Go2-Velocity-Scan` 训教师（可先试 `--num_envs 2048`）；毕后 `--task Unitree-Go2-Velocity-Distill --load_run <教师run> --checkpoint model_N.pt`。③ 若教师仍卡 ~10cm：按备忘调奖励（clearance 目标高/stumble 权重）+ 定 held-out 第 6 地形。

## 状态 2026-10-17 19:30（eval_terrain.py 源码级 API 复核通过 + resume 平台确认中）

- 本轮做了什么：
  - **eval_terrain.py 全量源码级复核**（代替 GPU 实测，GPU/RAM 仍被 A2 resume 占用）：逐项对照 IsaacLab/rsl_rl 源码核实——`TerminationManager._term_dones`（done 行当步必重写、无陈旧标志、同帧多 term 取最后）、`get_term`/`command` 属性、`vecenv_wrapper.step` 4 元组返回与 `extras["time_outs"]`（`is_finite_horizon` 默认 False 时注入）、`terrain_levels/terrain_types` 每 env 张量、列→地形名 cumsum 公式与 `terrain_generator.py:240` 逐字符一致、Event/Curriculum 管理器对 `None` term 跳过、go2 终止项名 `time_out`/`base_contact`/`bad_orientation`（time_out 恰为首项不冲突归因）。**发现 1 个真 bug 已修**：`re.search(...).group(1)` 对不匹配 ckpt 名（如 get_checkpoint_path fallback）会 AttributeError，已改防御式。py_compile 通过。
  - **resume 最新分段均值（至 iter 9353，654 pts）**：`lin_vel_cmd_levels` 已于 ~9200 封顶 1.50；封顶后首窗口（9200-9350）fall 0.183 / err_xy 0.241 / rew 15.8——**与 leg1 平台带（0.15–0.19 / 0.243）完全重合**，"恢复"概率进一步下降，平台确认假说实时兑现中。terrain_levels 均值 ~1.7/9，难行从未被大量占据。
- 验证结果：上述两处更新已写入 `状态-A1A2训练进展.md`（现状判读节 resume 条 + eval_terrain 注意节）。训练健康：iter ~9353/23400，~4.2s/iter，ETA 明日 ~11:00。
- 下一步建议：不变——等 resume（或用户在场时提前停）→ eval_terrain.py 扫 model_{8700,…,latest}。若用户想现在停 resume 直接进 A3：信息其实已够（封顶后仍 0.18 摔倒），eval 用 leg1 的 model_8700.pt 跑即可，不必等 23400。

## 状态 2026-10-17 19:20（平台点分析：resume 大概率在确认而非恢复）

- 本轮做了什么：分段均值分析 A1/A2-leg1 全曲线。**A1 在 iter ~2000 平台**（摔倒 0.3%、error 0.19、track 1.42 到 8400 不动）；**A2-leg1 摔倒率 iter ~500 即平台**（0.15–0.19 到 8700）——盲策略台阶上限瞬间触顶。
- 验证结果：推论已写入状态文档——A1 级任务 ~2000iter/2.2h 收敛（3-seed 便宜）；resume→23400 大概率仅确认平台。**建议（不擅自执行，run 是用户 18:40 手动启动的）：下次用户在场可考虑提前停 resume，用 leg1 ckpt 跑 eval_terrain.py 定平台高度直接进 A3。**
- 下一步建议：同上；若 resume 真跑完，eval_terrain.py 扫 model_{8700,15000,23400} 即可。

## 状态 2026-10-17 19:15（resume 段趋势判读 + 小修）

- 本轮做了什么：
  - resume 段 470 iter 分段均值分析：**指标回落是指令课程重爬所致**（lin_vel_cmd_levels 0.5→1.5 在 ~500 iter 内走完），当前摔倒 ~17%、reward ~14.7 ≈ leg1 末态持平，无遗忘恶化但也未见恢复——真恢复与否看命令范围封顶后的曲线。
  - 确认 `--seed` 已支持（train.py:41）→ A1 的 3-seed = `--seed 1/2/3`。
  - 小修：G1 `velocity_env_cfg.py` 工作树 `-9.81` 那行的注释 "lunar"→"earth"（值本来就是地球重力，注释误导）。
- 验证结果：趋势判读已写入 `状态-A1A2训练进展.md` 现状判读节。
- 下一步建议：不变——等 ~23400 → eval_terrain.py 扫 ckpt；若到时摔倒仍 ~17% 即盲策略平台实锤进 A3。

## 状态 2026-10-17 19:10（更正 max_iterations 语义 + A3 路径调研）

- 本轮做了什么：
  - **更正**：`--max_iterations` 在 rsl_rl 里是"再训 N iter"（`tot_iter = start + N`）——A2 resume 实际终点 ≈ **iter 23400**（非 14700），明日 ~11:20 完。已修正 `状态-A1A2训练进展.md`。
  - 写 `docs/quadruped/A3-teacher-student实现路径.md`：rsl_rl 3.0.1 蒸馏机制已摸清（`obs_groups {"policy","teacher"}`、StudentTeacher、须先 load 教师）；isaaclab_rl 有现成 `RslRlDistillationRunnerCfg` 模板；列出教师初始化/奖励调整/scan 开销三个待决策点。
- 验证结果：代码核对（distillation_runner/StudentTeacher/anymal_d 参考 cfg）；训练仍健康。
- 下一步建议：A2 完训（~23400）→ eval_terrain.py 扫 ckpt → 若盲策略平台化则按 A3 备忘实施。

## 状态 2026-10-17 19:05（补 A0 逐项解读文档）

- 本轮做了什么：写 `docs/quadruped/Go2-env配置逐项解读.md`——对照源码逐条解释 Go2 env 的 command/obs/reward/termination/event/curriculum 每项（A0 验收项"能逐条解释每个奖励项"的落纸）。关键语义均已读码核实：feet_air_time 负值正常、track 核=exp(−err²/0.25)、joint_pos 站立时罚×5、terrain_levels 均值=存活位置非进度条、lin_vel_cmd_levels 在 resume 后重爬、Go2 有 gait_phase 观测但无 gait 奖励（与 G1 相反）。
- 验证结果：文档工作；训练仍健康（iter ~9060，摔倒 ~7-10%，ETA ~16h）。
- 下一步建议：同下条 handoff；A2 完训后先跑 eval_terrain.py（已建好，见下文）。

## 状态 2026-10-17 19:00（A2 训练监测 + 指标基线 + per-terrain 评估脚本）

- 本轮做了什么：
  - 确认 Go2 **A2 微调正在本机（robot, 5060 8GB）运行**：PID 7928，`--resume model_8700.pt → max_iterations 14700`，num_envs=2048，~4.1s/iter，ETA ~16h（约明午）。未干扰。
  - 解析 A1（5090, 8400 iter）/A2 leg1（robot, →8700）/A2 resume 三段 tensorboard events，核实指标语义，写 `docs/quadruped/状态-A1A2训练进展.md`。
  - 排除疑虑：Go2 各 run env.yaml `history_length=5`，G1 的 history=80 事故不影响 Go2 ckpt。
  - 新增 `unitree_rl_lab/scripts/rsl_rl/eval_terrain.py`：per-(地形类型,难度行) 分解摔倒率/跟踪误差，支持多 ckpt 扫（`--checkpoints "model_*.pt"`），输出 eval_rows.csv + eval_summary.csv 到 run 目录 eval/ 下。冻结地形分布方式：删两个课程项 + `max_init_terrain_level=9` + 指令用 limit_ranges + 默认关 push_robot。**仅 py_compile + API 核对，未 GPU 实测**（GPU/RAM 被训练占着）。
- 验证结果（指标，非训练）：A1 收敛好（摔倒~0.3%、track 95% 满权）；A2 加楼梯后摔倒 17%、reward 腰斩属预期；resume 段恢复中（摔倒回 7.9%、reward 23.7）。`error_vel_xy` 是绝对误差（m/s），~0.20 相当于 ~20% 相对——路线图 <10% 验收需 per-terrain 评估后判定。
- ⚠️ **任务 B 冲突待用户裁决**：`lunar-supervisor.service` 活着且在 `wait_gpu_free` 循环——Go2 跑完（明午前后）会自动拉起 G1 `lsurface_earth` 续训（19500→29998，+10499 iter）。使命规定任务 B 暂停；但这是用户自建自动化、round 905 刚修复 history=80 根因后有意重启的，故本轮未动。若想阻止：`systemctl --user stop lunar-supervisor.service`。
- 下一步建议：
  1. 等 A2 到 14700（明午）→ 逐 ckpt 评估 + per-terrain 摔倒率/误差分解，确定盲策略台阶天花板 → 决定 A3 height-scanner 入口。
  2. resume 会重置指令课程范围（`lin_vel_cmd_levels` 从 0.5 重爬），评估时读绝对命令范围而非课程等级。
  3. G1 `velocity_env_cfg.py` 工作树仍是未提交的回退（gravity -9.81 但注释仍写 lunar、history=5）——任务 B 恢复前先提交清理。

## 状态 2026-10-15 晚（理论梳理 + 诊断新证据）

- 本轮做了什么：
  - 拉取 76a668e（两任务线重整）并完成知识对接：调研成果归档在 `docs/research/`，PPO/rsl_rl 学习路径已建立（Spinning Up PPO 页已存 `docs/research/spinningup_ppo.{html,pdf}`）
  - **诊断清单第 5 项有新证据**：`gait` 奖励开着但 `gait_phase` 观测被注释——奖励按节拍打分、策略看不到节拍，是 gait~0.51 停滞的强候选解释（详见 `docs/biped/状态-G1基线诊断.md` 新加小节）
  - **发现隐患**：`velocity_env_cfg.py` 工作区有未提交的 `sim.gravity=-1.62`，地球基线任务当前实为月面重力，恢复训练前必须删除
  - 配置实验（未提交）：G1 `history_length` 5→80（两个步态周期）、`push_robot` 间隔 (5,5)→(10,30)
  - 决策：A3 暂缓 DreamWaQ/GRU 隐式估计，默认 height scanner + teacher-student
  - 已推送：`docs/agent/Agent运行环境-Skills-MCP-环境配置需求.md`（77cd5c3）、lunar_panel 及月面任务归档（91fe05f）
- 验证结果：本轮无训练验证（任务 B 暂停中，只做文档与配置层面的整理）
- ⚠️ 设备更正（2026-10-16）：本工作区在**三台机器**上同步使用——本机 `robot`（Ubuntu 26.04 原生，RTX 5060 Laptop 8GB）、5090 训练机 `ubuntu-System-Product-Name`（Go2 A1 在此跑）、WSL2 机 `DESKTOP-9S36E5P`（RTX 4070 Ti，`~/仿真/…` 路径）。此前文档误把 WSL 机特征当成本机通用环境，已在 `docs/agent/Agent运行环境-*.md` §3.1 改为三设备矩阵。写脚本一律用环境名/相对路径，勿写死单机绝对路径
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
