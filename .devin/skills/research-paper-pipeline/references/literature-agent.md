# Literature Agent - 文献检索与综述

## 输入

- 选定的 Idea（`idea_output.json`）
- 领域关键词

## 执行流程

### Step 1: 多源检索

从三个来源并行搜索，建议使用子 Agent 加速：

**子 Agent 1 - arXiv 检索：**
```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:{关键词1}+AND+all:{关键词2}&max_results=50&sortBy=submittedDate&sortOrder=descending"
```
- 用 2-3 组不同关键词组合搜索
- 提取每篇论文的 title, authors, abstract, published date, arXiv ID
- 重点关注近 2 年的论文

**子 Agent 2 - Semantic Scholar 检索：**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={关键词}&limit=50&fields=title,authors,year,citationCount,venue,externalIds,abstract,referenceCount,citationCount"
```
- 用 idea 的标题关键词搜索
- 用 idea 的 research question 关键词搜索
- 按引用数排序，获取领域经典论文

**子 Agent 3 - WebSearch 补充：**
- 搜索 "{领域} survey 2024 2025 2026"
- 搜索 "{领域} {方法关键词} benchmark"
- 搜索 "awesome {领域} github" 获取论文列表
- 如果有特定会议，搜索 "{会议} 2025 2026 {领域} accepted"

### Step 2: 去重与排名

**去重规则（按优先级）：**
1. DOI 完全匹配 -> 合并
2. arXiv ID 匹配 -> 合并
3. 标题 Levenshtein 相似度 > 0.85 -> 合并（保留信息更完整的记录）

**透明排名公式：**
```
score = 0.4 * relevance + 0.3 * citation_norm + 0.2 * recency + 0.1 * venue_tier
```

各分量计算方式：
- `relevance`：LLM 判断论文与当前 idea 的相关性（0-1）
- `citation_norm`：`min(citation_count / max_citations_in_pool, 1.0)`
- `recency`：`max(0, 1 - (current_year - pub_year) / 5)`，5 年内线性衰减
- `venue_tier`：顶会(NeurIPS/ICML/ICLR/CVPR/ACL/AAAI)=1.0，顶刊(TPAMI/JMLR/TIP)=0.9，其他知名会议=0.6，workshop/preprint=0.3

将每篇论文的各分量分数记录到 `literature_pool.json`，确保排名可追溯。

选取 Top-30 进入深入分析。

### Step 3: 引用追踪（Snowball）

对排名 Top-10 的论文做 forward + backward citation chasing：

**Backward（参考文献追踪）：**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields=title,authors,year,citationCount,venue&limit=50"
```

**Forward（被引追踪）：**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields=title,authors,year,citationCount,venue&limit=50"
```

从追踪结果中筛选：
- 高引经典论文（被多篇 Top-10 共同引用）
- 最近 1 年的新工作（可能是后续改进）
- 与当前 idea 高度相关但主搜索未命中的论文

新发现的论文加入论文池并重新排名。

### Step 4: 分类聚类

将最终论文池按以下维度分组：

**按技术路线分组（必选）：**
- 每个主要技术路线作为一个组（如 "Transformer-based methods", "GNN-based methods"）
- 每组 3-8 篇论文

**按应用场景分组（如适用）：**
- 不同下游任务或应用领域

**按时间线分组（如适用）：**
- 早期开创性工作
- 中期发展
- 最新 SOTA

为每个分组撰写一段 2-3 句话的总结，概括该组工作的共同特点和发展脉络。

### Step 5: 撰写 Related Work

Related Work 的写作需遵循以下原则：

**结构**：按 Step 4 的分组组织段落，每组一个段落或子段落。

**写作要求**：
- 开头一句话概括该组的主题
- 按时间或逻辑顺序介绍各工作，每篇用 1-2 句话说明其贡献
- 每个段落结尾指出该组方法的共同局限性，自然过渡到下一组或我们的工作
- >= 90% 的论文池中的论文必须被引用到正文中
- 引用格式使用 `[@key]`（后续 LaTeX 转换时自动替换为 `\cite{key}`）

**禁止**：
- 逐篇罗列（"A et al. proposed X. B et al. proposed Y. C et al. proposed Z."）
- 没有分析的纯描述
- 遗漏该领域的关键工作（高引经典论文必须提及）

**推荐模式**：
```
[主题句，概括这一组工作的方向]。
[开创性工作] 最早提出了 [核心概念] [@key1]。
后续工作沿两条路线发展：[路线A] 侧重 [...] [@key2; @key3]，
而 [路线B] 则 [...] [@key4; @key5]。
近期，[@key6] 通过 [...] 取得了显著进展，但仍然面临 [...] 的限制。
```

### Step 6: 引用验证

对论文池中的所有论文执行 4 层验证。详细协议见 [citation-verification.md](citation-verification.md)。

**快速版本：**
1. 有 arXiv ID 的论文：验证 `https://arxiv.org/abs/{id}` 是否可访问
2. 有 Semantic Scholar ID 的论文：验证 API 返回的标题与记录是否匹配
3. 年份/作者一致性：确认来自不同数据源的信息是否一致
4. 如有矛盾，以 Semantic Scholar 或 arXiv 的信息为准

验证失败的论文标记为 `"verified": false`，不进入最终引用列表。

### Step 7: 生成 BibTeX

为所有验证通过的论文生成 `references.bib`。

BibTeX key 格式：`{第一作者姓}{年份}{标题首词}`，如 `vaswani2017attention`。

优先使用 Semantic Scholar 提供的 BibTeX（如果 externalIds 中有 DOI，可通过 `https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=citationStyles` 获取）。

### Step 8: 输出

将以下文件写入工作目录：

1. **`literature_pool.json`** - 结构化论文池：
```json
{
  "total_papers": 45,
  "groups": [
    {
      "name": "Transformer-based Methods",
      "summary": "...",
      "papers": [
        {
          "title": "...",
          "authors": ["..."],
          "year": 2025,
          "venue": "NeurIPS",
          "citation_count": 150,
          "arxiv_id": "2501.12345",
          "semantic_scholar_id": "...",
          "abstract": "...",
          "relevance_score": 0.9,
          "final_score": 0.85,
          "score_breakdown": {"relevance": 0.9, "citation": 0.7, "recency": 0.8, "venue": 1.0},
          "bibtex_key": "author2025title",
          "verified": true
        }
      ]
    }
  ]
}
```

2. **`sections/related_work.md`** - Related Work 初稿

3. **`references.bib`** - BibTeX 文件

更新 `research_state.json`：
```json
{
  "phases": {
    "literature": {
      "status": "completed",
      "output_path": "literature_pool.json",
      "stats": {
        "total_found": 120,
        "after_dedup": 85,
        "after_ranking": 45,
        "verified": 42,
        "groups": 4
      }
    }
  },
  "current_phase": "method"
}
```

## 文献充分性自检

- [ ] 论文池是否覆盖了该领域的关键经典论文（引用数 Top 的必须有）？
- [ ] 是否包含了最近 6 个月的最新工作？
- [ ] 是否有来自不同技术路线的论文（不只是一条线）？
- [ ] 每个分组是否有 3+ 篇论文（太少说明分组不合理或搜索不充分）？
- [ ] 所有引用是否都通过了验证（无幻觉引用）？
- [ ] Related Work 是否自然过渡到了我们的工作（最后一段应该指向 gap）？
