---
原文标题: "SpaceHopper: A Small-Scale Legged Robot for Exploring Low-Gravity Celestial Bodies"
中文译名: "SpaceHopper：用于探索低重力天体的小型腿式机器人"
来源: "IEEE International Conference on Robotics and Automation (ICRA) 2024；arXiv:2403.02831v1 [cs.RO]，2024 年 3 月 5 日"
翻译日期: "2026-09-30"
---

# SpaceHopper：用于探索低重力天体的小型腿式机器人

**作者**：Alexander Spiridonov, Fabio Buehler, Moriz Berclaz, Valerio Schelbert, Jorit Geurts, Elena Krasnova, Emma Steinke, Jonas Toma, Joschua Wuethrich, Recep Polat, Wim Zimmermann, Philip Arm, Nikita Rudin, Hendrik Kolvenbach, and Marco Hutter

**单位与致谢**：本研究由瑞士国家科学基金会（Swiss National Science Foundation）通过国家数字制造能力研究中心（NCCR dfab）部分资助。通讯作者为 Alexander Spiridonov。Jonas Toma 和 Wim Zimmermann 就职于瑞士温特图尔 ZHAW（苏黎世应用科学大学）。其余作者均就职于瑞士苏黎世联邦理工学院机器人系统实验室（Robotic Systems Lab, ETH Zurich, 8092 Zurich）。© 2024 IEEE。

## 摘要

我们提出了 SpaceHopper——一种三足小型机器人，面向未来小行星与卫星（moons）的移动探测任务。该机器人重 5.2 kg，机体尺寸为 245 mm，并采用航天级（space-qualifiable）元器件。此外，SpaceHopper 的设计与控制使其非常适合研究具有长飞行相位的动态运动模式。系统不使用陀螺仪或飞轮，而是利用其三条腿在飞行中重新调整机体姿态，为着陆做准备。我们使用深度强化学习（Deep Reinforcement Learning, DRL）策略来控制用于姿态重定向的腿部运动。在谷神星（Ceres）重力（0.029 g）的仿真中，机器人可以可靠地跳至 6 m 以内的指定位置。我们的实物实验表明，SpaceHopper 能够在旋转万向架（gimbal）中以 9.7° 以内的误差重定向到安全着陆姿态，并能在地球重力下的配重（counterweight）装置中完成跳跃。总体而言，我们认为 SpaceHopper 是迈向低重力环境下受控跳跃运动的重要一步。

**关键词**——腿式机器人（Legged Robots）、空间机器人与自动化（Space Robotics and Automation）、机器人系统工程（Engineering for Robotic Systems）

【图1：完全组装后的小型低重力机器人 SpaceHopper，标注了各部件名称（Body 机体、Hip 髋关节、Knee 膝关节、Shin 小腿、Foot 足端）与尺寸（小腿 185 mm）。该图展示了机器人的整体构型：三角形机体、三个角各安装一条腿。】

## I. 引言

小行星和卫星等低重力天体正成为越来越热门的航天任务目标。它们的物质构成在科学价值与经济价值两方面都很有意义 [1]。此外，新太空经济（Space Economy）的兴起也有望降低造访这些天体的成本——小型立方星（CubeSat）的发射对许多企业而言已经可以负担 [2]。在此背景下，我们旨在开发一种能够实现可扩展的移动式小行星探测的机器人。传统上使用的轮式运动系统，如火星"毅力号"（Perseverance）漫游车 [3] 或提议中的 MMX 漫游车 [4]，并不太适合小行星：低重力会导致车轮失去牵引力，而崎岖的地形则要求系统具备很强的适应性 [5]。其他类型的机器人，如小行星跳跃器 MASCOT [6]、JAXA 的 Minerva [7]，或腿式攀爬机器人 LEMUR [8] 和 ReachBot [9]，为微重力机动提供了替代方案。然而，它们的非关节式构型，或对专用夹持器/对接适配器的依赖，使其不太适合对小行星进行高效、大范围的探测。

另一方面，ANYmal [10] 和 Spot [11] 等动态行走机器人已在地球上展示了穿越非结构化地形的出色能力。因此，此类机器人的变体在天体移动探测方面具有很高的潜力 [12]。一些探路者项目，如 Spot Nebula [13] 和 SpaceBok [14]，已在类比场地（analog sites）进行了测试，但尚未针对航天应用进行专门设计 [15]。此外，在小行星的低重力环境中，具有长飞行相位的步态效率越来越高 [16]。与其他行走步态相比，动态跳跃运动还具有优势：它可以直接跳过障碍从而快速越过它们。但它也带来了在跳跃相位中稳定低重力下机器人姿态的挑战 [17]。传统上，空间及低重力天体上的姿态控制使用反作用轮（reaction wheels）。然而，为了节省重量并消除额外子系统的复杂性，可以省去反作用轮，仅用腿来控制机器人的姿态。每条腿仅有两个自由度（DOF）的 SpaceBok 利用这一思想，在微重力环境的平面化表示中实现了跳跃运动 [18]。

