# 宿主 Agent 集成指南

本 Skill 不包含任何 LLM 调用或 SDK 依赖。所有 LLM 推理和联网操作由宿主 Cursor Agent 执行。本文档说明各 Agent 需要宿主提供的能力。

## 宿主需要的能力

| 能力 | 用途 | 对应 Agent |
|------|------|-----------|
| **WebSearch** | 搜索论文趋势、最新工作 | Idea, Literature |
| **WebFetch** | 访问 arXiv/Semantic Scholar API | Idea, Literature, Review |
| **Shell** | 执行 curl 命令、Python 脚本、LaTeX 编译 | 全部 |
| **Read/Write** | 读写工作目录中的文件 | 全部 |
| **子 Agent** | 并行执行搜索任务 | Literature |
| **AskQuestion** | 让用户做选择（选 idea、确认方向） | Idea |

## API 调用模式

### arXiv API

免费，无需 API Key，有速率限制（3 秒间隔）。

```bash
curl -s "https://export.arxiv.org/api/query?search_query=all:{query}&max_results=30&sortBy=submittedDate&sortOrder=descending"
```

返回 Atom XML，需要解析 `<entry>` 元素。宿主 Agent 直接用 LLM 解析 XML 即可，不需要专门的 XML parser。

### Semantic Scholar API

免费层：100 requests/5 min（无 API Key）。如有 API Key 可提升到 100 requests/1 sec。

**论文搜索：**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=20&fields=title,authors,year,citationCount,venue,externalIds,abstract"
```

**论文详情（通过 arXiv ID）：**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/ARXIV:{arxiv_id}?fields=title,authors,year,citationCount,venue,references,citations"
```

**引用列表：**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references?fields=title,authors,year,citationCount,venue&limit=50"
curl -s "https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations?fields=title,authors,year,citationCount,venue&limit=50"
```

### 速率限制处理

如果 API 返回 429 (Too Many Requests)：
- arXiv：等待 5 秒后重试
- Semantic Scholar：等待 60 秒后重试
- 如果持续 429，减少单次搜索的 `max_results`/`limit`

## 各阶段的宿主调用流程

### Idea Agent 阶段
```
1. 宿主读取 idea-agent.md 获取指令
2. 宿主执行 WebSearch/curl 搜索趋势
3. 宿主用 LLM 推理生成 ideas
4. 宿主执行 curl 做 novelty check
5. 宿主用 AskQuestion 让用户选择
6. 宿主写入 idea_output.json + 更新 state
```

### Literature Agent 阶段
```
1. 宿主读取 literature-agent.md 获取指令
2. 宿主启动 2-3 个子 Agent 并行搜索
3. 宿主合并搜索结果，执行去重排名
4. 宿主执行 curl 做 citation chasing
5. 宿主用 LLM 撰写 Related Work
6. 宿主执行 verify_citations.py 验证引用
7. 宿主写入 literature_pool.json + references.bib + related_work.md
```

### Writing Agent 阶段
```
1. 宿主读取 writing-agent.md 获取指令
2. 宿主读取前序所有 section 文件
3. 宿主用 LLM 撰写 abstract + introduction + conclusion
4. 宿主组装完整论文到 output/paper.md
5. 宿主执行一致性检查 + AI 味检测
```

### 最终输出阶段
```
1. 宿主执行 python scripts/md_to_latex.py 转换格式
2. 宿主执行 bash scripts/build_paper.sh 编译 PDF
3. 如编译失败，宿主读取 log 修复 LaTeX 错误
```

## Cursor 中的使用方式

用户在 Cursor 中可以这样触发：

- "帮我写一篇关于 federated learning on wearable devices 的论文"
  -> 触发全流程，从 Idea Agent 开始

- "帮我做一下这个方向的 literature review"
  -> 只触发 Literature Agent

- "帮我审一下这篇论文" + 粘贴论文内容
  -> 只触发 Review Agent

- "帮我写 rebuttal" + 粘贴 review 内容
  -> 只触发 Rebuttal Agent

宿主 Agent 根据 SKILL.md 中的入口点判断表选择起始阶段。
