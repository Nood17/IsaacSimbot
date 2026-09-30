---
原文标题: "Locomotion analysis of a quadruped interacting with the lunar granular surface"
中文译名: "四足机器人与月球颗粒表面相互作用的运动学分析"
来源: "arXiv:2606.10273v1 [cs.RO]，2026 年 6 月 9 日；作者单位：意大利帕多瓦大学工业工程系"
翻译日期: "2026-09-30"
---

# 四足机器人与月球颗粒表面相互作用的运动学分析

**作者**：Yash Vyas

**单位**：意大利帕多瓦大学工业工程系（Department of Industrial Engineering, University of Padua）

**日期**：2026 年 6 月 10 日

## 摘要

由于复杂的地形相互作用以及能量、热约束，在地外环境中部署腿式机器人面临诸多挑战。要对月球探测四足机器人进行有效的机械设计，需要仔细权衡电机扭矩、能量消耗与运输代价（cost of transport）。月球表面由颗粒状的风化层/月壤（regolith）构成，这会影响腿式机器人的运动及其性能。基于刚性接触假设训练的运动算法在应用于具有软接触（soft contacts）的环境（如颗粒表面）时同样会失效，可能导致失稳与跟踪性能变差。本报告将颗粒状月球表面与机器人足端接触的物理建模应用于仿真环境，并使用强化学习（Reinforcement Learning, RL）训练运动策略。我们对在刚性接触环境与软接触环境中训练的策略进行了对比，分析了步态与运动性能指标。分析表明，模拟月壤表面的软接触为基于 RL 的训练带来了额外挑战，会产生定性上不同的步态，并增加总体能量消耗。

## 1 引言

腿式机器人凭借穿越困难地形的能力，正被越来越多地用于巡检与探测任务。随着无模型强化学习（model-free RL）[1, 2] 等现代运动控制方法的发展，这类机器人在非结构化环境中的鲁棒性不断提高。由于其在地球环境中的成功，腿式机器人已被提议用于空间探测任务 [3]。迄今为止，月球与火星探测机器人均为轮式或履带式漫游车。然而，对于月球深坑（lunar pits）等难以到达的地貌，腿式机器人更为适合，因为它们既能穿越平坦地形也能穿越岩石地形。尽管已在地球上的地外环境类比场（analog environments）中进行了大量实验 [4, 5]，腿式机器人尚未真正部署于空间探测。

与地球环境相比，在地外天体上运行机器人有独特的挑战 [6]。由于缺乏保护性磁场，元器件必须是航天级（space-grade）以抵抗高得多的辐射。基于现有探测机器人数据对地形物质的理解仍然有限。磁化带电尘埃等现象可能因扬尘或尘暴（火星情况下）侵入关键部件并妨碍其运行。稀薄或缺失的大气使热管理复杂化，因为热量难以散出。此外，探测机器人的能量预算受限于太阳能电池板所能提供的功率。这些问题并非腿式机器人独有，此前大多数漫游车任务也曾与这些挑战搏斗。

LunarLeaper [7] 等任务旨在部署一台 10–15 kg 的腿式机器人，用于探测月球上的马利乌斯丘陵坑（Marius Hills Pit）区域。该区域受到关注是因为它位于过去火山活动广泛的地区，观测表明它可能是熔岩管（lava tube）的入口。现在需要一次表面任务来验证这一假设并进一步研究其特征，因为熔岩管可能适合作为长期月球驻留计划的一部分建造人类栖息地 [8]。

已有许多任务概念提案建议使用大型、昂贵的漫游车与起重机来探测月球坑；然而，这些方法既无法轻松穿越由尘土斜坡与巨石混合构成的复杂地形，也无法在保持平台稳定的情况下将观测设备放入坑中。相比之下，小型轻量化腿式机器人更适合穿越多样化的地形类型，安全接近并将科学仪器部署到坑内。

对于这类任务，需要一种具有最优运动步态的腿式机器人平台：其步态须满足月球条件下的能量与热预算，同时缓解尘埃侵入科学仪器与太阳能板的问题。此外，月球表面由月壤（regolith）构成——一种类似沙的黏性颗粒基底（granular substrate）——由于足下土壤本身的流动，它在运动中有使腿式机器人失稳的风险 [9, 10]。

该平台的腿部形态（morphology）与运动控制器必须能促进在这种地形上的安全、鲁棒穿越，这一点至关重要。此类分析势在必行，因为刚性与软接触地形模型之间的差异，可能导致不同形态在 RL 训练下对应不同的最优步态，也可能影响哪组形态参数能按任务需求取得最优性能。

过去十年中，人们为在复杂环境中运行的腿式机器人开发了多种鲁棒、敏捷的控制方法。早期方法侧重于基于线性或二次优化的轨迹规划器，显式估计足端接触力 [11]。近年来，强化学习（RL）因能对不同环境条件（如接触摩擦 [2]）进行泛化，以及对外部扰动和观测误差的鲁棒性 [12]，成为首选方法。针对地外重力环境的 RL 策略训练已由 Arm 等人 [14] 通过重力卸载系统（gravity-offload system）模拟月球重力，在 Magnecko 机器人 [13] 上得到验证。

本报告对腿式机器人穿越月球地形的运动性能进行了地面动力学（terradynamic）分析，在 [14] 的基础上扩展引入颗粒表面接触。通过将 [15] 中的颗粒表面与机器人足端模型实现到 RL 仿真环境中，我分别对标准刚性接触与颗粒表面接触训练并比较了运动策略。通过在两种环境中用训练好的 RL 运动策略生成月球表面穿越的仿真推演（rollouts），分析了步态特征以及以扭矩、功耗与能量消耗衡量的运动性能。

本文结构如下：第 2 节介绍地外探测腿式机器人、腿式机器人运动强化学习以及颗粒表面接触的地面动力学建模背景；第 3 节概述所选颗粒表面地面动力学模型在仿真环境中的方法与实现，以及 RL 策略训练的关键特征；第 4 节对比并分析刚性与颗粒表面接触环境的结果；第 5 节总结分析结论。

## 2 背景

### 2.1 使用腿式机器人的月球探测