本文提出了 SpaceHopper——一种小型、轻量、可采用航天级器件的机器人，用于研究低重力场景中的受控运动。该系统以跳跃作为主要运动形式，且机器人仅利用其腿部即可在低重力下控制姿态。除展示系统的机械与电气可行性外，我们还在仿真中以及部分在实物系统上展示了 SpaceHopper 的跳跃与重定向能力。具体而言，本文的贡献如下：

- 我们提出了一种专为受控低重力运动设计的三足、立方星尺寸、轻量化机器人。
- 我们在仿真中验证了 SpaceHopper 的设计：实现了精确的低重力姿态控制，并能跳至指定位置。
- 我们借助万向架（gimbal）和配重装置（counterweight setup），在硬件上展示了二维姿态控制与垂直跳跃。

## II. 系统设计

### A. 系统概览

SpaceHopper 是一种三足机器人，作为空间低重力运动的研究平台。我们在实验室环境中对 SpaceHopper 进行了测试（见第 IV、V 节），据此估计其技术成熟度等级（TRL）为四级。机体呈三角形且对称，每个角安装一条腿（图 1）。腿完全收拢时，SpaceHopper 可以装入 27U 立方星 [19]；其 5.2 kg 的重量也显著低于 54 kg 的立方星上限。

【图2：髋关节与膝关节的剖切视图，标注了传动机构、运动方向与零部件。图中展示了髋关节的差动驱动（differential drive）布置——两台电机置于机体内，以及膝关节的直角传动（right-angled drive）。】

### B. 腿部设计

跳跃与重定向是 SpaceHopper 的主要运动目标，也是腿部设计的指导性特征。三足是 SpaceHopper 的独特之处，相比经典的四足设计可以节省重量（一条腿含全部电机重 1.17 kg）。三条腿可以实现静态站立，相比两足设计提高了稳定性。四足虽然能实现静态行走（static locomotion），但在低重力环境下该步态效率较低 [16]，并不理想。SpaceHopper 的每条腿具有三个主动自由度，因为在姿态控制上这远优于仅有两个主动自由度的腿 [18]。其中两个主动自由度位于髋部，通过差动驱动（differential drive，见 II-C 节）实现髋关节屈曲/伸展（HFE）与髋关节外展/内收（HAA）；另一个主动自由度位于膝部，实现膝关节屈曲/伸展（KFE）。膝部采用经典的直角传动，将膝关节电机高效地布置于大腿内（见图 2）。所选执行器为髋部的 Maxon EC 45 flat [20] 与膝部的 ECX Torque 22 M [21]。选择这些电机是因其高扭矩-重量/尺寸比，以及存在相同规格的航天级版本。计入传动比后的最大关节扭矩见表 I。如图 2 所示，所有直角传动均采用小齿轮-冠齿轮（pinion-crown gear）组合而非经典锥齿轮，因为小齿轮-冠齿轮组合对轴向定位公差的要求更宽松 [22]——考虑到空间中的大幅温度波动，这种自由度是有利的。

| | 膝关节 | | 髋关节 | | | |
|---|---|---|---|---|---|---|
| | 电机 | 关节 | 电机 | 俯仰与偏航（Pitch & Yaw）| 俯仰（Pitch）| 偏航（Yaw）|
| 最大扭矩 (N·m) | 0.078 | 0.740 | 0.152 | 1 | 2.8 | 1.5 |

**表 I**：所选电机可达到的最大扭矩（受绕组温度、功率与堵转扭矩限制）。

### C. 髋部设计

许多现代四足机器人，如 ANYbotics 的 ANYmal [10] 或波士顿动力的 Spot [23]，都采用串联连杆驱动链（serially linked drivetrain）。这种驱动链机械设计简单、效率高 [24]。然而，针对 SpaceHopper 在低重力环境中的特殊用途，我们基于以下考虑为髋部驱动选择了并联连杆驱动链，即差动驱动（differential drive）形式：

**1) 用于跳跃的联合扭矩**：与串联驱动链不同，差动驱动允许两台电机在所有构型下共同为俯仰（pitch）扭矩出力。SpaceHopper 可由此显著受益：跳跃依赖 HFE 运动，两台电机协同工作可提供双倍扭矩（见图 2）。对于俯仰与偏航的联合运动，扭矩按式 (1) 分配；这并不关键，因为联合运动仅出现在载荷不大的重定向过程中。

$$
\begin{pmatrix} \gamma_{h1} \\ \gamma_{h2} \end{pmatrix}
=
\begin{pmatrix} 1/(2 i_{hd}\, i_{hr}\, i_{hd}) & 1/(2 i_{hp}) \\ -1/(2 i_{hd}\, i_{hr}\, i_{hp}) & 1/(2 i_{hp}) \end{pmatrix}
\cdot
\begin{pmatrix} \tau_p \\ \tau_y \end{pmatrix} \tag{1}
$$

其中 $\gamma_{h1}$、$\gamma_{h2}$ 为两台髋部电机的扭矩，$\tau_p$、$\tau_y$ 为俯仰、偏航关节扭矩；$i_{hd}$、$i_{hr}$、$i_{hp}$ 分别为差动、直角与行星传动的传动比。

