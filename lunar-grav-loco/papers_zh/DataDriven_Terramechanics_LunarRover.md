# 面向月面巡视器逼真实时仿真器的数据驱动地面力学方法

> **元信息**
> - 原文标题：Data-Driven Terramechanics Approach Towards a Realistic Real-Time Simulator for Lunar Rovers
> - 中文译名：面向月面巡视器逼真实时仿真器的数据驱动地面力学方法
> - 来源：arXiv:2601.04547v1 [cs.RO]，2026-01-08
> - 原文文件：`papers/DataDriven_Terramechanics_LunarRover.pdf`
> - 翻译日期：2026-09-30
> - 资助：JST Moonshot 研发计划（Grant No. JPMJMS223B）

**作者**：Jakob M. Kern, James M. Hurrell, Shreya Santra, Keisuke Takehana, Kentaro Uno, Kazuya Yoshida

**作者单位**：日本东北大学大学院工学研究科 航空宇宙工学专攻 空间机器人实验室（Space Robotics Lab, SRL），仙台 980–8579。通讯作者：Jakob M. Kern（kern.jakob.marian.s4@dc.tohoku.ac.jp）

## 摘要

面向月面的高保真仿真器为巡视器操作与任务规划的广泛测试提供了数字化环境。然而，目前的仿真器要么侧重视觉真实性，要么侧重物理精度，难以全面复现月球条件。本工作通过将高视觉保真度与真实的地形交互相结合来弥补这一差距，实现对月面巡视器的逼真呈现。由于车轮—土壤交互的直接仿真计算开销巨大，本文采用数据驱动方法：利用整车实验与单轮实验及仿真中采集的数据，建立滑移率（slip ratio）与沉陷（sinkage）的回归模型。所得基于回归的地面力学（terramechanics）模型能在平地及 20° 以内坡面上精确复现稳态与动态滑移以及沉陷行为，并通过现场测试结果验证。此外，还改进了地形变形与轮迹可视化的真实感。该方法支持需要物理合理的地形响应与高视觉保真度的实时应用。

## I. 引言

真实任务中测试月面巡视器的机会有限，凸显了对逼真月面仿真器的需求。数字化环境可复现月球条件，从长阴影下的极端光照等视觉特征到地形特征。然而，对行星巡视器操作与任务规划而言，仿真的月面环境不仅要视觉上逼真，还必须精确建模巡视器与地形之间的物理交互。特别地，衡量车轮牵引性能的滑移率（slip ratio）以及车轮陷入地形的沉陷（sinkage），是月壤（lunar regolith）等颗粒土壤上的关键特征。虽然车轮—土壤交互可用接触动力学与粒子仿真详细分析，但该方法计算密集，不适合实时应用。

为解决这一局限，本研究采用数据驱动方法提升实时月面仿真中车轮—地形交互的物理保真度（如图 1 所示）。滑移率与沉陷的回归模型源自 JAXA（日本宇宙航空研究开发机构）相模原校区太空探测试验场中高速巡视器 [1] 的实验数据。这些模型被集成到刚体仿真框架中，在低计算开销下于数字环境中复现真实的车轮滑移与沉陷。本工作的主要贡献为：

- 基于车轮速度与坡角的**车轮滑移实现**；
- 基于滑移率与车轮载荷的**车轮沉陷实现**；
- 基于滑移率的**地形变形**，提升巡视器轮迹的真实感。

本工作集成到开源的 OmniLRS 仿真器 [3]（基于 NVIDIA IsaacSim [4]）中，以更高的物理保真度扩展了其行星巡视器测试能力。

【图 1：(a) 实时月面仿真器 OmniLRS 中用于复现真实车轮滑移、沉陷与轮迹的数据驱动地面力学模型；(b) 巡视器在本仿真器中留下物理合理的轮迹；(c) 刚性接触与软接触分别处理。】

## II. 相关工作

