---
原文标题: Towards Low-Gravity Planetary Exploration using Reinforcement Learning for Walking, Jumping, and In-flight Attitude Control
中文译名: 面向低重力行星探测的强化学习行走、跳跃与飞行中姿态控制
来源/arXiv: arXiv:2605.24643v1 [cs.RO]（2026年5月23日）
翻译日期: 2026-09-30
---

# 面向低重力行星探测的强化学习行走、跳跃与飞行中姿态控制

**Jørgen Anker Olsen 和 Kostas Alexis**

作者单位：挪威科技大学（NTNU）自主机器人实验室（Autonomous Robots Lab），地址：O.S. Bragstads Plass 2D, 7034, 挪威特隆赫姆。邮箱：jorgen.a.olsen@gmail.com
主页：https://ntnu-arl.github.io/olympus/

## 摘要

本文提出了用于行星探测场景中动态四足运动的强化学习（reinforcement learning, RL）策略。基于一个采用五杆（5-bar）腿构型、经任务优化的四足机器人，我们开发了行走、垂直跳跃、前向跳跃以及飞行中姿态控制的 RL 策略，这些策略专门针对火星上较低的重力环境而定制。这些策略使此类机器人能够通过协调的跳跃与精确的飞行中重定向（in-flight reorientation）来克服比自身更大的障碍，从而实现安全着陆。我们在 Olympus 四足机器人上通过单轴重定向测试演示了姿态控制策略的仿真到实物迁移（Sim2Real transfer），而所有运动策略均在仿真中进行了验证。一个完整的火星探测任务场景展示了在复杂地形上的多策略协调部署。实验结果表明，机器人可在 2.6 秒内完成 90° 的姿态重定向；仿真结果则表明在火星重力条件下可实现 3.1 米的垂直跳跃和 3.9 米的前向跳跃。

– 补充视频：https://www.youtube.com/watch?v=qlSJ3P87A4A

**关键词：** 跳跃（Jumping）、四足机器人（Quadruped）、飞行中姿态控制（In-Flight Attitude Control）

## 1 引言

传统的太空探测一直由巡视器（rover）和着陆器（lander）构型主导，这是因为它们在月球和火星上部署并回传科学图像与数据方面取得了历史性成功 [1,2]。轮式设计使其能够高效探索月球和行星表面较平坦的区域，但在陡峭斜坡、松软土壤和带有大型障碍物的崎岖地形上可能会举步维艰 [3]。然而，许多具有科学价值的区域位于巡视器难以抵达之处。一个重要的例子是熔岩管（lava tube），它被认为集科学、探测与资源三大价值于一体 [4,5]。这促使人们采用能够为机器人探测带来显著优势的替代构型 [3]。

腿式机器人（legged robot）提供了一种有前景的解决方案，近年来其能力和鲁棒性已有了显著提升 [6]。火星（3.71 m/s²）或其他行星体如月球（1.62 m/s²）的低重力环境尤其有利于动态运动：在地球上具有挑战性的跳跃机动变得可行，使机器人能够克服远大于其体型的障碍物 [7]。一些概念方案甚至提出将连续跳跃作为主要运动方式 [8]。然而，控制这些动态行为带来了重大挑战。跳跃需要在起跳、飞行中姿态控制和协调着陆各个阶段进行精确配合，同时还要适应不平整的地形和可能松软的土壤。飞行过程中三维姿态重定向的复杂性以及接触时序的不确定性，使得经典控制方法难以奏效 [8,7,9]。

【图1：站立在火星类似环境中的 Olympus 机器人。该图展示了 Olympus 四足机器人在一个模拟火星表面环境（红色沙石地形）中的实物照片，用于说明本文所研究机器人在行星探测场景中的形态。】

在前期 Olympus 工作（图1）的基础上——Olympus 是一个为低重力环境中强力跳跃与飞行中姿态控制而优化的四足平台 [10]——我们研究使用深度强化学习（deep reinforcement learning, DRL）在火星地形上实现高动态四足运动。我们的贡献包括：

- 一种基于 DRL 的姿态控制策略，能够实现快速的飞行中重定向以确保安全着陆；在机器人硬件实验验证中，可在 2.6 秒内完成 90° 旋转。
- 针对火星重力条件训练的行走、垂直跳跃与前向跳跃 DRL 策略。仿真表明在火星重力下可实现最高 3.1 米的垂直跳跃和最高 3.9 米的水平跳跃。对可选的并联弹簧辅助（parallel spring assistance）的研究表明其能够增加跳跃高度与距离。
- 一种分层策略部署框架（hierarchical policy deployment framework），通过在行星探测场景中协调执行多个策略，使机器人能够穿越显著大于自身体型的障碍物。

本文其余部分组织如下：第 2 节回顾相关工作；第 3 节介绍 Olympus 四足机器人；第 4 节详述电机与弹簧模型；第 5 节概述训练方法；第 6 节展示仿真结果；第 7 节给出姿态控制策略的实验验证；第 8 节介绍行星探测流程；第 9 节给出结论。

## 2 相关工作

着陆器、巡视器以及近期的直升机已被证明是机器人太空探测中非常成功的方案 [11]。与此同时，一些采用独特机器人的替代方案也被提出用于行星表面与地下探测，其中包括腿式机器人 [3,12]。跳跃式腿式机器人也已被提出，近期工作已能够利用强化学习控制器实现此类运动能力 [8]。跳跃式腿式机器人在此类任务中的一个关键优势是其能够跃过比自身更大的障碍物，尤其是在火星等低重力环境中。传统机器人与直升机可能难以胜任的特别受关注的区域，包括火星熔岩管（Martian Lava Tube）以及高海拔崎岖地形 [7]。

