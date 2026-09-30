---
原文标题: Autonomous Legged Mobile Manipulation for Lunar Surface Operations via Constrained Reinforcement Learning
中文译名: 基于约束强化学习的月面自主腿式移动操作
来源/arXiv: arXiv:2510.12684v1 [cs.RO]（2025年10月14日）
翻译日期: 2026-09-30
---

# 基于约束强化学习的月面自主腿式移动操作

**Alvaro Belmonte-Baeza¹、Miguel Cazorla¹、Gabriel J. García²、Carlos J. Pérez-Del-Pulgar³、Jorge Pomares²**

¹ Alvaro Belmonte-Baeza 与 Miguel Cazorla：西班牙阿利坎特大学（University of Alicante）计算机科学与人工智能系。通讯作者：alvaro.belmonte@ua.es
² Gabriel J. García 与 Jorge Pomares：西班牙阿利坎特大学物理、系统工程与信号理论系。
³ Carlos J. Pérez-Del-Pulgar：西班牙马拉加大学（University of Málaga）系统与自动化工程系。

*本研究由 MICIU/AEI/10.13039/501100011033/FEDER（欧盟）资助项目 PID2024-160373OB-C22 及 FPU21/02586 奖学金支持。*

## 摘要

机器人技术在行星科学与探测中扮演着关键角色——由于空间环境固有的风险与挑战，自主、可靠的系统至关重要。建立永久性月球基地需要能够在恶劣月面地形中导航与操作的机器人平台。虽然轮式巡视器一直是行星探测的主力，但其在非结构化与陡峭地形上的局限促使人们采用腿式机器人——后者提供了更强的机动性与适应性。本文提出一种面向在月球环境中作业的自主四足移动操作机器人（mobile manipulator）的约束强化学习（constrained reinforcement learning, CRL）框架。所提框架将全身（whole-body）运动与操作能力相结合，同时显式处理关键安全约束——包括碰撞避免、动态稳定性与能量效率——以确保在月球特有条件（如低重力与不规则地形）下的鲁棒性能。实验结果表明，该框架能够实现精确的六维（6D）任务空间末端执行器（end-effector, EE）位姿跟踪，平均位置精度达 4 cm、姿态精度达 8.1 度。系统始终同时遵守软约束（soft constraints）与硬约束（hard constraints），并展现出针对月球重力条件优化的适应性行为。本工作有效地将自适应学习与任务关键的安全需求相衔接，为未来月球任务中先进的自主机器人探测器铺平了道路。

【图1：本工作使用的、位于月球环境中的腿式移动操作机器人。图中展示了在四足机器人（Unitree Go2）背部安装 6 自由度机械臂构成的腿式移动操作平台，置于模拟月面场景中，用于说明本文研究的系统形态。】

## I. 引言

机器人系统对现代行星探测不可或缺——由于太空任务固有的极端风险与通信延迟，自主运行、精确性与可靠性必不可少。即将建立的永久性月球基础设施以及原位资源利用（in-situ resource exploitation），要求机器人平台能够在不仅遥远而且极端严酷的环境中执行复杂的操作与移动任务。NASA 的阿尔忒弥斯（Artemis）[1] 与中国的嫦娥 [2] 等任务，凸显了对机器人系统执行长时月面作业日益增长的依赖。

迄今为止，行星探测主要依赖轮式巡视器，它们展现了出色的鲁棒性与简洁性。然而，在陡坡、不平整表面与松软风化层（regolith）上——这些正是月面景观的主导条件——其性能严重下降。因此，行星机器人界正将注意力转向腿式机器人，它们提供了更强的适应性与地形可达性。若干研究原型，包括 SpaceClimber [3]、ATHLETE [4] 与 SpaceBok [5][6]，已探索了面向太空探测的腿式移动能力的各个方面——从静稳定攀爬到为低重力运动优化的高动态步态。这些发展表明，腿式系统可以将行星任务的可达范围扩展到轮式巡视器此前无法进入的区域。

除移动能力外，未来的月面作业还将要求机器人不仅能穿越崎岖地形，还能执行样本采集、栖息地建造与设备维护等操作任务。四足移动操作机器人是一种尤其有前景的解决方案，因为它将腿式运动的机动性与关节机械臂的灵巧性结合在一起（见图 1）。然而，对这两个子系统的协调引入了一个高维控制问题，需要围绕平衡、力与安全约束进行实时的全身推理（whole-body reasoning）。

强化学习（reinforcement learning, RL）近来已成为在高维机器人系统中实现鲁棒、自适应控制行为的强大范式。基于 RL 的控制器已在四足与人形机器人运动 [7]–[9]、灵巧操作 [10] 以及一体化导航 [11][12] 中达到最先进的性能。更近期地，若干工作探讨了全身移动操作（whole-body loco-manipulation），即联合学习运动与操作以完成协调任务。例如，文献 [13][14] 展示了机身与机械臂的联合控制，但前者中操作与运动分开处理，后者中操作由单独的、计算密集的扩散策略（diffusion policy）完成。其他方法确实将末端执行器跟踪与平衡控制相集成，以在平坦与不规则地形上实现适应性行为 [15]–[17]。然而，这些框架通常面向地球环境，缺乏保证形式化安全属性的机制——而在行星条件下，故障不可挽回，形式化安全是自主运行的基本要求。

