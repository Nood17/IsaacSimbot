# Figures Agent - 论文绘图

## 定位

Figures Agent 负责将论文中所有 `[FIGURE: ...]` 占位符转化为高质量 SVG 矢量图，并将所有 SVG 统一嵌入一个 PPTX 文件中，方便用户在 PowerPoint 中编辑、导出。

## 输入

- Method 设计（`sections/method.md`）— 包含框架图描述
- Experiments（`sections/experiments.md`）— 包含结果图/表描述
- 完整论文草稿（`output/paper.md`）— 所有 `[FIGURE: ...]` 占位符

## 触发时机

在 Writing Agent 完成全文组装（Step 7）之后、一致性检查之前执行。也可独立触发（用户说"帮我画论文里的图"）。

## 执行流程

### Step 1: 扫描所有图表占位符

从 `output/paper.md`（或各 section 文件）中提取所有 `[FIGURE: ...]` 标记：

```
[FIGURE: method_overview] — 方法整体框架图
[FIGURE: module_detail] — 模块细节图
[FIGURE: results_comparison] — 实验对比柱状图
[FIGURE: ablation_curve] — 消融实验曲线
[FIGURE: attention_visualization] — 注意力可视化
```

生成图表清单 `figures/figure_list.json`：

```json
[
  {
    "id": "method_overview",
    "type": "architecture",
    "description": "方法整体框架图，展示输入到输出的数据流",
    "source_section": "method",
    "svg_path": "figures/svg_output/method_overview.svg",
    "status": "pending"
  },
  {
    "id": "results_comparison",
    "type": "chart_bar",
    "description": "主实验结果对比柱状图",
    "source_section": "experiments",
    "svg_path": "figures/svg_output/results_comparison.svg",
    "status": "pending"
  }
]
```

### Step 2: 分类图表类型

按用途分类，每类有不同的绘制策略：

| 类型 | 说明 | SVG 策略 |
|------|------|----------|
| `architecture` | 方法框架图 / 系统架构图 | 模块方块 + 箭头连线 + 标签文字 |
| `module_detail` | 单模块内部结构 | 细粒度组件 + 数据流 |
| `pipeline` | 流程图 / 管线图 | 步骤节点 + 顺序箭头 |
| `chart_bar` | 柱状图 | 坐标轴 + 矩形柱 + 数值标签 |
| `chart_line` | 折线图 / 曲线图 | 坐标轴 + polyline + 图例 |
| `chart_radar` | 雷达图 | 多边形轮廓 + 标签 |
| `table_visual` | 可视化表格 | rect 网格 + 文字 + 颜色编码 |
| `visualization` | 注意力 / 特征可视化 | 热力图色块 / 连接线 |
| `comparison` | 对比示意图 | 左右/上下分栏 + 标注 |

### Step 3: 逐图生成 SVG

对每张图，按以下规范生成 SVG 文件。

#### SVG 技术规范

**画布尺寸**（学术论文场景）：

| 用途 | 尺寸 | 说明 |
|------|------|------|
| 单栏图 (column width) | `viewBox="0 0 800 500"` | 适合单栏论文或双栏中的单列 |
| 双栏图 (text width) | `viewBox="0 0 1600 500"` | 跨双栏的宽图 |
| 方形图 | `viewBox="0 0 800 800"` | 注意力可视化、混淆矩阵 |

**配色方案**（学术风格）：

```
主色系（区分不同方法/模块）:
  - #2196F3 (蓝)   — 本文方法
  - #4CAF50 (绿)   — Baseline 1
  - #FF9800 (橙)   — Baseline 2
  - #9C27B0 (紫)   — Baseline 3
  - #F44336 (红)   — Baseline 4

辅助色:
  - #37474F (深灰) — 文字/标签
  - #ECEFF1 (浅灰) — 背景/网格
  - #FFFFFF (白)   — 模块填充
  - #B0BEC5 (中灰) — 边框/箭头
```

**字体规范**：

```xml
font-family="Arial, Helvetica, sans-serif"
```

- 标题：`font-size="18"` `font-weight="bold"`
- 正文标签：`font-size="14"`
- 坐标轴刻度：`font-size="12"`
- 数学符号：`font-style="italic"`

