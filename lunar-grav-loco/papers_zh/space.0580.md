# 自适应月面跳跃策略：理解行为后果的时间关联

> **元信息**
> - 原文标题：Adaptive Lunar Jumping Strategies: Understanding Temporal Associations for Behavior Consequences
> - 中文译名：自适应月面跳跃策略：理解行为后果的时间关联
> - 来源：*Space: Science & Technology* 2026; 6: Article 0580. https://doi.org/10.34133/space.0580
> - 原文文件：`papers/space.0580.pdf`
> - 翻译日期：2026-09-30
> - 投稿 2024-12-02；修回 2026-03-10；录用 2026-04-07；出版 2026-07-14
> - 版权 © 2026 Hanying Sang 等；北京理工大学出版社独家授权；CC BY 4.0 许可

**论文类型**：研究论文（RESEARCH ARTICLE）

**作者**：Hanying Sang¹˒², Jun Li¹˒², Yidong Ye¹˒², Shuquan Wang¹˒²*（*通讯作者：shuquan.wang@csu.ac.cn）

**作者单位**：
1. 中国科学院空间应用工程与技术中心，北京 100094
2. 中国科学院大学，北京 101408

## 摘要

越来越多的月球探测任务要求机器人能够适应月面复杂且不可预测的地形；月面低重力使四足跳跃成为一种高效的移动方式。然而，六分之一地球重力所导致的大幅延长的腾空相，加之其他不变的惯性力，会放大复杂地形中次优跳跃动作及其所产生的角动量引起的旋转效应。为弥补现有模型在理解序列行为长期后果方面的局限，本文提出一种基于 Transformer、采用因果序列输入的强化学习算法，以增强机器人在复杂月面环境中的跳跃适应性。本文设计了面向序列输入流的定制特征提取器，并将其集成到配备 Transformer 注意力机制的强化学习策略头中，采用时间窗口同时保持时间连续性与采样随机性。此外，实现了分阶段课程学习（curriculum learning）框架：以机器人在平地上习得的跳跃与稳定技能为基础，逐步迁移至不同难度的随机崎岖地形以及大小不一、边缘不规则的月坑（lunar pit）。该方法避免了保守策略并提升了训练效率。所提算法在复杂月面仿真任务中成功实现了高效跳跃，并在各项指标上优于消融实验组。

## 引言

月面探测中最具价值的科学发现往往源自对复杂与极端地形的研究，例如月球两极的撞击坑 [1]。然而，现有月球任务大多使用大型巡视器；为降低任务风险，它们通常被限制在平坦地形中探索。这种方式限制了机器人穿越多样地貌并在复杂环境中近距离采集地质与地貌数据的能力 [2]。新时代的需求包括对最极端地貌（如永久阴影区 [3]）的原位探测。四足机器人凭借其悬挂式结构，在规则性较差的地形上具有显著的移动优势——特别是利用跳跃作为运动方式，可充分利用弱引力场特性实现高效移动与越障，展现出巨大的应用前景 [4]。

然而，四足机器人在复杂月面地形中进行低重力跳跃的运动规划与控制面临重要挑战。在结构层面，这类机器人是多连杆冗余机构，其关节自由度之间存在显著的非线性运动耦合 [5]。足端与月面之间各种接触与碰撞模式的转换，使月面呈现动态变化的拓扑结构，令所涉复杂动力学的精确仿真更加困难 [6]。此外，月球重力仅为地球的六分之一，欠驱动跳跃的腾空相被大幅延长，而其他惯性力保持不变；崎岖月面上起飞误判会产生相当大的旋转力矩，使机器人在空中持续旋转，其灾难性后果随时间累积，给着陆控制带来极大不确定性与挑战 [7]。

传统控制方法通过离线计算最优轨迹，可利用系统的非线性动力学及其对控制变量的约束，生成满足代价函数所定义性能指标的运动 [8,9]。然而在以往的工业应用中，机器人通常只能执行重复性任务，难以应对多变性与不确定性。传统反馈控制方法虽对路径跟踪类任务有效，但在涉及机器人—环境接触的应用中面临困难——接触与摩擦难以辨识和刻画，阻碍了自适应、鲁棒控制行为的实现 [4]。进一步地，对于月面广阔、未知且复杂的地形，难以预先设计覆盖所有场景的固定轨迹，也难以事先估计各种系统参数。

近年来，深度强化学习（DRL，deep reinforcement learning）因其解决复杂决策问题的潜力而受到广泛关注 [5,10–14]。DRL 通过与周围环境交互学习应对未知关系的行为，并已证明其可泛化到不同于控制设计阶段的新场景 [15]。控制目标可作为奖励函数的一项间接指定，而非显式由控制动作给出，从而能处理传统控制器难以应对的控制问题 [16]。近期出现了将传统方法与强化学习（RL）相结合的趋势 [17–19]。例如文献 [20] 提出了一种结合 DRL 求解四足跳跃非线性轨迹优化的框架，对扰动机器人站立高度达 33% 的环境噪声实现了鲁棒性。我们的前期工作 [21] 提出了一个结合关键点轨迹生成器与 DRL 的月球低重力跳跃框架，为以最少量人类直觉先验知识进行训练提供了参考。然而，现有模型缺乏对长序列信息的关注，而长序列信息对掌握复杂环境动力学与行为后果至关重要。四足机器人跳跃过程中产生的数据具有明显的时间特征，但传统 DRL 智能体只能以自然时间顺序接收单帧观测进行逐步预测，无法有效利用这些时间数据的相关性或演化规律，难以为高维系统的动力学控制提供充分信息。在复杂决策环境中，未来策略往往依赖一系列动作与状态，而非仅仅是最近的那些。例如人类和其他动物在遇到未知环境时能迅速适应复杂运动，利用既有经验与知识将应对技能迁移到新情境中。这种经验包括在不同条件下采取的不同策略，以及对行为后果与采取这些策略的原因之间关系的深刻理解。类比于月面跳跃，着陆事件受起飞前获得的角动量影响；两个当前相似的状态可能因其截然不同的历史演化过程而走向分歧——这凸显了需要由丰富历史上下文支撑的策略以及预测当前发展趋势的能力。

Transformer 架构因其处理长程依赖的能力而受到关注 [22,23]。近来其跨界应用已成趋势，在图像分类、语义分割与目标检测中取得突破，并被引入 RL 领域，形成了基于 Transformer 的强化学习（TRL，Transformer-based reinforcement learning）[24]。当前 TRL 研究主要分为两类：表征学习与序列决策。表征学习主要利用 Transformer 从多模态输入中提取特征表示，再由智能体通过基于价值或基于策略的方法进行决策 [25]。例如 TransDreamer [26] 与"内部语音自回归想象"方法 [27] 利用基于 Transformer 的世界模型进行预测，并与基于 Transformer 的策略网络共享该世界模型。在表征学习中，Transformer 可将环境中的实体序列作为输入，输出实体间关系的表示以支持更好的策略学习。训练目标通常是回归或分类任务（取决于动作空间），直接学习从状态与累积回报到动作的映射；回归目标通常是最小化预测动作与实际动作之差，倾向于模仿历史中的高回报轨迹。例如多智能体 Transformer [28] 提出了通过环境在线试错训练的编码器—解码器架构，采用同策略（on-policy）方式。在机器人应用领域，Transformer 是整合多模态输入的有效工具：Yang 等人 [29] 提出端到端模型 LocoTransformer，将本体感受状态与深度图像数据作为输入 token 集成到 Transformer 编码器中，使模型能利用两种模态的互补信息进行推理。然而它们仅处理当前时刻的数据。用 Transformer 增强序列输入处理是一个有价值的研究方向。

除作为可与常规 RL 算法结合的表达性架构外，Transformer 还可作为直接执行序列决策的模型，其依据是"RL 可被构建为序列建模问题"这一概念。主要方法包括决策 Transformer（DT，Decision Transformer）[30] 与轨迹 Transformer（TT，Trajectory Transformer）[31]。DT 将 RL 问题视为以奖励为条件的序列建模任务，把 RL 任务转化为监督学习问题，直接使用轨迹数据（状态、动作、累积回报）预测下一个最优动作 [32]。Mao 等人 [33] 提出了名为 Transformer in Transformer 的骨干网络，将内部 Transformer 与外部 Transformer 级联：内部 Transformer 在观测片段（patch）层面处理单个观测，外部 Transformer 处理序列观测（DT 范式）以捕捉多个连续观测间的关键时间信息。Janner 等人 [31] 提出的 TT 用 Transformer 架构对轨迹分布建模，在序列建模任务基础上进一步对状态与奖励转移建模；TT 预测所有状态、动作、奖励 token，且不同于预测未来动作的传统模型，它预测未来状态序列。该方法融入了基于模型的成分以增强轨迹建模能力，并使用额外的束搜索（Beam Search）算法进行规划。例如 Robine 等人 [34] 利用基于 Transformer 的世界模型以自监督方式学习环境动力学的生成模型，通过迭代预测下一状态与奖励生成新轨迹并用于 RL 训练，无需再与真实环境交互，从而提高样本效率。