这些基于学习的全身控制进展，因其能够从经验中学习并适应不确定环境，正日益被视为在行星机器人系统中实现自适应与智能行为的关键。此外，这些策略使用的神经网络架构通常是简单的多层感知机（Multi-Layer Perceptron, MLP），可用更有限的计算资源部署。然而，基于学习的控制器缺乏形式化安全保证，仍在阻碍空间机器人界将这类技术应用于行星领域。

在月面上作业带来了超越地球环境的独特挑战。月球更低的重力（约为地球的六分之一），加上高度不规则的地形、松软的风化层与无大气环境，使得微小的控制失稳可能迅速演变为灾难性故障。此外，受限的通信带宽与时延排除了直接人工监督。因此，具有安全意识的自主性（safety-aware autonomy）至关重要：月球机器人必须能够自我保护式运行，即使面对扰动或地形特性不确定性也能保持稳定性与效率。

在此背景下，约束强化学习（Constrained Reinforcement Learning, CRL）为将 RL 的自适应能力与显式安全保证相结合提供了有原则的框架。与仅优化奖励函数的传统 RL 不同，CRL 融入了所学策略在训练与执行过程中都必须满足的任务相关约束 [18]。该范式已在地面腿式运动 [19]–[22] 与新兴的移动操作任务 [23][24] 中展现出提升安全性与鲁棒性的前景。然而，其在行星机器人——尤其是在月球条件下作业的腿式移动操作机器人——中的应用迄今尚未被探索。

本文提出一种面向月面作业的自主腿式移动操作机器人的约束强化学习框架。我们的框架在月球特有的环境条件下实现一体化的运动与操作控制，将碰撞避免、稳定性维持与能量效率等安全关键约束显式嵌入学习过程。由此，该方法将自适应学习与形式化安全考量相结合——这两个方面在行星机器人中很少被统一起来。

本工作的主要贡献包括：

- **全身协调（Whole-Body Coordination）：** 我们提出一种一体化控制架构，联合优化运动与操作行为，以利用系统全部自由度执行任务，实现动态稳定与协调运动。
- **六维任务空间末端执行器跟踪（6D Task-space EE tracking）：** 我们的 CRL 形式化实现了任务空间中精确的六维末端执行器位姿跟踪，平均位置精度 4 cm、姿态精度 8.1°，可与最佳地面基准相比。
- **安全强化学习架构（Safe RL Architecture）：** 该方法施加了涵盖碰撞避免、力矩与速度限制、能量效率与机体姿态安全的显式软、硬约束——这对低重力环境中的自主运行至关重要。
- **环境适应（Environmental Adaptation）：** 该框架通过域随机化（domain randomization）与随机化约束执行，学习在崎岖、不平整、低重力地形上作业，展现出诸如月球重力下节能步态等涌现行为（emergent behaviors）。

通过这些贡献，我们的方法弥合了自适应学习型控制与真实月球机器人任务所需可靠性之间的差距。通过将安全约束显式纳入学习过程，本工作向能够在地外环境中执行复杂科学与操作任务的自主四足移动操作机器人迈出了重要一步。

## II. 背景

### A. 约束强化学习问题

在强化学习框架中，我们通常将序列决策问题（如机器人控制）建模为马尔可夫决策过程（Markov Decision Process, MDP）。MDP 由元组 $(S, A, R, P)$ 定义，其中 $S$ 为状态空间，$A$ 为动作空间，$R : S \times A \times S \to \mathbb{R}$ 为奖励函数（将经由动作发生的状态转移映射为标量奖励），$P : S \times A \times S \to [0, 1]$ 给出智能体采取动作 $A$ 时从一状态转移到另一状态的概率。RL 问题的目标是找到最大化期望累积奖励的策略 $\pi : S \to A$：

$$
J(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t\, r(s_t, a_t, s_{t+1})\right], \tag{1}
$$

其中 $\gamma \in [0, 1)$ 称为折扣因子（discount factor），用于权衡短期与长期奖励的相对重要性。

为处理受约束的序列决策问题，上述框架可扩展为约束马尔可夫决策过程（Constrained MDP, CMDP）。为此，我们引入一组以代价函数（cost functions）表示的约束 $C$ 及其关联的限制 $L$。由此，每个定义的约束 $c_i \in C$ 将一次状态转移映射为该转移的代价，产生代价函数：

$$
J_{c_i}(\pi) = \mathbb{E}\left[\sum_{t=0}^{\infty} \gamma^t\, c_i(s_t, a_t, s_{t+1})\right]. \tag{2}
$$

在这些考虑下，约束学习问题寻求在保持未来代价 $c_i$ 的折扣和处于其定义上限 $l_i$ 之内的同时，最大化公式 (1) 所述目标函数的策略：

