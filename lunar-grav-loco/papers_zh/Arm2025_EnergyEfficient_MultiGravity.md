---
原文标题: Energy-Efficient Learning-Based Control of a Legged Robot in Multiple Gravity Environments
中文译名: 多重力环境下腿式机器人的高能效学习型控制
来源: arXiv:2509.10128v2 [cs.RO]（2025-11-14）；ETH Zurich, Robotics Systems Lab
翻译日期: 2026-09-30
备注: 本地 PDF 文件交叉引用表损坏（疑似下载不完整），本译文基于从 arXiv 重新下载的同版本（v2）PDF 全文翻译。
---

# 多重力环境下腿式机器人的高能效学习型控制

**Philip Arm\*, Oliver Fischer\*, Joseph Church, Adrian Fuhrer, Hendrik Kolvenbach, Marco Hutter**

\* 共同一作。所有作者均任职于 ETH Zurich 机器人系统实验室（Robotics Systems Lab）；Leonhardstrasse 21, 8092 Zurich, Switzerland。联系方式：parm@ethz.ch

> 资助说明：本研究由瑞士国家科学基金会（SNF）通过国家能力研究中心数字制造方向（NCCR dfab）资助。LunarLeaper 项目感谢 CHiwi 基金会、SERI 的 NASO 计划（1-012571, LunarLeaper 2024）、Moog Inc. 与 maxon 的资助。

## 摘要

腿式机器人凭借其在非结构化地形上的出色移动能力，是探索月球、火星或小行星等低重力天体上困难区域的有力候选者。然而，由于行星机器人的功率与热预算高度受限，这些机器人需要能轻松迁移到多种重力环境的高能效控制方法。在本工作中，我们提出了一种基于强化学习的腿式机器人控制方法，采用随重力缩放的功率优化奖励函数（gravity-scaled power-optimized reward functions）。我们使用该方法在仿真中开发并验证了在从月球重力（$1.62\,\mathrm{m/s^2}$）到假想超级地球（$19.62\,\mathrm{m/s^2}$）的重力环境下的运动控制器（locomotion controller）与基座姿态控制器（base pose controller）。我们的方法借助随重力缩放的奖励函数，成功地在这些重力水平下实现了运动与基座姿态控制。在真实系统上，功率优化的运动控制器在地球重力下使一台 15.65 kg 的机器人以 0.4 m/s 行走时运动功耗达到 23.4 W，相比基线策略改善了 23%。此外，我们设计了一套恒力弹簧卸载系统（constant-force spring offload system），使我们能够在月球重力下进行真实世界的腿式运动实验。在该测试装置中，功率优化控制策略达到 12.2 W，比未针对功率效率优化的基线控制器低 36%。我们的方法为跨多个重力水平开发腿式机器人高能效运动控制器提供了一种可扩展的途径。

【图 1：我们的机器人可以使用随重力缩放的功率优化控制策略，在地球重力（左上）与月球重力测试装置（左下）中高效行走。此外，我们还创建了一个可在相同环境中工作的基座姿态跟踪控制器（右上与右下）。】

## I. 引言

对太阳系的机器人探测对于推进我们对太阳系的理解、并为未来载人登陆其他行星体的任务铺平道路至关重要。尽管轨道器与静止着陆器可以提供对其他行星体状况的初步认识，机器人表面任务对于回答更多科学问题、并为载人探索做准备不可或缺。许多有价值的探测目标——如月球南极附近的永久阴影区（permanently shadowed regions）、陨石坑壁与熔岩管（lava tubes）——都难以到达。因此，我们需要具备先进移动能力的机器人来深入这些挑战性环境。

迄今为止，用于行星探测的巡视器（rover）几乎完全依赖轮式移动：从第一台巡视器 Lunokhod 1 [1]，到火星巡视器 [2]–[4]，再到现代月球巡视器 [5], [6]。相应地，轮式系统可以依托数十年的飞行经验（flight heritage），在相对平坦的地形中提供可靠的移动能力。然而，在带有颗粒地形（granular terrain）的陡坡以及非结构化、高度不确定的环境中，它们会达到能力极限 [7]。

与此同时，腿式机器人在过去十年中在地球上展现了令人印象深刻的运动能力。在基于强化学习的控制的最新进展推动下，这些机器人现在可以探索非结构化的自然地形 [8]–[10]，并越过高于自身身高的障碍 [11], [12]。多个研究团队已研究了将腿式机器人用于行星探测 [13]–[16]。如今，腿式机器人已在模拟任务（analog mission）场景中成功应用，例如 ESA-ESRIC 太空资源挑战赛 2021-2022 [17], [18] 与 NASA BRAILLE 项目 [19]。

