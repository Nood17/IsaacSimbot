# NaVILA：用于导航的腿式机器人视觉-语言-动作模型

> **原文标题**：NaVILA: Legged Robot Vision-Language-Action Model for Navigation
> **中文译名**：NaVILA：用于导航的腿式机器人视觉-语言-动作模型
> **来源**：RSS 2025；arXiv:2412.04453v2 [cs.RO]（2025 年 2 月 17 日）
> **项目主页**：https://navila-bot.github.io
> **翻译日期**：2026-09-30

**作者**：An-Chieh Cheng¹\*，Yandong Ji¹\*，Zhaojing Yang²\*，Zaitian Gongye¹，Xueyan Zou¹，Jan Kautz³，Erdem Bıyık²，Hongxu Yin³†，Sifei Liu³†，Xiaolong Wang¹ᐧ³†

¹ UC San Diego　² USC　³ NVIDIA
（\* 同等贡献，按字母排序；† 同等指导）

---

**【图 1：NaVILA 的真实世界演示。接收到人类指令后，NaVILA 使用视觉-语言模型处理 RGB 视频帧，并调用运动技能在机器人上执行任务。机器人能够成功处理长时程导航任务，并在具有挑战性的环境中安全运行。图中展示了四种场景——Workspace（工作区）、Home（家庭）、Outdoor（户外）——及对应的自然语言指令示例，如"立即左转，直行，踩上垫子，继续前进，在非常靠近垃圾桶时停下"；"向前移动并走出办公区，然后右转，停在蓝色垃圾桶附近"；"向前走，看到楼梯栏杆时右转，绕楼梯走到走廊，沿走廊右转，停在浴室门前"；"沿路向前走，在黄色消防栓处左转，沿斜坡前进并停在门前"。】**

## 摘要

本文提出用腿式机器人解决视觉-语言导航（Vision-and-Language Navigation，VLN）问题，这不仅为人类指挥机器人提供了灵活的方式，也使机器人能够穿越更具挑战性、更杂乱的场景。然而，将人类语言一路转换为低层腿部关节动作并非易事。我们提出 NaVILA——一个两层框架，将视觉-语言-动作模型（Vision-Language-Action model，VLA）与运动技能（locomotion skills）统一起来。NaVILA 并非让 VLA 直接预测低层动作，而是首先以语言形式生成带有空间信息的中层动作（mid-level action），例如"向前移动 75 厘米"，再将该语言指令作为视觉运动强化学习（RL）策略的输入加以执行。NaVILA 在已有基准上大幅超越了先前方法。同样的优势也体现在我们基于 IsaacLab 新开发的基准上——该基准具有更真实的场景、低层控制和真实机器人实验。

## I. 引言

视觉-语言导航（VLN）能力已成为现代机器人系统的基础组成部分：机器人需要在不提供地图的情况下，依照语言指令在未见过的环境中导航 [1–6]。这不仅提供了更好的人机交互接口，还通过语言增强了跨场景泛化能力。本文进一步将 VLN 研究扩展到腿式机器人（如四足或人形机器人）。用腿代替轮子使机器人能够在更具挑战性、更杂乱的场景中导航。如图 1 中的示例所示，我们的机器人可以穿行于过道狭窄的杂乱实验室，在住宅中从一个房间进入另一个房间，还能应对户外具有挑战性的环境，如布满小石块、坑洞和沟槽的不平整地形。

要将语言转化为动作，机器人需要对输入语言进行推理，执行闭环规划以及低层控制。随着大语言模型（LLM）和视觉-语言模型（VLM）的最新进展，若干端到端视觉-语言-动作（VLA）系统被开发出来 [7–9]。这些系统使用大规模机器人操作示教数据对通用 VLM 进行微调，以输出低层动作。在单一模型中统一推理与执行虽然很有吸引力且取得了令人鼓舞的结果，但值得深入思考一个问题：**在量化的低层指令之外，是否存在更好的动作表示方式？** 毕竟，LLM 和 VLM 主要是用自然语言训练的。当我们需要把推理结果转换为精确的非语言动作时，统一推理与执行就变得十分困难。

受 VLM 在空间位置与距离推理方面最新进展 [10, 11] 的启发，我们提出 NaVILA——一个用于腿式机器人 VLN 的两层框架：对 VLM 进行微调，使其以语言形式输出中层动作（VLA），如"右转 30 度"；再训练一个低层视觉运动策略来跟随该指令执行。VLA 输出的中层动作只传达位置与方向信息，而不包含低层指令。该框架的优势有三方面：

1. 将低层执行与 VLA 解耦后，同一个 VLA 只需更换低层策略即可应用于不同机器人；
2. 以中层语言指令表示动作，使 VLA 训练可以使用多样化的数据源，包括真实人类视频和推理问答（QA）任务。这增强了推理能力而不会使输出过拟合到特定低层指令，并能利用真实世界数据实现泛化；
3. NaVILA 在两个不同时间尺度上运行：VLA（通常是计算密集的大模型）以较低频率运行，提供高层导航指令；而运动策略实时运行。这种双频率方式使运动策略能够处理复杂的避障并提升整体鲁棒性。

在训练 VLA 方面，我们展示了如何：(i) 在现有 VLM 框架内整合 VLN 中的历史上下文与当前观测；(ii) 设计专为 VLN 任务定制的导航提示词（prompt）；(iii) 利用来自 YouTube 人类游览视频的真实数据提升连续环境中的导航能力；(iv) 引入精心配比的数据集混合方案以增强 VLN 泛化性。这些策略使我们能够将通用的基于图像的 VLM 微调成面向导航的智能体，同时继续在通用视觉-语言数据集上训练它，从而保持其广泛的泛化能力。此外，这也是首个表明直接在人类视频上训练可提升连续环境导航能力的工作。

为训练鲁棒的运动技能，我们采用单阶段方法学习基于视觉的运动策略。我们从原始 LiDAR 点云构建高度图（height map），并引入随机化以弥合仿真到现实（sim-to-real）差距。该控制器接收 VLA 模型的输出，将其转换为指令速度，并通过控制关节位置来跟踪这些速度。这种端到端方法能够训练出既鲁棒又安全的视觉运动技能，便于在真实世界的挑战性环境中部署（如强阳光下或接近某些透明表面时）。

实验表明，我们的 VLA 在经典 VLN 基准上显著超越现有最优方法，成功率提升超过 17%。此外，我们的单阶段运动策略大幅超越先前基于策略蒸馏（policy distillation）的方法。为更好地模拟 VLN 中运动导航的挑战，我们使用 Isaac Sim 引入了新基准 VLN-CE-Isaac。该基准考虑了细致的机器人关节运动及与环境的交互，这是以往 VLN 工作未曾涉及的。在 VLN-CE-Isaac 实验中，我们的视觉策略以显著优势超越盲视（blind）策略，成功率提升 14%。我们还展示了该 VLA 可跨不同机器人部署（Unitree Go2、Unitree H1、Booster T1），各自使用不同的运动技能。最后，我们在真实世界中部署 NaVILA，展现出令人印象深刻的鲁棒性：在 25 条指令上取得 88% 的成功率，其中包括在多样场景下复杂指令 75% 的成功率。

## II. 方法

NaVILA 将高层视觉语言理解与低层运动控制相结合（图 2）。它使用 VLM 处理单视角图像并生成自然语言形式的路点指令，再由运动策略将其转换为精确的关节运动，实现对机器人的实时控制。VLM 的推理能力与运动策略的执行能力之间的协同，使 NaVILA 能够泛化到多样化环境。我们首先在第 II-A 节介绍如何将 VLM 驯化用于高层 VLN，然后在第 II-B 节概述机器人配置与运动策略。

**【图 2：NaVILA 是一个结合高层视觉语言理解与低层运动控制的两层框架。我们的 VLA 模型处理单视角图像，以自然语言生成中层动作，再由先进的低层运动策略将其转换为精确的关节运动。图中结构为：输入包括"指令（Instruction）"、"历史视角（History Views）"、"当前视角（Current View）"和高度图（Height Map）；VLA 输出中层动作（如"向前移动 75 cm"）；运动策略 π 接收速度指令（Velocity Commands）、先前动作（Prior Actions）、关节位置与速度（Joint Pos. & Vel.）、朝向（Orientation）、角速度（Angular Velocity）等本体感知（Proprioception）信息，输出关节位置（Joint Positions）。这种集成实现了跨不同真实环境的强泛化与适应性，并可实时操控机器人。】**

### A. 驯化 VLM 用于视觉语言导航

VLN 需要将视频输入作为观测进行处理。在 VLM 中处理视频输入的常见方法是通过视频编码器 [12]。然而，VLM 的最新进展在很大程度上是由图像-文本数据的可用性推动的。虽然有工作尝试将这种成功扩展到视频编码器，但缺乏大规模、高质量的视频-文本数据集限制了它们的预训练。为应对这一挑战，我们在方法中选择基于图像的视觉-语言模型。这些模型表现出更强的泛化能力并拥有更广的知识，更适合应对 VLN 中的泛化挑战。具体而言，我们基于 VILA [13–19] 构建方法——VILA 是一族兼顾理解与生成的高效 VLM。VILA 的预训练已被证明对多图推理特别有效，因而尤其适合需要理解序列图像间关系的 VLN 任务。

**VILA 预备知识。** VILA 由三个主要组件构成：视觉编码器、投影器（projector）和 LLM。视觉编码器处理输入图像，将其转换为视觉 token 序列。这些 token 随后被下采样并通过 MLP 投影器映射到语言域。之后，投影得到的 token 与文本 token 一起送入 LLM 进行自回归生成。处理视频时，VILA 按固定间隔均匀采样帧，并将所有帧信息置于文本之前。一个典型的视频描述提示词形如"⟨frame3⟩⟨frame6⟩⟨frame9⟩...Tell me about this video."（⟨第3帧⟩⟨第6帧⟩⟨第9帧⟩……告诉我这个视频的内容）。值得注意的是，借助序列并行训练 [16]，VILA 最多可包含 1024 帧。VILA 经历三阶段训练过程：首先用对齐数据 [20] 在冻结的 LLM 与视觉骨干之间预训练连接器；然后用文本-图像交错语料 [21, 22] 同时预训练连接器与 LLM；最后用指令微调数据 [20, 23] 微调所有模块（视觉编码器、连接器、LLM）。