$$
\pi^* = \arg\max_{\pi}\ J(\pi) \quad \text{s.t.} \quad J_{c_i}(\pi) \leq l_i,\ \forall i \in \{1, \dots, L\}, \tag{3}
$$

从上述形式化可以看出，约束 RL 设置引入了一组 $C$ 个代价函数，每个都需要用独立的评论家网络（critic networks）处理，因此需要专门的算法实现，阻碍了直接使用现成的知名 RL 算法实现。

### B. 约束即终止（Constraints as Terminations, CaT）

约束即终止（CaT）框架 [21] 旨在降低实现复杂性，其做法是重新形式化约束 RL 目标，优先保证简洁性与易用性。为此，在策略学习期间引入随机化终止（stochastic terminations）以强制执行期望约束，使得对约束的任何违反都意味着从该时刻起有一定概率终止其未来奖励。

回顾公式 (3)，其中的不等式引入了约束的"预算/额度"（budget/allowance）概念。这可以重新表述为：最大化奖励，同时避免违反约束，即 $P(s,a)\cdot[c_i(s,a) > 0] \leq \tilde{l}_i,\ \forall i \in L$。该简化只对一般约束 RL 框架的特殊情形成立，但对大多数机器人控制 RL 应用已经足够。

因此，CaT 框架将公式 (1) 中的学习目标重新形式化为：

$$
\max_{\pi}\ \mathbb{E}_{\tau \sim \pi}\left[\sum_{t=0}^{\infty} \prod_{t'=0}^{t} \gamma^{t'}\,(1 - \delta(s_{t'}, a_{t'}))\; r(s_t, a_t)\right], \tag{4}
$$

其中 $\delta_t \in [0, 1]$ 为表示回合是否在时刻 $t$ 终止的随机变量——若终止，其后所有未来奖励均不被智能体获得。$\delta_t$ 自然是约束 $c_i$ 的函数，其取值取决于对这些约束的违反情况。此外，CaT 形式化让 $\delta_t$ 在 $[0,1]$ 区间内取值，从而形成随机终止：依据当前时刻的约束违反程度，以概率方式截断未来奖励。

按此推理，每个时刻 $\delta$ 依下式计算：

$$
\delta = \max_{i \in I}\; p_i^{max} \cdot \mathrm{clip}\!\left(\frac{c_i^+}{c_i^{max}},\, 0,\, 1\right), \tag{5}
$$

其中 $c_i^+ = \max(0, c_i(s,a))$ 为约束 $c_i$ 的违反量，$c_i^{max}$ 为在训练中对每批采集数据经验更新的最大约束违反量的滑动平均。clip 运算将 $\frac{c_i^+}{c_i^{max}}$ 项限制在 $[0,1]$ 区间内。

通过这些修改，CaT 框架允许将 PPO 等最先进的 RL 算法便捷地集成进约束 RL 框架：只需将所得奖励乘以因子 $(1-\delta)$，并用 $\delta$ 更新回合终止标志即可。

## III. 方法

我们提出对腿式移动操作问题的约束强化学习形式化，以实现对一个由四足机器人与安装在机体顶部的机械臂构成的机器人系统的安全、鲁棒的全身控制。施加于系统的约束对学习过程进行调制：违反任何约束都会使智能体无法获得约束未被满足期间采集到的部分奖励。这自然地使智能体趋向于满足约束，以最大化所获奖励。

在本节中，我们描述用于在月球环境中通过腿式移动操作系统的全身控制来跟踪期望任务空间六维末端执行器位置的框架。我们首先给出马尔可夫决策过程的各个组成部分，以形式化描述该序列决策问题，其中重点给出奖励函数形式化的关键细节，以实现对期望任务空间位姿的精确高效跟踪。随后我们定义施加于智能体的约束，以确保策略在学习手头任务时考虑到一组安全保证。所提方法的总览见图 2，各模块在以下小节中描述。

【图2：所提方法的总览框图。图中展示了策略网络接收观测（机体姿态、速度、关节状态、前一动作、足部接触、LiDAR 高度扫描、期望 EE 位姿），输出关节位置目标，经低层 PD 控制器驱动四足机器人与机械臂；同时约束模块基于 CaT 计算终止系数 $\delta$，对违反约束的奖励按比例截断，用于训练中的安全执行。】

### A. 全身腿式移动操作问题形式化

我们的目标是训练一个能够在任务空间中安全跟踪六维末端执行器位姿的策略。大多数先前工作相对于机器人机体系（body frame）定义全身跟踪问题，因为这只需局部信息即可简化策略学习。然而，如果机器人机身因某种原因发生位移，由于机身与 EE 的相对位置未变，末端执行器位置也会随之改变。这种行为在第 I 节所述的应用场景中是不可取的——我们希望按任务空间坐标精确地操作或检查特定区域。

因此，我们必须定义一个正确刻画期望任务的 MDP，即以全身协调跟踪期望 EE 位姿。下面详述实现期望行为的具体形式化。

