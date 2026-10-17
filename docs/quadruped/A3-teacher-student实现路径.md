# A3 实现备忘：height scanner + Teacher-Student 蒸馏

> 2026-10-17 调研结论（只读代码未实施）。前提：A2 盲策略在台阶上平台化后，按路线图进入 A3。依赖已确认存在：rsl_rl 3.0.1 内置 `runners/distillation_runner.py` + `algorithms/distillation.py` + `modules/student_teacher.py`。
>
> **2026-10-17 更新：脚手架已实施**（py_compile 通过，未 GPU 实测）。见文末"实施记录"。

## rsl_rl 蒸馏机制（已核实）

- `DistillationRunner`（agent_cfg `algorithm.class_name = "Distillation"` 时由 train.py 走 load 分支）：
  - `policy.class_name = "StudentTeacher"`，`obs_groups = {"policy": [<学生组名>], "teacher": [<教师组名>]}`——key 固定叫 `"policy"`（其实是学生）和 `"teacher"`。
  - 学生 MLP 吃 `obs_groups["policy"]` 列出的 env 观测组；教师 MLP 吃 `obs_groups["teacher"]`。
  - `learn()` 开头断言 `policy.loaded_teacher`——**必须先 `--checkpoint` 加载教师权重**（train.py 对 Distillation 类强制走 runner.load）。
- 学生输入 = 盲 proprio（当前 `policy` 组即可）；教师输入 = proprio + height_scanner。

## 两阶段流程

1. **Stage A — 训教师**：需要一个"policy 组含 height_scanner"的 env 变体跑普通 PPO。可直接从 A2 ckpt resume 继续训（scan 维度新增会改变 obs 维度→**不能直接 resume 旧 ckpt**，维度不匹配；教师得从头训或接受 obs 扩容重置——见下"待决策"）。
   - cfg 改动：`PolicyCfg`（或新建 teacher 变体）加 `height_scanner = ObsTerm(func=mdp.height_scan, params={"sensor_cfg": SceneEntityCfg("height_scanner")}, clip=(-1.0,5.0))`；传感器已实例化在场景里（`debug_vis=False`，update_period 已配）。
2. **Stage B — 蒸馏**：新 agent cfg（Go2 版 `DistillationRunnerCfg`）：
   - `class_name`/`algorithm.class_name = "Distillation"`，policy `StudentTeacher`（hidden 对齐 [512,256,128] 或教师结构）
   - `obs_groups = {"policy": ["policy"], "teacher": ["teacher"]}`
   - env 增加 `teacher` 观测组 = policy 全部项 + height_scanner（或偷懒指向 `critic` 组并把其中 scan 取消注释——但 critic 组含 lin_vel/effort 真值，教师多吃信息无害；更干净是单独建 teacher 组）
   - `--checkpoint <教师model_*.pt>` 载入教师权重后蒸馏

## 待决策/风险

- **教师初始化**：obs 维度变了，旧 A2 ckpt 无法直接 resume（policy 输入维度 +scan 维度）。两个办法：(a) 教师从头训（最稳，本机 ~16h/1.5w iter 量级）；(b) 手动把旧 actor 权重拷进新 actor（首层补零初始化 scan 列），再 resume——省一半时间但要写一次性转换脚本。
- **奖励可能要动**：当前奖励套没有攀爬激励（A0 解读文档已记：stumble/clearance 抑止蹭台阶）。教师有了 scan 也未必愿意上高台阶——若 stage A 平台仍在 ~10cm，考虑加 `foot_height_body`/调 clearance 目标高度，或降 feet_stumble 权重（撞竖面本来就是上台阶的一部分）。
- **num_envs**：加 scan 后每 env 多 187 ray（1.6×1.0m @0.1m），2048 envs 的 raycast 开销在 5060 上待测，可能要降到 1024。
- **held-out 地形**（路线图纪律 #4）：进入 A3 前先把验收用的第 6 种地形定下来（候选：`MeshRandomGridTerrainCfg` boxes，模板里已注释备好），训评估分开。

## 参考入口

- 现成 cfg 模板：`isaaclab_rl` 提供 `RslRlDistillationRunnerCfg` / `RslRlDistillationStudentTeacherCfg` / `RslRlDistillationAlgorithmCfg`；参考实例 `isaaclab_tasks/.../anymal_d/agents/rsl_rl_distillation_cfg.py`（AnymalDFlatDistillationRunnerCfg，obs_groups `{"policy":["policy"],"teacher":["policy"]}`——我们的教师组换成含 scan 的组即可）
- train.py 的 Distillation 分支：`scripts/rsl_rl/train.py:188`（`algorithm.class_name == "Distillation"` 时强制 load ckpt）
- play.py 已支持 `DistillationRunner`：`scripts/rsl_rl/play.py:126-129`
- 注册蒸馏任务时另写一个 `rsl_rl_cfg_entry_point`（如 `Unitree-Go2-Velocity-A3` / 或同任务传不同 agent cfg）

## 实施记录（2026-10-17 晚，py_compile 通过、未 GPU 实测）