**导航提示词。** 在视觉语言导航任务中，不同时间步的图像承担两种不同职能。时间步 t 的图像代表当前观测，这对 VLN 智能体做出即时决策至关重要（如在路口右转或在到达目标时停下）。另一方面，时间步 t 之前的帧是历史帧，充当记忆库，帮助智能体追踪整体进度（如记住起始位置、推理已访问过的地点并规划下一步）。像 VILA 那样按固定间隔均匀采样帧并不理想，因为它没有区分这两种表示类型。因此，我们首先提取最近的第 t 帧作为当前观测，然后从前面的 t−1 帧中均匀采样，并确保第一帧始终被包含。此外，由于当前观测与历史观测承担不同角色，我们在任务提示词中用文本线索区分它们，如对记忆帧使用 "a video of historical observations:"（一段历史观测视频），对最新帧使用 "current observation:"（当前观测）。与 [12] 不同，我们避免引入可能使 LLM 学习过程复杂化的额外特殊 token；相反，我们遵循将 LLM 的输入与输出都保持在语言域的设计原则，以充分利用预训练 LLM 的推理能力。通过将历史与当前观测的这些 token 与导航指令结合，我们构建了导航任务提示词，如图 2 所示。

**【图 3：VLA 框架概览。紫色块表示从历史帧采样的记忆 token，红色块表示当前观测 token，🔥 表示可训练参数。历史视角（History Views）经视觉编码器、下采样与投影器后得到 196×t 个 token；当前视角（Current View）产生 196 个 token；连同导航提示词（"Imagine you are a robot programmed for navigation tasks. You have been given a video of historical observations: ... and current observation: ... Your assigned task is: ... Analyze this series of images to decide your next move, which could involve turning left or right by a specific degree, moving forward a certain distance, or stop if the task is completed."——想象你是一个为导航任务编程的机器人。你已获得一段历史观测视频……和当前观测……你的任务是……分析这一系列图像以决定下一步动作，可以是向左/右转特定角度、向前移动特定距离，或在任务完成时停下）一并送入 LLM，输出"下一步动作是：转 θ 度 / 前进 d cm / 停止"。实验中测试了 t 取 8 至 64 帧的配置。】**

**从人类视频中学习。** 近期研究 [24–26] 表明，从人类视频中采集"轨迹-指令"对可以增强导航能力。然而，先前工作局限于离散导航设定，且主要将真实视频用于预训练以减小域差距或改善地标理解，而非直接用于训练导航模型。将该思路扩展到连续设定存在重大挑战，因为连续动作标签难以获取。最近在野外度量位姿估计（metric-pose estimation）方面的进展使这成为可能，使我们能够从人类视频中提取空间理解并直接训练导航模型。

如图 4 所示，我们的数据管线从 YouTube 上的 2K 个第一人称（egocentric）游览视频开始，它们提供了丰富的真实世界数据，用于从人类行为中学习机器人导航。我们通过基于熵的采样 [26] 将这些视频处理成 20K 条多样且有代表性的轨迹。接着，我们使用 MASt3R [27] 估计相机位姿以提取逐步动作，并使用基于 VLM [13] 的 captioning 加 LLM [28] 改写为每条轨迹生成自然语言指令。该方法使我们能够利用人类演示进行连续导航，这在以前是难以实现的。

**【图 4：将野外人类游览视频转换为连续环境中成对导航数据的数据管线。流程为：YouTube 视频 → 基于熵的轨迹采样（Entropy-based Trajectory Sampling）→ 度量位姿估计（MASt3R）→ 逐步动作（Step-wise Actions，如"右转 30 度"）；同时 VLM 与 LLM 生成指令（Instructions，如"沿走廊走并进入餐厅"）。我们首先通过基于熵的采样 [26] 将视频处理为有意义的轨迹，然后通过度量相机位姿估计 [27] 提取逐步动作，并利用 VLM [13] 和 LLM [28] 生成指令。】**

**监督微调（SFT）数据配比。** 有效的监督微调（Supervised Fine-tuning，SFT）数据对开发鲁棒的视觉-语言动作模型至关重要。模型应当专精于具身任务，同时避免对特定动作过拟合；它还应当很好地泛化到真实场景，同时保留广泛的世界知识。得益于 NaVILA 模块化框架出色的可扩展性与适应性，将多样数据源整合进我们的管线十分直接。这种灵活性使我们能够增强导航的泛化性。我们的 SFT 数据配比从四个角度设计：(1) 来自真实视频的导航数据；(2) 来自仿真的导航数据；(3) 辅助导航数据；(4) 通用 VQA 数据集。

对于仿真导航数据，连续环境中可用的 VLN 数据集有限，仅有 R2R-CE [29] 和 RxR-CE [30] 提供了由离散 VLN 版本转换而来的稀疏路径点。我们在 Habitat 仿真器中利用这两个数据集，用最短路径跟随器沿测地最短路径生成动作序列。这产生了逐步导航视频，其中每个样本包含一段 (t+1) 帧的视频和时间步 t 对应的专家动作。为鼓励 LLM 生成距离和角度的连续值标签，我们合并连续动作（如将两个"前进 25 cm"合并为一个"前进 50 cm"），最多合并三个连续动作。这一合并过程不仅缩减了数据集规模以提高处理效率，还引入了更丰富的动作多样性，缓解过拟合。此外，针对标签不平衡——尤其是"停止"动作占比不足——我们采用再平衡（rebalancing）技术使分布更均匀。所有导航专用数据都经过前述帧提取策略处理，并与导航任务提示词配对。

为进一步改善场景理解并弥补 R2R-CE 和 RxR-CE 中指令的不足，我们加入了辅助导航数据集。沿用 [12]，我们使用 EnvDrop [31] 的增广指令，并引入一个"导航轨迹总结"辅助任务：给定一段轨迹视频，保留第一帧并均匀采样历史帧，以标注指令作为标签，让 LLM 根据这些帧描述机器人的轨迹。为进一步增强空间场景理解，我们整合了 ScanQA [32] 数据集——它包含真实世界 3D 扫描的 QA 对，问题经人工编辑、答案自由组织且基于 3D 物体。训练时我们使用来自原始扫描的多视角 RGB 图像支持该任务。

最后，为保持模型的通用能力，我们加入了通用 VQA 数据集 [23, 33, 34]。这一综合数据集设计确保 NaVILA 能有效泛化到新场景与真实环境。

**训练与推理范式。** 训练从 VILA 的第二阶段模型开始，该模型已完成视觉语言语料预训练。随后我们应用 SFT 数据配比，按标准做法对整个 VLM 训练一个 epoch。训练期间，视觉编码器、连接器、LLM 三个组件全部解冻。推理阶段，我们实现了一个正则表达式解析器 [35]，从 LLM 输出中提取动作类型（如"前进"或"左转"）及其对应参数（如具体距离或角度）。该方法在仿真环境与真实实验中均被证明有效：我们经验性地发现所有实验中的全部动作都能被成功匹配与映射。

### B. 视觉运动策略

本节首先简要介绍本工作使用的实验平台 Go2 机器狗，然后描述端到端视觉控制策略的开发——该策略解释来自 VLM 的高层语言导航指令并将其转换为精确的关节运动。控制策略在 Isaac Sim 仿真器中使用 Isaac Lab [36] 训练，然后直接部署到真实机器人。

**Go2 机器人。** 如图 5 所示，机器人在其头部底座处装有一个 LiDAR 传感器，以 15 Hz 的频率广播点云。机器人具有 18 个自由度（DoF）：机身 6 个 DoF，四条腿各 3 个 DoF。在策略训练过程中，机身的 6 个 DoF 不受约束，策略仅控制腿上的 12 个关节电机。

**解释高层指令。** 按我们的表述，VLM 输出一组固定的动作词汇，如 {前进、左转、右转、停止}，我们将这些指令映射为固定的指令速度 {$0.5\ \mathrm{m\,s^{-1}}$、$\frac{\pi}{6}\ \mathrm{rad\,s^{-1}}$、$-\frac{\pi}{6}\ \mathrm{rad\,s^{-1}}$、$0$}，并按对应的持续时长执行，以与具体的 VLM 数值对齐。

**低层动作与观测空间。** 控制策略的动作空间 $\mathbf{a}$ 定义为期望关节位置 $\mathbf{q}^d \in \mathbb{R}^{12}$，通过刚度与阻尼转换为仿真中的力矩输入。我们采用 PPO 算法 [37] 训练策略。训练时，评论家（critic）观测特权环境信息并生成价值函数以更新行动者（actor），而行动者只接收真实世界中可用的传感器数据。评论家的观测空间 $\mathbf{o}_c$ 包含当前时间步 $t$ 的本体感知与速度指令，以及机器人周围的特权地形高度扫描。本体感知数据包括机器人线速度与角速度、朝向、关节位置、关节速度和上一个动作。在行动者的观测空间 $\mathbf{o}_a$ 中，线速度被排除（真实世界无法获取），改为用本体感知数据的历史来隐式推断该信息。机器人通过 LiDAR 传感器生成的高度图感知周围地形。

**从 LiDAR 点云构建高度图。** 鉴于 LiDAR 在探测透明物体方面的卓越能力以及在强阳光下的鲁棒表现，我们选择厂商提供的 LiDAR 作为感知机器人周围环境和保证安全导航的主传感器。Unitree L1 生成视场角达 $360^\circ \times 90^\circ 的点云，我们基于补充材料中列出的参数从中创建 2.5D 高度图。对每个体素格，选取范围内的最低值，然后对最近 5 帧 LiDAR 点云施加最大滤波以平滑得到的高度图。

**【图 5：从点云重建高度图。(a) 仿真：Go2 机器人在仿真中跟随速度指令并避障；红点显示从传感器中心向地形网格射线投射的 LiDAR 点；右图显示预处理后、数值按传感器约束裁剪的高度图，颜色越深表示高度越高。(b) 在玻璃附近的安全运动：俯视高度图能检测到深度与 RGB 图像无法发现的玻璃表面。】**

