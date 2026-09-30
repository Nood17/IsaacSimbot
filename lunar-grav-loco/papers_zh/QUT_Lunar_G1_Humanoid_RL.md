---
原文标题: Training Humanoid Robots to Walk in Lunar Gravity Using Reinforcement Learning
中文译名: 使用强化学习训练人形机器人在月球重力下行走
来源: Klein, Benjamin & Roberts, Jonathan (2025). Proceedings – Australasian Conference on Robotics and Automation (ACRA 2025), Australian Robotics and Automation Association (ARAA). QUT ePrints: https://eprints.qut.edu.au/262116/
翻译日期: 2026-09-30
---

# 使用强化学习训练人形机器人在月球重力下行走

**Benjamin Klein & Jonathan Roberts**

昆士兰科技大学（Queensland University of Technology）工程学院，澳大利亚昆士兰州布里斯班
& 澳大利亚协作机器人中心（Australian Cobotics Centre）

Benklein83@yahoo.com.au

> 原文版权说明：本文为作者投稿/录用版本（author's version），收录于 ACRA 2025 会议论文集。版权事宜请咨询作者；除非文档以知识共享（Creative Commons）许可发布，否则仅限个人使用。

## 摘要

人形机器人是月球探测的有力候选者，但如何让运动能力适应降低的重力仍是一个挑战。本文研究使用强化学习（reinforcement learning, RL），借助 NVIDIA Isaac Sim 5.0 和 Unitree RL Lab，训练宇树 Unitree G1 人形机器人在模拟月球重力下行走。我们开发了三个策略（policy）：一个地球基线策略、一个由地球策略微调（fine-tuned）得到的月球模型，以及一个从零开始训练的月球模型（lunar-from-scratch）。结果表明，月球策略自主发现了步态适应行为，包括缩短步幅、以脚尖为主的行走方式（toe-dominant walking）以及质心（centre of mass, CoM）前移，与此前关于低重力的分析研究一致。微调被证明更为高效：在不到一半的训练时间内取得了与从零训练相当的性能。这些发现表明，强化学习可以有效地使人形机器人的运动能力适应地外环境，并凸显了微调作为行星机器人任务实用策略的价值。

【图 1：月球栖息地舱段中的人形机器人示意图，用于引出论文的应用背景——人形机器人在月面栖息地中执行任务的愿景。】

## 1 引言

人形机器人因其适应能力和类人形态，将在未来的月球与太空探索中发挥关键作用。本文所报道的工作旨在利用先进的仿真软件结合强化学习，研究在月球重力下开发和改进人形机器人高级运动模型的困难。

太空产业对人形机器人潜力的认识已有二十多年，主要源于其拟人化设计（anthropomorphic design）（Stoica et al., 2005）。这种认识体现在公共与私营部门的高额投资中。例如，NASA 正在积极开发 Valkyrie 机器人，使其能在人造环境中作业并执行危险的舱外任务，以支持未来的地外航天活动（Radford et al., 2015）。类似地，SpaceX 也已投入其 Optimus 项目（于 2022 年 AI Day 发布），其既定目标是最终让机器人协助在火星上建立殖民地（Tesla, 2022）。

这种类人形态的核心优势是双重的。第一，它们灵巧的类人手部使其能够操作已为宇航员设计好的工具与设备。这一能力至关重要，因为它免去了运送重型专用机器人设备的需要，大幅降低了任务载荷与后勤负担。第二，其双足结构使其能够穿越多样的地形——从太空栖息地中按人体尺寸设计的踏板通道、脚手架与梯子（Stoica et al., 2005），到复杂、非结构化的行星表面。这些综合能力使其成为执行准备性任务的理想选择——例如在宇航员抵达之前组装栖息地或进入狭小空间（Omer et al., 2011）。

在本工作中，我们使用 NVIDIA Isaac Sim 5.0 和 Unitree RL Lab，研究如何应用强化学习使人形机器人的运动能力适应月球重力。我们在三种条件下训练了 Unitree G1 人形机器人模型：(i) 在地球重力下训练的基线策略；(ii) 从地球基线微调而来的月球策略；(iii) 从零开始训练的月球策略。这些实验旨在评估重力如何影响行走步态、质心位置与控制精度，同时比较迁移学习（transfer learning）相对于从零训练的效率。结果为现代强化学习方法如何支持人形机器人在低重力环境中的部署提供了新的见解。

本文的贡献如下：

- 首次展示了基于强化学习的人形机器人运动控制——在模拟月球重力下使用 Unitree G1 模型。
- 对地球基线、月球微调和月球从零训练三种策略进行了对比研究，揭示了各自独特的步态适应。
- 实证证据表明：微调可将训练时间减少一半以上，同时达到同等性能。
- 使用现代高保真仿真器验证了此前关于低重力行走行为的分析性见解。
- 将人形机器人运动的强化学习研究扩展到地外环境，为未来的行星探索奠定基础。