基于这些近期的成功，并考虑到月球坑洞周围的崎岖地形，我们为 LunarLeaper 任务¹选择了一台腿式机器人，用于探索月球表面的熔岩管 [20]。除了先进的运动能力外，腿式机器人在操作安装于基座上的仪器时还具有额外优势：它可以在站立时控制自身基座姿态。这一特性对诸如相机俯仰调整、天线对准以及太阳能帆板相对太阳定向等应用十分有用。然而，尽管腿式系统已被证明能在陡峭地形中良好运作并在模拟任务中体现价值，我们仍缺乏对腿式机器人在月球重力下基于强化学习控制的验证。

此外，由于月面上的功率与热约束，我们需要更加关注腿式机器人的高能效控制。

因此，本文聚焦于腿式机器人在多个任务与多重力环境下的高能效强化学习控制。虽然我们确实将控制器开发为能在崎岖地形上工作，但为保证可比性，我们将评估限制在平坦、刚性的地面上。具体而言，我们的贡献如下：

- 我们表明：以物理上有意义的方式使奖励函数随重力缩放，可以在不同重力环境下为多个任务产生可用的控制器。
- 我们在不同重力水平下比较了基线奖励函数与功率优化奖励函数，并验证了使用功率优化奖励函数能够在仿真与真实机器人上、在多个重力水平下得到高效率的运动控制器。

## II. 相关工作

### A. 太空中的腿式运动（Legged Locomotion in Space）

多个研究项目在陡坡与颗粒土壤上开展了腿式机器人的模拟运动测试 [13], [14], [22]。这些工作表明，腿式机器人可以在坚实地面穿越高达 35° 的坡 [14]，在火星模拟土壤上穿越 25° 的坡 [22]。一些团队甚至制造了能够攀爬垂直墙面的自由攀爬机器人 [23], [24]。尽管这些工作在挑战性地形上表现出色，但它们都未考虑行星探测中降低的重力。

另一些工作聚焦于低重力与微重力环境下的腿式移动 [25]–[28]。然而，这些工作要么仅限于仿真实验，要么在微重力下以降维（reduced dimensionality）方式验证系统。没有任何一项工作在月球重力下的真实机器人上研究并评估腿式运动。

### B. 高能效腿式运动（Power-Efficient Legged Locomotion）

多项工作已研究了使用深度强化学习开发更高能效运动策略的方法。在大多数工作中，功耗在仿真中基于关节力矩与速度值计算，并在训练过程中加以惩罚 [29], [30]。Valsecchi et al. [31] 训练了一个神经网络，根据在真实机器人上采集的数据由关节状态直接估计能耗；该数据驱动的功率模型随后被用于在训练中估计并惩罚功耗。Mahankali et al. 将功耗优化为辅助目标，约束条件是策略必须达到未加正则化的策略所能获得的最大任务奖励 [32]。尽管这些高效运动方法已在地球重力下得到广泛验证，但在不同重力水平下对这些基于功率的方法的验证仍然缺失。

## III. 方法

我们将控制器实现在改进版 Magnecko 四足机器人 [33] 上。Magnecko 是一台 15.65 kg、采用昆虫式构型（insect-style configuration）的机器人，腿长 0.5 m（图 1）。

我们基于现代强化学习流水线，为两个任务训练控制策略：一个是运动控制策略（locomotion control policy），用于跟踪平面速度指令；另一个是基座姿态控制策略（base pose control policy），用于跟踪基座高度、俯仰（pitch）与偏航（yaw）。这些策略使我们能够验证奖励的重力缩放（第 III-A 节）以及基线与功率优化策略在不同重力水平下的功耗（第 III-B 节）。第 III-C 节详细介绍两个策略的训练设置。

我们使用 IsaacLab 作为仿真环境 [34]，采用近端策略优化（Proximal Policy Optimization, PPO）作为深度强化学习算法 [21]，Actor 与 Critic 网络均为多层感知机（multi-level perceptron, MLP），隐藏层大小为 $\{512, 256, 128\}$。我们使用 Bjelonic et al. [35] 提出的系统辨识方法辨识了关节摩擦、阻尼与电枢（armature）参数，以实现有效的仿真到现实（sim-to-real）迁移。我们在一块 RTX 4090 GPU 上对每个策略训练 3000 次迭代，每次训练约需 3 小时。

【图 2：训练设置概览。我们采用非对称 Actor-Critic（asymmetric actor-critic）结构的 PPO [21]；基于第一性原理（first principles）使奖励函数随重力缩放，使我们的设置能够跨多个重力水平扩展。】