**关键机制修正**：原备忘说"train.py 有 Distillation 分支"——实际上 train.py **只**在 `algorithm.class_name == "Distillation"` 时强制 load ckpt，runner 构造却硬编码 `OnPolicyRunner`（`eval("StudentTeacher")` 在其命名空间不存在，会直接 NameError）。**已给 train.py 加了与 play.py 相同的 class_name 分发**（eval_terrain.py 同步加了）。

**已实现**（全部是增量，不影响现有 `Unitree-Go2-Velocity` 任务与在跑 A2 run）：

- `velocity_env_cfg.py` 新增 `ScanObservationsCfg`（继承原 ObservationsCfg，policy/critic 组原样，**另加 `teacher` 组** = policy 全部 proprio 项（**无噪声**）+ `height_scanner`，history_length=5、concatenate_terms=True）及 `RobotScanEnvCfg`/`RobotScanPlayEnvCfg`。
- 新文件 `tasks/locomotion/agents/rsl_rl_distill_cfg.py`：
  - `Go2ScanPPORunnerCfg`（Stage A）：`obs_groups = {"policy": ["teacher"], "critic": ["critic"]}`——PPO actor 直接吃 teacher 组，**训出来的 actor 就是教师**，无需单独教师组结构。
  - `Go2DistillationRunnerCfg`（Stage B）：`obs_groups = {"policy": ["policy"], "teacher": ["teacher"]}`，StudentTeacher [512,256,128]×2，norm 双开。
  - **两 cfg 共用 `experiment_name="unitree_go2_velocity_a3"`**：`get_checkpoint_path` 按 `<experiment>/<load_run>/<ckpt>` 正则解析，教师 ckpt 必须在同一 experiment 目录下才能被 `--load_run` 找到。
- `go2/__init__.py` 注册两任务：`Unitree-Go2-Velocity-Scan`（Stage A）、`Unitree-Go2-Velocity-Distill`（Stage B），共享 env cfg。
- `eval_terrain.py` runner 按 `agent_cfg.class_name` 分发（同 play.py），可评蒸馏学生；另加 `--agent_cfg module:Class` 直接按类路径换 agent cfg（experiment_name 随之切换→load_run 自动落在对的 experiment 目录）。
- **Held-out 验收地形已定并实施**：`HELDOUT_TERRAINS_CFG`（同文件）= `boxes`（MeshRandomGrid，高 0.05–0.2，参用 canonical ROUGH_TERRAINS_CFG）40% + `gap`（MeshGap，缝宽 0.1–0.5）30% + `discrete_obstacles`（HfDiscreteObstacles，障碍高 0.01–0.2）30%——三种训练集里完全没有的类型。`RobotHeldoutEnvCfg(RobotScanEnvCfg)` 仅换 generator（保留全部三组观测，teacher 组在 → 盲学生/教师/蒸馏 ckpt 都能评）；`curriculum=True` 烘进 generator，行列语义与训练网格一致。注册 `Unitree-Go2-Velocity-Heldout`（agent cfg 默认 BasePPORunnerCfg）。用法：`--task Unitree-Go2-Velocity-Heldout --load_run <run> [--agent_cfg ...:Go2ScanPPORunnerCfg|Go2DistillationRunnerCfg]`。

**已核实的加载链路**：`StudentTeacher.load_state_dict` 检测到 `"actor."` 键自动重映射进 teacher 网络（PPO ckpt 直接喂）；actor 输入维 = teacher 组维（Stage A 的 `["policy"]=["teacher"]` 保证了这一点）。stage B CLI：`--load_run <教师run目录名> --checkpoint model_N.pt`。

**重要修正（2026-10-17 晚第二轮）**：本管线所有 PPO ckpt **不含任何 `*_obs_normalizer.*` 键**——`RslRlPpoActorCriticCfg` 的 normalization 字段是 MISSING→序列化成 `{}`→falsy→`Identity()`，`empirical_normalization:true` 实际未生效（观测归一化全管线从未开启，A2 也一样）。因此 `Go2DistillationRunnerCfg` 的 `student/teacher_obs_normalization` **必须 False**——`StudentTeacher.load_state_dict` 会 strict 加载 `teacher_obs_normalizer`，设 True 会因缺键直接崩（原备忘"norm 双开"是错的，已改）。同时 `TeacherCfg` 里 `height_scanner` 已挪到**组末**（history 是 per-term 展平，proprio 块占前 235 维连续）→ 新增 `scripts/rsl_rl/expand_actor_obs.py` 可把盲 actor ckpt 扩成教师输入（`actor.0.weight` 末尾补零列 + 优化器态同步扩；`--add_dim 935`=187ray×hist5），warm-start 已在 CPU 端到端验证（strict load + forward + 权重块非零/scan 块全零）。教师两路线齐备：(a) 从头训（~16h）或 (b) `expand_actor_obs.py` 暖启动（--set_iter 0 可从 0 计迭代）。

**成本备注**：`height_scanner` RayCaster **早已常驻场景**（RobotSceneCfg 一直实例化、update_period 已配，A2 也付着 raycast 开销）——Scan 任务新增的只是观测拼接 + history 堆叠内存，不是 raycast 本身。num_envs 可先从 2048 试，OOM 再降。