**2) 电机静态布置**：髋部采用差动驱动可将每条腿的两台电机置于机体内部。这种电机布置非常节省空间，并便于航天应用所需的热管理、防尘与线缆管理。

为在髋关节屈曲/伸展上达到与串联驱动链相同的运动范围（ROM），差动驱动与直角二级传动相配合，如图 2 所示。所得 ROM 为 $\pm 85^{\circ}$，使 SpaceHopper 能在起跳时获得更高的离地速度。髋关节外展/内收的 ROM 为 $\pm 70^{\circ}$，膝关节为 $\pm 170^{\circ}$。二级传动还允许独立微调各髋部运动的扭矩。由于跳跃需要的扭矩高于重定向，SpaceHopper 髋部俯仰运动的扭矩为偏航运动的两倍（$i_{hr} = 2$）。

### D. 机体设计

三角形机体形状在最大化偏航自由度 ROM 的同时，最小化了机体尺寸以节省重量。内部结构采用 3D 打印，具有很高的设计灵活性。得益于此，我们能够紧凑地集成机体内部部件，并使用减振器（vibration dampers）将电子设备堆栈与承力结构解耦。

### E. 材料

腿部的大部分结构件与机体的主三角形框架采用航空铝合金 7075 制造，该材料具有良好的强度-重量比，且广泛用于航天应用 [25]。小腿与机体内部电子设备结构由 3D 打印的碳纤维增强复合材料制成，在制造成本与结构强度之间取得了良好平衡。齿轮与轴分别采用硬化钢（16MnCr5 与 30CrNiMo8）制造，以承受高表面压力与弯曲载荷。最后，侧向结构由 2 mm 厚的层叠碳纤维水刀切割而成，以获得高抗拉强度与低重量。

### F. 电气系统

电子设备堆栈的中心是由 Tiny BMS s516 v2.1 电池管理系统 [26] 管理的 7S1P 锂离子电池组。我们选用锂离子电池是因其高功率-重量比。一块定制电源分配板（PDB）将电池电力分配至各电机与机载处理单元（Nvidia Jetson Nano）。一块 STM32 微控制器 [27] 连接内部温度传感器、BMS 与 Nvidia Jetson Nano；在过热或其他故障情况下，STM32 芯片会关闭系统，提高了系统的鲁棒性。我们使用 Nvidia Jetson Nano，因为它可通过 GPU 核心高效执行控制策略的推理。我们使用三台 Maxon EPOS4 Compact 24/5 EtherCAT 三轴电机控制器 [28]，它们结构紧凑并支持再生制动（regenerative braking），提高了效率并延长了任务时长。机器人还装有三个飞行时间激光测距传感器（LRF）[29]，每个最大量程 4 m，提供高度信息。

## III. 控制系统概览

### A. 控制架构

SpaceHopper 的控制框架使用共享内存缓冲区，通过机器人操作系统（ROS）[30] 与外设通信。控制框架由三部分组成：低层控制器、高层控制器与状态估计器。状态估计器接收关节状态、动作捕捉数据与激光测距传感器信息，用于估计机体的高度与姿态（见图 3）。高层控制器处理状态估计器输出的数据并计算期望关节位置。这些期望关节位置被发送至低层控制器，后者将其映射为期望电机位置，并通过 EtherCAT 网络发送给电机控制器。

【图3：SpaceHopper 重定向测试期间的数据流可视化。绿色框为运行在机载计算机上的软件模块（策略、控制器、状态估计等），黄色框为外围模块（传感器、电机控制器、动作捕捉等）。该图说明了机载/机外计算的分工及信息流向。】

### B. 运动控制器

为低重力跳跃运动开发鲁棒的控制器具有挑战性。由于飞行相位很长，起跳时机体上的微小扭矩会累积成很大的姿态变化。为了安全着陆，控制飞行相位中的机器人姿态至关重要。然而，用腿进行重定向十分困难：自由漂浮空间机械臂的运动学是非完整（nonholonomic）的，动态奇异性（dynamic singularities）会显著限制可控工作空间 [31]。已有基于模型的控制方法通过非线性优化计算近似最优轨迹，但计算速度慢且难以扩展到多条腿 [32]。另一些方法通过让腿部做小圆周运动来规避动态奇异性 [33]，但这些方案会导致重定向时间延长。另一方面，无模型深度强化学习（DRL）已在 SpaceBok 机器人的自由漂浮姿态控制中取得成功 [18]。因此，我们在这一先前成果的基础上，使用改进的近端策略优化（PPO）算法 [34], [35] 为 SpaceHopper 训练运动策略。所得运动策略为神经网络：输入观测，输出期望关节位置。策略架构为多层感知机（MLP），包含三个隐藏层，规模为 [512, 256, 128]。

