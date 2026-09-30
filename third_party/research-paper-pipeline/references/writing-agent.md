# Writing Agent - 论文撰写

## 设计原则

Writing Agent 的核心定位是 **组装者 + 润色者**，而非重写者。前序 Agent 已生产了 Related Work / Method / Experiments 三大 section，Writing Agent 只负责：
- **新写** Abstract、Introduction、Conclusion + Limitations（这三块前面没人写）
- **原样复用 + 轻量润色** 已有 section（Related Work / Method / Experiments）
- **拼接** 所有 section 成完整论文

**关键约束：绝对不要让 LLM 重新生成已有 section 的全文。** 这是引发 token 爆炸和限流的根源。

## 输入

- Idea（`idea_output.json`）
- Related Work（`sections/related_work.md`）— 直接复用
- Method（`sections/method.md`）— 直接复用
- Experiments（`sections/experiments.md`）— 直接复用
- 文献池（`literature_pool.json`）
- 引用文件（`references.bib`）
- 目标会议（`research_state.json` 中的 `target_venue`）

## 执行流程：分段独立执行

每个 Step 独立完成、独立写入文件，**不要在一次 LLM 调用中生成全文**。

---

### Step 1: 新写 Abstract → `sections/abstract.md`

四段式结构，每段 1-2 句话，总计 ~150 词：

1. **问题/背景**：该领域的核心挑战（1 句）
2. **现有方法的局限**：当前方法为什么不够好（1 句）
3. **我们的方法**：核心 idea 是什么（2-3 句）
4. **结果/意义**：关键 benchmark 结果（1-2 句）

字数严格控制在 150 ± 20 词。

**禁忌：**
- 不要以 "In recent years" 开头
- 不要用 "novel" 超过 1 次
- 不要出现 "to the best of our knowledge"
- 不要列举全部 contributions
- 不要出现超过 2 个具体数字

完成后写入 `sections/abstract.md`，更新 state。

---

### Step 2: 新写 Introduction → `sections/introduction.md`

漏斗结构，~1.5 页，共 5 段：

**第 1 段：大背景（3-4 句）** — 领域的核心问题 + 为什么重要
**第 2 段：具体问题 + 现有方法（4-5 句）** — 聚焦技术问题、概述主流方法
**第 3 段：现有方法局限（3-4 句）** — Research Gap，用 "However" 等转折
**第 4 段：我们的方法（4-5 句）** — "In this paper, we propose ..."
**第 5 段：Contributions（bullet list）** — 3 条，每条 1-2 句

信息来源：读取 `idea_output.json` 获得核心 idea、novelty、contributions；读取 `literature_pool.json` 获得关键引用。**不要自行搜索或编造引用**，全部从已有文件中取。

完成后写入 `sections/introduction.md`，更新 state。

---

### Step 3: 整合 Related Work — 轻量润色

**操作：读取 `sections/related_work.md`，不重写。**

只做以下 4 项检查 + 小修：

1. 最后一段是否自然过渡到我们的方法？若无，补 1-2 句过渡。
2. 引用 key 是否与 `references.bib` 一致？不一致则修正。
3. Introduction 中提到但 Related Work 遗漏的论文？补充到对应分组中。
4. 各分组段落长度是否大致均衡？明显失衡则微调。

**执行方式**：使用 StrReplace 做定点修改，不要整段重写。修改后写回 `sections/related_work.md`。

---

### Step 4: 整合 Method — 轻量润色

**操作：读取 `sections/method.md`，不重写。**

只做以下 5 项检查 + 小修：

1. 是否有方法概述段落？若无，在开头加 3-4 句总结。
2. 是否有 problem formulation / preliminaries 段落定义符号？若无，添加。
3. 每个公式是否有编号和文字解释？不足则补充。
4. 框架图位置是否标注？确认 `[FIGURE: ...]` 占位符正确。
5. 伪代码是否使用 Algorithm 环境格式？

**执行方式**：使用 StrReplace 做定点修改。修改后写回 `sections/method.md`。

---

### Step 5: 整合 Experiments — 轻量润色

**操作：读取 `sections/experiments.md`，不重写。**

只做以下 4 项检查 + 小修：

