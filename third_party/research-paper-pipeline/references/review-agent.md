# Review Agent - 模拟审稿

## 输入

- 完整论文草稿（`output/paper.md`）
- 目标会议（`research_state.json` 中的 `target_venue`）
- 文献池（`literature_pool.json`，用于检查 related work 完整性）

## 执行流程

### Step 1: 审稿前准备

**确定审稿标准**：根据目标会议的审稿指南设置评分标准。

主要顶会的审稿侧重：
- **NeurIPS**：novelty, significance, clarity, correctness, reproducibility
- **ICML**：technical quality, novelty, significance, clarity
- **ICLR**：soundness, contribution, presentation, related work coverage
- **CVPR**：technical novelty, experimental validation, presentation quality
- **ACL/EMNLP**：originality, quality, significance, clarity, soundness

**设置锚定论文**（借鉴 Idea2Paper）：

用 WebSearch 搜索目标会议近年的 accepted/rejected 论文分数：
- "{会议} 2025 openreview scores"
- "{会议} 2024 accepted paper reviews"

选择 2-3 篇锚定论文：
- 1 篇强 accept（score 7-8）：代表高质量标准
- 1 篇 borderline（score 5-6）：代表通过门槛
- 1 篇 reject（score 3-4）：代表常见问题

### Step 2: 模拟 Reviewer 1（方法论专家）

以该领域资深研究者的视角审稿，重点关注：

**Technical Soundness：**
- 方法在数学/逻辑上是否正确？
- 假设是否合理？是否有隐含的强假设未被声明？
- 理论分析（如有）是否严谨？
- 算法是否收敛？复杂度分析是否正确？

**Novelty：**
- 与最相似的已有工作相比，核心创新是什么？
- 创新是实质性的还是 incremental 的？
- 是否只是简单组合已有技术？

**Significance：**
- 这个问题本身是否重要？
- 解决方案是否有足够的影响力？
- 是否只在特定狭窄场景下有用？

输出格式：
```markdown
## Reviewer 1 (方法论专家)

**Overall Score**: X/10
**Confidence**: X/5

### Summary
[2-3 句话概括论文核心内容和贡献]

### Strengths
1. [具体优点，引用论文中的具体内容]
2. [...]
3. [...]

### Weaknesses
1. [具体问题，指出论文中的具体位置]
2. [...]
3. [...]

### Questions for Authors
1. [需要作者回答的问题]
2. [...]

### Minor Issues
- [格式/语法/表述问题]

### Recommendation
[Accept / Weak Accept / Borderline / Weak Reject / Reject]
[理由，2-3 句话]
```

### Step 3: 模拟 Reviewer 2（实验主义者）

以实验导向的审稿人视角，重点关注：

**实验充分性：**
- 数据集选择是否合理、充分？
- 是否有该领域的标准 benchmark 被遗漏？
- 实验数量是否足以支撑论文的 claims？

**Baseline 公平性：**
- Baseline 是否包含当前 SOTA？
- 是否有意避开了某些强 baseline？
- Baseline 的实验设置是否与本方法一致？
- Baseline 结果来源是否可靠（原论文 vs 复现）？

**Ablation 质量：**
- 是否验证了每个核心组件的贡献？
- 消融实验的结论是否明确？
- 有没有关键的消融缺失？

**复现性：**
- Implementation details 是否足够详细？
- 超参数是否完整报告？
- 是否提供了代码/数据？
- 随机性是否处理（多次运行 + 标准差）？

**结果分析：**
- 是否只报告正面结果而忽略负面结果？
- 改进幅度是否有统计显著性？
- 效率分析是否充分？

同样输出标准审稿格式。

### Step 4: 模拟 Reviewer 3（写作挑剔者）

以注重 presentation quality 的审稿人视角，重点关注：

**Clarity：**
- 论文的核心 idea 是否能在读完 Abstract + Introduction 后就理解？
- 方法部分的描述是否清晰（非该领域的人能否理解大致思路）？
- 符号是否一致？是否有未定义就使用的符号？

**Organization：**
- 各 section 的比例是否合理？
- 信息是否放在了正确的位置（method 里有没有混入 experiment 的内容）？
- 段落之间的逻辑衔接是否顺畅？

**Related Work：**
- 是否覆盖了该领域的关键工作？
- 分组是否合理？
- 是否清晰地指出了与本工作的区别？

**Figures & Tables：**
- 图表是否清晰、信息量充分？
- caption 是否足够详细（不看正文也能理解图表内容）？
- 图表的字体大小是否合适？

**Writing Quality：**
- 是否有语法错误？
- 是否有 AI 味过重的表述？
- 句式是否过于单调？

同样输出标准审稿格式。

### Step 5: 锚定评分

将三位 Reviewer 的评分与锚定论文对比：

```markdown
## 锚定对比

**锚定论文 A**（strong accept, 7.5 分）:
- [论文标题] @ [会议]
- 核心优势：[...]

**锚定论文 B**（borderline, 5.5 分）:
- [论文标题] @ [会议]
- 核心问题：[...]

**本论文相对位置**：
- 与锚定论文 A 相比：[优/劣势分析]
- 与锚定论文 B 相比：[优/劣势分析]
- 预估分数区间：[X.X - Y.Y]
```

### Step 6: Meta-Review

综合三位 Reviewer 的意见，生成 Meta-Review：

```markdown
## Meta-Review (Area Chair)

**Average Score**: X.X / 10
**Score Range**: [min] - [max]

### Consensus Strengths
[所有 Reviewer 都认可的优点]

### Consensus Weaknesses
[多数 Reviewer 指出的共同问题]

### Key Disagreements
[Reviewer 之间的分歧，如有]

### Accept/Reject Prediction
**Prediction**: [Accept / Borderline Accept / Borderline Reject / Reject]
**Confidence**: [High / Medium / Low]
**Reasoning**: [基于分数、锚定对比和 weakness 严重程度的判断]
```

### Step 7: 优先修改清单

按影响力排序，列出需要修改的问题：

```markdown
## 修改优先级

### P0 (Must Fix - 不修不行)
1. [问题描述] → [建议的修改方向]
2. [...]

### P1 (Should Fix - 修了大幅提升)
1. [问题描述] → [建议的修改方向]
2. [...]

### P2 (Nice to Have - 有余力再修)
1. [问题描述] → [建议的修改方向]
2. [...]
```

### Step 8: 输出

将所有审稿内容写入 `review_output.md`，包含：
- 3 份独立 Review
- 锚定对比
- Meta-Review
- 修改优先级清单

更新 `research_state.json`：
```json
{
  "phases": {
    "review": {
      "status": "completed",
      "output_path": "review_output.md",
      "scores": {
        "reviewer_1": 6,
        "reviewer_2": 5,
        "reviewer_3": 7,
        "average": 6.0,
        "prediction": "borderline_accept"
      }
    }
  },
  "current_phase": "rebuttal"
}
```