**训练。** 不同于多数采用两阶段"教师-学生"训练范式的现有工作 [38–41]，我们以单阶段方式训练运动策略。与两阶段训练相比，单阶段 RL 更省时，因为它不需要策略蒸馏。此外，策略直接与环境交互，可以探索并有可能发现新策略。借助 Isaac Lab 中的射线投射（ray-casting）支持，我们的视觉 RL 策略训练在单块 RTX 4090 GPU 上达到超过 6 万 FPS 的高吞吐。

## III. 实验

我们通过实验回答以下问题：
(1) 我们的 VLA 在 VLN-CE 基准和通用空间场景理解任务上的性能与现有最优方法相比如何？（第 III-A 节）
(2) 我们的单阶段视觉运动策略与基于策略蒸馏的方法相比表现如何？（第 III-B 节）
(3) 如何在仿真器中评估运动导航，NaVILA 在这些场景中有多有效和灵活？（第 III-C 节）
(4) NaVILA 管线能否成功部署到真实机器人 VLN 实验中？（第 III-D 节）

### A. 高层 VLA 性能

**VLN-CE 基准。** 我们在 VLN-CE 基准上评估 VLA——该基准在重建的逼真室内场景中为导航动作的执行提供连续环境。我们聚焦于 R2R（Room-to-Room）与 RxR（Room-across-Room）两个数据集的 val-unseen 划分，因为它们是 VLN 中最受认可的两个基准。我们采用 VLN 任务广泛使用的评估指标：导航误差（Navigation Error，NE）、Oracle 成功率（OS）、成功率（SR）、按成功率加权的路径长度（SPL）和归一化动态时间规整（nDTW）。表 I 给出了结果：NaVILA 用单一模型在两个基准上均显著超越所有不依赖仿真器预训练路点预测器的基线。值得注意的是，这也是首次有只使用单视角 RGB 输入训练的 VLN 智能体取得与使用全景视图、里程计或仿真器预训练路点预测器的模型相当或更优的结果。这表明 NaVILA 的强泛化能力能有效弥补 RGB 单视角或传感器观测的局限。

**表 I：在 R2R-CE [29] 与 RxR-CE [30] 的 Val-Unseen 划分上与现有最优方法的比较。** ∗ 表示使用 Hong 等人 [42] 的路点预测器的方法。NaVILA 超越了所有不依赖仿真器预训练路点预测器的方法，即使那些方法使用了深度、全景视图和里程计等额外输入。

| 方法 | S.RGB | Pano. | Depth | Odo. | NE↓ | OS↑ | SR↑ | SPL↑ | RxR NE↓ | RxR SR↑ | RxR SPL↑ | RxR nDTW↑ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HPN+DN∗ [43] | | ✓ | ✓ | ✓ | 6.31 | 40.0 | 36.0 | 34.0 | - | - | - | - |
| CMA∗ [42] | | ✓ | ✓ | ✓ | 6.20 | 52.0 | 41.0 | 36.0 | 8.76 | 26.5 | 22.1 | 47.0 |
| VLN⟳BERT∗ [42] | | ✓ | ✓ | ✓ | 5.74 | 53.0 | 44.0 | 39.0 | 8.98 | 27.0 | 22.6 | 46.7 |
| Sim2Sim∗ [44] | | ✓ | ✓ | ✓ | 6.07 | 52.0 | 43.0 | 36.0 | - | - | - | - |
| GridMM∗ [45] | | ✓ | ✓ | ✓ | 5.11 | 61.0 | 49.0 | 41.0 | - | - | - | - |
| Ego2-Map∗ [46] | | ✓ | ✓ | ✓ | 5.54 | 56.0 | 47.0 | 41.0 | - | - | - | - |
| DreamWalker∗ [47] | | ✓ | ✓ | ✓ | 5.53 | 59.0 | 49.0 | 44.0 | - | - | - | - |
| Reborn∗ [48] | | ✓ | ✓ | ✓ | 5.40 | 57.0 | 50.0 | 46.0 | 5.98 | 48.6 | 42.0 | 63.3 |
| ETPNav∗ [49] | | ✓ | ✓ | ✓ | 4.71 | 65.0 | 57.0 | 49.0 | 5.64 | 54.7 | 44.8 | 61.9 |
| HNR∗ [50] | | ✓ | ✓ | ✓ | 4.42 | 67.0 | 61.0 | 51.0 | 5.50 | 56.3 | 46.7 | 63.5 |
| BEVBert∗ [51] | | ✓ | ✓ | ✓ | 4.57 | 67.0 | 59.0 | 50.0 | 4.00 | 68.5 | - | 69.6 |
| HAMT+ScaleVLN∗ [52] | | ✓ | ✓ | ✓ | 4.80 | - | 55.0 | 51.0 | - | - | - | - |
| AG-CMTP [53] | | ✓ | ✓ | ✓ | 7.90 | 39.0 | 23.0 | 19.0 | - | - | - | - |
| R2R-CMTP [53] | | ✓ | ✓ | ✓ | 7.90 | 38.0 | 26.0 | 22.0 | - | - | - | - |
| LAW [54] | ✓ | | ✓ | ✓ | 6.83 | 44.0 | 35.0 | 31.0 | 10.90 | 8.0 | 8.0 | 38.0 |
| CM2 [55] | ✓ | | ✓ | ✓ | 7.02 | 41.0 | 34.0 | 27.0 | - | - | - | - |
| WS-MGMap [56] | ✓ | | ✓ | ✓ | 6.28 | 47.0 | 38.0 | 34.0 | - | - | - | - |
| AO-Planner [57] | | ✓ | ✓ | | 5.55 | 59.0 | 47.0 | 33.0 | 7.06 | 43.3 | 30.5 | 50.1 |
| Seq2Seq [58] | ✓ | | ✓ | | 7.77 | 37.0 | 25.0 | 22.0 | 12.10 | 13.9 | 11.9 | 30.8 |
| CMA [58] | ✓ | | ✓ | | 7.37 | 40.0 | 32.0 | 30.0 | - | - | - | - |
| RGB-Seq2Seq [58] | ✓ | | | | 10.10 | 8.0 | 0.0 | 0.0 | - | - | - | - |
| RGB-CMA [58] | ✓ | | | | 9.55 | 10.0 | 5.0 | 4.0 | - | - | - | - |
| NaVid [12] | ✓ | | | | 5.47 | 49.0 | 37.0 | 35.0 | - | - | - | - |
| **NaVILA** | ✓ | | | | **5.22** | **62.5** | **54.0** | **49.0** | **6.77** | **49.3** | **44.0** | **58.8** |

（注：S.RGB=单视角 RGB；Pano.=全景；Depth=深度；Odo.=里程计。左侧四列为 R2R Val-Unseen 指标。）

为评估跨数据集性能，我们沿用 [12] 的做法：仅用 R2R 样本训练 NaVILA，不使用 RxR 训练集，然后评估其在 RxR Val-Unseen 划分上的零样本（zero-shot）性能。如表 II 所示，我们的方法显著超越当前最优模型 NaVid，SR 大幅提升 10%。

**表 II：RxR-CE [30] Val-Unseen 划分上的跨数据集性能。** 所有结果均未在 RxR-CE 训练集上训练。NaVILA 显著超越当前单视角最优方法 NaVid [12]。

| 方法 | S.RGB | Depth | Odo. | NE↓ | OS↑ | SR↑ | SPL↑ |
|---|---|---|---|---|---|---|---|
| LAW [54] | ✓ | ✓ | ✓ | 10.87 | 21.0 | 8.0 | 8.0 |
| CM2 [55] | ✓ | ✓ | ✓ | 8.98 | 25.3 | 14.4 | 9.2 |
| WS-MGMap [56] | ✓ | ✓ | ✓ | 9.83 | 29.8 | 15.0 | 12.1 |
| Seq2Seq [58] | ✓ | ✓ | | 11.8 | 5.02 | 3.51 | 3.43 |
| CMA [58] | ✓ | ✓ | | 11.7 | 10.7 | 4.41 | 2.47 |
| RGB-Seq2Seq [12] | ✓ | | | 11.2 | 12.2 | 0.0 | 0.0 |
| RGB-CMA [12] | ✓ | | | 9.55 | 14.8 | 0.0 | 0.0 |
| A2 NAV [59] | ✓ | | | - | - | 16.8 | 6.3 |
| NaVid [12] | ✓ | | | 8.41 | 34.5 | 23.8 | 21.2 |
| **NaVILA** | ✓ | | | **8.78** | **46.8** | **34.3** | **28.2** |

**空间场景理解基准。** 作为通用导航智能体，鲁棒的空间场景理解（如物体定位、指代理解和空间推理）至关重要。为评估 NaVILA 的场景理解能力，我们在 ScanQA Validation 基准——一个广泛使用的 3D 问答数据集——上进行评估。ScanQA 基于真实世界扫描，我们使用这些扫描的多视角图像作为输入来查询 NaVILA。如表 III 所示，NaVILA 以显著优势超越先前最优模型 NaviLLM [60]（CIDEr 分数高出 20 分）。此外，使用 64 帧时，NaVILA 的表现优于最先进的基于 3D 的大型多模态模型 [61, 62]。这一点尤其值得关注，因为那些模型需要 3D 扫描或带相机位姿的 RGBD 数据作为输入，而我们的方法以更少的观测取得了更好的结果。

**表 III：ScanQA 数据集 [32] Validation 划分上的空间场景理解性能评估。** NaVILA 超越当前最优 VLA 模型，并优于需要深度或相机位姿等额外输入的 3D LMM。∗ 表示需要在 ScanQA 数据集上进行任务特定微调的 3D LMM。

| 方法 | Bleu-4↑ | Rouge↑ | Cider↑ | Meteor↑ | EM↑ |
|---|---|---|---|---|---|
| *任务专用模型* | | | | | |
| VoteNet+MCAN [63] | 6.2 | 29.8 | 54.7 | 11.4 | 17.3 |
| ScanRefer+MCAN [63] | 7.9 | 30.0 | 55.4 | 11.5 | 18.6 |
| ScanQA [32] | 10.1 | 33.3 | 64.9 | 13.1 | 21.0 |
| 3D-VisTA [64] | 10.4 | 35.7 | 69.6 | 13.9 | 22.4 |
| *3D 大型多模态模型* | | | | | |
| 3D-LLM (flamingo)∗ [65] | 7.2 | 32.3 | 59.2 | 12.2 | 20.4 |
| 3D-LLM (BLIP2-flant5)∗ [65] | 12.0 | 35.7 | 69.4 | 14.5 | 20.5 |
| LL3DA∗ [66] | 13.5 | 37.3 | 76.8 | 15.9 | - |
| Chat-3Dv2∗ [67] | 14.0 | - | 87.6 | - | - |
| Scene-LLM∗ [61] | 12.0 | 40.0 | 80.0 | 16.6 | 27.2 |
| LEO [62] | 13.2 | 49.2 | 101.4 | 20.0 | 24.5 |
| *2D 视觉-语言-动作模型* | | | | | |
| NaviLLM [60] | 12.0 | 38.4 | 75.9 | 15.4 | 23.0 |
| NaVILA（8 帧） | 14.8 | 46.4 | 95.1 | 18.7 | 27.0 |
| NaVILA（64 帧） | **16.9** | **49.3** | **102.7** | **20.1** | **28.6** |