1. 每个表格前是否有实验设置说明？若无，补 1-2 句。
2. 每个表格后是否有分析段落？若无，补 1-2 段。分析要具体到数字。
3. Ablation 部分是否逐条解释了每个组件的贡献？不足则补。
4. 若有不如 baseline 的结果，是否诚实分析了原因？

**执行方式**：使用 StrReplace 做定点修改。修改后写回 `sections/experiments.md`。

---

### Step 6: 新写 Conclusion + Limitations → `sections/conclusion.md`

**Conclusion（1 段）：**
- 重述核心贡献（换个说法，不要复制 Abstract）
- 总结关键实验发现
- 展望未来方向（1-2 句）

**Limitations（1 段）：**
- 诚实列出 2-3 个局限性
- 每个局限性说明原因 + 可能的解决方向
- 语调：honest acknowledgment + future direction

完成后写入 `sections/conclusion.md`，更新 state。

---

### Step 7: 全文组装 — 纯文件拼接，不经过 LLM

**这是最关键的优化：组装阶段不调用 LLM，只做机械拼接。**

读取以下文件，按顺序拼接写入 `output/paper.md`：

```
sections/abstract.md
sections/introduction.md
sections/related_work.md
sections/method.md
sections/experiments.md
sections/conclusion.md
```

拼接模板：

```markdown
# [论文标题]

## Abstract
[读取 sections/abstract.md 的内容]

## 1. Introduction
[读取 sections/introduction.md 的内容]

## 2. Related Work
[读取 sections/related_work.md 的内容]

## 3. Method
[读取 sections/method.md 的内容]

## 4. Experiments
[读取 sections/experiments.md 的内容]

## 5. Conclusion
[读取 sections/conclusion.md 中 Conclusion 部分]

## Limitations
[读取 sections/conclusion.md 中 Limitations 部分]

## References
[引用 references.bib]
```

**执行方式**：使用 Read 工具逐个读取文件内容，用 Write 工具写入 `output/paper.md`。全程不需要 LLM 生成任何内容。

---

### Step 8: 一致性检查 — 目标明确的定点扫描

组装完成后，对 `output/paper.md` 做以下检查。每项检查单独执行，发现问题用 StrReplace 修复。

**术语一致性：**
- 用 Grep 搜索方法名的不同拼写变体，统一为一种
- 用 Grep 搜索同一概念的不同称呼，统一为一种

**符号一致性：**
- 扫描数学符号（`$...$`），检查同一变量是否前后一致

**引用完整性：**
- 提取所有 `[@key]` 标记，对照 `references.bib` 检查是否每个 key 都有对应条目
- 提取 `references.bib` 中所有 key，检查是否每个都在正文中被引用
- 去除未引用的 bib 条目

**图表引用：**
- 检查所有 Figure / Table 占位符是否在正文中被引用
- 统一引用格式（Figure 1 / Fig. 1 / Table 1，选一种全文统一）

**页数估算：**
- 按 250 词/页估算正文页数，对照会议要求检查

**执行方式**：每项检查输出一个简短报告（1-3 行），有问题则直接修复。无问题则跳过。不要把检查结果写入论文。

---

### Step 9: 输出 + 更新状态

1. 确认 `output/paper.md` 已就绪
2. 更新 `research_state.json`：`writing.status = "completed"`
3. 告知用户论文草稿就绪，可以进入 Review Agent

## AI 味检测清单

在 Step 1（Abstract）和 Step 2（Introduction）新写完成后，对新写内容逐项检查。
**只检查新写的内容**，不要对已有 section 做全面重写。

**高频踩雷句式（绝对禁用）：**
- "In recent years, ... has attracted significant attention"
- "With the rapid development of ..."
- "To the best of our knowledge"
- "It is worth noting that"
- "Extensive experiments demonstrate the effectiveness"
- "plays a crucial/vital/pivotal role"
- "a plethora of" / "delve into" / "leveraging the power of" / "in a nutshell"

**结构性 AI 味：**
- 过度使用 "Firstly, ... Secondly, ... Thirdly, ..."
- 每段开头都是 "Moreover" / "Furthermore" / "Additionally"
- 同一意思用三种不同说法重复表达
- 过于对称的段落结构

**修复策略：**
- 用更具体的描述替换空泛的形容词
- 变化段落长度和句式结构
- 开头直接切入主题
- 用数据说话
