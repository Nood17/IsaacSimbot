# 长线自主迭代 — 任务提示词

> 本文件由 `run-iteration.sh` 通过 `devin -p --prompt-file` 注入每一轮新会话。
> 按需修改使命与收口规则；改动对下一轮生效。

## 使命（Mission）

<!-- TODO: 写清楚这次长线迭代的总目标，例如：
     "持续改进 G1 月面重力 locomotion 策略，直到 sim-to-sim 迁移通过全部验收指标" -->

当前主线为**任务 A：Go2 四足机器狗复杂地形训练**——按 `I:\仿真\docs\quadruped\路线图-Go2复杂地形训练.md`（WSL 内 `/mnt/i/仿真/docs/quadruped/`）分阶段推进，目标是学会"难任务仿真训练"的完整方法论（奖励设计、课程、域随机化、checkpoint 评估），而非追求最高 reward。每阶段有明确的行为验收标准（摔倒率/跟踪误差/per-terrain 分解/3 seeds），未达标不进下一阶段。

任务 B（lunar-grav-loco 双足 G1）**暂停**：地球基线纸面指标正常但实际行为差（指令课程卡 1 级、偏航跟踪失效）。不要续训 G1、不要跑月面重力任务，除非路线图全部 A 阶段完成且完成 `docs/biped/状态-G1基线诊断.md` 的诊断清单。

注意环境要点：本机为 WSL2 + RTX 4070 Ti 12GB；训练前必须 `conda activate env_isaaclab`（其 activate.d 会 export `LD_LIBRARY_PATH` 含 `~/仿真/wsl_lib_links` 与 `/usr/lib/wsl/lib`，否则 PhysX GPU 初始化失败进程静默退出），非交互运行需 `OMNI_KIT_ACCEPT_EULA=YES`。

## 每轮工作规则

1. 先读 `.devin/handoff.md`，继承上一轮留下的状态与下一步计划。
2. 每轮只做**一个可验证的增量**：改代码/调参 → 跑验证 → 记录结果。
3. 跑长耗时任务（训练、仿真）时优先用后台/短步验证，避免单轮无输出卡死被 watchdog 杀掉。
4. 不破坏已有可复现基线；实验改动前先备份相关配置。

## 收口规则（Closing）

每轮结束前，把以下内容**覆写**到 `.devin/handoff.md` 顶部区块：

```
## 状态 YYYY-MM-DD HH:MM
- 本轮做了什么：
- 验证结果：
- 下一步建议：
```

（更早的区块往下堆叠，不要删除历史。）

## 完结条件（Mission complete）

当使命达成、没有剩余待办时：在 `.devin/handoff.md` **最顶部**单独写一行：

```
MISSION-COMPLETE
```

调度器检测到该行后会自动停掉 timer，结束整个迭代循环。