然而，对于四足机器人在复杂月面地形跳跃的应用，上述方法存在一定局限。如前所述，低重力与未知崎岖地形组成的月球环境对算法的时间感知与决策能力提出了更高要求。仅依赖当前观测做决策的传统 RL 方法易使机器人陷入局部最优，围绕次优状态振荡。尽管 Transformer 架构在长程依赖处理上展现了潜力，现有 TRL 方法（如 DT）依赖高质量示范数据和预定义期望回报作为条件输入来引导动作生成。然而在月面场景中，难以为所有可能地形获取最优跳跃轨迹供 DT 学习，低质量示范数据会导致 DT 生成次优甚至错误的跳跃动作。TT 虽可通过序列建模进行规划，但规划阶段需要束搜索等额外算法遍历可能的未来轨迹；这些组件构成复杂的级联架构并消耗大量计算资源，导致训练时间过长。此外，TT 本质上是拟合历史轨迹的条件分布，倾向于模仿已有数据中的高回报轨迹片段，可能限制其在不同未知月面崎岖地形（如不规则月面几何形态以及地形摩擦与恢复系数变化）上的泛化能力。另外，一些现有 TRL 集成了多个网络模块，如 CoBERL [35] 同时使用 ResNet、BERT [36]、LSTM 与门控；GTrXL [37] 与 Catformer [38] 结合 ResNet、Transformer-XL [39]、门控与多层感知机（MLP）。然而这些复杂架构也会增加训练不稳定性，可能导致策略难以收敛、性能振荡，或在低重力复杂地形跳跃任务中无法维持持续稳定的跳跃。因此有必要开发一种新方法，将时间因果建模（利用历史数据）与 RL 策略优化的稳定训练、高效探索统一起来，绕开对监督示范数据的需求。

针对上述挑战，本文旨在引入一种新型集成方案：在 RL 中利用 Transformer 架构，不仅增强表征深度，还隐式建模因果关系，直接作为理解时间行为后果的策略网络，无需额外的规划算法，也不依赖行为克隆或示范数据。该方法遵循标准 RL 范式，保证训练不完全依赖历史数据质量，保留了 SAC（Soft Actor–Critic，软行动者—评论家）平衡探索与利用的能力，同时通过持续交互不断补充经验数据。

本文的主要贡献如下：**第一**，提出了一种兼具特征提取与序列决策能力的基于 Transformer 的 RL 设计方案，以定制特征提取和因果序列建模作为输入 token。Transformer 的注意力机制捕捉高维提取特征序列中的时间依赖与因果关系，学习隐式关联与动力学理解，在无监督条件下进行决策。**第二**，设计了一种使用时间窗口的经验回放机制，兼顾序列数据的时间连续性与采样随机性：每个采样项包含 $T$ 个连续时间步，但每批数据的起始点随机选取。**第三**，针对多种复杂月面环境中训练适应性的挑战，提出了面向不同任务间迁移学习的分阶段课程：通过设计渐进复杂且随机化的任务，优化智能体积累经验的顺序；通过在源域与目标域之间迁移训练数据实例与模型参数，使智能体能够基于简单任务习得的知识学习复杂任务，增强其面对未知环境的泛化能力。

## 预备知识

在传统 RL 中，马尔可夫性质（Markov property）是一个基本概念：下一状态 $s_{t+1}$ 只依赖当前状态 $s_t$ 与当前动作 $a_t$，此前状态与动作对预测未来状态无关。数学上表示为：

$$P(s_{t+1}\mid s_t, a_t) = P(s_{t+1}\mid s_1, a_1, s_2, a_2, \cdots, s_t, a_t) \tag{1}$$