通常，基于 DRL 的运动控制器在仿真中训练，再借助"仿真到现实"（sim-to-real）技术迁移至真实世界 [36]。我们在 IsaacGym 仿真环境 [37] 中训练策略，借助其 GPU 加速实现快速训练。为将策略迁移到真实机器人，我们对机器人连杆质量、质心、关节自由度摩擦以及 P&D 增益进行域随机化（domain randomization）[38]。

| 策略 | 观测 |
|---|---|
| 姿态控制（仿真） | $q,\ \dot{q},\ q_b,\ \omega_b,\ a_{t-1}$ |
| 姿态控制（万向架） | $q,\ q_b,\ \omega_b,\ a_{t-1}$ |
| 跳跃（仿真） | $q,\ \dot{q},\ r_b,\ r_b^{*},\ v_b,\ q_b,\ \omega_b,\ a_{t-1}$ |

| 奖励项 | 表达式 |
|---|---|
| orientation 3d（三维姿态） | $\lVert \mathrm{rot\,vec}(q_b) \rVert_2$ |
| orientation 2d（二维姿态） | $7 - (\lvert\theta\rvert + \lvert\phi\rvert)$ |
| action rate（动作变化率） | $\lVert a_t - a_{t-1} \rVert_2$ |
| torques（扭矩） | $\lVert \tau \rVert_2^2$ |
| dof vel（关节速度） | $\lVert \dot{q} \rVert_2$ |
| dof acc（关节加速度） | $\lVert \ddot{q} \rVert_2$ |
| collision（碰撞） | $\sum_j \mathbb{1}(\lVert f_j \rVert_2 > 0.2)$ |
| height（高度） | $\lvert r_{b,3} \rvert$ |
| pos cmd（位置指令） | $1 - \lVert r_b - r_b^{*} \rVert_2 / \lVert r_b^{*} \rVert_2$ |
| dof limits（关节限位） | $\lVert \mathrm{ReLU}(q_l - q) \rVert_1 + \lVert \mathrm{ReLU}(q - q_u) \rVert_1$ |

符号说明：$q$ 为关节位置；$\dot{q}, \ddot{q}$ 为关节速度与加速度；$r_b$ 为机体位置；$v_b$ 为机体速度；$q_b$ 为机体四元数；$\omega_b$ 为机体角速度；$a_t$ 为动作；$r_b^{*}$ 为指令机体位置；$q_l$、$q_u$ 分别为关节自由度下限与上限；$\tau$ 为关节扭矩；$f_j$ 为机体 $j$ 的接触力。

**表 II**：策略观测与奖励分量。

## IV. 姿态控制

由于低重力姿态控制是一项关键能力，我们对其单独进行了研究。第一步，我们使用 DRL 训练一个策略，使机器人在零重力自由漂浮状态下完成重定向；随后在真实系统上验证重定向能力。对于每条腿有 3 个自由度的系统，在地球重力下构建精确的低重力重定向测试颇具挑战。为此，我们开发了一套定制的万向架（gimbal）测试台，在卸载机体所受重力的同时允许其自由转动。我们还训练了一个针对该测试装置进行重定向的 DRL 策略。尽管重力卸载系统会显著改变机器人的动力学特性，但它使我们能够在姿态控制机动中测试机械、电气与控制系统，并有助于评估 sim-to-real 的表现。

### A. 仿真研究

**1) 实验设置**：由于机器人在起跳到着陆之间实际上处于失重状态，我们在仿真中让机器人漂浮在零重力环境中。机器人从一个随机初始姿态开始，重定向至直立的着陆构型。

**2) 控制器**：我们使用 DRL 策略。所有策略观测与奖励分量见表 II。训练使用的总奖励为：

$$
r = c_1 \cdot r_{\text{orientation 3d}} + c_2 \cdot r_{\text{action rate}} + c_3 \cdot r_{\text{torques}} + c_4 \cdot r_{\text{dof limits}} \tag{2}
$$

其中 $(c_1, c_2, c_3, c_4) = (-1, -0.04, -0.15, -3)$。$r_{\text{orientation 3d}}$ 惩罚非直立姿态；$r_{\text{action rate}}$ 防止关节出现高频振荡；$r_{\text{torques}}$ 鼓励策略寻找低扭矩解；$r_{\text{dof limits}}$ 惩罚接近 ROM 极限的关节位置。

**3) 结果**：训练后，机器人可以精确、快速地重定向到直立姿态。图 4 展示了机器人从随机初始姿态调整至直立的过程。该策略在 1 s 内即可达到直立姿态（见图 5 左图）。此外，姿态控制具有鲁棒性：对二十个随机初始姿态，最小角度姿态误差均值为 0.501°（见图 5 右图）。总体而言，考虑到谷神星重力（0.029 g）下跳 6 m 的距离约需 8 s（见图 8），该重定向速度足以在着陆前达到直立构型。

【图4：SpaceHopper 将自身重定向至直立姿态的连续过程快照序列；直立姿态以黑色线条标示。该图直观展示了策略驱动的腿部摆动如何带动机体逐步转正。】