## 2 背景

### 2.1 行走的"编排"（The Choreography of Walking）

双足行走是一种身体在单腿支撑（single-leg support）与双腿支撑（double support）之间交替的运动形式，需要平衡、前进动量与地面反作用力（ground reaction forces）之间持续不断的相互作用。重力在行走中的主要作用是允许钟摆式能量交换（pendular energy exchange）：当质心（COM）下降时，重力势能转化为动能，从而减少维持运动所需的肌肉外部功，同时也使每一步步态能产生摩擦力并保持稳定（Cavagna et al., 2000）。因此，重力也显著影响人形机器人的运动能力，许多研究分析了在不同重力条件下的行走步态与速度（Omer et al., 2011, 2014）。

在月球（地球重力的 1/6）或火星（地球重力的 1/3）等低重力环境中，更低的重力要求以更慢的行走速度来维持平衡；或者，必须切换到跑步步态才能获得必要的动态稳定性（dynamic stability）（Omer et al., 2011）。

【图 2：月球上人形机器人的早期仿真（Omer et al., 2014），展示了此前在简化仿真中研究月面双足行走的工作。】

例如，Omer et al. (2014) 的仿真表明，月球上的人形机器人需要将其行走速度较地球降低约 60%，以避免倾倒，或者采用类似跑步的跳跃式运动（hopping motion）（Omer et al., 2011）。此外，步态周期中髋部高度与加速度的变化说明：降低的重力会减弱向下的力，从而影响摩擦力的产生与前向推进（Omer et al., 2014）。

【图 3：最大稳定速度与重力的关系曲线（Omer et al., 2011）。图中显示重力越低，可保持稳定行走的最大速度越低，说明需要针对特定重力环境调整现代先进控制系统与步态策略，以确保在地外表面上有效运动。】

重力对最大稳定行走速度的总体影响见图 3，这凸显了使现代先进控制系统和步态策略适应特定重力环境的必要性，以确保在地外表面上的有效运动。

### 2.2 通过仿真训练人形机器人

鉴于人形机器人拥有大量自由度（degrees-of-freedom, DoF），以及在真实机器人上开发鲁棒关节控制与行走步态的困难，利用仿真来解决人形机器人行走问题是一个传统做法。Kee et al. (2004) 为 GuRoo 人形机器人提出了一种两阶段、受生物启发的控制方案：首先用遗传算法（Genetic Algorithm）调节局部 PI 反馈控制器以最小化误差与振动；然后由受小脑启发的神经网络（CMAC）提供前馈补偿（feed-forward compensation），从轨迹误差中在线学习。包括下蹲动作在内的实验展示了将进化式调参与自适应神经控制相结合的好处。

MuJoCo 物理引擎（Multi-Joint dynamics with Contact）由 Todorov et al. (2012) 提出，为机器人与生物力学系统中的连续、接触密集（contact-rich）动力学仿真提供了一个快速而准确的平台。与面向图形的引擎不同，MuJoCo 从一开始就被设计为支持基于模型的控制（model-based control）与强化学习研究，重点关注效率、可微性（differentiability）与稳定的接触处理。

自 2012 年发布以来，MuJoCo 已成为开发与基准测试强化学习算法的标准仿真环境。它支撑了广泛使用的环境，如 OpenAI Gym 的 Humanoid、Ant 和 HalfCheetah 任务，以及 DeepMind Control Suite（Tassa et al., 2018）。这些基准对推动连续控制（continuous control）的进展起到了重要作用。2021 年，MuJoCo 被 DeepMind 收购并开源发布（DeepMind, 2021），大大扩展了其对机器人与 AI 研究社区的可及性。

### 2.3 利用前沿技术

#### NVIDIA Isaac Sim 5.0

NVIDIA Isaac Sim 5.0 是一个高保真机器人仿真平台，强调精确的物理、可扩展性与开源适应性。其底层使用 PhysX 引擎，并支持物理对象与环境资产的通用场景描述（Universal Scene Description, USD）模式，能够实现具有真实刚体动力学、多关节铰接（multi-joint articulation）、传感器（相机、LiDAR、接触）仿真以及摩擦模型、速度/力矩限制和可变形体（beta 版）等高级特性的仿真（NVIDIA Corporation, 2025d）。由于 Isaac Sim 的大部分代码库（包括 Isaac Sim 专属扩展）已在 Apache 2.0 许可下开源，用户可以对其进行适配、扩展或集成到定制的机器人或仿真工作流中（Isaac Sim Development Team, 2025）。