**1) 任务空间中的末端执行器位姿指令：** 我们将指令定义为任务空间中的期望末端执行器位姿 $p_{ee} \in SE(3)$。学习期间，指令在机器人附近的一定范围内随机采样为六维位姿，使机器人可能需要穿越一段地形才能到达，但无需移动很远。我们认为该定义足以满足本问题，因为此处学习的策略并非用于长距离运动；相反，我们会在机器人处于感兴趣的局部区域（希望对其检查或采样）时部署该策略。

**2) 动作与观测空间：** 动作空间定义为机械臂与四足机器人腿部双方的期望关节位置。本工作中，所用机械臂具有 6 个自由度，四足机器人有 4 条腿、每条腿 3 个关节，因此 $a_t \in \mathbb{R}^{18}$。策略输出的目标位置先经处理，再发送给机械臂与腿部各自的低层 PD 控制器。原始策略动作乘以缩放因子 $\sigma$ 并叠加到默认关节位置上，即 $q^{*,t} = a_t \cdot \sigma + q_{default}$。

观测空间需要包含使移动操作机器人正确执行期望任务空间跟踪任务的全部相关信息——既包括刻画机器人状态的本体感知（proprioceptive）信息，也包括使运动适应机器人需穿越的崎岖月面地形的外部感知（exteroceptive）信息。

因此，我们的观测向量包括：由投影重力向量（projected gravity vector）定义的机器人机身姿态；机身线速度与角速度；系统所有关节的关节位置与速度（完整的关节空间状态信息）；策略上一步施加的动作；以及表示四足各足接触状态的四维布尔向量（用于评估机器人稳定性及与环境的交互）。对外部感知，加入由安装在机器人"下巴"处的 LiDAR 执行的高度扫描（height scan），提供局部地形高程信息。

最后，向策略输入任务空间中的当前期望 EE 位姿。关键在于，虽然目标按第 III-A.1 节所述在任务坐标系中生成，但在将其加入观测向量之前，我们先将其变换到机体系。这样做既保留了局部信息对策略学习的益处，又维持了任务空间位姿的定义——正如任务规划器（mission planner）会提供的那样。

为便于参考与记号清晰，表 I 列出了策略所用的观测。

**表 I：策略观测**

| 观测名称 | 表达式 |
|---|---|
| 投影重力向量（Projected gravity vector） | $\varphi_b$ |
| 机身线速度与角速度（Body linear and angular velocities） | $v_b,\ \omega_b$ |
| 关节位置与速度（Joint positions and velocities） | $q,\ \dot{q}$ |
| 前一动作（Previous actions） | $a_{t-1}$ |
| 高度图扫描（Height map scan） | $h$ |
| 期望末端执行器位姿（Desired end-effector pose） | $p_{ee}^*$ |

**3) 全身移动操作的奖励函数：** 任务空间末端执行器位姿跟踪场景有两个主要问题需要在奖励函数形式化中处理——奖励函数是引导策略学习期望行为的关键部分。

第一个问题是：像我们这样的移动操作任务本质上是一个两阶段的分层问题——首先需要利用系统的运动能力足够接近目标位姿，使其进入机械臂的可达范围；然后需要保持稳定的基座位置，使机械臂能够达到期望 EE 位姿。文献中这些任务通常被分开处理，因为各自本身就是复杂问题，将二者结合会带来额外困难 [13][15]。然而，分开处理运动与操作任务，就无法利用系统的全身控制（WBC）能力——而这些能力可能在某些关键任务中有所帮助，例如以有助于机械臂够到困难位姿的方式摆放四足机器人，或在基座移动中同时使用机械臂以节省宝贵的作业时间，甚至利用机械臂帮助基座在崎岖地形上保持平衡。

第二个问题与位姿跟踪任务本身有关。成功的六维跟踪意味着精确到达三维位置与三维姿态。这两个目标通常在奖励形式化中被分开处理，采用独立的位置与姿态跟踪奖励。这虽是可行方法，但引入了平衡两项权重的需求，以使两个量级都能被精确跟踪。平衡这些项并不直接，因为误差量级不同，且精确跟踪三维姿态已被证明尤其具有挑战性 [15]。

**a) 全身六维 EE 跟踪奖励：** 为同时应对这两个挑战，我们提出一种奖励形式化，它隐式处理运动与操作两个阶段，并内在地平衡位置与姿态跟踪，使任何一项都不会凌驾于另一项之上。

计算位姿奖励时，先分别计算位置奖励与姿态奖励。位置奖励定义为机体系中当前位置与期望位置之差的平方范数之和；姿态奖励为机体系中当前姿态与期望姿态的四元数差的幅值：

$$
e_{pos} = \sum \|p_{ee} - p_{ee}^*\|^2, \quad e_{rot} = quat_{ee} \ominus quat_{ee}^* \tag{6}
$$

其中四元数之差以两四元数间相对旋转的轴角表示（axis-angle representation）的幅值计算。随后，位置与姿态各自的奖励计算为：