【图5：仿真中 SpaceHopper 从随机初始姿态重定向至直立时机体姿态（欧拉角 x、y、z）随时间变化的曲线（左图）；以及二十个随机初始姿态下最终姿态误差的箱线图（右图）。用于量化重定向速度与精度。】

### B. 硬件测试

**1) 实验设置**：我们使用定制万向架测试 SpaceHopper 的能力，该装置允许机器人在两个自由度上自由转动。内环可转角记为 $\varphi$，外环转角记为 $\theta$（见图 6）。机器人从随机的 $\varphi$、$\theta$ 初始构型出发，需要达到直立姿态。我们使用 Vicon 动作捕捉系统跟踪机体姿态与角速度。

**2) 控制器**：我们使用 DRL 策略。总奖励为：

$$
\begin{aligned}
r = {} & c_1 \cdot r_{\text{orientation 2d}} + c_2 \cdot r_{\text{action rate}} + c_3 \cdot r_{\text{torques}} \\
& + c_4 \cdot r_{\text{dof limits}} + c_5 \cdot r_{\text{dof acc}} + c_6 \cdot r_{\text{dof vel}}
\end{aligned} \tag{3}
$$

其中 $(c_1, c_2, c_3, c_4, c_5, c_6) = (0.15, -0.06, -0.01, -1, -4\times10^{-6}, -0.01)$。$r_{\text{orientation 2d}}$ 鼓励机器人保持直立。我们引入 $r_{\text{dof vel}}$ 与 $r_{\text{dof acc}}$ 以避免 sim-to-real 问题。当机器人与自身或万向架部件发生碰撞时，环境终止。

**3) 结果**：我们通过在二十组随机万向架角 $\varphi$、$\theta$ 初始构型下释放机器人来分析 SpaceHopper 的重定向性能。SpaceHopper 能从所有构型达到直立姿态。图 7 左图显示了某一随机初始构型下的姿态变化：机器人用时 5 s 达到直立姿态。二十个随机初始构型的平均最终姿态误差为 9.7°（见图 7 右图）。尽管存在显著的动力学失配（将在 VI-C 节进一步阐述），本实验的良好结果仍是对 SpaceHopper 在未来更真实微重力实验中能力的积极预示。

【图6：安装在万向架测试台上的 SpaceHopper。内环转角 $\varphi$ 以橙色标注，外环转角 $\theta$ 以蓝色标注。该图说明重力卸载测试装置如何允许机器人两自由度转动。】

【图7：万向架中 SpaceHopper 从随机初始姿态重定向至直立时机体姿态（欧拉角 x、y、z）随时间变化曲线（左图）；二十个随机初始姿态下最终姿态误差的箱线图（右图）。】

## V. 跳跃运动

展示受控的低重力跳跃运动是 SpaceHopper 的总体目标。成功的跳跃运动需要将跳跃、姿态控制与着陆三者集成。我们首先在与谷神星（0.029 g）相同重力的仿真中展示受控跳跃运动。由于在地球重力下于真实硬件上验证该控制器需要大型测试设施 [39]，我们仅在配重装置中展示真实机器人的垂直跳跃能力。

### A. 仿真研究

**1) 实验设置**：仿真环境由平坦地面与谷神星重力构成。机器人从地面出发，被指令跳向初始位置周围半径 6 m 范围内的目标机体位置 $r_b^{*}$。

**2) 控制器**：我们提出一种端到端（end-to-end）方法，统一处理跳跃、重定向与着陆。同时为三项任务训练的 DRL 策略不受控制器间启发式切换的限制。总奖励为：

$$
\begin{aligned}
r = {} & c_1 \cdot r_{\text{pos cmd}} + c_2 \cdot r_{\text{orientation 3d}} + c_3 \cdot r_{\text{action rate}} \\
& + c_4 \cdot r_{\text{torques}} + c_5 \cdot r_{\text{collision}} + c_6 \cdot r_{\text{height}}
\end{aligned} \tag{4}
$$

各奖励分量的权重为 $(c_1, c_2, c_3, c_4, c_5, c_6) = (1.5, -0.4, -0.05, -0.4, -15, 0.19)$。其中 $r_{\text{pos cmd}}$ 鼓励缩小与目标位置的距离；$r_{\text{collision}}$ 惩罚与地面的碰撞；$r_{\text{orientation 3d}}$ 强制机体姿态直立；$r_{\text{height}}$ 激励策略探索包含跳跃的解。

**3) 结果**：如图 9 所示，该策略能端到端地完成跳跃、重定向与着陆。机器人最大飞行高度达 2.55 m，能稳定自身姿态，并在 9 s 内以足部着陆。对于 100 个距离 6 m 的随机位置指令，策略的平均位置误差为 0.316 m，最差位置误差为 0.843 m。最重要的是，机器人的机体、大腿和小腿从未与地面碰撞。图 8 验证了我们的假设：跳跃所需的俯仰扭矩高于偏航扭矩。

【图8：仿真中跳向 100 个随机位置时偏航、俯仰与膝关节扭矩的曲线。粗线为均值，阴影区域为标准差；各腿关节扭矩取了平均。机器人约在 0.4 s 时刻离地。该图用于说明跳跃中俯仰扭矩需求大于偏航扭矩，支持差动驱动设计取舍。】

