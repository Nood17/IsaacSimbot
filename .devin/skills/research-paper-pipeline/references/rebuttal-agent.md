# Rebuttal Agent - 反驳与修改

## 输入

- 完整论文草稿（`output/paper.md`）
- 审稿意见（`review_output.md`，来自 Review Agent 或用户粘贴的真实 review）
- 修改优先级清单

## 执行流程

### Step 1: 解析审稿意见

将每位 Reviewer 的 Weaknesses 和 Questions 提取为结构化列表：

```json
[
  {
    "reviewer": 1,
    "type": "weakness",
    "id": "R1W1",
    "content": "原始描述",
    "severity": "major | minor",
    "category": "method | experiment | writing | novelty | other"
  }
]
```

### Step 2: 分类与策略制定

对每条意见判断应对策略：

| 策略 | 适用场景 | Rebuttal 中怎么写 |
|------|---------|-----------------|
| **直接回复** | Reviewer 误解了论文内容 | 澄清 + 指出论文中的具体位置 |
| **承认 + 补数据** | 缺少某个实验 | 承认 + 提供补充实验结果 |
| **承认 + 改写** | 表述不清导致的问题 | 承认 + 给出修改后的段落 |
| **承认 + 讨论** | 确实是局限但非致命 | 诚实承认 + 解释为什么不影响核心贡献 + 加入 Limitations |
| **无法解决** | 根本性问题 | 诚实标注，不强行辩护 |

**分类原则：**
- P0 问题（所有 Reviewer 都提到的）必须有实质性回应
- 不要对每个 minor issue 都长篇大论
- Reviewer 误解的情况，先反思是不是论文写得不清楚

### Step 3: 生成 Rebuttal Letter

使用标准 rebuttal 格式：

```markdown
# Rebuttal

We thank all reviewers for their constructive feedback. We address each concern below.

---

## Response to Reviewer 1

**[R1W1] [Weakness 标题的简短概括]**

> [引用 Reviewer 原文]

[回复内容。2-5 句话，直接回答问题。]

[如果涉及修改，展示修改前后的对比：]

**Original (Section X, Paragraph Y):**
> [原文]

**Revised:**
> [修改后的文字]

---

**[R1W2] ...**

...

## Response to Reviewer 2
...

## Response to Reviewer 3
...

---

## Summary of Changes

| Change | Section | Description |
|--------|---------|-------------|
| C1 | 3.2 | Added clarification on ... |
| C2 | 4.3 | Added ablation experiment for ... |
| C3 | 5 | Added limitation discussion on ... |
```

**Rebuttal 写作原则：**
- 语气礼貌但不卑微（"Thank you for this insightful comment" 而不是 "We deeply apologize"）
- 每个回复以直接回答开头，不绕弯子
- 涉及实验的回复要给数据（哪怕是估算的）
- 修改的部分用红色标注或前后对比展示
- 全文控制在会议规定的字数/页数内（多数会议 rebuttal 限制 1 页）

### Step 4: 生成论文修改建议

对论文中需要修改的部分，生成具体到段落级别的修改建议：

```json
[
  {
    "id": "C1",
    "triggered_by": ["R1W1", "R2W3"],
    "section": "3.2",
    "action": "rewrite | add | delete | move",
    "original": "原始段落/句子",
    "revised": "修改后的段落/句子",
    "rationale": "为什么这样改"
  }
]
```

### Step 5: 判断是否需要大改

评估修改的规模：

**小改（直接在 Rebuttal Agent 内完成）：**
- 修改不超过 5 处
- 每处修改不超过 1 段
- 不涉及方法/实验的根本性改变

**大改（触发回到 Writing Agent）：**
- 需要重写整个 section
- 需要新增大量实验
- 方法需要根本性调整
- 多数 Reviewer 给了 reject

如果判断为大改，输出修改方案，并建议用户决定是否启动新一轮写作。

### Step 6: 应用修改

如果是小改，直接在 `output/paper.md` 上应用修改：
1. 逐条应用 Step 4 生成的修改
2. 每次修改后检查上下文一致性
3. 更新 `references.bib`（如新增了引用）

如果是大改，生成修改方案文档 `revision_plan.md`，交由 Writing Agent 执行。

### Step 7: 输出

1. **`output/rebuttal.md`** - Rebuttal Letter
2. **`output/paper_revised.md`** - 修改后的论文（如果执行了修改）
3. **`revision_plan.md`** - 修改方案（如果需要大改）

更新 `research_state.json`：
```json
{
  "phases": {
    "rebuttal": {
      "status": "completed",
      "output_path": "output/rebuttal.md",
      "changes_count": 8,
      "major_revision_needed": false
    }
  },
  "current_phase": "done"
}
```

如果需要大改并决定回到 Writing Agent：
```json
{
  "current_phase": "writing",
  "revision_round": 2,
  "phases": {
    "writing": {"status": "in_progress"},
    "review": {"status": "pending"},
    "rebuttal": {"status": "pending"}
  }
}
```

## Rebuttal 自检

- [ ] 是否回应了每位 Reviewer 的每条 Weakness 和 Question？
- [ ] P0 问题是否都有实质性回应（不是敷衍）？
- [ ] 无法解决的问题是否诚实标注了？
- [ ] 字数/页数是否符合会议 rebuttal 限制？
- [ ] 语气是否专业、礼貌但不卑微？
- [ ] 新增的实验/数据是否真实？
- [ ] 修改建议是否具体到段落级别？