### B. 低层 RL 策略性能

为凸显我们的 RL 策略相对于基于策略蒸馏方法的优势，我们将其与正则化在线自适应（Regularized Online Adaptation，ROA）[68] 进行比较。在 ROA 训练中，模型先学习一个特权编码器处理高度扫描点及其他特权观测，再由该特权编码器监督一个自适应编码器——后者以与我们的低层策略相同的 2.5D 高度图为输入。我们用三个指标评估两种方法：线速度误差、角速度误差和碰撞率。前两个指标评估策略跟踪速度指令的精度，第三个衡量模型的避障能力。如表 V 所示，我们的低层策略在全部三个指标上优于 ROA，尤其是碰撞率显著更低，证明了我们训练方法的有效性。

**表 V：低层策略性能。**

| 方法 | 线速度误差↓ | 角速度误差↓ | 碰撞率↓ |
|---|---|---|---|
| ROA (w/ BC Loss) [68] | 0.189 | 0.152 | 3.25 |
| ROA [68] | 0.161 | 0.152 | 3.09 |
| **NaVILA** | **0.066** | **0.113** | **0.81** |

### C. 仿真中的腿式机器人导航性能

**高保真 VLN-CE-Isaac 基准。** 目前没有专门为腿式机器人定制的 VLN-CE 基准。现有视觉语言导航基准 [29, 30] 基于 Habitat [69] 仿真器，侧重高层规划而不涉及精确的低层机器人控制。例如，Habitat 中的智能体可以穿过 10 厘米宽的缝隙（如两个沙发之间），这对四足或人形等腿式机器人并不现实。为克服这一局限，我们引入基于 Isaac Sim 的新基准 VLN-CE-Isaac。Isaac Sim 的高保真仿真捕捉了细致的机器人关节运动及与环境的交互，使得从高层规划到精确机器人执行的整个导航管线都能被全面评估。我们采用与 R2R 相同的场景并将机器人部署其中（如图 6 所示）。从 R2R Val-Unseen 划分的 1839 条轨迹中，我们选取 1077 条具有高质网格的可通行轨迹，以确保导航场景的真实性。为保持一致性，我们使用与先前工作相同的指标评估性能。

**【图 6：VLN-CE-Isaac 基准可视化：腿式机器人（Go2、H1）在重建的室内场景中进行视觉语言导航的仿真画面。】**

值得注意的是，VLN-CE-Isaac 兼容多种机器人平台。为展示这种灵活性，我们在基准中测试了 Unitree Go2 机器人和 Unitree H1 机器人。为凸显视觉策略的有效性，我们将其与仅本体感知的盲视策略进行比较。如表 IV 所示，视觉策略在 Go2 设定下成功率比盲视策略高 14%，在 H1 设定下高 21%，这归功于其更优的避障能力。我们还与使用 Oracle 低层策略的基线（假设指令被完美执行、不考虑真实物理）比较了 NaVILA：在 Go2 设定上不使用 Oracle 策略时成功率低 15%，在 H1 设定上低 27%。这些性能差距突显了我们的基准带来的更高挑战性与真实性。此外，我们还观察到 NaVILA 在 H1 机器人上的成功率显著低于 Go2，这符合预期，因为人形机器人尺寸更大。

**表 IV：VLN-CE-Isaac 评估结果。**（低层观测：Proprio.=本体感知；LiDAR Height Scan=LiDAR 高度扫描）

| 低层观测 | Proprio. | LiDAR | NE↓ | OS↑ | SR↑ | SPL↑ |
|---|---|---|---|---|---|---|
| Oracle | | | 5.25 | 59.8 | 51.3 | 46.9 |
| *Unitree Go2* | | | | | | |
| NaVILA-Blind | ✓ | | 6.03 | 49.0 | 36.2 | 33.3 |
| NaVILA-Vision | ✓ | ✓ | 5.49 | 58.7 | 50.2 | 45.5 |
| *Unitree H1* | | | | | | |
| NaVILA-Blind | ✓ | | 7.67 | 33.3 | 24.4 | 21.0 |
| NaVILA-Vision | ✓ | ✓ | 5.86 | 54.6 | 45.3 | 40.3 |

### D. 真实世界评估

随后我们在真实世界中进行实验，使用 25 条指令，每条重复三次，涵盖三类环境——工作区（Workspace）、家庭（Home）和户外开放环境——中的简单与复杂任务。简单指令由一两条导航指令组成，机器人无需在房间之间穿行（如"走到椅子旁停下"）；复杂指令则包含三条或更多指令，要求机器人穿越多个房间或地标（如"走出房间，右转，进入你前方的房间，停在桌边"）。我们使用标准指标（SR 和 NE），并将 NaVILA 与 GPT-4o——一个以强泛化性著称的最先进 VLM——进行比较。如表 VI 所示，NaVILA 在 SR 和 NE 上均显著优于 GPT-4o。我们还对加入人类视频的效果做了消融：结果表明，借助人类视频，模型能更好地泛化到户外场景，并在所有环境中取得更高成功率。为展示两层方法的灵活性，我们还在 Booster Dynamics T1 人形机器人上做了评估，使用同一个 VLA 模型且不做任何重训练。尽管存在相机高度与视角变化等因素，NaVILA 始终优于基线，凸显了模型的强泛化能力。定性结果见图 1 与图 7。在图 7 中，我们展示了与语音识别的集成，实现了通过我们框架的语音控制导航。这些结果突显了 NaVILA 在弥合视觉-语言理解与真实世界导航任务之间鸿沟方面的有效性。

**表 VI：四足（Unitree Go2）与人形（Booster T1）机器人在不同环境（工作区、家庭、户外）中的真实世界实验。** Simple 与 Complex 分别指简单与复杂指令跟随任务。† 表示未使用人类游览视频训练的模型。

| 机器人 / 方法 | Workspace Simple NE↓ SR↑ | Workspace Complex NE↓ SR↑ | Home Simple NE↓ SR↑ | Home Complex NE↓ SR↑ | Outdoor Simple NE↓ SR↑ | Outdoor Complex NE↓ SR↑ |
|---|---|---|---|---|---|---|
| *Unitree Go2* | | | | | | |
| GPT-4o [28] | 2.01 / 0.67 | 2.38 / 0.33 | 1.49 / 0.53 | 3.00 / 0.00 | - / 0.67 | - / 0.50 |
| NaVILA † | 2.00 / 0.60 | 1.81 / 0.73 | 2.17 / 0.47 | 2.32 / 0.40 | - / 0.00 | - / 0.00 |
| **NaVILA** | **1.29 / 1.00** | **1.76 / 0.80** | **1.15 / 1.00** | **1.76 / 0.67** | **- / 1.00** | **- / 0.83** |
| *Booster T1* | | | | | | |
| GPT-4o [28] | 1.53 / 0.67 | 2.78 / 0.13 | - / - | - / - | - / 0.44 | - / - |
| NaVILA † | 2.36 / 0.40 | 2.16 / 0.62 | - / - | - / - | - / 0.22 | - / - |
| **NaVILA** | **1.18 / 0.93** | **1.91 / 0.67** | - / - | - / - | **- / 0.89** | - / - |

**【图 7：NaVILA 真实世界部署的定性结果。(a) 我们将语音识别 [70] 集成到 NaVILA 中，人类可以用以"Hey Robot!"开头的语音指令控制机器人（示例指令："向前走，在垃圾桶处右转，靠近门时停下"）。(b) 机器人成功处理长时程导航任务：给定一条很长的指令，它穿过住宅的不同区域并停在指定目标（"右转绕楼梯走到走廊，稍向左转朝肖像海报走，会看到一扇开着的门；直行进入房间直到圆形空间尽头；左转进浴室；走到浴室垫并踩上去；右转向前走到体重秤处"）。(c)(d)(e) 机器人展示了穿越障碍、跨越挑战性地形（"沿斜坡走并踏入停车场，停在橙色锥桶前"；"沿路走，停在石凳和石桌前"）以及上下楼梯（"上楼梯并停在门前"）的能力。】**

## IV. 相关工作

**视觉导航。** 视觉导航是机器人学中一个长期研究课题 [71–74]。经典方法依赖预计算地图 [75]，或在使用深度传感器 [76]、单目相机为机器人定位（SLAM）[77, 78] 的同时构建几何地图。最近，使用模仿学习 [79, 80] 和强化学习 [81, 82] 的学习型方法展现出强大性能，并将应用扩展到了视觉-语言导航。

**视觉-语言导航。** 视觉-语言导航（VLN）是具身智能（embodied AI）的基础挑战：智能体利用视觉线索与自然语言指令在复杂环境中导航。该领域随时间显著演进。早期研究 [1, 30, 83] 关注 MP3D [84] 等仿真环境中的离散导航，智能体在导航图的预定义节点之间瞬移 [31, 85–91]。随着基础模型的发展，许多 VLN 系统通过利用大规模预训练模型 [25, 92] 和预训练技术 [24, 52, 93] 取得大幅进步，在该设定下接近人类水平。然而，这种设定强调高层决策而忽略了底层运动控制的挑战。近来，研究 [12, 54–57] 转向使用 Habitat [69] 等仿真器的连续环境（VLN-CE [58]）。这引入了更大的复杂性，因为智能体必须执行前进或旋转等中层动作，而非在节点间瞬移。为弥合离散与连续导航的差距，一些方法 [44, 49, 51, 94] 使用仿真器预训练的路点模型 [42, 43] 来预测智能体周围的候选位置，并取得了显著的性能提升。然而，由于依赖仿真器特定数据，这些方法往往难以泛化。此外，这些模型预测的候选位置只覆盖附近位置，且不考虑低层运动规划或避障。本文旨在推动 VLN 走向真实机器人应用，特别是面向具有挑战性的腿式机器人。NaVILA 同时处理高层决策并生成低层动作来控制机器人的完整运动。此外，我们引入基于 Isaac Sim 的新 VLN 基准，提供更真实的仿真环境，相信这将惠及未来 VLN 工作。

