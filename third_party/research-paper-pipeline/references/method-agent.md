# Method Agent - 方法设计

## 输入

- 选定的 Idea（`idea_output.json`）
- 文献池（`literature_pool.json`）
- Related Work 初稿（`sections/related_work.md`）

## 执行流程

### Step 1: 现有方法分析

从 `literature_pool.json` 的分组中提取每个技术路线的核心特点：

对每组方法，总结：
- 核心思路（一句话）
- 关键组件/模块
- 优势
- 局限性（从论文的 experiments/limitations 提取）
- 代表性论文

生成一个 **方法对比表**：

```markdown
| Method | Core Idea | Strengths | Limitations | Representative Papers |
|--------|-----------|-----------|-------------|----------------------|
| 路线 A | ... | ... | ... | [@key1], [@key2] |
| 路线 B | ... | ... | ... | [@key3], [@key4] |
```

### Step 2: 方法结构设计

基于 Idea 的 `approach_sketch`，设计完整的方法结构：

**2.1 总体架构**

用文字描述方法的整体流程，包含：
- 输入是什么，输出是什么
- 分为几个主要模块/阶段
- 各模块之间的数据流

同时描述一个方法框架图（用 Mermaid 或文字描述，Writing Agent 后续转为 LaTeX figure）：
```
图描述：
- 左侧输入 -> 模块A -> 模块B -> 模块C -> 右侧输出
- 模块A和模块C之间有跳跃连接
- 模块B内部包含子模块B1和B2
```

**2.2 各模块详细设计**

对每个核心模块，给出：
- 模块名称
- 输入/输出
- 核心操作（数学公式用 LaTeX 格式，如 `$\mathcal{L} = \mathcal{L}_{cls} + \lambda \mathcal{L}_{reg}$`）
- 与现有方法的差异（novelty 体现在哪）
- 设计动机（为什么这样做而不是那样做）

**2.3 损失函数设计（如适用）**

- 总损失函数的组成
- 各项的含义和权重
- 为什么选择这些损失项

### Step 3: Baseline 选定

从文献池中选取 3-5 个 Baseline，遵循以下原则：

**必选 Baseline：**
- 该领域当前 SOTA（至少 1 个）
- 最经典的方法（被广泛对比的 baseline）
- 与本方法最相似的工作（最直接的竞争者）

**可选 Baseline：**
- 不同技术路线的代表方法
- 最近发表的强 baseline

输出 Baseline 列表：
```json
[
  {
    "name": "方法名",
    "paper": "论文标题",
    "bibtex_key": "author2025title",
    "why_selected": "选择理由",
    "type": "SOTA | classic | closest_competitor | different_paradigm",
    "code_available": true,
    "code_url": "https://github.com/..."
  }
]
```

### Step 4: 算法伪代码

用 Algorithm 环境格式撰写核心算法的伪代码：

```
Algorithm 1: [方法名]
Input: [输入描述]
Output: [输出描述]
Parameters: [超参数列表]

1: [初始化步骤]
2: for each [迭代单元] do
3:   [核心操作步骤 1]
4:   [核心操作步骤 2]
5:   [条件判断/分支]
6: end for
7: return [输出]
```

伪代码要求：
- 足够详细以支撑复现
- 使用标准数学符号
- 核心创新步骤用注释标注

### Step 5: 理论分析（如适用）

如果方法有理论贡献，给出：
- 关键定理/命题的非正式陈述
- 证明思路的简要概述
- 时间/空间复杂度分析
- 与 Baseline 方法的复杂度对比

### Step 6: 输出

将方法设计写入 `sections/method.md`，包含：
- 方法概述段落
- 各模块详细描述
- 数学公式
- 框架图描述（`[FIGURE: ...]` 标注）
- 算法伪代码

同时将 Baseline 列表写入 `research_state.json` 或独立的 `baselines.json`。

更新 `research_state.json`：
```json
{
  "phases": {
    "method": {
      "status": "completed",
      "output_path": "sections/method.md"
    }
  },
  "current_phase": "experiment"
}
```

## 方法设计自检

- [ ] 方法的创新点是否清晰（能用一段话说清和现有方法的区别）？
- [ ] 各模块的设计动机是否合理（不是为了新而新）？
- [ ] 数学符号是否一致（同一个变量全文用同一个符号）？
- [ ] 伪代码是否足够详细以支撑复现？
- [ ] 框架图是否清晰展示了数据流？
- [ ] Baseline 选择是否公平全面（没有故意避开强 baseline）？
