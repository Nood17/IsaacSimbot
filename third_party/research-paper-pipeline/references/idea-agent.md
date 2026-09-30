# Idea Agent - 选题与创意生成

## 输入

- 领域关键词（如 "federated learning", "BLE wearable + mental health"）
- 研究兴趣描述（可选）
- 已有工作/系统（可选）

## 执行流程

### Step 1: 领域趋势扫描

并行执行以下搜索：

**arXiv 最新 preprint（近 6 个月）：**
```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:{关键词1}+AND+all:{关键词2}&max_results=30&sortBy=submittedDate&sortOrder=descending"
```

**WebSearch 搜索顶会趋势：**
- "{领域} survey 2025 2026"
- "{领域} NeurIPS ICML ICLR 2025 2026 accepted papers"
- "{领域} benchmark SOTA 2025 2026"

**Semantic Scholar 高引论文：**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={关键词}&limit=20&fields=title,authors,year,citationCount,venue,abstract&year=2024-2026&sort=citationCount:desc"
```

### Step 2: Research Gap 识别

从搜索结果中提取以下信息：

1. **当前主流方法**：列出 3-5 个主流技术路线
2. **已解决的问题**：这些方法各自解决了什么
3. **未解决的限制**：每个方法的明确局限性（从论文的 Limitations 和 Future Work 段落提取）
4. **新兴方向**：最近 3 个月出现的新趋势

Gap 识别策略：
- 方法 A 在场景 X 效果好，但在场景 Y 失败 -> 场景 Y 的 gap
- 方法 A 和方法 B 各有优势但未被结合 -> 融合的 gap
- 现有方法都依赖假设 Z，但假设 Z 在现实中不成立 -> 放松假设的 gap
- 某个相邻领域的技术尚未被引入到当前领域 -> 跨领域迁移的 gap
- 缺乏统一的 benchmark 或评估标准 -> 基准建设的 gap

### Step 3: 生成候选 Idea

为每个识别到的 Gap 生成一个研究 Idea。每个 Idea 包含：

```json
{
  "title_en": "英文标题",
  "title_zh": "中文标题",
  "research_question": "用一个问句表达核心研究问题",
  "gap": "它要填补的 research gap 是什么",
  "novelty": [
    "与现有工作的核心区别点 1",
    "与现有工作的核心区别点 2"
  ],
  "contributions": [
    "Contribution 1: ...",
    "Contribution 2: ...",
    "Contribution 3: ..."
  ],
  "approach_sketch": "方法的一句话概述",
  "difficulty": "low | medium | high",
  "resource_requirements": "需要什么数据/计算资源/设备",
  "potential_venues": ["NeurIPS", "ICML"],
  "similar_works": []
}
```

生成 3-5 个候选 Idea，确保覆盖不同类型：
- 至少 1 个方法创新型（新算法/新架构）
- 至少 1 个应用创新型（已有方法应用到新场景）
- 至少 1 个系统/实证型（新 benchmark/大规模实验/系统实现）

### Step 4: Novelty Check

对每个候选 Idea，用 Semantic Scholar 搜索最相似的已有工作：

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={idea标题关键词}&limit=10&fields=title,authors,year,citationCount,venue,abstract"
```

对每篇搜索结果，判断与当前 Idea 的重叠度：
- **高重叠（>0.8）**：idea 的核心贡献已被完成，需要重新定位或放弃
- **中等重叠（0.5-0.8）**：有相关工作但角度不同，需要明确差异化
- **低重叠（<0.5）**：novelty 较好

将最相似的 3 篇论文记录到 `similar_works` 字段。

如果某个 Idea 的所有 top 相似工作都是高重叠，标记为 "novelty_risk: high"，建议用户谨慎选择。

### Step 5: 用户选择

将所有候选 Idea 呈现给用户，包含：
- 标题
- Research Question
- Novelty 点
- Contributions
- 难度评估
- 最相似的已有工作及重叠度评估

使用 AskQuestion 工具让用户选择一个 Idea（或要求修改/组合）。

### Step 6: 输出

将选定的 Idea 写入 `idea_output.json`。

更新 `research_state.json`：
```json
{
  "phases": {
    "idea": {
      "status": "completed",
      "output_path": "idea_output.json"
    }
  },
  "current_phase": "literature",
  "selected_idea_index": 0
}
```

## Idea 质量自检

生成 Idea 后，用以下清单自检：

- [ ] Research Question 是否清晰、可回答？
- [ ] Gap 是否真实存在（有论文证据支撑）？
- [ ] Novelty 点是否明确（能用一句话说清和已有工作的区别）？
- [ ] Contributions 是否具体（不是 "we propose a novel method" 这种空话）？
- [ ] 难度评估是否现实？
- [ ] 目标会议是否匹配（系统论文别投 NLP 会议）？