**机器人基础模型。** 机器人基础模型旨在提供统一框架，处理多种模态（如视觉与语言）的输入并直接输出动作，使机器人能够完成复杂任务。现有工作 [7, 8, 95] 在大规模机器人数据集上训练以获得通用机器人策略，但主要聚焦于操作任务。Doshi 等人 [96] 和 Yang 等人 [97] 提出了面向不同机器人任务的端到端视觉-语言跨具身（cross-embodiment）模型。最近，若干基础导航模型被提出 [98–100]，但它们主要关注以简短语言描述或目标图像为输入的目标导航。对于腿式机器人，Ding 等人 [101] 提出统一模型，利用视觉和语言输入生成可执行的低层动作。另一条工作线 [102, 103] 关注训练专门的策略作为技能库以处理特定动作，由 VLM 或 LLM 充当控制器来决定执行哪个技能。类似地，这些方法无法执行指令跟随任务，因为它们难以理解对通用导航至关重要的复杂指令。为此，我们提出专为通用视觉语言导航任务设计的 VLA 模型。

**腿式机器人运动学习。** 腿式机器人运动学习关注使机器人能够穿越各种地形。仅依赖机器人本体感知信息的先前工作 [104, 105] 在避障等场景中表现吃力；其他端到端视觉方法 [106–109] 则因传感器局限易受极端环境条件（如强烈阳光）影响。Lee 等人 [38] 在深度相机之外加入 LiDAR 传感器以改善地形感知，但依赖耗时的两阶段训练。此外，Miki 等人 [39] 在训练时查询预定义地形高度来构建高度图，而部署时依赖外部工具 [110] 生成高度图，导致训练与部署之间的差异。为克服这些局限，我们提出单阶段 RL 框架，在训练中整合 LiDAR 感知输入，使机器人能够直接从与环境的交互中学习，在复杂场景中获得更好的效率与鲁棒性。

## V. 结论与局限

我们介绍了 NaVILA——一个将 VLA 与运动技能统一用于通用导航的两层框架。NaVILA 生成高层语言指令，而实时运动策略负责避障，增强了跨机器人鲁棒性。该设计既保留了推理能力，又防止过拟合，并能直接从人类视频中学习以获得更好的泛化。NaVILA 在经典 VLN 基准上取得 17% 的提升，超越基于蒸馏的低层策略，在 VLN-CE-Isaac 上胜过盲视策略，并在多样环境与多种腿式机器人上展现出强大的真实世界性能。

**局限。** 尽管 NaVILA 性能强大，但在某些真实场景中仍会失败（见附录 E 节）。通过在真实感仿真中进行更大规模训练来增强泛化性与空间理解可能有所帮助。此外，基于图像的视觉-语言模型计算开销大；长上下文 LLM 的进展可能通过更高效的序列处理来缓解这一问题。

## 附录

**附录目录：**
- A 更多消融研究（A1 不同仿真数据配比；A2 人类游览视频数据；A3 不同记忆大小）
- B 更多定性结果（B1 VLN-CE-Isaac；B2 真实世界；B3 空间场景理解）
- C 更多实现细节（C1 视频导航轨迹总结；C2 VLA 超参数；C3 运动策略；C4 VLA 计算资源）
- D 参数高效量化
- E 局限

### A. 更多消融研究

**1) 不同仿真数据配比：** 我们通过消融研究评估不同仿真数据配比对 VLA 训练的影响。如表 VII 所示，不进行标签再平衡的导航数据训练会导致性能显著下降。此外，仅在 RxR 数据上训练的 VLA 在 R2R-CE 上表现出合理的跨数据集性能，印证了我们在表 II 中的观察。最后，我们考察了去除 RxR 数据集是否会降低 R2R-CE 性能：结果表明 RxR 数据集对 R2R-CE 性能贡献并不显著。

**表 VII：R2R-CE 上使用不同数据配比的结果（Val Unseen）。**

| 方法 | NE↓ | OSR↑ | SR↑ | SPL↑ |
|---|---|---|---|---|
| NaVILA †（无标签平衡） | 7.82 | 47.5 | 30.0 | 25.1 |
| NaVILA †（仅 RxR） | 7.57 | 40.8 | 31.5 | 27.8 |
| NaVILA †（无 RxR） | 6.11 | 57.0 | 47.7 | 42.4 |
| NaVILA † | **5.37** | **57.6** | **49.7** | **45.5** |

**2) 人类游览视频数据：** 我们在仿真中进行消融，评估使用 YouTube 人类游览视频真实数据的效果。如表 VIII 所示，加入该数据带来显著提升，OS、SR、SPL 均提高约 5%。真实世界实验（表 VI）同样显示更高的成功率与更少的导航误差。这些结果验证了我们数据管线的有效性，并突显了 NaVILA 框架的可扩展性——它支持轻松整合来自多样来源的数据。

**表 VIII：R2R-CE 上使用来自人类游览视频的额外真实数据的结果（Val Unseen）。** † 表示未使用人类游览视频训练的模型。

| 方法 | NE↓ | OSR↑ | SR↑ | SPL↑ |
|---|---|---|---|---|
| NaVILA † | 5.37 | 57.6 | 49.7 | 45.5 |
| NaVILA | **5.22** | **62.5** | **54.0** | **49.0** |

**3) 不同记忆大小：** 我们在 R2R-CE 基准上进行消融，评估记忆大小（历史帧数）对导航任务的影响。表 IX 的结果表明，对 R2R-CE 而言 8 帧足以覆盖大多数指令时程，增大记忆带来的性能提升有限。真实世界实验中，受延迟限制我们采用 8 帧记忆。

**表 IX：R2R-CE [29] Validation Unseen 划分上不同记忆大小的消融研究。**

| 方法 | NE↓ | OSR↑ | SR↑ | SPL↑ |
|---|---|---|---|---|
| NaVid [12] | 5.47 | 49.0 | 37.0 | 35.0 |
| NaVILA †（8 帧） | **5.37** | 57.6 | 49.7 | **45.5** |
| NaVILA †（16 帧） | 5.63 | 55.8 | 48.6 | 44.4 |
| NaVILA †（32 帧） | 5.74 | 55.9 | 49.5 | 44.1 |
| NaVILA †（64 帧） | 5.63 | **60.5** | **50.1** | 45.4 |

### B. 更多定性结果

**1) VLN-CE-Isaac：** 图 8 展示了一个可视化示例，说明为何 Go2 视觉策略显著优于盲视策略。如图所示，当遇到障碍时，并未专门针对避障训练的 VLA 无法有效绕行；盲视策略在没有额外传感输入的情况下执行 VLA 指令，被卡在障碍处。相反，利用 LiDAR 输入训练的视觉策略即使高层 VLA 模型没有检测到危险，也能自主避障。

**【图 8：Go2 盲视策略与视觉策略对比。盲视策略未能避开障碍物而被卡住；视觉策略检测到障碍并绕行避开。】**

**2) 真实世界：** 图 9 展示了更多真实世界结果。NaVILA 在多样设定中展现出鲁棒的性能与出色的泛化能力。

**【图 9：更多多样环境中的结果，如城市街道、校园人行道、庭院和不同住宅，示例指令包括"稍向左转，直行，踩上草地时停下"、"向前走，踩上草地继续前进，靠近大熊雕像时停下"、"走到房间另一端，左转，找到一套玩具厨具"、"前进进入厨房，在拐角右转，直行，停在红碗前"、"走出房间，右转进入另一个房间，停在桌前"、"立即右转，沿走廊走，在尽头左转进入最左边的卧室"、"一直往前走，在路口左转，找到书架/球"。这些设定带来了显著多样性与挑战，包括崎岖地形、动态物体与不同光照条件。NaVILA 取得的结果是一个重要里程碑，展示了此前从未被演示过的能力。】**

**3) 空间场景理解：** 图 10 展示了 NaVILA 在 ScanQA 基准上的空间场景理解定性结果。

**【图 10：ScanQA 基准上的空间场景理解结果。给定从视频中采样的图像序列，NaVILA 能正确地定位（ground）并识别物体。图中以浴室场景的四组问答展示模型的视觉定位能力。】** 示例问答：

- 问：垃圾桶放在哪里？ NaVILA：马桶右边。
- 问：马桶和浴缸之间的墙上挂着什么？ NaVILA：卫生纸。
- 问：椅子右边的墙上能看到什么？ NaVILA：白板。
- 问：房间角落里的小冰箱是什么颜色？ NaVILA：黑色。

### C. 更多实现细节

**1) 视频导航轨迹总结：** 我们为"视频导航轨迹总结"辅助任务提供数据提示词。沿用 [12] 的方法，我们构建提示模板，将 LLM 刻画为导航机器人。我们将轨迹视频处理为历史帧，把帧 token 插入提示中，让 LLM 从视频推断导航指令。该任务旨在增强机器人对场景的理解及其对指令格式的熟悉度。提示词为：

> Assume you are a robot designed for navigation. You are provided with captured image sequences: `<frame3><frame6><frame9>...` Based on this image sequence, please describe the navigation trajectory of the robot.
> （假设你是一个为导航设计的机器人。你获得采集的图像序列：`<帧3><帧6><帧9>……`。基于该图像序列，请描述机器人的导航轨迹。）

**2) VLA 超参数：** 前两个阶段的超参数详见 VILA 论文。在指令微调阶段，我们使用学习率 $1\times10^{-4}$、余弦衰减和 0.03 的预热比率（warm-up ratio）。我们将在论文发表后公开训练代码与数据。

**3) 运动策略：** Go2 运动策略训练所用的奖励函数与域随机化见表 X 与表 XI。鲁棒策略在图 11 所示的平地、粗糙、坡道和障碍地形上训练。LiDAR 与高度图设置见表 XII。