【图 4：NVIDIA Isaac Sim 5.0 系统需求（NVIDIA Corporation, 2025b），列出了运行该仿真器所需的硬件配置。】

然而，也存在一些权衡。首先，硬件性能要求很高：用户需要具备 NVIDIA 指定的计算配置（图 4），并且只能使用 NVIDIA 显卡（NVIDIA Corporation, 2025b）。其次，作为一个相对较新的发布版本，其安装复杂，文档与生态支持有限，部分组件不够成熟或示例/教程较少，且不断有已知问题被发现（NVIDIA Corporation, 2025c）。这可能使使用该仿真器变得困难，需要解决尚未在网上讨论过的新问题。总体而言，Isaac Sim 5.0 在物理精确、可扩展的机器人仿真方面迈出了强有力的一步，尤其适合能够满足硬件要求并愿意与不断演进的文档和 API 打交道的用户。本项目选择该仿真器，是因为它是目前可用的最逼真、最先进的开源软件，并且与 Isaac Lab（一个 Isaac Sim 的强化学习扩展，允许用户使用强化学习训练机器人完成新任务）无缝集成。

#### NVIDIA Isaac Lab

NVIDIA Isaac Lab 是一个开源的、统一的模块化机器人学习框架，旨在简化机器人研究中的常见工作流，如强化学习、模仿学习（imitation learning）与运动规划，构建于 NVIDIA Isaac Sim 之上。它旨在通过 PhysX 的 GPU 加速物理仿真与基于 RTX 的渲染来缩小仿真到现实（sim-to-real）差距并加速机器人策略的开发，实现大规模并行环境执行，同时结合了精确的传感器仿真、域随机化（domain randomisation）以及对多种机器人形态（机械臂、四足机器人、人形机器人等）的支持。它提供了大量开箱即用的示例环境、任务、传感器与工具，使用来自领先机器人公司（如 Unitree、Boston Dynamics、Franka Emika 和 Universal Robots）的精细机器人模型，同时具备定制或构建新内容的能力，强调模块化与可扩展性。该框架支持本地或云端运行，可在多种机器人配置上扩展实验（NVIDIA Corporation, 2025a）。Isaac Lab 利用跨多环境并行计算的能力、对 Unitree G1 等工业机器人的支持、其环境的模块化，再加上大量现成的示例，使其成为本项目的理想选择。这些特性通过抽象化建模、仿真与强化学习组件，加快了软件的学习速度并降低了整体代码复杂度。

表 1 给出了 MuJoCo 及相关仿真器中近期人形机器人运动强化学习方法的比较。

**表 1：MuJoCo 及相关仿真器中近期人形机器人运动强化学习方法比较**

| 论文 | 机器人/环境 | 方法 | 关键贡献 | 与月球步态研究的相关性 |
|---|---|---|---|---|
| Singh et al. (2022) 《Learning Bipedal Walking on Planned Footsteps》 | MuJoCo 人形机器人（HRP5P、JVRC-1） | 课程学习（curriculum learning）+ 落足点规划器的强化学习 | 借助落足点条件化实现包括转弯、楼梯、不平地形在内的鲁棒运动 | 展示课程学习 + 任务塑形（task shaping）如何提升泛化能力，与不平整月面相关 |
| Seo et al. (2025) 《FastTD3》 | MuJoCo 人形机器人基准 | FastTD3（改进的 TD3 变体） | 通过大批量、并行仿真、分布式评论网络（distributional critic）加速 RL 训练 | 展示效率如何翻倍——与本文"微调 vs 从零训练"的发现相呼应 |
| Sferrazza et al. (2024) 《HumanoidBench》 | MuJoCo Unitree H1（带手） | RL 基准（PPO、SAC 等） | 仿真中运动+操作的广泛基准 | 提供社区基线；本文将低重力运动作为新挑战加入 |
| **本工作 (2025)《月球重力下的 Unitree G1》** | Isaac Sim + Unitree G1 | 强化学习（通过 Unitree RL Lab 的 PPO） | 首次在低重力下研究人形 RL 运动；微调使训练时间减半 | 将 RL 人形机器人工作扩展到地外环境——新颖的域迁移 |

#### Unitree Robotics（宇树科技）

Unitree G1（图 5）是宇树科技开发的全尺寸人形机器人。它高约 127 cm，重 35 kg，具有 23 个自由度，包括带驱动的手臂、腿和躯干。G1 专为运动、操作与人机交互的通用研究而设计。它由高扭矩执行器（actuator）驱动，集成了用于平衡与运动控制的传感，并可依靠机载电池无线缆运行。其拟人化设计、紧凑的外形以及对科研机构的可获得性，使其成为开发和评估人形控制策略的实用平台。