除巡视器和直升机等成熟平台 [13] 之外，为行星探测提出的机器人系统还包括坑洞机器人（pit-bot）[14] 与腿式机器人 [3,5]。在这些新兴平台中，腿式系统因其离散的落脚点选择能力以及能够克服比传统巡视器更大的障碍物，特别适合复杂地形。在充满挑战的行星探测场景中，要在此类系统上实现鲁棒运动，需要先进的控制策略。

强化学习已成为控制复杂四足行为的有力方法 [15]。近期的进展包括极其鲁棒的行走策略 [16]，以及跳跃 [9,17] 和姿态控制 [8,18] 等任务的进步。

在 [8,7,9] 的工作与思想基础上，我们提出了一组用于行走、垂直跳跃、前向跳跃与姿态控制的高性能 DRL 策略。这些策略在分层的、依任务切换的状态机（state machine）中组合使用时，展示了四足机器人 Olympus 的能力，以及跳跃式腿式机器人在低重力行星探测中的潜力。

## 3 行星探测系统

本节介绍机器人本体、设计优化过程、最终硬件参数以及机载控制架构。

### 3.1 机器人设计与优化

四足机器人 Olympus 专为火星重力环境中的动态运动而设计。其每条腿具有三个自由度，五杆腿构型既为飞行中姿态控制提供了足够大的工作空间，也赋予了出色的跳跃能力。机器人可选用并联弹簧以辅助跳跃机动（非必需）。设计优化的目标是在保持火星重力条件下动态行走能力的同时，最大化跳跃性能与重定向能力。优化过程在形态设计空间上进行网格搜索（grid search），变化身体尺寸与腿部参数。搜索的身体尺寸包括体长 $l_{body}$、前腿间距 $w_{body,f}$ 与后腿间距 $w_{body,b}$。五杆腿的参数搜索空间包括连杆长度 $l_1$ 至 $l_4$ 以及弹簧刚度 $k$。网格搜索优先考虑垂直跳跃高度、水平跳跃距离与角重定向速率。优化方法与设计空间探索的完整细节见文献 [7]。机器人最终优化参数列于表 1，并在图 2 中结合机器人结构加以标注；其中对每条腿，$\theta_l$ 为侧向电机角度（lateral motor angle），$\theta_{ot}$ 为外横向电机角度（outer transversal motor angle），$\theta_{it}$ 为内横向电机角度（inner transversal motor angle）。

机器人质量为 14.5 kg，总身长 0.67 m，由 12 台 CubeMars 力矩控制无刷直流电机驱动（侧向关节用 AK80-9，横向关节用 AK70-10）。侧向电机最大扭矩为 $\tau_{max,l} = 18.0\ \mathrm{N\,m}$，横向电机最大扭矩为 $\tau_{max,t} = 24.8\ \mathrm{N\,m}$。五杆连杆腿构型允许选用集成在腿内的弹簧，弹簧通过绳索经五杆腿膝关节处的滑轮连接，可在跳跃中提升能量输出，并在着陆时提供柔顺性与储能。除非另有说明，所有实验均使用不安装弹簧的机器人构型。

【图2：Olympus 结构设计图，标注了身体与腿部参数。图中以示意图形式标注了体长 $l_{body}$、前腿间距 $w_{body,f}$、后腿间距 $w_{body,b}$，五杆腿连杆 $l_1$–$l_4$、内外横向电机角 $\theta_{it}$、$\theta_{ot}$、膝关节位置以及可选弹簧（Optional Springs）的布置方式。】

**表 1. 优化后的身体与腿部参数**

| 参数 | 符号 | 数值 |
|---|---|---|
| 前后腿距离 | $l_{body}$ | 0.6 m |
| 前腿间距 | $w_{body,f}$ | 0.21 m |
| 后腿间距 | $w_{body,b}$ | 0.3 m |
| 连杆 0 长度 | $l_0$ | 0.09 m |
| 连杆 1 和 2 长度 | $l_1$ & $l_2$ | 0.175 m |
| 连杆 3 和 4 长度 | $l_3$ & $l_4$ | 0.3 m |
| 弹簧刚度 | $k$ | 800 N/m |

### 3.2 机载控制架构

部署的控制架构以闭环方式运行（图 3）：策略接收任务相关（即前向/垂直跳跃、行走、姿态机动）的观测 $o$ 并输出动作 $a$。动作经重新缩放与偏移，以默认关节角 $\theta_{m,def}$ 为中心，产生电机目标角 $\theta_{m,target}$。按任务分别施加的缩放为：行走对所有电机使用 60°；姿态控制对所有电机使用 90°；跳跃对侧向电机使用 15°、对横向电机使用 90°。所有侧向与横向电机的默认角度分别为 $\theta_{l,def} = 0°$ 与 $\theta_{t,def} = 45°$。为确保安全运行，目标角经安全过滤器（safety filter）处理，产生安全的电机目标角 $\theta_{m,safe}$。随后 PD 电机控制器跟踪这些滤波后的角度，生成下发给执行器的参考力矩 $\tau_{t+1}$。该控制架构在仿真与硬件实验中完全一致。仿真中由 NVIDIA Isaac Lab 直接提供全部状态；硬件上策略推理在 NVIDIA Jetson Orin NX 机载计算机上以 60 Hz 运行，从 Vicon 动作捕捉（motion capture, MoCap）系统接收当前机体系姿态 $q_B^I$ 与角速度 $\omega_B$，并直接从电机读取关节角 $\theta_m$ 与角速度 $\dot{\theta}_m$，其中 $B$ 为机体系、$I$ 为惯性系。

【图3：机器人与仿真中的控制器架构图。图中展示策略推理（60 Hz）输出动作 $a$，经缩放与偏移（Scale & offset，围绕默认角 $\theta_{m,def}$）得到电机目标角 $\theta_{m,target}$，再经安全过滤器得到 $\theta_{m,safe}$，由 PD 控制器（500 Hz）输出力矩 $\tau_{t+1}$ 驱动机器人；并列出各策略的观测构成——所有策略共有：关节位置、关节速度、前一动作、机体角速度；姿态控制：四元数误差、投影重力；运动策略：机体线速度；前向跳跃：跳跃目标、机体高度；垂直跳跃：目标跳跃高度、机体高度、跳跃触发；行走：线速度指令、偏航速率指令。状态来自 MoCap 或仿真器。】