月面巡视器移动性的高保真仿真既需要视觉可信的环境，也需要物理精确的车轮—土壤交互。然而现有仿真工具往往以牺牲一方为代价来优先另一方：实时月面仿真器通常强调高视觉保真度与机器人控制框架的集成，却简化了地形交互；而高保真地面力学仿真器能详细建模颗粒土壤动力学，但计算量过大，无法实时使用。本节回顾两个领域的关键工作，并引出我们弥合这一差距的方法。

### A. 实时月面仿真器

面向实时应用的若干高保真月面仿真器正在积极开发中，主要聚焦视觉真实性。这些月面环境采用刚性地形模型与简单物理模型，限制了其在真实巡视器移动仿真中的效用。

一个例子是 NASA 约翰逊航天中心开发的"数字月球探测场"（DLES，Digital Lunar Exploration Sites）[5,6]，它基于月球轨道器激光高度计（LOLA）[7] 提供了月球南极的精细模型。作者描述了数字高程图的处理与大尺度环境（含撞击坑与巨石）的高效管理。DLES 设计为可跨多个渲染引擎使用；其 Unreal 仿真工具（DUST）[8] 将 DLES 地形数据库集成到 Unreal Engine 5 中，具备高分辨率地形、真实光照与巡视器路径规划工具，但缺乏地形变形建模与复杂的车轮—地形动力学——轮迹有视觉渲染，但无物理仿真。

RSIM 月面仿真器 [9]（前身为 VIPER 月面仿真器 [10]）由 NASA 艾姆斯研究中心开发、基于 Gazebo 构建，具备月面探测的许多关键要素：真实光照、相机镜头光晕与合成增强的大尺度地形。它包含一个在 NASA Glenn SLOPE 设施推导的坡度相关车轮滑移模型，用"滑移图（slip map）"模拟牵引力损失。但该模型不考虑速度相关的滑移行为，滑移引起的车轮沉陷也无视觉或物理表示。轮迹使用凹凸贴图（bump mapping）渲染，通过改变表面法线制造变形错觉，但并不修改实际地形网格，且轮迹渲染不考虑车轮几何或滑移。

OmniLRS 是基于 NVIDIA Omniverse IsaacSim 的开源月面机器人仿真器，由卢森堡大学与东北大学空间机器人实验室开发 [3]。它提供三个环境：(1) Lunalab，复现卢森堡大学的月面试验场；(2) Lunaryard，程序化生成的月面地形；(3) 基于月球数字高程图的大尺度月面环境。该仿真器已在 Lunalab 环境中成功验证了视觉岩石分割任务的仿真到现实（sim-to-real）迁移。轮迹以视觉方式表示，并通过基于接触力的回归模型缩放——若已知车轮的网格几何，该模型还可调整以适配带履刺（grouser）车轮 [11]。但该仿真器缺少完整的地面力学考虑，例如滑移插件或车轮沉陷可视化。

### B. 地面力学仿真器

地面力学仿真器将车辆—地形交互的精确计算置于合成环境的视觉真实感之上，此外巡视器的感知与控制通常被简化或缺失。

在高保真建模方面，源于 Cundall 与 Strack 工作的离散元方法（DEM，discrete element method）[12] 可将月壤建模为相互作用的颗粒集合，颗粒与穿越地形的车轮相互作用。接触力与力矩用高时空分辨率的计算密集方法求解。DEM 在地面力学中被广泛用于研究滑移、车轮沉陷与土壤变形。将 DEM 与多体动力学耦合可对巡视器在颗粒材料上的移动性进行详细分析，从复杂单轮运动、悬挂系统到整车研究 [13]。但该方法不适合实时应用，且缺少对机器人控制与传感器的支持。

为解决这一局限，Project Chrono [14] 等框架提供了多种可变形地形模型。除支持 DEM 外，Chrono 还有连续表征模型（CRM）与土壤接触模型（SCM）：SCM 计算表面与地面之间的接触力，允许地形网格变形并近似实时地给出接触响应。但其仿真受限于小尺度环境，且缺少与机器人感知、控制软件栈的集成。

## III. 方法

