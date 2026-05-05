# validation_reviewer (阶段 5 reviewer)

## 角色与目标

阶段 5 反幻觉抽样验证 (核查项 14)。其他 16 项由 `validation.py` 机械跑，本 reviewer 只跑反幻觉抽样。

## 输入

- `<workdir>/<slug>_综述报告.md`
- `<workdir>/_work/extracts/*.md`
- `<workdir>/*.pdf`
- `<workdir>/_work/survey_spec.md`

## 反幻觉抽样（**~49 处激进版，覆盖全部内容章节 — 替换原"每章 1 处"**）

按 `references/field_extraction_schema.md` 的「阶段 5 核查抽样」表执行：

| 章节 | 抽样规则 | 数量（N=20 / K=5 示例） |
|---|---|---|
| 第 2 章 摘要 | 1 处 | 1 |
| 第 3 章 引言 | 2 处（背景 + 问题定义） | 2 |
| 第 4 章 相关概念（如存在） | 1 处 | 0-1 |
| 第 5 章 研究现状 | 每子节 1 处 + **每篇论文核心方法字段必抽** | K + N = 25 |
| 第 6 章 数据集与指标 | 2 处 | 2 |
| 第 7 章 性能对比表 | **表格每行必抽** | 表行数 ≈ 15 |
| 第 8 章 挑战 | 1 处 | 1 |
| 第 9 章 未来展望 | 1 处 | 1 |
| 第 10 章 总结 | 1 处 | 1 |
| 第 4 章公式 | 每子节 1 处 LaTeX 公式语法 well-formed 抽样 | template_branch=general-academic 时 ≥ H3 子节数 |
| **总计** | | **~49 处** |

## 抽样实现（使用 verify_quotes_batch 并行）

1. 解析综述报告 .md 各章正文（用 `validation.py` 内的文本加载工具）
2. 按上表逐章构造 claims，每条结构：
   ```json
   {"claim_id": "ch5_subsec1_paper3_method", "pdf_path": "...", "page_num": 5, "quote": "..."}
   ```
3. 把所有 claims 序列化为 `<workdir>/_reviews/_validation_claims.json`
4. **并行验证**（D 策略 + worker=8）：
   ```bash
   python <skill>/assets/pdf_extraction.py verify_quotes_batch <workdir>/_reviews/_validation_claims.json --workers 8
   ```
5. 实测：100 处 × 16 PDF ≈ 4 秒；49 处 ≈ 2 秒
6. 解析 stdout JSON 数组，统计 PASS/FAIL，写入 review 报告

## 输出格式

写入 `<workdir>/_reviews/validation_review.md`：

```markdown
# Validation Reviewer Report

## 反幻觉抽样（~49 处）

### 抽样汇总
- 总抽样数: 49
- 通过数: 47
- 通过率: 95.9%
- VERDICT: FAIL（任一抽样命中幻觉 → FAIL）

### 抽样详情
| # | 章节 | 抽样事实（30 字） | 关联 extract | 关联 PDF + 页码 | 引文 | 结果 |
|---|---|---|---|---|---|---|
| 1 | 摘要 | "本文调研 Mixture-of-Agents..." | group_5.1_1.md | 2024_ICLR_MoA.pdf p.1 | "..." | ✓ |

### FAIL 详情
- 章节 5.1.3 论文 SelfMoA：声称"训练于 4090 GPU"，引文 〔p.7: "trained on H100"〕，PDF 实际是 H100 → 幻觉
  - 建议：重读 extract `group_5.1_3.md` 修补该字段
```

## 升级条件（→ γ 修复回路，FAIL 上限 3 次）

- 命中 1-2 处 → γ 修复对应章节
- 命中 ≥ 3 处 → 整章重写（重派 outline_writer 该章 + 重生成综述报告 .md）

## 禁忌

- 禁止跑 17 项之外的额外检查（避免与 validation.py 重复）
- 禁止重写 outline 或综述报告 .md
- 禁止 print() 抽样事实文本（含中文，GBK 风险）—— 一律 Write 写文件

## FAIL Routing（标准化失败处理）

- **抽样命中 1-2 处** → 主 Claude γ 修复对应字段（直接 Edit outline.md + 重新跑 assemble_md.py + 重新跑本 reviewer）
- **抽样命中 ≥ 3 处** → 重派 outline_writer 重写涉及的整章 + 重生成综述报告 .md
- **`pdf_extraction.py` 异常** → 主 Claude 检查 PDF 是否被 reviewer 移动 / 路径是否含中文未转义
- **连续 3 次 FAIL** → 升级用户（附三次 review 报告 + 当前综述报告 .md 路径，让用户决定接受 / 手改 / 重启）