### A. 基于重力的奖励缩放（Gravity-Based Reward Scaling）

为设计基于重力的奖励缩放，我们考察多体系统的运动方程：

$$\tau = M(q)\ddot{q} + b(q, \dot{q}) + g(q) - J_c(q)^T F_c$$

其中：

| 符号 | 含义 |
|---|---|
| $\tau$ | 力矩（Torques） |
| $M(q)$ | 质量矩阵（Mass matrix） |
| $q,\ \dot{q},\ \ddot{q}$ | 位置、速度与加速度向量 |
| $b(q,\dot{q})$ | 科里奥利与离心项（Coriolis and centrifugal terms） |
| $g(q)$ | 重力项（Gravitational terms） |
| $J_c(q)$ | 接触力对应的雅可比矩阵（Jacobian） |
| $F_c$ | 接触力（Contact forces） |

由于 Magnecko 67% 的质量集中在基座与髋部执行器中，我们假设腿部产生的惯性力较小。进一步假设基座不经历高加速度，因此接触力 $F_c$ 由重力 $F_g$ 主导。作为重力缩放的一阶近似，我们相应地假设力矩近似与重力成正比：

$$\tau \propto g$$

我们将地球重力下奖励函数 $i$ 的默认奖励权重定义为 $w_{iE}$，定义重力因子 $\alpha_g = \frac{g}{g_E}$，其中 $g$ 为目标重力，$g_E$ 为地球重力。随后根据奖励函数与关节力矩的关系，用重力因子 $\alpha_g$ 对权重 $w_{iE}$ 进行缩放，以在不同重力环境中保持各奖励函数的相对量级。例如，对于惩罚关节功率之和 $\dot{q}\tau$ 的奖励函数，该函数随重力近似缩放为：

$$\dot{q}\tau \propto \tau \propto g$$

因此相应奖励函数的权重为 $w_i = \alpha_g w_{iE}$。类似地，力矩平方项的奖励函数缩放为：

$$\tau^2 \propto g^2$$

因此我们将其权重缩放为：

$$w_i = \alpha_g^2\, w_{iE} \tag{1}$$

### B. 功率优化正则化奖励（Power-Optimized Regularization Reward）

除了为不同重力水平定义奖励函数的缩放律外，我们还需要一个能在跟踪期望指令的同时最小化机器人功耗的奖励函数。先前工作表明，基于能量的奖励可生成鲁棒且高效的步态 [29], [32]。在本文中，我们将总功率损耗建模为回收损耗（recuperation loss）与绕组损耗（winding loss）之和（图 3）。齿轮箱损耗（gearbox loss）通过我们基于系统辨识流水线 [35] 在仿真中设置的阻尼参数隐式包含。因此我们不单独建模齿轮箱损耗，而将功率损耗奖励函数表述为：

$$r_{Power} = r_{Joint} + r_{Winding} \tag{2}$$

回收损耗计算为：

$$r_{Joint} = \max(\tau \cdot \dot{q},\ 0) - \min(\eta_{Recup} \cdot \tau \cdot \dot{q},\ 0) \tag{3}$$

Magnecko 的功率电子器件并未设计为能将能量回收到电池，因此本工作中设回收参数 $\eta_{Recup} = 0$。绕组损耗计算为：

$$r_{Winding} = \left(\frac{\tau}{G \cdot k_t}\right)^2 \cdot R \tag{4}$$

其中 $G$ 为减速比（gearbox ratio），$k_t$ 为力矩常数（torque constant），$R$ 为绕组电阻（winding resistance）。绕组损耗因绕组中的电阻发热而耗散。我们为功率奖励选取权重 $-3 \times 10^{-3}$，并对 $r_{Joint}$ 与 $r_{Winding}$ 两项分别应用奖励缩放：$r_{Joint}$ 按 $\alpha_g$ 缩放，$r_{Winding}$ 按 $\alpha_g^2$ 缩放。

【图 3：传动系统（drivetrain）中的功率损耗示意。回收损耗的产生是因为当传动系统制动时，并非所有动能都被有效转化为电能。】

### C. 运动与基座姿态控制的 MDP 建模（MDP Formulation）

我们分别训练了运动控制器与基座姿态控制器，以评估重力缩放与功率优化奖励的性能。对于运动控制器，指令定义为基座坐标系下基座的 x、y 方向速度与偏航速度：$c_{loco} = \left(_B v_{Bx},\ _B v_{By},\ _B\dot{\psi}_B\right)^T$。基座姿态跟踪控制器的指令为局部地形坐标系（terrain frame）下期望的基座高度、俯仰角与偏航角速度：$c_{base} = \left(_T r_{Bz},\ _T\theta_B,\ _T\dot{\psi}_B\right)^T$。动作 $a \in \mathbb{R}^{12}$ 控制机器人各关节 PD（比例-微分）控制器的目标关节位置，以 50 Hz 频率更新。目标位置 $q^*$ 计算为：