本工作旨在以数据驱动方法弥合高保真地面力学仿真与实时照片级机器人环境之间的差距，如图 2 所示。由现场测试、单轮实验与 DEM 仿真推导的车轮滑移与沉陷回归模型被集成到月面仿真器 OmniLRS [3] 中。滑移率 $s$ 通过指令巡视器跟踪滑移修正速度 $v$ 来模拟；沉陷 $z$ 通过柔顺接触（弹簧—阻尼系统）建模，其刚度 $k$ 决定沉陷深度。此外，贡献还包括改进的车轮轮迹地形变形渲染——不仅随接触力 $F_z$ 缩放（如文献 [11]），还随滑移率 $s$ 变化。本文聚焦实现方法而非数据采集或回归建模本身。

【图 2：所提方法的架构图，展示回归模型、滑移/沉陷实现与地形变形模块间的关系。】

### A. 实验流程

为测量车轮滑移，在 JAXA 太空探测设施 [2] 进行了现场测试，使用 EX1——一台尺寸为 (0.82, 0.52, 0.67 m)、重 21.63 kg 的四轮高速巡视器，配备空间机器人实验室研发的被动弹簧—阻尼悬挂 [1]。车轮设计基于文献 [17] 的履刺间距方程优化。数据采集测试如图 3 所示：实验场地为 20 m × 20 m 区域，填充约 0.3 m 深的东北硅砂 5 号（Tohoku Silica No.5）[18] 砂。这种干燥松散的硅砂常被用作低保真月壤模拟物，其稀疏的颗粒分布为车轮沉陷与打滑提供了更具挑战性的条件 [15]。

【图 3：数据采集现场测试的实验布置（上），以及爬坡（左下）与加速（右下）的两张代表性快照。】

测试在平地上以车轮速度 $v_w = \omega R$ 为 0.23–1.17 m/s 进行，在 0°–18° 坡面上以最高 0.47 m/s 的速度进行；附加试验包括快速加减速以分析瞬态滑移（图 3）。车轮速度 $v_w$ 由编码器测量，平移速度 $v$ 由 16 相机 OptiTrack 动作捕捉系统（180 Hz，±0.15 mm 精度）跟踪。为独立估计平均滑移，外部相机记录了车轮旋转及通过一段 2 m 定义区段的行驶时间（亦见表 I）。

滑移率 $s$ 按式 (1) 计算，其中 $\omega$ 为角速度，$R$ 为含履刺高度的有效车轮半径。许多带履刺车轮运动的研究仅用轮半径计算滑移率、忽略履刺高度；但发现若在滑移计算中不含履刺长度，行驶运动中的滑移会被算成负值或滑移倒转（skidding）。将履刺长度计入有效车轮半径后，所有加速与稳态运动中的滑移均为正；减速时滑移/滑转如预期为负。

$$s = \begin{cases} 1 - \dfrac{v}{\omega R}, & \text{若 } \omega R \ge v \\[6pt] \dfrac{\omega R}{v} - 1, & \text{若 } \omega R < v \end{cases} \tag{1}$$

在加减速测试中，动作捕捉系统还跟踪车轮垂向位移，以估计相对初始静止位置的沉陷。为补充现场数据，参考了先前单轮测试台实验 [15] 与 DEM 仿真 [16,19] 的结果（图 4）——DEM 能对车轮—土壤交互进行详细分析，弥补物理测试在可控性与测量精度上的限制。测试台提供滑移—沉陷关系；固定滑移率 20% 的 DEM 仿真用于评估不同垂向载荷的影响。

【图 4：单轮测试台（左）[15] 与 DEM 仿真（右）[16]。】

**表 I. 用于滑移率与沉陷估计的传感器、数据、采样频率与数据点数概览。**

| 传感器 | 记录数据 | 计算数据 | 频率 | 数据点 |
|---|---|---|---|---|
| 动作捕捉系统 | 位置 $[x,y,z]$ 与姿态 $[q_x,q_y,q_z,q_w]$ | 速度 $v$ | 180 Hz | ≤ 1000 |
| 相机 | 图像 | 平均速度 $v$ | 60 Hz | — |
| 电机编码器 | 角速度 $[\omega]$ | — | 5 Hz | ≤ 35 |