【图 5：Unitree G1 人形机器人实物照片。】

宇树表示致力于通过开源资源促进创新，最著名的是 Unitree RL Lab——一个基于 IsaacLab 构建的综合仓库，为 G1 等机器人提供强化学习环境。这一开源项目使研究者和开发者能够训练、仿真和部署策略，加速了机器人自主性与智能的进步（Unitree Robotics, 2024）。G1 的可获得性与开源软件工具使这一生态成为我们工作的理想选择。

#### 人形机器人基础模型（Foundation Humanoid Robot Models）

人形机器人基础模型（如 NVIDIA Isaac GR00T）是大型预训练人工智能系统，旨在跨一系列人形机器人形态与任务提供通用的推理、感知与控制能力。它们通过使机器人能够理解高级指令（通常包含语言与视觉）、进行规划、适应新环境并执行连续控制策略（continuous control policies），而无需为每个新任务或新身体从零训练，从而加速机器人研究与部署（NVIDIA Corporation, 2025a,b）。此类模型的例子包括 NVIDIA 的 Isaac GR00T N1 / N1.5，支持多模态输入并可针对不同形态与任务进行微调。这些模型在大型多样化数据集上训练，数据集包含真实机器人演示、合成轨迹（在仿真中生成）、互联网规模视频，以及将观测、动作甚至语言或高级描述配对的多模态数据（Liu et al., 2024）。其训练机制通常先在宽泛的通用任务/环境上预训练，然后针对特定形态或任务微调（NVIDIA Corporation, 2025b）。

基础模型面临的最大挑战包括：机器人相关数据（尤其是带真实物理与安全标注的数据）的稀缺、跨不同机器人形态与环境泛化的困难、在真实世界部署中确保安全可靠的行为、处理不确定性，以及实现实时性能（Liu et al., 2024; NVIDIA Corporation, 2025a）。总体而言，人形基础模型代表了通向通用型机器人系统的关键一步，但其成功将取决于能否克服数据、安全与部署方面的挑战。

#### 强化学习策略（Reinforcement Learning Policy）

强化学习（RL）通过试错过程训练机器人：机器人根据任务表现获得奖励（reward）或惩罚（penalty），从而学习最优动作。这种方法在动态环境中表现出色，使机器人无需显式编程即可改进其行为（Chen et al., 2020）。例如，RL 已被用于通过优化步态模式来增强人形机器人的行走稳定性。Chen et al. (2020) 描述了一项使用 RL 训练机器人在真实世界条件下适应其步长与时序的研究，提高了其穿越不平地形和从外部扰动（如推搡或打滑）中恢复的能力（Kober et al., 2013）。尽管 RL 策略很有效，但仍面临挑战，包括高昂的计算成本、难以泛化到训练任务之外，以及在不可预测的环境中确保安全鲁棒的性能。

RL 与基础模型都能增强人形机器人的能力，但面临不同的挑战。RL 局限于特定任务范围，而基础模型则受限于人类演示数据的数量与多样性（Chen et al., 2020; Gu et al., 2025）。当前研究旨在通过结合二者来解决这些问题：在物理仿真器中生成的合成数据集正被用于增强训练，减少对真实世界数据的依赖（Gu et al., 2025）。

### 2.4 研究空白（Knowledge Gap）

先前的研究已通过简化仿真模型探索了月球重力下的人形机器人运动（Omer et al., 2011; Stoica et al., 2005），但这些方法尚未使用现代人形机器人平台或当代强化学习方法复现。早期工作严重依赖分析式控制系统与数学模型来使电机指令适应不同重力（Omer et al., 2014），而当前的人形机器人（如 Unitree G1）运行的是将演示数据与强化学习相结合的学习型策略（learned policies）（Unitree Robotics, 2024）。将这些基于基础模型的控制器（如 NVIDIA 的 GR00T，NVIDIA Corporation, 2025a）适配到低重力环境，仍是一个开放问题，也是该领域当前的关键挑战之一（Gu et al., 2025）。高保真物理引擎的最新进展（如具有 GPU 加速并行计算的 NVIDIA Isaac Sim 5.0，NVIDIA Corporation, 2024; NVIDIA Corporation, 2025d）现已允许更逼真地训练人形机器人策略。本文通过将强化学习应用于使 Unitree G1 的行走策略适应月球重力来填补这一空白，在现代仿真环境中考察步态适应与迁移学习的效率。

## 3 训练月球 Unitree G1 人形机器人策略

### 3.1 搭建 Isaac Sim 5.0 环境