已有众多腿式机器人月球探测器的概念被开发并制作了原型，腿数包括 3、4 甚至 6 条。Lauron-V [16] 与 SpaceClimber [9] 均为腿部 4 自由度的六足机器人，通过静态步态提供高运动稳定性。相比之下，SpaceBok [17] 是专为动态步态设计的 2 自由度并联机构腿四足机器人。SpaceHopper [18] 采用四足构型（tetrapod configuration）中带齿轮传动的高扭矩 2 自由度腿，实现了高能量效率的跳跃步态。地球上的运动研究表明，动态步态相比静态步态可降低能耗。在月球等更低重力环境中，这种差异更为显著，"全蹄跳"（pronking）或跳跃步态在节能运动方面更可行 [19, 20]，在陡峭、颗粒化地形上尤其如此 [10]。

在四足设计中，髋关节有两种构型：哺乳型（Mammalian，俯仰）与蛛型（Arachnid，偏航）。尽管哺乳型构型因其更快、更节能的步态在地面四足机器人中更流行 [21]，但蛛型构型凭借更大的支撑多边形与近似径向对称性，为全向运动提供了更高的稳定性 [22]。因此，本分析建模了基于 Magnecko 机器人 [13] 的蛛型构型概念，与 [14] 中所做的实验一致。

月球探测任务将遵循"运动—科学测量—休息/充电"的重复循环 [7]。运动相位仅占每个循环周期的至多 4%，这使得节能运动成为重要目标：每个相位需穿越 10 m 的规定距离。这样可以留出充足时间散去运动功耗产生的热量、进行科学测量、通过太阳能板为下一次行走序列发电，并向地球指挥/控制中心下行数据。同时，机器人需要稳定安全的步态，以最大限度减少尘埃侵入重力计（Gravimeter）、探地雷达（Ground Penetrating Radar）与相机等科学仪器。

### 2.2 腿式机器人运动的强化学习

RL 将序贯决策形式化为马尔可夫决策过程（MDP），由状态空间 $\mathcal{S}$、动作空间 $\mathcal{A}$、转移概率分布 $P(s(t+1) \mid s(t), a(t))$ 与奖励函数 $R(s, a)$ 定义。智能体遵循随机策略 $\pi_\theta(a \mid s)$，将状态映射到动作分布。目标是学习一个最大化期望累积折扣奖励 $J(\pi_\theta)$ 的最优策略。最优策略下的期望值 $\mathbb{E}_\tau$ 针对由策略 $\pi_\theta$ 与环境随机动力学 $P$ 诱导的轨迹分布取期望 [23]：

$$
J(\pi_\theta) = \mathbb{E}_{\tau \sim \pi_\theta, P} \left[ \sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \right], \tag{1}
$$

其中 $\gamma \in [0, 1)$ 为折扣因子，$\tau = (s_0, a_0, s_1, a_1, \ldots)$ 表示一条轨迹。

无模型 RL 不显式建模环境的状态转移动力学，而是通过采样状态-动作对并将其拟合到隐分布来估计价值函数、优化策略梯度。在部分可观测环境中，策略接收由状态映射而来的观测 $o(t) = \Omega(s(t)) + \epsilon_t$，其中 $\epsilon$ 为噪声（建模为高斯分布 $\mathcal{N}(0, \sigma)$）。策略与价值函数实现为神经网络，如带非线性激活函数的多层感知机（MLP），将观测映射为动作或估计价值函数。MLP 利用采样状态-动作对的奖励来逼近最优策略或价值函数。无模型 RL 因能在不建模动力学的情况下处理复杂环境而被广泛用于运动控制，但需要大量样本——通常由仿真生成——才能使策略收敛。

用于生成状态-动作样本的仿真环境与真实世界物理条件之间的差异会导致"虚实差距"（sim-to-real gap），使训练的策略难以泛化到真实环境。在复杂地面动力学相互作用的语境下，这带来额外风险：在线性摩擦条件下学到的策略不太可能泛化到由足端与颗粒介质（granular media）相互作用产生的黏性接触。除变化摩擦之外的其他域随机化技术（如添加随机扰动与观测噪声）在本研究中被略去，因为研究完全在仿真中进行。

### 2.3 机器人足端与颗粒表面相互作用的地面动力学建模

基于模型的方法（如模型预测控制 MPC）与无模型的运动控制方法（如强化学习）都需要腿式机器人足部与地面之间的物理接触模型，以在仿真中准确预测运动行为。这些模型往往有理想化假设，如完全刚性、非弹性碰撞，并使用简单的足-地摩擦模型，如库仑摩擦（Coulomb friction）或基于地面贯入深度的均匀弹簧-阻尼物理模型 [24]。对这些模型的要求是求解器收敛而非物理精度。在强化学习中，鲁棒性通过摩擦与碰撞参数的域随机化来训练。然而，这仍包含关于这些碰撞物理关系的定性假设，而这些假设不适用于沙地等可变形地面。

这些简单的刚性接触模型无法准确刻画机器人足端在月壤（lunar regolith）上的地面动力学（terradynamics）——月壤是类似沙的颗粒基底。即使对地面摩擦参数进行了域随机化，用这些接触模型在仿真中训练的运动控制策略，对足端之下土壤自身流动引起的失稳也不鲁棒。这些相互作用与库仑摩擦所建模的低摩擦滑移有本质区别。此外，正如地球上的研究所观察到的那样 [25]，穿越颗粒表面预计会增加能量与功率消耗。

刚性与可变形物体之间的接触建模是一个活跃的研究领域，因为它影响抓取等许多实际机器人任务 [26]。运动机器人物理学（locomotion robophysics）领域研究机器人腿与不同介质（如颗粒基底）的相互作用 [27]。已有研究表明，在沙等颗粒基底中的运动是黏性且非线性的，取决于足端形状、与表面的夹角及运动方向。早期研究旨在利用 Hunt-Crossley 模型与库仑摩擦分析刚性/可变形足部与地形接触的一般性质 [28]。此后，众多研究试图基于理论原理 [29, 30] 与实验数据 [15, 31] 建立腿式机器人在颗粒表面上地面动力学的基础模型。

基于地形识别的步态控制最早由 Wu 等人 [32] 提出。另一种思路是通过添加域随机化与扰动来提高鲁棒性 [1]。Choi 等人 [33] 最近的研究将可变形软地面接触模型与强化学习控制相结合，强调求解器收敛性与稳定性以及计算高效的训练。

本研究将 Li 等人 [15] 的地面动力学模型与基于 RL 的运动策略结合，研究黏性地面接触动力学与步态性能之间的关系。该地面动力学模型刻画了月球地形足-地相互作用的黏性，包括侵入角（angle of intrusion）和运动方向与所施加接触力之间的关系。它通过简单系数即可泛化到任意足部形态与颗粒介质属性，这些系数可通过实验辨识或由经验关系推断。