### B. 回归模型

基于实验观测，推导了车轮滑移与沉陷的回归模型以刻画地形交互。平地滑移率 $s$ 被发现随车轮速度 $v_w$ 线性增大，如式 (2) 所示。坡角 $\alpha$ 对滑移率的影响通过拟合以 $v_w$ 参数化的二阶多项式捕捉，得到式 (3) 的综合滑移模型。多项式拟合基于 16 次独立实验运行的平均值。

$$s(v_w) = 0.0265\,v_w + 0.0256 \tag{2}$$

$$s(v_w, \alpha) = (0.00522\,v_w + 0.00105)\,\alpha^2 + s(v_w) \tag{3}$$

沉陷模型结合单轮测试台与 DEM 仿真结果建立。沉陷 $z$ 建模为滑移率 $s$ 与垂向载荷 $F_z$ 相对标称参考载荷 $F_{ref}$ 偏差的线性函数；$F_{ref}$ 对应月球重力下均匀受力分布时单个车轮上的静载荷。静态沉陷在现场测试中由动作捕捉系统测量。沉陷回归模型（$z$ 以毫米 mm 表示）为：

$$z(s, F_z) = -33.56\,s - 0.9291\,(F_z - F_{ref}) - 3.11 \tag{4}$$

### C. 滑移实现

在真实运行与高保真地面力学仿真中，滑移源于车轮与可变形地形的复杂交互；相比之下，本方法使用回归模型确定车轮滑移。在每个仿真时间步，以当前车轮速度 $v_w$ 与局部坡角 $\alpha$ 为输入评估回归模型得到滑移率 $s$，进而确定滑移修正平移速度 $v$：

$$v = \bigl(1 - s(v_w, \alpha)\bigr)\,v_w \tag{5}$$

由于仿真基于含库仑摩擦的刚体动力学，无法复现稳态滑移（即以恒定速度运动时的滑移）。为复现滑移的运动学效应，车轮直接以滑移修正速度 $v$ 驱动。该方法在保持刚体框架的同时实现滑移行为的逼真仿真。

为复现打滑车轮的视觉外观，每个车轮被拆分为一个纯视觉体（用于渲染）与一个纯物理体（用于物理交互）：两种表示共享同一位置，但通过独立关节与底盘连接，允许独立驱动。物理轮以滑移修正速度 $v$ 驱动，视觉轮以指令车轮速度 $v_w$ 旋转，从而在物理几何与地形之间未发生实际滑移的情况下产生车轮打滑的视觉印象。视觉几何采用精细网格以真实呈现履刺车轮；物理几何则采用简单胶囊体（图 5）以获得稳定的接触交互。

【图 5：巡视器的车轮视觉几何（左）与物理几何（右）示意。】

除稳态滑移行为外，巡视器加减速过程中的瞬态动力学对与实验数据保持一致至关重要。为此，仿真库仑摩擦模型用现场测试获得的速度剖面标定：测试表明急停时减速率在指令速度 0.2–1.17 m/s 范围内保持一致。将静、动摩擦系数分别设为 1.0 与 0.8 后，仿真减速与观测行为高度吻合。

然而高摩擦参数会导致不真实的过快加速。为此引入了限制器函数（limiter function），约束时间步之间平移速度的最大允许变化。该约束基于现场测试：初始加速度在很大程度上与指令车轮速度无关，表明其受履刺几何与土壤特性限制。现场测试数据与限制器见图 6。值得注意的是，超过某一速度阈值后加速度下降，该趋势可用如下分段线性函数近似：

$$\Delta v \le \begin{cases} 3.476, & v \le 0.75 \\ 0.612, & 0.75 < v \le 1.02 \\ 0.114, & v > 1.02 \end{cases} \tag{6}$$

【图 6：四种不同指令车轮速度下加速过程的实测平移速度。红色曲线为限制器函数，定义最大可能加速度。】