$$
r_{pos} = e^{-\frac{e_{pos}}{\sigma_{pos}}}, \quad r_{rot} = e^{-\frac{e_{rot}}{\sigma_{rot}}} \tag{7}
$$

其中 $\sigma_{pos}$、$\sigma_{rot}$ 为调节指数衰减对误差敏感度的参数。最后，为内在地平衡这两项，将位姿跟踪奖励取为两项之积：

$$
r_{pose} = r_{pos} \cdot r_{rot} \tag{8}
$$

这样，以牺牲一项为代价提升另一项不会获得更高奖励；只有位置与姿态跟踪同时稳定提升，才能最大化奖励函数。

**b) 腿式移动操作奖励：** 公式 (8) 的奖励形式化未利用四足机器人作为移动操作基座的移动性。这可能导致策略学到过于激进的机械臂行为，因为没有显式奖励信号告知"将基座移近 EE 目标也有助于机械臂到达期望位姿"。

为向策略提供该信息，我们构造一个基座-目标门控奖励（body-to-target gated reward），鼓励机器人机身靠近期望 EE 笛卡尔位置至半径 $r$ 以内——在该半径内机械臂可以舒适地够到指令位姿。记 $d_{base} = \|p_{body,xy} - p_{ee,xy}^*\|$，则基座位置跟踪奖励定义为：

$$
r_{base} = e^{-\frac{d_{base} - r}{0.5}} \tag{9}
$$

其中下标 $xy$ 表示只用 XY 平面分量计算差值。基座与 EE 位姿组合跟踪奖励为：

$$
r_{task} = r_{pose} \cdot (g \cdot r_{base}) \tag{10}
$$

其中 $g = \mathrm{Sigmoid}(k \cdot (d_{base} - r)) \in (0.0, 1.0)$ 为门控因子，调节基座距离奖励的重要性。其直观含义是：移动操作机器人首先需要到达目标 EE 位置在 XY 平面上半径 $r$ 范围内，一旦进入该半径，即可获得位姿奖励项的最大值。

通过这种形式化，我们鼓励策略先让机器人移动到接近期望目标的位置，然后内在地平衡位置与姿态跟踪，以实现成功的六维位姿控制。此外，以连续方式（而非显式状态机与阈值）刻画这些不同阶段有利于学习，并带来任务阶段间平滑、自主的过渡。

**4) 能耗最小化奖励：** 最后，我们还希望引导学习智能体趋向于在实现目标的同时使能量消耗最低的动作。在 RL 文献中，这通常通过惩罚函数（penalty functions）处理——即负奖励，阻止策略采取某些动作。然而，由于我们采用的约束方法（详见第 II 节），负奖励反而会使违反约束有助于智能体最小化奖励损失，因为 $(1-\delta)$ 系数会同时削减施加给智能体的惩罚。

为适应这一特性，我们翻转惩罚形式化：不是在功率高时削减奖励，而是在功率低时给予更高奖励。做法是对每个关节施加的机械功率的平方范数之和施加指数核：

$$
r_{power} = \omega_{legs} \cdot e^{-\frac{\sum \|\dot{q}_{legs} \cdot \tau_{legs}\|}{\mu_{legs}}} + \omega_{arm} \cdot e^{-\frac{\sum \|\dot{q}_{arm} \cdot \tau_{arm}\|}{\mu_{arm}}} \tag{11}
$$

其中 $\omega_{legs}$、$\omega_{arm}$ 为各项的奖励权重，$\dot{q}$ 与 $\tau$ 分别表示腿部与机械臂关节的关节速度与力矩，$\mu$ 为归一化参数，对应各关节组的平均最大功率。

### B. 月面环境中安全、鲁棒移动操作的约束

在定义了主要任务奖励之后，我们现在聚焦于设定策略在学习奖励函数所描述任务时需要满足的约束。这些约束可以具有真实的物理意义（关节限位、最大力矩等），也可以描述机器人期望的行为，如不超过某个踏地步态力、不越过某个机体姿态阈值、或在某些速度限制内运动。

沿用先前工作的形式化 [21]，我们定义两类随机约束：**硬约束（Hard constraints）**——一旦违反，从该时刻起累积奖励立即终止；**软约束（Soft constraints）**——违反时以概率方式终止部分未来奖励。两类约束的概念区别在于：某些危险情形必须每次都避免（如机器人非足部部位与环境碰撞），而另一些情形我们希望避免但在万不得已时允许短暂的约束违反（如超过既定的速度限制）。

考虑到所用平台、手头任务以及月面作业施加的限制与安全保证，我们定义了以下一组在策略学习过程中使用的约束。