$$q^* = \sigma_a \cdot a + q_{def} \tag{5}$$

其中 $\sigma_a = 0.3$ 为启发式选取的动作缩放因子，$q_{def} \in \mathbb{R}^{12}$ 为默认关节位置。除指令形式不同外，两个控制器共享相同的观测。Actor 的观测 $o_a$ 包括：指令 $c_{task} \in \mathbb{R}^3$、过去 8 个时间步的 IMU 角速度读数 $\omega_{[t,\dots,t-8]} \in \mathbb{R}^{24}$、由 IMU 投影到基座坐标系的重力向量 $g_p \in \mathbb{R}^3$、关节位置 $q \in \mathbb{R}^{12}$、关节速度 $\dot{q} \in \mathbb{R}^{12}$，以及上一步动作 $a_{t-1} \in \mathbb{R}^{12}$：

$$o_a = \left[c_{task},\ \omega_{[t,\dots,t-8]},\ g_p,\ q,\ \dot{q},\ a_{t-1}\right] \in \mathbb{R}^{66} \tag{6}$$

Critic 的观测 $o_c$ 与 Actor 大致相同，唯一区别是 Critic 不接收 IMU 历史 $\omega_{[t,\dots,t-8]}$，而是接收基座真实运动旋量（ground truth base twist）$\xi \in \mathbb{R}^6$，使其观测为：

$$o_c = \left[c_{task},\ \xi,\ g_p,\ q,\ \dot{q},\ a_{t-1}\right] \in \mathbb{R}^{48} \tag{7}$$

表 I 列出了本工作中使用的所有奖励。两个控制器共享一组基础正则化项（base regularizations）。每个控制器还有单独的奖励函数用于跟踪各自的指令，并提供额外的任务专属正则化。

**表 I：用于训练运动与基座姿态控制器的奖励项**

| 奖励项（Term） | 表达式（Equation） | 权重（Weight） |
|---|---|---|
| **共享正则化项（Shared Regularizations）** | | |
| 关节限位（Joint limits） | $\sum_{i=1}^{12} \max(q_i - q_{max,i}, 0) - \min(q_i - q_{min,i}, 0)$ | $-2.0$ |
| 非期望接触（Undesired contacts） | $n_c$ | $-2.0$ |
| **基线正则化项（Baseline Regularizations）** | | |
| 力矩（Torque） | $\|\tau\|^2$ | $-\alpha_g^2 \cdot 10^{-4}$ |
| 动作变化率（Action rate） | $\|a_t - a_{t-1}\|^2$ | $-0.08$ |
| 关节加速度（Joint acceleration） | $\|\ddot{q}\|^2$ | $-8 \times 10^{-7}$ |
| **功率正则化项（Power Regularizations）** | | |
| 功率（Power） | $r_{Power}$（见式 2） | 见第 III-B 节 |
| **运动奖励（Locomotion Rewards）** | | |
| 线速度跟踪（Linear tracking） | $\exp\left(-(e_{v,x}^2 + e_{v,y}^2)/0.25\right)$ | $1.0$ |
| 偏航跟踪（Yaw tracking） | $\exp\left(-e_{\psi}^2/0.25\right)$ | $0.5$ |
| 足部冲击速度（Foot impact velocity，接触时） | $F \cdot v_F^2$ | $-0.6$ |
| **基座姿态奖励（Base Pose Rewards）** | | |
| 高度跟踪（Height tracking） | $\exp\left(-e_h^2/0.1^2\right)$ | $1.0$ |
| 俯仰跟踪（Pitch tracking） | $\exp\left(-e_\theta^2/0.15^2\right)$ | $1.0$ |
| 偏航跟踪（Yaw tracking） | $\exp\left(-e_{\dot{\psi}}^2/0.15^2\right)$ | $2.0$ |
| XY 速度（XY Velocity） | $v_x^2 + v_y^2$ | $-0.6$ |

> 表注：通过组合不同任务与正则化奖励，每种重力下共训练四个策略。指令跟踪误差按 $e_{v,x} = c_{v,x} - {}_B v_x$ 的规则记。$\alpha_g = \frac{g}{g_E}$ 表示重力缩放因子。$i$ 表示第 $i$ 个关节。