### D. 沉陷实现

为仅用刚体建模可变形地形上的车轮沉陷，采用柔顺接触建模：不将接触视为完全刚性，而用弹簧—阻尼系统模拟碰撞体（地形与车轮）之间的垂直接触力：

$$\ddot z(t) = -g - \frac{k}{m}z(t) - \frac{c}{m}\dot z(t), \quad z(t) < 0 \tag{7}$$

其中 $z(t)$ 为穿透深度，$\dot z(t)$ 为相对法向速度，$\ddot z(t)$ 为两物体的相对加速度；$k$、$c$ 分别为刚度与阻尼系数，$m$ 为接触处有效质量，$g$ 为重力加速度。垂向参考接触力为 $F_z = mg$。

在准静态条件（即 $\dot z(t) = \ddot z(t) = 0$）下，穿透深度为：

$$z = -\frac{F_z}{k} \tag{8}$$

因此，给定垂向力 $F_z$，可通过调节刚度 $k$ 控制穿透深度 $z$。由于回归模型给出期望沉陷 $z(s, F_z)$（滑移率 $s$ 与垂向载荷 $F_z$ 的函数），反解该关系即可确定合适的刚度。

对于履刺车轮，沉陷通常相对基圆半径 $r$ 测量，不计履刺沉入量。当用半径 $R = r + h$ 的物理几何仿真履刺车轮时，方程中须显式考虑履刺高度 $h$ 以获得正确沉陷。

车轮与地形的碰撞可能在单个或多个接触点求解，总载荷分配于这些点。为获得正确的穿透深度 $z$，刚度 $k$ 须按接触点数 $N$ 缩放，如式 (9)。建议使用球体或胶囊体等简单物理几何作为巡视器车轮，以通过稳定的接触点数产生平稳接触力：

$$k = -\frac{1}{N}\cdot\frac{F_z}{z(s, F_z) - h} \tag{9}$$

为保证数值稳定性，对接触力 $F_z$ 与刚度计算中的分母均施加最小阈值，防止除零及 $F_z$ 较小时近零刚度导致的不稳定行为。

刚度参数 $k$ 每个时间步根据当前接触力与滑移率更新，但这可能在减速时产生不真实行为：巡视器滑行时高滑移导致深沉陷；一旦停车、滑移归零，重算的沉陷变浅，$k$ 骤增使机器人可见地抬升。为避免这一伪影，当平移速度 $v$ 低于 $v_{min} = 0.1$ m/s 时对沉陷施加约束：

$$z^{(t)} \leftarrow \min\bigl(z^{(t-1)}, z^{(t)}\bigr), \quad \text{若 } v(t) \le v_{min} \tag{10}$$

除刚度参数外，阻尼常数影响接触的动态响应。本工作中阻尼常数取临界阻尼（式 11）以保证稳定：

$$c = 2\sqrt{km} \tag{11}$$

### E. 地形变形

对 Kamohara 等人 [11] 的地形实现进行扩展：除接触力外，将滑移纳入影响轮迹形状与深度的第二个参数。更高滑移值产生更深的地形变形，履刺车轮留下的正弦状轮迹图案在高滑移下幅度减小，与现场测试观测一致。除车轮几何调整外，变形机制被拆分为两部分：永久深度变形与瞬时轮迹图案。这种拆分增强了重叠轮迹的视觉保真度，尤其是巡视器多次经过同一区域时。

当前版本中，仅当新计算深度 $d$ 大于（深于）给定地形单元 $d_{x,y}$ 的现有值时才更新深度变形；而轮迹图案 $w$ 在每次经过时重新生成并施加，从而获得真实的轮迹视觉效果。深度 $d$ 与轮迹 $w$ 的组合在数字高程图（DEM）中产生真实、动态的地形修改。更新逻辑定义为：

$$\begin{aligned} \Delta d &\leftarrow \min(0,\ d - d_{x,y})\\ \Delta w &\leftarrow w - w_{x,y}\\ DEM_{x,y} &\leftarrow DEM_{x,y} + \Delta d + \Delta w\\ d_{x,y} &\leftarrow d_{x,y} + \Delta d\\ w_{x,y} &\leftarrow w \end{aligned}$$

