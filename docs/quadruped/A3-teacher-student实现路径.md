# A3 实现备忘：height scanner + Teacher-Student 蒸馏

> 2026-10-17 调研结论（只读代码未实施）。前提：A2 盲策略在台阶上平台化后，按路线图进入 A3。依赖已确认存在：rsl_rl 3.0.1 内置 `runners/distillation_runner.py` + `algorithms/distillation.py` + `modules/student_teacher.py`。

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