我们以两组不同的通用正则化项分别训练了每个控制器（即每个控制器训练两次）。"基线"（baseline）组采用腿式运动控制器中常用的正则化项 [36]；"功率优化"（power-optimized）组使用式 (2) 所述的功率惩罚。虽然功率惩罚在地球重力表达式中只有单一权重，但我们按式 (1) 分别对回收损耗与绕组损耗进行重新缩放。

由于机器人具有两条对称轴（左/右与前/后），我们按 Mittal et al. [37] 提供对称性数据增强（symmetry data augmentation）。我们在仿真中对机器人基座施加扰动：最高 0.7 m/s 的随机速度与最高 5 N 的恒定力。机器人质量随机化 ±2 kg；静摩擦系数在 0.4–1.4 间随机化，动摩擦系数在 0.1–1.4 间随机化。两个控制器使用相同的地形集合，由多种崎岖地形混合而成：最高 23° 的斜坡、最高 0.1 m 的随机方块，以及最高 0.1 m 的噪声地形。

我们为地形 [36] 与功率惩罚添加了课程（curriculum），使控制器先在简单条件下学习跟踪行为，再逐步增加地形难度并优化高效行为。

由于我们在地球重力下的重力卸载台架（gravity offset rig）上测试策略（第 III-D 节），机器人的腿在部署中实际承受的是地球重力。为使在低重力下训练的策略仍能实现仿真到现实的迁移，我们在训练与部署中都将腿部的重力补偿力矩 $g(q)$ 作为前馈项（feedforward terms）传给执行器。相应地，腿部始终处于重力补偿状态，策略只需在重力补偿的基础上进行调节。

### D. 重力卸载系统（Gravity Offload System）

为在真实世界模拟的月球重力下验证我们的强化学习控制器，我们开发了一套被动式重力卸载系统。该系统由两个恒力弹簧卷（constant-force spring coils）构成（图 4）。弹簧端部连接一根 2 mm Dyneema 绳。我们选择被动弹簧加载系统，以避免配重系统增加的惯量以及主动系统的控制带宽限制。与简单配重所需的 13 kg 相比，我们的系统只增加了约 1.5 kg 的寄生质量（parasitic mass）。

绳索穿过一根铝型材走线，确保即使在完全伸展时弹簧也始终被完全包覆。在型材末端，绳索经 PTFE（聚四氟乙烯）导向件穿出以最小化摩擦。我们将绳索连接到机器人基座上靠近质心的位置。

【图 4：恒力弹簧卸载系统（左）使我们能在真实机器人上测试月球运动策略。我们将该系统安装在带轮龙门架（wheeled gantry）上（右），以进行运动测试并测量机器人运动时的功耗。】

为测量系统的实际卸载力，我们用秤测量机器人质量，确定卸载力为 117.2 N，低于 Magnecko 所需的 128.2 N 竖直卸载力——最可能是由于弹簧系统的制造误差。为补偿该误差，我们在月球重力测试中取下了机器人 0.8 kg 的电池，使重力减小 7.9 N。相应地，我们将卸载机构的连接点移至接近机器人新质心的位置。此外，我们在仿真中为月球策略训练将机器人质量增加了 1.9 kg，以补偿剩余的 3.1 N。

我们将卸载系统安装在一个带轮龙门架上，使其能在测试区域内跟随机器人，并让 Dyneema 绳始终接近竖直（图 4）。在该装置中，当绳索不竖直时会引入额外误差源。竖直与水平方向上的相应误差为：

$$F_{\epsilon,z}(r) = F_{Spring}\left(1 - \frac{h}{\sqrt{r^2 + h^2}}\right) \tag{8}$$

$$F_{\epsilon,r}(r) = F_{Spring}\frac{r}{\sqrt{r^2 + h^2}} \tag{9}$$

其中 $r$ 为偏离竖直轴的径向偏移量（radial deflection）。假设 $r < 0.15$ m，且系统安装高度为 1.9 m，则竖直方向误差低于 0.37 N，径向最大误差力为 9.27 N。

## IV. 结果

### A. 用基于重力的奖励缩放适应多重力环境

为验证基于重力的奖励缩放（第 III-A 节），我们在仿真中、跨多个重力水平评估了基线策略与功率优化策略（含与不含重力缩放）在运动与姿态控制任务上的表现（表 II）。我们对各策略进行了定性视觉评估并测量其功耗。评估运动控制器时指令行走速度为 0.4 m/s、地形为平地。对于基座姿态控制器，机器人从 0.32 m 高度开始，随后依次指令：俯仰角回平、最大俯仰 0.5 rad、最大偏航角速度 0.5 rad/s。每次实验持续 15 s，以便对多个步态周期与姿态跟踪动作取平均。表 II 给出了所有重力水平、正则化方案与任务的结果。