## 4 仿真设置

### 4.1 电机模型

仿真中的电机控制结合了带饱和的 PD 控制模型与零阶转矩-转速特性模型。PD 控制器基于位置误差生成期望力矩，同时受公式 (1) 所描述的电机物理转矩-转速极限约束：

$$
|\tau| \leq \tau_{max}(\dot{\theta}) = \begin{cases}
\tau_{max} & \text{若 } |\dot{\theta}| \leq \dot{\theta}_{cut} \\[4pt]
\tau_{max}\left(1 - \dfrac{|\dot{\theta}| - \dot{\theta}_{cut}}{\dot{\theta}_{no\text{-}load} - \dot{\theta}_{cut}}\right) & \text{若 } \dot{\theta}_{cut} < |\dot{\theta}| < \dot{\theta}_{no\text{-}load} \\[8pt]
0 & \text{若 } |\dot{\theta}| \geq \dot{\theta}_{no\text{-}load}
\end{cases} \tag{1}
$$

其中 $\tau$ 为仿真中施加的电机力矩，无论 PD 控制器期望输出如何，均受电机转矩-转速曲线限制；$\tau_{max}$ 为零转速下的额定电机力矩；$\dot{\theta}$ 为关节角速度；$\dot{\theta}_{cut}$ 为可获得全部力矩的截止转速；$\dot{\theta}_{no\text{-}load}$ 为力矩降为零的空载转速。模型参数取自制造商规格；在姿态控制策略训练时采用了更保守的空载转速，以确保更安全的运动——因为部署期间腿部几乎不受外力，可能导致极快的运动。

### 4.2 安全约束

仿真中为辅助训练施加了三项执行器约束：1) 任务相关的力矩饱和，$\tau_{max,task}$ 为给定任务允许的最大力矩，因各任务所需最大力矩不同；行走设为 10 N·m，姿态控制设为 12 N·m，跳跃则使用电机所能提供的最大力矩。2) 受文献 [8] 启发，我们对姿态控制施加速度相关的制动约束：当关节速度幅值 $|\dot{\theta}|$ 超过设定安全阈值 $\dot{\theta}_{safe}$ 时限制力矩施加，只允许产生与运动方向相反的耗散力矩，以防关节速度过大。此约束仅在仿真中针对姿态控制施加。3) 施加关节角限位以防止机械自碰撞，即硬位置约束 $\theta_{min} \leq \theta_m \leq \theta_{max}$，其中 $\theta_{min}$、$\theta_{max}$ 分别为关节角下限与上限。此外，五杆连杆几何要求对横向关节施加耦合约束：$\theta_l \leq \theta_{it} + \theta_{ot} \leq \theta_u$，其中 $\theta_l$、$\theta_u$ 分别为横向角之和的下限与上限。这些角度约束通过第 3 节所述的安全过滤器，在仿真与实物上同时强制执行。

### 4.3 五杆弹簧模型

Olympus 四足机器人可集成并联弹簧：弹簧在腿部压缩时储能、在跳跃时释放能量以提升跳跃高度。仿真中将其建模为连接每条五杆腿机构两膝关节的虚拟弹簧，弹簧力以附加力矩 $\tau_{spring}$ 的形式作用于电机关节。总关节力矩 $\tau_{total}$ 由主动力矩 $\tau_{motor}$ 与被动弹簧力矩叠加而成：

$$
\tau_{total} = \tau_{motor} + \tau_{spring} \tag{2}
$$

弹簧模型采用拉伸弹簧（extension spring），其力与膝-膝距离超出其原长的伸长量成正比，膝-膝距离通过五杆连杆的正运动学（forward kinematics）计算。弹簧力矩由雅可比转置（Jacobian transpose）将弹簧力映射到关节力矩获得。由于物理弹簧设计 [10] 的原因，该模型在深蹲运动中基于组合角 $\theta_{combined} = \theta_{it} + \theta_{ot}$ 表现出两段式行为：第一段作用于 $\theta_{combined} \in [0°, 180°]$，第二段作用于 $\theta_{combined} \in [180°, 240°]$。力矩定义为：

$$
\tau_{spring} = \begin{cases}
J^T(\theta)\, F_{spring} & \text{若 } \theta_{combined} \leq 180° \\
F_{spring}\, r(\theta_{combined}) & \text{若 } \theta_{combined} > 180°
\end{cases} \tag{3}
$$

其中 $J^T(\theta)$ 为将弹簧力映射为关节力矩的腿雅可比转置，$F_{spring}$ 为弹簧力向量，$r(\theta_{combined})$ 为深度压缩时随角度变化的力臂——此时弹簧附着点相当于缠绕在电机轴上的滑轮。弹簧机构如图 2 所示。

## 5 DRL 流程

本节介绍所开发策略的强化学习训练方法。所有策略的奖励函数均为多个奖励项的加权和。行走、垂直跳跃与前向跳跃策略以及参考状态初始化（reference state initialization）方案建立在文献 [9] 所提框架之上，并针对火星重力运行做了适配，观测与完整奖励描述亦沿用该框架。姿态控制器在文献 [7] 的基础上进行了改进。各策略在训练与部署期间使用的不同观测如图 3 所示，奖励列于表 2。所有策略还施加正则化奖励（regularization rewards），以鼓励更平滑、更安全的运动。

### 5.1 姿态控制

姿态控制策略 $\pi_{AC}$ 的目标是利用腿部作为反作用质量（reaction mass）并改变机器人转动惯量来控制机体姿态。观测向量为：

$$
o = [q_B^R \quad \omega_B \quad \theta_m \quad \dot{\theta}_m \quad a_{t-1}], \tag{4}
$$