该模型通过将一块薄而刚性的板侵入颗粒介质中运动的实验构建。测量板上微小段的竖直与水平应力 $\sigma_z$ 和 $\sigma_x$，刻画它们与对介质层的攻角 $\beta_s$、侵入角（运动方向）$\gamma_s$ 以及贯入深度 $|z|_s$ 的关系。作用于足端形状的升力与阻力 $F_z$、$F_x$ 则由作用于侵入颗粒介质的迎流表面积 $S$ 上微段面积 $dA_s$ 的应力积分确定：

$$
F_{z,x} = \int_S \sigma_{z,x}(|z|_S, \beta_S, \gamma_S)\, dA_s. \tag{2}
$$

实验发现，所有受测颗粒介质的应力模型都可泛化为含 9 个零阶与一阶傅里叶系数的模型：$\sigma_{z,x}(\beta_S, \gamma_S)$ 与贯入深度 $z_s$ 线性相乘，并按系数 $\zeta$ 缩放——$\zeta$ 刻画介质的紧实度与粒径效应：

$$
\sigma_z = \zeta |z_s| \sum_{m=-1}^{1} \sum_{n=0}^{1} \left[ A_{m,n} \cos(2m\beta + n\gamma) + B_{m,n} \sin(2m\beta + n\gamma) \right], \tag{3}
$$

$$
\sigma_x = \zeta |z_s| \sum_{m=-1}^{1} \sum_{n=0}^{1} \left[ C_{m,n} \cos(2m\beta + n\gamma) + D_{m,n} \sin(2m\beta + n\gamma) \right]. \tag{4}
$$

所用的通用傅里叶系数汇总于表 1。

**表 1**：Li 等人 [15] 地面动力学应力模型的通用傅里叶系数；数值单位为 N·cm⁻³，贯入深度 $|z|_S$ 以 cm 计。

| m, n | 0,0 | 1,0 | 0,1 | 1,1 | −1,1 |
|---|---|---|---|---|---|
| $A_{m,n}$ | 0.206 | 0.169 | – | – | – |
| $B_{m,n}$ | – | – | 0.358 | 0.212 | 0.055 |
| $C_{m,n}$ | – | – | 0.253 | −0.124 | 0.007 |
| $D_{m,n}$ | – | −0.088 | – | – | – |

这一形式化表述使该模型适合域随机化：在 RL 算法中改变 $\zeta$，有助于让步态泛化到月球月壤材料性质的变化。此外，该实验方法可用于辨识月球月壤等效材料的傅里叶系数，为颗粒表面材料构建更准确的模型。

## 3 方法与实现

### 3.1 地形建模

第 2.3 节所述地面动力学模型的实现通过离散网格（mesh）表示泛化到任意足部形态。网格的面片（faces）被取作计算升力与阻力（式 (2)）时的有限面积微段。随后将这些微段力沿足部整体求和，得到作用于足端坐标系原点的总力与总力矩，并在仿真环境中以外力和外力矩的形式施加。该实现将 Li 等人 [15] 的公式推广为使用地面法线，从而能够用于非平坦地形：将微段坐标系相对地面法线投影，并用基于重力夹角的缩放因子缩放表面贯入深度。

初始化步骤如下：将网格面片解析为以 $s$ 为索引的微段，带有足体坐标系下的质心 $c_s^B \in \mathbb{R}^3$、法线 $n_s^B \in \mathbb{R}^3$ 与面积 $dA_s \in \mathbb{R}$。之后，在每个仿真步计算作用于足 $f$ 的累积力与力矩。总体流程为：算法在体坐标系与世界坐标系之间投影微段坐标，检查表面贯入与迎流面，计算 $\beta_s$ 与 $\gamma_s$，用式 (2) 计算应力，将力变换回世界坐标系并求和，得到作用于每个足端的累积力与力矩。详细实现见算法 1，算法中相关参数的示意如图 1 所示。

【图1：地面动力学接触模型示意：一个半球形网格足端侵入高度为 $z_h$ 的表面层。与介质接触的足部微段以红色显示；世界坐标系方向以彩色坐标轴表示，速度以橙色表示。该图说明了算法 1 中侵入角 $\beta_s$、运动方向角 $\gamma_s$、贯入深度等参数的几何含义。】

**算法 1 地面动力学接触模型（Terradynamic Contact Model）**

```
对每只足 f ∈ F：
    获取足的世界坐标系位姿 T_f^W = [R_f^W  p_f^W; 0_{1×3}  1]、
        线速度 v_f^W 与角速度 ω_f^W
    初始化总足力 F_f^W ← 0 与力矩 τ_f^W ← 0
    对每个微段 s ∈ S（体坐标系法线 n_s^B、质心 c_s^B、面积 A_s）：
        计算世界系下的法线与质心：n_s ← R_f^W n_s^B，c_s^W ← T_f^W c_s^B
        获取微段位置处地面高度 z_g^W 与地面法线 n_g^W
        计算对地面的表面贯入量：z_s^W = −([0 0 c_s^W] − z_g^W) · n_g^W
        表面贯入与迎流微段检查：若 z_s^W > 0 则跳过该微段
        计算微段在世界系中的速度：v_s^W ← v_f^W + (c_s^W − p_f^W) × ω_f^W
        迎流微段检查：若 v_s^W · n_s^W < 1×10⁻⁶ 则跳过该微段
        将微段坐标系对齐地面平面：n_s = n_g^W
        计算从世界系到地面-aligned 微段系的旋转：
            R_s^W ← [n_s^W − (n_s^W·n_g^W)n_g^W,  n_s^W × (n_s^W − (n_s^W·n_g^W)n_g^W),  n_g^W]^⊺
        将足法线与速度投影到地面对齐微段系：n_s^g ← R_s^W n_s^W，v_s^g ← R_s^W v_s^W
        计算侵入角与入射角：
            β_s ← arctan(n_s^s(x), −n_s^s(z))
            γ_s ← 0（若 |−v_s^s(z)| < 10⁻⁹），否则 arctan(v_s^s(x), −v_s^s(z))
        计算按沿地面法线重力修正的有效表面深度：z_s^g ← z_s^g |[0 0 1] n_g^W|
        计算微段力：F_z^s ← σ_z(z_s^g, β_s, γ_s) dA_s；F_x^s ← σ_x(z_s^g, β_s, γ_s) dA_s
        微段系下合力：F_s^s ← [F_x^s, 0, F_z^s]^⊺
        将微段力重投影回世界系：F_s^W ← (R_s^W)^⊤ F_s^s
        累积总足力：F_f^W ← F_f^W + F_s^W
        累积总足力矩：τ_f^W ← τ_f^W + (c_s^W − p_f^W) × F_s^W
    将外力 F_f^W 与外力矩 τ_f^W 施加到 p_f^W 处的足 F
```