这适用于围棋等棋类任务——当前棋局布局是唯一重要的因素，与到达该布局的路径无关。然而在机器人跳跃规划与控制等任务中，单一时间点的状态可能不足以完整表示真实当前状况。本文提出的算法使用 Transformer 处理长度为 $T$ 的因果序列（包含某一历史长度内的信息 $s_{t-T+1}, a_{t-T+1}, r_{t-T+1}, \cdots, s_{t-1}, a_{t-1}, r_{t-1}, s_t$）。该方法借鉴了利用历史数据的部分可观测马尔可夫决策过程（POMDP）思想。POMDP 由以下元素组成：状态集合 $S$；动作集合 $A$；状态转移函数 $P$，描述从某状态经动作转移到另一状态的概率分布 $P(s'|s,a)$；奖励函数 $R$；未来奖励的折扣因子 $\gamma$；观测集合 $o$；以及观测函数 $O$，即给定状态与动作获得特定观测的概率分布 $O(o|s,a)$。

在利用历史数据的部分可观测马尔可夫决策过程中，智能体无法直接观测真实当前状态，只能通过局部观测 $o_t \in O$ 获取部分信息，其中观测分布 $P(o_{t+1}|s_{t+1}, a_t)$ 依赖当前状态与前一动作。更好的模型表示 $\pi(a_t|o_t, o_{t-1}, \cdots, o_{t-T+1})$ 应利用过去 $T$ 个时间步的历史观测数据，以缓解无法获取真实状态的影响。在本文算法中，历史数据被利用并进一步转化为因果关系 token $x_{t-T+1:t} = (x_t, x_{t-1}, \cdots, x_{t-T+1})$，提取自状态、动作与奖励序列 $(s_{t-T+1}, a_{t-T+1}, r_{t-T+1}, \cdots, s_{t-1}, a_{t-1}, r_{t-1}, s_t)$。$x_{t-T+1:t}$ 的具体计算方法将在下一节详述。策略模型基于该历史因果序列生成动作：

$$a_t : \pi\bigl(x_{t-T+1:t}\bigr) \tag{2}$$

## 方法

所提算法——基于因果序列 Transformer 的自适应课程强化学习（C-STAR，causal sequence Transformer-based adaptive-curriculum RL）——包含一个带有定制因果历史序列输入的 TRL 和一个分阶段课程迁移学习框架，使机器人具备跳跃并适应复杂月面地形的能力。C-STAR 算法对一定时间窗口长度的状态、动作与奖励序列输入进行高维特征提取，将这些更具表达力的强化特征组合为综合信息，再经位置编码作为 Transformer 架构的因果序列输入，通过注意力机制捕捉行为与其后果之间的长程依赖。该设计使当前动作决策与此前高度抽象的因果序列关联，而非仅基于当前状态，从而通过增加信息量优化决策。此外，考虑到引入 Transformer 后模型复杂度增加，实现快速学习适应也是关键需求：若智能体在无任何先验经验的情况下直接在复杂月面地形上训练高难度跳跃，机器人策略往往会失败。因此进一步提出分阶段课程迁移学习框架，逐步增加训练难度以避免保守策略并促进收敛。C-STAR 算法的总体架构如图 1 所示，包含上述核心创新模块；其中 TRL（注意力增强 SAC）组件与分阶段课程迁移学习框架将在后续小节中结合其他附图进一步详述。下面详细介绍 C-STAR 算法的具体内容。

【图 1：因果序列 Transformer 自适应课程强化学习（C-STAR）算法架构图。左侧为分阶段课程迁移学习流程（Curriculum 1/2，网络参数与交互数据在课程间迁移），中部为经验回放缓冲区与时间窗采样（随机抽取 N 个起始位置、顺序提取 T 元组、裁剪拼接得到序列输入），右侧为注意力增强 SAC 结构（特征提取器 + Transformer 的策略/价值网络及 Critic V、Critic Q 更新）。】

### 带定制因果序列输入的 Transformer 策略

为使模型全面理解动作长期效应与状态转移之间的复杂关系，从而更好地适应低重力月面环境中的复杂任务，构建了带定制因果序列的 Transformer 策略来处理跨连续时间窗口的输入数据。总体结构如图 2 所示。本节详细阐述原始输入数据经定制特征提取器转化为因果序列，再由 Transformer 策略处理产生最终输出的过程。

定制了一个特征提取器处理原始输入数据。首先采用窗口法生成原始输入，选取窗口大小 $T$。对当前决策点 $t$，使用 $T$ 个连续状态、动作与奖励序列 $(s_{t-T+1}, a_{t-T+1}, r_{t-T+1}, \cdots, s_{t-1}, a_{t-1}, r_{t-1}, s_t)$ 作为初始输入。当当前时刻 $t$ 小于序列窗口长度 $T$ 时，不足部分用经验回放缓冲区中取出的历史经验数据自动前向填充；该缓冲区以平地低重力跳跃上一阶段训练的交互数据初始化。第 $i$ 个时间点（$i = t-T+1,\cdots,t$）的状态数据 $s_i$ 由惯性测量单元（IMU）读数 $IMU_i = [roll_i, pitch_i, yaw_i]^T$、关节角 $J_{\theta_i} = [\theta_{1i}, \theta_{2i}, \cdots, \theta_{12i}]^T$ 与关节角速度 $J_{\omega_i} = [\omega_{1i}, \omega_{2i}, \cdots, \omega_{12i}]^T$、机体速度 $V_i = [v_{xi}, v_{yi}, v_{zi}, \omega_{xi}, \omega_{yi}, \omega_{zi}]^T$、以及足端接触传感器读数 $C_i = [c_{1i}, c_{2i}, c_{3i}, c_{4i}]^T$ 组成。动作向量 $a_i$（$i = t-T+1,\cdots,t-1$）为 12 维，表示机器人关节期望角位置。每时刻获得的奖励 $r_i$（$i = t-T+1,\cdots,t-1$）为 1 维标量。

【图 2：带定制因果序列输入的 Transformer 策略头架构。状态、动作、奖励分别经 3 个独立特征提取器 MLP，嵌入为 d 维向量 $x_{t-(T-1)}\dots x_t$，加位置嵌入得 $z_{t-(T-1)}\dots z_t$，经 N 层编码器—解码器后输出动作 $a_t$。】

随后对原始输入数据进行高维特征提取。由于状态、动作与奖励具有不同的模式与含义且存在潜在因果关联，为促进这些模式的领域特征表达，使用定制特征提取器对原始输入预处理，在隐空间中以适配 Transformer 网络输入的统一序列 token 形式表示，再由 Transformer 进一步分析、处理并输出决策。如图 2 所示，定制特征提取器用 3 个独立 MLP 分别对状态、动作与奖励做线性映射（含多个全连接层与激活函数），最终在每一时间步提取统一的 $d$ 维特征向量。3 个特征提取器 MLP 各含 2 个维度为 256 的隐藏层，使用 ReLU 激活函数；输入维度分别对应状态、动作与奖励数据，输出特征维度 $d$ 统一设为 128。原始输入数据经特征提取的具体过程为：设 $s_i\in\mathbb{R}^{d_s}$，$a_i\in\mathbb{R}^{d_a}$，$r_i\in\mathbb{R}^{d_r}$（$i = t-T+1,\cdots,t-1$），进入特征提取器后：

$$E_s(s_i) = W^{(1,n)}\sigma\bigl(\cdots\sigma\bigl(W^{(1,2)}\sigma\bigl(W^{(1,1)}s_i + b^{(1,1)}\bigr) + b^{(1,2)}\bigr)\cdots\bigr) + b^{(1,n)} \tag{3}$$

其中：

$$W^{(1,1)}\in\mathbb{R}^{h_1\times d_s},\ b^{(1,1)}\in\mathbb{R}^{h_1};\quad W^{(1,k)}\in\mathbb{R}^{h_f\times h_f},\ b^{(1,k)}\in\mathbb{R}^{h_f},\ (k=2,\cdots,n-1);\quad W^{(1,n)}\in\mathbb{R}^{d\times h_f},\ b^{(1,n)}\in\mathbb{R}^{d} \tag{4}$$

$n$ 为 MLP 网络层数，$h_1$ 为第一嵌入层的输出维度；对后续每个全连接层配置相同的隐藏层维度 $h_f$。类似地：

$$E_a(a_i) = W^{(2,n)}\sigma\bigl(\cdots\sigma\bigl(W^{(2,2)}\sigma\bigl(W^{(2,1)}a_i + b^{(2,1)}\bigr) + b^{(2,2)}\bigr)\cdots\bigr) + b^{(2,n)} \tag{5}$$

$$E_r(r_i) = W^{(3,n)}\sigma\bigl(\cdots\sigma\bigl(W^{(3,2)}\sigma\bigl(W^{(3,1)}r_i + b^{(3,1)}\bigr) + b^{(3,2)}\bigr)\cdots\bigr) + b^{(3,n)} \tag{6}$$

其中：

$$W^{(2,1)}\in\mathbb{R}^{h_1\times d_a},\ b^{(2,1)}\in\mathbb{R}^{h_1};\quad W^{(2,k)}\in\mathbb{R}^{h_f\times h_f},\ b^{(2,k)}\in\mathbb{R}^{h_f},\ (k=2,\cdots,n-1);\quad W^{(2,n)}\in\mathbb{R}^{d\times h_f},\ b^{(2,n)}\in\mathbb{R}^{d}$$

$$W^{(3,1)}\in\mathbb{R}^{h_1\times d_r},\ b^{(3,1)}\in\mathbb{R}^{h_1};\quad W^{(3,k)}\in\mathbb{R}^{h_f\times h_f},\ b^{(3,k)}\in\mathbb{R}^{h_f},\ (k=2,\cdots,n-1);\quad W^{(3,n)}\in\mathbb{R}^{d\times h_f},\ b^{(3,n)}\in\mathbb{R}^{d} \tag{7}$$

$E_s(s_i)$、$E_a(a_i)$、$E_r(r_i)$ 经上述特征提取器变换后均为 $d$ 维向量。将时刻 $i$ 的 $E_s(s_i)$、$E_a(a_i)$、$E_r(r_i)$ 相加得到嵌入结果 $z_i$；最后时刻的 $E_s(s_t)$ 直接作为该时刻嵌入结果，即：

$$\begin{aligned} z_i &= E_s(s_i) + E_a(a_i) + E_r(r_i),\quad i = t-T+1,\cdots,t-1\\ z_i &= E_s(s_i),\quad i = t \end{aligned} \tag{8}$$

接下来进行位置编码，使模型能理解输入序列各元素间的时间关系。位置编码 $P$ 定义为：

$$\begin{aligned} P(i, 2j) &= \sin\left(\frac{i}{10000^{2j/d_{model}}}\right)\\ P(i, 2j+1) &= \cos\left(\frac{i}{10000^{2j/d_{model}}}\right) \end{aligned} \tag{9}$$

其中 $i = t-T+1,\cdots,t$ 表示当前输入 token 在整个输入序列中的位置；$d_{model}$ 为每个时间点向量的维度。在时间步 $t_i$，输入数据采用配对维度：第 $2j$ 维用正弦编码，第 $2j+1$ 维用余弦编码，即正弦用于偶数维位置、余弦用于奇数维位置。

$$x_i = z_i + P(i),\quad i = t-T+1,\cdots,t \tag{10}$$

至此，Transformer 网络获得了包含位置信息的输入序列 $x_{t-T+1},\cdots,x_t$，序列长度为 $T$，向量维度为 $d$。所用 Transformer 模型采用 4 层编码器与 4 层解码器堆叠，每层含 8 个注意力头；嵌入维度 $d_{model}$ 设为 128，前馈网络（FFN）隐藏维度为 512；每个子层（自注意力网络与 FFN）之后施加残差连接与层归一化，dropout 率 0.1 以防过拟合。下面介绍位置编码后的数据流。

输入数据进一步流入 $N$ 层堆叠的编码器层，执行多层自注意力，使模型能在多个抽象层次上理解时间输入数据的内在关联。进入每个编码器后，输入向量依次经过自注意力层、残差连接与层归一化、前馈神经网络、再一次残差连接与层归一化得到输出，继续送入下一编码器。当输入数据进入第 $m$ 个（$m = 0,\cdots,N-1$）编码器时，注意力层首先通过 3 种不同的线性变换生成查询（Q）、键（K）、值（V）向量：

$$X_Q^{(m)},\ X_K^{(m)},\ X_V^{(m)} = X^{(m-1)}W_Q^{(m)},\ X^{(m-1)}W_K^{(m)},\ X^{(m-1)}W_V^{(m)} \tag{11}$$

其中 $W_Q^{(m)}$、$W_K^{(m)}$、$W_V^{(m)}$ 为可学习的权重矩阵。随后计算查询与所有键的点积并施加 softmax 函数得到注意力权重：

$$W_T^{(m)} = \mathrm{Softmax}\left(\frac{X_Q^{(m)}X_K^{(m)T}}{\sqrt{d_K}}\right) \tag{12}$$

其中 $d_K$ 为 $X_K^{(m)}$ 的维度，该归一化步骤防止点积过大。注意力权重乘以值向量得到加权值向量 $At^{(m)}$，即自注意力层的输出，使模型在每个位置都能兼顾整个输入序列的信息：

$$At^{(m)} = W_T^{(m)}X_V^{(m)} \tag{13}$$

随后经残差连接与层归一化得到归一化输出 $Y^{(m)}$；再通过 2 层前馈神经网络以及又一轮残差连接与层归一化，得到最终输出，同时作为下一编码器的输入 $X^{(m+1)}$：

$$Y^{(m)} = LN\bigl(At^{(m)} + X^{(m)}\bigr)$$
$$X^{(m+1)} = LN\bigl(MLP\bigl(Y^{(m)}\bigr) + Y^{(m)}\bigr) \tag{14}$$

其中 $LN$ 表示层归一化。类似地，解码器由 $N$ 个顺序排列的解码器层组成，每层包含自注意力、编码器—解码器注意力机制与前馈神经网络。解码器用于计算注意力的输入数据为编码器处理后的结果 $X^{(N)}$；第 $m$ 个解码器的自注意力结果为：

$$\begin{aligned} \hat X_Q^{(m)}, \hat X_K^{(m)}, \hat X_V^{(m)} &= X^{(N)}W_{\hat Q}^{(m)},\ X^{(N)}W_{\hat K}^{(m)},\ X^{(N)}W_{\hat V}^{(m)},\ m=1\\ \hat X_Q^{(m)}, \hat X_K^{(m)}, \hat X_V^{(m)} &= \hat X^{(m-1)}W_{\hat Q}^{(m)},\ \hat X^{(m-1)}W_{\hat K}^{(m)},\ \hat X^{(m-1)}W_{\hat V}^{(m)},\ m>1 \end{aligned} \tag{15}$$

$$\hat{At}^{(m)} = \mathrm{Softmax}\left(\frac{\hat X_Q^{(m)}\hat X_K^{(m)T}}{\sqrt{d_{\hat K}}}\right)\hat X_V^{(m)} \tag{16}$$

与编码器类似，经残差连接与层归一化后，注意力结果 $\hat Y^{(m)}$ 即为第 $m$ 个解码器自注意力层的输出：

$$\hat Y^{(m)} = LN\bigl(\hat{At}^{(m)} + X^{(N)}\bigr) \tag{17}$$

在第 $m$ 个解码器的编码器—解码器注意力层中，查询（Q）来自第 $m$ 个解码器带掩码自注意力层的输出 $\hat Y^{(m)}$，键（K）与值（V）来自编码器最终输出 $X^{(N)}$；同时编码器—解码器注意力 $\hat{At}_{E-D}^{(m)}$ 为：

$$\hat{At}_{E-D}^{(m)} = \mathrm{Softmax}\left(\frac{\hat Y^{(m)}X_K^{(N)T}}{\sqrt{D}}\right)X^{(N)} \tag{18}$$

其中 $D$ 为键向量 $X^{(N)}$ 的维度。前馈神经网络、残差连接与层归一化的操作与编码器相同。最终得到第 $N$ 个解码器的输出 $X^{(N)}\in\mathbb{R}^{T\times d}$。由于外部 Transformer 中存在掩码操作，只有 $X^{(N)}$ 的最后一个元素能完整刻画所有已观测信息。因此将解码器在最后时间步的输出 $X^{(N)}[t]$ 经单层全连接网络（FFN）映射为动作分布的均值与对数标准差；该全连接层输出维度与动作空间维度一致，为 12。动作采样时采用重参数化技巧（reparameterization trick）以保证梯度传播：

$$a_t : FFN\bigl(X^{(N)}[t]\bigr) \tag{19}$$

### 与 SAC 的集成

考虑到离线 RL 随机采样与输入数据序列依赖性之间的矛盾，对经验回放机制进行改进，以将上述带因果序列输入的 Transformer 策略集成到 SAC 框架中。传统上，从经验回放缓冲区随机采样包含 $N$ 个五元组的小批量 $\{(s_{t_1}, a_{t_1}, r_{t_1}, s_{t_1+1}, d_{t_1}), \cdots, (s_{t_n}, a_{t_n}, r_{t_n}, s_{t_n+1}, d_{t_n})\}$（$d_t$ 为终止标志），这意味着数据在时间上不连续，与 Transformer 处理具有明确时间关系数据的意图相矛盾。因此修改经验回放机制，采用时间窗口策略获取 $N$ 个起始点随机的连续时间步序列，记为 $\{(s_{t_1-T+1}, a_{t_1-T+1}, r_{t_1-T+1}, \cdots, s_{t_1-1}, a_{t_1-1}, r_{t_1-1}, s_{t_1}), (s_{t_2-T+1}, a_{t_2-T+1}, r_{t_2-T+1}, \cdots, s_{t_2-1}, a_{t_2-1}, r_{t_2-1}, s_{t_2}), \cdots, (s_{t_N-T+1}, a_{t_N-T+1}, r_{t_N-T+1}, \cdots, s_{t_N-1}, a_{t_N-1}, r_{t_N-1}, s_{t_N})\}$，在序列的时间连续性与采样随机性之间取得平衡。

使用上述方法的算法流程见原文 Algorithm 1（伪代码：时间窗采样、序列裁剪拼接、Transformer 前向传播、SAC 双 Q 网络与策略网络更新）。Transformer 模型接收这些小批量序列并前向传播，计算策略网络与价值网络的输出。按 SAC 算法，通过最小化价值网络损失与最大化策略网络期望回报，同时优化策略与价值网络。训练过程批量大小为 256，熵系数 0.005，折扣因子 0.99，经验回放缓冲区容量 $5\times10^6$ 条。考虑到任务内存需求与计算资源之间的权衡，时间窗口长度 $T$ 设为 200，每时间步 0.02 s，与月球重力下机器人一个跳跃周期的平均时长对齐。

该采样设计同时保证了序列内时间连续性与序列间采样随机性，兼具随机采样与序列连贯的优点：**其一**，序列内连续性保留了状态、动作、奖励之间的长程因果依赖，使基于注意力的策略模型能捕捉隐式长程动力学并做出有预见性的决策——例如预判起飞与腾空相动作对后期着陆稳定性的影响。**其二**，同批内不同序列的随机起始点大幅降低了序列间样本相关性，使样本近似独立同分布，从而缓解过拟合。随机起始点促使算法探索多样的环境状态，防止策略过度聚焦于特定经验轨迹。该选择机制保证各种历史经验仍有被采样的机会，避免过早收敛到局部最优，保留了算法固有的探索与泛化能力。

### 分层分阶段课程迁移学习框架

为应对机器人在复杂月面地形中的适应性挑战，并防止算法在无先验经验时的"冷启动"问题，引入了分层分阶段课程迁移学习框架，渐进式地构建智能体的学习过程。月面不规则极端地形增大了起飞难度；由于低重力下腾空相延长，初始跳跃的小误差都可能导致机体严重旋转或失稳，这对机器人四肢协调性提出更高要求。若 RL 智能体在无先验经验时直接在仿真的复杂月面地形上训练，往往会为避免频繁跌倒惩罚而做出过度保守的决策，甚至停止运动。相比之下，人类面对陌生的复杂问题能快速学习适应，因为人脑在本质上是基于迁移学习运作的：遇到新情况时将过往经验内化为知识库，迅速为新挑战构建策略。从出生起积累的多样化经验为应对新问题提供了丰富的知识储备。

借鉴人类学习机制，人为设计了难度递增的训练任务。具体而言，智能体首先在仿真的简单平地上训练；随着算法性能提升，逐步引入更复杂的地形特征，如不同程度的崎岖度、更强的随机化以及更深的坑，最终具备满足真实月面任务环境需求的能力。如图 3 所示，在每一级复杂地形训练中，智能体利用迁移学习机制将上一任务的数据实例与已习得模型参数迁移到下一任务。通过迁移学习，智能体复用源任务中获得的知识以快速适应新的目标任务，这已被证明能提升解决复杂问题的性能或缩短收敛到最优策略所需的时间 [40–43]。该方法的本质是模拟人类学习过程：先掌握基本技能，再渐进至更复杂任务，最终目标是获得跨多种地形的适应能力。奖励函数在每个训练回合的跳跃周期内按不同阶段分层设计，将跳跃动作划分为起飞、腾空与着陆等多个阶段；针对各阶段的不同目标设计了细粒度子任务奖励函数，详见前期工作 [21]。这种分层奖励机制帮助机器人专注于各阶段关键技能，如起飞时的快速能量释放、腾空时的稳定维持以及着陆时的缓冲吸能。

【图 3：分层分阶段课程迁移学习框架架构图。展示 Curriculum 1（Episode 1…L1）、Curriculum 2、Curriculum 3 三个层级间网络参数与交互数据（知识）的逐级迁移，以及一个跳跃周期的训练回合。】

## 仿真实验

本节在若干不同的仿真月面环境中验证所提 C-STAR 方法。

### 仿真实验设置

为全面评估算法性能，构建了融合月面核心地形特征的仿真环境，以评估低重力与复杂地表条件下的运动控制效果；此外增强了地形随机化粗糙度，以同时提升训练与测试阶段的鲁棒性。

**月面地形建模**：为复现月球撞击坑与不规则地形的典型特征，首先使用 Unreal Engine 4 生成月面地形网格模型，确保其具有区别于平地的曲面轮廓与不规则起伏。这些模型以 object（obj）文件格式导出。如图 4 所示，图 4A 与 4B 展示了两种代表性地形——大型浅撞击坑与小型月坑——用于评估不同类别的跳跃任务。每个子图同时显示 obj 模型的可视化渲染（左）与其表面三角网格（右），直观展示不规则的凹凸几何形态。随后将模型导入 PyBullet 物理引擎，分别用 `createVisualShape` 与 `createCollisionShape` 加载几何视觉与碰撞属性。关键参数——网格缩放、全局位置、朝向四元数及物理属性（质量、侧向摩擦与恢复系数）——经配置以保证基础地形尺寸满足机器人运动范围需求。

【图 4：月面地形仿真模型。(A) 大型浅撞击坑；(B) 月坑。每个子图左侧为渲染效果，右侧为表面三角网格。】

**程序化粗糙度生成**：为渐进增加任务难度、增强机器人对高度不规则月面的适应性，在基础网格（如图 4A 的大坑中心）上叠加程序化生成的微地形，模拟细粒度表面粗糙度。该程序化地形使用 PyBullet 的 heightfield 方法构建，流程集成域随机化（domain randomization）以提升策略鲁棒性：

- **网格参数化**定义高度场的分辨率（每米采样数）与物理尺寸，在计算效率与空间保真度之间取得平衡；
- **高度数据生成**通过均匀采样产生随机高度矩阵 $H\in[0,1)^{M\times N}$，乘以缩放因子控制地形起伏幅度；
- **高斯滤波平滑**（`scipy.ndimage.gaussian_filter`，σ=3）消除突变伪影，生成过渡自然、近似真实月面形态的地形；
- **碰撞形状创建**将处理后的高度图传入 `createCollisionShape` 并配以合适的 `meshScale` 参数，将网格映射到仿真环境的物理坐标；
- **域随机化**在每个训练回合开始时对摩擦与恢复系数随机化，引入地形物理属性的变异性，模拟月壤（regolith）的不确定特性，培养策略对多样表面条件的鲁棒性。

本文提出的 C-STAR 算法的核心创新在于集成两个创新模块：带定制因果序列输入的 Transformer 策略，以及用于训练的分层分阶段课程迁移学习框架。本节除验证所提算法能使四足机器人在复杂月面环境中完成跳跃任务外，还旨在验证两个议题：(a) 相比基线，这两个创新模块的引入是否有效改善了训练效果或任务指标；(b) 这两个创新模块具体如何促进整体算法框架。

为验证上述两个议题并进行系统评估，设计了一系列对照实验，包括完整算法 C-STAR 与 3 个消融变体，具体设置如下：

- **完整算法 C-STAR**：同时使用带定制因果序列输入的 Transformer 策略与分层分阶段课程迁移学习框架；
- **消融组 1**：仅使用分层分阶段课程迁移学习框架；
- **消融组 2**：仅使用带定制因果序列输入的 Transformer 策略；
- **消融组 3**：基线模型，即不含任何创新模块的标准 SAC 算法。

### 任务设计

核心目标是训练机器人在不规则地形上跳跃，并利用跳跃进出特殊场景。为全面评估算法性能，设计了 3 类跳跃任务：**任务 1** 聚焦于在随机崎岖月面地形上跳跃；**任务 2** 针对下行跳跃（自高向低，即从坑缘跳入月坑）；**任务 3** 针对上行跳跃（自低向高，即从坑内跳出至坑缘）。每项任务采用逐步增加难度的课程以实现由简到难的技能迁移，如图 5 所示。任务 1 从平地训练开始，随后进入中等起伏地形（随机起伏粗糙地形 I），最终到达最大起伏的目标地形（随机起伏粗糙地形 II）。粗糙地形 I、II 的起伏程度可视化见图 6，横轴为地形 x 方向，纵轴为 y 方向，颜色表示高度的随机起伏程度。任务 2 以任务 1 的最终阶段（粗糙地形 II）作为课程 1，随后进入中等尺寸月坑跳入任务（Pit I，深 1.5 m），最终到达目标尺寸月坑跳入任务（Pit II，深 2.3 m）。任务 3 遵循类似的月坑跳出进阶，使用相同的 Pit I 与 Pit II 场景。

【图 5：3 个跳跃任务的课程设计图，分别展示任务 1（平地→随机起伏粗糙地形 I→II）、任务 2（粗糙地形 II→Pit I 跳入→Pit II 跳入）与任务 3（粗糙地形 II→Pit I 跳出→Pit II 跳出）的课程阶段与起止点。】

【图 6：地形起伏程度可视化，左为随机起伏粗糙地形 I，右为随机起伏粗糙地形 II，颜色表示高度随机起伏程度。】

为基准化算法性能，选取每项任务最具挑战性的课程阶段作为测试场景：任务 1 用随机起伏粗糙地形 II，任务 2 用 Pit II 跳入，任务 3 用 Pit II 跳出。这些场景涵盖了各自任务的核心挑战，能有效区分不同算法的泛化能力与鲁棒性。

### 评价指标

针对 3 类地形任务，定义以下评价指标以全面评估所提算法与消融组的性能：

1. **训练效率**：训练效率反映算法对复杂环境的适应速度，是衡量算法性能的关键指标，通过各训练阶段回合回报的收敛数据衡量；
2. **运动性能**：通过特定任务跳跃过程中关键动作的快照展示；
3. **跳跃稳定性指标**：通过跳跃中机体晃动（俯仰角速度范围）及腿部关节力矩数据体现。

## 结果与讨论

本实验评估所提 C-STAR 算法在 3 类典型月面跳跃任务中的性能，并与消融组对比以验证各创新模块的有效性。预期目标为：任务 1 要求在随机崎岖地形上实现稳定连续跳跃，根据前期平地结果将目标跳跃距离设为 2.7 m；任务 2 要求从高处坑缘平滑进入 Pit II 且着陆时保持姿态稳定；任务 3 要求成功从坑底跳出并在坑缘着陆时有效缓冲、保持平衡。如表 1 所示，完整 C-STAR 达成了所有目标（标记 T），而消融组因缺乏时间推理或课程迁移学习而失败或表现欠佳。下面给出各任务与预期目标的详细对比。

**表 1. 3 个跳跃任务的结果对比。**

| 任务 | 指标 | C-STAR | 消融组 1 | 消融组 2 | 消融组 3 |
|---|---|---|---|---|---|
| 任务 1 | 成功（T/F） | T | F | T | F |
| 任务 1 | 平均跳跃高度/m | 1.70 | — | 1.01 | — |
| 任务 1 | 平均跳跃距离/m | 2.71 | — | 1.21 | — |
| 任务 2 | 成功（T/F） | T | F | F | F |
| 任务 3 | 成功（T/F） | T | F | F | F |

（C-STAR：基于因果序列 Transformer 的自适应课程强化学习）

### 任务 1：在随机崎岖月面地形上跳跃

首先给出任务 1 的结果，即在月面随机崎岖地形上跳跃。图 7 展示了完整算法与 3 个消融实验在一个跳跃周期内的快照。图 7A 显示 C-STAR 成功完成单次跳跃，高度达 1.71 m、距离 2.71 m，且机器人能在连续跳跃中保持该水平指标。由于粗糙地形起伏的随机性，机器人经大量训练后采用了四足相对同相的起跳方式以维持机身稳定、防止翻转，同时微调四腿不同的发力模式以适应接触点处的地面不平。图 8A 给出跳跃过程中腿部关节力矩数据：成功跳跃所需力矩仅在起飞与着陆阶段显著偏高——执行平衡机动需要复杂的施力；腾空后力矩保持为零，滞空后期仅有少量扰动用于微调动作细节。反映机器人纵转（俯仰）方向动态稳定性的俯仰角速度如图 9A 所示（逆时针旋转记为负值）。机器人在初始化与起飞初始阶段有轻微上仰调整，对应初始的负值段；快速起跳中机体角度经历下俯变化，并在整个滞空相保持近似为零的极小逆时旋转；着陆阶段机体角速度经短暂振荡缓冲调整后，在落地瞬间产生负俯仰角速度，帮助机器人从轻微倾斜恢复到初始水平状态，此后俯仰角速度归零。

【图 7：任务 1 中 C-STAR 与消融组的跳跃快照对比。(A) C-STAR；(B) 消融组 1；(C) 消融组 2；(D) 消融组 3。】

【图 8：任务 1 中 C-STAR 与消融组的关节力矩对比。(A) C-STAR；(B) 消融组 1；(C) 消融组 2；(D) 消融组 3。】

【图 9：任务 1 中 C-STAR 与消融组的俯仰角速度对比。】

综上，任务 1 中 C-STAR 算法在随机崎岖月面地形上成功实现稳定跳跃：跳跃距离与 2.7 m 目标基本一致，滞空相姿态稳定性指标（俯仰角速度）保持近零值，整体跳跃性能达到预期目标。

C-STAR 的训练曲线如图 10 所示。任务 1 的课程 I 中，智能体从零开始训练：此时策略随机，回报从低值起步并随训练逐渐增加直至稳定。从课程 I 迁移到课程 II 时，课程 II 的初始回报高于课程 I 的起点，因为课程 II 在课程 I 策略基础上进一步优化——这种现象称为**起步提升效应（jumpstart effect）**：智能体能利用上一阶段获得的策略与知识，在更复杂任务中获得更好的起点并在更高策略水平上继续改进。类似地，课程 III 相对课程 II 的表现进一步验证了课程学习的优势：每个新课程建立在前一课程之上，逐步优化策略，获得更高的稳定回报。

【图 10：任务 1 中 C-STAR 的课程训练曲线（可见两次明显的 jumpstart 提升）。】

消融组 1 与完整算法的结果对比凸显了理解时间关联与动作预判的重要性。机器人需要通过一系列连续动作完成跳跃过程——起飞、腾空与着陆并非相互独立，而是彼此影响的关联阶段：先前动作的质量决定后续策略如何调整，后续动作又受先前动作积累的角动量等因素影响。如图 7B 所示，消融组 1 缺少序列化 Transformer 架构输入，机器人无法有效捕捉和理解动作间的因果关系，导致在崎岖地形上协调性差，更易因无法有效缓冲着陆冲击、维持平衡而跌倒——尽管跳跃最高点超过 1.7 m。图 9B 的俯仰角速度数据显示：着陆冲击阶段初期出现大的正值，随后持续为负，直至角度累积达到恢复平衡的阈值，最终向后跌倒。

无法对因果时间依赖建模在行为层面表现为"反应式"而非"预测式"的策略模式：与完整 C-STAR 算法不同，机器人无法基于历史观测预判起飞处地形起伏将如何影响随后的滞空相与着陆。因此策略呈现带迟滞的延迟响应特征，机器人无法在灾难性失败发生前采取预防措施，而倾向于在失败症状显现后才补救，显著增大失败风险。这种事后再补偿的行为模式反映了机器人缺少跳跃动力学的隐式学习模型，仅依赖当前传感反馈，在低重力崎岖地形下不足以实现稳定控制。

消融组 2 与完整算法的对比凸显了分阶段课程迁移学习框架在策略成熟度方面的作用。消融组 2 仅引入 Transformer 策略，训练后虽能在随机起伏粗糙地形 II 上完成完整跳跃，但缺少分层分阶段课程迁移学习使其策略较完整算法更保守、效果更差，性能指标更低——单次跳跃高度 0.96 m、距离 1.17 m。滞空相关节力矩出现一定振荡（图 8C）；俯仰角速度（图 9）在滞空过程中持续在俯冲与后仰之间交替，没有稳定归零的阶段，进一步说明缺少分阶段课程引导的知识迁移导致策略成熟度与稳定性均逊于相同训练条件下的完整 C-STAR。消融组 2 的振荡行为表明策略未收敛到稳定的极限环：滞空相持续存在无效的晃动动作，表现为俯仰角速度连续波动；智能体被迫牺牲跳跃距离优化以换取崎岖地形上稳定着陆的奖励，表明无课程学习训练的策略仅达到局部最优。

消融组 3 与其他组的对比凸显了两个创新模块的协同效应。消融组 3 既无 Transformer 网络也无分阶段课程迁移学习，机器人完全丧失了应对复杂地形的能力：起飞时无法有效应对不平地面，四腿发力与地面不同高度/平整度不匹配，导致旋转并随后跌倒（图 7D）。图 8D 的力矩数据显示，起飞时机不当后，机器人在空中旋转阶段约 1.2 s 处尝试简单的收腿动作，但无法抵消角动量积累的不平衡。图 9 的俯仰角速度数据显示初始跳跃振荡后持续为负，表明机器人在跳跃中无法维持纵向平衡，最终失去姿态控制。双模块同时缺失的结果与仅缺单一模块不同，说明这些组件并非独立叠加而是相互强化：Transformer 提供地形预判与适应所需的时间推理能力，课程学习则提供渐进精化该推理的结构化训练引导。二者协同学习产生稳定策略，能在随机化回合中持续生成成熟的机体俯仰控制并可重复成功；而消融组 3 在相同训练条件下回合间差异大，无法获得稳定成功的策略。

### 任务 2：跳入月坑

从凹凸不平的坑缘跳入月坑要求机器人在起飞时执行前向跳跃，以尽量小的垂直方向冲击平稳着陆。图 11A 展示了完整 C-STAR 算法成功执行该过程：机器人用腿向后蹬地实现前向跳入 Pit II——这不同于高跳采用的下蹬策略。着陆时需要适当的力矩缓冲冲击、实现稳定触地，如图 12A 所示。图 13 的俯仰角速度数据表明，整个跳跃过程中除起飞初始的俯仰变化外，机体保持稳定不变的平衡角直至着陆；触地冲击时机体先逆时针旋转吸震，随后通过矫正旋转恢复平衡角。训练曲线（图 14）显示任务 1 与任务 2 之间存在明显差异：与图 10 中第一次起步提升相比，从"随机起伏粗糙地形 II 跳跃"课程 I 迁移到"Pit I 跳入"课程 II 时初始起步提升较低；但从课程 II 迁移到最终任务时观察到第二次起步提升，训练后回报再度提升。总体而言，任务 2 中 C-STAR 算法使机器人从坑缘成功平滑跳入 2.3 m 深月坑，通过适当力矩缓冲在着陆时保持姿态稳定；滞空相俯仰角速度稳定在零附近，着陆后经姿态调整迅速恢复机体平衡，满足预期目标。

【图 11：任务 2 中 C-STAR 与消融组的跳跃快照对比。(A) C-STAR；(B) 消融组 1；(C) 消融组 2；(D) 消融组 3。】

【图 12：任务 2 中 C-STAR 与消融组的关节力矩对比。(A) C-STAR；(B) 消融组 1；(C) 消融组 2；(D) 消融组 3。】

【图 13：任务 2 中 C-STAR 与消融组的俯仰角速度对比。】

消融组 1 在图 11B 的月坑跳入任务中表现出与随机崎岖地形跳跃类似的后倾，再次反映其因缺乏对时序动作因果关系理解导致的稳定性问题：起飞不当使机器人失去平衡并最终跌倒，且未能有效扭转失衡。图 13B 的俯仰角速度数据表明，初始起飞阶段的误差使机器人保持持续负角速度，即持续失衡状态；图 12B 的力矩数据显示机器人腾空后关节无进一步运动调整，进一步说明其缺少跳跃后的补偿调节策略，导致不当旋转失控地累积放大。

消融组 2 中，仅引入 Transformer 策略使机器人勉强能执行跳入月坑（图 11C），但无法在着陆时保持机体平衡。图 12C 显示着陆瞬间机器人施加一定力矩试图减缓冲击；然而缺少课程迁移学习使着陆策略在有限训练回合内优化不充分，机器人未能找到软着陆的最优方法。图 13C 的俯仰角速度数据显示，与完整 C-STAR 相比，消融组 2 在滞空相存在持续负角速度、机体处于轻微后仰状态；着陆后短时间内出现大正角速度导致跌倒，进一步表明缺少课程训练导致策略平滑性与成熟度不足。

消融组 3 问题最严重：与消融组 1 类似，机器人起飞后立即明显后转并迅速跌倒（图 11D）。与消融组 1 相比，图 12D 的力矩数据显示其在滞空相有额外的振荡输出，表明机器人试图进一步收后腿；但图 13 的俯仰角速度显示更大的负角速度，体现了缺少分阶段课程迁移学习造成的差异。

### 任务 3：跳出月坑

月坑跳出任务与随机崎岖地形跳跃有相似之处，但月坑的独特环境对机器人着陆策略提出了新要求。如图 15A 所示，C-STAR 快照显示机器人起飞后采取后腿微张的策略以平衡机体、缓解潜在后倾。在接近跳跃顶点时，机器人下落速度较低时着陆，需要更早地在空中预判即将到来的着陆。图 16A 表明坑缘着陆时的力矩数据幅值相对任务 1、2 更小；图 17 的俯仰角速度显示滞空相有轻微负角速度，但机器人最终能通过着陆策略调整并稳定在平衡的机体角。任务 3 中 C-STAR 算法成功实现了从 2.3 m 深坑底跳出并稳定着陆于坑缘：滞空相俯仰控制与着陆缓冲策略均达到预期性能标准。

【图 15：任务 3 中 C-STAR 与消融组的跳跃快照对比。(A) C-STAR；(B) 消融组 1；(C) 消融组 2；(D) 消融组 3。】

【图 16：任务 3 中 C-STAR 与消融组的关节力矩对比。(A) C-STAR；(B) 消融组 1；(C) 消融组 2；(D) 消融组 3。】

【图 17：任务 3 中 C-STAR 与消融组的俯仰角速度对比。】

相比之下，消融组 1 因错误的起飞策略在跳跃早期积累大量顺时针角变化，最终因跳跃高度不足撞上坑壁（图 15B）。消融组 2 的快照（图 15C）显示与消融组 1 类似的失败原因，力矩数据见图 16C。尽管消融组 2 借助 Transformer 策略跳得比消融组 1 更高、对俯仰角速度控制相对更好，但缺少分阶段课程迁移学习仍导致其对着陆位置判断失误，预留着陆空间不足而未能成功着陆，反映了单一模块在提升整体策略能力上的局限。

图 15D 中消融组 3 因剧烈后翻失败，起飞力矩数据见图 16D，图 17 中俯仰角速度持续为大负值，进一步凸显传统 RL 在相同训练条件下、无创新模块辅助时难以适应复杂月坑跳跃任务。训练曲线（图 18）表明：相比任务 2，任务 3 早期策略与任务 1 更为相近，因此从"随机崎岖月面地形跳跃"课程 I 迁移到"Pit I 跳出"课程 II 时的初始起步提升远大于图 14 中的第一次起步提升；从课程 II 迁移至最终任务的训练过程中实现了稳定收敛。只有完整 C-STAR 算法能完成任务 3，证明了集成两个创新模块在月坑跳出姿态控制中的优势。

【图 14：任务 2 中 C-STAR 的课程训练曲线（可见两次 jumpstart 提升）。】

【图 18：任务 3 中 C-STAR 的课程训练曲线（可见两次 jumpstart 提升）。】

总体而言，从行为解读角度看，根本区别在于 C-STAR 习得的是预测性前馈补偿机制，而消融组是短视的反应式、事后补偿响应。四足跳跃是非完整约束（non-holonomic constraints）下的典型连续动力学过程：起飞时施加的力矩不仅决定跳跃距离，还通过角动量交换决定空中姿态演化；空中姿态无法像支撑相那样通过足—地反作用力的及时反馈轻易调整。滞空相构成受角动量守恒约束的欠驱动浮动基座系统，需要能预判滞空相旋转动力学并在起飞时实施预先补偿调整的预测性策略，而非仅能在地面接触时生效的即时反应式反馈机制。通过注意力机制，C-STAR 建立了将当前动作映射到未来状态的预测性因果链，能在起飞瞬间预测当前动作的着陆后果并据此预调动作方案。相比之下，消融组 1 缺乏时间建模能力，仅依赖当前状态做短视贪心决策，导致起飞时积累的俯仰角动量在滞空相无法被有效预测或补偿。从学习稳定性角度看，缺少前瞻性策略规划使机器人无法有效补偿地形扰动、抑制误差累积，导致角速度发散并最终丧失纵向稳定性。从策略演化与学习稳定性角度看，分阶段课程学习驱动策略沿策略流形从保守但次优的解向高效成熟策略演化，同时渐进扩展可行解空间以避免局部最优。消融组 2 中观测到的力矩振荡本质上表明策略尚未收敛到平滑最优；尽管引入了 Transformer 网络，从零学习最高难度任务使机器人收敛到次优跳跃模式。通过渐进增加地形复杂度，课程学习有效引导策略优化轨迹沿"由简单动力学向复杂动力学"的路径渐进演化，避免了训练中的梯度方差爆炸与策略振荡。对于消融组 3，我们进一步分析了双模块缺失导致的级联失败，阐明了 Transformer 与课程学习构成的"表征—优化"正反馈回路。

## 结论

理解与行为后果存在时间关联的序列信息，对机器人在复杂环境中执行月面探测任务至关重要。本文提出了带定制因果序列输入的 Transformer 策略并将其集成到 SAC 框架中，利用注意力机制生成具有隐式理解与预判能力的策略；辅以分阶段课程迁移学习框架进行环境适应性训练。仿真实验与消融研究的对比结果验证：所提算法能在多种类型的复杂随机化月面仿真地形中成功实现高适应性、高稳定性的跳跃运动；且完整算法是唯一能够成功完成全部 3 类跳跃任务的组别，证明了其在增强机器人环境适应能力与决策能力方面的有效性。

## 致谢

**经费资助**：本工作由中国科学院战略性先导科技专项（No. XDA30010500）及空间应用工程与技术中心重点实验室基金（No. CXJJ-22S021）资助。

**作者贡献**：H.S.：概念提出、方法论、数据采集与分析、初稿撰写；S.W.：指导、项目管理、经费获取、审阅与编辑；Y.Y.：数据分析与稿件起草修订；J.L.：数据分析与稿件起草修订。

**利益冲突**：作者声明无利益冲突。

**数据可用性**：支持本研究发现的部分或全部数据可向通讯作者合理索取。

## 参考文献（保留原文）

1. Qiao L, Xu L, Head JW, Chen J, Zhang Y, Li B, Ling Z. Geological evidence for extensive basin ejecta as plains terrains in the Moon's South Polar Region. *Nat Commun.* 2024;15:Article 5783.
2. Li Z, Zeng X, Wang S. Hopping trajectory planning for asteroid surface exploration accounting for terrain roughness. *Trans Japan Soc Aeronaut Space Sci.* 2021;64(4):205–214.
3. Wei G, Li X, Zhang W, Tian Y, Jiang S, Wang C, Ma J. Illumination conditions near the Moon's south pole: Implication for a concept design of China's Chang'E-7 lunar polar exploration. *Acta Astronaut.* 2023;208:74–81.
4. Qi J, Gao H, Su H, Han L, Su B, Huo M, Yu H, Deng Z. Reinforcement learning-based stable jump control method for asteroid-exploration quadruped robots. *Aerosp Sci Technol.* 2023;142:Article 108689.
5. Jiang J, Zeng X, Guzzetti D, You Y. Path planning for asteroid hopping rovers with pre-trained deep reinforcement learning architectures. *Acta Astron.* 2020;171:265–279.
6. Li Z, Peng X, Abbeel P, Levine S, Berseth G, Sreenath K. Robust and versatile bipedal jumping control through reinforcement learning. In: *Robotics: Science and Systems XIX.* Daegu (Republic of Korea): Robotics: Science and Systems Foundation, 2023.
7. Rudin N, Kolvenbach H, Tsounis V, Hutter M. Cat-like jumping and landing of legged robots in low-gravity using deep reinforcement learning. *arXiv.* 2021. https://doi.org/10.48550/arXiv.2106.09357
8. Luo B. Balance control based on six-dimensional spatial mechanics and velocity adjustment through region intervention and foot landing for quadruped robot. *Robotica.* 2022;40(8):2855–2877.
9. Luo B, Luo Y. A balanced jumping control algorithm for quadruped robots. *Robot Auton Syst.* 2022;158(6):Article 104278.
10. Shi J, Bai C, He H, Han L, Wang D, Zhao B, Zhao M, Li X, Li X. Robust quadrupedal locomotion via risk-averse policy learning. *arXiv.* 2023. https://doi.org/10.48550/arXiv.2308.09405
11. Ma J, Wu F, Chen Y, Ji X, Ding Y. Effective multimodal reinforcement learning with modality alignment and importance enhancement. *arXiv.* 2023. https://doi.org/10.48550/arXiv.2302.09318
12. Sang H, Wang S. Motion planning of space robot obstacle avoidance based on DDPG algorithm. In: *2022 International Conference on Service Robotics (ICoSR).* Chengdu (China): IEEE; 2022. p. 175–181.
13. Ji M, Zhang L, Wang S. A path planning approach based on Q-learning for robot arm. In: *2019 3rd International Conference on Robotics and Automation Sciences.* Wuhan (China): IEEE; 2019. p. 15–19.
14. Zhu L, Ma J, Wang S. Deep neural networks based realtime optimal control for lunar landing. In: *3rd International Conference on Aeronautical Materials and Aerospace Engineering.* Shanghai (China): IOP Publishing; 2019. p. 7.
15. Qi J, Gao H, Yu H, Huo M, Feng W, Deng Z. Integrated attitude and landing control for quadruped robots in asteroid landing mission scenarios using reinforcement learning. *Acta Astronaut.* 2023;204:599–610.
16. Yu R, Wang Q, Wang Y, Wang Z, Wu J, Zhu Q. Walking with terrain reconstruction: Learning to traverse risky sparse footholds. *arXiv.* 2024. https://doi.org/10.48550/arXiv.2409.15692
17. Gangapurwala S, Geisert M, Orsolino R, Fallon M, Havoutis I. RLOC: Terrain-aware legged locomotion using reinforcement learning and optimal control. *IEEE Trans Robot.* 2022;38:2908–2927.
18. Kovalev V, Shkromada A, Ouerdane H, Osinenko P. Combining model-predictive control and predictive reinforcement learning for stable quadrupedal robot locomotion. *arXiv.* 2023. https://doi.org/10.48550/arXiv.2307.07752
19. Han X, Zhao M. Learning quadrupedal high-speed running on uneven terrain. *Biomimetics.* 2024;9:37.
20. Bellegarda G, Nguyen C, Nguyen Q. Robust quadruped jumping via deep reinforcement learning. *Robot Auton Syst.* 2024;182:Article 104799.
21. Sang H, Wang S. Lunar leap robot: 3M architecture–enhanced deep reinforcement learning method for quadruped robot jumping in low-gravity environment. *J Aerosp Eng.* 2024;37(6):04024076.
22. Driess D, Xia F, Sajjadi MSM, Lynch C, Chowdhery A, Ichter B, Wahid A, Tompson J, Vuong Q, Yu T, et al. PaLM-E: An embodied multimodal language model. In: *Proceedings of the 40th International Conference on Machine Learning.* Vol. 202. ICML'23. Honolulu (Hawaii): JMLR.org; 2023. p. 8469–8488.
23. Du Y, Watkins O, Wang Z, Abbeel P, Gupta A, Andreas J. Guiding pretraining in reinforcement learning with large language models. In: *Proceedings of the 40th International Conference on Machine Learning.* Vol. 202. ICML'23. Honolulu (Hawaii): JMLR.org; 2023. p. 8657–8677.
24. Singh S, Katti S, Ghatnekar V. Memory based reinforcement learning with transformers for long horizon timescales. In: Samsonovich AV, Liu T, editors. *Biologically inspired cognitive architectures 2023.* Cham: Springer Nature Switzerland; 2024. p. 845–852.
25. Wang Z, Cai S, Chen G, Abbeel P, Gupta A, Andreas J. Describe, Explain, Plan and select: Interactive planning with large language models enables open-world multi-task agents. In: *Proceedings of the 37th International Conference on Neural Information Processing Systems.* NIPS'23. Red Hook (NY): Curran Associates Inc.; 2024. p. 34153–34189.
26. Chen C, Wu YF, Yoon J, Ahn S. TransDreamer: Reinforcement learning with Transformer world models. *arXiv.* 2202. https://doi.org/10.48550/arXiv.2202.09481
27. Micheli V, Alonso E, Fleuret F. Transformers are sample-efficient world models. *arXiv.* 2023. https://doi.org/10.48550/arXiv.2209.00588
28. Wen M, Kuba JG, Lin R, Zhang W, Wen Y, Wang J, Yang Y. Multi-agent reinforcement learning is a sequence modeling problem. In: *Proceedings of the 36th International Conference on Neural Information Processing Systems.* NIPS'22. Red Hook (NY): Curran Associates Inc., 2024. p. 16509–16521.
29. Yang R, Zhang M, Hansen N, Xu H, Wang X. Learning vision-guided quadrupedal locomotion end-to-end with cross-modal transformers. *arXiv.* 2022. https://doi.org/10.48550/arXiv.2107.03996
30. Chen L, Lu K, Rajeswaran A, Lee K, Grover A, Laskin M, Abbeel P, Srinivas A, Mordatch I. Decision Transformer: Reinforcement learning via sequence modeling. In: *Proceedings of the 35th International Conference on Neural Information Processing Systems.* NIPS'21. Red Hook (NY): Curran Associates Inc.; 2024. p. 15084–15097.
31. Janner M, Li Q, Levine S. Offline reinforcement learning as one big sequence modeling problem. In: *Proceedings of the 35th International Conference on Neural Information Processing Systems.* NIPS'21. Red Hook (NY): Curran Associates Inc.; 2024. p. 1273–1286.
32. Hu K, Zheng RC, Gao Y, Xu H. Decision Transformer under Random Frame Dropping. *arXiv.* 2023. https://doi.org/10.48550/arXiv.2303.03391
33. Mao H, Zhao R, Chen H, Hao J, Chen Y, Li D, Zhang J, Xiao Z. TransformerinTransformer as backbone for deep reinforcement learning. *arXiv.* 2023. https://doi.org/10.48550/arXiv.2212.14538
34. Robine J, Höftmann M, Uelwer T, Harmeling S. Transformer-based world models are happy with 100k interactions. *arXiv.* 2023. https://doi.org/10.48550/arXiv.2303.07109
35. Banino A, Badia AP, Walker J, Scholtes T, Mitrovic J, Blundell C. CoBERL: Contrastive BERT for Reinforcement Learning. *arXiv.* 2022. https://doi.org/10.48550/arXiv.2107.05431
36. Devlin J, Chang MW, Lee K, Toutanova K. BERT: Pre-Training of Deep Bidirectional Transformers for Language Understanding. In: Burstein J, Doran C, Solorio T, editors. *Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers).* Minneapolis (MN): Association for Computational Linguistics; 2019. p. 4171–4186.
37. Parisotto E, Song HF, Rae JW, Pascanu R, Gulcehre C, Jayakumar SM, Jaderberg M, Kaufman RL, Clark A, Noury S, et al. Stabilizing transformers for reinforcement learning. In: *Proceedings of the 37th International Conference on Machine Learning.* Vol. 119. ICML'20. Brookline (MA): JMLR.org; 2020. p. 7487–7498.
38. Davis JQ, Gu A, Choromanski K, Dao T, Re C, Finn C, Liang P. Catformer: Designing stable transformers via sensitivity analysis. In: *Proceedings of the 38th International Conference on Machine Learning.* Brookline (MA): PMLR, 2021. p. 2489–2499.
39. Dai Z, Yang Z, Yang Y, Carbonell J, Le Q, Salakhutdinov R. Transformer-XL: Attentive language models beyond a fixed-length context. In: Korhonen A, Traum D, Màrquez L, editors. *Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics.* Florence (Italy): Association for Computational Linguistics; 2019. p. 2978–2988.
40. Narvekar S, Peng B, Leonetti M, Sinapov J, Taylor ME, Stone P. Curriculum learning for reinforcement learning domains: A framework and survey. *J Mach Learn Res.* 2020;21:7382–7431.
41. Kong Y, Liu L, Wang J, Tao D. Adaptive curriculum learning. In: *Proceedings of the IEEE/CVF International Conference on Computer Vision.* Montreal (Canada): IEEE; 2021. p. 5067–5076.
42. Ryu K, Liao Q, Li Z, Sreenath K, Mehr N. CurricuLLM: Automatic task curricula design for learning complex robot skills using large language models. *arXiv.* 2024. https://doi.org/10.48550/arXiv.2409.18382
43. Radhakrishnan A, Ruiz Luyten M, Prasad N, Uhler C. Transfer learning with kernel methods. *Nature Comm.* 2023;14(1):5570.