**a) 软约束：** 定义软约束 $c_{q_j}$、$c_{\dot{q}_j}$、$c_{\tau_j}$，将关节位置、速度与力矩限制在其工作范围与最大标称值之内（即：即使物理上可达，也希望避免峰值力矩与峰值速度）。此外，加入风格约束（style constraints）以获得期望的基座运动：设定 $c_v$ 将机身线速度限制在最大 0.25 m/s，设定 $c_{rot}$ 以 0.3 弧度为限避免机身过度旋转。最后，$c_{fstd}$ 约束各足所施加力分布的最大标准差，促使质量在足间均匀分布。这在我们的月面作业场景中至关重要——足部可能陷入月面风化层中，从而引发灾难性故障。

**b) 硬约束：** 定义一组硬约束，规定策略在执行期望任务时必须避免的情形。设定约束 $c_{contact}$：限制机器人除足部以外任何部位受到较大接触力。设定 $c_{fall}$ 约束：当机身滚转或俯仰角超过 90° 时触发，以避免几乎必然导致跌倒并损坏机器人的基座姿态。同理，设定最小机身高度约束 $c_{h,min}$，防止机身撞击地面。最后，为应对月面作业的极端情形，专门加入两条面向月球环境的约束：设定 $c_{f,max}$ 为机器人足部可施加的最大冲击力，以避免高力冲击使机器人与地面脱离接触、漂浮到危险高度，或损伤腿部导致急停；类似地，设定 $c_{h,max}$ 约束机器人在作业中允许的最大高度——允许利用月球低重力进行一定的漂浮与跳跃运动，但不至于离地过远而失去对局面的控制。

## IV. 实验结果

### A. 实现细节

我们训练移动操作策略，使其在满足一组用户定义约束的同时到达期望的末端执行器六维位姿。实验平台为 Unitree Go2 四足机器人，其背部安装 Interbotix WX250s 六自由度机械臂，如图 1 所示。为模拟月面探测的危险条件，我们将重力幅值减小到地球重力的 1/6，并生成形貌类似月球表面的崎岖、不平整地形。

每个训练回合中，在以机器人 XY 位置为中心、半径 1.2 m、高 0.7 m 的圆柱体内于任务空间采样目标 EE 位置；期望姿态在默认 EE 姿态 ±30° 范围内均匀采样。我们引入域随机化（domain randomization）技术以增强控制策略的鲁棒性：具体地，每次重置时将四足机器人质量在其标称值 ±10% 范围内随机化。我们还采用带延迟的 PD 控制器跟踪策略给出的期望关节位置，对控制动作施加最大 40 ms 的随机延迟。最后，对策略接收的观测加入高斯噪声，以模拟不完美的状态估计与传感器测量。

关于约束概率，软约束采用与文献 [23] 类似的概率课程（probability curriculum）：每个约束设有最小与最大终止概率，随训练进行线性增长。这些约束的最大值在全部训练时间的 60% 处达到，从而在训练初期允许更探索性的行为，并随基础技能的习得逐渐收紧约束。各约束项的最小与最大概率见表 II。

我们使用 NVIDIA Isaac Sim [25] 作为该任务的高保真物理仿真器，使用 NVIDIA Isaac Lab [26] 作为学习框架搭建学习环境。我们通过修改 RSL-RL 库 [27] 中的 PPO 实现，实现了文献 [21] 中约束 PPO 算法的定制版本。策略 $\pi_\theta$ 由具有三个隐藏层（神经元数分别为 512、256、128）的 MLP 参数化，激活函数为 ELU [28]。若未提前终止，每个训练回合持续 10 s；策略以 100 Hz 运行，底层 PD 控制器以 200 Hz 运行。我们使用 4096 个并行环境（每个环境一台机器人）训练 10000 次学习迭代，在配备单块 NVIDIA GeForce RTX 3090 GPU 的台式机上耗时约 5 小时。

### B. 结果

仿真实验在 4096 个环境中各运行单个回合，报告最终位姿跟踪误差均值以评估全身 EE 控制性能，并报告每个约束在所有测试环境中不被满足的平均时间占比，以评估所采用 CRL 形式化的有效性。

**a) 末端执行器任务空间位姿跟踪：** 按第 IV-A 节所述采样用于评估位姿跟踪性能的目标位姿，并按第 III-A.3 节奖励函数所述方式计算误差。我们的移动操作任务取得了平均位置误差 4 cm、姿态误差 8.1 度的成绩，与地面领域最先进移动操作工作的性能相当 [14][15]。位置与姿态误差分布见图 3：最大位置误差约为 10 cm，而绝大部分密度集中在 2–6 cm 位置误差区间。图 4 展示了机器人跟踪的一系列位姿，说明我们的腿式移动操作机器人成功利用其全部自由度到达期望位姿。此外，策略还表现出利用低重力条件的涌现行为：四足关节出现轻微的跳跃步态以最小化能耗，同时利用手臂与腿部的小幅运动在机动中保持稳定。

【图3：4096 个评估样本的位置误差与姿态误差分布直方图。显示位置误差主要集中在 2–6 cm，最大约 10 cm，用于直观展示跟踪精度的统计特性。】