### 3.2 运动步态

运动控制通过训练一个深度强化学习策略实现，训练算法为近端策略优化（PPO）[34]——Actor-Critic 方法的一种变体，通过最大化截断参数代理目标（clipped surrogate objective）并使用 ADAM 优化器来保证稳定的梯度下降，从而更新网络权重。

观测、奖励、动作、神经网络与训练过程与 [14] 类似，仅有如下小幅修改：

1. 注意功率惩罚项使用了功率损耗方程 (5)，其中含 $\tau^2$ 与功率 $\tau \dot{q}$ 分量及相应系数。因此这里将其设为扭矩惩罚与机械功率惩罚，并重新调节权重以得到稳定的运动步态。这样可将电机性能特性与 RL 策略训练解耦。
2. 增加了对偏离水平基座姿态的小惩罚，有助于收敛到基座稳定的步态——在颗粒接触环境中，足部滑移力很容易使机器人失衡，该惩罚尤其重要。
3. 略去速度扰动、外力扰动与观测噪声，以加速策略训练，因为本分析不需要它们。
4. 采用课程学习（curriculum training）：从课程起始的回合（episode）起，对地形难度做线性递增。

跟踪通过基座坐标系速度指令实现，指令由前向与侧向线速度 $v_{c,x}^B$、$v_{c,y}^B$ 以及绕基座中心的偏航转速 $v_{c,\psi}^B$ 组成，作为观测提供。完整的观测集合见表 2。

策略的输出为动作 $a \in \mathbb{R}^{12}$，经 PD 控制器映射为目标关节角：$q^* = 0.3a + q_i$，其中 $q_i$ 为该四足机器人模型的默认构型关节角。Actor 与 Critic 网络均为含 3 个全连接层的多层感知机，维度为 [512, 256, 128]，每层使用指数线性单元（ELU）激活函数。

奖励分为两类：跟踪奖励（tracking rewards）——鼓励收敛到符合指令线速度的稳定行走步态；平滑奖励（smoothing rewards）——减少急动、防止关节扭矩过大并降低功耗 [14]。训练初始仅启用跟踪奖励，以鼓励在可行行走步态区域内探索；在 200 个回合的仿真推演之后，平滑奖励以线性缩放因子在 50 个回合内逐步引入。完整的奖励集合见表 3。

刚性与颗粒接触两种环境使用完全相同的 RL 策略训练参数与特征，以便对运动性能进行公平比较。

**表 2**：训练 RL 策略时 Actor 与 Critic 网络使用的观测输入。

| 观测 | 维度 | Actor/Critic | 表达式 |
|---|---|---|---|
| 基座线速度 | 3 | Critic | $v_B(t)$ |
| 历史角速度 | 21 | Actor | $[\omega_B(t-7dt)\ \ldots\ \omega_B(t-dt)]^\intercal$ |
| 基座角速度 | 3 | 两者 | $\omega_B(t)$ |
| 投影重力 | 3 | 两者 | $R_B^{W\top} [0\ 0\ -1]^\intercal$ |
| 速度指令 | 3 | 两者 | $[0.5\, v_{c,x}^B\ v_{c,y}^B\ v_{c,\psi}^B]^\intercal$ |
| 关节角 | 12 | 两者 | $q$ |
| 关节速度 | 12 | 两者 | $\dot{q}$ |
| 上一动作 | 12 | 两者 | $a_{t-1}$ |

**表 3**：训练运动与基座姿态控制器所用的奖励。跟踪误差在基座坐标系中由指令与实际线速度 $[v_x^B\ v_y^B\ v_\psi^B]^\intercal$ 计算，以前向为例：$e_{v,x} = v_{c,x}^B - v_x^B$。

| 奖励 | 表达式 | 权重 |
|---|---|---|
| **跟踪奖励** | | |
| 线速度跟踪 | $\exp\{-(e_{v,x}^2(t) + e_{v,y}^2(t))\}/0.25$ | 1.0 |
| 偏航速度跟踪 | $\exp\{-e_\psi^2\}/0.25$ | 0.5 |
| 水平姿态 | $[0\ 0\ -1]^\intercal - R_B^{W\top}[0\ 0\ -1]^\intercal$ | −0.2 |
| 关节限位违例 | $\lVert \max(0, q_{min} - q(t)) + \max(0, q(t) - q_{max}) \rVert_2^2$ | −1.0 |
| 非期望接触 | $n_c$ | −1.0 |
| 触地足端速度 | 接触时的 $v_{f,z}^{W\,2}$ | −0.6 |
| **平滑奖励** | | |
| 关节扭矩 | $\lVert \tau(t) \rVert_2$ | $-1\times10^{-5}$ |
| 关节加速度 | $\lVert \ddot{q}(t) \rVert_2$ | $-1\times10^{-7}$ |
| 动作变化率 | $\lVert a(t) - a(t - dt) \rVert_2$ | −0.08 |
| 总功率 | $\lVert \tau(t)^\intercal \dot{q}(t) \rVert_2$ | $-1\times10^{-6}$ |

## 4 结果

### 4.1 仿真环境

带地面动力学模型的 RL 训练环境在 RaiSim [35] 中实现，该仿真器支持底层外力的计算与施加以及并行化。实现了两类环境：其一使用标准刚性接触 RaiSim 求解器，足-地相互作用采用库仑摩擦；其二为"软"环境，实现第 3.1 节所述的地面动力学模型。软环境依赖地面动力学接触模型，实现为对高度 $z_H = 0.05$ m 的虚拟土层贯入，深度过大时以刚性地面作为兜底（fallback）。

所用腿式机器人模型为 Magnecko [13] 的简化类比：均匀密度基座 4.5 kg，轻质铝连杆质量密度 0.2 kg/m，电机对应 Maxon DT50M 的质量/惯性特性，总质量 13.5 kg。刚性地形训练采用球形足模型，仅下半球与地面接触，因为求解器对滚动点接触更稳定、计算更快。软地形足部建模为以 688 个面片离散的半球。

