# Research Paper Writing Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LaTeX](https://img.shields.io/badge/LaTeX-required-green.svg)](https://www.latex-project.org/get/)

面向 CS 顶会论文写作的 7-Agent Pipeline Skill，运行在 [Claude Code](https://claude.ai/code) 之上。将一个粗糙的研究想法变成一篇投稿就绪的顶会论文，覆盖从选题到 Rebuttal 的完整管线。

## 目录

- [工作流概览](#工作流概览)
- [特性](#特性)
- [安装](#安装)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [管线详解](#管线详解)
- [项目结构](#项目结构)
- [支持会议](#支持会议)
- [质量红线](#质量红线)
- [常见问题](#常见问题)
- [贡献](#贡献)
- [License](#license)

## 工作流概览

```
用户输入（方向/idea/草稿）
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Phase 1        Idea Agent          选题：搜索趋势 → 识别 gap  │
│                                     → 候选 idea → Novelty Check │
├─────────────────────────────────────────────────────────────┤
│  Phase 2        Literature Agent    文献：多源检索 → 去重排名    │
│                                     → Snowball → 分类 → Related Work │
├─────────────────────────────────────────────────────────────┤
│  Phase 3        Method Agent        方法：分析路线 → 架构设计    │
│                                     → Baseline → 伪代码       │
├─────────────────────────────────────────────────────────────┤
│  Phase 4        Experiment Agent    实验：数据集 → 指标         │
│                                     → Ablation → 结果表格      │
├─────────────────────────────────────────────────────────────┤
│  Phase 5        Writing Agent       写作：组装 section         │
│                                     → 润色 → 一致性检查        │
├─────────────────────────────────────────────────────────────┤
│  Phase 5.5      Figures Agent       绘图：扫描占位符 → 生成 SVG │
│                                     → 汇总 PPTX → 更新 LaTeX   │
├─────────────────────────────────────────────────────────────┤
│  Phase 6        Review Agent        审稿：3 Reviewer           │
│                                     → Meta-Review → 预测结果   │
├─────────────────────────────────────────────────────────────┤
│  Phase 7        Rebuttal Agent      反驳：逐条分析 → 分类回复   │
│                                     → 生成 Rebuttal Letter     │
└─────────────────────────────────────────────────────────────┘
```

## 特性

- **7-Agent Pipeline** — 每个 Agent 专注于一个阶段，可独立运行也可串联跑完整管线
- **智能入口判断** — 根据你的输入自动决定从哪个阶段开始，不必每次都从头跑
- **断点续跑** — 基于 `research_state.json` 状态文件，随时可从中断处接续
- **多会议支持** — NeurIPS / ICML / ICLR / CVPR / ACL / ICCSE
- **引用验证** — 4 层校验（arXiv DOI / Semantic Scholar 标题匹配 / 元数据交叉验证）
- **学术绘图** — SVG 矢量图生成 → PPTX 汇总，兼容 PowerPoint 精调
- **LaTeX 全自动输出** — Markdown → LaTeX → PDF 一条命令完成

## 安装

### 前置条件

- **Python 3.9+**
- **LaTeX 发行版**（[TeX Live](https://www.tug.org/texlive/) 或 [MiKTeX](https://miktex.org/)）
- **[Claude Code](https://claude.ai/code)** CLI 环境

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/SGloria/research-paper.git
cd research-paper

# 2. 安装 Python 依赖
pip install -r requirements.txt

# 3. 验证安装
python scripts/verify_citations.py --help
python scripts/md_to_latex.py --help
```

> **说明**：`md_to_latex.py` 和 `verify_citations.py` 仅使用 Python 标准库，无需额外安装依赖。`figure_to_pptx.py` 需要 `requirements.txt` 中的 `python-pptx` 和 `cairosvg`。

### 在 Claude Code 中启用此 Skill

将此仓库路径添加到 Claude Code 的 Skill 配置中，或直接在工作目录下使用 `.claude/settings.local.json` 注册 Skill。

## 快速开始

下面的流程演示从一条研究方向开始，跑完整条管线：

```bash
# 1. 创建工作目录
mkdir -p "my-paper"/{sections,figures/{svg_output,output},data,output}

# 2. 在 Claude Code 中，告诉它你的研究方向
#    例如："我想写一篇关于 BLE wearable 与心理健康预测的 NeurIPS 论文"

# 3. Skill 会自动：
#    - 创建 research_state.json 初始化状态
#    - 进入 Idea Agent，搜索趋势并生成候选选题
#    - 让你选择一个 idea 后，自动推进到 Literature Agent
#    - ... 依次推进，直到产出完整论文
```

如果只想做某个阶段：

```
# 只做文献综述
"帮我做 literature review，方向是 few-shot learning with LLM"

# 只审稿
"帮我模拟审稿这篇论文"（附上草稿）

# 只写 rebuttal
"帮我生成 rebuttal letter"（附上论文和 reviewer 意见）
```

## 使用示例

### 场景一：从零开始写一篇论文

```
用户："我想写一篇关于 diffusion model 做 time series forecasting 的 ICML 论文"

Skill 响应：
  Phase 1 - Idea Agent:
    搜索 arxiv + Semantic Scholar，识别 gap
    生成 3 个候选 idea：
      1. Denoising Diffusion Probabilistic Forecasting (DDPM-based)
      2. Score-based Diffusion for Multivariate Time Series
      3. Conditional Diffusion with Seasonal Decomposition
    评估 novelty 后推荐 #2
    用户确认 → 进入 Phase 2

  Phase 2 - Literature Agent:
    检索 200+ 论文，去重后保留 85 篇
    按方法分类：Score-based / DDPM / SDE-based / Hybrid
    输出 references.bib + sections/related_work.md
    → 进入 Phase 3

  ... (后续阶段类似推进)

  最终产出：
    output/paper.md       → 完整论文 Markdown
    output/paper.tex      → 符合 ICML 格式的 LaTeX
    output/paper.pdf      → 编译后的 PDF
    figures/output/paper_figures.pptx  → 所有图表的 PPTX
```

### 场景二：已有论文草稿，只要审稿

```
用户："帮我模拟审稿这篇论文"（粘贴 paper.md）

Skill → 直接进入 Phase 6 (Review Agent)
  模拟 3 位 Reviewer 给出评审意见
  生成 Meta-Review 和 Accept/Reject 预测
  输出优先修改清单
```

### 场景三：只要生成图表

```
用户："我的论文写好了，帮我生成里面的图表"
      （论文中含有 [FIGURE: ...] 占位符）

Skill → 进入 Phase 5.5 (Figures Agent)
  扫描所有占位符 → 逐个生成 SVG → 汇总到 PPTX
  更新 LaTeX 中的 figure 环境
```

## 管线详解

### 各 Agent 职责

| Agent | 输入 | 输出 | 核心动作 |
|-------|------|------|---------|
| **Idea** | 研究方向/关键词 | `idea_output.json` | 趋势搜索 → Gap 分析 → 候选选题 → Novelty Check |
| **Literature** | 选定 idea | `literature_pool.json`, `references.bib`, `sections/related_work.md` | 多源检索 → 去重排名 → 引用追踪 → 分类 → 写 Related Work |
| **Method** | idea + 文献 | `sections/method.md` | 技术路线分析 → 架构设计 → Baseline 选定 → 伪代码 |
| **Experiment** | 方法设计 | `sections/experiments.md` | 数据集 → 指标 → Ablation Study → 结果表格 |
| **Writing** | 前 4 阶段产出 | `sections/*.md`, `output/paper.md` | 组装 → 写 Abstract/Introduction → 润色 → 一致性检查 |
| **Figures** | paper.md (含占位符) | `figures/svg_output/*.svg`, `figures/output/paper_figures.pptx` | SVG 生成 → 质量检查 → 汇总 PPTX → 更新 LaTeX |
| **Review** | 完整论文草稿 | 评审报告 | 3 Reviewer 模拟审稿 → Meta-Review → Accept/Reject 预测 |
| **Rebuttal** | 论文 + review 意见 | `rebuttal.md` | 逐条分析 → 分类回复 → 生成 Rebuttal Letter |

### 断点续跑机制

所有进度保存在 `research_state.json` 中：

```json
{
  "project_name": "my-paper",
  "target_venue": "neurips_2026",
  "current_phase": "experiment",
  "phases": {
    "idea": {"status": "completed", "output_path": "idea_output.json"},
    "literature": {"status": "completed", "output_path": "literature_pool.json"},
    "method": {"status": "completed", "output_path": "sections/method.md"},
    "experiment": {"status": "pending", "output_path": null},
    ...
  }
}
```

下次对话时 Skill 自动读取此文件，从 `current_phase` 接续。

### 命令行工具

```bash
# 引用验证
python scripts/verify_citations.py references.bib

# Markdown → LaTeX
python scripts/md_to_latex.py output/paper.md output/paper.tex \
  --venue neurips_2026 --bib references.bib

# LaTeX → PDF
bash scripts/build_paper.sh output/paper.tex

# SVG → PPTX
python scripts/figure_to_pptx.py figures/
```

## 项目结构

```
research-paper/
├── SKILL.md                          # Skill 定义与管线总览（Claude Code 注册入口）
├── README.md                         # 本文件
├── LICENSE                           # MIT 许可证
├── requirements.txt                  # Python 依赖
├── scripts/                          # 可执行脚本
│   ├── figure_to_pptx.py             # SVG → PPTX 汇总
│   ├── md_to_latex.py                # Markdown → LaTeX 转换
│   ├── verify_citations.py           # 引用真实性验证
│   └── build_paper.sh                # LaTeX → PDF 编译
├── references/                       # 各 Agent 详细指令（管线运行时读取）
│   ├── idea-agent.md
│   ├── literature-agent.md
│   ├── method-agent.md
│   ├── experiment-agent.md
│   ├── writing-agent.md
│   ├── figures-agent.md
│   ├── review-agent.md
│   ├── rebuttal-agent.md
│   ├── citation-verification.md      # 引用验证协议
│   ├── venue-templates.md            # 会议模板说明
│   └── host-integration.md           # 宿主集成指南
├── templates/                        # 会议 LaTeX 样式文件
│   ├── neurips_2026/
│   ├── icml_2026/
│   ├── iclr_2026/
│   └── iccse_2026/
└── assets/                           # 静态资源
    └── wechat-pay.jpg                # 赞赏码
```

## 支持会议

| 会议 | 领域 | 模板 |
|------|------|------|
| NeurIPS | 机器学习/人工智能 | `templates/neurips_2026/` |
| ICML | 机器学习 | `templates/icml_2026/` |
| ICLR | 表征学习 | `templates/iclr_2026/` |
| CVPR | 计算机视觉 | 内置支持 |
| ACL | 自然语言处理 | 内置支持 |
| ICCSE | 计算机科学与教育 | `templates/iccse_2026/` |

> **注意**：CVPR 和 ACL 使用内置配置，无需单独的模板目录。如需支持其他会议，参考 [venue-templates.md](references/venue-templates.md) 自行添加。

## 质量红线

以下任何一条出现，论文不可提交：

- 引用了不存在的论文（幻觉引用）
- 实验数据或结果是编造的
- 方法描述与实际实现不一致
- Related Work 遗漏了该领域的关键工作
- 论文存在明显的逻辑矛盾

发现上述问题时必须停下来修复，不可跳过。

## 常见问题

<details>
<summary><b>Q: 这个 Skill 生成的论文能直接投稿吗？</b></summary>

Skill 生成的是高质量初稿，覆盖了完整结构和内容框架。但投稿前仍需人工审读、核实实验结果、精调措辞。它解决的是"从 0 到 1"的问题，不是"从 1 到 100"。
</details>

<details>
<summary><b>Q: 我可以只使用其中一两个 Agent 吗？</b></summary>

可以。Skill 会根据你的输入自动判断入口点。比如你说"帮我审稿"，就直接进入 Review Agent，前面的阶段不会运行。
</details>

<details>
<summary><b>Q: 引用验证是怎么工作的？</b></summary>

4 层验证：1) arXiv ID 校验（URL 格式的正确性）；2) Semantic Scholar API 查询（标题匹配）；3) 元数据交叉验证（作者、年份、venue 一致性）；4) 引用完整性检查（所有 \cite 是否都有 bib entry）。
</details>

<details>
<summary><b>Q: 为什么要出 PPTX？</b></summary>

SVG 是学术出版标准格式，但研究人员通常需要在 PowerPoint 中做最后的视觉精调（对齐、颜色、标注）。汇总到 PPTX 可以一次编辑所有图表，也可以直接复制到答辩 PPT 中重用。
</details>

<details>
<summary><b>Q: 运行过程中断网了怎么办？</b></summary>

由于有 `research_state.json` 断点续跑机制，重新开始对话后 Skill 会自动从中断处接续。所有已完成的阶段不需要重做。
</details>

<details>
<summary><b>Q: 是否需要 API Key？</b></summary>

本 Skill 运行在 Claude Code 之上，需要有效的 Anthropic API 订阅。此外，Literature Agent 使用免费的 arXiv API 和 Semantic Scholar API，无需额外申请 Key。
</details>

## 贡献

欢迎贡献！以下是一些你可以参与的方向：

- **新增会议模板** — 在 `templates/` 下添加新会议的 LaTeX 样式文件
- **改进 Agent 指令** — 优化 `references/` 中各 Agent 的 prompt
- **增强脚本功能** — 改进 `scripts/` 中的 Python 工具
- **报告问题** — 通过 GitHub Issues 提交 bug 或功能建议

贡献前请阅读 [SKILL.md](SKILL.md) 了解整体架构。

## License

MIT — 详见 [LICENSE](LICENSE)

---

如果这个项目对你的研究有帮助，欢迎投喂作者一杯咖啡。

<img src="assets/wechat-pay.jpg" width="200" alt="微信赞赏码" />