### F. 仿真设置

实现基于机器人仿真器 IsaacSim（版本 2023.1.1）结合 OmniLRS 环境开发。滑移与沉陷模型以 Omnigraphs 实现，主要使用自定义脚本节点；轮迹功能直接集成进 OmniLRS 基础代码。所有仿真在 Lunaryard 环境中以默认物理设置 [3] 与 30 Hz 仿真步长进行。

## IV. 结果与分析

通过将滑移率与车轮沉陷的仿真结果与回归模型输出对比评估实现效果，以此衡量仿真复现预期行为的准确程度。

平地上，在所有最高至 1.17 m/s 的车轮速度下滑移率误差保持在 0.02% 以下；坡角最高 20° 的倾斜地形上，平均绝对误差平均为 0.22%。在月球重力下参考力 8.72 N ±5 N 变化范围、全部滑移率范围内，沉陷深度平均误差为 0.25 mm。

此外，图 7 直接对比了指令车轮速度 $v_w = 1.17$ m/s 时平地现场测试与仿真结果，在稳态运动、加速与减速阶段均高度吻合：上图给出 $v_w$ 与实测平移速度 $v$，中图对比滑移率，下图分别绘制加速（左）与减速（右）起点对应的沉陷深度。

【图 7：指令车轮速度 1.17 m/s 下同一实验的现场测试与仿真结果对比（含急加速与急减速阶段）。】

图 8 为改进地形变形模型生成轮迹的俯视视图：高亮区域表示变形深度超过 12 mm 的位置——蓝色与红色标记加减速期间的高滑移区，白色对应外侧前轮载荷增大引起的转向变形。

【图 8：巡视器经过后的可见地形变形，高亮区域表示变形深度大于 12 mm 的位置。】

最终，我们的仿真器按图 9 所示运行：实现真实的车轮滑移与沉陷，以及地形网格的物理变形（即月面上的轮迹）。

【图 9：完成的仿真平台快照，四轮 EX1 巡视器正在数字化月面环境中行驶。车轮滑移与沉陷根据回归模型随地形（坡角）与巡视器运动（车轮速度、接触力）动态变化；轮迹通过视觉地形网格的实时变形呈现；穿越岩石时，岩石被赋予极高的柔顺接触刚度，有效防止车轮沉陷。】

所提方法精确复现了滑移与沉陷行为，证实了基于回归的地面力学模型的有效性。虽然针对特定巡视器—地形组合调参，但通过替换为新实验数据导出的回归模型，该方法可兼容其他配置。

滑移已在多种速度、上下坡以及平地加减速条件下考虑，但未显式处理侧向滑移与转向时的轮间滑移差异。此外，当前回归模型基于干燥硅砂，其力学特性与月壤不同且更均匀。未来工作的重要方向是利用真实月壤模拟物或月球原位数据（可能结合在线自适应方法）开发回归模型，以提升对真实任务的适用性。

## V. 结论

本工作提出了一种在实时仿真中复现巡视器月面行驶的真实性的数据驱动方法。通过集成基于回归的地面力学模型，实现方案精确捕捉了稳态与动态的滑移及沉陷行为，与现场测试结果高度一致；同时提升了地形变形与轮迹可视化的真实感。

该方法支持物理真实地形交互响应十分重要的实时应用，如移动性分析、巡视器测试、任务规划或数字孪生环境。未来工作应聚焦于将其适配到腿式机器人的表面交互，以提升空间机器人各类平台的仿真保真度。

## 致谢

作者感谢 Simon Giel、Momoko Shimizu、Antoine Jonquieres、Takeaki Komine、Yoshimasa Muneishi 与 Nette Levijoki 在现场测试与数据采集中给予的宝贵支持。

## 参考文献（保留原文）