**剩余待决策**：教师训练是否要先等 eval_terrain.py 定下盲策略天花板；若教师 stage-A 仍卡 ~10cm 需调奖励（feet_clearance 目标高/feet_stumble 权重）。~~held-out 第 6 地形~~ → 已定（HELDOUT_TERRAINS_CFG，见上）。

## Stage-A 奖励 Plan-B 预案（教师仍卡 ~10cm 时启用，先改档不实施）

判读前提：eval 显示盲策略在 stairs level 3-4（10-12cm）摔倒率陡升 = 天花板实锤；Stage A 教师训 ~3-5k iter 后若 eval 仍卡同行 → 按序试下表（一次只动一项，便于归因）：

| 序 | 改动 | 依据 |
|---|------|------|
| 1 | `feet_clearance.params.target_height` 0.05→0.10（`RobotScanEnvCfg` 或新建 `RobotScanClimbEnvCfg` 子类覆写，不动 A0-A2 cfg） | `foot_clearance_reward = exp(-Σ(z-0.05)²/0.05)·tanh(2·v_xy)`——峰值在 5cm 抬脚，对 15cm 台阶奖励信号错位；抬到 10cm 对齐目标步高（留 5cm 余量防过度高抬） |
| 2 | `feet_stumble.weight` -0.5→-0.25 | stumble 罚的是"足底水平方向撞击"——上台阶本来就要踢踏竖板，-0.5 直接惩罚台阶接近行为 |
| 3 | 可选加 `feet_height_body`（mdp 已有此 func，未启用）：weight ~0.2, target_height 0.1, tanh_mult 2.0 | 对地抬腿高度的软塑形，与 clearance 互补（clearance 管摆动期，height_body 管绝对抬升） |
| 4 | 最后手段：`track_lin_vel_xy` std sqrt(0.25)→sqrt(0.35) 放宽核宽容度 | 台阶行跟踪误差天然大，核太窄→奖励梯度消失；放宽给学习留梯度。副作用：平地跟踪精度略降 |

注意：只动 `RobotScanEnvCfg`/`RobotScanPlayEnvCfg` 的继承链（新建子类覆写 RewardsCfg），**绝不动 `RobotEnvCfg`**——A2 基线可复现性优先。蒸馏学生无需同步改（学生学教师行为，不学奖励）。

## 启动链路终验（2026-10-17 晚第三轮，对安装版源码逐环核对）

- `cli_args.update_rsl_rl_cfg` 把 `--resume/--load_run/--checkpoint/--run_name/--seed/--logger` 写进 agent_cfg；`--max_iterations` 由 train.py:126 单独应用（"再训 N iter"语义：runner 从 ckpt iter 起算 learn N）。BasePPORunnerCfg 与 RslRlDistillationRunnerCfg 都继承 `RslRlBaseRunnerCfg`（含 resume/load_run/load_checkpoint 全部字段）——两阶段 CLI 语义一致。
- **`obs_groups` 空 dict 机制**：`BasePPORunnerCfg` 根本没设 `obs_groups`（继承 MISSING）→ `to_dict()`（= `class_to_dict`，逐 `__dict__` 项）把 MISSING 哨兵序列化成 `{}` → `resolve_obs_groups` 回退逻辑自动填 `{"policy":["policy"],"critic":["critic"]}`（A1/A2 就是这么跑的，agent.yaml 里 `obs_groups: {}` 实证）。我们两 cfg 写的是显式 dict，跳过回退直接校验：`{"policy":["teacher"],"critic":["critic"]}`（Stage A）与 `{"policy":["policy"],"teacher":["teacher"]}`（Stage B）引用的组在 `ScanObservationsCfg` 里全部存在（policy/critic/teacher 三组）。OnPolicyRunner `default_sets=["critic"]`、DistillationRunner `default_sets=["teacher"]`——集合名约定匹配。
- `DistillationRunner(OnPolicyRunner)` 构造签名相同（train.py 同形调用可行），`learn()` 首查 `policy.loaded_teacher`；`load(path, map_location=)` 继承自 OnPolicyRunner——train.py 的 `runner.load(resume_path, map_location="cpu")` 合法。
- `StudentTeacher.load_state_dict`：ckpt 含 `actor.*` 键 → 重命名灌入 teacher 网络 + `teacher_obs_normalizer.load_state_dict({})`（norm=False → Identity 无状态，strict 空载安全）；返回 False → runner 不加载 optimizer 态（蒸馏从头）。已 `learn()` 守卫 loaded_teacher。
- `eval(...class_name)` 在 runner 模块命名空间 eval——`StudentTeacher`/`Distillation` 均已在 distillation_runner.py 顶部 import，无 NameError 风险（train.py 的分发是 `hasattr(agent_cfg,"class_name")` + 显式 elif，不走 eval）。
- 结论：**Stage A/B 命令行→runner→权重加载全链路已无可查环节**，仅剩 GPU 运行时（USD 场景构建/RayCaster/显存）未实测。