**【图 11：随机粗糙、障碍与坡道地形。】**

**表 X：训练 RL 策略的奖励函数参数。**

| 奖励项 | 表达式 | 权重 |
|---|---|---|
| 线速度跟踪 | $\exp(-\lVert \mathbf{v}^{cmd}_{xy} - \mathbf{v}_{xy}\rVert_2^2)$ | 1.5 |
| 角速度跟踪 | $\exp(-\lVert \omega^{cmd}_{yaw} - \omega_{yaw}\rVert_2^2)$ | 1.5 |
| 线速度惩罚（z） | $v_z^2$ | -2.0 |
| 角速度惩罚（xy） | $\lVert\boldsymbol{\omega}_{xy}\rVert_2^2$ | -0.05 |
| 机身姿态平稳 | $\lVert\mathbf{g}\rVert_2^2$ | -2.0 |
| 关节加速度 | $\lVert\ddot{\boldsymbol{\theta}}\rVert^2$ | $-2.5\times10^{-7}$ |
| 能量 | $-\lVert\boldsymbol{\tau}\dot{\mathbf{q}}\rVert_2^2$ | $-2\times10^{-5}$ |
| 机身高度 | $(h_{target}-h)^2$ | -5.0 |
| 足部打滑 | $-\lVert\mathbf{v}_{feet}\cdot\mathbf{1}[F_{feet}>1]\rVert^2$ | 0.05 |

**表 XI：训练 RL 策略的域随机化参数。**

| 参数 | 取值范围 |
|---|---|
| 机身质量 | [-3.0, 3.0] |
| 静摩擦系数 | [0.4, 4.0] |
| 动摩擦系数 | [0.4, 4.0] |
| 电机强度 | [0.9, 1.1] |
| 系统延迟 | $[\Delta t, \Delta t]$ |

**表 XII：仿真中的 LiDAR 与高度图参数。**

| 参数 | 取值 |
|---|---|
| 通道数 | 32 |
| 垂直范围（度） | (0, 90) |
| 水平范围（度） | (-180, 180) |
| 水平分辨率（度） | 4 |
| 体素尺寸（m） | 0.06 |
| X 范围（m） | [-0.8, 0.2] |
| Y 范围（m） | [-0.8, 0.8] |
| Z 范围（m） | [0.05, 0.5] |

**4) VLA 计算资源：** NaVILA 的前两个阶段继承自 VILA [13]，在 16 个 A100 GPU 节点（每节点 8 卡）上训练。我们 8B 模型各阶段训练时长为：连接器初始化 4 小时，视觉语言预训练 30 小时；最后的视觉指令微调阶段在 4 个 A100 GPU 节点上实验，耗时 18 小时。推理时，NaVILA 的 VLA 模型可在单块 RTX 4090 GPU 上以约 1 FPS 运行。

### D. 参数高效量化

我们探索了提升 NaVILA 推理效率的优化技术。具体而言，我们将 AWQ [111]——一种最先进的 VLM 量化方法——应用到 FP16 的 NaVILA-8B 模型上。通过将其转换为 W4A16 格式（低比特仅权重量化），我们取得显著改进：显存需求减半，处理速度提升约 40%。最重要的是，导航能力保持稳健，结果见表 XIII。这些优化使 NaVILA 可以直接部署在机器人上，从而显著消除图像传输时间，我们将其留作未来工作。

**【图 12：避障截图。运动策略在高草、某些透明玻璃和强阳光下的大型物体面前能保证无碰撞；策略在沙地和草地地形上表现出鲁棒性。】**

**表 XIII：NaVILA 量化结果。** 计算成本在 RTX 4090 上测试，使用 1737 个上下文 token 和 10 个生成 token，测试样本取自 R2R-CE。

| 模型 | 总延迟 (ms)↓ | GPU 显存 (GB)↓ | NE↓ | OS↑ | SR↑ | SPL↑ |
|---|---|---|---|---|---|---|
| NaVILA (FP16) | 594.58 | 18.5 | 5.37 | 57.6 | 49.7 | 45.5 |
| NaVILA (W4A16) | **367.80** | **8.6** | 5.66 | 56.8 | 48.2 | 43.6 |

### E. 局限

图 13 展示了一个真实世界失败案例：机器人起初遵循指令，但最终未能到达卧室。该失败源于机器人在出现偏差时无法进行有效的纠错。为进一步提升性能，增强泛化性与空间理解是关键。一个潜在方向是在更真实的仿真中进行更大规模训练，以提供更多样的导航场景与错误恢复案例。此外，在训练中加入显式推理数据可能帮助模型更好地预判并纠正错误。

**【图 13：NaVILA 的失败案例。指令为"沿走廊走并进入卧室"，机器人未能到达卧室。】**

## 参考文献（References，原文保留未译）

[1] Peter Anderson, Qi Wu, Damien Teney, Jake Bruce, Mark Johnson, Niko Sünderhauf, Ian Reid, Stephen Gould, and Anton Van Den Hengel. Vision-and-language navigation: Interpreting visually-grounded navigation instructions in real environments. In CVPR, 2018.

[2] Xin Wang, Qiuyuan Huang, Asli Celikyilmaz, Jianfeng Gao, Dinghan Shen, Yuan-Fang Wang, William Yang Wang, and Lei Zhang. Reinforced cross-modal matching and self-supervised imitation learning for vision-language navigation. In CVPR, 2019.

[3] Devendra Singh Chaplot, Dhiraj Gandhi, Saurabh Gupta, Abhinav Gupta, and Ruslan Salakhutdinov. Learning to explore using active neural slam. In ICLR, 2020.

[4] Devendra Singh Chaplot, Dhiraj Prakashchand Gandhi, Abhinav Gupta, and Russ R Salakhutdinov. Object goal navigation using goal-oriented semantic exploration. In NeurIPS, 2020.

[5] Devendra Singh Chaplot, Ruslan Salakhutdinov, Abhinav Gupta, and Saurabh Gupta. Neural topological slam for visual navigation. In CVPR, 2020.

[6] Ram Ramrakhya, Eric Undersander, Dhruv Batra, and Abhishek Das. Habitat-web: Learning embodied object-search strategies from human demonstrations at scale. In CVPR, 2022.

[7] Anthony Brohan, Noah Brown, Justice Carbajal, Yevgen Chebotar, Xi Chen, Krzysztof Choromanski, Tianli Ding, Danny Driess, Avinava Dubey, Chelsea Finn, et al. Rt-2: Vision-language-action models transfer web knowledge to robotic control. arXiv preprint, 2023.

[8] Moo Jin Kim, Karl Pertsch, Siddharth Karamcheti, Ted Xiao, Ashwin Balakrishna, Suraj Nair, Rafael Rafailov, Ethan Foster, Grace Lam, Pannag Sanketi, et al. Openvla: An open-source vision-language-action model. arXiv preprint, 2024.

[9] Abhishek Padalkar, Acorn Pooley, Ajinkya Jain, Alex Bewley, Alex Herzog, Alex Irpan, Alexander Khazatsky, Anant Rai, Anikait Singh, Anthony Brohan, et al. Open x-embodiment: Robotic learning datasets and rt-x models. In ICRA, 2024.

[10] Boyuan Chen, Zhuo Xu, Sean Kirmani, Brain Ichter, Dorsa Sadigh, Leonidas Guibas, and Fei Xia. Spatialvlm: Endowing vision-language models with spatial reasoning capabilities. In CVPR, 2024.

[11] An-Chieh Cheng, Hongxu Yin, Yang Fu, Qiushan Guo, Ruihan Yang, Jan Kautz, Xiaolong Wang, and Sifei Liu. Spatialrgpt: Grounded spatial reasoning in vision-language models. In NeurIPS, 2024.

[12] Jiazhao Zhang, Kunyu Wang, Rongtao Xu, Gengze Zhou, Yicong Hong, Xiaomeng Fang, Qi Wu, Zhizheng Zhang, and Wang He. Navid: Video-based vlm plans the next step for vision-and-language navigation. In RSS, 2024.

[13] Ji Lin, Hongxu Yin, Wei Ping, Pavlo Molchanov, Mohammad Shoeybi, and Song Han. Vila: On pre-training for visual language models. In CVPR, 2024.

[14] Yecheng Wu, Zhuoyang Zhang, Junyu Chen, Haotian Tang, Dacheng Li, Yunhao Fang, Ligeng Zhu, Enze Xie, Hongxu Yin, Li Yi, et al. Vila-u: a unified foundation model integrating visual understanding and generation. arXiv preprint, 2024.

[15] Yunhao Fang, Ligeng Zhu, Yao Lu, Yan Wang, Pavlo Molchanov, Jan Kautz, Jang Hyun Cho, Marco Pavone, Song Han, and Hongxu Yin. Vila²: Vila augmented vila. arXiv preprint, 2024.

[16] Fuzhao Xue, Yukang Chen, Dacheng Li, Qinghao Hu, Ligeng Zhu, Xiuyu Li, Yunhao Fang, Haotian Tang, Shang Yang, Zhijian Liu, et al. Longvila: Scaling long-context visual language models for long videos. arXiv preprint, 2024.

[17] Hanrong Ye, De-An Huang, Yao Lu, Zhiding Yu, Wei Ping, Andrew Tao, Jan Kautz, Song Han, Dan Xu, Pavlo Molchanov, et al. X-vila: Cross-modality alignment for large language model. arXiv preprint, 2024.

[18] De-An Huang, Shijia Liao, Subhashree Radhakrishnan, Hongxu Yin, Pavlo Molchanov, Zhiding Yu, and Jan Kautz. Lita: Language instructed temporal-localization assistant. In ECCV, 2024.

[19] Zhijian Liu, Ligeng Zhu, Baifeng Shi, Zhuoyang Zhang, Yuming Lou, Shang Yang, Haocheng Xi, Shiyi Cao, Yuxian Gu, Dacheng Li, et al. Nvila: Efficient frontier visual language models. arXiv preprint, 2024.

[20] Haotian Liu, Chunyuan Li, Qingyang Wu, and Yong Jae Lee. Visual instruction tuning. In NeurIPS, 2023.

[21] Minwoo Byeon, Beomhee Park, Haecheon Kim, Sungjun Lee, Woonhyuk Baek, and Saehoon Kim. Coyo-700m: Image-text pair dataset. https://github.com/kakaobrain/coyo-dataset, 2022.