**在 Conda 环境中安装 Isaac Sim / Isaac Lab**：按照 Unitree RL Lab 的要求，使用 pip 在 Conda 环境中安装了 Isaac Lab。安装验证完成后安装 Unitree RL Lab。随后从 HuggingFace 克隆了所需的 Unitree USD 模型文件并链接到模型目录。通过列出可用环境并运行一个示例训练任务来确认安装，表明 Unitree RL Lab 与 Isaac Lab 之间的集成工作正常（Unitree Robotics, 2025; NVIDIA Corporation, 2025a）。

【图 6：自定义分析配置视图。图中显示仿真界面侧视视角：机器人头顶的绿色箭头表示当前速度指令（velocity command），相机从侧方跟踪机器人以便进行步态对比分析。】

### 3.2 修改 Unitree RL Lab 示例

Unitree RL Lab 提供了一个名为 "Unitree-G1-29dof-Velocity" 的训练任务，用于训练 G1 人形机器人在平地上行走。该任务提供了预配置的仿真器场景、动作、奖励、观测、课程（curriculum）、指令与事件，使 G1 能通过强化学习从零学习行走。对于地球对照策略，除相机外没有修改任何配置。相机被配置为在训练过程中录制视频，对准机器人使其每段画面都在镜头内。录制通常配置为每 5000 个全局步长（global steps）进行一次，而地球对照策略则配置为每 50000 个全局步长一次。为使机器人在月球重力下训练，通过仿真环境配置设置了仿真重力。强化学习配置的核心部分保持与 Unitree RL Lab 一致，不做更改。

为了在模型之间进行公平且有意义的比较，我们创建了一个自定义配置：让机器人沿一个方向线性增加速度，同时如图 6 所示从侧面观察机器人。这需要配置相机跟踪机器人（将相机原点改为机器人的惯性系），并强制机器人朝一个方向行走——需要修改 "reset root state uniform"（重置根状态均匀分布）事件，以确保机器人每次都朝同一方向复位。为确保机器人以逐渐增大的速度沿直线行走（由图 6 中机器人头顶的绿色箭头表示），我们移除了原有训练课程，并创建了新课程：在每个训练回合（episode）结束时将速度指令增加 20%。这一自定义配置能够生成一致的视频，使模型之间的比较更快、更容易、更准确。

### 3.3 训练

使用强化学习共训练了三个策略：第一个是对照组，训练 G1 在地球重力下行走；第二个在月球重力下训练，但从地球策略继续训练（即微调）；最后一个从一开始就（从零开始）在月球重力下训练。地球策略用于验证 Unitree RL 库——确保机器人确实能学会行走、建立性能基线，并给出训练其余策略所需时间的大致估计。第二个策略对地球策略进行微调使其能在月球重力下行走，旨在研究微调地球基策略的性能与有效性，同时代表一种现实场景：机器人已经拥有成熟的地球策略，希望在月球上使用它。最后一个策略从一开始就（从零开始）在月球重力下训练，研究训练一个月球重力策略所需时间，以便与微调现有模型所需时间进行比较。除了研究月球重力行走策略对步态与速度的影响之外，以这种方式训练三个策略还能让我们了解：对于机器人可能工作的任何重力水平，到底是微调策略更好，还是从零开始更好。

所有训练都使用相同的 Unitree RL Lab 任务完成，仅在会话之间改变重力，并且只有当平均速度误差（velocity error）和因姿态不良（bad orientation）导致的终止次数的平均值收敛时才结束训练。图 7 展示了这些指标在整个微调运行过程中的变化，显示它们如何收敛，标志着训练的结束。

【图 7：微调策略的速度误差与"姿态不良终止"指标的收敛曲线。两条曲线随训练迭代逐渐下降并收敛，表示训练完成。】

【图 8：微调策略训练过程中速度指令逐步增加的曲线。每当机器人平均能以 80% 以上的时间跟踪其指令速度时，指令速度区间就随之扩大。】

【图 9：跟踪速度指令的奖励项（reward term）曲线，收敛于 0.8，表示机器人在 80% 的时间内能跟踪所请求的速度。】

每个策略均使用 4096 个机器人并行训练，回合长度为 20 秒，并配合一系列课程：随着机器人学会更好地行走而逐渐提高速度。课程在一组允许的 (x, y) 速度范围内给出一个指令速度，该速度基于机器人在上一回合中行走的距离——即机器人行走距离越短，课程请求的速度越慢。该范围由设定限值界定，可为正或负。如图 8 所示，当机器人平均能够在超过 80% 的时间内跟踪其请求速度时（如图 9 中收敛于 0.8 的曲线所示），所请求的速度范围就会扩大。这种课程组合使机器人能学到一个可应对所有速度（直至最大值）以及任意方向的策略。

## 4 结果