**表 II：不同重力水平下，重力缩放/未缩放的运动与基座姿态策略的仿真评估。** 指令行走速度 0.4 m/s、平坦地形；策略质量按好（✓）、中（∼）、差（✗）定性分级；功耗按我们的功率模型（第 III 节）计算。所有运动任务的速度跟踪误差标准差均小于 0.05 m/s。

*运动任务 — 定性评估：*

| 重力环境 | 基线 | 重力缩放基线 | 功率优化 | 重力缩放 + 功率优化 |
|---|---|---|---|---|
| 地球 9.81 m/s² | ✓ | ✓ | ✓ | ✓ |
| 火星 3.73 m/s² | ✓ | ✓ | ∼ | ✓ |
| 月球 1.62 m/s² | ∼ | ∼ | ✗ | ✓ |
| 超级地球 19.62 m/s² | ✓ | ✓ | ✓ | ✓ |

*运动任务 — 功耗（W）：*

| 重力环境 | 基线 | 重力缩放基线 | 功率优化 | 重力缩放 + 功率优化 |
|---|---|---|---|---|
| 地球 9.81 m/s² | 66.6 | 66.6 | 39.9 | 39.9 |
| 火星 3.73 m/s² | 18.9 | 18.1 | 59.6 | 15.4 |
| 月球 1.62 m/s² | 10.6 | 8.3 | 26.5 | 3.93 |
| 超级地球 19.62 m/s² | 121.7 | 161.7 | 45.7 | 172.3 |

*基座姿态任务 — 定性评估：*

| 重力环境 | 基线 | 重力缩放基线 | 功率优化 | 重力缩放 + 功率优化 |
|---|---|---|---|---|
| 地球 9.81 m/s² | ∼ | ∼ | ✓ | ✓ |
| 火星 3.73 m/s² | ✗ | ∼ | ∼ | ∼ |
| 月球 1.62 m/s² | ∼ | ∼ | ✗ | ✓ |
| 超级地球 19.62 m/s² | ∼ | ∼ | ∼ | ∼ |

*基座姿态任务 — 功耗（W）：*

| 重力环境 | 基线 | 重力缩放基线 | 功率优化 | 重力缩放 + 功率优化 |
|---|---|---|---|---|
| 地球 9.81 m/s² | 59.8 | 59.8 | 24.3 | 24.3 |
| 火星 3.73 m/s² | 16.0 | 19.6 | 7.3 | 5.0 |
| 月球 1.62 m/s² | 3.4 | 4.4 | 5.9 | 2.2 |
| 超级地球 19.62 m/s² | 89.9 | 111.8 | 31.4 | 83.0 |

### B. 多重力环境下真实世界功耗对比

我们使用第 III-D 节介绍的重力卸载系统模拟月球重力，将地球与月球运动策略部署到真实机器人上。注意该环境与真实月球重力不同：卸载只在机器人基座上提供单点力，而非卸载所有连杆；腿部则按第 III-C 节所述在内部进行卸载补偿。机器人在铺设高摩擦垫的平面上运行。我们比较了重力缩放基线运动策略与重力缩放功率优化运动策略在地球重力与月球测试环境中的功耗（表 III）。

机器人由外部电源供电，我们用示波器测量电源电压与电流以得到总功耗。机器人的待机功耗（所有系统运行但驱动器不输出力矩）为 77 W。我们仅评估运行控制策略所增加的功耗，该功耗来自传动系统损耗（绕组与齿轮箱损耗）以及关节处的机械功率（第 III-B 节）。每次运行对 15 s 内的功率取平均，约对应 22 个步态周期。

**表 III：地球与月球重力下真实机器人基线与功率优化运动控制器的功耗（W）。** 注意已扣除机器人 77 W 的基础（待机）功耗。

| 重力环境 | 基线 | 功率优化 |
|---|---|---|
| 地球 9.81 m/s² | 30.4 | 23.4 |
| 月球 1.62 m/s² | 19.2 | 12.2 |

## V. 讨论

在两个任务、所有重力水平下，功率优化奖励都比基线奖励产生了更节能、定性表现更好的策略。没有重力缩放时，功率优化奖励组无法很好地扩展到低重力水平：在低重力下重新训练会导致异常行为，例如幅度很大、速度很快的腿部动作。重力缩放使功率优化奖励组在所有重力水平下都能产生可用的策略。此外，这些重新缩放的策略普遍非常节能。能效提升主要源于较高的基座位置——这意味着腿部接近奇异位形（singularity），支撑基座所需的力矩更小 [22]。在超级地球的情形中，未缩放的功率优化奖励反而优于重力缩放的功率优化奖励。基于这一结果，缩放律应在更宽的重力范围内被重新审视与检验。缩放对基线策略的影响小于对功率优化策略的影响；但基线策略总体上能效也更低。对每种重力与每个任务，最优的功率优化策略在定性与定量评估中都优于最优的基线策略。