其中四元数误差 $q_B^R = (q_B^I)^* \otimes q_R^I$ 表示当前机体姿态 $q_B^I$ 与期望姿态 $q_R^I$ 之间的相对姿态（$R$ 表示参考坐标系），使用四元数共轭 $(\cdot)^*$ 与四元数乘法 $(\otimes)$ 计算；$a_{t-1}$ 为前一时刻动作。

表 2 列出了奖励组成。主要奖励项为四元数误差奖励，它使用两个不同宽度的核函数，分别提供细粒度（$\sigma_1$）与粗粒度（$\sigma_2$）的姿态反馈，策略因将误差驱动至零而受奖。记 $r_{q1} = \phi_{\sigma_1}(q_B^R)$ 为窄核的激活值，用于仅在接近目标姿态时有条件地启用次级奖励。机体角速度奖励通过奖励与来自 $q_B^R$ 的旋转轴 $\varphi$ 对齐的角速度来鼓励旋转运动；当 $q_B^R < 5°$ 时该奖励关闭，以便收敛。稳定性奖励鼓励接近目标时保持低角速度。着陆位置奖励驱动侧向与横向关节趋向默认角，为着陆准备好腿部构型，其中 $\theta_l \in \mathbb{R}^4$、$\theta_t \in \mathbb{R}^8$ 分别表示四条腿全部侧向与横向关节角向量。对称性奖励鼓励协调的腿部运动：侧向对称项奖励每侧前、后腿侧向关节角的相似性（左侧为 $\theta_{l,FL}$ 与 $\theta_{l,BL}$，右侧为 $\theta_{l,FR}$ 与 $\theta_{l,BR}$），横向对称项奖励所有内、外横向关节（$\theta_{it}$ 与 $\theta_{ot}$）的相似性。发生自碰撞时回合终止。与文献 [7] 的关键区别在于：更关注快速重定向；引入对称性奖励（鼓励前后侧向匹配与内外横向匹配）以获得更干净的运动；以及引入着陆构型奖励，为与跳跃策略协同的实际飞行使用做准备。另外，部署时当姿态误差较小（5° 以内）时，在默认关节位置与指令关节位置之间施加线性插值以减少振荡 [18]。

### 5.2 行走

行走策略的主要奖励跟踪指令线速度 $c_{xy}$ 与偏航角速度 $\omega_z^*$，分别对应机器人 xy 平面速度 $v_{xy}$ 与角速度 $\omega_z$。次级奖励惩罚竖直速度 $v_z$、侧向角速度 $\omega_{xy}$、机体倾斜（通过投影重力 $g_{xy}$），并驱动侧向与横向关节角趋向期望角（$\theta_t^*$、$\theta_l^*$）。该策略直接在火星重力下用此奖励结构训练，并相对于地球重力基线增加了正则化、调整了奖励权重。

### 5.3 垂直跳跃

垂直跳跃策略在收到跳跃触发信号后跟踪指令跳跃高度 $h^*$。该策略针对火星重力训练，并在地球重力奖励结构基础上做了修改。主要奖励修改包括：高度缩放以强调在更大量级上达到目标高度 $h^*$；更宽的核容差 $\sigma$ 以反映更高的跳跃高度；以及放宽终止条件，以允许在精细调整精度之前先对高跳跃进行早期探索。高度奖励将实际达到的最大高度 $h_m$ 与 $h^*$ 比较评估；估计高度奖励则在飞行中利用基于抛体运动（projectile motion）的估计 $\hat{h}_m$ 提供连续反馈。对称性奖励奖励关节对称性。公共跳跃奖励鼓励软着陆并惩罚不希望的运动。软着陆（Soft impact）奖励通过惩罚沿归一化速度方向 $\tilde{v}$ 上超过阈值 $a_{body,max}$ 的机体加速度 $a_{body}$ 来鼓励更柔和的着陆。其他公共奖励惩罚机体角速度、姿态误差与过大的地面力 $F_{ground}$，同时鼓励电机目标 $\theta_m^*$ 跟踪，并通过截断的竖直速度与阻尼关节运动鼓励软着陆。

**表 2. 全部策略的奖励公式。** 记号约定：$\phi_\sigma(x) := \exp(-\frac{x^2}{\sigma^2})$，$\psi_\sigma(x) := \exp(-\frac{|x|}{\sigma})$。

**姿态控制（Attitude Control）**

| 奖励项 | 表达式 |
|---|---|
| 四元数误差（Quaternion error） | $\phi_{\sigma_1}(q_B^R) + 0.6\,\phi_{\sigma_2}(q_B^R)$ |
| 机体角速度（Body ang. vel.） | $\frac{\omega_B \cdot \varphi}{\|\varphi\|}$（当 $q_B^R \geq 5°$） |
| 稳定性（Stability） | $\phi_{\sigma_3}(\|\omega_B\|^2)\, r_{q1}$ |
| 着陆侧向（Landing lateral） | $\phi_{\sigma_3}(\|\theta_l - \theta_{l,def}\|)\, r_{q1}$ |
| 着陆横向（Landing transversal） | $\phi_{\sigma_4}(\|\theta_t - \theta_{t,def}\|^2)\, r_{q1}$ |
| 对称性侧向（Symmetry lateral） | $\phi_{\sigma_5}(\|\theta_{l,BL} - \theta_{l,FL}\| + \|\theta_{l,BR} - \theta_{l,FR}\|)$ |
| 对称性横向（Symmetry transversal） | $\phi_{\sigma_6}(\|\theta_{it} - \theta_{ot}\|)$ |

**行走（Walking）**