【图9：谷神星重力下 SpaceHopper 跳向 6 m 外指令位置（白线标示）的连续快照。展示端到端策略的一次完整"起跳—空中重定向—着陆"过程。】

### B. 硬件测试

**1) 实验设置**：SpaceHopper 的驱动链功率不足以支持在地球上跳跃。我们使用一套简单的滑轮-配重装置，连接在机器人机体顶部以卸载机体重力。使用 3.9 kg 配重时，机体竖直方向上等效模拟 2.5 m/s² 的重力。选择该数值是为了保证机器人跳跃时不超过测试台的最大高度。

**2) 控制器**：受测试装置限制（见 VI-C 小节），我们仅验证机械与电气系统的跳跃能力。因此未采用完整的 DRL 控制方案，而是使用一个简单控制器：跟踪手工设计的关节空间轨迹，并结合激光测距传感器的高度估计。该轨迹由起跳的伸腿动作与飞行相中的收腿动作（为下一次跳跃做准备）组成；三条腿使用同一轨迹，当机器人低于某一高度时触发。

**3) 结果**：图 10 显示 SpaceHopper 跳至 1.2 m 高度，着陆后立即再次起跳。在连续跳跃模式下，SpaceHopper 至少能连续跳 4 次、最多 15 次，之后才需人工介入。失败模式源于开环控制器设计：随时间推移，微小扰动不断累积，使机器人与配重绳索产生摆动；经人工稳定摆动后，机器人可继续跳跃，最长可持续 80 min。

【图10：SpaceHopper 通过顶部滑轮系统悬挂 3.9 kg 配重进行连续跳跃的照片。说明真实硬件上垂直跳跃能力的验证装置。】

## VI. 讨论

### A. 元器件的航天适格性

如各节所述，我们在设计中面向空间应用为 SpaceHopper 选用了合适的材料（铝 7075 与碳纤维）、可航天化的电机、带冠齿轮的差动驱动设计以及锂离子电池。然而，系统尚未达到完全的航天级标准：例如电子设备未做辐射屏蔽，而足够的热防护对在太空中生存至关重要。针对月球任务的热评估可行性研究已经完成 [40]。此外，系统在测试期间依赖外部动作捕捉系统。因此需要内部状态估计，以估计机器人相对惯性系的位置与速度。目前的三个 LRF 传感器布局不足以完成该任务。融合 IMU（加速度计与陀螺仪）、相机、LRF 并执行测距-视觉-惯性里程计（range-VIO）可能是一种可行方案 [41], [42]。

### B. DRL 用于空间探测的安全性与鲁棒性

航天任务代价高昂，使安全、鲁棒的控制器成为系统的关键组成部分。标准的无模型 RL 没有理论上的安全保证。然而，正如我们的实验与先前工作 [43] 所示，DRL 控制器在实践中即使面对高度复杂的环境也表现出优秀的鲁棒性。借助域随机化等现代训练技术，所得策略可以泛化到未见过的目标环境。此外，安全强化学习（safe RL）是一个活跃的研究领域 [44]。未来，此类成果可被整合进控制方法中以获得额外的理论保证。

### C. 低重力场景的模拟

尽管万向架与配重装置使我们能够在地球重力下测试 SpaceHopper 的重定向与跳跃，但它们无法准确复现低重力环境中的机器人动力学。对这两种重力卸载系统而言，地球重力仍作用在腿上；万向架测试装置引入的额外惯量进一步改变了系统动力学。此外，万向架配平的不完美会在机器人上产生恒定扭矩，增大姿态误差并延长稳定时间。仅测试垂直跳跃也不足以验证真实硬件上的"全蹄跳"（pronking）运动。而且，快速跳跃动力学会使配重绳索松弛，引入额外误差并使 DRL 策略的 sim-to-real 迁移变得困难。未来工作中，我们计划开展抛物线飞行测试活动以克服这些限制，从而能够测试主要运动目标并提高 SpaceHopper 的技术成熟度等级（TRL）。

### D. 对不规则地形的适应

小行星的不规则地形对 MINERVA [7] 这类非关节式跳跃机器人提出了重大挑战：着陆后不可预测的弹跳严重限制了精确运动。我们假设，有肢系统可以调整腿部实现软着陆，从而获得与表面更可控的交互。未来工作需要在这一设定下验证我们的控制方法，特别是在松软、颗粒状的介质（granular media）上——这可能需要不同的足端设计。

## VII. 结论与未来工作