在真实世界实验中，功率优化运动策略比基线策略功耗更低，与仿真结果一致。基线与功率优化之间的相对差在地球重力下为 23%，在月球测试装置中为 36%。

我们注意到，机器人由于机载计算机、路由器与电机控制器产生的待机功耗，是高效月球运动策略功耗的六倍。这一比例表明：对于使用腿式机器人的月球任务，我们不仅需要为功率效率优化控制策略，还需要优化所有机载系统，尤其是电机控制器。

虽然我们在带有地面参数域随机化（domain randomization）的崎岖地形上训练了控制器，但为了公平比较，我们将功耗评估限制在平坦地形。我们预计在崎岖颗粒地形上，功率优化策略与基线策略之间也会出现类似的定性趋势，但该假设有待进一步实验验证。

被动弹簧加载测试装置使我们能够在真实机器人上验证月球重力策略。尽管策略成功迁移且仿真与真实机器人之间的行为在视觉上可比，仍需进一步工作来减小水平方向的扰动力。此外，一个能够调节卸载力以匹配机器人的调整机构将是有益的改进。

## VI. 结论与未来工作

我们提出并成功验证了一种为腿式机器人跨多个任务与重力水平开发高能效控制器的方法。

我们表明，使用功率优化奖励函数可为运动与基座姿态控制两个任务带来节能的策略。然而，将同样的功率优化奖励朴素地迁移到不同重力会导致性能变差。让功率奖励随重力缩放可以缓解该问题，并在多重力环境下产生可用且节能的控制器。但我们也看到，在高重力的超级地球情形中，重力缩放反而会损害功率效率。未来工作应研究在高重力水平下仍保持高效的缩放律。

此外，本文聚焦于运动策略的重力缩放。未来需要在颗粒地形上使用重力卸载系统进行测试，以了解此类地形如何影响低重力运动。

我们还将改进弹簧加载测试装置，使卸载力可以微调，从而能为质量相近的多个机器人提供精确的重力卸载。

## 致谢

我们感谢 Magnecko 团队在实验、机器人软硬件维护方面的帮助，并总体上建造了一个工程精良、易于使用的系统。感谢 Filip Bjelonic 就机器人传动系统功率建模进行的富有成效的讨论。

## 参考文献（保留原文）

[1] S. Kassel, "Lunokhod-1 soviet lunar surface vehicle," Advanced Research Projects Agency, Tech. Rep., 1971.

[2] R. A. Lindemann, et al., "Mars exploration rover mobility development," IEEE Robotics & Automation Magazine, vol. 13, no. 2, pp. 19–26, 2006.

[3] J. P. Grotzinger, et al., "Mars science laboratory mission and science investigation," Space Science Reviews, vol. 170, no. 1, pp. 5–56, 2012.

[4] K. A. Farley, et al., "Mars 2020 mission overview," Space Science Reviews, vol. 216, no. 8, pp. 1–41, 2020.

[5] L. Ding, et al., "A 2-year locomotive exploration and scientific investigation of the lunar farside by the yutu-2 rover," Science Robotics, vol. 7, no. 62, 2022.

[6] S. Mathavaraj, et al., "Isro's unprecedented journey to the moon," Acta Astronautica, vol. 177, pp. 286–298, 2020.

[7] L. David, "Opportunity mars rover stuck in sand," https://www.space.com/1019-opportunity-mars-rover-stuck-sand.html, 2005, online; accessed 27-Jan-2023.

[8] J. Lee, et al., "Learning quadrupedal locomotion over challenging terrain," Science Robotics, vol. 5, no. 47, p. eabc5986, 2020.

[9] T. Miki, et al., "Learning robust perceptive locomotion for quadrupedal robots in the wild," Science Robotics, vol. 7, no. 62, p. eabk2822, 2022.

[10] A. Agha, et al., "Nebula: Quest for robotic autonomy in challenging environments; team costar at the darpa subterranean challenge," arXiv preprint arXiv:2103.11470, 2021.

[11] D. Hoeller, et al., "Anymal parkour: Learning agile navigation for quadrupedal robots," arXiv preprint arXiv:2306.14874, 2023.

[12] X. Cheng, et al., "Extreme parkour with legged robots," in 2024 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2024, pp. 11443–11450.

[13] S. Dirk and K. Frank, "The bio-inspired scorpion robot: design, control & lessons learned," in Climbing and Walking Robots: Towards New Applications. InTech, 2007.