| 奖励项 | 表达式 |
|---|---|
| 线速度误差（Linear vel. error） | $\phi_{\sigma_7}(\|v_{xy} - c_{xy}\|)$ |
| 偏航速率（Yaw rate） | $\phi_{\sigma_8}(\omega_z - \omega_z^*)$ |
| 竖直速度（Vertical vel.） | $v_z^2$ |
| 侧向稳定性（Lateral stability） | $\|\omega_{xy}\|^2$ |
| 姿态水平（Flat） | $\|g_{xy}\|^2$ |
| 站立（Stand） | $\phi_{\sigma_9}(\|\theta_t - \theta_t^*\|)$ |
| 侧向位置（Lateral pos.） | $\phi_{\sigma_{10}}(\|\theta_t - \theta_t^*\|^4)$ |
| 横向位置（Transversal pos.） | $\phi_{\sigma_{11}}(\|\theta_l - \theta_l^*\|^{10})$ |

**垂直跳跃（Vertical Jump）**

| 奖励项 | 表达式 |
|---|---|
| 高度（Height） | $\phi_{\sigma_{12}}(h_m - h^*) + 3\,\psi_{\sigma_{13}}(h_m - h^*)$ |
| 估计高度（Est. height） | $\phi_{\sigma_{14}}(\hat{h}_m - h^*) + 3\,\psi_{\sigma_{15}}(\hat{h}_m - h^*)$ |
| 对称性（Symmetry） | $\phi_{\sigma_{16}}(\mathrm{Var}(\theta_t)) + \phi_{\sigma_{17}}(\|\theta_l\|)$ |

**前向跳跃（Forward Jump）**

| 奖励项 | 表达式 |
|---|---|
| 跟踪（Tracking） | $\phi_{\sigma_{18}}(|e|)$ |
| 估计跟踪（Est. tracking） | $\phi_{\sigma_{19}}(|\hat{e}|) + 0.1\,\phi_{\sigma_{20}}(\hat{e})$ |
| 对称性（Symmetry） | $\phi_{\sigma_{21}}(\|\theta_{t,L} - \theta_{t,R}\|)$ |

**公共跳跃奖励（Common Jumping Rewards）**

| 奖励项 | 表达式 |
|---|---|
| 角速度（Angular vel.） | $\phi_{\sigma_{22}}(\|\omega_B\|)$ |
| 关节位置（Joint pos.） | $\phi_{\sigma_{23}}(\|\theta_m - \theta_m^*\|)$ |
| 姿态误差（Orient. error） | $\phi_{\sigma_{24}}(q_B^R)^2$ |
| 地面力（Ground force） | $\|F_{ground}\|^2$ |
| 软着陆（Soft impact） | $\max\!\big(0,\ 1 - |\min(0, \frac{a_{body}}{a_{body,max}} \cdot \tilde{v})|\big)$ |
| 缓冲着陆（Catch landing） | $\mathrm{clamp}(-v_z, 0, 1)$ |
| 阻尼着陆（Damp landing） | $\mathrm{clamp}(\dot{\theta}_t, 0, 1)$ |

**正则化奖励（Regularization Rewards，所有策略共用）**

| 奖励项 | 表达式 |
|---|---|
| 动作变化率（Action rate） | $\|a(t) - a(t-1)\|^2$ |
| 动作裁剪（Action clip） | $\|\theta_{m,target} - \theta_{m,safe}\|^2$ |
| 关节加速度（Joint acceleration） | $\|\ddot{\theta}\|^2$ |
| 关节力矩（Joint torque） | $\|\tau\|^2$ |

### 5.4 前向跳跃

前向跳跃策略跟踪 xy 平面内的指令目标位置，并针对火星重力训练，奖励修改考虑了更低的重力与更长的飞行时间。主要奖励修改包括距离缩放与反映更大跳跃距离的更宽核容差。跟踪（Tracking）奖励鼓励最小化当前机器人位置与目标位置之间的水平跟踪误差 $e$；估计跟踪（Est. tracking）在飞行中基于抛体运动使用估计的着陆误差 $\hat{e}$。对称性奖励通过惩罚左右腿横向关节角（$\theta_{t,L}$ 与 $\theta_{t,R}$）之差来鼓励对称运动。

### 5.5 训练期间的初始化

学习执行大幅跳跃的过程具有挑战性，因为策略的规划时域远短于完成跳跃并达到目标高度或目标着陆位置所需的时间。因此，训练采用了一套完整的、基于课程学习（curriculum）的参考状态初始化（reference state initialization）策略，以帮助智能体学习正确的跳跃行为。这对在跳跃的地面相与飞行相中把智能体推向期望状态都是必要的。智能体被初始化在跳跃机动的不同阶段：站立、下蹲、飞行中以及触地前瞬间。飞行相与触地相中智能体的状态由抛体运动方程确定，即根据期望跳跃高度/距离计算其在飞行轨迹中应处的位置。

训练期间，姿态控制策略以随机姿态与零角动量初始化；同时所有电机角度在全工作范围内初始化，使智能体在训练中能够观测到所有状态。

### 5.6 面向机器人部署的 Sim2Real 迁移

训练期间应用了域随机化（domain randomization）与噪声，以促进策略部署时有效的仿真到实物迁移（Sim2Real transfer）。被随机化的物理属性包括机身与连杆质量、关节摩擦、电机阻尼与控制时延，同时对全部本体感知观测施加高斯噪声。通过系统辨识（system identification）的精确电机建模进一步缩小了 Sim2Real 差距。行走与跳跃控制方法建立在前期工作之上：采用该方法训练的策略曾在地球重力条件下成功迁移至硬件 [9]，这为所训练策略的可迁移性提供了支持。因此，主要未经测试的差距在于低重力工况与弹簧集成——这二者在地球上难以复现。在相同方法下训练的姿态控制策略成功完成硬件迁移，也支持了运动策略的部署就绪性。

### 5.7 神经网络架构与实现

