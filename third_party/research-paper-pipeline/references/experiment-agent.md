# Experiment Agent - 实验方案设计

## 输入

- 方法设计（`sections/method.md`）
- Baseline 列表（`baselines.json` 或 `research_state.json`）
- 文献池（`literature_pool.json`）
- 用户的真实实验数据/代码（可选）

## 执行流程

### Step 1: 数据集选择

从文献池中统计 Baseline 论文使用的数据集，选择实验数据集：

**选择原则：**
- 至少 1 个被多数 Baseline 使用的标准 benchmark（公平对比）
- 至少 1 个能体现本方法优势的数据集（差异化场景）
- 如果本方法针对特定场景，加入该场景的专用数据集

对每个数据集记录：
```json
{
  "name": "数据集名称",
  "description": "简要描述",
  "size": "样本数/规模",
  "split": "训练/验证/测试划分方式",
  "source": "下载链接或来源",
  "used_by": ["baseline1", "baseline2"],
  "why_selected": "选择理由"
}
```

### Step 2: 评估指标设计

**主指标**：选择该领域通用的核心指标（从 Baseline 论文中提取最常用的）

**辅助指标**：补充能体现本方法独特优势的指标

对每个指标记录：
```json
{
  "name": "指标名称",
  "formula": "计算公式（LaTeX格式）",
  "range": "取值范围",
  "higher_is_better": true,
  "type": "primary | secondary",
  "why": "选择理由"
}
```

**指标选择禁忌：**
- 不要只选有利于自己方法的指标
- 不要忽略该领域的标准指标
- 如果引入新指标，必须说明动机

### Step 3: 实验设置

撰写 Implementation Details，包含：

**训练设置：**
- 优化器及参数（lr, batch_size, epochs, scheduler）
- 硬件环境（GPU 型号、数量）
- 随机种子处理（多次运行取平均 + 标准差）
- 预训练模型（如使用）

**Baseline 复现说明：**
- 有官方代码的：使用官方实现，标注版本/commit
- 无官方代码的：自行实现或引用第三方复现，标注来源
- 所有 Baseline 使用相同的训练设置（公平对比）

**统计显著性：**
- 报告均值 +/- 标准差
- 如适用，进行统计检验（t-test / Wilcoxon）

### Step 4: 主实验结果表格

设计主实验结果表格模板（待填充真实数据）：

```markdown
| Method | Dataset1-Metric1 | Dataset1-Metric2 | Dataset2-Metric1 | Dataset2-Metric2 |
|--------|------------------|------------------|------------------|------------------|
| Baseline1 [@key] | - | - | - | - |
| Baseline2 [@key] | - | - | - | - |
| Baseline3 [@key] | - | - | - | - |
| **Ours** | **-** | **-** | **-** | **-** |
```

表格设计原则：
- 我们的方法放最后一行，加粗
- 最优结果加粗，次优加下划线
- 如果数据来自原论文，标注 "*"；如果是复现结果，标注 "+"
- 表格标题说明实验设置的关键信息

### Step 5: Ablation Study 设计

设计至少 3 组 ablation 实验，验证各核心组件的贡献：

**Ablation 类型：**

1. **组件消融**：逐个移除方法的核心模块
   - Full model
   - w/o Module A
   - w/o Module B
   - w/o Module C

2. **超参数敏感性**：关键超参数的影响
   - 选 2-3 个最重要的超参数
   - 每个测试 4-5 个取值

3. **设计选择验证**：证明设计选择的合理性
   - 替换核心模块为更简单的替代方案
   - 对比不同 backbone/encoder 的效果

为每组 ablation 设计对应的表格或图表模板。

### Step 6: 补充实验（可选）

根据方法特点，选择性添加：

- **效率分析**：训练时间、推理时间、参数量、FLOPs 对比
- **可视化分析**：attention map、t-SNE、生成结果示例
- **Case Study**：具体样本的定性分析
- **Scalability**：不同数据规模/模型规模的表现
- **Robustness**：噪声/对抗样本下的表现

### Step 7: 真实数据接入（如用户提供）

如果用户提供了真实实验数据或代码：

1. 读取数据文件，理解数据格式和维度
2. 将数据填入设计好的表格模板
3. 自动生成描述性统计（均值、标准差、最优标注）
4. 检查结果是否合理（是否超出已知 SOTA 太多或太少）

如果用户没有真实数据，表格中用 `-` 占位，并在输出中标注 "待填充真实实验结果"。

### Step 8: 输出

将实验方案写入 `sections/experiments.md`，包含：
- Datasets 描述
- Evaluation Metrics 定义
- Implementation Details
- 主实验结果表格（模板或真实数据）
- Ablation Study 表格
- 补充实验（如适用）

更新 `research_state.json`：
```json
{
  "phases": {
    "experiment": {
      "status": "completed",
      "output_path": "sections/experiments.md"
    }
  },
  "current_phase": "writing"
}
```

## 实验设计自检

- [ ] 数据集选择是否覆盖了标准 benchmark？
- [ ] 评估指标是否包含该领域通用指标（不要只选有利于自己的）？
- [ ] Baseline 对比是否公平（相同设置、相同数据划分）？
- [ ] Ablation Study 是否覆盖了所有核心组件？
- [ ] 实验数量是否足够（顶会论文通常 4-6 个表/图）？
- [ ] 如果有真实数据，结果是否合理（没有异常值）？
- [ ] 统计显著性是否处理（均值 +/- 标准差，或置信区间）？