总之，SpaceHopper 是一个用于研究探索低重力天体（如小行星与卫星）的高动态腿式运动的研究平台。三条腿、轻量化结构、小尺寸、差动驱动链等独特设计使该系统非常适合低重力下的跳跃运动。在零重力仿真中，SpaceHopper 能在 1 s 内改变姿态；在谷神星重力仿真中，它能以 0.316 m 的平均位置误差跳至 6 m 处的指令位置。真实机器人在万向架测试台内 5 s 内达到直立姿态，平均姿态误差 9.7°；机械与电气系统支持在配重装置中反复垂直跳跃。由于 SpaceHopper 面向低重力优化的设计，在地球上构建合适的测试是一项重大挑战。本工作的自然延续是在抛物线飞行的微重力环境中测试 SpaceHopper 的能力。还需要进一步工作以展示在小行星和卫星上常见的颗粒介质（granular media）上的跳跃。最后，必须扩展并验证状态估计，使其能在目标环境中工作。

## 参考文献（原文保留）

[1] M. Elvis, "Let's mine asteroids — for science and profit," Nature, vol. 485, no. 7400, pp. 549–549, May 2012.

[2] A. M. Yazici and S. Darici, "The new opportunities in space economy," İnsan ve Toplum Bilimleri Araştırmaları Dergisi, vol. 8, no. 4, pp. 3252–3271, 2019.

[3] J. Green, "Perseverance rover and its search for life on mars," Communications of the Byurakan Astrophysical Observatory, pp. 464–469, 01 2021.

[4] H.-J. Sedlmayr, et al., "Mmx - development of a rover locomotion system for phobos," 03 2020, pp. 1–10.

[5] H. Kolvenbach, M. Breitenstein, C. Gehring, and M. Hutter, "Scalability analysis of legged robots for space exploration," in Unlocking imagination, fostering innovation and strengthening security: 68th International Astronautical Congress (IAC 2017), vol. 16. Curran, 2018, pp. 10 399–10 413.

[6] T.-M. Ho, et al., "Mascot—the mobile asteroid surface scout onboard the Hayabusa2 mission," Space Science Reviews, vol. 208, no. 1, pp. 339–374, 2017.

[7] H. Yabuta, "Arrival, touchdown and sequel to the voyage of Hayabusa2," Nature Astronomy, vol. 3, no. 4, pp. 287–289, Apr. 2019.

[8] A. Parness, N. Abcouwer, C. Fuller, N. Wiltsie, J. Nash, and B. Kennedy, "Lemur 3: A limbed climbing robot for extreme terrain mobility in space," in 2017 IEEE International Conference on Robotics and Automation (ICRA), 2017, pp. 5467–5473.

[9] T. G. Chen, et al., "Reachbot: A small robot with exceptional reach for rough terrain," in 2022 International Conference on Robotics and Automation (ICRA), 2022, pp. 4517–4523.

[10] M. Hutter, et al., "Anymal - toward legged robots for harsh environments," Advanced Robotics, vol. 31, no. 17, pp. 918–931, 2017. [Online]. Available: https://doi.org/10.1080/01691864.2017.1378591

[11] A. Bouman, et al., "Autonomous spot: Long-range autonomous exploration of extreme environments with legged locomotion," in 2020 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2020, pp. 2518–2525.

[12] H. Kolvenbach, "Quadrupedal robots for planetary exploration," Ph.D. dissertation, ETH Zurich, 2021.

[13] A. Agha, et al., "Nebula: Quest for robotic autonomy in challenging environments; TEAM costar at the DARPA subterranean challenge," CoRR, vol. abs/2103.11470, 2021. [Online]. Available: https://arxiv.org/abs/2103.11470

[14] P. Arm, et al., "Spacebok: A dynamic legged robot for space exploration," in 2019 International Conference on Robotics and Automation (ICRA), 2019, pp. 6288–6294.

[15] H. Kolvenbach, et al., "Traversing steep and granular martian analog slopes with a dynamic quadrupedal robot," in Field Robotics, 2022.

[16] H. Kolvenbach, C. D. Bellicoso, F. Jenelten, L. Wellhausen, and M. Hutter, "Efficient gait selection for quadrupedal robots on the moon and mars," in 14th International Symposium on Artificial Intelligence, Robotics and Automation in Space (i-SAIRAS 2018). ESA Conference Bureau, 2018.

[17] H. Kolvenbach, E. Hampp, P. Barton, R. Zenkl, and M. Hutter, "Towards jumping locomotion for quadruped robots on the moon," in IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2019, pp. 5459–5466.

[18] N. Rudin, H. Kolvenbach, V. Tsounis, and M. Hutter, "Cat-like jumping and landing of legged robots in low-gravity using deep reinforcement learning," CoRR, vol. abs/2106.09357, 2021. [Online]. Available: https://arxiv.org/abs/2106.09357

[19] "Cubesat - deployer standards," https://www.eoportal.org/other-space-activities/cubesat-deployer-standards, Last accessed: 05.09.2023.

[20] "Ec 45 flat 42.8 mm, brushless, 50 watt, with hall sensors," https://www.maxongroup.com/maxon/view/product/motor/ecmotor/ecflat/ecflat45/651610, Last accessed: 07.09.2023.

[21] "Ecx torque 22 m 22 mm, brushless, with hall sensors," https://www.maxongroup.com/maxon/view/product/motor/ecmotor/ECX/ECX22/ECXI22M4ZF46C4IL1Y479A, Last accessed: 07.09.2023.