训练与仿真使用 IsaacLab [19] 及 RL Games [20] 的近端策略优化（proximal policy optimization, PPO）实现。所有策略在单块 NVIDIA RTX 3090 GPU 上以 4096 个并行环境训练。每个策略采用三层全连接多层感知机（multilayer perceptron, MLP）架构。网络配置为：姿态控制 [512, 256, 128]；行走 [256, 128, 128]；垂直跳跃 [256, 128, 128]；水平跳跃 [128, 128, 128]。

## 6 仿真研究

我们在两类场景下评估训练所得策略：自由飞行（零重力）中的姿态控制，以及火星重力条件下的行走、垂直跳跃与前向跳跃。

### 6.1 姿态控制

姿态控制策略通过自由飞行条件下的阶跃响应（step response）测试进行评估。给定四元数误差 $q_B^R$，策略生成动作以达到目标姿态。收敛定义为姿态误差在 5° 以内。三组测试场景评估重定向能力的不同方面：单轴响应测试对每个轴（滚转 roll、俯仰 pitch、偏航 yaw）独立施加 90° 与 180° 阶跃指令；三维重定向响应测试则指令从 $[-90°, 90°, 90°]$（滚转、俯仰、偏航）同时旋转至 $[0°, 0°, 0°]$，以评估协调的多轴控制。

图 4a 展示了策略对 90° 单轴指令的响应：滚转在 0.96 s 达到目标阈值，俯仰 1.08 s，偏航 1.45 s。策略表现出平滑、单向的收敛，无显著超调。图 4b 展示了对更大的 180° 指令的响应，滚转轴响应最快，在 1.9 s 达到阈值。图 4c 给出了复杂三维机动的结果，策略在 2.45 s 内到达目标姿态。

【图4：滚转、俯仰与偏航对目标姿态变化的响应曲线（仿真）。包含三个子图：(a) 90° 测试中滚转、俯仰、偏航的重定向响应；(b) 180° 测试中三轴的重定向响应；(c) 滚转-俯仰-偏航三轴联动的三维重定向响应。横轴为时间（秒），纵轴为角度（度），并绘制参考目标线，用于展示收敛速度与无超调特性。】

### 6.2 低重力下的垂直跳跃

垂直跳跃策略通过 244 次跳跃试验进行评估，目标高度覆盖 1.0 m 至 3.5 m；策略训练的目标高度范围为 1.8 m 至 2.8 m，该范围介于最大可达高度（3.2 m）与垂直跳跃的最小有用高度之间。成功定义为实际最高点（apogee）高度与指令目标高度之差在 0.2 m 以内。图 5a 显示在整个测试范围内具有很强的跟踪性能：平均绝对误差 0.123 m，总体成功率 88.9%，最大跳跃高度 3.1 m。值得注意的是，所有失败尝试（最高点误差超过 0.2 m）均出现在 2.95 m 以上的目标，这已超出训练分布。在 1.8 m 至 2.5 m 的训练范围内，策略表现出高可靠性，而对更高目标的外推则有一定性能下降。

### 6.3 低重力下的前向跳跃

前向跳跃策略在火星重力条件下通过 244 次前向跳跃进行评估，目标距离覆盖 1.0 m 至 4.5 m；策略训练范围为 1.5 m 至 4.1 m。超过 4.1 m 的目标已接近当前执行器设置所能达到的极限。最终着陆位置与指令目标之差在 0.2 m 以内定义为成功跳跃。策略在整个测试范围内表现出很强的目标跟踪性能（图 5b）：平均绝对误差 0.208 m，最大前向跳跃 3.9 m，总体成功率 80.7%。注意所有失败尝试（着陆误差超过 0.2 m）均出现在 4.1 m 以上的目标，超出训练分布；在 1.0 m 至 3.8 m 范围内策略可靠性非常高。仿真测试还表明，前向跳跃时策略在触地机体姿态达滚转 45°、俯仰 60°、偏航 90° 的情况下仍能保持成功着陆。

【图5：无弹簧时跳跃目标与实际成绩的对比散点图。包含两个子图：(a) 垂直跳跃——横轴为目标高度（1.0–3.0 m），纵轴为实际最高点高度，绘制理想跟踪线（Target height）与 ±0.2 m 容差带，标注 N=244 次跳跃、成功率 88.9%、平均误差 0.123 m；(b) 前向跳跃——横轴为目标距离（1–4 m），纵轴为实际距离，标注成功率 80.7%、平均误差 0.208 m。图中直观展示了策略在训练范围内的紧密跟踪以及超出训练分布后的偏差。】

### 6.4 跳跃中的弹簧集成

如第 3 节所述，机器人设计允许集成弹簧。为研究在跳跃策略训练与部署中启用并联弹簧的效果，我们按第 3 节的优化结果，以 800 N/m 的弹簧刚度训练了启用弹簧的垂直与前向跳跃策略。启用弹簧的跳跃评估见图 6。弹簧使跳跃高度与距离提升约 21%，同时保持了合理的跟踪性能，展示了实现更强力跳跃的潜力，尽管跟踪性能有一定代价。

【图6：带仿真弹簧时跳跃目标与实际成绩的对比散点图。子图 (a) 为垂直跳跃（±0.4 m 容差，N=244，成功率 72.1%，平均误差 0.303 m）；子图 (b) 为前向跳跃（±0.4 m 容差，N=244，成功率 93.4%，平均误差 0.191 m）。与图 5 对比可看出弹簧将跳跃能力提高约 21%，但垂直跳跃的跟踪精度有所下降。】

## 7 实验验证

本节给出姿态控制策略在 Olympus 四足机器人上的实验验证。状态估计由动作捕捉系统提供。电机力矩限制为 12 N·m，与仿真训练条件一致，以确保安全运行。实验在欧空局（ESA）ESTEC 的轨道机器人实验室（Orbital Robotics Lab）进行。

### 7.1 姿态控制——单轴旋转