确定微段应力计算的正确缩放因子尤为重要，因为它影响地面动力学相互作用中的滑移、下陷与弹性碰撞特性。[15] 的补充材料给出紧实堆积罂粟籽的缩放因子为 0.488。应力值单位为 N·cm³，乘以以 cm 计的深度 $|z|_S$。为转换到 SI 单位，将缩放因子转为应力密度，即乘以 $1\times10^{8}$。再经另外两个一阶因子缩放：地球到月球的重力比（$1.62/9.81 = 0.165$），以及罂粟籽（580 kg·m⁻³ [36]）与 JSC1A（月球月壤模拟物 [37]，1500 kg·m⁻³）的粒径与紧实度之比。所得应力密度为 $2.15\times10^{7}$。颗粒介质中贯入深度的研究表明这是可接受的一阶近似 [38, 39]。为与刚性接触模型对比，静摩擦与动摩擦设为 0.3，模拟尽可能接近软接触滑移的低摩擦表面。

实现了两类域随机化：摩擦与地形（通过课程学习），在每个并行环境中分别随机化。对刚性接触环境，静库仑摩擦在 $[0.3, 1.0]$ 内均匀采样，动库仑摩擦设为静摩擦的系数，在 $[0.3, 1.1]$ 内均匀采样且最小为 0.1。对软接触环境，应力密度固定为 $2.15\times10^{7}$。

地形课程学习采用 Perlin 随机化程序化生成粗糙起伏表面：刚性接触环境从第 1000 回合、软接触环境从第 1100 回合开始由平坦表面起步，每 50 回合更新一次，难度缩放因子为每回合 $0.75\times10^{-3}$。这主要模拟缓坡，因为软接触模型在大角度下会失效并产生异常大的接触力，导致机器人飞离地面，从而造成训练不稳定、偏离可行步态。

RL 训练使用 1000 个并行仿真环境，每个回合持续 20 s，控制器频率 50 Hz 采样。仿真求解器频率在刚性接触环境为 400 Hz、软接触环境为 800 Hz，因为软接触力更易出现数值不稳定与波动。各环境中给予观测输入的速度指令在 $[-1.0, 1.0]$（$v_{c,x}^B$ 与 $v_{c,y}^B$）及 $[-0.75, 0.75]$（$\omega_{c,\psi}$）内均匀随机采样。每 10 s 仿真时间给出新指令，即每回合两次。

RL 策略训练在 44 GB CPU 内存（分布于 36 核）与一块 4 GB 显存的 GPU（用于更新 RL 网络）上进行。由于软接触环境需要更高的求解器频率并对离散网格做更多运算，其平均每回合训练时间约为刚性环境的两倍。学习参数汇总于表 4。

**表 4**：RL 训练参数。

| 参数 | 值 |
|---|---|
| 折扣因子 $\gamma$ | 0.99 |
| 熵系数 | 0.007 |
| 学习率 | $1\times10^{-3}$ |
| 最大梯度范数 | 0.95 |
| 广义优势估计 $\lambda$ | 0.95 |
| mini-batch 数量 | 4 |
| 学习回合数（learning epochs） | 4 |
| 截断范围（clip range） | 0.2 |
| 总回合数 | 2000 |

表 3 所述功率奖励对每个电机使用机械功率 $P_{mech}(t) = \tau \dot{q}$（$\tau$ 为扭矩、$\dot{q}$ 为速度），并假设无功率回收（即最小为 0）。然而实际中存在显著的绕组电阻与齿轮损耗，取决于电机工作的扭矩/速度区间。为计入这些损耗，在运动策略分析中按式 (5) 的功率损耗模型计算功率损耗：

$$
P_{loss}(t) = P_{gear}(t) + P_{motor}(t) + P_{winding}(t) + P_{driver}(t), \tag{5}
$$

$$
P_{motor}(t) = (1 - \eta_{motor})\, P_{mech}(t), \tag{6}
$$

$$
P_{gear}(t) = (1 - \eta_{gear})\, P_{mech}(t), \tag{7}
$$

$$
P_{driver}(t) = \frac{\alpha}{(\eta_{gear} N \kappa_\tau)^2}\, \tau(t)^2 + \frac{\beta}{\eta_{gear} \kappa_\tau}\, P_{mech} + P_{elec}, \tag{8}
$$

$$
P_{winding}(t) = \frac{3 R_s}{(\eta_{gear} N \kappa_\tau)^2}\, \tau(t)^2, \tag{9}
$$

其中 $\kappa_\tau$ 为电机扭矩常数，$N$ 为减速比，$\eta_{gear}$ 与 $\eta_{motor}$ 分别为齿轮与电机效率系数，$R_s$ 为每相绕组电阻，$\alpha_1$、$\alpha_2$ 为通用系数，$P_{elec}$ 为恒定电损耗。总功率为 $P_{total}(t) = P_{mech}(t) + P_{loss}(t)$。功率损耗系数取值汇总于表 5。可从电机数据手册提取的参数纳入模型，未知参数置 0。

**表 5**：功率损耗计算中所用 Maxon DT50M 的电机模型参数。

| 参数 | 单位 | 值 |
|---|---|---|
| $\eta_{gear}$ | – | 0.95 |
| $\eta_{motor}$ | – | 0.92 |
| $R_s$ | Ω | 0.748 |
| $N$ | – | 18 |
| $\kappa_\tau$ | Nm/A | 0.105 |
| $\alpha$ | – | 0.0 |
| $\beta$ | – | 0.0 |
| $P_{elec}$ | W | 0.748 |

### 4.2 地形模型与运动步态对比

策略训练完成后进行了两类分析：对机器人运动步态的定性分析，以及对扭矩/功率曲线的定量分析。定性分析包括对步态的目视检查，以分类其类型（walk、trot、pronk 等）并刻画步幅长度、高度与足部触地/腾空时间等特征。随后迭代调整奖励，以产生一致、周期且节能的步态。

步态奖励调参的一个挑战是找到一组公共参数，使刚性与软接触两种模型的训练都能稳定收敛到行走步态。通常软接触模型约束更强，因此在调好刚性接触行走后，将同样的奖励参数用于软地形模型测试时，未能泛化到足-地接触高度非均匀且非线性的动力学。MLP 网络的层数与规模也影响网络学习软地步态的能力。

从零开始在纯软接触环境中训练软接触策略未能得到平滑或可行的步态，因为训练初期接触高度不稳定，导致收敛到迈小碎步（scuttle steps）的过度保守步态。为此，软接触模型采用迁移学习：以训练 800 回合的刚性模型（此时它已学会站立并以大步幅进行基本行走）为基座模型，从第 0 回合起继续训练。

