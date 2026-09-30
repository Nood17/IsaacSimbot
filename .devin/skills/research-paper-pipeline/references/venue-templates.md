# 顶会模板规范

各主要 CS 顶会的论文格式要求速查。Writing Agent 和 LaTeX 转换脚本使用此文件确定格式参数。

## NeurIPS

| 参数 | 要求 |
|-----|------|
| 页数限制 | 正文 9 页，参考文献不限，附录不限 |
| 列数 | 单栏 |
| 字体 | Times, 10pt |
| 页边距 | 1in all sides |
| Abstract | 不超过 300 词 |
| 匿名 | 双盲 |
| 模板 | `neurips_2026.sty` |
| 引用格式 | `\citep{}` / `\citet{}` (natbib) |
| Checklist | 必须填写 NeurIPS Paper Checklist |

## ICML

| 参数 | 要求 |
|-----|------|
| 页数限制 | 正文 8 页，参考文献不限，附录最多 12 页 |
| 列数 | 双栏 |
| 字体 | Times, 10pt |
| Abstract | 不超过 200 词 |
| 匿名 | 双盲 |
| 模板 | `icml2026.sty` |
| 引用格式 | `\citep{}` / `\citet{}` (natbib) |

## ICLR

| 参数 | 要求 |
|-----|------|
| 页数限制 | 正文 9 页（含图表），参考文献不限，附录不限 |
| 列数 | 单栏 |
| 字体 | Times, 10pt |
| Abstract | 不超过 250 词 |
| 匿名 | 双盲 |
| 模板 | `iclr2026_conference.sty` |
| 引用格式 | `\citep{}` / `\citet{}` (natbib) |
| 特殊要求 | 投稿到 OpenReview |

## CVPR

| 参数 | 要求 |
|-----|------|
| 页数限制 | 正文 8 页，参考文献额外 2 页 |
| 列数 | 双栏 |
| 字体 | Times, 10pt |
| Abstract | 无明确字数限制，建议 150 词以内 |
| 匿名 | 双盲 |
| 模板 | `cvpr.sty` |
| 引用格式 | `\cite{}` 标准 |

## ACL / EMNLP

| 参数 | 要求 |
|-----|------|
| 页数限制 | 长文 8 页，短文 4 页，参考文献不限 |
| 列数 | 双栏 |
| 字体 | Times, 11pt |
| Abstract | 不超过 200 词 |
| 匿名 | 双盲（ARR 审稿） |
| 模板 | `acl.sty` |
| 引用格式 | `\citep{}` / `\citet{}` (natbib) |
| 特殊要求 | Limitations section 必须有；Ethics Statement 鼓励但不强制 |

## AAAI

| 参数 | 要求 |
|-----|------|
| 页数限制 | 正文 7 页 + 参考文献 1 页 + 附录 |
| 列数 | 双栏 |
| 字体 | Times, 10pt |
| 匿名 | 双盲 |
| 模板 | `aaai26.sty` |
| 引用格式 | `\cite{}` 标准 |

## IEEE ICCSE 2026

> **Invited Session 7: New Technologies, Methods, and Models in Computer Experiment Teaching**
> Session Chair: Li Shanshan (Tsinghua University), Co-chair: Fan Xuesong (Peking University)

| 参数 | 要求 |
|-----|------|
| 页数限制 | 正文 4–6 页（含图表和参考文献），IEEE 标准格式 |
| 列数 | 双栏 |
| 字体 | Times, 10pt |
| 纸张 | US Letter (8.5" × 11") |
| Abstract | 不超过 200 词 |
| 匿名 | 非盲审（正常署名） |
| 模板 | IEEE Conference Template (`IEEEtran.cls`) |
| 引用格式 | `\cite{}` IEEE 标准编号引用 |
| 投稿系统 | EasyChair: https://easychair.org/conferences/?conf=iccse2026 |
| 投稿截止 | 2026-05-15 |
| 录用通知 | 2026-06-15 |
| 终稿提交 | 2026-06-20 |
| Camera-ready | 2026-07-15 |
| 会议日期 | 2026-07-21 ~ 07-25，布达佩斯 Óbuda University |
| 会议主题 | AI-driven Educational Digital Innovation for the Belt and Road Initiative (BRI) |
| 检索 | IEEE Xplore, EI Compendex |

**Session 7 征稿方向**：
- 实践教育理论及其在计算机领域的实现
- 计算机实验教学体系构建与实验案例设计
- AI 赋能的计算机教学实验系统建设
- 未来技术背景下的计算机人才培养教学与实验体系
- AI 大模型背景下的计算机实践教育
- 计算机虚拟仿真实验平台建设与资源共享
- 实践教学的科学评估体系与监控机制
- 计算机与应用系统中复杂工程问题的研究与实践
- 计算机实验技术创新与实验设备开发

**写作注意事项（ICCSE 特别）**：
- 非盲审，正常填写作者信息和单位
- 正文需包含完整的 Introduction / Related Work / Method / Experiments / Conclusion 结构
- 图表需清晰，建议使用 IEEE 标准双栏排版的图表尺寸
- 参考文献使用 IEEE 编号格式（[1], [2], ...），不使用作者-年份格式
- 投稿时选择 Invited Session 7 作为 track

## 通用写作注意事项

- **双盲**：正文中不要出现作者信息、"our previous work [X]" 这种泄露身份的表述、致谢中不要提具体人名/机构
- **页数**：宁可在限制内写紧凑，也不要为凑页数注水
- **图表**：图要高清（300 dpi+），文字要可读（不要缩太小）
- **引用**：区分 `\citet`（作者名出现在句中，如 "Vaswani et al. (2017)"）和 `\citep`（括号引用，如 "(Vaswani et al., 2017)"）
- **数学**：行内公式用 `$...$`，独立公式用 `equation` 环境并编号
- **代码/URL**：投稿版本中如果要匿名，用 anonymous GitHub 或 anonymous.4open.science