#### SVG 禁用特性（兼容 PPTX 导出）

与 ppt-master 相同的限制：

| 禁用特性 | 替代方案 |
|----------|----------|
| `<style>` / `class` | 内联样式属性 |
| `<foreignObject>` | 纯 SVG 元素 |
| `<symbol>` + `<use>` | 直接绘制 |
| `mask` | `clipPath`（仅用于 image） |
| `rgba()` | `fill="#HEX" fill-opacity="0.x"` |
| `<animate*>` | 静态图 |
| HTML entities (`&mdash;`) | 直接 Unicode 字符 |

#### 架构图模板

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 500" width="1600" height="500">
  <!-- 背景 -->
  <rect width="1600" height="500" fill="#FFFFFF"/>

  <!-- 模块: 输入 -->
  <g id="module-input">
    <rect x="50" y="180" width="180" height="80" rx="8" fill="#E3F2FD" stroke="#2196F3" stroke-width="2"/>
    <text x="140" y="225" text-anchor="middle" font-size="14" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Input Data</text>
  </g>

  <!-- 箭头: 输入 -> 模块A -->
  <line x1="230" y1="220" x2="320" y2="220" stroke="#B0BEC5" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- 模块: 核心模块A -->
  <g id="module-a">
    <rect x="320" y="150" width="250" height="140" rx="8" fill="#FFFFFF" stroke="#2196F3" stroke-width="2"/>
    <text x="445" y="180" text-anchor="middle" font-size="16" font-weight="bold" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Module A</text>
    <!-- 子模块 -->
    <rect x="340" y="195" width="100" height="40" rx="4" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1"/>
    <text x="390" y="220" text-anchor="middle" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Sub-A1</text>
    <rect x="450" y="195" width="100" height="40" rx="4" fill="#E8F5E9" stroke="#4CAF50" stroke-width="1"/>
    <text x="500" y="220" text-anchor="middle" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Sub-A2</text>
  </g>

  <!-- 箭头定义 -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L10,5 L0,10 Z" fill="#B0BEC5"/>
    </marker>
  </defs>
</svg>
```

#### 柱状图模板

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
  <rect width="800" height="500" fill="#FFFFFF"/>

  <!-- 坐标轴 -->
  <line x1="80" y1="420" x2="750" y2="420" stroke="#37474F" stroke-width="1.5"/>
  <line x1="80" y1="420" x2="80" y2="50" stroke="#37474F" stroke-width="1.5"/>

  <!-- Y轴网格线 -->
  <line x1="80" y1="320" x2="750" y2="320" stroke="#ECEFF1" stroke-width="1"/>
  <line x1="80" y1="220" x2="750" y2="220" stroke="#ECEFF1" stroke-width="1"/>
  <line x1="80" y1="120" x2="750" y2="120" stroke="#ECEFF1" stroke-width="1"/>

  <!-- Y轴标签 -->
  <text x="70" y="425" text-anchor="end" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">0</text>
  <text x="70" y="325" text-anchor="end" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">25</text>
  <text x="70" y="225" text-anchor="end" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">50</text>
  <text x="70" y="125" text-anchor="end" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">75</text>

  <!-- 柱状数据组（示例: Metric 1） -->
  <g id="group-metric1">
    <!-- Ours -->
    <rect x="120" y="140" width="35" height="280" fill="#2196F3"/>
    <!-- Baseline 1 -->
    <rect x="160" y="200" width="35" height="220" fill="#4CAF50"/>
    <!-- Baseline 2 -->
    <rect x="200" y="240" width="35" height="180" fill="#FF9800"/>
    <!-- X轴标签 -->
    <text x="177" y="445" text-anchor="middle" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Metric 1</text>
  </g>

  <!-- 图例 -->
  <g id="legend" transform="translate(550, 60)">
    <rect x="0" y="0" width="16" height="16" fill="#2196F3"/>
    <text x="22" y="13" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Ours</text>
    <rect x="0" y="24" width="16" height="16" fill="#4CAF50"/>
    <text x="22" y="37" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Baseline 1</text>
    <rect x="0" y="48" width="16" height="16" fill="#FF9800"/>
    <text x="22" y="61" font-size="12" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Baseline 2</text>
  </g>

  <!-- 图标题 -->
  <text x="400" y="485" text-anchor="middle" font-size="14" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Figure X: Comparison of methods on benchmark Y</text>
</svg>
```