尽管如此，刚性与软接触环境步态的定性特征仍有差异。刚性接触步态步幅更宽，因为步态对高冲量接触反力更有信心，有利于建立落脚点。软接触步态在高足部速度冲击下会产生显著侧滑，增大跟踪误差。因此软接触模型的步幅更小、占空比（duty cycle）更高，以最小化滑移力——滑移力与足-面接触角及运动方向成正比。

与假设步态摆动相中无地面作用力的刚性接触模型不同，软地形模型存在侵入与拔出力（尽管幅值较低）。这一点加上不同攻角与侵入角产生的阻力差异，使跟踪性能退化，因为在颗粒介质中更难获得稳定立足点。经 2000 回合训练，步态在 10 m 穿越上收敛到 5% 的净跟踪误差。

平坦行走的扭矩与功率曲线见图 2、图 3（0.2 m/s）与图 5、图 6（0.4 m/s），分别对应刚性与软地形接触模型；相同行走的功耗对比见图 4 与图 7。

【图2：慢速行走（0.2 m/s）下刚性地形四条腿（LF/RF/LH/RH）的关节扭矩曲线，分别为偏航（红）、俯仰（蓝）与膝部（绿）关节，横轴为时间（s）。用于展示刚性接触下的高冲量扭矩特征。】

【图3：慢速行走（0.2 m/s）下颗粒接触（软地形）的对应扭矩曲线，图例同上。与图 2 对比可见软接触峰值扭矩较低。】

【图4：慢速行走（0.2 m/s）的机械功率（蓝）与总功率（红）消耗曲线，(a) 刚性接触、(b) 软接触两子图对比。】

为在不同行走方向的变化上测量聚合统计量，进行了多组穿越的并行仿真。基准测试了两类穿越：50 s、0.2 m/s 的慢速行走与 25 s、0.4 m/s 的快速行走，两者均在缓坡地形上各覆盖 10 m。为增加穿越多样性，加入了至多 50% 的侧向速度均匀随机变化以及至多 ±0.05 rad/s 的偏航速度分量。结果汇总于表 6 与表 7，列出了绝对关节扭矩、机械功率、功率损耗、总能量以及机械运输代价（Mechanical Cost of Transport, MCOT）。

【图5：快速行走（0.4 m/s）下颗粒接触的扭矩曲线（原图标题如此），为偏航（红）、俯仰（蓝）、膝部（绿）关节。】

【图6：快速行走（0.4 m/s）下颗粒接触的扭矩曲线（另一组/另一条件），图例同上。（注：原文图 5、图 6 标题均写为"granular contacts"，其中一个应为刚性接触——按上下文应为"图 5：刚性接触；图 6：颗粒接触"。）】

**表 6**：100 次 50 s、0.2 m/s 慢速行走穿越的聚合运动统计，含均值（µ）、标准差（σ）与最大值。

| 指标 | 刚性地形 µ±σ | 刚性地形 Max | 软地形 µ±σ | 软地形 Max |
|---|---|---|---|---|
| 绝对关节扭矩 (Nm) | 0.418 ± 0.685 | 7.33 | 0.521 ± 0.688 | 5.97 |
| 机械功率 (W) | 2.27 ± 2.04 | 13.8 | 2.01 ± 1.45 | 15.4 |
| 功率损耗 (W) | 0.474 ± 1.85 | 37.4 | 0.542 ± 1.57 | 68.5 |
| 总功率 (W) | 7.96 ± 8.76 | 60.8 | 8.51 ± 7.00 | 90.4 |
| 距离 (m) | 10.6 ± 0.251 | 11.3 | 9.61 ± 0.518 | 12.0 |
| 总能量 (J) | 382 ± 12.7 | 407 | 409 ± 14.5 | 439 |
| MCOT | 0.485 ± 0.0256 | 0.510 | 0.475 ± 0.0209 | 0.532 |

两种速度下刚性与软地形接触模型的对比表明，运动步态在定性与定量行为上确实存在差异。由于软接触的冲量低于刚性接触，最大关节扭矩更低。与预期相反，软地形的机械功率与 MCOT 更低；但功率损耗更高，因为步态的支撑相与摆动相都存在持续的足部接触力。

这可以从接触力的性质解释：刚性接触模型产生高冲量，动能快速耗散；而软接触模型的耗散更平缓，且随深度线性变化。加之软模型侵入与拔出力的双重作用，机器人随时间推移为推动穿越颗粒表面所需的持续努力而损失更多功率。长期来看，这导致覆盖相同 10 m 目标距离时能量耗散更大。所有仿真中的最大总能量与总功率也更高，尽管均值与标准差相当。这表明存在更多离群情形：四足机器人在月壤中"陷住"（可能是在穿越斜坡时），需要高功率与高能耗。

【图7：快速行走（0.4 m/s）的机械功率（蓝）与总功率（红）消耗，(a) 刚性接触、(b) 软接触两子图。】

**表 7**：100 次 25 s、0.4 m/s 快速行走穿越的聚合运动统计，含均值（µ）、标准差（σ）与最大值。

| 指标 | 刚性地形 µ±σ | 刚性地形 Max | 软地形 µ±σ | 软地形 Max |
|---|---|---|---|---|
| 绝对关节扭矩 (Nm) | 0.519 ± 0.743 | 8.41 | 0.591 ± 0.734 | 6.62 |
| 机械功率 (W) | 3.59 ± 3.15 | 19.6 | 3.03 ± 2.37 | 19.3 |
| 功率损耗 (W) | 0.613 ± 2.31 | 49.3 | 0.653 ± 1.86 | 86.5 |
| 总功率 (W) | 10.9 ± 11.8 | 79.1 | 10.9 ± 9.0 | 107 |
| 距离 (m) | 10.0 ± 0.061 | 10.2 | 10.1 ± 0.18 | 10.5 |
| 总能量 (J) | 252 ± 5.64 | 260 | 250 ± 11.7 | 278 |
| MCOT | 0.389 ± 0.0246 | 0.419 | 0.326 ± 0.0267 | 0.386 |

## 5 结论

本报告研究了由强化学习控制器结合颗粒介质地形接触模型训练的运动策略。通过在仿真环境中实现 Li 等人 [15] 的地面动力学模型，分析了月球探测四足机器人穿越月壤的运动。这一"软"颗粒地形接触模型与刚性接触模型（RL 仿真中惯用的模型）进行了基准对比，以确定关节扭矩、功耗与能量在定性步态差异和定量差异上的表现。

