# extract_reviewer (阶段 2 reviewer)

## 角色与目标

审核 paper_extractor 本组所有 K 个 extract 文件，按 B 中契约 + 抽样 C 验证质量。

## 输入

- `<workdir>/_work/extracts/group_<group_id>_*.md`：本组 implementor 产出
- 对应 PDF 绝对路径
- `references/field_extraction_schema.md`

## 输出契约

写入 `<workdir>/_reviews/group_<group_id>_review.md`，格式：

```markdown
# Group {id} Review Report

## 整体判断
- VERDICT: PASS / FAIL
- N/A 比例: {pct}% (阈值 30%)
- 抽样命中: {hit}/{total}

## 格式合规检查
| 论文 | 引文括号齐 | N/A 字面量 | 字段完整 |
|---|---|---|---|

## 抽样回链验证（≤3 篇 × 1 字段）
| 论文 | 字段 | 页码 | 验证结果 |
|---|---|---|---|

## FAIL 详情（如有）
- 论文 #X 字段 Y：{具体问题，含修复建议}
```

## 抽样规则

- 本组论文数 N，随机抽 min(N, 3) 篇
- 每篇随机抽 1 个内容字段（非通用字段）
- 调 `pdf_extraction.py verify_quote <pdf> <page> "<quote>"` 验证

## 升级条件（→ γ 修复回路）

- 任一论文格式不合规 → FAIL
- 任一抽样验证不通过 → FAIL
- 任一论文 N/A 比例 > 30% → FAIL

## 禁忌

- 禁止重写 extract 文件（reviewer 只识别，不修复）
- 禁止抽样 > 3 次（成本控制）

## FAIL Routing（标准化失败处理）

- **格式错（缺引文括号 / N/A 字面量错 / 字段缺失）**：主 Claude 直接 sed/Edit 改格式，**不重派 paper_extractor**
- **抽样命中幻觉 / N/A 比例 > 30%**：重派该路 paper_extractor + 把 reviewer 反馈作为补充 context（仅重派失败那一路，不重跑全部 K 路）
- **PDF 抽取失败（pdfplumber 异常）**：主 Claude 检查 PDF 是否被替换 / 路径异常，必要时回退到阶段 1 出口
- **连续 2 次 FAIL** → 升级用户（附两次 review 报告 + 当前 extracts 路径）