[1] D. Rodríguez-Martínez et al., "Enabling faster locomotion of planetary rovers with a mechanically-hybrid suspension," *IEEE Robotics and Automation Letters*, pp. 1–8, 11 2023.
[2] JAXA. (Accessed: 2024-12-09). [Online]. Available: https://www.ihub-tansa.jaxa.jp/english/
[3] A. Richard et al., "OmniLRS: A photorealistic simulator for lunar robotics," in *2024 IEEE International Conference on Robotics and Automation (ICRA)*, vol. 21, May 2024, p. 16901–16907.
[4] NVIDIA IsaacSim. (Accessed: 2025-03-09). [Online]. Available: https://docs.isaacsim.omniverse.nvidia.com/latest/index.html
[5] E. Z. Crues et al., "Digital Lunar Exploration Sites (DLES)," in *2022 IEEE Aerospace Conference (AERO)*, 2022, pp. 1–13.
[6] C. Foreman et al., "Digital Lunar Exploration Sites (DLES) Terrain Crafting," in *2025 IEEE Aerospace Conference*, 2025, pp. 1–18.
[7] R. Vondrak et al., "Lunar Reconnaissance Orbiter (LRO): Observations for Lunar Exploration and Science," *Space Science Reviews*, vol. 150, no. 1-4, pp. 7–22, February 2010. https://doi.org/10.1007/s11214-010-9631-5
[8] L. Bingham et al., "Digital Lunar Exploration Sites Unreal Simulation Tool (DUST)," in *2023 IEEE Aerospace Conference*, 2023, pp. 1–12.
[9] M. Allan, "RSIM Lunar Surface Simulator," Presentation at the Digital Twins for Cislunar & Lunar Surface Enterprise Integration Workshop #3, NASA Ames Research Center, Moffett Field, CA, United States, Apr. 2025, public Use Permitted. NASA Technical Review by Peer Committee. Contract: 80ARC020D0010. [Online]. Available: https://ntrs.nasa.gov/citations/20250004026
[10] M. Allan et al., "Planetary rover simulation for lunar exploration missions," in *2019 IEEE Aerospace Conference*, 2019, pp. 1–19.
[11] J. Kamohara et al., "Modeling of terrain deformation by a grouser wheel for lunar rover simulator," in *21st International and 12th Asia-Pacific Regional Conference of the International Society for Terrain-Vehicle Systems (ISTVS)*, 01 2024.
[12] P. A. Cundall and O. D. L. Strack, "A discrete numerical model for granular assemblies," *Géotechnique*, vol. 29, no. 1, pp. 47–65, 03 1979.
[13] T. M. Wasfy et al., "Coupled Multibody Dynamics and Discrete Element Modeling of Vehicle Mobility on Cohesive Granular Terrains," in *10th International Conference on Multibody Systems, Nonlinear Dynamics, and Control*, ASME, vol. 6, 08 2014, p. V006T10A050.
[14] A. Tasora et al., "Chrono: An Open Source Multi-physics Dynamics Engine," in *International Conference on High Performance Computing in Science and Engineering*, 06 2016, pp. 19–49.
[15] K. Takehana et al., "Grouser wheel high-speed traction performance: DEM simulation and experimental result," *Journal of Terramechanics*, vol. 120, p. 101084, 2025.
[16] J. Hurrell et al., "Traction performance evaluation for a rashid-1 rover wheel," *Space Science Reviews*, vol. 221, no. 3, p. 37, 2025.
[17] K. Skonieczny et al., "A grouser spacing equation for determining appropriate geometry of planetary rover wheels," in *Proceedings of the IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)*, Vilamoura–Algarve, Portugal, Oct. 2012, pp. 5065–5070.
[18] Tohoku Keisa Sangyo Co., Ltd., "Tohoku silica sand no.5," https://www.ktsangyo.co.jp/data1.htm, 2024, accessed: 2025-06-25.
[19] J. Hurrell et al., "Lunar rover discrete element method study and calibration," in *Proceedings of the 16th European-African Regional Conference of the ISTVS (ISTVS '23)*, Lublin, Poland, 2023.