### 4.1 重力对行走步态的影响

【图 10：地球与月球重力下训练策略的行走步态对比（三个子图：(a) 地球策略，(b) 微调策略，(c) 直接月球策略）。图中红色线段位于每只脚上的相同位置，用于标示步幅长度；绿线标示机器人质心位置。月球训练的模型表现出更短的步幅、前移的质心，以及相比地球基线更依赖脚尖触地，与此前关于低重力运动的分析一致。】

重力显著改变了 G1 的行走步态。对比图 10 中的图像：红线位于每只脚上的相同位置以标示步幅长度，绿线表示机器人质心所在位置。观察地球训练的策略：较宽的红线间距表明步幅较长，质心大致位于两条红线中点稍靠前的位置。两个月球策略的步幅相比地球策略都短得多，且质心大幅前移，现在大约与前脚的脚尖对齐。这与以往研究相符：随着重力降低，为实现快速稳定的行走，必须控制腿部产生的竖直向心力（centripetal force），因此出现了奇特的"踮脚尖"步态与极小的大腿运动幅度——这一切都是为了尽量减小腿部运动引起的向心力，从而形成以更短步幅、脚尖着地的行走方式。月球上质心比地球上更靠前，这表明由于月球重力加速度小于地球，要达到与地球相同的前向加速度矢量，质心必须更大幅地前倾到身体旋转中心之前。使用带精细机器人模型的现代仿真所得到的这些结果，确认了此前研究（如 Omer et al., 2011, 2014）的结论，并证明了这种适应对于高自由度人形机器人是可能实现的。

### 4.2 速度误差（Velocity Error）

速度误差是期望速度与机器人实际速度之间误差的均值，可用于评估模型的控制精度。对比图 11 中的曲线：两个月球策略的误差大约为 0.4，比地球策略的速度误差高 0.1。由于所有策略都训练至收敛，且使用相同的强化学习任务配置，误差差异只能归因于重力的降低。然而，重力降低似乎也有助于机器人学习行走而不摔倒。观察地球策略训练的曲线，速度误差在收敛前随迭代稳步上升；而月球策略的误差则直接迅速上升。这可能表明月球上的机器人不会那么快摔倒，从而使它们能更快地学会如何支撑自身重量。

【图 11：三个子图 (a) 地球速度误差、(b) 微调速度误差、(c) 月球速度误差，展示微调策略与月球从零训练策略所产生的行走步态/速度误差收敛过程。两者对低重力表现出相似的适应，但微调策略以显著更少的训练时间达到同等的步态稳定性，体现了迁移学习的效率。】

### 4.3 训练时间

**表 2：训练时间**

| 策略 | 地球 | 微调 | 月球（从零） |
|---|---|---|---|
| 迭代次数（Iteration） | 9,100 | 4,300 | 12,300 |
| 时间（小时） | 14.5 | 7 | 20 |

将两个月球策略的训练时间与其结果进行比较可以发现：如果要让一个基于地球环境的人形控制策略适应新环境，微调比从零训练一个新策略更有效。从表 2 的训练时间看，微调只用了 7 小时就达到了与从零训练 20 小时所得策略相当的能力。对比图 10 中的行走步态，两个月球策略的步态看起来几乎完全相同。两个策略的表现也相近——如图 11 所示，两者的速度误差都开始收敛于 0.4 左右。当手头已有一个在地球重力下训练好的人形机器人策略时，将其微调到月球重力要比再次从零训练更快，同时能提供相同水平的性能。

## 5 讨论

本研究的结果凸显了使用强化学习使人形机器人运动策略适应低重力环境时面临的挑战与机遇。训练揭示了地球与月球重力下步态特征的明显差异，与此前基于仿真的低重力运动分析（Omer et al., 2011；Omer et al., 2014）一致。具体而言，月球训练的策略表现出缩短的步幅、以脚尖为主的行走方式以及更靠前移的质心。这些调整表明，强化学习能够自主识别在低重力下维持稳定所需的补偿策略，而无需人为设计的步态规则。

一个关键发现是：与从零训练相比，对地球训练策略进行微调非常高效。微调模型在不到一半的训练时间内达到了与月球从零训练模型相当的性能，支持了"基线策略中蕴含的先验知识可以加速跨环境适应"这一观点。这一见解对未来的行星机器人任务具有直接意义——在这类任务中，计算资源可能受限，而快速的策略适应至关重要。

与此同时，对速度误差的分析表明，月球重力下训练的策略尚未达到地球训练策略的控制精度。尽管实现了收敛，但月球条件下的残余误差仍然更高，说明奖励函数设计与课程塑形（curriculum shaping）将是重要的改进方向。诸如对步态不稳定加权惩罚或尝试替代奖励结构等调整，可能会产生误差更低、运动更高效的策略。