为验证姿态控制策略的重定向能力，我们采用了定制的测试台架：机器人安装在旋转杆上，旋转杆再安装于浮动气浮平台（floating air-bearing platform）。该构型将运动约束为单一旋转自由度，从而每次仅对一个轴模拟自由飞行动力学，实现隔离的滚转、俯仰与偏航控制测试。图 8 给出了各姿态轴的机器人安装构型。由于俯仰测试中的机械约束（平台会限制腿部运动），我们开发了专门的策略变体 $\pi_{AC\text{-}pitch}$，将髋关节运动限制在 ±5° 以内，以避免腿-平台碰撞。

每个轴执行三类重定向测试：90° 阶跃响应、180° 阶跃响应与多阶跃序列。鉴于安装平台的不稳定性，为确保安全运行，使用滑动平均滤波器（20 采样窗口）降低了腿部运动速度。所得重定向时间汇总于表 3。注意由于该安全约束，实际时间慢于仿真；采用等效滤波的仿真表现出相当的性能，表明在移除硬件约束后策略能够实现更快的响应。

图 7a 展示了 90° 阶跃响应测试，滚转在 2.6 s 达到目标姿态。图 7b 展示了 180° 测试，滚转最快，在 4.6 s 达到目标姿态。图 7c 展示了多阶跃序列的结果。

【图7：硬件测试中滚转、俯仰与偏航对目标姿态变化的实测响应曲线。包含三个子图：(a) 90° 测试的三轴响应；(b) 180° 测试的三轴响应；(c) 目标姿态多次阶跃变化下的跟踪响应。曲线为各轴角度随时间的变化及目标参考线，用于展示实物上的收敛速度与安全滤波带来的延迟。】

**表 3. 姿态控制重定向时间**

| 测试 | 滚转（仿真 / 实物） | 俯仰（仿真 / 实物） | 偏航（仿真 / 实物） |
|---|---|---|---|
| 90° | 0.96 s / 2.6 s | 1.08 s / 4.2 s | 1.44 s / 3.9 s |
| 180° | 1.9 s / 4.6 s | 2.3 s / 8.4 s | 2.4 s / 7.1 s |

【图8：姿态控制实验装置示意图。机器人安装在旋转杆上，旋转杆固定于超平地板上的浮动气浮平台，Vicon 动捕系统提供状态估计，两侧设有墙面。图中分别展示了滚转（Roll）、俯仰（Pitch）与偏航（Yaw）三种单轴安装构型。】

### 7.2 姿态控制——墙面弹跳

为演示动态机动中的综合重定向能力，我们进行了墙面弹跳（wall-bounce）实验，将姿态控制与自由漂浮飞行阶段相结合。机器人初始安装于自由浮动平台上，以指向墙面的初速度运动，同时姿态控制策略保持"脚朝前"的姿态。当到达距墙 1 m 处时，机器人执行预编程的推离机动，使轨迹反向朝向对面墙面；同时姿态控制策略收到 180° 重定向指令，以面向来墙的脚朝前姿态迎接着陆。这形成了连续的弹跳序列，机器人必须在每一段自由漂浮飞行阶段中完成重定向以获得正确的着陆姿态。

实验对每个旋转轴（滚转、俯仰、偏航）分别进行，每次测试至少完成五个完整弹跳循环。图 9 展示了一个代表性的滚转序列，可见从左到右的轨迹与成功的重定向。该测试验证了策略在接近行星探测任务中自由飞行场景的动态条件下执行快速姿态修正的能力。

【图9：动态机动中姿态控制策略的墙面弹跳实验验证序列帧图。展示机器人在墙面交互之间转换时，围绕滚转轴成功完成 180° 重定向的过程：机器人从一侧墙面推离、自由漂浮、在空中完成 180° 翻转、以脚朝前姿态到达对面墙面。】

## 8 行星探测流程测试

为验证全部已训练策略的综合能力，我们在仿真火星地形与重力中实施了一项完整的探测任务。该任务演示了行走、垂直跳跃、水平跳跃与飞行中姿态控制策略的协调部署，以穿越火星挑战性行星探测场景中的典型地形特征。

基于路点（waypoint）的分层控制器协调任务执行：每个路点指定目标位置 $(x, y)$、朝向（偏航角）与运动模式（行走、垂直跳跃或带相关参数的前向跳跃，如跳跃距离或目标高度）。控制器在机器人机体系中跟踪位置与朝向误差，指令行走策略以 0.07 m 阈值逼近路点。行走策略能够在高至 0.15 m 的障碍物与陡至 20° 的坡面上鲁棒行走，同时能在零速度指令下保持完全静止——这对向跳跃策略的一致交接至关重要。到达跳跃路点后，系统经历预定义状态序列：机器人在站立位稳定 1 s，切换到相应的跳跃策略起跳；一旦足部失去地面接触、高度超过 0.6 m 且竖直速度为正，姿态控制策略介入，调节机体姿态以确保安全着陆；当机器人下降到 0.9 m 以下，控制权交还跳跃策略执行着陆。触地并短暂恢复后，行走策略重新接管并展示恢复控制能力——尽管空中阶段带来动量延续，仍能在跳跃-行走切换中保持稳定。

任务包含多个运动挑战：穿越崎岖地形；跃过 2.1 m 宽的撞击坑；从 1.1 m 高的台缘执行 3.5 m 前向跳跃；进行 2.6 m 垂直跳跃以获得高处观测；以及在困难着陆条件下翻越 1.1 m 台缘。图 10 展示了连续仿真运行中成功完成任务的序列帧。该集成系统能够穿越传统探测机器人无法通行的地形，验证了跳跃式腿式机器人多策略运动方案在行星探测应用中的价值。

【图10：Isaac Lab 中集成行星探测任务仿真的单次连续运行序列帧（俯视轨迹图 + 关键帧截图）。图中彩色圆点表示该时刻使用的任务策略：行走策略、前向跳跃策略、垂直跳跃策略、姿态控制策略。标注的关键节点为：0 任务开始；1、2、4 前向跳跃；3 垂直跳跃；5 任务完成。机器人成功穿越崎岖地形，跃过 2.1 m 宽撞击坑，从 1.1 m 台缘执行 3.5 m 前跳，完成 2.6 m 垂直侦察跳跃，并在前跳中翻越 1.1 m 台缘；姿态控制策略在所有飞行相位维持期望姿态以保证安全着陆。火星地形模型来自 https://sketchfab.com/gaiastucky】