#### 折线图模板

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
  <rect width="800" height="500" fill="#FFFFFF"/>

  <!-- 坐标轴 -->
  <line x1="80" y1="420" x2="750" y2="420" stroke="#37474F" stroke-width="1.5"/>
  <line x1="80" y1="420" x2="80" y2="50" stroke="#37474F" stroke-width="1.5"/>

  <!-- 折线数据 -->
  <polyline points="120,350 220,300 320,250 420,180 520,150 620,130 720,120"
    fill="none" stroke="#2196F3" stroke-width="2.5" stroke-linejoin="round"/>
  <polyline points="120,380 220,350 320,320 420,280 520,260 620,250 720,240"
    fill="none" stroke="#4CAF50" stroke-width="2.5" stroke-linejoin="round" stroke-dasharray="6,3"/>

  <!-- 数据点标记 -->
  <circle cx="720" cy="120" r="4" fill="#2196F3"/>
  <circle cx="720" cy="240" r="4" fill="#4CAF50"/>

  <!-- 轴标签 -->
  <text x="400" y="470" text-anchor="middle" font-size="13" font-family="Arial, Helvetica, sans-serif" fill="#37474F">Training Epochs</text>
  <text x="30" y="240" text-anchor="middle" font-size="13" font-family="Arial, Helvetica, sans-serif" fill="#37474F" transform="rotate(-90, 30, 240)">Accuracy (%)</text>
</svg>
```

### Step 4: SVG 质量自检

每张 SVG 生成后检查：

1. **XML 合法性** — 无裸 `&`/`<`/`>`，无 HTML entities
2. **viewBox 一致** — `width`/`height` 与 `viewBox` 匹配
3. **无禁用特性** — 无 `<style>`/`class`/`mask`/`foreignObject`
4. **文字可读** — font-size >= 12，对比度足够
5. **箭头方向** — 数据流方向正确
6. **颜色语义** — 本文方法始终用蓝色，baseline 用其他色

### Step 5: 汇总到 PPTX

所有 SVG 生成完毕后，运行脚本将所有图汇总到一个 PPTX 文件中：

```bash
python3 [skill目录]/scripts/figure_to_pptx.py "[项目路径]/figures"
```

输出：`figures/output/paper_figures.pptx`

PPTX 结构：
- 每张 SVG 占一页 slide
- slide 标题 = figure id + 描述
- SVG 以原生 DrawingML 形状嵌入（可编辑）
- 保持矢量精度，用户可在 PPT 中微调

### Step 6: 更新占位符

将论文中的 `[FIGURE: id]` 占位符更新为 LaTeX figure 引用格式：

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/method_overview.pdf}
  \caption{Overview of our proposed method. ...}
  \label{fig:method_overview}
\end{figure}
```

更新 `figures/figure_list.json` 中每个图的 status 为 `"completed"`。

## 输出

| 文件 | 说明 |
|------|------|
| `figures/svg_output/*.svg` | 各图的 SVG 源文件 |
| `figures/output/paper_figures.pptx` | 所有图汇总的 PPTX（可编辑） |
| `figures/figure_list.json` | 图表清单 + 状态 |

## 图表设计原则

### 学术图的基本要求

1. **清晰性优先** — 学术图不是展示设计功力的地方，信息传达准确 > 视觉花哨
2. **黑白友好** — 考虑打印场景，不要仅靠颜色区分（辅以虚线、形状、标签）
3. **一致性** — 全文所有图使用相同的配色方案、字体、线宽
4. **自包含** — 仅看图 + caption 就能理解图在说什么
5. **避免冗余** — 图和表不要重复表达相同信息

### 常见错误

- 坐标轴没有标签/单位
- 图例缺失或位置不当
- 字号过小（打印后看不清）
- 颜色对比度不足
- 框架图箭头方向不清
- 过多装饰性元素分散注意力