这些发现还引发了关于在地外栖息地部署人形机器人的更广泛的考量。虽然在平坦的仿真地形上行走证明了可行性，但真实月面具有不平整的月壤（regolith）、尘土和低摩擦条件。将训练扩展到包含这类环境复杂性，对于确保鲁棒性必不可少。此外，将强化学习与人形机器人基础模型相结合，可能提供可泛化的运动策略，使其能更无缝地跨重力水平与地形迁移。

总体而言，本研究表明，高保真物理仿真器中的强化学习不仅能复现早期关于低重力运动的分析性见解，还能生成实用的、针对特定机器人的行走策略。通过验证微调既比从零训练更快又同样有效，本工作为行星探索场景中可扩展的人形机器人适应方法奠定了基础。

尽管结果令人鼓舞，本研究仍存在若干局限。第一，所有实验均使用物理引擎在仿真中进行；仿真到现实（sim-to-real）差距仍是一大挑战，将月球训练的策略迁移到物理硬件上很可能会暴露未建模的动力学因素，如执行器非线性、延迟与柔性（compliance）。第二，训练环境假设平坦地形与稳定接触，而月壤不平整、多尘且摩擦更低。第三，只考虑了前向行走；转弯、攀爬或从扰动中恢复等其他步态未做处理。最后，计算成本不低——每次训练运行需要多天的 GPU 算力，这可能限制其在资源受限的任务场景中的可扩展性。解决这些局限是从概念验证走向可部署系统的关键。

## 6 结论

本文提出了一种强化学习方法，以 Unitree G1 为案例研究，训练人形机器人在模拟月球重力下行走。结果表明，在低重力下训练的策略会自主调整步态策略，包括更短的步幅与改变的质心位置，既呼应了先前的分析研究，也揭示了机器人特有的补偿方式。事实证明，对地球训练模型进行微调非常有效，在不到一半的时间内达到了与月球从零训练相当的性能，凸显了迁移学习在跨环境适应中的价值。

这些发现为太空探索中人形机器人这一日益壮大的研究领域做出了贡献，表明可以为地外环境开发可扩展、可适应的运动策略。

总之，本工作的关键贡献为：

- 证明了强化学习能够自主地使人形机器人运动策略适应月球重力，产生的步态策略与先前的理论预测一致。
- 表明通过微调进行迁移学习能在保持性能的同时大幅减少训练时间，为行星机器人任务提供了一条实用途径。
- 将人形机器人运动的强化学习研究扩展到地球基准之外的地外语境，为太空探索中的可扩展部署建立了基础。

### 6.1 未来工作

进一步的研究方向包括：调整强化学习奖励、大幅增加训练时间，以及理解如何利用策略生成合成的机器人演示数据。通过操纵奖励权重，有可能发现更多新颖的行走步态，或许能产生全新的运动风格。延长训练时间直至所有指标充分覆盖，也有助于这些发现。使用新颖行走步态策略生成合成数据，可以让 NVIDIA Isaac GR00T（NVIDIA Corporation, 2025b）这类基础模型获得在任何重力下更有效移动的能力。这些领域的进一步工作可能带来新的洞见，最终让 Unitree G1 能够以其独特却高效的方式，在月球上、在月球栖息地中行走。

## 参考文献（保留原文）

Cavagna, G. A., Willems, P. A., and Heglund, N. C. (2000). The role of gravity in human walking: pendular energy exchange, external work and optimal speed. The Journal of Physiology, 528(3):657–668.

Chen, P., Wang, Y., Luo, C., Cai, W., and Zhao, M. (2020). Hifar: Multi-stage curriculum learning for high-dynamics humanoid fall recovery. Engineering Applications of Artificial Intelligence. Forthcoming or preprint.

DeepMind (2021). Mujoco is now free and open source. https://deepmind.com/blog/article/mujoco. Accessed: 2025-09-21.

Gu, Z., Li, J., Shen, W., Yu, W., Xie, Z., McCrory, S., Cheng, X., Shamsah, A., Griffin, R., Liu, C. K., Kheddar, A., Peng, X. B., Zhu, Y., Shi, G., Nguyen, Q., Cheng, G., Gao, H., and Zhao, Y. (2025). Humanoid locomotion and manipulation: Current progress and challenges in control, planning, and learning.

Isaac Sim Development Team (2025). Isaac sim on github. https://github.com/isaac-sim/IsaacSim. Accessed 2025.

Kee, D., Wyeth, G., and Roberts, J. (2004). Biologically inspired joint control for a humanoid robot. In 4th IEEE/RAS International Conference on Humanoid Robots, 2004., volume 1, pages 385–401 Vol. 1.