所用地面动力学模型可泛化到不同足端形状与形态，同时保留了机器人足部以不同角度与速度侵入地面时相互作用的复杂性。它允许对单一参数进行简便的域随机化，以缩小虚实差距（sim-to-real gap）。在本实现中，其计算耗时与网格点接触刚性接触求解器相当。但该模型偶尔会产生剧烈变化的接触力，可能导致飞行或快速滑动行为。还需进一步分析该足部形态下足-面接触的侵入角与运动角，以为接触力建立数值界限。

刚性接触与软地形接触模型之间的基准对比表明，穿越月壤等颗粒基底会导致运动步态变化：穿越中的滑移问题使跟踪能力下降。从 RL 角度看，由于模型边界问题，可行奖励组合的空间受限；但仍能找到一组对刚性与软接触模型都收敛到稳定且节能步态的公共奖励权重。平均与最大扭矩升高；尽管机械功率降低，地形颗粒流动提供的阻力仍导致更大的功率损耗。

对不同接触模型的这一探索表明，地外环境中腿式机器人的机械与运动控制协同设计（co-design）必须纳入颗粒地形建模。理解足-地相互作用对颗粒基底的行为，是此类任务中腿部与足部形态设计、电机驱动选型以及鲁棒节能运动控制的必要条件。

## 致谢

产生这些成果的研究获得了欧盟"地平线 2020"（Horizon 2020）研究与创新计划下 Marie Skłodowska-Curie 资助协议（编号 101034319）以及欧盟 NextGenerationEU 的资助。

作者感谢机器人系统实验室（Robotics Systems Lab）的 Marco Hutter 教授、Oliver Fischer、Joseph Church、Philip Arm、Adrian Fuhrer、Elena Krasnova 与 Hendrik Kolvenbach 的指导与支持。

## 参考文献（原文保留）

[1] J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, "Learning quadrupedal locomotion over challenging terrain," Science Robotics, vol. 5, p. eabc5986, Oct. 2020.

[2] T. Miki, J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, "Learning robust perceptive locomotion for quadrupedal robots in the wild," Science Robotics, vol. 7, p. eabk2822, Jan. 2022.

[3] H. Kolvenbach, M. Breitenstein, C. Gehring, and M. Hutter, "Scalability Analysis of Legged Robots for Space Exploration," in 68th International Astronautical Congress (IAC 2017), vol. 16, pp. 10399–10413, Curran, June 2018.

[4] P. Arm, G. Waibel, J. Preisig, T. Tuna, R. Zhou, V. Bickel, G. Ligeza, T. Miki, F. Kehl, H. Kolvenbach, and M. Hutter, "Scientific exploration of challenging planetary analog environments with a team of legged robots," Science Robotics, vol. 8, p. eade9548, July 2023.

[5] B. J. Morrell, M. Saboia da Silva, M. Kaufmann, S. Moon, T. Kim, X. Lei, C. Patterson, J. Uribe, T. S. Vaquero, G. J. Correa, L. M. Clark, A. Agha, and J. G. Blank, "Robotic exploration of Martian caves: Evaluating operational concepts through analog experiments in lava tubes," Acta Astronautica, vol. 223, pp. 741–758, Oct. 2024.

[6] H. Kolvenbach, P. Arm, G. Valsecchi, N. Rudin, and M. Hutter, "Legged Systems for Exploration," pp. 135–156, Cham: Springer Nature Switzerland, 2024.

[7] H. Kolvenbach, A. Mittelholz, S. C. Stähler, P. Arm, V. T. Bickel, A. Fuhrer, J. G. Jodar, R. Margarit, J. Church, E. Krasnova, K. Walas, M. Grott, S.-E. Hamran, Özgür Karatekin, M. Olivares-Mendez, S. Coloma, M. Pagnamenta, M. Gumiela, J. Aaron, and M. Hutter, "Lunarleaper—a mission concept to explore the lunar subsurface with a small-scale legged robot," Acta Astronautica, vol. 240, pp. 63–75, 2026.

[8] H. Kalita, A. Quintero, A. Wissing, B. Haugh, C. Angie, G. Nail, J. Wilson, J. Richards, J. Landin, K. Kukkala, M. Vazquez, N. Tan, Q. Lamey, R. Lu, R. Peralta, V. Vilvanathan, and J. Thangavelautham, "Evaluation of Lunar Pits and Lava Tubes for Use as Human Habitats," Earth and Space 2021, pp. 944–957, Apr. 2021.

[9] S. Bartsch, "Development, Control, and Empirical Evaluation of the Six-Legged Robot SpaceClimber Designed for Extraterrestrial Crater Exploration," KI - Künstliche Intelligenz, vol. 28, pp. 127–131, June 2014.

[10] H. Kolvenbach, P. Arm, E. Hampp, A. Dietsche, V. Bickel, B. Sun, C. Meyer, and M. Hutter, "Traversing Steep and Granular Martian Analog Slopes with a Dynamic Quadrupedal Robot," Field Robotics, vol. 2, pp. 910–939, May 2022.

[11] A. W. Winkler, C. D. Bellicoso, M. Hutter, and J. Buchli, "Gait and Trajectory Optimization for Legged Systems Through Phase-Based End-Effector Parameterization," IEEE Robotics and Automation Letters, vol. 3, pp. 1560–1567, July 2018.

[12] J. Hwangbo, J. Lee, A. Dosovitskiy, D. Bellicoso, V. Tsounis, V. Koltun, and M. Hutter, "Learning agile and dynamic motor skills for legged robots," Science Robotics, vol. 4, p. eaau5872, Jan. 2019.

[13] S. Leuthard, T. Eugster, N. Faesch, R. Feingold, C. Flynn, M. Fritsche, N. Hürlimann, E. Morbach, F. Tischhauser, M. Müller, M. Montenegro, V. Schelbert, J.-R. Chiu, P. Arm, and M. Hutter, "Magnecko: Design and Control of a Quadrupedal Magnetic Climbing Robot," in Walking Robots into Real World (K. Berns, M. O. Tokhi, A. Roennau, M. F. Silva, and R. Dillmann, eds.), (Cham), pp. 55–67, Springer Nature Switzerland, 2024.

[14] P. Arm, O. Fischer, J. Church, A. Fuhrer, H. Kolvenbach, and M. Hutter, "Efficient learning-based control of a legged robot in lunar gravity," 2025.

[15] C. Li, T. Zhang, and D. I. Goldman, "A Terradynamics of Legged Locomotion on Granular Media," Science, vol. 339, pp. 1408–1412, Mar. 2013.