[22] Wanrong Zhu, Jack Hessel, Anas Awadalla, Samir Yitzhak Gadre, Jesse Dodge, Alex Fang, Youngjae Yu, Ludwig Schmidt, William Yang Wang, and Yejin Choi. Multimodal c4: An open, billion-scale corpus of images interleaved with text. In NeurIPS, 2024.

[23] Haotian Liu, Chunyuan Li, Yuheng Li, and Yong Jae Lee. Improved baselines with visual instruction tuning. In CVPR, 2024.

[24] Pierre-Louis Guhur, Makarand Tapaswi, Shizhe Chen, Ivan Laptev, and Cordelia Schmid. Airbert: In-domain pretraining for vision-and-language navigation. In ICCV, 2021.

[25] Arjun Majumdar, Ayush Shrivastava, Stefan Lee, Peter Anderson, Devi Parikh, and Dhruv Batra. Improving vision-and-language navigation with image-text pairs from the web. In ECCV, 2020.

[26] Kunyang Lin, Peihao Chen, Diwei Huang, Thomas H Li, Mingkui Tan, and Chuang Gan. Learning vision-and-language navigation from youtube videos. In ICCV, 2023.

[27] Vincent Leroy, Yohann Cabon, and Jérôme Revaud. Grounding image matching in 3d with mast3r. In ECCV. Springer, 2024.

[28] OpenAI. Hello gpt-4o, 2024. URL https://openai.com/index/hello-gpt-4o/.

[29] Jacob Krantz, Erik Wijmans, Arjun Majundar, Dhruv Batra, and Stefan Lee. Beyond the nav-graph: Vision and language navigation in continuous environments. In ECCV, 2020.

[30] Alexander Ku, Peter Anderson, Roma Patel, Eugene Ie, and Jason Baldridge. Room-across-room: Multilingual vision-and-language navigation with dense spatiotemporal grounding. In EMNLP, 2020.

[31] Hao Tan, Licheng Yu, and Mohit Bansal. Learning to navigate unseen environments: Back translation with environmental dropout. In NAACL, 2019.

[32] Daichi Azuma, Taiki Miyanishi, Shuhei Kurita, and Motoaki Kawanabe. Scanqa: 3d question answering for spatial scene understanding. In CVPR, 2022.

[33] Lin Chen, Jisong Li, Xiaoyi Dong, Pan Zhang, Conghui He, Jiaqi Wang, Feng Zhao, and Dahua Lin. Sharegpt4v: Improving large multi-modal models with better captions. In ECCV, 2024.

[34] Muhammad Maaz, Hanoona Rasheed, Salman Khan, and Fahad Shahbaz Khan. Video-chatgpt: Towards detailed video understanding via large vision and language models. In ACL, 2024.

[35] Steven M Kearns. Extending regular expressions with context operators and parse extraction. Software: Practice and Experience, 1991.

[36] Mayank Mittal, Calvin Yu, Qinxi Yu, Jingzhou Liu, Nikita Rudin, David Hoeller, Jia Lin Yuan, Ritvik Singh, Yunrong Guo, Hammad Mazhar, Ajay Mandlekar, Buck Babich, Gavriel State, Marco Hutter, and Animesh Garg. Orbit: A unified simulation framework for interactive robot learning environments. In RAL, 2023.

[37] John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization algorithms. arXiv preprint, 2017.

[38] Joonho Lee, Jemin Hwangbo, Lorenz Wellhausen, Vladlen Koltun, and Marco Hutter. Learning quadrupedal locomotion over challenging terrain. Science Robotics, 2020.

[39] Takahiro Miki, Joonho Lee, Jemin Hwangbo, Lorenz Wellhausen, Vladlen Koltun, and Marco Hutter. Learning robust perceptive locomotion for quadrupedal robots in the wild. Science Robotics, 2022.

[40] Gabriel B Margolis, Ge Yang, Kartik Paigwar, Tao Chen, and Pulkit Agrawal. Rapid locomotion via reinforcement learning. In RSS, 2022.

[41] Joonho Lee, Marko Bjelonic, Alexander Reske, Lorenz Wellhausen, Takahiro Miki, and Marco Hutter. Learning robust autonomous navigation and locomotion for wheeled-legged robots. Science Robotics, 2024.

[42] Yicong Hong, Zun Wang, Qi Wu, and Stephen Gould. Bridging the gap between learning in discrete and continuous environments for vision-and-language navigation. In CVPR, 2022.

[43] Jacob Krantz, Aaron Gokaslan, Dhruv Batra, Stefan Lee, and Oleksandr Maksymets. Waypoint models for instruction-guided navigation in continuous environments. In CVPR, 2021.

[44] Jacob Krantz and Stefan Lee. Sim-2-sim transfer for vision-and-language navigation in continuous environments. In ECCV, 2022.

[45] Zihan Wang, Xiangyang Li, Jiahao Yang, Yeqi Liu, and Shuqiang Jiang. Gridmm: Grid memory map for vision-and-language navigation. In ICCV, 2023.

[46] Yicong Hong, Yang Zhou, Ruiyi Zhang, Franck Dernoncourt, Trung Bui, Stephen Gould, and Hao Tan. Learning navigational visual representations with semantic map supervision. In ICCV, 2023.

[47] Hanqing Wang, Wei Liang, Luc Van Gool, and Wenguan Wang. Dreamwalker: Mental planning for continuous vision-language navigation. In ICCV, 2023.

[48] Dong An, Zun Wang, Yangguang Li, Yi Wang, Yicong Hong, Yan Huang, Liang Wang, and Jing Shao. 1st place solutions for rxr-habitat vision-and-language navigation competition. In CVPRW, 2022.

[49] Dong An, Hanqing Wang, Wenguan Wang, Zun Wang, Yan Huang, Keji He, and Liang Wang. Etpnav: Evolving topological planning for vision-language navigation in continuous environments. IEEE TPAMI, 2024.

[50] Zihan Wang, Xiangyang Li, Jiahao Yang, Yeqi Liu, Junjie Hu, Ming Jiang, and Shuqiang Jiang. Lookahead exploration with neural radiance representation for continuous vision-language navigation. In CVPR, 2024.

[51] Dong An, Yuankai Qi, Yangguang Li, Yan Huang, Liang Wang, Tieniu Tan, and Jing Shao. Bevbert: Multimodal map pre-training for language-guided navigation. In ICCV, 2023.

[52] Zun Wang, Jialu Li, Yicong Hong, Yi Wang, Qi Wu, Mohit Bansal, Stephen Gould, Hao Tan, and Yu Qiao. Scaling data generation in vision-and-language navigation. In ICCV, 2023.

[53] Kevin Chen, Junshen K Chen, Jo Chuang, Marynel Vázquez, and Silvio Savarese. Topological planning with transformers for vision-and-language navigation. In CVPR, 2021.

[54] Sonia Raychaudhuri, Saim Wani, Shivansh Patel, Unnat Jain, and Angel Chang. Language-aligned waypoint (law) supervision for vision-and-language navigation in continuous environments. In EMNLP, 2021.

[55] Georgios Georgakis, Karl Schmeckpeper, Karan Wanchoo, Soham Dan, Eleni Miltsakaki, Dan Roth, and Kostas Daniilidis. Cross-modal map learning for vision and language navigation. In CVPR, 2022.

[56] Peihao Chen, Dongyu Ji, Kunyang Lin, Runhao Zeng, Thomas Li, Mingkui Tan, and Chuang Gan. Weakly-supervised multi-granularity map learning for vision-and-language navigation. In NeurIPS, 2022.

[57] Jiaqi Chen, Bingqian Lin, Xinmin Liu, Xiaodan Liang, and Kwan-Yee K Wong. Affordances-oriented planning using foundation models for continuous vision-language navigation. arXiv preprint, 2024.

[58] Jacob Krantz, Erik Wijmans, Arjun Majumdar, Dhruv Batra, and Stefan Lee. Beyond the nav-graph: Vision-and-language navigation in continuous environments. In ECCV, 2020.

[59] Peihao Chen, Xinyu Sun, Hongyan Zhi, Runhao Zeng, Thomas H. Li, Gaowen Liu, Mingkui Tan, and Chuang Gan. A2 nav: Action-aware zero-shot robot navigation by exploiting vision-and-language ability of foundation models. arXiv preprint, 2023.

[60] Duo Zheng, Shijia Huang, Lin Zhao, Yiwu Zhong, and Liwei Wang. Towards learning a generalist model for embodied navigation. In CVPR, 2024.

[61] Rao Fu, Jingyu Liu, Xilun Chen, Yixin Nie, and Wenhan Xiong. Scene-llm: Extending language model for 3d visual understanding and reasoning. arXiv preprint, 2024.

[62] Jiangyong Huang, Silong Yong, Xiaojian Ma, Xiongkun Linghu, Puhao Li, Yan Wang, Qing Li, Song-Chun Zhu, Baoxiong Jia, and Siyuan Huang. An embodied generalist agent in 3d world. In ICML, 2024.

[63] Zhou Yu, Jun Yu, Yuhao Cui, Dacheng Tao, and Qi Tian. Deep modular co-attention networks for visual question answering. In CVPR, 2019.

[64] Ziyu Zhu, Xiaojian Ma, Yixin Chen, Zhidong Deng, Siyuan Huang, and Qing Li. 3d-vista: Pre-trained transformer for 3d vision and text alignment. In ICCV, 2023.

[65] Yining Hong, Haoyu Zhen, Peihao Chen, Shuhong Zheng, Yilun Du, Zhenfang Chen, and Chuang Gan. 3d-llm: Injecting the 3d world into large language models. In NeurIPS, 2023.

[66] Sijin Chen, Xin Chen, Chi Zhang, Mingsheng Li, Gang Yu, Hao Fei, Hongyuan Zhu, Jiayuan Fan, and Tao Chen. Ll3da: Visual interactive instruction tuning for omni-3d understanding reasoning and planning. In CVPR, 2024.

[67] Haifeng Huang, Zehan Wang, Rongjie Huang, Luping Liu, Xize Cheng, Yang Zhao, Tao Jin, and Zhou Zhao. Chat-scene: Bridging 3d scene and large language models with object identifiers. In NeurIPS, 2024.

