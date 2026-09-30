# 引用验证协议

4 层验证管线，确保论文中的每条引用都指向真实存在的论文。

## 为什么需要引用验证

LLM 生成的引用有两类常见错误：
1. **完全幻觉**：论文根本不存在（虚构的标题、作者）
2. **张冠李戴**：论文存在但引用的内容/结论与原文不符

两类错误都是学术不端，必须在投稿前彻底清除。

## 4 层验证管线

### Layer 1: 标识符验证

对每条引用，检查其标识符是否有效：

**arXiv ID 验证：**
```bash
curl -s -o /dev/null -w "%{http_code}" "https://arxiv.org/abs/{arxiv_id}"
```
- HTTP 200 = 存在
- HTTP 404 = 不存在，标记为验证失败

**DOI 验证：**
```bash
curl -s -o /dev/null -w "%{http_code}" "https://doi.org/{doi}"
```
- HTTP 200 或 301/302（重定向）= 存在
- HTTP 404 = 不存在

没有 arXiv ID 也没有 DOI 的论文，直接进入 Layer 2。

### Layer 2: Semantic Scholar 标题匹配

用论文标题在 Semantic Scholar 中搜索：

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={标题}&limit=5&fields=title,authors,year,venue,externalIds"
```

匹配标准：
- 对返回的每条结果，计算与目标标题的 Levenshtein 相似度
- 相似度 > 0.85 视为匹配
- 匹配后，用 Semantic Scholar 返回的信息更新/验证 BibTeX 条目

未匹配的论文标记为 `"verified": false, "reason": "not_found_in_semantic_scholar"`。

### Layer 3: 元数据交叉校验

对 Layer 2 匹配成功的论文，交叉校验关键元数据：

| 字段 | 校验规则 |
|------|---------|
| 年份 | BibTeX 中的年份与 Semantic Scholar 返回的年份相差不超过 1 年 |
| 作者 | 第一作者姓氏匹配（容忍拼写变体） |
| Venue | 会议/期刊名称匹配（容忍缩写，如 "NeurIPS" = "Neural Information Processing Systems"） |

任一字段不匹配，标记为 `"verified": "partial", "reason": "metadata_mismatch"`，并输出不匹配的具体字段。

### Layer 4: LLM 相关性判断

对所有通过前 3 层的引用，检查引用的相关性：

对论文中每处引用 `[@key]`，提取引用所在的句子和上下文（前后各 1 句），判断：
- 引用的论文是否确实支撑了该句话的 claim？
- 引用的论文是否是该 claim 的最佳引用？

标记不相关的引用为 `"relevance": "low"`，建议替换或删除。

## 验证结果汇总

```json
{
  "total_citations": 45,
  "verified": 42,
  "failed": 2,
  "partial": 1,
  "failed_details": [
    {"key": "fake2024paper", "reason": "not_found_anywhere", "action": "remove"},
    {"key": "wrong2023title", "reason": "title_mismatch", "action": "fix_title"}
  ],
  "low_relevance": [
    {"key": "tangential2024work", "context": "...", "suggestion": "replace_with_more_relevant"}
  ]
}
```

## 使用脚本验证

Layer 1-3 可通过脚本自动化：
```bash
python scripts/verify_citations.py references.bib --output verification_report.json
```

Layer 4 需要 LLM 介入，由宿主 Agent 读取论文全文后执行。

## 处理验证失败

- **完全幻觉**：立即从 `references.bib` 删除，并修改论文中引用该论文的段落
- **元数据不匹配**：用 Semantic Scholar 的数据更新 BibTeX
- **低相关性**：替换为更相关的论文，或修改引用所在句子的 claim