【图4：全身 EE 位姿跟踪示例序列图。展示腿式移动操作机器人在不同构型下精确、安全的 EE 位姿跟踪——包括伸展、低姿态、跨越地形等多种情形，说明其可用于样本采集或表面检查等任务。】

**b) 约束满足情况：** 按先前工作 [22][23] 的做法，我们以每个约束被违反的回合时间平均占比衡量约束满足情况。表 II 给出了每个约束不被满足的回合时间平均百分比。可以看到，所有硬约束始终被策略遵守，确保在我们最严格的决策上实现鲁棒、安全的部署。软约束方面同样观察到成功的行为：最坏情况下每条约束被违反的平均时间占比 ≤ 0.08%，全部软约束的平均违反占比约为 0.01%。

**表 II：约束概率与实验约束满足结果**

| 约束 | $c_{q_j}$ | $c_{\dot{q}_j}$ | $c_{\tau_j}$ | $c_v$ | $c_{rot}$ | $c_{fstd}$ | $c_{contact}$ | $c_{fall}$ | $c_{h,min}$ | $c_{h,max}$ | $c_{f,max}$ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 最小概率 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| 最大概率 | 0.9 | 0.9 | 0.25 | 0.25 | 0.9 | 0.25 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| 回合违反时间占比 % | 0.002 | 0.0 | 0.004 | 0.08 | 0.02 | 0.005 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

## V. 结论

本文提出一种专为在挑战性月球环境中作业的四足移动操作机器人设计的约束强化学习（CRL）框架。所提方法成功集成了全身运动与操作能力，并利用包括碰撞避免、动态稳定性与功率管理在内的显式安全约束。

仿真实验评估表明，该方法在六维末端执行器位姿跟踪上表现优异：平均位置误差仅 4 cm，姿态误差约 8.1 度，达到最先进地面系统确立的性能标准。此外，CRL 框架展现出卓越的约束满足能力，在大规模测试中对硬约束与软约束均保持近乎完美的遵守。

值得注意的是，系统表现出利用月球低重力条件的涌现行为，采用高效、自适应的运动方式在保持任务效果的同时最小化能耗。这些结果凸显了所提基于 CRL 的方法在实现可靠、自适应、安全的月球探测任务自主移动操作方面的潜力，有效应对了空间机器人固有的关键运行挑战。

未来工作应寻求在更具挑战性的地形（如撞击坑或陡坡）上评估策略。此外，结合任务规划算法在真实月面类似地形中开展实验，将有助于验证本工作的适应性，并展示约束强化学习在挑战性真实场景中的潜力。

## 致谢

Alvaro Belmonte-Baeza 感谢 Elliot Chane-Sane 在我们为 IsaacLab 定制实现 CaT 期间所做的详尽讲解与帮助。

## 参考文献（保留原文）