## 9 结论

本文提出了一种用于行星探测场景中动态四足运动的强化学习方法，展示了针对火星重力与飞行中条件训练的姿态控制、行走与跳跃策略。姿态控制策略在硬件实验中以 2.6 s 完成 90° 姿态重定向（仿真中为 0.96 s）；仿真跳跃测试实现了最高 3.1 m 的垂直跳跃与最高 3.9 m 的水平跳跃。组合的多策略行星探测流程的能力通过在仿真中成功穿越巡视器无法通行的复杂地形特征得到验证。主要局限包括：运动策略尚未在低重力条件下进行硬件验证，以及弹簧集成未经实物测试——二者均为自然的未来工作方向。尽管如此，这些结果证明了跳跃式腿式机器人用于行星探测的可行性。

## 参考文献（保留原文）

1. S. T. Arzo, D. Sikeridis, M. Devetsikiotis, F. Granelli, R. Fierro, M. Esmaeili, and Z. Akhavan, "Essential technologies and concepts for massive space exploration: Challenges and opportunities," IEEE Transactions on Aerospace and Electronic Systems, vol. 59, no. 1, pp. 3–29, 2022.
2. A. R. Vasavada, "Mission overview and scientific contributions from the mars science laboratory curiosity rover after eight years of surface operations," Space Science Reviews, vol. 218, no. 3, p. 14, 2022.
3. P. Arm, G. Waibel, J. Preisig, T. Tuna, R. Zhou, V. Bickel, G. Ligeza, T. Miki, F. Kehl, H. Kolvenbach, et al., "Scientific exploration of challenging planetary analog environments with a team of legged robots," Science Robotics, vol. 8, no. 80, p. eade9548, 2023.
4. F. Sauro, R. Pozzobon, M. Massironi, P. De Berardinis, T. Santagata, and J. De Waele, "Lava tubes on earth, moon and mars: A review on their size and morphology revealed by comparative planetology," Earth-Science Reviews, vol. 209, p. 103288, 2020.
5. H. Kolvenbach et al., "Lunarleaper-a mission concept to explore the lunar subsurface with a small-scale legged robot," in IAC 2024 Conference Proceedings.
6. M. Tranzatto, T. Miki, M. Dharmadhikari, L. Bernreiter, M. Kulkarni, F. Mascarich, O. Andersson, S. Khattak, M. Hutter, R. Siegwart, et al., "Cerberus in the darpa subterranean challenge," Science Robotics, vol. 7, no. 66, p. eabp9742, 2022.
7. J. A. Olsen, G. Malczyk, and K. Alexis, "Olympus: A jumping quadruped for planetary exploration utilizing reinforcement learning for in-flight attitude control," in 2025 IEEE International Conference on Robotics and Automation (ICRA), pp. 4366–4372, 2025.
8. N. Rudin, H. Kolvenbach, V. Tsounis, and M. Hutter, "Cat-like jumping and landing of legged robots in low gravity using deep reinforcement learning," IEEE Transactions on Robotics, vol. 38, no. 1, pp. 317–328, 2022.
9. J. A. Olsen, L. R. Pettersen, and K. Alexis, "Towards quadrupedal jumping and walking for dynamic locomotion using reinforcement learning," IEEE Robotics and Automation Letters, vol. 11, no. 4, pp. 4809–4816, 2026.
10. J. A. Olsen and K. Alexis, "Design and experimental verification of a jumping legged robot for martian lava tube exploration," in 2023 21st International Conference on Advanced Robotics (ICAR), pp. 452–459, IEEE, 2023.
11. A. Patel, S. Karlsson, B. Lindqvist, C. Kanellakis, A.-A. Agha-Mohammadi, and G. Nikolakopoulos, "Towards energy efficient autonomous exploration of mars lava tube with a martian coaxial quadrotor," Advances in Space Research, vol. 71, no. 9, pp. 3837–3854, 2023.
12. R. Doyle, T. Kubota, M. Picard, B. Sommer, H. Ueno, G. Visentin, and R. Volpe, "Recent research and development activities on space robotics and ai," Advanced Robotics, vol. 35, no. 21-22, pp. 1244–1264, 2021.
13. F. Mier-Hicks et al., "Sample Recovery Helicopter," in 2023 IEEE Aerospace Conference, pp. 1–11, Mar. 2023. ISSN: 1095-323X.
14. J. Thangavelautham, M. S. Robinson, A. Taits, T. McKinney, S. Amidan, and A. Polak, "Flying, hopping pit-bots for cave and lava tube exploration on the moon and mars," arXiv preprint arXiv:1701.07799, 2017.
15. J. Tan, T. Zhang, E. Coumans, A. Iscen, Y. Bai, D. Hafner, S. Bohez, and V. Vanhoucke, "Sim-to-real: Learning agile locomotion for quadruped robots," arXiv preprint arXiv:1804.10332, 2018.
16. J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, and M. Hutter, "Learning quadrupedal locomotion over challenging terrain," Science Robotics, vol. 5, no. 47, p. eabc5986, 2020.
17. V. Atanassov, J. Ding, J. Kober, I. Havoutis, and C. D. Santina, "Curriculum-based reinforcement learning for quadrupedal jumping: A reference-free design," IEEE Robotics and Automation Magazine, vol. 32, no. 2, pp. 35–48, 2025.
18. T. El-Agroudi, F. G. Maurer, J. A. Olsen, and K. Alexis, "In-flight attitude control of a quadruped using deep reinforcement learning," in 8th Annual Conference on Robot Learning, 2024.