[14] S. Bartsch, et al., "Development of the six-legged walking and climbing robot spaceclimber," Journal of Field Robotics, vol. 29, no. 3, pp. 506–532, 2012.

[15] A. Roennau, et al., "Reactive posture behaviors for stable legged locomotion over steep inclines and large obstacles," in 2014 IEEE/RSJ International Conference on Intelligent Robots and Systems. IEEE, 2014, pp. 4888–4894.

[16] P. Arm, et al., "SpaceBok: A Dynamic Legged Robot for Space Exploration," in IEEE International Conference on Robotics and Automation (ICRA), May 2019.

[17] T. Schnell, et al., "An efficient scalable autonomy approach for teams of heterogeneous mobile robots," in 2023 IEEE 19th International Conference on Automation Science and Engineering (CASE). IEEE, 2023, pp. 1–7.

[18] P. Arm, et al., "Scientific exploration of challenging planetary analog environments with a team of legged robots," Science Robotics, vol. 8, no. 80, p. eade9548, 2023.

[19] B. J. Morrell, et al., "Robotic exploration of martian caves: Evaluating operational concepts through analog experiments in lava tubes," Acta Astronautica, vol. 223, pp. 741–758, 2024.

[20] H. Kolvenbach, et al., "Lunarleaper-a mission concept to explore the lunar subsurface with a small-scale legged robot," in IAC 2024 Conference Proceedings. International Astronautical Federation, 2024.

[21] J. Schulman, et al., "Proximal policy optimization algorithms," arXiv preprint arXiv:1707.06347, 2017.

[22] H. Kolvenbach, et al., "Traversing steep and granular martian analog slopes with a dynamic quadrupedal robot," in Field Robotics, 2022.

[23] A. Parness, et al., "LEMUR 3: A limbed climbing robot for extreme terrain mobility in space," in 2017 IEEE International Conference on Robotics and Automation (ICRA), May 2017, pp. 5467–5473.

[24] Y. Tanaka, et al., "Scaler: A tough versatile quadruped free-climber robot," in 2022 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). IEEE, 2022, pp. 5632–5639.

[25] N. Rudin, et al., "Cat-like jumping and landing of legged robots in low-gravity using deep reinforcement learning," in Transactions on Robotics. IEEE, 2021.

[26] J. A. Olsen and K. Alexis, "Design and experimental verification of a jumping legged robot for martian lava tube exploration," in 2023 21st International Conference on Advanced Robotics (ICAR). IEEE, 2023, pp. 452–459.

[27] A. Spiridonov, et al., "Spacehopper: A small-scale legged robot for exploring low-gravity celestial bodies," arXiv preprint arXiv:2403.02831, 2024.

[28] H. Kolvenbach, et al., "Efficient Gait Selection for Quadrupedal Robots on the Moon and Mars," International Symposium on Artificial Intelligence, Robotics and Automation in Space (I-SAIRAS), June 2018.

[29] Z. Fu, et al., "Minimizing energy consumption leads to the emergence of gaits in legged robots," 2021. [Online]. Available: https://arxiv.org/abs/2111.01674

[30] Y. Yang, et al., "Fast and efficient locomotion via learned gait transitions," 2021. [Online]. Available: https://arxiv.org/abs/2104.04644

[31] G. Valsecchi, et al., "Accurate power consumption estimation method makes walking robots energy efficient and quiet," in 2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS). IEEE, 2024, pp. 13282–13288.

[32] S. Mahankali, et al., "Maximizing Quadruped Velocity by Minimizing Energy," in 2024 IEEE International Conference on Robotics and Automation (ICRA), May 2024, pp. 11467–11473.

[33] S. Leuthard, et al., "Magnecko: Design and control of a quadrupedal magnetic climbing," in Walking Robots into Real World: Proceedings of the CLAWAR 2024 Conference, Volume 2, vol. 1115. Springer Nature, 2025, p. 55.

[34] M. Mittal, et al., "Orbit: A unified simulation framework for interactive robot learning environments," IEEE Robotics and Automation Letters, vol. 8, no. 6, pp. 3740–3747, 2023.

[35] F. Bjelonic, et al., "Towards bridging the gap: Systematic sim-to-real transfer for diverse legged robots."

[36] N. Rudin, et al., "Learning to walk in minutes using massively parallel deep reinforcement learning," in Conference on Robot Learning. PMLR, 2022, pp. 91–100.

[37] M. Mittal, et al., "Symmetry considerations for learning task symmetric robot policies," in 2024 IEEE International Conference on Robotics and Automation (ICRA). IEEE, 2024, pp. 7433–7439.