[16] A. Roennau, G. Heppner, M. Nowicki, and R. Dillmann, "LAURON V: A versatile six-legged walking robot with advanced maneuverability," in 2014 IEEE/ASME International Conference on Advanced Intelligent Mechatronics, pp. 82–87, July 2014. ISSN: 2159-6255.

[17] P. Arm, R. Zenkl, P. Barton, L. Beglinger, A. Dietsche, L. Ferrazzini, E. Hampp, J. Hinder, C. Huber, D. Schaufelberger, F. Schmitt, B. Sun, B. Stolz, H. Kolvenbach, and M. Hutter, "SpaceBok: A Dynamic Legged Robot for Space Exploration," in 2019 International Conference on Robotics and Automation (ICRA), pp. 6288–6294, May 2019. ISSN: 2577-087X.

[18] M. Trentini, P. Arm, G. Valsecchi, H. Kolvenbach, and M. Hutter, "Concept Study of a Small-Scale Dynamic Legged Robot for Lunar Exploration," in IAC 2023 Conference Proceedings, p. 78250, International Astronautical Federation, Oct. 2023.

[19] H. Kolvenbach, D. Bellicoso, F. Jenelten, L. Wellhausen, and M. Hutter, "Efficient Gait Selection for Quadrupedal Robots on the Moon and Mars," ESA Conference Bureau, June 2018.

[20] H. Kolvenbach, E. Hampp, P. Barton, R. Zenkl, and M. Hutter, "Towards Jumping Locomotion for Quadruped Robots on the Moon," in 2019 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), pp. 5459–5466, Nov. 2019. ISSN: 2153-0866.

[21] H. Chai, Y. Li, R. Song, G. Zhang, Q. Zhang, S. Liu, J. Hou, Y. Xin, M. Yuan, G. Zhang, and Z. Yang, "A survey of the development of quadruped robots: Joint configuration, dynamic locomotion control method and mobile manipulation approach," Biomimetic Intelligence and Robotics, vol. 2, p. 100029, Mar. 2022.

[22] N. Kashiri, A. Ajoudani, D. G. Caldwell, and N. G. Tsagarakis, "Evaluation of hip kinematics influence on the performance of a quadrupedal robot leg," in Proceedings of the 13th International Conference on Informatics in Control, Automation and Robotics, pp. 205–212, SCITEPRESS - Science and and Technology Publications, 2016.

[23] R. S. Sutton, Reinforcement learning. Adaptive computation and machine learning, Cambridge, Massachusetts: The MIT Press, second edition ed., 2020.

[24] Q. Le Lidec, W. Jallet, L. Montaut, I. Laptev, C. Schmid, and J. Carpentier, "Contact Models in Robotics: A Comparative Analysis," IEEE Transactions on Robotics, vol. 40, pp. 3716–3733, 2024.

[25] C. Li, A. M. Hoover, P. Birkmeyer, P. B. Umbanhowar, R. S. Fearing, and D. I. Goldman, "Systematic study of the performance of small robots on controlled laboratory substrates," in Micro- and Nanotechnology Sensors, Systems, and Applications II, vol. 7679, pp. 291–303, SPIE, May 2010.

[26] J.-P. Sleiman, F. Farshidian, and M. Hutter, "Versatile multicontact planning and control for legged loco-manipulation," Science Robotics, vol. 8, p. eadg5014, Aug. 2023.

[27] J. Aguilar, T. Zhang, F. Qian, M. Kingsbury, B. McInroe, N. Mazouchova, C. Li, R. Maladen, C. Gong, M. Travers, R. L. Hatton, H. Choset, P. B. Umbanhowar, and D. I. Goldman, "A review on locomotion robophysics: the study of movement at the intersection of robotics, soft matter and dynamical systems," Reports on Progress in Physics, vol. 79, p. 110001, Sept. 2016.

[28] L. Ding, H. Gao, Z. Deng, J. Song, Y. Liu, G. Liu, and K. Iagnemma, "Foot–terrain interaction mechanics for legged robots: Modeling and experimental validation," The International Journal of Robotics Research, vol. 32, pp. 1585–1606, Nov. 2013.

[29] W. Kang, Y. Feng, C. Liu, and R. Blumenfeld, "Archimedes' law explains penetration of solids into granular media," Nature Communications, vol. 9, p. 1101, Mar. 2018.

[30] S. Agarwal, A. Karsai, D. I. Goldman, and K. Kamrin, "Surprising simplicity in the modeling of dynamic granular intrusion," Science Advances, vol. 7, p. eabe0631, Apr. 2021.

[31] J. Aguilar and D. I. Goldman, "Robophysical study of jumping dynamics on granular media," Nature Physics, vol. 12, pp. 278–283, Mar. 2016.

[32] X. A. Wu, T. M. Huh, A. Sabin, S. A. Suresh, and M. R. Cutkosky, "Tactile Sensing and Terrain-Based Gait Control for Small Legged Robots," IEEE Transactions on Robotics, vol. 36, pp. 15–27, Feb. 2020.

[33] S. Choi, G. Ji, J. Park, H. Kim, J. Mun, J. H. Lee, and J. Hwangbo, "Learning quadrupedal locomotion on deformable terrain," Science Robotics, vol. 8, p. eade2256, Jan. 2023.

[34] "Proximal Policy Optimization Algorithms," Aug. 2017.

[35] J. Hwangbo, J. Lee, and M. Hutter, "Per-contact iteration method for solving contact dynamics," IEEE Robotics and Automation Letters, vol. 3, no. 2, pp. 895–902, 2018.

[36] K. Saçılık and A. Çolak, "Dielectric Properties of Opium Poppy Seed," Journal of Agricultural Sciences, vol. 11, pp. 104–109, Jan. 2005.

[37] R. Kovtun, "An overview of lunar regolith simulants," techreport, Simulant Development Lab, NASA JSC-ARES, Sept. 2023.

[38] T. A. Brzinski, P. Mayor, and D. J. Durian, "Depth-dependent resistance of granular media to vertical penetration," Physical Review Letters, vol. 111, p. 168002, Oct. 2013.

[39] A. Daca, D. Tremblay, and K. Skonieczny, "Expansion and Experimental Evaluation of Scaling Relations for the Prediction of Wheel Performance in Reduced Gravity," Microgravity Science and Technology, vol. 35, p. 59, Dec. 2023. ADS Bibcode: 2023MicST..35...59D.