[68] Zipeng Fu, Xuxin Cheng, and Deepak Pathak. Deep whole-body control: Learning a unified policy for manipulation and locomotion. In CoRL, 2022.

[69] Manolis Savva, Abhishek Kadian, Oleksandr Maksymets, Yili Zhao, Erik Wijmans, Bhavana Jain, Julian Straub, Jia Liu, Vladlen Koltun, Jitendra Malik, et al. Habitat: A platform for embodied ai research. In ICCV, 2019.

[70] Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine McLeavey, and Ilya Sutskever. Robust speech recognition via large-scale weak supervision. In ICML, 2023.

[71] Hans Peter Moravec. Obstacle avoidance and navigation in the real world by a seeing robot rover. Stanford University, 1980.

[72] Alberto Elfes. Sonar-based real-world mapping and navigation. IEEE Journal on Robotics and Automation, 1987.

[73] Sebastian Thrun, Dieter Fox, Wolfram Burgard, and Frank Dellaert. Robust monte carlo localization for mobile robots. Artificial intelligence, 2001.

[74] Theophile Gervet, Soumith Chintala, Dhruv Batra, Jitendra Malik, and Devendra Singh Chaplot. Navigating to objects in the real world. Science Robotics, 2023.

[75] Sebastian Thrun, Maren Bennewitz, Wolfram Burgard, Armin B Cremers, Frank Dellaert, Dieter Fox, Dirk Hahnel, Charles Rosenberg, Nicholas Roy, Jamieson Schulte, et al. Minerva: A second-generation museum tour-guide robot. In ICRA, 1999.

[76] Richard A Newcombe, Shahram Izadi, Otmar Hilliges, David Molyneaux, David Kim, Andrew J Davison, Pushmeet Kohli, Jamie Shotton, Steve Hodges, and Andrew Fitzgibbon. Kinectfusion: Real-time dense surface mapping and tracking. In International Symposium on Mixed and Augmented Reality, 2011.

[77] Andrew J Davison, Ian D Reid, Nicholas D Molton, and Olivier Stasse. Monoslam: Real-time single camera slam. IEEE TPAMI, 2007.

[78] Eagle S Jones and Stefano Soatto. Visual-inertial navigation, mapping and localization: A scalable real-time causal approach. The International Journal of Robotics Research, 2011.

[79] Devendra Singh Chaplot, Kanthashree Mysore Sathyendra, Rama Kumar Pasumarthi, Dheeraj Rajagopal, and Ruslan Salakhutdinov. Gated-attention architectures for task-oriented language grounding. In AAAI, 2018.

[80] Felipe Codevilla, Matthias Müller, Antonio López, Vladlen Koltun, and Alexey Dosovitskiy. End-to-end driving via conditional imitation learning. In ICRA, 2018.

[81] Volodymyr Mnih, Koray Kavukcuoglu, David Silver, Andrei A Rusu, Joel Veness, Marc G Bellemare, Alex Graves, Martin Riedmiller, Andreas K Fidjeland, Georg Ostrovski, et al. Human-level control through deep reinforcement learning. Nature, 2015.

[82] TP Lillicrap. Continuous control with deep reinforcement learning. arXiv preprint, 2015.

[83] Yuankai Qi, Qi Wu, Peter Anderson, Xin Wang, William Yang Wang, Chunhua Shen, and Anton van den Hengel. Reverie: Remote embodied visual referring expression in real indoor environments. In CVPR, 2020.

[84] Angel Chang, Angela Dai, Thomas Funkhouser, Maciej Halber, Matthias Niessner, Manolis Savva, Shuran Song, Andy Zeng, and Yinda Zhang. Matterport3d: Learning from rgb-d data in indoor environments. In 3DV, 2017.

[85] Daniel Fried, Ronghang Hu, Volkan Cirik, Anna Rohrbach, Jacob Andreas, Louis-Philippe Morency, Taylor Berg-Kirkpatrick, Kate Saenko, Dan Klein, and Trevor Darrell. Speaker-follower models for vision-and-language navigation. In NeurIPS, 2018.

[86] Chih-Yao Ma, Jiasen Lu, Zuxuan Wu, Ghassan AlRegib, Zsolt Kira, Richard Socher, and Caiming Xiong. Self-monitoring navigation agent via auxiliary progress estimation. In ICLR, 2019.

[87] Liyiming Ke, Xiujun Li, Yonatan Bisk, Ari Holtzman, Zhe Gan, Jingjing Liu, Jianfeng Gao, Yejin Choi, and Siddhartha Srinivasa. Tactical rewind: Self-correction via backtracking in vision-and-language navigation. In CVPR, 2019.

[88] Yicong Hong, Cristian Rodriguez, Yuankai Qi, Qi Wu, and Stephen Gould. Language and visual entity relationship graph for agent navigation. In NeurIPS, 2020.

[89] Shizhe Chen, Pierre-Louis Guhur, Cordelia Schmid, and Ivan Laptev. History aware multimodal transformer for vision-and-language navigation. In NeurIPS, 2021.

[90] Jiaqi Chen, Bingqian Lin, Ran Xu, Zhenhua Chai, Xiaodan Liang, and Kwan-Yee Wong. Mapgpt: Map-guided prompting with adaptive path planning for vision-and-language navigation. In ACL, 2024.

[91] Gengze Zhou, Yicong Hong, Zun Wang, Xin Eric Wang, and Qi Wu. Navgpt-2: Unleashing navigational reasoning capability for large vision-language models. In ECCV, 2024.

[92] Xiujun Li, Chunyuan Li, Qiaolin Xia, Yonatan Bisk, Asli Celikyilmaz, Jianfeng Gao, Noah Smith, and Yejin Choi. Robust navigation with language pretraining and stochastic sampling. In EMNLP, 2019.

[93] Aishwarya Kamath, Peter Anderson, Su Wang, Jing Yu Koh, Alexander Ku, Austin Waters, Yinfei Yang, Jason Baldridge, and Zarana Parekh. A new path: Scaling vision-and-language navigation with synthetic instructions and imitation learning. In CVPR, 2023.

[94] Muhammad Zubair Irshad, Chih-Yao Ma, and Zsolt Kira. Hierarchical cross-modal agent for robotics vision-and-language navigation. In ICRA, 2021.

[95] Octo Model Team, Dibya Ghosh, Homer Walke, Karl Pertsch, Kevin Black, Oier Mees, Sudeep Dasari, Joey Hejna, Tobias Kreiman, Charles Xu, et al. Octo: An open-source generalist robot policy. In RSS, 2024.

[96] Ria Doshi, Homer Rich Walke, Oier Mees, Sudeep Dasari, and Sergey Levine. Scaling cross-embodied learning: One policy for manipulation, navigation, locomotion and aviation. In CoRL, 2024.

[97] Jonathan Yang, Catherine Glossop, Arjun Bhorkar, Dhruv Shah, Quan Vuong, Chelsea Finn, Dorsa Sadigh, and Sergey Levine. Pushing the limits of cross-embodiment learning for manipulation and navigation. arXiv preprint, 2024.

[98] Kuo-Hao Zeng, Zichen Zhang, Kiana Ehsani, Rose Hendrix, Jordi Salvador, Alvaro Herrasti, Ross Girshick, Aniruddha Kembhavi, and Luca Weihs. Poliformer: Scaling on-policy rl with transformers results in masterful navigators. In CoRL, 2024.

[99] Dhruv Shah, Ajay Sridhar, Arjun Bhorkar, Noriaki Hirose, and Sergey Levine. Gnm: A general navigation model to drive any robot. In ICRA, 2023.

[100] Ajay Sridhar, Dhruv Shah, Catherine Glossop, and Sergey Levine. Nomad: Goal masked diffusion policies for navigation and exploration. In ICRA, 2024.

[101] Pengxiang Ding, Han Zhao, Zhitao Wang, Zhenyu Wei, Shangke Lyu, and Donglin Wang. Quar-vla: Vision-language-action model for quadruped robots. In ECCV, 2024.

[102] Annie S Chen, Alec M Lessing, Andy Tang, Govind Chada, Laura Smith, Sergey Levine, and Chelsea Finn. Commonsense reasoning for legged robot adaptation with vision-language models. arXiv preprint, 2024.

[103] Yutao Ouyang, Jinhan Li, Yunfei Li, Zhongyu Li, Chao Yu, Koushil Sreenath, and Yi Wu. Long-horizon locomotion and manipulation on a quadrupedal robot with large language models. arXiv preprint, 2024.

[104] Yikai Wang, Zheyuan Jiang, and Jianyu Chen. Learning robust, agile, natural legged locomotion skills in the wild. In CoRL, 2023.

[105] Junfeng Long, Zirui Wang, Quanyi Li, Liu Cao, Jiawei Gao, and Jiangmiao Pang. Hybrid internal model: Learning agile legged locomotion with simulated robot response. In ICLR, 2024.

[106] Simar Kareer, Naoki Yokoyama, Dhruv Batra, Sehoon Ha, and Joanne Truong. Vinl: Visual navigation and locomotion over obstacles. In ICRA, 2023.

[107] Ruihan Yang, Minghao Zhang, Nicklas Hansen, Huazhe Xu, and Xiaolong Wang. Learning vision-guided quadrupedal locomotion end-to-end with cross-modal transformers. In ICLR, 2022.

[108] Chieko Sarah Imai, Minghao Zhang, Yuchen Zhang, Marcin Kierebiński, Ruihan Yang, Yuzhe Qin, and Xiaolong Wang. Vision-guided quadrupedal locomotion in the wild with multi-modal delay randomization. In IROS, 2022.

[109] Ruihan Yang, Ge Yang, and Xiaolong Wang. Neural volumetric memory for visual locomotion control. In CVPR, 2023.

[110] Takahiro Miki, Lorenz Wellhausen, Ruben Grandia, Fabian Jenelten, Timon Homberger, and Marco Hutter. Elevation mapping for locomotion and navigation using gpu. In IROS, 2022.

[111] Ji Lin, Jiaming Tang, Haotian Tang, Shang Yang, Wei-Ming Chen, Wei-Chen Wang, Guangxuan Xiao, Xingyu Dang, Chuang Gan, and Song Han. Awq: Activation-aware weight quantization for llm compression and acceleration. In MLSys, 2024.