Kober, J., Bagnell, J. A., and Peters, J. (2013). Reinforcement learning in robotics: A survey. The International Journal of Robotics Research, 32(11):1238–1274.

Liu, S., Wu, L., Tan, H., Chen, H., Zhu, J., et al. (2024). Rdt-1b: a diffusion foundation model for bimanual manipulation. arXiv preprint arXiv:2410.07864.

NVIDIA Corporation (2024). Nvidia isaac sim. Accessed: 2025-04-09. Specific version updates may alter the year.

NVIDIA Corporation (2025a). Isaac gr00t n1: An open foundation model for humanoid robots. arXiv preprint arXiv:2503.14734.

NVIDIA Corporation (2025b). Isaac gr00t n1.5 github repository.

NVIDIA Corporation (2025a). Isaac lab: Unified framework for robot learning. Technical documentation. Isaac Sim Documentation – Includes APIs, environments, GPU-accelerated simulation, domain randomisation, and robot models from companies such as Unitree, Boston Dynamics, and Franka Emika.

NVIDIA Corporation (2025b). Isaac sim requirements — isaac sim documentation. https://docs.isaacsim.omniverse.nvidia.com/5.0.0/installation/requirements.html. Accessed 2025.

NVIDIA Corporation (2025c). Known issues — isaac sim documentation. https://docs.robotsfan.com/isaacsim/5.0.0/overview/known_issues.html. Accessed 2025.

NVIDIA Corporation (2025d). Physics — isaac sim documentation. https://docs.isaacsim.omniverse.nvidia.com/latest/physics/index.html. Accessed 2025.

Omer, A., Hashimoto, K., ok Lim, H., and Takanishi, A. (2011). Initial study of bipedal robot locomotion approach on different gravity levels. In International Symposium on Artificial Intelligence, Robotics and Automation in Space (i-SAIRAS).

Omer, A., Hashimoto, K., ok Lim, H., and Takanishi, A. (2014). Study of bipedal robot walking motion in low gravity: Investigation and analysis. International Journal of Advanced Robotic Systems, 11:139.

Radford, N. A., Strawser, P., Hambuchen, K., Mehling, J. S., Verdeyen, W. K., Donnan, A. S., Holley, J., Sanchez, J., Nguyen, V., Bridgwater, L., Berka, R., Ambrose, R., Diftler, M., Bluethmann, W., Paine, N., Kuehn, J., Beeson, P., Ballard, B., Davis, D., Tyree, K., Kim, S.-H., Lim, B., Gaddis, B., Ames, A., Faber, J., Strawser, P., Aldridge, H., Askew, R. S., Burridge, R. R., Bluethmann, W., Lovchik, C., Magruder, D., and Rehnmark, F. (2015). Valkyrie: Nasa's first bipedal humanoid robot. Journal of Field Robotics, 32:397–419.

Seo, Y., Li, S., Lee, K., Abbeel, P., and Ba, J. (2025). Fasttd3: Simple, fast, and capable reinforcement learning for humanoid control. arXiv preprint arXiv:2505.22642.

Sferrazza, C., Wang, Y., Krishnan, S., Shi, Y., and Fazeli, N. (2024). Humanoidbench: Simulated humanoid benchmark for whole-body locomotion. arXiv preprint arXiv:2403.10506.

Singh, R. P., Benallegue, M., Morisawa, M., Cisneros, R., and Kanehiro, F. (2022). Learning bipedal walking on planned footsteps for humanoid robots. arXiv preprint arXiv:2207.12644.

Stoica, A., Keymeulen, D., Csaszar, A., Gan, Q., Hidalgo, T., Moore, J., Newton, J., Sandoval, S., and Xu, J. (2005). Humanoids for lunar and planetary surface operations. In 5th IEEE-RAS International Conference on Humanoid Robots, pages 1–6.

Tassa, Y., Doron, Y., Muldal, A., Erez, T., Li, Y., Casarini, F., Kumar, S., King, M., Kohli, P., Lefrancq, A., Lillicrap, T., Galashov, A., and Silver, D. (2018). Deepmind control suite. arXiv preprint arXiv:1801.00690.

Tesla (2022). Tesla ai day 2022. YouTube.

Todorov, E., Erez, T., and Tassa, Y. (2012). Mujoco: A physics engine for model-based control. In 2012 IEEE/RSJ International Conference on Intelligent Robots and Systems, pages 5026–5033. IEEE.

Unitree Robotics (2024). Unitree rl lab. Accessed: 2025-09-19.

Unitree Robotics (2025). Unitree rl lab: Reinforcement learning implementation for unitree robots, based on isaaclab. Accessed 20 September 2025.



