# Iteration Handoff

<!-- Agent 每轮把最新状态写到本文件顶部；使命完成时在最顶部单独写一行 MISSION-COMPLETE -->

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