[1] NASA, "Artemis," https://www.nasa.gov/humans-in-space/artemis/, National Aeronautics and Space Administration, 2025, accessed: 2025-07-28.
[2] Y. Jia, Y. Zou, J. Ping, C. Xue, J. Yan, and Y. Ning, "The scientific objectives and payloads of chang'e4 mission," Planetary and Space Science, vol. 162, pp. 207–215, 2018.
[3] S. Bartsch, T. Birnschein, F. Cordes, D. Kuehn, P. Kampmann, J. Hilljegerdes, S. Planthaber, M. Roemmermann, and F. Kirchner, "Spaceclimber: Development of a six-legged climbing robot for space exploration," in ISR 2010 (41st International Symposium on Robotics) and ROBOTIK 2010 (6th German Conference on Robotics), 2010, pp. 1–8.
[4] B. H. Wilcox, T. Litwin, J. Biesiadecki, J. Matthews, M. Heverly, J. Morrison, J. Townsend, N. Ahmad, A. Sirota, and B. Cooper, "Athlete: A cargo handling and manipulation robot for the moon," Journal of Field Robotics, vol. 24, no. 5, pp. 421–434, 2007.
[5] P. Arm, R. Zenkl, P. Barton, L. Beglinger, A. Dietsche, L. Ferrazzini, E. Hampp, J. Hinder, C. Huber, D. Schaufelberger, F. Schmitt, B. Sun, B. Stolz, H. Kolvenbach, and M. Hutter, "Spacebok: A dynamic legged robot for space exploration," in 2019 International Conference on Robotics and Automation (ICRA), 2019, pp. 6288–6294.
[6] H. Kolvenbach, P. Arm, E. Hampp, A. Dietsche, V. Bickel, B. Sun, C. Meyer, and M. Hutter, "Traversing steep and granular martian analog slopes with a dynamic quadrupedal robot," Field Robotics, vol. 2, pp. 910–939, 2022.
[7] D. Hoeller, N. Rudin, D. Sako, and M. Hutter, "Anymal parkour: Learning agile navigation for quadrupedal robots," Science Robotics, vol. 9, no. 88, p. eadi7566, 2024.
[8] T. Miki, J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, "Learning robust perceptive locomotion for quadrupedal robots in the wild," Science Robotics, vol. 7, no. 62, p. eabk2822, 2022.
[9] R. P. Singh, M. Morisawa, M. Benallegue, Z. Xie, and F. Kanehiro, "Robust humanoid walking on compliant and uneven terrain with deep reinforcement learning," in 2024 IEEE-RAS 23rd International Conference on Humanoid Robots (Humanoids), 2024, pp. 497–504.
[10] OpenAI, I. Akkaya, M. Andrychowicz, M. Chociej, M. Litwin, B. McGrew, A. Petron, A. Paino, M. Plappert, G. Powell, R. Ribas, J. Schneider, N. Tezak, J. Tworek, P. Welinder, L. Weng, Q. Yuan, W. Zaremba, and L. Zhang, "Solving rubik's cube with a robot hand," 2019.
[11] N. Rudin, D. Hoeller, M. Bjelonic, and M. Hutter, "Advanced skills by learning locomotion and local navigation end-to-end," 2022.
[12] D. Shah and S. Levine, "ViKiNG: Vision-Based Kilometer-Scale Navigation with Geographic Hints," in Proceedings of Robotics: Science and Systems, 2022.
[13] Z. Fu, X. Cheng, and D. Pathak, "Deep whole-body control: Learning a unified policy for manipulation and locomotion," in Conference on Robot Learning (CoRL), 2022.
[14] H. Ha, Y. Gao, Z. Fu, J. Tan, and S. Song, "UMI on legs: Making manipulation policies mobile with manipulation-centric whole-body controllers," in Proceedings of the 2024 Conference on Robot Learning, 2024.
[15] T. Portela, A. Cramariuc, M. Mittal, and M. Hutter, "Whole-body end-effector pose tracking," 2025.
[16] Z. He, K. Lei, Y. Ze, K. Sreenath, Z. Li, and H. Xu, "Learning visual quadrupedal loco-manipulation from demonstrations," in 2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2024, pp. 9102–9109.
[17] S. Li, G. Wang, Y. Pang, P. Bai, S. Hu, Z. Liu, L. Wang, and J. Li, "Learning agility and adaptive legged locomotion via curricular hindsight reinforcement learning," Scientific Reports, vol. 14, no. 1, 2024.
[18] J. Achiam, D. Held, A. Tamar, and P. Abbeel, "Constrained policy optimization," in International Conference on Machine Learning. PMLR, 2017, pp. 22–31.
[19] J. Lee, L. Schroth, V. Klemm, M. Bjelonic, A. Reske, and M. Hutter, "Exploring constrained reinforcement learning algorithms for quadrupedal locomotion," in 2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2024, pp. 11132–11138.
[20] Y. Kim, H. Oh, J. Lee, J. Choi, G. Ji, M. Jung, D. Youm, and J. Hwangbo, "Not only rewards but also constraints: Applications on legged robot locomotion," Trans. Rob., vol. 40, p. 2984–3003, Jan. 2024.
[21] E. Chane-Sane, P.-A. Leziart, T. Flayols, O. Stasse, P. Souères, and N. Mansard, "Cat: Constraints as terminations for legged locomotion reinforcement learning," in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2024.
[22] E. Chane-Sane, J. Amigo, T. Flayols, L. Righetti, and N. Mansard, "Soloparkour: Constrained reinforcement learning for visual locomotion from privileged experience," in Conference on Robot Learning (CoRL), 2024.
[23] I. Dadiotis, M. Mittal, N. Tsagarakis, and M. Hutter, "Dynamic object goal pushing with mobile manipulators through model-free constrained reinforcement learning," 2025.
[24] Y. Ma, A. Cramariuc, F. Farshidian, and M. Hutter, "Learning coordinated badminton skills for legged manipulators," Science Robotics, vol. 10, no. 102, p. eadu3922, 2025.
[25] V. Makoviychuk, L. Wawrzyniak, Y. Guo, M. Lu, K. Storey, M. Macklin, D. Hoeller, N. Rudin, A. Allshire, A. Handa, and G. State, "Isaac gym: High performance gpu-based physics simulation for robot learning," 2021.
[26] M. Mittal, C. Yu, Q. Yu, J. Liu, N. Rudin, D. Hoeller, J. L. Yuan, R. Singh, Y. Guo, H. Mazhar, A. Mandlekar, B. Babich, G. State, M. Hutter, and A. Garg, "Orbit: A unified simulation framework for interactive robot learning environments," IEEE Robotics and Automation Letters, vol. 8, no. 6, pp. 3740–3747, 2023.
[27] N. Rudin, D. Hoeller, P. Reist, and M. Hutter, "Learning to walk in minutes using massively parallel deep reinforcement learning," in Proceedings of the 5th Conference on Robot Learning, ser. Proceedings of Machine Learning Research, vol. 164. PMLR, 2022, pp. 91–100.
[28] D.-A. Clevert, T. Unterthiner, and S. Hochreiter, "Fast and accurate deep network learning by exponential linear units (elus)," 2016. [Online]. Available: https://arxiv.org/abs/1511.07289