[22] U. Kissling and S. Beermann, "Face gears: Geometry and strength," Gear Technol, vol. 1, no. 2, pp. 54–61, 2007.

[23] "Spot, boston dynamics," https://www.bostondynamics.com/products/spot, Last accessed: 08.03.2023.

[24] A. Abate, J. W. Hurst, and R. L. Hatton, "Mechanical antagonism in legged robots." in Robotics: Science and Systems, vol. 6. Ann Arbor, MI, 2016.

[25] "NASA - Materials Data Handbook - Aluminum Alloy 7075," https://ntrs.nasa.gov/citations/19720022809, Last accessed: 15.09.2023.

[26] "Battery management system (bms) 30a," https://enepaq.com/product/battery-management-system-bms-30a/, Last accessed: 05.09.2023.

[27] "Stm32g431kb," https://www.st.com/en/microcontrollers-microprocessors/stm32g431kb.html, Last accessed: 05.09.2023.

[28] "Epos4 compact 24/5 ethercat 3-axes, digital positioning controller, 5 a per axis, 10 - 24 vdc," https://www.maxongroup.com/maxon/view/product/control/Positionierung/684519, Last accessed: 07.09.2023.

[29] "Time-of-flight (tof) ranging sensor with advanced multi-zone and multi-object detection," https://www.st.com/en/imaging-and-photonics-solutions/vl53l1.html, Last accessed: 07.09.2023.

[30] M. Quigley, et al., "Ros: an open-source robot operating system," in ICRA workshop on open source software, vol. 3, no. 3.2. Kobe, Japan, 2009, p. 5.

[31] E. G. Papadopoulos, Nonholonomic Behavior in Free-floating Space Manipulators and its Utilization. Boston, MA: Springer US, 1993, pp. 423–445. [Online]. Available: https://doi.org/10.1007/978-1-4615-3176-0_11

[32] C. Fernandes, L. Gurvits, and Z. Li, "Attitude control of space platform/manipulator system using internal motion," in Proceedings 1992 IEEE International Conference on Robotics and Automation, 1992, pp. 893–898 vol.1.

[33] Z. Vafa and S. Dubowsky, On the Dynamics of Space Manipulators Using the Virtual Manipulator, with Applications to Path Planning. Boston, MA: Springer US, 1993, pp. 45–76. [Online]. Available: https://doi.org/10.1007/978-1-4615-3588-1_3

[34] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, "Proximal policy optimization algorithms," CoRR, vol. abs/1707.06347, 2017. [Online]. Available: http://arxiv.org/abs/1707.06347

[35] N. Rudin, D. Hoeller, P. Reist, and M. Hutter, "Learning to walk in minutes using massively parallel deep reinforcement learning," CoRR, vol. abs/2109.11978, 2021. [Online]. Available: https://arxiv.org/abs/2109.11978

[36] W. Zhao, J. P. Queralta, and T. Westerlund, "Sim-to-real transfer in deep reinforcement learning for robotics: a survey," CoRR, vol. abs/2009.13303, 2020. [Online]. Available: https://arxiv.org/abs/2009.13303

[37] V. Makoviychuk, et al., "Isaac gym: High performance gpu-based physics simulation for robot learning," CoRR, vol. abs/2108.10470, 2021. [Online]. Available: https://arxiv.org/abs/2108.10470

[38] J. Tobin, R. Fong, A. Ray, J. Schneider, W. Zaremba, and P. Abbeel, "Domain randomization for transferring deep neural networks from simulation to the real world," CoRR, vol. abs/1703.06907, 2017. [Online]. Available: http://arxiv.org/abs/1703.06907

[39] O. Bekdash, et al., "Development and evaluation of the active response gravity offload system as a lunar and martian eva simulation environment." 2020 International Conference on Environmental Systems, 2020.

[40] M. Trentini, P. Arm, G. Valsecchi, H. Kolvenbach, and M. Hutter, "Concept study of a small-scale dynamic legged robot for lunar exploration," in IAC-23: IAF SPACE EXPLORATION SYMPOSIUM. BCC B3: IAF, October 3 2023, paper code: IAC-23,A3,2B,7,x78250; Session: 2B. Moon Exploration – Part 2. [Online]. Available: https://iafastro.directory/iac/paper/id/78250/summary/

[41] J. Delaune, D. S. Bayard, and R. Brockers, "Range-visual-inertial odometry: Scale observability without excitation," CoRR, vol. abs/2103.15215, 2021. [Online]. Available: https://arxiv.org/abs/2103.15215

[42] B. Balaram, et al., "Mars helicopter technology demonstrator," in 2018 AIAA Atmospheric Flight Mechanics Conference, 2018, p. 0023.

[43] N. Rudin, D. Hoeller, M. Bjelonic, and M. Hutter, "Advanced skills by learning locomotion and local navigation end-to-end," in 2022 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS), 2022, pp. 2497–2503.

[44] S. Gu, et al., "A review of safe reinforcement learning: Methods, theory and application," 2023.



